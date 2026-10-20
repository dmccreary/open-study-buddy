# mqtt_common.py -- the Study Buddy's MQTT link (Chapter 15)
#
# Used by tests 02 to 08. It wraps umqtt.simple so that a device can:
#   * connect with a last will, announce itself "online" (retained), and
#     subscribe to its alert topics,
#   * be polled once per loop pass with service(), which never sleeps,
#   * keep the connection alive with PINGREQs and notice when it has died,
#   * reconnect with a growing wait between tries, without ever blocking
#     the loop for longer than one connect attempt's timeout,
#   * hand alerts to the main loop through a small queue, so the MQTT
#     callback never draws or plays sound.
#
# Install the library once (the Pico must be on Wi-Fi):
#     mpremote mip install umqtt.simple
#
# Add these lines to the kit's secrets.py (it is never committed):
#     mqtt_host = "192.168.1.50"        # the broker's IP address, not a name
#     mqtt_user = "desk-07"
#     mqtt_pass = "something-long-and-unique"
# and, if you want to change them, school_id, room, and device_id.

import time
import network

import alerts
import backoff
import topics
import wifi_link

try:
    import secrets
except ImportError:
    secrets = None

try:
    import edition                  # Chapter 16 writes this file; absent here
except ImportError:
    edition = None


def _setting(lower, upper, default):
    """edition.py (Chapter 16, upper-case names) wins, then secrets.py (lower-case)."""
    if edition is not None and hasattr(edition, upper):
        return getattr(edition, upper)
    if secrets is not None and hasattr(secrets, lower):
        return getattr(secrets, lower)
    return default


SCHOOL_ID = _setting("school_id", "SCHOOL_ID", "crhs")
ROOM = _setting("room", "ROOM", "214")
DEVICE_ID = _setting("device_id", "DEVICE_ID", "desk-07")
HOST = _setting("mqtt_host", "MQTT_HOST", None)
PORT = _setting("mqtt_port", "MQTT_PORT", 1883)
USER = _setting("mqtt_user", "MQTT_USER", None)
PASSWORD = _setting("mqtt_pass", "MQTT_PASS", None)

KEEPALIVE_S = 30                    # told to the broker in CONNECT
PING_MS = KEEPALIVE_S * 1000 // 2   # send a PINGREQ this often when idle
DEAD_MS = KEEPALIVE_S * 1500        # nothing heard for this long: link is dead
CONNECT_TIMEOUT_S = 2               # a connect attempt blocks the loop this long, at most
BACKOFF_BASE_MS = 1000
BACKOFF_CAP_MS = 30000
MAX_PENDING = 4                     # alerts waiting for the main loop

STATUS_TOPIC = topics.device_status(SCHOOL_ID, DEVICE_ID)
TELEMETRY_TOPIC = topics.device_telemetry(SCHOOL_ID, DEVICE_ID)
ALERT_TOPICS = (topics.school_alert(SCHOOL_ID), topics.room_alert(SCHOOL_ID, ROOM))
ONLINE = b"online"
OFFLINE = b"offline"


def retry_wait_ms(attempt):
    """How long to wait after the `attempt`-th failure in a row (1 is the first).
    This is Chapter 14's backoff.py (copied into this folder): the ceiling doubles,
    2 s, 4 s, 8 s, 16 s, then 30 s, and the wait is a random number from 0 up to
    the ceiling ("full jitter"), so a classroom of devices does not all retry at
    the same instant after a broker restart."""
    return backoff.delay_ms(attempt, BACKOFF_BASE_MS, BACKOFF_CAP_MS)


def connect_wifi(timeout_ms=15000):
    """Join the Wi-Fi network named in secrets.py with Chapter 13's wifi_link.py
    (copied into this folder). Raises wifi_link.WifiError with a readable reason."""
    return wifi_link.connect(timeout_ms=timeout_ms)


def _why(error):
    """A readable reason. umqtt raises OSError(-1) when the broker closes the
    connection, which prints as just '-1'."""
    if isinstance(error, OSError) and error.args and error.args[0] == -1:
        return "connection closed by the broker"
    return str(error) or error.__class__.__name__


class _Spy:
    """Wraps umqtt's socket so we know when the broker last sent us anything."""

    def __init__(self, sock, link):
        self.sock = sock
        self.link = link

    def read(self, n):
        data = self.sock.read(n)
        if data:
            self.link.last_rx = time.ticks_ms()
        return data

    def write(self, buf, n=None):
        if n is None:
            return self.sock.write(buf)
        return self.sock.write(buf, n)

    def setblocking(self, flag):
        return self.sock.setblocking(flag)

    def close(self):
        return self.sock.close()


class Link:
    """One device's MQTT connection. Call service() once per loop pass."""

    def __init__(self, client_class=None, extra_topics=(), on_other=None):
        """extra_topics: more topics to subscribe to (QoS 0). Messages on
        them go to on_other(topic, msg) instead of the alert queue."""
        if client_class is None:
            from umqtt.simple import MQTTClient
            client_class = MQTTClient
        self.client_class = client_class
        self.extra_topics = extra_topics
        self.on_other = on_other
        self.alert_topics = [t.encode() for t in ALERT_TOPICS]
        self.client = None
        self.up = False
        self.attempt = 0
        self.next_try = time.ticks_ms()
        self.last_ping = 0
        self.last_rx = 0
        self.pending = []
        self.seen = alerts.Seen()
        self.connects = 0
        self.drops = 0
        self.dupes = 0
        self.bad = 0
        self.overflow = 0
        self.last_error = ""

    # ---- the callback: queue only, never draw or play sound here ---------
    def _on_msg(self, topic, msg):
        if self.on_other is not None and topic not in self.alert_topics:
            self.on_other(topic, msg)
            return
        alert = alerts.decode_alert(msg)
        if alert is None:
            self.bad += 1
        elif not self.seen.is_new(alert["id"]):
            self.dupes += 1
        elif len(self.pending) >= MAX_PENDING:
            self.overflow += 1
        else:
            self.pending.append(alert)

    # ---- connecting ------------------------------------------------------
    def _try_connect(self):
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            wlan.active(True)
            wlan.connect(secrets.wifi_ssid, secrets.wifi_pass)    # returns at once
            raise OSError("Wi-Fi is down")
        if not HOST:
            raise OSError("mqtt_host is not set in secrets.py")
        client = self.client_class(DEVICE_ID, HOST, PORT, USER, PASSWORD,
                                   keepalive=KEEPALIVE_S)
        client.set_callback(self._on_msg)
        client.set_last_will(STATUS_TOPIC, OFFLINE, retain=True, qos=1)
        try:
            client.connect(True, timeout=CONNECT_TIMEOUT_S)
        except TypeError:                   # an older umqtt.simple has no timeout=
            client.connect(True)
        client.sock = _Spy(client.sock, self)
        self.last_rx = time.ticks_ms()
        for topic in ALERT_TOPICS:
            client.subscribe(topic, 1)
        for topic in self.extra_topics:
            client.subscribe(topic, 0)
        client.publish(STATUS_TOPIC, ONLINE, True, 1)       # the "birth" message
        self.client = client
        self.last_ping = time.ticks_ms()

    def _lost(self, error):
        self.up = False
        self.drops += 1
        self.last_error = _why(error)
        try:
            self.client.sock.close()
        except Exception:
            pass
        self.client = None

    def service(self):
        """Call once per pass of the main loop. Returns True while connected.
        Never sleeps. The only call that can take long is a connect attempt,
        and it is bounded by CONNECT_TIMEOUT_S."""
        now = time.ticks_ms()
        if not self.up:
            if time.ticks_diff(now, self.next_try) < 0:
                return False
            try:
                self._try_connect()
            except Exception as error:                  # OSError, MQTTException, ...
                self.last_error = _why(error)
                self.attempt += 1
                self.next_try = time.ticks_add(
                    time.ticks_ms(), retry_wait_ms(self.attempt))
                return False
            self.up = True
            self.attempt = 0
            self.connects += 1
            return True
        try:
            self.client.check_msg()
            if time.ticks_diff(now, self.last_ping) >= PING_MS:
                self.client.ping()
                self.last_ping = now
            if time.ticks_diff(now, self.last_rx) > DEAD_MS:
                raise OSError("broker silent for %d s" % (DEAD_MS // 1000))
        except Exception as error:
            self._lost(error)
            self.next_try = time.ticks_add(time.ticks_ms(), retry_wait_ms(1))
            return False
        return True

    def take(self):
        """The oldest queued alert, or None."""
        if self.pending:
            return self.pending.pop(0)
        return None

    def publish(self, topic, payload, retain=False, qos=0):
        """Publish if connected. Returns True if it was sent."""
        if not self.up:
            return False
        try:
            self.client.publish(topic, payload, retain, qos)
            self.last_ping = time.ticks_ms()            # any packet counts as traffic
            return True
        except Exception as error:
            self._lost(error)
            self.next_try = time.ticks_add(time.ticks_ms(), retry_wait_ms(1))
            return False

    def publish_telemetry(self, volume, heap, last_wake=None):
        """Small JSON status for dashboards. QoS 0: the next one replaces it."""
        wake = "null" if last_wake is None else str(int(last_wake))
        text = '{"up":%d,"vol":%d,"heap":%d,"wake":%s,"conn":%d}' % (
            time.ticks_ms() // 1000, volume, heap, wake, self.connects)
        return self.publish(TELEMETRY_TOPIC, text, False, 0)

    def close(self):
        """Leave politely. A clean DISCONNECT does NOT trigger the last will,
        so we publish "offline" ourselves first."""
        if self.up:
            try:
                self.client.publish(STATUS_TOPIC, OFFLINE, True, 1)
                self.client.disconnect()
            except Exception:
                pass
        self.up = False
