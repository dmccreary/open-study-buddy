# Chapter 16, Test 02: The school's splash screen
# Draws the mascot, the school name in the school's accent color, and the slogan,
# and CHECKS that every piece lies inside the round screen's visible circle
# before drawing it. Everything comes from edition.py, which is generated from
# agent.toml. Needs the display and griffin.rgb565.
#
# PASS: the printout says every item is inside the safe circle, and on the
# screen nothing is clipped by the bezel. Change the school name in agent.toml
# to a long one, re-run make_edition.py and upload: the check names the line that
# no longer fits.

NAME = "02-edition-splash.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math

import config
import edition

SMALL = config.SMALL_FONT       # 8 x 16
FONT_W = 8
FONT_H = 16


def inside_safe_circle(x, y, w, h):
    """True if all four corners of the box are inside the visible circle."""
    for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        if math.sqrt((cx - config.CENTER_X) ** 2 + (cy - config.CENTER_Y) ** 2) > config.SAFE_RADIUS:
            return False
    return True


def show_image(display, path, x, y, size, rows_per_chunk=10):
    chunk = bytearray(size * rows_per_chunk * 2)
    view = memoryview(chunk)
    with open(path, "rb") as f:
        for row in range(0, size, rows_per_chunk):
            rows = min(rows_per_chunk, size - row)
            f.readinto(view[:size * rows * 2])
            display.blit_buffer(view[:size * rows * 2], x, y + row, size, rows)


size = edition.MASCOT_SIZE
IMAGE_Y = 18
NAME_Y = IMAGE_Y + size + 8
SLOGAN_Y = NAME_Y + FONT_H + 4
parts = (
    ("mascot", (config.WIDTH - size) // 2, IMAGE_Y, size, size),
    ("name", (config.WIDTH - len(edition.SCHOOL_NAME) * FONT_W) // 2, NAME_Y,
     len(edition.SCHOOL_NAME) * FONT_W, FONT_H),
    ("slogan", (config.WIDTH - len(edition.SLOGAN) * FONT_W) // 2, SLOGAN_Y,
     len(edition.SLOGAN) * FONT_W, FONT_H),
)

# The mascot is a circle inside its square, so test its circle, not its corners.
all_fit = True
print()
for label, x, y, w, h in parts:
    if label == "mascot":
        far = math.sqrt((x + w // 2 - config.CENTER_X) ** 2 + (y + h // 2 - config.CENTER_Y) ** 2) + w // 2
        ok = far <= config.SAFE_RADIUS
        print("{:<7} circle reaches {:.0f} px from the center: {}".format(label, far, "inside" if ok else "OUTSIDE"))
    else:
        ok = inside_safe_circle(x, y, w, h)
        print("{:<7} {:>3} x {:<2} box at {:>3},{:<3}: {}".format(label, w, h, x, y, "inside" if ok else "OUTSIDE"))
    all_fit = all_fit and ok

if not all_fit:
    raise SystemExit("Something is outside the visible circle. Shorten the text or shrink the mascot.")

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
show_image(display, edition.MASCOT_FILE, parts[0][1], parts[0][2], size)
config.centered_text(display, SMALL, edition.SCHOOL_NAME, NAME_Y, edition.ACCENT, config.BLACK)
config.centered_text(display, SMALL, edition.SLOGAN, SLOGAN_Y, config.WHITE, config.BLACK)
print()
print("PASS: all {} items inside the safe circle. Look at the screen.".format(len(parts)))

# Try This
#   1. Change the slogan in agent.toml to a 40-character sentence, run
#      make_edition.py and upload edition.py. Which check fails first?
#   2. Use config.BIG_FONT (16 x 32) for the name. How many characters fit on one
#      line at that y? (Hint: the visible chord is shorter near the bottom.)
