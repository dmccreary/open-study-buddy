# Lab 08: How the Display Mixes Color
# Every pixel on the screen is a tiny red, green, and blue light. This lab
# draws each of the three on its own, from off to full, and then a ring of
# every hue mixed from them.
#
# THE IDEA: RGB565. The display wants 16 bits per pixel. 16 does not split
# evenly three ways, so the bits are shared out 5 + 6 + 5:
#
#     bit:  15 14 13 12 11 | 10  9  8  7  6  5 | 4  3  2  1  0
#           r  r  r  r  r  | g   g  g  g  g  g | b  b  b  b  b
#
# Red and blue get 5 bits each, 32 shades (2 to the 5th). Green gets the
# extra bit, 64 shades, because human eyes are most sensitive to green.
# Look closely at the red and blue strips: you can see the steps. The
# green strip has steps half as wide.
#
# color565(red, green, blue) packs three ordinary 0-255 numbers into those
# 16 bits by keeping only the top bits of each: 255 keeps all of them,
# and 7 and 0 come out the same (both lose everything below bit 3).
#
# Parts: the display.
#
# PASS: three strips (red, green, blue) fade from black to full color, and
# a rainbow ring goes all the way around the edge. The shell shows how
# three colors are packed.

NAME = "08-color-mixing.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from array import array
import math

import config
import shapes

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

# ---------------------------------------------------------------------
# 1. Show the packing in the shell.
# ---------------------------------------------------------------------
print()
for name, rgb in (("orange", (255, 128, 0)), ("sky blue", (90, 170, 255)),
                  ("white", (255, 255, 255))):
    color = config.color565(*rgb)
    bits = "{:016b}".format(color)
    print("{:9} {:>15} -> 0x{:04X} = {} {} {}".format(
        name, str(rgb), color, bits[:5], bits[5:11], bits[11:]))
print("                              (red   green  blue)")

# ---------------------------------------------------------------------
# 2. One strip per color, each from 0 to its largest value.
# ---------------------------------------------------------------------
STRIP_X = 80
STRIP_W = 200
STRIP_H = 16

config.centered_text(display, config.BIG_FONT, "RGB565", 52, config.WHITE)

# (label, how many shades, where its bits sit in the 16)
STRIPS = (("red: 5 bits, 32 shades", 32, 11),
          ("green: 6 bits, 64 shades", 64, 5),
          ("blue: 5 bits, 32 shades", 32, 0))
y = 98
for label, shades, shift in STRIPS:
    config.centered_text(display, SMALL, label, y, DIM)
    for i in range(STRIP_W):
        level = i * shades // STRIP_W         # 0 .. shades-1 across the strip
        display.vline(STRIP_X + i, y + 18, STRIP_H, level << shift)
    y += 42

config.centered_text(display, SMALL, "eyes see green best", 228, DIM)

# ---------------------------------------------------------------------
# 3. A ring of hues: 72 wedges, each 5 degrees, mixing two of the three
#    lights at a time -- red to yellow to green to cyan to blue to magenta.
# ---------------------------------------------------------------------
def hue_to_rgb(hue):
    """hue 0-360 -> (red, green, blue), full brightness."""
    sector = hue / 60
    i = int(sector) % 6
    rise = int(255 * (sector - int(sector)))     # 0 -> 255 inside a sector
    fall = 255 - rise
    return ((255, rise, 0), (fall, 255, 0), (0, 255, rise),
            (0, fall, 255), (rise, 0, 255), (255, 0, fall))[i]


INNER = 148
OUTER = config.SAFE_RADIUS - 2
cx, cy = config.CENTER_X, config.CENTER_Y
for step in range(72):
    a0 = math.radians(step * 5)
    a1 = math.radians(step * 5 + 5.5)          # overlap a little: no gaps
    corners = []
    for angle, radius in ((a0, INNER), (a0, OUTER), (a1, OUTER), (a1, INNER)):
        corners.append(round(cx + radius * math.sin(angle)))
        corners.append(round(cy - radius * math.cos(angle)))
    color = config.color565(*hue_to_rgb(step * 5))
    shapes.poly(display, 0, 0, array('h', corners), color, config.FILL)

print()
print("Drawn: look at the screen.")

# Try This
#   1. color565(7, 7, 7) and color565(0, 0, 0) are the same color. Why?
#      Which is the smallest red that is NOT black?
#   2. Change the green strip's shades from 64 to 32 (and its label). Can
#      you see the steps now? This is what green would look like as 5-bit.
#   3. Find white, gray, and yellow in the 16 bits: which bits are on for
#      each? (Print them with "{:016b}".format(color).)
