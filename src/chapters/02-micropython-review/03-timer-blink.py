# Chapter 2, Test 03: Blink with a Timer
# A hardware timer toggles the onboard LED every 250 ms while the main program
# keeps running its own loop. Needs only the Pico.
#
# PASS: the LED blinks twice a second AND the shell keeps printing a count
# once per second. If the count stopped while the LED blinked, or the other
# way round, something is blocking the main loop.

NAME = "03-timer-blink.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin, Timer

led = Pin("LED", Pin.OUT)


def blink(timer):
    led.toggle()


tick = Timer(period=250, mode=Timer.PERIODIC, callback=blink)
print("Timer running. The main loop prints a count each second. Ctrl-C to stop.")

try:
    seconds = 0
    while True:
        time.sleep(1)
        seconds += 1
        print("main loop:", seconds, "s")
finally:
    tick.deinit()
    led.value(0)
    print("Timer stopped.")

# Try This
#   1. Change period=250 to 50. Can you still see it blink?
#   2. Use mode=Timer.ONE_SHOT. How many times does the LED change now?
