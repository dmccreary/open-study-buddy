# device.py -- the five-mode state machine from Chapter 7
#
# Pure Python: no hardware, so it also runs on your computer. Feed it button
# events with on_button(name, event, held_ms) and internal events with
# on_internal(what). Read .state, .volume, .item and .theme.
#
# Modes: CLOCK, LISTENING, THINKING, SPEAKING, SETTINGS.
# Rules are the table in the chapter section "The State Machine".

CLOCK, LISTENING, THINKING, SPEAKING, SETTINGS = range(5)
NAMES = ("CLOCK", "LISTENING", "THINKING", "SPEAKING", "SETTINGS")
ITEMS = ("Volume", "Theme")
THEMES = ("NIGHT", "DAY")
LONG_MS = 800       # a hold this long is a "long" press
MIN_MS = 200        # holding MODE for less than this is a bump, not a question


class Device:
    def __init__(self):
        self.state = CLOCK
        self.volume = 40
        self.theme = 0
        self.item = 0

    def go(self, state):
        # A real build also redraws the status region and sets the LED here.
        self.state = state

    def step_volume(self, direction):
        self.volume = max(0, min(100, self.volume + 10 * direction))

    def snapshot(self):
        """Everything the screen shows, as one tuple, so a loop can tell
        whether anything changed."""
        return (self.state, self.volume, self.item, self.theme)

    def on_button(self, name, event, held_ms=0):
        s = self.state
        step = 1 if name == "up" else -1
        if s == CLOCK:
            if name == "mode" and event == "press":
                self.go(LISTENING)
            elif name == "up" and event == "long":
                self.go(SETTINGS)
            elif name != "mode" and event == "release" and held_ms < LONG_MS:
                self.step_volume(step)
        elif s == LISTENING:
            if name == "mode" and event == "release":
                self.go(THINKING if held_ms >= MIN_MS else CLOCK)
        elif s == THINKING:
            if name == "mode" and event == "press":
                self.go(CLOCK)
        elif s == SPEAKING:
            if name == "mode" and event == "press":
                self.go(CLOCK)
            elif name != "mode" and event == "press":
                self.step_volume(step)
        elif s == SETTINGS:
            if name == "mode" and event == "long":
                self.go(CLOCK)
            elif name == "mode" and event == "release" and held_ms < LONG_MS:
                self.item = (self.item + 1) % len(ITEMS)
            elif name != "mode" and event == "press":
                if self.item == 0:
                    self.step_volume(step)
                else:
                    self.theme = 1 - self.theme

    def on_internal(self, what):
        if self.state == LISTENING and what == "full":
            self.go(THINKING)
        elif self.state == THINKING and what == "reply":
            self.go(SPEAKING)
        elif self.state == SPEAKING and what == "done":
            self.go(CLOCK)
