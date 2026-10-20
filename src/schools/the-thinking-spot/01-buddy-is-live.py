# Thinking Spot Study Buddy demo: "The Thinking Spot Buddy is Live"
# Shows the Thinking Spot tree logo with the words "The Thinking Spot" and
# "Buddy is Live" under it, on a white round screen. Needs the display and
# tree-logo.rgb565 on the Pico (upload.sh copies both).
#
# PASS: the tree logo is centered near the top, the two lines of text are
# inside the glass and none of the letters are cut off by the bezel.
# If the picture looks sheared, LOGO_WIDTH / LOGO_HEIGHT do not match the size
# tools/logo-to-rgb565.py made the file at. If the colors are wrong (red and
# blue swapped), re-create the file with that tool.

NAME = "01-buddy-is-live.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import os

import config

PATH = "tree-logo.rgb565"
LOGO_WIDTH = 150
LOGO_HEIGHT = 170

# Colors sampled from the logo, so the text matches the trunk and the leaves.
WHITE = config.WHITE
PURPLE = config.color565(94, 43, 85)
GREEN = config.color565(125, 200, 30)


def show_image(display, path, x, y, width, height, rows_per_chunk=10):
    chunk = bytearray(width * rows_per_chunk * 2)
    view = memoryview(chunk)
    with open(path, "rb") as f:
        for row in range(0, height, rows_per_chunk):
            rows = min(rows_per_chunk, height - row)
            f.readinto(view[:width * rows * 2])
            display.blit_buffer(view[:width * rows * 2], x, y + row, width, rows)


expected = LOGO_WIDTH * LOGO_HEIGHT * 2
actual = os.stat(PATH)[6]
print("{} is {} bytes (expect {})".format(PATH, actual, expected))
if actual != expected:
    raise SystemExit("File size does not match LOGO_WIDTH x LOGO_HEIGHT.")

display = config.init_display()
config.set_backlight(True)
display.fill(WHITE)

show_image(display, PATH, (config.WIDTH - LOGO_WIDTH) // 2, 20,
           LOGO_WIDTH, LOGO_HEIGHT)

# BIG_FONT is 16 x 32: "The Thinking Spot" is 17 letters, 272 pixels wide.
config.centered_text(display, config.BIG_FONT, "The Thinking Spot",
                     202, PURPLE, WHITE)
config.centered_text(display, config.BIG_FONT, "Buddy is Live",
                     240, GREEN, WHITE)

print("Drawn: look at the screen.")

# Try This
#   1. Change the second line to "Buddy says hi". How many letters fit on the
#      second line before the bezel cuts it off? (It is lower, so the glass is
#      narrower there than on the first line.)
#   2. Swap the colors of the two lines.
#   3. Use docs/schools/the-thinking-spot/logo-no-text.jpg instead (it is
#      square) and change WIDTH and HEIGHT in tools/logo-to-rgb565.py.
