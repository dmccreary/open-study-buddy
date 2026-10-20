# Chapter 18, Capstone 12: Study timer buddy
# A focus/break timer. MODE starts, pauses, and resumes; a long MODE press skips
# to the other phase; UP and DOWN change the focus length (5 to 60 minutes) while
# idle. A beep marks the end of each phase. The default is 25 minutes of focus
# and a 5 minute break, with a 15 minute break after every 4th focus: change them.
#
# Needs: display, three buttons, speaker. (The microphone is not used.)
# The logic is detectors.StudyTimer, tested in 09-detectors-test.py. This file
# only reads buttons, draws changed regions, and beeps.
#
# PASS: MODE starts the countdown; the time region updates once a second; MODE
# pauses and resumes; the beep sounds at 0:00; nothing else on the screen is
# redrawn when only the seconds change.

NAME = "12-study-timer.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
from detectors import StudyTimer, IDLE, FOCUS, BREAK
from listen import beep

BIG, SMALL = config.BIG_FONT, config.SMALL_FONT
DIM = config.color565(150, 150, 150)
LONG_MS = 800
DEBOUNCE_MS = 30

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
mode, up, down = config.init_buttons()
timer = StudyTimer(diff=time.ticks_diff, add=time.ticks_add)


def put(text, y, font, color, width):
    config.centered_text(display, font, text.center(width), y, color)


class Pad:
    """Turns raw pins into the press kinds StudyTimer understands."""

    def __init__(self):
        self.mode_down_at = None
        self.mode_long_sent = False
        self.state = {"up": False, "down": False}
        self.changed = {"up": 0, "down": 0}

    def poll(self, now):
        if mode.value() == 0:
            if self.mode_down_at is None:
                self.mode_down_at = now
                self.mode_long_sent = False
            elif not self.mode_long_sent and time.ticks_diff(now, self.mode_down_at) >= LONG_MS:
                self.mode_long_sent = True
                return "mode_long"
        elif self.mode_down_at is not None:
            held = time.ticks_diff(now, self.mode_down_at)
            was_long = self.mode_long_sent
            self.mode_down_at = None
            if not was_long and held >= DEBOUNCE_MS:
                return "mode"
        for name, pin in (("up", up), ("down", down)):
            is_down = pin.value() == 0
            if is_down != self.state[name] and \
                    time.ticks_diff(now, self.changed[name]) > DEBOUNCE_MS:
                self.state[name] = is_down
                self.changed[name] = now
                if is_down:
                    return name
        return None


def mmss(seconds):
    return "{:02d}:{:02d}".format(seconds // 60, seconds % 60)


LABEL = {IDLE: "READY", FOCUS: "FOCUS", BREAK: "BREAK"}
pad = Pad()
last = None
put("Study Buddy", 70, SMALL, DIM, 20)
while True:
    now = time.ticks_ms()
    kind = pad.poll(now)
    if kind:
        print("press:", kind, "->", timer.press(kind, now))
    event = timer.tick(now)
    if event:
        print("event:", event, " cycles:", timer.cycles)
        beep()
    snap = timer.snapshot(now)
    if snap != last:                                   # dirty-region rule
        phase, paused, seconds, cycles, focus_min = snap
        if last is None or last[0] != phase or last[1] != paused:
            label = "PAUSED" if paused else LABEL[phase]
            put(label, 100, BIG, config.YELLOW if phase == FOCUS else config.CYAN, 10)
        put(mmss(seconds), 150, BIG, config.WHITE, 8)
        if last is None or last[3] != cycles:
            put("done: {}".format(cycles), 215, SMALL, DIM, 12)
        last = snap
    time.sleep_ms(5)

# Try This
#   1. Set the focus length to 5 minutes and watch a whole cycle. Does the beep
#      come when you expect it?
#   2. Hold MODE during FOCUS. Does the break start on time? How would a
#      classmate know a long press is needed? (User testing, below.)
#   3. Add the microphone: hold UP to ask "how long is left?" using the
#      push-to-talk path of Chapters 11 and 14.
