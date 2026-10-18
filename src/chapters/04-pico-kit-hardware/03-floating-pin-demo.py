# Chapter 4, Test 03: A floating pin versus a pulled pin
# Reads GP16, a pin NOTHING IS CONNECTED TO, 40 times each with no pull, with a
# pull-up, and with a pull-down. This is the "Pull-Up Button Circuit" activity
# done on real hardware.
#
# BEFORE YOU RUN: make sure no wire is plugged into GP16 (physical pin 21).
#
# PASS: with the pull-up every reading is 1; with the pull-down every reading
# is 0; with no pull the readings may be a mix or may all be the same. If they
# are all the same, touch the end of a pin header lightly while it runs: a
# floating pin is easily pushed around by your body.

NAME = "03-floating-pin-demo.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

PIN = 16
READINGS = 40


def read_many(pull, label):
    pin = Pin(PIN, Pin.IN, pull)
    values = []
    for _ in range(READINGS):
        values.append(pin.value())
        time.sleep_ms(25)
    ones = sum(values)
    print("{:<10}: {} ones, {} zeros   {}".format(
        label, ones, READINGS - ones, "".join(str(v) for v in values)))
    return ones


none_ones = read_many(None, "no pull")
up_ones = read_many(Pin.PULL_UP, "pull-up")
down_ones = read_many(Pin.PULL_DOWN, "pull-down")

print()
if up_ones == READINGS and down_ones == 0:
    print("PASS: pull-up reads 1, pull-down reads 0.")
    if 0 < none_ones < READINGS:
        print("The floating pin flickered between 0 and 1, as the chapter describes.")
    else:
        print("The floating pin held steady this time ({} ones), but it is not guaranteed to.".format(none_ones))
else:
    print("CHECK: is something wired to GP{}?".format(PIN))
