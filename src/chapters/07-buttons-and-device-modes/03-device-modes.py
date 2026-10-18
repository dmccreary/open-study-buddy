# Chapter 7, Test 03: The five-mode device on real buttons
# Runs the Device state machine (device.py) with the debounced Button class,
# shows the current mode on the display, and lights the onboard LED while
# LISTENING. There is no microphone or server here: when you release MODE the
# device "thinks" for 2 s, "speaks" for 2 s, and returns to the clock.
# Needs the display and the three buttons.
#
# Try this sequence (the screen and the shell print each change):
#   1. Hold MODE: LISTENING (LED on). Let go after 1 s: THINKING, then SPEAKING,
#      then CLOCK.
#   2. Tap MODE for under a quarter second: back to CLOCK at once ("too short").
#   3. In CLOCK tap UP and DOWN: the volume moves in steps of 10.
#   4. Hold UP for a second: SETTINGS. MODE (tap) moves to the next setting,
#      UP and DOWN change it, hold MODE to return to CLOCK.
#
# PASS: every transition matches the table in the chapter. Ctrl-C to stop.

NAME = "03-device-modes.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
from buttons import Button
from device import (Device, NAMES, ITEMS, THEMES,
                    CLOCK, LISTENING, THINKING, SPEAKING, SETTINGS)

LISTEN_MAX_MS = 3000
THINK_MS = 2000
SPEAK_MS = 2000

COLORS = {CLOCK: config.CYAN, LISTENING: config.RED, THINKING: config.YELLOW,
          SPEAKING: config.GREEN, SETTINGS: config.MAGENTA}
DIM = config.color565(150, 150, 150)

display = config.init_display()
config.set_backlight(True)
led = config.init_led()
mode, up, down = config.init_buttons()
buttons = (("mode", Button(mode)), ("up", Button(up)), ("down", Button(down)))
device = Device()


def put(text, y, font, color, width):
    config.centered_text(display, font, text.center(width), y, color)


def draw():
    state, volume, item, theme = device.snapshot()
    put(NAMES[state], 110, config.BIG_FONT, COLORS[state], 11)
    if state == SETTINGS:
        line = "{}: {}".format(ITEMS[item], volume if item == 0 else THEMES[theme])
    else:
        line = "Volume {}".format(volume)
    put(line, 170, config.SMALL_FONT, DIM, 30)
    hints = {CLOCK: "hold MODE to talk", LISTENING: "let go to send",
             THINKING: "MODE cancels", SPEAKING: "UP/DOWN volume",
             SETTINGS: "MODE next, hold MODE exits"}
    put(hints[state], 200, config.SMALL_FONT, DIM, 30)
    led.value(1 if state == LISTENING else 0)


display.fill(config.BLACK)
shown = None
entered_at = time.ticks_ms()
last_state = device.state
print("Ready. State:", NAMES[device.state])

try:
    while True:
        now = time.ticks_ms()
        for name, button in buttons:
            event = button.update()
            if event:
                device.on_button(name, event, button.held)

        if device.state != last_state:                    # a transition happened
            print("-> {}  (volume {})".format(NAMES[device.state], device.volume))
            last_state = device.state
            entered_at = now

        age = time.ticks_diff(now, entered_at)
        if device.state == LISTENING and age >= LISTEN_MAX_MS:
            device.on_internal("full")
        elif device.state == THINKING and age >= THINK_MS:
            device.on_internal("reply")
        elif device.state == SPEAKING and age >= SPEAK_MS:
            device.on_internal("done")

        snapshot = device.snapshot()
        if snapshot != shown:                              # dirty test: redraw only on change
            draw()
            shown = snapshot
        time.sleep_ms(5)
except KeyboardInterrupt:
    led.value(0)
    print("Stopped.")
