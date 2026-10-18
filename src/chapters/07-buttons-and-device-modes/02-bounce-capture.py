# Chapter 7, Test 02: Capture real contact bounce
# Waits for you to press the MODE button, then records the raw pin value every
# 200 microseconds for 40 ms and prints it as a string of 1s and 0s (one
# character per 200 us). It repeats for 8 presses, prints how many times the pin
# changed value and when it last changed, and finally suggests a debounce
# time. Needs the MODE button (GP13).
#
# PASS: you see strings like 11110100100000000..., and a summary. Compare the
# "last change" times with the 30 ms debounce in the kit. Real bounce is
# usually 0 to 5 ms for a good tactile switch, but yours may be worse.
#
# Also prints each trace downsampled to one value per 5 ms, in the format used
# by the Chapter 7 debounce activity, so you can paste your own switch into it.

NAME = "02-bounce-capture.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

PRESSES = 8
STEP_US = 200
SAMPLES = 200                  # 200 x 200 us = 40 ms

button = Pin(13, Pin.IN, Pin.PULL_UP)
settle_times = []
change_counts = []

print("Press the MODE button {} times, letting go between presses.".format(PRESSES))
for n in range(1, PRESSES + 1):
    while button.value() == 1:           # wait for the first touch
        pass
    trace = bytearray(SAMPLES)
    t0 = time.ticks_us()
    for i in range(SAMPLES):
        trace[i] = button.value()
        while time.ticks_diff(time.ticks_us(), t0) < (i + 1) * STEP_US:
            pass
    changes = 0
    last = 0
    for i in range(1, SAMPLES):
        if trace[i] != trace[i - 1]:
            changes += 1
            last = i
    settle_ms = last * STEP_US / 1000
    settle_times.append(settle_ms)
    change_counts.append(changes)
    text = "".join(str(v) for v in trace)
    print()
    print("press {}: changes {}, last change at {:.1f} ms".format(n, changes, settle_ms))
    print("  raw  :", text[:100], "...")
    every5ms = "".join(str(trace[i]) for i in range(0, SAMPLES, 25))
    print("  5 ms :", ",".join(every5ms), "(first 40 ms; starts at the first touch)")
    while button.value() == 0:           # wait for release before the next press
        pass
    time.sleep_ms(200)

worst = max(settle_times)
print()
print("changes per press : {}".format(change_counts))
print("worst settle time : {:.1f} ms".format(worst))
print("kit debounce (30 ms) is {} for this switch.".format(
    "enough" if worst < 30 else "NOT enough: raise DEBOUNCE_MS"))
