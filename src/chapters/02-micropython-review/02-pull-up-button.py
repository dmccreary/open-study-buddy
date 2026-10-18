# Chapter 2, Test 02: A pull-up button
# Reads the MODE button (GP13) and prints each change. The pin is an input with
# the built-in pull-up, so it reads 1 when idle and 0 while pressed.
# Needs the MODE button wired as in the kit README.
#
# PASS: "1" before you press, "0" while you hold, "1" after you let go. Press
# Ctrl-C to stop; the program prints the last value it saw.
#
# The chapter's rule: "pressed" reads as 0 with a pull-up.

NAME = "02-pull-up-button.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

PIN_NUMBER = 13

button = Pin(PIN_NUMBER, Pin.IN, Pin.PULL_UP)
last = None
print("Watching GP{}. Press and release the MODE button. Ctrl-C to stop.".format(
    PIN_NUMBER))

try:
    while True:
        value = button.value()
        if value != last:
            print("GP{} reads {}   ({})".format(
                PIN_NUMBER, value, "pressed" if value == 0 else "not pressed"))
            last = value
        time.sleep_ms(10)
except KeyboardInterrupt:
    print("Stopped. Last value:", last)
