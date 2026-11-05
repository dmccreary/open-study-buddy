# Lab 11: What a Button Press Really Looks Like
# Press the buttons and watch three numbers for each one: how many times
# the pin changed, how many presses a naive program would count, and how
# many presses there really were.
#
# THE IDEA: EDGES AND BOUNCE.
#
#   LEVEL vs EDGE. button.value() tells you the LEVEL: 0 while held, 1 when
#   not. A program usually wants the EDGE: the moment it went from 1 to 0.
#   So remember the last reading, and act only when the new one differs.
#
#   BOUNCE. A button is two bits of metal slapping together. For a few
#   milliseconds they rattle -- touching, springing apart, touching again --
#   and the pin flickers between 0 and 1. A fast loop sees every flicker as
#   a press.
#
#   DEBOUNCE. Only believe a new level once the pin has STAYED at it for
#   DEBOUNCE_MS. While the metal rattles, the pin never stays put that
#   long, so the rattle is ignored; once it settles, the press counts once.
#   People cannot press a button 30 times a second, so anything faster is
#   the metal, not the finger.
#
# This loop has no sleep in it, so it reads the pins as fast as it can and
# catches the bounces. (Cheap buttons bounce more. Some good ones hardly
# bounce at all -- try pressing slowly and hard, then quick and light.)
#
# Parts: the buttons and the display.
#
# PASS: each press adds 1 to "real", and "naive" is the same or higher. Any
# difference between them is bounce the debounce caught. The circle above
# each button fills while it is held.

NAME = "11-button-bounce.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import shapes

DEBOUNCE_MS = 30

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
NAMES = ("MODE", "UP", "DOWN")
COLUMN_X = (95, 180, 265)
LAMP_Y = 104

pins = config.init_buttons()
last_raw = [1, 1, 1]          # the last reading of each pin
changes = [0, 0, 0]           # every 1->0 or 0->1 the loop saw
naive = [0, 0, 0]             # 1->0 edges with no debounce at all
real = [0, 0, 0]              # debounced presses
steady = [1, 1, 1]            # the debounced level: what we believe
changed_at = [0, 0, 0]        # when the pin last changed at all

config.centered_text(display, SMALL, "BUTTON BOUNCE", 50, DIM)
for i in range(3):
    x = COLUMN_X[i]
    display.text(SMALL, NAMES[i], x - len(NAMES[i]) * 4, 72, config.WHITE,
                 config.BLACK)
for label, y in (("changes", 140), ("naive", 192), ("real", 244)):
    config.centered_text(display, SMALL, label, y, DIM)


def number(font, value, x, y, color):
    """A 3-digit number centered on x. "%3d" pads it with spaces, so it
    always covers the number that was there before."""
    display.text(font, "%3d" % (value % 1000), x - 3 * font.WIDTH // 2, y,
                 color, config.BLACK)


def show(i):
    """Redraw column i's three numbers and its lamp."""
    x = COLUMN_X[i]
    number(SMALL, changes[i], x, 156, DIM)
    number(SMALL, naive[i], x, 208, config.YELLOW)
    number(BIG, real[i], x, 260, config.GREEN)
    shapes.circle(display, x, LAMP_Y, 12,
                  config.CYAN if steady[i] == 0 else config.BLACK,
                  config.FILL)
    shapes.circle(display, x, LAMP_Y, 12, config.CYAN)


for i in range(3):
    show(i)

print("Press the buttons. Each line is one change the loop saw.")
while True:
    now = time.ticks_ms()
    for i in range(3):
        raw = pins[i].value()
        if raw != last_raw[i]:
            # An edge. Count it, every one, bounce or not...
            last_raw[i] = raw
            changed_at[i] = now
            changes[i] += 1
            if raw == 0:
                naive[i] += 1              # ...a naive program stops here
            print("{:<4} {}  changes {:3}  naive {:3}  real {:3}".format(
                NAMES[i], "down" if raw == 0 else "up  ", changes[i],
                naive[i], real[i]))
            show(i)

        # ...but only believe a new level once it has held still.
        if raw != steady[i] and time.ticks_diff(now, changed_at[i]) >= DEBOUNCE_MS:
            steady[i] = raw
            if raw == 0:
                real[i] += 1
                print("{:<4} PRESS #{}".format(NAMES[i], real[i]))
            show(i)

# Try This
#   1. Set DEBOUNCE_MS to 0. Does "real" now match "naive"?
#   2. Set DEBOUNCE_MS to 300. Every press still counts, but watch the
#      circle: how long after you press does it fill? That delay is the
#      price of a long debounce. What is the shortest one that still never
#      counts a bounce?
#   3. Add time.sleep_ms(50) at the bottom of the loop. Do the bounces
#      disappear? Why is that not a good fix? (Hint: try a very quick tap.)
