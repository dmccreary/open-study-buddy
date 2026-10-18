# Chapter 4, Test 01: Count the SPI bytes behind one pixel
# Wraps the display's SPI bus in a small counter and then draws a single pixel,
# a 100 x 30 rectangle with fill_rect, and the same rectangle one pixel at a
# time (just 100 pixels of it, to keep it quick). Needs the display.
#
# PASS: one pixel() sends 13 bytes; fill_rect(100 x 30) sends 6,011 bytes
# (11 bytes of commands + 6,000 bytes of pixels). Those are the numbers in
# Chapters 4 and 6.

NAME = "01-pixel-spi-bytes.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import config


class CountingSPI:
    """Passes every write to the real SPI bus and counts the bytes."""

    def __init__(self, spi):
        self.spi = spi
        self.bytes = 0
        self.writes = 0

    def write(self, data):
        self.bytes += len(data)
        self.writes += 1
        return self.spi.write(data)

    def reset(self):
        self.bytes = 0
        self.writes = 0


display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
counter = CountingSPI(display.spi)
display.spi = counter

ok = True

counter.reset()
display.pixel(10, 20, config.RED)
print("pixel(10, 20, RED)        : {:>6} bytes in {:>3} writes (expect 13)".format(
    counter.bytes, counter.writes))
ok = ok and counter.bytes == 13

counter.reset()
display.fill_rect(130, 72, 100, 30, config.CYAN)
print("fill_rect(100 x 30)       : {:>6} bytes in {:>3} writes (expect 6011)".format(
    counter.bytes, counter.writes))
ok = ok and counter.bytes == 6011

counter.reset()
for x in range(100):
    display.pixel(130 + x, 120, config.YELLOW)
print("100 pixel() calls         : {:>6} bytes in {:>3} writes (expect 1300)".format(
    counter.bytes, counter.writes))
ok = ok and counter.bytes == 1300
print("  -> the same 3,000 pixels one at a time would be 39,000 bytes.")

print()
print("PASS" if ok else "CHECK: a count differs from the chapter. Print the numbers and compare.")

# Try This
#   1. Draw a 1 x 1 pixel with fill_rect. Is it smaller or larger than pixel()?
#   2. Call display.text(config.SMALL_FONT, "A", 100, 200). How many writes
#      and bytes is one letter? (The driver sends 2 blits of 8 x 8 pixels.)
