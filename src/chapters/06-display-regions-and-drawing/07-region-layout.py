# Chapter 6, Test 07: The five-region layout
# Draws the chapter's five regions (status bar, time, mascot, spectrum, agent
# message), checks that every corner is inside the safe circle, then times a
# full redraw of each region and of all five together. Needs the display.
#
# PASS: every corner check says "inside"; the total is 50,752 bytes. Write
# down your total redraw time: the chapter's best case is 16.9 ms at 24 MHz,
# versus 86.4 ms or more for the full screen.

NAME = "07-region-layout.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time

import config

REGIONS = (
    ("status", 120, 30, 120, 20, config.YELLOW),
    ("time", 130, 72, 100, 32, config.CYAN),
    ("mascot", 148, 112, 64, 64, config.GREEN),
    ("spectrum", 80, 190, 200, 40, config.MAGENTA),
    ("message", 60, 240, 240, 32, config.BLUE),
)

ok = True
print()
for name, x, y, w, h, color in REGIONS:
    inside = True
    for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        distance = math.sqrt((cx - config.CENTER_X) ** 2 + (cy - config.CENTER_Y) ** 2)
        if distance > config.SAFE_RADIUS:
            inside = False
    ok = ok and inside
    print("{:<9} {:>3},{:>3} {:>3}x{:<3} {:>7,} bytes  corners {}".format(
        name, x, y, w, h, w * h * 2, "inside" if inside else "OUTSIDE"))

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

print()
total_bytes = 0
total_ms = 0.0
for name, x, y, w, h, color in REGIONS:
    best = None
    for _ in range(3):
        start = time.ticks_us()
        display.fill_rect(x, y, w, h, color)
        elapsed = time.ticks_diff(time.ticks_us(), start) / 1000
        best = elapsed if best is None else min(best, elapsed)
    size = w * h * 2
    total_bytes += size
    total_ms += best
    if w >= len(name) * 8:
        config.centered_text(display, config.SMALL_FONT, name, y + h // 2 - 8,
                             config.BLACK, color)
    print("{:<9} {:>7,} bytes  wire time {:>5.1f} ms  measured {:>5.1f} ms".format(
        name, size, size * 8 / 24000, best))

print("{:<9} {:>7,} bytes  wire time {:>5.1f} ms  measured {:>5.1f} ms".format(
    "ALL FIVE", total_bytes, total_bytes * 8 / 24000, total_ms))
print()
print("PASS" if ok and total_bytes == 50752 else "CHECK: a corner is outside or the total differs")
