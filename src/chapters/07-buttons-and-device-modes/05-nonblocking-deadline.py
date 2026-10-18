# Chapter 7, Test 05: Blocking versus non-blocking waits
# Waits 3 seconds two ways and counts how many times the main loop got to run
# in that time:
#   blocking      time.sleep(1), three times
#   non-blocking  keep looping and check a deadline with ticks_diff
# Also prints how many 40 ms audio frames each way would have missed. Needs only
# the Pico. Tap the MODE button during the run if it is wired: the non-blocking
# loop notices it, the blocking one cannot.
#
# PASS: the blocking loop runs 3 passes and misses about 75 frames' worth of
# time; the non-blocking loop runs many thousands of passes.

NAME = "05-nonblocking-deadline.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

button = Pin(13, Pin.IN, Pin.PULL_UP)
SECONDS = 3

print("Blocking: sleep(1) x", SECONDS)
passes = 0
taps = 0
start = time.ticks_ms()
for _ in range(SECONDS):
    time.sleep(1)                       # nothing else can happen here
    passes += 1
blocking_ms = time.ticks_diff(time.ticks_ms(), start)
print("  passes:", passes, "  time: {} ms".format(blocking_ms))
print("  a 40 ms audio frame arrives every 40 ms: up to {} frames went unread".format(
    blocking_ms // 40))

print()
print("Non-blocking: tap MODE during these", SECONDS, "seconds")
deadline = time.ticks_add(time.ticks_ms(), SECONDS * 1000)
passes = 0
taps = 0
was_down = False
start = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), deadline) < 0:
    passes += 1
    is_down = button.value() == 0
    if is_down and not was_down:
        taps += 1
    was_down = is_down
elapsed = time.ticks_diff(time.ticks_ms(), start)
print("  passes:", passes, "  time: {} ms   taps noticed: {}".format(elapsed, taps))
print("  that is one pass every {:.3f} ms".format(elapsed / passes))
print()
print("PASS" if passes > 1000 else "CHECK: the non-blocking loop ran fewer passes than expected")
