# Chapter 15, Test 04: What does check_msg() cost?
# Connects with mqtt_common.Link, then measures
#   phase 1: 1,000 back-to-back idle check_msg() calls (nothing waiting)
#   phase 2: PHASE2_SECONDS of one link.service() call per 40 ms pass, during
#            which YOU publish alerts from your computer; the slowest pass that
#            delivered a message is reported separately.
# Prints microseconds and the share of one 40,000 us audio frame. Needs the
# Pico, Wi-Fi and a broker. WRITE DOWN the numbers: the chapter has only an
# estimate until a board has run this.
#
# PASS: both phases print numbers and the last line says PASS. Send at least
# three alerts with different ids during phase 2, for example
#   python3 server/publish_alert.py --room 214 --type notice --title A --when B --text C

NAME = "04-check-msg-cost.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import time

import mqtt_common as mc

FRAME_US = 40000
IDLE_CALLS = 1000
PHASE2_SECONDS = 30

mc.connect_wifi()
link = mc.Link()
deadline = time.ticks_add(time.ticks_ms(), 20000)
while not link.service():
    if time.ticks_diff(time.ticks_ms(), deadline) > 0:
        raise SystemExit("Could not connect: {}".format(link.last_error))
    time.sleep_ms(100)
print("connected")

# phase 1: idle check_msg(), straight on the client (no ping logic mixed in)
gc.collect()
low = 10 ** 9
high = 0
total = 0
for _ in range(IDLE_CALLS):
    t0 = time.ticks_us()
    link.client.check_msg()
    cost = time.ticks_diff(time.ticks_us(), t0)
    total += cost
    low = min(low, cost)
    high = max(high, cost)
print()
print("phase 1: {} idle check_msg() calls".format(IDLE_CALLS))
print("  fastest {} us   average {} us   slowest {} us".format(low, total // IDLE_CALLS, high))
print("  average is {:.2f}% of one {} us frame".format(100 * (total / IDLE_CALLS) / FRAME_US, FRAME_US))

# phase 2: realistic loop, publish alerts now
print()
print("phase 2: {} s, one service() per 40 ms pass. Publish alerts now.".format(PHASE2_SECONDS))
passes = 0
slow_delivery = 0
slowest = 0
delivered = 0
end = time.ticks_add(time.ticks_ms(), PHASE2_SECONDS * 1000)
while time.ticks_diff(time.ticks_ms(), end) < 0:
    before = len(link.pending) + link.dupes + link.bad
    t0 = time.ticks_us()
    link.service()
    cost = time.ticks_diff(time.ticks_us(), t0)
    passes += 1
    slowest = max(slowest, cost)
    if len(link.pending) + link.dupes + link.bad != before:
        delivered += 1
        slow_delivery = max(slow_delivery, cost)
    link.take()
    time.sleep_ms(40)
print("  {} passes, slowest pass {} us".format(passes, slowest))
if delivered:
    print("  {} pass(es) delivered a message; the slowest took {} us = {:.1f}% of a frame".format(
        delivered, slow_delivery, 100 * slow_delivery / FRAME_US))
else:
    print("  no message arrived: publish an alert while phase 2 runs and run it again")
link.close()
print()
print("PASS" if delivered else "CHECK: no delivery was measured")

# Try This
#   1. Publish a 500-byte alert (a long text). Does the delivery pass get slower?
#   2. Compare the slowest pass with the Chapter 8 work time of your loudness
#      calculation. Which is bigger? Do both together still fit in 40 ms?
