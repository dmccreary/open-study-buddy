# Chapter 6, Test 08: Load an image from flash
# Reads sage.rgb565 (a 120 x 120 RGB565 image, 28,800 bytes) from the Pico's
# flash, ten rows at a time, and shows it in the middle of the screen with
# blit_buffer(). Needs the display and sage.rgb565 on the Pico (the upload
# script copies it).
#
# PASS: Sage the owl appears inside a round black mask, centered, in under
# 100 ms. If the colors look wrong (red and blue swapped, or a green tint),
# the byte order in the file is wrong: re-create it with tools/png-to-rgb565.py.
# If the picture looks sheared, the size passed to show_image() is not the
# size the file was made at.

NAME = "08-show-image.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import os
import time

import config

PATH = "sage.rgb565"
SIZE = 120


def show_image(display, path, x, y, size, rows_per_chunk=10):
    chunk = bytearray(size * rows_per_chunk * 2)
    with open(path, "rb") as f:
        for row in range(0, size, rows_per_chunk):
            f.readinto(chunk)
            display.blit_buffer(chunk, x, y + row, size, rows_per_chunk)


expected = SIZE * SIZE * 2
actual = os.stat(PATH)[6]
print("{} is {} bytes (expect {})".format(PATH, actual, expected))
if actual != expected:
    raise SystemExit("File size does not match SIZE. Make the file at the size you pass.")

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

start = time.ticks_ms()
show_image(display, PATH, (config.WIDTH - SIZE) // 2, (config.HEIGHT - SIZE) // 2, SIZE)
elapsed = time.ticks_diff(time.ticks_ms(), start)
print("drew the image in {} ms (wire-time minimum is about 9.6 ms)".format(elapsed))
print("PASS if the owl looks right." if elapsed < 100 else "Slower than expected; check the SPI rate.")
