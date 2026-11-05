# Lab 09: Angles to Pixels on a Round Screen
# Draws a clock face -- 60 tick marks and the numbers 12, 3, 6, 9 -- and a
# second hand that sweeps around once a minute. Every one of them is placed
# with the same two lines of trigonometry.
#
# THE IDEA: POLAR TO X, Y. On a round screen it is natural to think in
# "how far round, how far out" -- an angle and a radius -- but the display
# only takes x and y. Sine and cosine convert:
#
#     x = center_x + radius * sin(angle)
#     y = center_y - radius * cos(angle)
#
# Angle 0 points straight up and the angle grows clockwise, like a clock.
# The minus sign is there because screen y grows DOWNWARD: a point above
# the center has a SMALLER y. One second is 360 / 60 = 6 degrees.
#
# To move the hand, the old one is drawn again in the background color
# (black) and the new one is drawn in white. That is cheaper than clearing
# the screen, and nothing else flickers.
#
# Parts: the display.
#
# PASS: a ring of 60 ticks (longer every 5 seconds), the four numbers, and a
# red second hand that moves once a second. The bottom line shows the
# hand's angle and where its tip is, in x and y from the center.

NAME = "09-angles-to-pixels.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time

import config
import shapes

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

CX = config.CENTER_X
CY = config.CENTER_Y
OUTER = config.SAFE_RADIUS - 2       # where the ticks start, from the center
HAND = 92                            # second hand length
DIM = config.color565(150, 150, 150)
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT


def polar(angle_degrees, radius):
    """The x, y of a point `radius` pixels from the center, at a clock
    angle (0 = straight up, growing clockwise)."""
    a = math.radians(angle_degrees)
    return (round(CX + radius * math.sin(a)),
            round(CY - radius * math.cos(a)))


# 60 tick marks: a short line from the rim inward. Every fifth is longer.
for second in range(60):
    length = 16 if second % 5 == 0 else 7
    color = config.WHITE if second % 5 == 0 else DIM
    x0, y0 = polar(second * 6, OUTER)
    x1, y1 = polar(second * 6, OUTER - length)
    display.line(x0, y0, x1, y1, color)

# The numbers. polar() gives the CENTER of each number; text() wants its
# top-left corner, so move back half the text's width and height.
for number, angle in (("12", 0), ("3", 90), ("6", 180), ("9", 270)):
    x, y = polar(angle, OUTER - 38)
    display.text(BIG, number, x - len(number) * BIG.WIDTH // 2,
                 y - BIG.HEIGHT // 2, config.CYAN, config.BLACK)


def draw_hand(second, color):
    """Three lines side by side make a hand 3 pixels thick."""
    tip_x, tip_y = polar(second * 6, HAND)
    for dx, dy in ((0, 0), (1, 0), (0, 1)):
        display.line(CX + dx, CY + dy, tip_x + dx, tip_y + dy, color)
    return tip_x, tip_y


shown = None
while True:
    second = time.localtime()[5]
    if second != shown:
        if shown is not None:
            draw_hand(shown, config.BLACK)          # erase the old hand
        tip_x, tip_y = draw_hand(second, config.RED)
        shapes.circle(display, CX, CY, 5, config.WHITE, config.FILL)
        readout = "{:2d}s {:3d} deg x{:+4d} y{:+4d}".format(
            second, second * 6, tip_x - CX, tip_y - CY)
        config.centered_text(display, SMALL, readout, 224, config.YELLOW)
        shown = second
    time.sleep_ms(20)

# Try This
#   1. Make the hand run backwards: use (60 - second) instead of second.
#   2. Add a minute hand, 70 pixels long, using time.localtime()[4] * 6.
#      What angle should it have at 30 minutes?
#   3. Take out the minus sign in polar(). Which way does the hand go now,
#      and where does it start?
