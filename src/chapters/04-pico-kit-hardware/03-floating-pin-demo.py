# Chapter 4, Test 03: A floating pin versus a pulled pin
# Reads GP16, a pin NOTHING IS CONNECTED TO, 40 times in four situations:
#   1. no pull, after the pin was driven low
#   2. pull-up
#   3. pull-down, after the pin was driven low
#   4. pull-down, after the pin was driven HIGH (a quirk test, see below)
# This is the "Pull-Up Button Circuit" activity done on real hardware.
#
# BEFORE YOU RUN: make sure no wire is plugged into GP16 (physical pin 21).
#
# PASS: situation 2 reads all 1 and situation 3 reads all 0.
#
# WHY SITUATION 4 EXISTS: on a Pico 2 W tested for this book, GP16 and GP17 kept
# reading 1 with the pull-down enabled once the pin had been driven or pulled
# high (it did not fall back to 0). The RP2350 chip has a known pad quirk of
# this kind (check Raspberry Pi's RP2350 errata). Pull-UPS are not affected, which
# is one more reason the kit's buttons use pull-ups. If situation 4 reads 0 on
# your board, your chip does not have the quirk.

NAME = "03-floating-pin-demo.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

PIN = 16
READINGS = 40


def read_many(pull, label, drive=None):
    if drive is not None:
        Pin(PIN, Pin.OUT, value=drive)       # force a known level first
        time.sleep_ms(50)
    pin = Pin(PIN, Pin.IN, pull)
    values = []
    for _ in range(READINGS):
        values.append(pin.value())
        time.sleep_ms(25)
    ones = sum(values)
    print("{:<30}: {:>2} ones {:>2} zeros  {}".format(
        label, ones, READINGS - ones, "".join(str(v) for v in values)))
    return ones


none_ones = read_many(None, "1. no pull (driven low first)", 0)
up_ones = read_many(Pin.PULL_UP, "2. pull-up")
down_low = read_many(Pin.PULL_DOWN, "3. pull-down (driven low first)", 0)
down_high = read_many(Pin.PULL_DOWN, "4. pull-down (driven HIGH first)", 1)
Pin(PIN, Pin.OUT, value=0)                   # leave the pin tidy
Pin(PIN, Pin.IN)

print()
if up_ones == READINGS and down_low == 0:
    print("PASS: pull-up reads 1, pull-down reads 0.")
else:
    print("CHECK: is something wired to GP{}?".format(PIN))
if down_high == READINGS:
    print("Quirk seen: the pull-down could not pull the pin low after it was high.")
elif down_high == 0:
    print("No quirk: the pull-down pulled the pin low even after it was high.")
