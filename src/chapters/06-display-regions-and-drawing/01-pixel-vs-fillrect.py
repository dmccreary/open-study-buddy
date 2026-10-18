# Chapter 6, Test 01: pixel() versus fill_rect() versus blit_buffer()
# Paints the same 100 x 30 box three ways and reports the time and the number
# of bytes each way sends over SPI. Needs the display.
#
# PASS: fill_rect and blit_buffer each send 6,011 bytes; 3,000 pixel() calls
# send 39,000 bytes and take several times longer. Write down the three times.

NAME = "01-pixel-vs-fillrect.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config

X, Y, W, H = 130, 72, 100, 30


class CountingSPI:
    def __init__(self, spi):
        self.spi = spi
        self.bytes = 0

    def write(self, data):
        self.bytes += len(data)
        return self.spi.write(data)


display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
counter = CountingSPI(display.spi)
display.spi = counter


def measure(label, draw):
    counter.bytes = 0
    start = time.ticks_us()
    draw()
    elapsed = time.ticks_diff(time.ticks_us(), start) / 1000
    print("{:<22} {:>7,} bytes {:>8.1f} ms".format(label, counter.bytes, elapsed))
    return counter.bytes, elapsed


def per_pixel():
    for y in range(Y, Y + H):
        for x in range(X, X + W):
            display.pixel(x, y, config.RED)


def one_fill():
    display.fill_rect(X, Y, W, H, config.GREEN)


pixels = bytearray(W * H * 2)
high, low = config.BLUE >> 8, config.BLUE & 255
for i in range(W * H):
    pixels[i * 2] = high
    pixels[i * 2 + 1] = low


def one_blit():
    display.blit_buffer(pixels, X, Y, W, H)


print()
print("Painting a {} x {} box ({:,} pixels):".format(W, H, W * H))
a = measure("3,000 pixel() calls", per_pixel)
b = measure("1 fill_rect()", one_fill)
c = measure("1 blit_buffer()", one_blit)

print()
print("Best-case wire time at 24 MHz for 6,011 bytes: {:.1f} ms".format(6011 * 8 / 24000))
ok = b[0] == 6011 and c[0] == 6011 and a[0] == 39000
print("PASS: byte counts match the chapter." if ok else "CHECK: a byte count differs from the chapter.")
print("pixel() was {:.1f}x slower than fill_rect().".format(a[1] / b[1]))
