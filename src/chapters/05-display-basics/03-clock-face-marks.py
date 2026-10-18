# Chapter 5, Test 03: Clock face geometry
# Places the 12 hour marks on a circle of radius 150 around (180, 180) with the
# polar-to-Cartesian formulas, checks five of them against the chapter's
# table, and draws a minute hand and hour hand for 10:10. Needs the display.
#
# PASS: twelve dots form a round clock face with 12 at the top and 3 on the
# right, and the hands point at the 10 and the 2. The five checks print "ok".

NAME = "03-clock-face-marks.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math

import config
import shapes

CX = config.CENTER_X
CY = config.CENTER_Y
RING = 150


def polar(radius, degrees):
    """Clock angles: 0 degrees at 12 o'clock, going clockwise."""
    angle = math.radians(degrees)
    return CX + round(radius * math.sin(angle)), CY - round(radius * math.cos(angle))


display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

for hour in range(12):
    x, y = polar(RING, hour * 30)
    size = 6 if hour % 3 == 0 else 3
    shapes.circle(display, x, y, size, config.WHITE, config.FILL)

# 10:10 -> minute hand at 60 degrees, hour hand at 305 degrees
for radius, degrees, color in ((125, 60, config.CYAN), (80, 305, config.YELLOW)):
    x, y = polar(radius, degrees)
    display.line(CX, CY, x, y, color)
shapes.circle(display, CX, CY, 5, config.RED, config.FILL)

expected = {12: (180, 30), 1: (255, 50), 3: (330, 180), 6: (180, 330), 9: (30, 180)}
ok = True
print()
for hour, want in expected.items():
    got = polar(RING, (hour % 12) * 30)
    good = got == want
    ok = ok and good
    print("hour {:>2}: got {}, chapter says {}  {}".format(hour, got, want, "ok" if good else "WRONG"))
print()
print("PASS" if ok else "FAIL: a mark is in the wrong place")
