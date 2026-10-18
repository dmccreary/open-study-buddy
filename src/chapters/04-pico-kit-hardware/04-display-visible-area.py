# Chapter 4, Test 04: How much of the square screen can you see?
# Draws a red ring at radius 180 (the edge of the glass) and a green ring at
# radius 168 (SAFE_RADIUS), marks four pixels the chapter discusses, and
# prints their distances from the center. Needs the display.
#
# PASS: look at the screen. The green ring should be fully visible all the way
# around. The red ring is at or beyond the bezel: part of it may be hidden.
# The white dot at (180, 20) is visible; the dot at (20, 20) in the corner is
# not. Write down which marks you can see.

NAME = "04-display-visible-area.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math

import config
import shapes

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

shapes.ring(display, config.CENTER_X, config.CENTER_Y, config.RADIUS, config.RED, 2)
shapes.ring(display, config.CENTER_X, config.CENTER_Y, config.SAFE_RADIUS, config.GREEN, 2)

MARKS = ((180, 180, "center"), (180, 20, "top, inside the safe ring"),
         (20, 20, "corner, hidden"), (355, 180, "edge, barely visible"))
for x, y, label in MARKS:
    shapes.circle(display, x, y, 4, config.WHITE, config.FILL)
    distance = math.sqrt((x - config.CENTER_X) ** 2 + (y - config.CENTER_Y) ** 2)
    print("({:>3}, {:>3}) distance {:>5.1f}  {}".format(x, y, distance, label))

config.centered_text(display, config.SMALL_FONT, "red = 180  green = 168",
                     config.CENTER_Y + 20, config.WHITE)
visible = math.pi * config.RADIUS ** 2
safe = math.pi * config.SAFE_RADIUS ** 2
print()
print("pixels in the square: {:,}".format(config.WIDTH * config.HEIGHT))
print("pixels in the glass circle: about {:,.0f} ({:.1f}%)".format(
    visible, 100 * visible / (config.WIDTH * config.HEIGHT)))
print("pixels in the safe circle : about {:,.0f} ({:.1f}%)".format(
    safe, 100 * safe / (config.WIDTH * config.HEIGHT)))
