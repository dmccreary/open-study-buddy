# Chapter 5, Test 01: How long does a full-screen update really take?
# Fills the whole 360 x 360 screen with a color at three SPI speeds and times
# it. Compares the measured time with the chapter's best case: 259,200 bytes x
# 8 bits / baud rate (86.4 ms at 24 MHz). Also prints the SPI object so you
# can see the baud rate you ACTUALLY got. Needs the display.
#
# PASS: the table prints, the measured time is at least the best case at each
# speed, and the "you get" column shows 8, 12, and 24 MHz for the three
# requests. Write down your measured time at 24 MHz: it is the number the
# whole chapter is built around.

NAME = "01-fill-timing.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config

FRAME_BYTES = config.WIDTH * config.HEIGHT * 2
ASKED = (8_000_000, 12_000_000, 20_000_000, 24_000_000)
COLORS = (config.RED, config.GREEN, config.BLUE)


def actual_baud(spi):
    text = str(spi)
    start = text.find("baudrate=")
    if start < 0:
        return None
    digits = ""
    for ch in text[start + 9:]:
        if not ch.isdigit():
            break
        digits += ch
    return int(digits) if digits else None


print()
print("{:>11} {:>11} {:>14} {:>13} {:>8}".format(
    "you ask", "you get", "best case ms", "measured ms", "frames/s"))
results = []
for asked in ASKED:
    config.BAUDRATE = asked
    display = config.init_display()
    config.set_backlight(True)
    got = actual_baud(display.spi)
    best = FRAME_BYTES * 8 * 1000 / got if got else 0
    times = []
    for color in COLORS:
        start = time.ticks_us()
        display.fill(color)
        times.append(time.ticks_diff(time.ticks_us(), start) / 1000)
    measured = min(times)
    results.append((asked, got, best, measured))
    print("{:>11} {:>11} {:>14.1f} {:>13.1f} {:>8.1f}".format(
        asked, got if got else "?", best, measured, 1000 / measured))

config.BAUDRATE = 24_000_000
print()
ok = True
for asked, got, best, measured in results:
    if got and measured < best * 0.98:
        ok = False
        print("Faster than the best case at", asked, "-- something is off")
print("PASS: measured times are at or above the best case." if ok else "CHECK the lines above.")
print("Fastest rate you can ask for is 24 MHz; asking for 20 MHz gives 12 MHz.")
