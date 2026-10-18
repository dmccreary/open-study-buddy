# Chapter 7, Test 01: Button events
# Uses the debounced Button class (buttons.py) on the MODE, UP, and DOWN
# buttons and prints each event: press, long (after 800 ms), and release with
# how long the button was held. Needs the three buttons.
#
# PASS: a quick tap prints "press" then "release held=~100". Holding longer
# than 0.8 s prints "long" once, and then "release" when you let go. Pressing
# two buttons at once reports both. Ctrl-C to stop.

NAME = "01-button-events.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
from buttons import Button

mode, up, down = config.init_buttons()
buttons = (("MODE", Button(mode)), ("UP", Button(up)), ("DOWN", Button(down)))
led = config.init_led()

print("Tap and hold each button. Ctrl-C to stop.")
try:
    while True:
        any_down = False
        for name, button in buttons:
            event = button.update()
            if event == "release":
                print("{:<5} release  held={} ms  ({})".format(
                    name, button.held, "long" if button.held >= button.long_ms else "tap"))
            elif event:
                print("{:<5} {}".format(name, event))
            any_down = any_down or button.down
        led.value(1 if any_down else 0)
        time.sleep_ms(5)
except KeyboardInterrupt:
    led.value(0)
    print("Stopped.")
