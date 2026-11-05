# Lab 10: Flicker-Free Text -- Send Only What Changed
# Three counters run as fast as the Pico can draw them, each redrawn a
# different way. Watch which ones flicker, and read how long each update
# takes.
#
# THE IDEA: DRAWING IS SENDING. This display has no memory you can draw
# into first. Every pixel you draw is two bytes sent down the SPI wire,
# right then, and the glass shows it the moment it lands. So:
#
#   A. ERASE, THEN DRAW. Fill the box black, then draw the new number. For a
#      moment the box is empty, and the eye sees that as flicker. It also
#      sends every pixel twice.
#   B. OVERWRITE. The font draws each letter's background as well as its
#      shape, so drawing "0042" right over "0041" covers it completely. No
#      empty moment, and half the bytes.
#   C. ONLY WHAT CHANGED. Remember what is on the screen; going from 0041
#      to 0042, only the last digit changed, so send only that one.
#
# Parts: the display.
#
# PASS: counter A flickers, B and C do not, and C takes the least time per
# update (often several times less than A).

NAME = "10-flicker-free-text.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
DIGITS = 4
BOX_W = DIGITS * BIG.WIDTH
X = config.CENTER_X - BOX_W // 2
ROWS = (("A: erase, then draw", 70, config.RED),
        ("B: overwrite", 150, config.YELLOW),
        ("C: only what changed", 230, config.GREEN))

for label, y, color in ROWS:
    config.centered_text(display, SMALL, label, y - 22, DIM)

shown_c = None              # what counter C last put on the glass


def draw_a(text, y, color):
    display.fill_rect(X, y, BOX_W, BIG.HEIGHT, config.BLACK)
    display.text(BIG, text, X, y, color, config.BLACK)


def draw_b(text, y, color):
    display.text(BIG, text, X, y, color, config.BLACK)


def draw_c(text, y, color):
    global shown_c
    for i in range(DIGITS):
        if shown_c is None or text[i] != shown_c[i]:
            display.text(BIG, text[i], X + i * BIG.WIDTH, y, color,
                         config.BLACK)
    shown_c = text


DRAWERS = (draw_a, draw_b, draw_c)
totals = [0, 0, 0]          # microseconds spent, per method
count = 0
while True:
    text = "%04d" % (count % 10000)
    for i in range(3):
        label, y, color = ROWS[i]
        start = time.ticks_us()
        DRAWERS[i](text, y, color)
        totals[i] += time.ticks_diff(time.ticks_us(), start)
    count += 1

    if count % 100 == 0:        # every 100 updates, report the averages
        report = []
        for i in range(3):
            ms = totals[i] / 100 / 1000
            report.append("%.1f" % ms)
            config.centered_text(display, SMALL, "%5.1f ms per update" % ms,
                                 ROWS[i][1] + BIG.HEIGHT + 2, DIM)
            totals[i] = 0
        print("ms per update  A {}  B {}  C {}".format(*report))

# Try This
#   1. Count by 7 instead of 1 (count += 7). C now changes more digits each
#      time. How much slower does it get?
#   2. Make the numbers 8 digits long (DIGITS = 8 and "%08d"). Which method
#      suffers most? Why does A grow the fastest?
#   3. Work out the bytes for one big digit: 16 x 32 pixels x 2 bytes. At
#      24 MHz (3 million bytes a second), how long should one digit take?
#      Is the measured time close? Where does the rest go?
