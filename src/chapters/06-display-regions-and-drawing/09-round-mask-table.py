# Chapter 6, Test 09: How wide is the visible span on each row?
# For a row y, the visible x range inside the safe circle (radius 168 around
# (180, 180)) is 180 +/- sqrt(168^2 - dy^2). Prints the chapter's table and
# a few more rows. Runs on the Pico or on your computer. No hardware needed.
#
# PASS: row 20 gives x 129 to 231 (width 102), and the last line says PASS.

NAME = "09-round-mask-table.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math

CX = CY = 180
RADIUS = 168


def span(y, radius=RADIUS):
    dy = y - CY
    if abs(dy) > radius:
        return None
    half = math.sqrt(radius * radius - dy * dy)
    return round(CX - half), round(CX + half)


print()
print("{:>5} {:>13} {:>14} {:>7}".format("row y", "from center", "visible x", "width"))
for y in (12, 20, 40, 60, 90, 120, 150, 180):
    s = span(y)
    print("{:>5} {:>13} {:>14} {:>7}".format(
        y, abs(y - CY), "{} to {}".format(*s), s[1] - s[0]))

ok = span(20) == (129, 231) and span(180) == (12, 348)
print()
print("PASS" if ok else "FAIL")
