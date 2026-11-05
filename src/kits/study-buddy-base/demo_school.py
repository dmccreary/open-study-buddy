# demo_school.py -- demo 5 of 20-demo-template.py: the school calendar.
#
# A school's own Study Buddy: its mascot at the top, its name, and what is
# coming up this week. The school here, Owl Creek Middle School, is made
# up for the demo, and so are its events -- this is a picture of what the
# calendar agent of Chapter 16 will show, not the agent itself.
#
#   UP / DOWN   next / previous page of events (they also turn by
#               themselves every PAGE_MS)
#
# THE MASCOT. The owl is drawn from shapes (demo_icons.owl), so there is no
# file to upload. To show a real school's mascot instead, put a 140 x 140
# picture on the Pico as mascot-140.rgb565 -- the school-generator skill
# and each school's tools/mascot-to-rgb565.py in src/schools/ make one --
# and set the colors and words below to match that school.

import os
import time

import config
import demo_icons
from demo_kit import SMALL, BIG, CX, centered, menu_hint

SCHOOL = "Owl Creek Middle School"
BUDDY_NAME = "Owl Buddy"
MASCOT_FILE = "mascot-140.rgb565"
MASCOT_SIZE = 140

BACKGROUND = config.color565(0x0B, 0x2A, 0x55)     # school navy
DAY_COLOR = config.color565(0xFF, 0xC8, 0x3C)      # school gold
WHAT_COLOR = config.WHITE
NAME_COLOR = config.color565(0x9C, 0xC2, 0xFF)

# (day, what). Wednesday's Coding Club is on the first page. Keep each
# line under about 30 letters; the lowest line is where the glass is
# narrower.
EVENTS = (
    ("Wednesday:", "Coding Club!"),
    ("Thursday:", "Science Fair"),
    ("Friday:", "Pizza Day"),
    ("Monday:", "Spelling Bee"),
    ("Tuesday:", "Band Concert"),
    ("Thursday:", "Field Trip Forms Due"),
)
ROWS = 3
PAGE_MS = 5000

MASCOT_Y = 10
TITLE_Y = 152
RULE_Y = 190
EVENTS_Y = 200
ROW_PITCH = 24
SCHOOL_Y = 276
MENU_Y = 300


def start(display, kit, saved):
    global _display, _kit, page, turned_at
    _display = display
    _kit = kit
    display.fill(BACKGROUND)
    if not show_mascot_file(display):
        # The drawn owl paints its own pixels only, so its corners stay
        # the background color.
        demo_icons.owl(display, CX, 80, 1.15, BACKGROUND)
    centered(display, BIG, BUDDY_NAME, TITLE_Y, config.WHITE, BACKGROUND)
    display.fill_rect(CX - 70, RULE_Y, 140, 2, DAY_COLOR)
    centered(display, SMALL, SCHOOL, SCHOOL_Y, NAME_COLOR, BACKGROUND)
    menu_hint(display, MENU_Y, BACKGROUND)
    page = 0
    show_page()


def show_mascot_file(display):
    """Show mascot-140.rgb565 if it is on the Pico. Returns True if it was."""
    try:
        size = os.stat(MASCOT_FILE)[6]
    except OSError:
        return False
    if size != MASCOT_SIZE * MASCOT_SIZE * 2:
        print(MASCOT_FILE, "is the wrong size -- drawing the owl instead")
        return False
    rows = 10
    chunk = bytearray(MASCOT_SIZE * rows * 2)
    x = CX - MASCOT_SIZE // 2
    with open(MASCOT_FILE, "rb") as f:
        for row in range(0, MASCOT_SIZE, rows):
            f.readinto(chunk)
            display.blit_buffer(chunk, x, MASCOT_Y + row, MASCOT_SIZE, rows)
    return True


def pages():
    return (len(EVENTS) + ROWS - 1) // ROWS


def show_page():
    global turned_at
    display = _display
    display.fill_rect(30, EVENTS_Y, 300, ROWS * ROW_PITCH, BACKGROUND)
    for row in range(ROWS):
        i = page * ROWS + row
        if i >= len(EVENTS):
            break
        day, what = EVENTS[i]
        y = EVENTS_Y + row * ROW_PITCH
        x = (config.WIDTH - (len(day) + 1 + len(what)) * SMALL.WIDTH) // 2
        display.text(SMALL, day, x, y, DAY_COLOR, BACKGROUND)
        display.text(SMALL, what, x + (len(day) + 1) * SMALL.WIDTH, y,
                     WHAT_COLOR, BACKGROUND)
    turned_at = time.ticks_ms()


def update(now):
    global page
    step = 1 if _kit.up.pressed(now) else -1 if _kit.down.pressed(now) else 0
    if step == 0 and time.ticks_diff(now, turned_at) >= PAGE_MS:
        step = 1
    if step:
        page = (page + step) % pages()
        show_page()


def stop():
    return None
