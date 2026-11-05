# demo_quote.py -- demo 9 of 20-demo-template.py: the quote of the day.
#
# One of twenty quotes about coding and learning, picked at random, word-
# wrapped to fit the ROUND glass: demo_kit.wrap_in_circle() works out how
# many letters fit on each line from where that line sits on the circle,
# and uses the big font when the quote is short enough.
#
#   UP or DOWN   another quote

import random
import time

import config
from demo_kit import (BLACK, WHITE, DIM, SMALL, BIG, CX, centered,
                      text_block, menu_hint)

# (quote, who said it). Keep the quotes short: the round screen holds
# about 150 letters in the small font.
QUOTES = (
    ("Knowledge representation is the key to AI.", ""),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("Program testing can be used to show the presence of bugs, but never "
     "to show their absence!", "Edsger W. Dijkstra"),
    ("Programs must be written for people to read, and only incidentally "
     "for machines to execute.", "Harold Abelson"),
    ("Debugging is twice as hard as writing the code in the first place.",
     "Brian Kernighan"),
    ("The only way to learn a new programming language is by writing "
     "programs in it.", "Dennis Ritchie"),
    ("Any fool can write code that a computer can understand. Good "
     "programmers write code that humans can understand.", "Martin Fowler"),
    ("The most dangerous phrase in the language is: we've always done it "
     "this way.", "Grace Hopper"),
    ("Everybody in this country should learn to program a computer, "
     "because it teaches you how to think.", "Steve Jobs"),
    ("Any sufficiently advanced technology is indistinguishable from magic.",
     "Arthur C. Clarke"),
    ("Computers are good at following instructions, but not at reading "
     "your mind.", "Donald Knuth"),
    ("Code is like humor. When you have to explain it, it's bad.",
     "Cory House"),
    ("Every bug you fix teaches you something new.", ""),
    ("A computer will do what you tell it to do, not what you want it "
     "to do.", ""),
    ("Small steps, tested often, build big programs.", ""),
    ("The expert at anything was once a beginner.", ""),
)

TITLE_Y = 38
QUOTE_CENTER_Y = 160
MENU_Y = 304


def start(display, kit, saved):
    global _display, _kit, last
    _display = display
    _kit = kit
    random.seed(time.ticks_us())
    last = None if saved is None else saved.get("last")
    show(pick())


def pick():
    """A random quote, never the same one twice in a row."""
    global last
    i = last
    while i == last:
        i = random.randrange(len(QUOTES))
    last = i
    return QUOTES[i]


def show(entry):
    words, who = entry
    display = _display
    display.fill(BLACK)
    centered(display, SMALL, "QUOTE OF THE DAY", TITLE_Y, config.YELLOW)
    # Leave room under the quote for the name: wrap it in a circle a little
    # smaller than the glass, and a little above the middle.
    top, bottom = text_block(display, '"' + words + '"', QUOTE_CENTER_Y,
                             WHITE, fonts=((BIG, 4), (SMALL, 7)),
                             radius=config.SAFE_RADIUS - 6)
    if who:
        centered(display, SMALL, "- " + who, min(bottom + 10, 270),
                 config.CYAN)
    centered(display, SMALL, "UP: another", MENU_Y - 22, DIM)
    menu_hint(display, MENU_Y)


def update(now):
    if _kit.up.pressed(now) or _kit.down.pressed(now):
        show(pick())


def stop():
    return {"last": last}
