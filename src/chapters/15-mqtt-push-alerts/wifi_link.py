# wifi_link.py -- join Wi-Fi in station mode, with a timeout and readable errors
#
# connect() returns the WLAN object when the Pico has an IP address, and raises
# WifiError (with .code and .reason) when it cannot. It never loops forever.
# Credentials come from secrets.py (wifi_ssid, wifi_pass).

import time
import network

# network.WLAN.status() returns these numbers on the Pico 2 W (the CYW43 driver's
# link states). The names in network.STAT_* map to the same numbers; 2 has no name.
REASONS = {
    0: "idle (not trying)",
    1: "joining the network",
    2: "joined, waiting for an IP address",
    3: "connected",
    -1: "failed (other reason)",
    -2: "network not found (wrong name, out of range, or 5 GHz only)",
    -3: "wrong password",
}


def reason(code):
    return REASONS.get(code, "unknown status {}".format(code))


class WifiError(Exception):
    def __init__(self, code, text=None):
        Exception.__init__(self, text or reason(code))
        self.code = code
        self.reason = text or reason(code)


def connect(ssid=None, password=None, timeout_ms=15000, hostname=None, show=None):
    """Join the network. show(text) is called each time the state changes."""
    if ssid is None:
        import secrets
        ssid, password = secrets.wifi_ssid, secrets.wifi_pass

    if hostname:
        try:
            network.hostname(hostname)      # must be set before connecting
        except AttributeError:
            pass                            # older firmware: no network.hostname()

    wlan = network.WLAN(network.STA_IF)     # station mode: we join someone else's network
    wlan.active(True)
    if wlan.isconnected():
        return wlan

    wlan.connect(ssid, password)
    start = time.ticks_ms()
    last = None
    while True:
        code = wlan.status()
        if code != last:
            last = code
            if show:
                show(reason(code))
        if code == 3:
            return wlan
        if code < 0:
            raise WifiError(code)
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            raise WifiError(code, "gave up after {} ms: {}".format(timeout_ms, reason(code)))
        time.sleep_ms(200)


def disconnect(wlan):
    wlan.disconnect()
    wlan.active(False)
