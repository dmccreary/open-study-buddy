# Chapter 15, Test 02: Your first MQTT conversation
# The plain umqtt.simple calls, one at a time: join Wi-Fi, connect with a last
# will, announce "online" (retained), subscribe to the school-wide and the
# classroom alert topics, then poll with check_msg() and send a ping every
# 15 seconds for RUN_SECONDS. Needs only the Pico, Wi-Fi and a broker (see
# README.md for the one-time setup). It draws nothing.
#
# PASS: it prints "connected", "subscribed", and "published online". Then, from
# your computer, run   python3 server/publish_alert.py --room 214 --type notice
# --title Hello --when Now --text Hi    and the alert prints here within a
# moment. At the end it prints PASS if the connection stayed up.
#
# While it runs, watch the status topic from your computer:
#     python3 server/watch.py 'school/crhs/device/+/status'
# You should see "online" with an R (retained) flag, and "offline" when the
# script ends.

NAME = "02-mqtt-hello.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from umqtt.simple import MQTTClient

import mqtt_common as mc

RUN_SECONDS = 60
SEND_PINGS = True            # Try This 1: set False and see what the broker does

got = []


def on_message(topic, msg):
    print("  message on {}: {}".format(topic.decode(), msg.decode()))
    got.append(topic)


print("Joining Wi-Fi ...")
wlan = mc.connect_wifi()
print("Wi-Fi up, address", wlan.ifconfig()[0])

client = MQTTClient(mc.DEVICE_ID, mc.HOST, mc.PORT, mc.USER, mc.PASSWORD,
                    keepalive=mc.KEEPALIVE_S)
client.set_callback(on_message)
client.set_last_will(mc.STATUS_TOPIC, mc.OFFLINE, retain=True, qos=1)

print("Connecting to {}:{} as {} ...".format(mc.HOST, mc.PORT, mc.DEVICE_ID))
client.connect(True)
print("connected (keepalive {} s)".format(mc.KEEPALIVE_S))
try:
    for topic in mc.ALERT_TOPICS:
        client.subscribe(topic, 1)
        print("subscribed:", topic)
    client.publish(mc.STATUS_TOPIC, mc.ONLINE, True, 1)
    print("published online to", mc.STATUS_TOPIC)

    end = time.ticks_add(time.ticks_ms(), RUN_SECONDS * 1000)
    last_ping = time.ticks_ms()
    pings = 0
    print("Listening for {} s ...".format(RUN_SECONDS))
    while time.ticks_diff(time.ticks_ms(), end) < 0:
        client.check_msg()                 # returns at once if nothing arrived
        if SEND_PINGS and time.ticks_diff(time.ticks_ms(), last_ping) >= mc.PING_MS:
            client.ping()
            pings += 1
            last_ping = time.ticks_ms()
        time.sleep_ms(50)
    print("{} ping(s) sent, {} message(s) received".format(pings, len(got)))
    print("PASS: the connection stayed up for {} s.".format(RUN_SECONDS))
finally:
    # A clean DISCONNECT does not fire the last will, so say goodbye ourselves.
    try:
        client.publish(mc.STATUS_TOPIC, mc.OFFLINE, True, 1)
        client.disconnect()
    except OSError:
        pass

# Try This
#   1. Set SEND_PINGS = False and RUN_SECONDS = 120. The broker drops you after
#      1.5 x 30 = 45 s of silence and publishes the last will. Does the script
#      notice? (Look at what check_msg() does after the drop.)
#   2. Instead of letting the script finish, unplug the USB cable. Watch
#      server/watch.py: when does "offline" appear, and why that long?
#   3. Run the script on two Picos that share the same DEVICE_ID. What happens?
