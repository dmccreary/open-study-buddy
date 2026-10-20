# listening_indicator.py -- Chapter 17: one place that opens the microphone
#
# The rule this file enforces: THE LISTENING INDICATOR IS DRIVEN BY THE SAME
# CODE THAT OPENS THE MICROPHONE. Nothing else in the program may open it.
#
#   start():  1. light the indicator   2. open the microphone
#   stop():   1. close the microphone  2. only then turn the indicator off
#
# So at every instant, "microphone open" implies "indicator on". If opening
# fails, the indicator goes back off. If closing fails, the indicator STAYS on,
# because we cannot prove the microphone is closed (fail toward telling the
# truth). A mute switch is checked before every open and every read.
#
# No hardware is imported here, so this file runs on a computer too. The
# hardware is passed in: see 02-indicator-demo.py for the real parts and
# 03-indicator-test.py for fakes.

OFF, LISTENING, MUTED = "off", "listening", "muted"


class LedIndicator:
    """The onboard LED: on only while the microphone is open."""

    def __init__(self, pin):
        self.pin = pin

    def show(self, state):
        self.pin.value(1 if state == LISTENING else 0)


class StatusBarIndicator:
    """The 120 x 20 status bar region from Chapter 6 (x=120, y=30).
    Text AND background change, so the state never depends on color alone."""

    X, Y, W, H = 120, 30, 120, 20

    def __init__(self, display, config):
        self.display = display
        self.config = config
        self.last = None

    def show(self, state):
        if state == self.last:          # dirty-region rule: draw on change only
            return
        self.last = state
        c = self.config
        if state == LISTENING:
            text, back, fore = "LISTENING", c.RED, c.WHITE
        elif state == MUTED:
            text, back, fore = "MIC OFF", c.GRAY, c.WHITE
        else:
            text, back, fore = "", c.BLACK, c.WHITE
        self.display.fill_rect(self.X, self.Y, self.W, self.H, back)
        if text:
            c.centered_text(self.display, c.SMALL_FONT, text, self.Y + 2,
                            fore, back)


class Listener:
    """Owns the microphone. Everything else asks the Listener for audio."""

    def __init__(self, open_mic, indicators, mute_pin=None):
        self._open_mic = open_mic        # function: returns an I2S-like object
        self._indicators = indicators    # list of objects with .show(state)
        self._mute_pin = mute_pin        # reads 0 when the mute switch is on
        self._mic = None
        self.state = OFF
        self._set(OFF)

    def _set(self, state):
        self.state = state
        for indicator in self._indicators:
            indicator.show(state)

    def is_muted(self):
        return self._mute_pin is not None and self._mute_pin.value() == 0

    def is_open(self):
        return self._mic is not None

    def start(self):
        """Returns True if the microphone is now open."""
        if self._mic is not None:
            return True
        if self.is_muted():
            self._set(MUTED)
            return False
        self._set(LISTENING)             # 1. tell the truth first
        try:
            self._mic = self._open_mic() # 2. then listen
        except Exception:
            self._mic = None
            self._set(OFF)               # it never opened, so say so
            raise
        return True

    def stop(self):
        if self._mic is not None:
            self._mic.deinit()           # if this raises, the indicator stays ON
            self._mic = None
        self._set(MUTED if self.is_muted() else OFF)

    def readinto(self, buf):
        """Fill buf from the microphone. Returns 0 (and closes) if muted."""
        if self._mic is None:
            return 0
        if self.is_muted():
            self.stop()
            return 0
        return self._mic.readinto(buf)
