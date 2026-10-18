# Test 03: Buttons on the Console
# Watches the three push buttons and reports every press and release in the
# Thonny shell. No display, speaker, or microphone needed -- just the buttons
# and the Pico.
#
#   MODE   GP13   (other leg to GND)
#   UP     GP14   (other leg to GND)
#   DOWN   GP15   (other leg to GND)
#
# Each pin has a pull-up, so it reads 1 until a press connects it to GND and
# pulls it to 0. The onboard LED lights while any button is held, so you can
# see a press even without looking at the shell.
#
# PASS: press and release each button once. The test prints "PASS" when it
# has seen all three, then keeps running so you can press more. Press Stop
# (Ctrl-C) to end it.
#
# If a button never reports, the wire is loose or on the wrong pin. If one
# reports many presses from a single push, that is contact "bounce" -- the
# DEBOUNCE_MS wait below ignores it.

NAME = "03-buttons.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config

DEBOUNCE_MS = 30     # ignore changes that come faster than this

led = config.init_led()
buttons = config.init_buttons()
labels = ("MODE", "UP", "DOWN")
pins = (config.BUTTON_MODE_PIN, config.BUTTON_INCREMENT_PIN,
        config.BUTTON_DECREMENT_PIN)

pressed = [False, False, False]        # what we last reported
last_change = [0, 0, 0]                # when it last changed, in ms
counts = [0, 0, 0]                     # presses seen
reported_pass = False

print()
print("Press each button. Waiting...")

while True:
    now = time.ticks_ms()
    for i in range(3):
        is_down = buttons[i].value() == 0
        if is_down != pressed[i] and \
                time.ticks_diff(now, last_change[i]) > DEBOUNCE_MS:
            pressed[i] = is_down
            last_change[i] = now
            if is_down:
                counts[i] += 1
                print("{:<5} GP{} pressed   (press #{})".format(
                    labels[i], pins[i], counts[i]))
            else:
                print("{:<5} GP{} released".format(labels[i], pins[i]))

    led.value(1 if any(pressed) else 0)

    if not reported_pass and all(counts):
        reported_pass = True
        print()
        print("PASS: all three buttons work.")
        print("(Keep pressing, or press Stop to end the test.)")

    time.sleep_ms(5)
