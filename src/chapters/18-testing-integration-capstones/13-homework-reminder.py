# Chapter 18, Capstone 13: Homework reminder buddy
# Shows the next TEST: and DUE: items and says how soon each is. A beep announces
# an item the first time it is tomorrow or today.
#
#   MODE  next item           UP / DOWN  move "today" forward / back one day
#
# WHERE THE EVENTS COME FROM (it degrades gracefully, so it always works):
#   1. events.json on the Pico, if you copied one (see tools/trim_events.py)
#   2. otherwise a short list built into this file
# Chapter 16 shows the buddy server reading the same kind of file (and a
# calendar feed) and answering for the device. When your server is ready, replace
# load_events() with a request to it; nothing else in this program changes.
#
# WHAT "TODAY" IS: a Pico has no calendar until you give it one. Setting the
# clock from the network is an extension (config.py already has TIMEZONE_HOURS
# and USE_US_DST for it). Here "today" starts at the Cedar Ridge demo date and
# the UP and DOWN buttons move it, so the program works with no network at all.
#
# Needs: display, three buttons. Optional: speaker for the beep.
# The Cedar Ridge events are synthetic: no real student information is used.
#
# PASS: at 2026-10-19 the first item is "TOMORROW" with the Algebra II test;
# UP moves to the next day and the English draft becomes tomorrow, with a beep.

NAME = "13-homework-reminder.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import json
import time

import config
import detectors as dt

BIG, SMALL = config.BIG_FONT, config.SMALL_FONT
DIM = config.color565(150, 150, 150)
START_DATE = "2026-10-19"
DEBOUNCE_MS = 30

BUILT_IN = [
    {"id": "b1", "title": "TEST: Algebra II Unit 3 - Quadratics", "date": "2026-10-20"},
    {"id": "b2", "title": "DUE: English 10 personal narrative draft", "date": "2026-10-21"},
    {"id": "b3", "title": "DUE: Biology osmosis lab report", "date": "2026-10-22"},
]


def load_events():
    try:
        with open("events.json") as f:
            data = json.load(f)
        events = data["events"] if isinstance(data, dict) else data
        print("events: {} from events.json".format(len(events)))
        return events
    except (OSError, ValueError, KeyError):
        print("events: using the built-in list ({} items)".format(len(BUILT_IN)))
        return BUILT_IN


try:
    from listen import beep
except ImportError:
    def beep():
        pass

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
buttons = config.init_buttons()
events = load_events()
today = dt.parse_date(START_DATE)
reminders = dt.Reminders(alert_days=1)
index = 0
changed_at = [0, 0, 0]
is_down = [False, False, False]


def put(text, y, font, color, width):
    config.centered_text(display, font, text.center(width), y, color)


def redraw(items):
    put(dt.date_text(today), 80, SMALL, DIM, 20)
    if not items:
        put("NOTHING DUE", 130, BIG, config.GREEN, 14)
        put("in the next 7 days", 175, SMALL, DIM, 24)
        put("", 205, SMALL, DIM, 24)
        return
    left, kind, title, _ = items[index % len(items)]
    color = config.RED if left <= 1 else config.YELLOW if left <= 3 else config.GREEN
    put(dt.when_text(left), 130, BIG, color, 14)
    put(kind, 175, SMALL, config.WHITE, 24)
    put(dt.short_title(title, 22), 205, SMALL, config.WHITE, 24)
    put("{} of {}".format(index % len(items) + 1, len(items)), 245, SMALL, DIM, 24)


items = dt.upcoming(events, today)
redraw(items)
for left, kind, title, ident in reminders.new_alerts(items):
    print("ALERT:", dt.when_text(left), kind, dt.short_title(title))
    beep()
while True:
    now = time.ticks_ms()
    press = None
    for i in range(3):
        down = buttons[i].value() == 0
        if down != is_down[i] and time.ticks_diff(now, changed_at[i]) > DEBOUNCE_MS:
            is_down[i] = down
            changed_at[i] = now
            if down:
                press = i
    if press is not None:
        if press == 0:
            index += 1
        else:
            today += 1 if press == 1 else -1
            index = 0
        items = dt.upcoming(events, today)
        redraw(items)
        for left, kind, title, ident in reminders.new_alerts(items):
            print("ALERT:", dt.when_text(left), kind, dt.short_title(title))
            beep()
    time.sleep_ms(5)

# Try This
#   1. Copy a trimmed events.json to the Pico (tools/trim_events.py) and rerun.
#   2. Move "today" to 2026-10-26. What is the first item? Is that right?
#   3. Add a third alert level for "in 3 days" and test it with user testing.
