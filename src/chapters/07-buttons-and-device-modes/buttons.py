# buttons.py -- the debounced Button class from Chapter 7
#
# Call update() often (every 5 ms is plenty). It returns one of:
#   "press"    the instant the button goes down (a debounced falling edge)
#   "long"     once, when the button has been held for long_ms
#   "release"  when the button comes back up; .held is how long it was down (ms)
#   None       nothing happened
#
# It never waits, so it is safe to call on three buttons inside one loop.

import time


class Button:
    def __init__(self, pin, debounce_ms=30, long_ms=800):
        self.pin = pin
        self.debounce_ms = debounce_ms
        self.long_ms = long_ms
        self.down = False
        self.changed_at = -1000
        self.pressed_at = 0
        self.long_sent = False
        self.held = 0

    def update(self):
        now = time.ticks_ms()
        is_down = self.pin.value() == 0
        if is_down != self.down and \
                time.ticks_diff(now, self.changed_at) > self.debounce_ms:
            self.down = is_down
            self.changed_at = now
            if is_down:
                self.pressed_at = now
                self.long_sent = False
                return "press"
            self.held = time.ticks_diff(now, self.pressed_at)
            return "release"
        if self.down and not self.long_sent and \
                time.ticks_diff(now, self.pressed_at) >= self.long_ms:
            self.long_sent = True
            return "long"
        return None
