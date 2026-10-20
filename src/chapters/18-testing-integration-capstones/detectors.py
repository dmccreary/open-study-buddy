# detectors.py -- Chapter 18: the logic of four capstone projects, with no hardware
#
# Everything here is plain Python on numbers, so it runs on a computer, where
# 09-detectors-test.py feeds it synthetic sound and scripted button presses.
# The capstone programs (10 to 13) connect these classes to the real microphone,
# display, and buttons.
#
#   bits_from_samples   a frame of 24-bit samples -> loudness in "bits" (log2 of
#                       the average distance from the middle: kit test 06)
#   ClapDetector        a short loud burst that rises from, and falls back to, the
#                       calibrated floor
#   NoiseMonitor        smoothed level -> QUIET / TALKING / LOUD, and how long in each
#   StudyTimer          a focus/break state machine driven by a deadline
#   Reminders           which TEST: and DUE: events are coming up, announced once
#
# No threshold below is a measured fact about a classroom. Each one is either a
# parameter you set after running the calibration, or a starting value marked
# "tune me" that user testing should change.

import math

LOG2 = math.log(2)
FRAME_MS = 40                         # 512 samples at 12,800 Hz (Chapter 8)


def bits_from_samples(samples):
    n = len(samples)
    middle = sum(samples) // n                       # the DC offset
    average = sum(abs(s - middle) for s in samples) // n
    return math.log(average + 1) / LOG2


def mean_std(values):
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return mean, math.sqrt(var)


# ---------------------------------------------------------------------------
class ClapDetector:
    """update(bits) once per frame. Returns True on the frame a clap ENDS.

    A clap is: loud (jump bits above the floor), for only 1 to max_run frames,
    then back below. Speech stays loud for many frames, so it is not a clap.
    A steady loud sound (a fan switching on) makes the floor drift up to it, so
    it stops counting as loud. After a clap, refractory frames are ignored.

    jump = max(jump_min, jump_k x the spread of the quiet frames), so a noisier
    room needs a bigger jump. jump_min=2.0 bits (the SPEECH_ABOVE_FLOOR of kit
    test 06) means 4 times the average level of the quiet room.
    """

    def __init__(self, floor, spread, jump_min=2.0, jump_k=4.0, max_run=2,
                 refractory=6, adapt_after=25, alpha=0.05):
        self.baseline = floor
        self.jump = max(jump_min, jump_k * spread)
        self.max_run = max_run
        self.refractory = refractory
        self.adapt_after = adapt_after
        self.alpha = alpha
        self.run = 0
        self.cool = 0
        self.claps = 0
        self.peak = 0.0                 # loudest frame of the current loud run
        self.last_peak = 0.0            # ... of the last clap

    def update(self, bits):
        if self.cool > 0:
            self.cool -= 1
        if bits >= self.baseline + self.jump:
            self.run += 1
            self.peak = max(self.peak, bits)
            if self.run >= self.adapt_after:              # a new normal, not a clap
                self.baseline += 0.2 * (bits - self.baseline)
            return False
        clap = False
        if 1 <= self.run <= self.max_run and self.cool == 0:
            clap = True
            self.claps += 1
            self.last_peak = self.peak
            self.cool = self.refractory
        self.run = 0
        self.peak = 0.0
        self.baseline += self.alpha * (bits - self.baseline)   # follow slow changes
        return clap


# ---------------------------------------------------------------------------
QUIET, TALKING, LOUD = "QUIET", "TALKING", "LOUD"


class NoiseMonitor:
    """Level only. It keeps a smoothed number and three counters. It never
    keeps audio, and it cannot: it is handed one number per frame.

    bands are in bits above the floor: +2 bits is 4 times the quiet room's
    average level (about 12 dB), +4 bits is 16 times (about 24 dB). They are
    RELATIVE to this microphone and this room, not sound-pressure decibels.
    'Tune me': the right bands depend on your classroom and your rules.
    """

    def __init__(self, floor, talking=2.0, loud=4.0, tau_ms=1000, dwell=12):
        self.floor = floor
        self.talking = talking
        self.loud = loud
        self.alpha = 1 - math.exp(-FRAME_MS / tau_ms)
        self.dwell = dwell
        self.ema = floor
        self.band = QUIET
        self._candidate = QUIET
        self._count = 0
        self.frames = {QUIET: 0, TALKING: 0, LOUD: 0}
        self.peak = floor

    def _band_for(self, level):
        above = level - self.floor
        if above >= self.loud:
            return LOUD
        if above >= self.talking:
            return TALKING
        return QUIET

    def update(self, bits):
        self.ema += self.alpha * (bits - self.ema)
        if bits > self.peak:
            self.peak = bits
        want = self._band_for(self.ema)
        if want == self.band:
            self._count = 0
        else:
            if want != self._candidate:
                self._candidate = want
                self._count = 0
            self._count += 1
            if self._count >= self.dwell:          # held long enough: switch
                self.band = want
                self._count = 0
        self.frames[self.band] += 1
        return self.band

    def fraction(self, span=6.0):
        """0.0 to 1.0 for a bar: how far the smoothed level is above the floor."""
        return max(0.0, min(1.0, (self.ema - self.floor) / span))

    def summary(self):
        """Seconds spent in each band since the last call, then start over."""
        out = {b: n * FRAME_MS / 1000 for b, n in self.frames.items()}
        self.frames = {QUIET: 0, TALKING: 0, LOUD: 0}
        return out


# ---------------------------------------------------------------------------
IDLE, FOCUS, BREAK = "IDLE", "FOCUS", "BREAK"


class StudyTimer:
    """A focus/break timer. Time comes from the caller (now_ms). On the Pico
    pass diff=time.ticks_diff and add=time.ticks_add, so the millisecond
    counter's wrap-around is handled (Chapter 7); on a computer the defaults
    are plain subtraction and addition."""

    def __init__(self, focus_min=25, break_min=5, long_break_min=15, long_every=4,
                 diff=lambda a, b: a - b, add=lambda a, b: a + b):
        self.focus_min = focus_min
        self.break_min = break_min
        self.long_break_min = long_break_min
        self.long_every = long_every
        self.diff = diff
        self.add = add
        self.phase = IDLE
        self.paused = False
        self.cycles = 0                    # focus periods completed
        self._end = 0
        self._left_ms = 0                  # remaining time while paused

    def _begin(self, phase, minutes, now):
        self.phase = phase
        self.paused = False
        self._end = self.add(now, minutes * 60000)

    def remaining_ms(self, now):
        if self.phase == IDLE:
            return self.focus_min * 60000
        if self.paused:
            return self._left_ms
        return max(0, self.diff(self._end, now))

    def press(self, kind, now):
        """kind: 'mode' (start, pause, resume), 'mode_long' (skip to the other
        phase, or reset when idle), 'up' / 'down' (change focus minutes when IDLE).
        Returns an event name or None."""
        if kind == "mode":
            if self.phase == IDLE:
                self._begin(FOCUS, self.focus_min, now)
                return "focus_started"
            if self.paused:
                self.paused = False
                self._end = self.add(now, self._left_ms)
                return "resumed"
            self._left_ms = self.remaining_ms(now)
            self.paused = True
            return "paused"
        if kind == "mode_long":
            if self.phase == FOCUS:
                self._begin(BREAK, self.break_min, now)
                return "break_started"
            if self.phase == BREAK:
                self._begin(FOCUS, self.focus_min, now)
                return "focus_started"
            return None
        if kind in ("up", "down") and self.phase == IDLE:
            step = 5 if kind == "up" else -5
            self.focus_min = max(5, min(60, self.focus_min + step))
            return "length_changed"
        return None

    def tick(self, now):
        """Call often. Returns 'focus_done' or 'break_done' when a phase ends."""
        if self.phase == IDLE or self.paused:
            return None
        if self.diff(self._end, now) > 0:
            return None
        if self.phase == FOCUS:
            self.cycles += 1
            long_break = self.cycles % self.long_every == 0
            self._begin(BREAK, self.long_break_min if long_break else self.break_min, now)
            return "focus_done"
        self._begin(FOCUS, self.focus_min, now)
        return "break_done"

    def snapshot(self, now):
        """Everything the screen shows, so a loop can redraw only on change."""
        return (self.phase, self.paused, self.remaining_ms(now) // 1000,
                self.cycles, self.focus_min)


# ---------------------------------------------------------------------------
def day_number(y, m, d):
    """Days since a fixed origin, by arithmetic (no datetime on the Pico).
    Only differences between two day numbers are meaningful."""
    y -= m <= 2
    era = y // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe


def date_text(day):
    """The inverse of day_number: a day number -> '2026-10-19'."""
    era = day // 146097
    doe = day - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + (3 if mp < 10 else -9)
    y = yoe + era * 400 + (1 if m <= 2 else 0)
    return "{:04d}-{:02d}-{:02d}".format(y, m, d)


def parse_date(text):
    """'2026-10-19' -> day number."""
    return day_number(int(text[0:4]), int(text[5:7]), int(text[8:10]))


def kind_of(title):
    if title.startswith("TEST:"):
        return "TEST"
    if title.startswith("DUE:"):
        return "DUE"
    return None


def short_title(title, width=20):
    text = title.split(":", 1)[1].strip() if ":" in title else title
    return text if len(text) <= width else text[:width - 1] + "~"


def upcoming(events, today, within=7):
    """TEST: and DUE: events from today to `within` days ahead, soonest first.
    today is a day number. Returns a list of (days_left, kind, title, id)."""
    out = []
    for e in events:
        kind = kind_of(e["title"])
        if kind is None:
            continue
        left = parse_date(e["date"]) - today
        if 0 <= left <= within:
            out.append((left, kind, e["title"], e.get("id", e["title"])))
    out.sort(key=lambda item: (item[0], item[1] != "TEST", item[2]))
    return out


def when_text(days_left):
    if days_left == 0:
        return "TODAY"
    if days_left == 1:
        return "TOMORROW"
    return "IN {} DAYS".format(days_left)


class Reminders:
    """Announce an item once, when it first comes within `alert_days` days."""

    def __init__(self, alert_days=1):
        self.alert_days = alert_days
        self.announced = set()

    def new_alerts(self, items):
        fresh = []
        for left, kind, title, ident in items:
            if left <= self.alert_days and ident not in self.announced:
                self.announced.add(ident)
                fresh.append((left, kind, title, ident))
        return fresh
