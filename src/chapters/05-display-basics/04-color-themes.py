# Chapter 5, Test 04: Color themes
# Draws the same small screen in two themes, NIGHT and DAY, three times,
# switching every two seconds. Changing the theme changes one variable.
# Needs the display.
#
# PASS: the screen alternates between a dark and a light version, the text
# stays readable in both, and nothing needed to be edited but `theme`.

NAME = "04-color-themes.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import shapes

NIGHT = {"background": config.BLACK, "text": config.WHITE, "accent": config.CYAN}
DAY = {"background": config.WHITE, "text": config.BLACK, "accent": config.BLUE}


def draw(theme, name):
    display.fill(theme["background"])
    shapes.ring(display, config.CENTER_X, config.CENTER_Y, config.SAFE_RADIUS,
                theme["accent"], 3)
    config.centered_text(display, config.BIG_FONT, "Study Buddy",
                         config.CENTER_Y - 30, theme["text"], theme["background"])
    config.centered_text(display, config.SMALL_FONT, name + " theme",
                         config.CENTER_Y + 20, theme["accent"], theme["background"])


display = config.init_display()
config.set_backlight(True)

for _ in range(3):
    for theme, name in ((NIGHT, "NIGHT"), (DAY, "DAY")):
        print("showing", name)
        draw(theme, name)
        time.sleep(2)
print("Done.")

# Try This
#   1. Add a third theme with your school's colors, using config.color565().
#   2. Make the accent color too close to the background. At what point is it
#      hard to read?
