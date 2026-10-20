# Chapter 15, Test 08: Round-trip time to the broker and back
# Publishes a numbered message on the device's "echo" topic; the computer-side
# server/echo_responder.py publishes the same bytes on "echo-reply"; this script
# times the round trip with time.ticks_us(). Run it TRIALS times (QoS 0, 200 ms
# apart) and prints the fastest, median and slowest. A round trip is NOT the
# one-way delivery time of an alert, but it is the number you can measure with
# one clock. Needs the Pico, Wi-Fi, a broker and the echo responder running:
#     python3 server/echo_responder.py
#
# PASS: most trials come back, and the summary prints. WRITE DOWN the three
# numbers and your Wi-Fi conditions (distance, other users): the chapter has no
# measured value until a board has run this.

NAME = "08-echo-rtt.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import mqtt_common as mc
import topics

TRIALS = 20
WAIT_MS = 2000

ECHO = topics.device_topic(mc.SCHOOL_ID, mc.DEVICE_ID, "echo")
REPLY = ECHO + "-reply"
replies = {}


def on_other(topic, msg):
    replies[msg] = time.ticks_us()


mc.connect_wifi()
link = mc.Link(extra_topics=(REPLY,), on_other=on_other)
deadline = time.ticks_add(time.ticks_ms(), 20000)
while not link.service():
    if time.ticks_diff(time.ticks_ms(), deadline) > 0:
        raise SystemExit("Could not connect: {}".format(link.last_error))
    time.sleep_ms(100)

rtts = []
lost = 0
try:
    for n in range(TRIALS):
        key = b"%d" % n
        sent = time.ticks_us()
        link.publish(ECHO, key, False, 0)
        wait_end = time.ticks_add(time.ticks_ms(), WAIT_MS)
        while key not in replies and time.ticks_diff(time.ticks_ms(), wait_end) < 0:
            link.service()
            time.sleep_ms(1)
        if key in replies:
            rtts.append(time.ticks_diff(replies[key], sent))
        else:
            lost += 1
        time.sleep_ms(200)
finally:
    link.close()

print()
if rtts:
    rtts.sort()
    print("{} of {} trials answered ({} lost)".format(len(rtts), TRIALS, lost))
    print("fastest {:.1f} ms   median {:.1f} ms   slowest {:.1f} ms".format(
        rtts[0] / 1000, rtts[len(rtts) // 2] / 1000, rtts[-1] / 1000))
    print("PASS")
else:
    print("No reply. Is server/echo_responder.py running, and may this device write {} ?".format(ECHO))

# Try This
#   1. The loop above polls every 1 ms. Change it to 40 ms (an audio frame).
#      By how much does the median grow, and why?
#   2. Move the Pico farther from the access point and repeat. Is the slowest
#      trial more affected than the fastest?
