# Chapter 16, Test 01: Show the school mascot on the round display
# Loads the mascot picture named in edition.py (griffin.rgb565: Gale the Griffin,
# 240 x 240 pixels = 115,200 bytes) from flash, ten rows at a time, and draws
# it in the middle of the screen. edition.py and the picture come from the
# computer: server/make_edition.py and server/mascot_check.py --write. Needs
# the display.
#
# PASS: Gale appears centered inside the round screen with the gold ring
# complete and nothing cut off by the bezel, and the time printed is under
# 100 ms. If the picture is sheared, MASCOT_SIZE in edition.py does not match
# the file; if the colors are wrong, re-make the file with mascot_check.py.

NAME = "01-show-school-mascot.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import os
import time

import config
import edition


def show_image(display, path, x, y, size, rows_per_chunk=10):
    """Chapter 6's loader: read a few rows at a time, never the whole file."""
    chunk = bytearray(size * rows_per_chunk * 2)
    view = memoryview(chunk)
    with open(path, "rb") as f:
        for row in range(0, size, rows_per_chunk):
            rows = min(rows_per_chunk, size - row)
            f.readinto(view[:size * rows * 2])
            display.blit_buffer(view[:size * rows * 2], x, y + row, size, rows)


size = edition.MASCOT_SIZE
expected = size * size * 2
actual = os.stat(edition.MASCOT_FILE)[6]
print("{} is {} bytes (expect {} for {} x {})".format(edition.MASCOT_FILE, actual, expected, size, size))
if actual != expected:
    raise SystemExit("File size does not match MASCOT_SIZE in edition.py.")

# The image is a circle drawn inside its square. It must also fit inside the
# glass's visible circle, SAFE_RADIUS (168) around the center.
x = (config.WIDTH - size) // 2
y = (config.HEIGHT - size) // 2
print("Image radius {} px; the visible radius is {} px: {}".format(
    size // 2, config.SAFE_RADIUS, "fits" if size // 2 <= config.SAFE_RADIUS else "WILL BE CUT"))

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

start = time.ticks_ms()
show_image(display, edition.MASCOT_FILE, x, y, size)
elapsed = time.ticks_diff(time.ticks_ms(), start)
print("drew {} in {} ms (wire-time minimum at 24 MHz is {:.1f} ms)".format(
    edition.MASCOT_NAME, elapsed, expected * 8 / 24000))
print("PASS if {} looks right.".format(edition.MASCOT_NAME) if elapsed < 100
      else "Slower than expected; check the SPI rate.")

# Try This
#   1. Re-run server/mascot_check.py --write after setting size = 336 in
#      agent.toml, then make_edition.py. The picture now fills the visible circle.
#      Does the load time grow in proportion to the byte count?
#   2. Set size = 120. How much flash does that save? (Chapter text has the table.)
