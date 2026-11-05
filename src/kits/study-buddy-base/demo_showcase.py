# demo_showcase.py -- mode 0 of 20-demo-template.py: the showcase.
#
# A slide show of twelve screens. The first is the welcome (welcome.py):
# "Study Buddy Kit" and the parts in the kit. The other eleven are one for
# each demo, with an icon, a title, a sentence, and a hint. A new
# screen comes up every DWELL_MS, around and around, until someone walks
# up and presses a button:
#
#   short press   UP or MODE: next screen now.  DOWN: the screen before.
#   hold 1 s      ANY button: try the demo this screen is about.
#
# The showcase owns all three buttons (the template does not watch MODE
# here), and update() returns the number of the demo to launch.

import time

import config
import demo_icons
import welcome
from demo_kit import (BLACK, WHITE, DIM, FAINT, SMALL, BIG, CX, centered,
                      text_block)
from watchparts import SHORT, LONG

DWELL_MS = 6000

# (icon, title, what it does, title color). Screen n launches demo n.
# The first screen is drawn by welcome.py instead, and launches demo 1.
# Titles are 15 letters or fewer, so they fit across the glass in the big
# font.
SCREENS = (
    None,                                   # welcome.py
    ("clock", "Clock+Weather",
     "Sets itself over WiFi and shows today's and tomorrow's weather.",
     config.CYAN),
    ("bell", "Alarm Clock",
     "Set the alarm with the three buttons. It rings on the speaker.",
     demo_icons.GOLD),
    ("hourglass", "Timer",
     "Count down a homework sprint, then take a break.",
     demo_icons.SKY),
    ("stopwatch", "Stopwatch",
     "Time laps to a hundredth of a second.",
     config.GREEN),
    ("owl", "School News",
     "Your school mascot and what is coming up this week.",
     demo_icons.TAN),
    ("speaker", "Sound Lab",
     "Sine, square, triangle and sawtooth tones, then a tune.",
     config.CYAN),
    ("mic", "Listening",
     "A sound meter that jumps when you talk or clap.",
     config.GREEN),
    ("record", "Record & Play",
     "Say something for 3 seconds and hear it played back.",
     config.RED),
    ("quote", "Quote of Day",
     "Words of wisdom about coding and learning.",
     demo_icons.GOLD),
    ("bubble", "Spanish Quiz",
     "Hear a word in Spanish and pick what it means.",
     demo_icons.SPAIN_RED),
    ("book", "Vocabulary",
     "A new word and its meaning, flash card style.",
     demo_icons.SKY),
)

LABEL_Y = 30
ICON_Y = 98
TITLE_Y = 152
TEXT_CENTER_Y = 222
HINT_Y = 282
DOT_Y = 326
DOT_SPACING = 12


def start(display, kit, saved):
    global _display, _kit, index, shown_at
    _display = display
    _kit = kit
    index = 0 if saved is None else saved.get("index", 0) % len(SCREENS)
    show(index)


def show(i):
    global shown_at
    display = _display
    if i == 0:
        welcome.show(display)
    else:
        icon, title, words, color = SCREENS[i]
        display.fill(BLACK)
        centered(display, SMALL, "DEMO {} OF {}".format(i, len(SCREENS) - 1),
                 LABEL_Y, DIM)
        demo_icons.draw(icon, display, CX, ICON_Y)
        centered(display, BIG, title, TITLE_Y, color)
        text_block(display, words, TEXT_CENTER_Y, WHITE, fonts=(SMALL,),
                   max_lines=3)
    centered(display, SMALL, "Hold any button to try it", HINT_Y,
             config.YELLOW)
    draw_dots(i)
    shown_at = time.ticks_ms()


def draw_dots(current):
    import shapes
    x = CX - (len(SCREENS) - 1) * DOT_SPACING // 2
    for i in range(len(SCREENS)):
        shapes.circle(_display, x + i * DOT_SPACING, DOT_Y, 3,
                      WHITE if i == current else FAINT, config.FILL)


def update(now):
    """Returns the number of a demo to launch, or None."""
    global index
    for button, step in ((_kit.mode, 1), (_kit.up, 1), (_kit.down, -1)):
        press = button.short_or_long(now)
        if press == LONG:
            return index if index > 0 else 1
        if press == SHORT:
            index = (index + step) % len(SCREENS)
            show(index)
            return None
    if time.ticks_diff(now, shown_at) >= DWELL_MS:
        index = (index + 1) % len(SCREENS)
        show(index)
    return None


def stop():
    return {"index": index}
