# Chapter 6, Test 04: Pad text so one call draws and erases
# Draws "Listening..." and then the shorter word "Done" twice: once without
# padding (leftover letters stay on screen) and once padded to a fixed width
# with str.center() (the old word is fully covered). Needs the display.
#
# PASS: the top line shows "Doneening..." (leftovers); the bottom line shows
# just "Done" centered.

NAME = "04-text-padding.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

font = config.BIG_FONT
WIDTH_CHARS = 14


def put_plain(text, y):
    display.text(font, text, 30, y, config.YELLOW, config.BLACK)


def put_padded(text, y):
    config.centered_text(display, font, text.center(WIDTH_CHARS), y, config.GREEN)


config.centered_text(display, config.SMALL_FONT, "no padding", 100, config.WHITE)
config.centered_text(display, config.SMALL_FONT, "padded to 14 characters", 200, config.WHITE)

put_plain("Listening...", 130)
put_padded("Listening...", 230)
time.sleep(1.5)
put_plain("Done", 130)
put_padded("Done", 230)

print("Top line  : leftover letters from the longer word.")
print("Bottom line: padded to", WIDTH_CHARS, "characters, so the old word is gone.")
