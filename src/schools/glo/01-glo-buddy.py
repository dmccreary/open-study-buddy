# GLO Study Buddy demo: "Groves Buddy" with upcoming events
# Shows the GLO Coding Club griffin in a round badge at the top, the words
# "Groves Buddy" under it, and a mock-up of three events coming up this week,
# on a Groves blue round screen. Needs the display and griffin-140.rgb565 on
# the Pico (upload.sh copies both).
#
# The events are typed in below as a mock-up, not read from a GLO calendar.
# This is a picture of what the buddy will look like, not the calendar agent
# itself (that is Chapter 16).
#
# PASS: the griffin badge is centered near the top, the title is white, the
# three events and "Groves Learning Organization" are inside the glass
# and none of the letters are cut off by the bezel.
# If the picture looks sheared, MASCOT_SIZE does not match the size
# tools/mascot-to-rgb565.py made the file at. If the colors are wrong (red
# and blue swapped), re-create the file with that tool.

NAME = "01-glo-buddy.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import os

import config

PATH = "griffin-140.rgb565"
MASCOT_SIZE = 140

# GLO colors, from groveslearning.org (primary blue, accent cyan).
# BACKGROUND must match the one in tools/mascot-to-rgb565.py.
BACKGROUND = config.color565(0x00, 0x64, 0x9B)   # Groves blue
CYAN = config.color565(0x01, 0xBA, 0xDE)
WHITE = config.color565(0xFF, 0xFF, 0xFF)

# Mock-up events: (day, what). Keep each line under 33 letters; the third
# line is low on the round glass, where it is narrower.
EVENTS = [
    ("Wednesday:", "Coding Club"),
    ("Thursday:", "Calculus Quiz"),
    ("Friday:", "Harvest Dance"),
]


def show_image(display, path, x, y, width, height, rows_per_chunk=10):
    chunk = bytearray(width * rows_per_chunk * 2)
    view = memoryview(chunk)
    with open(path, "rb") as f:
        for row in range(0, height, rows_per_chunk):
            rows = min(rows_per_chunk, height - row)
            f.readinto(view[:width * rows * 2])
            display.blit_buffer(view[:width * rows * 2], x, y + row, width, rows)


def event_line(display, font, day, what, y):
    """Draw "day what" centered at row y, the day in cyan, the rest in white."""
    x = (config.WIDTH - (len(day) + 1 + len(what)) * font.WIDTH) // 2
    display.text(font, day, x, y, CYAN, BACKGROUND)
    x += (len(day) + 1) * font.WIDTH
    display.text(font, what, x, y, WHITE, BACKGROUND)


expected = MASCOT_SIZE * MASCOT_SIZE * 2
actual = os.stat(PATH)[6]
print("{} is {} bytes (expect {})".format(PATH, actual, expected))
if actual != expected:
    raise SystemExit("File size does not match MASCOT_SIZE x MASCOT_SIZE.")

display = config.init_display()
config.set_backlight(True)
display.fill(BACKGROUND)

show_image(display, PATH, (config.WIDTH - MASCOT_SIZE) // 2, 12,
           MASCOT_SIZE, MASCOT_SIZE)

# BIG_FONT is 16 x 32: "Groves Buddy" is 12 letters, 192 pixels wide.
config.centered_text(display, config.BIG_FONT, "Groves Buddy",
                     160, WHITE, BACKGROUND)

# A short cyan rule between the title and the events.
display.fill_rect(120, 200, 120, 2, CYAN)

y = 212
for day, what in EVENTS:
    event_line(display, config.SMALL_FONT, day, what, y)
    y += 24

config.centered_text(display, config.SMALL_FONT, "Groves Learning Organization",
                     292, CYAN, BACKGROUND)

print("Drawn: look at the screen.")

# Try This
#   1. Add a fourth event under Friday. Does it fit, or does the bezel cut it
#      off? (Each line down is narrower than the one above it.)
#   2. Shorten the days to "Wed", "Thu" and "Fri". Which looks better from
#      across the room?
#   3. Swap the colors: make the days white and the events cyan. Which is
#      easier to read?
