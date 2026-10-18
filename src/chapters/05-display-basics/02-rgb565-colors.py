# Chapter 5, Test 02: RGB565 colors
# Computes color565() for the colors in the chapter's table, checks them against
# the values printed there, and draws a swatch for each on the screen. Needs the
# display.
#
# PASS: every row prints "ok", the last line says PASS, and you see seven
# bands of color. Do the orange by hand first: (255, 128, 0) -> 0xFC00.

NAME = "02-rgb565-colors.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import config

COLORS = (
    ("red", (255, 0, 0), 0xF800),
    ("green", (0, 255, 0), 0x07E0),
    ("blue", (0, 0, 255), 0x001F),
    ("yellow", (255, 255, 0), 0xFFE0),
    ("cyan", (0, 255, 255), 0x07FF),
    ("orange", (255, 128, 0), 0xFC00),
    ("gray", (110, 110, 110), 0x6B6D),
)

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

ok = True
print()
print("{:<7} {:<16} {:>8} {:>10} {}".format("color", "(R, G, B)", "value", "bytes", ""))
band = 36
top = 54
for i, (name, rgb, expected) in enumerate(COLORS):
    value = config.color565(*rgb)
    good = value == expected
    ok = ok and good
    print("{:<7} {:<16} {:>8} {:>10} {}".format(
        name, str(rgb), "0x{:04X}".format(value),
        "{:02X} {:02X}".format(value >> 8, value & 255), "ok" if good else "WRONG"))
    y = top + i * band
    display.fill_rect(70, y, 220, band - 4, value)
    config.centered_text(display, config.SMALL_FONT, name, y + 10, config.BLACK, value)

print()
print("PASS" if ok else "FAIL: a value does not match the chapter's table")
