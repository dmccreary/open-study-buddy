# detector.py -- the wake-word detector's math and bookkeeping (Chapter 12)
#
# Pure Python, no hardware: it runs on the Pico and on your computer.
#
# The idea, in four steps (K frames x B bands of features make a "window"):
#   1. mean subtraction    for each band, subtract that band's average over the
#                          window (removes steady room and microphone colouring)
#   2. unit normalization  scale the whole window to length 1 (removes loudness)
#   3. dot product         multiply with the enrolled template, which is also
#                          mean-subtracted and length 1: the score is the cosine
#                          of the angle between them, from -1 to 1
#   4. decide              fire when the score reaches the threshold, the window
#                          is full, enough frames had speech, and no cooldown
#
# Two ways to compute the same score are here on purpose:
#   score_direct()   the textbook steps, easy to read, allocates a copy
#   Window.score()   the running-sums version used in the live loop: it never
#                    builds the mean-subtracted copy and does no allocation
# 01-detector-math-test.py checks that they agree.

import math
import struct
from array import array

import features

K = 25                      # frames in the window: 25 x 40 ms = 1 second
B = features.BANDS          # 16 bands
THRESHOLD = 0.70            # a STARTING value, not a measured one: tune with 08
COOLDOWN_FRAMES = 50        # 2 seconds of ignoring after a detection
MIN_ACTIVE_FRAMES = 8       # a window needs 8 frames (320 ms) with the gate open
RESYNC_FRAMES = 250         # recompute the running sums exactly every 10 seconds
LEAD_FRAMES = 3             # enrollment starts the window 3 frames before the speech

MAGIC = b"HPT1"
TEMPLATE_PATH = "wake_template.bin"


# ---------------------------------------------------------------------------
# The three steps, written out
# ---------------------------------------------------------------------------
def mean_subtract(x, k=K, b=B):
    """In place: subtract each band's mean over the k frames. x is k*b numbers,
    frame by frame (x[i*b + j] is band j of frame i)."""
    for j in range(b):
        total = 0.0
        for i in range(k):
            total += x[i * b + j]
        mean = total / k
        for i in range(k):
            x[i * b + j] -= mean


def length(x):
    total = 0.0
    for v in x:
        total += v * v
    return math.sqrt(total)


def normalize(x):
    """In place: scale x to length 1. Returns the length it had (0 means silence)."""
    size = length(x)
    if size > 1e-9:
        for i in range(len(x)):
            x[i] /= size
    return size


def dot(a, c):
    total = 0.0
    for i in range(len(a)):
        total += a[i] * c[i]
    return total


def score_direct(x, template):
    """Cosine score of one window against a template, by the textbook steps."""
    copy = array("f", x)
    mean_subtract(copy)
    if normalize(copy) <= 1e-9:
        return 0.0
    return dot(copy, template)


def build_template(windows):
    """Average several enrolled windows into one template.

    Each window (K*B raw features) is mean-subtracted and made length 1; the
    results are averaged and the average is made length 1 again. Returns
    (template, consistency): consistency[i] is window i's score against the
    finished template, a check that the utterances agree."""
    total = array("f", [0.0] * (K * B))
    for w in windows:
        c = array("f", w)
        mean_subtract(c)
        normalize(c)
        for i in range(K * B):
            total[i] += c[i]
    normalize(total)
    return total, [score_direct(w, total) for w in windows]


# ---------------------------------------------------------------------------
# The rolling window
# ---------------------------------------------------------------------------
class Window:
    """The last K frames of features, oldest first, with running sums so the
    score costs one pass over K*B numbers and no new memory."""

    def __init__(self, k=K, b=B):
        self.k, self.b = k, b
        self.rows = array("f", [0.0] * (k * b))     # a ring of k frames
        self.active = array("B", [0] * k)           # 1 where the level gate was open
        self.sum = array("f", [0.0] * b)
        self.sumsq = array("f", [0.0] * b)
        self.head = 0                               # slot for the NEXT frame (the oldest when full)
        self.count = 0
        self.active_count = 0
        self.age = 0

    def reset(self):
        """Empty the window: fill percentage goes back to 0."""
        for i in range(len(self.rows)):
            self.rows[i] = 0.0
        for j in range(self.b):
            self.sum[j] = 0.0
            self.sumsq[j] = 0.0
        for i in range(self.k):
            self.active[i] = 0
        self.head = self.count = self.active_count = self.age = 0

    def fill_percent(self):
        return 100 * self.count // self.k

    def is_full(self):
        return self.count == self.k

    def push(self, feats, gate_open):
        """Add one frame (16 features) and drop the oldest if the window is full."""
        b, rows = self.b, self.rows
        base = self.head * b
        if self.count == self.k:                    # forget the oldest frame
            for j in range(b):
                v = rows[base + j]
                self.sum[j] -= v
                self.sumsq[j] -= v * v
            self.active_count -= self.active[self.head]
        else:
            self.count += 1
        for j in range(b):
            v = feats[j]
            rows[base + j] = v
            self.sum[j] += v
            self.sumsq[j] += v * v
        self.active[self.head] = 1 if gate_open else 0
        self.active_count += self.active[self.head]
        self.head = (self.head + 1) % self.k
        self.age += 1
        if self.age % RESYNC_FRAMES == 0:
            self._resync()

    def _resync(self):
        """Recompute the sums from the stored rows: stops rounding errors building up."""
        b = self.b
        for j in range(b):
            self.sum[j] = 0.0
            self.sumsq[j] = 0.0
        for i in range(self.count):
            for j in range(b):
                v = self.rows[i * b + j]
                self.sum[j] += v
                self.sumsq[j] += v * v

    def flat(self):
        """The window in time order (oldest first) as a new array: k*b numbers."""
        out = array("f", [0.0] * (self.k * self.b))
        start = self.head if self.count == self.k else 0
        for i in range(self.count):
            slot = (start + i) % self.k
            for j in range(self.b):
                out[i * self.b + j] = self.rows[slot * self.b + j]
        return out

    def score(self, template):
        """Cosine score against the template, or None if the window is not full.

        The template has zero mean in every band, so the dot product of the
        template with the mean-subtracted window equals its dot product with
        the raw window. The window's length after mean subtraction comes from
        the running sums:  sum over bands of ( sumsq - sum*sum / k )."""
        if self.count < self.k:
            return None
        k, b, rows = self.k, self.b, self.rows
        start = self.head                            # oldest frame
        total = 0.0
        for i in range(k):
            r = ((start + i) % k) * b
            t = i * b
            for j in range(b):
                total += template[t + j] * rows[r + j]
        energy = 0.0
        for j in range(b):
            energy += self.sumsq[j] - self.sum[j] * self.sum[j] / k
        if energy <= 1e-9:
            return 0.0
        return total / math.sqrt(energy)


# ---------------------------------------------------------------------------
# The detector
# ---------------------------------------------------------------------------
class Detector:
    def __init__(self, template, gate, threshold=THRESHOLD,
                 cooldown_frames=COOLDOWN_FRAMES, min_active=MIN_ACTIVE_FRAMES):
        self.template = template
        self.gate = gate                            # a levels.LevelGate
        self.threshold = threshold
        self.cooldown_frames = cooldown_frames
        self.min_active = min_active
        self.window = Window()
        self.cooldown = 0
        self.last_score = None

    def reset(self):
        """Forget the window (e.g. after the microphone was closed for a beep)."""
        self.window.reset()
        self.gate.is_open = False

    def start_cooldown(self):
        self.cooldown = self.cooldown_frames

    def update(self, feats, bits):
        """Process one frame: its 16 features and its loudness in bits.

        Returns (score, fired). score is None when the frame cannot be scored:
        the window is not full yet, or fewer than min_active frames of the window
        had the gate open (no speech in it)."""
        loud = self.gate.update(bits)
        self.window.push(feats, loud)
        score = None
        if self.window.is_full() and self.window.active_count >= self.min_active:
            score = self.window.score(self.template)
        self.last_score = score
        fired = False
        if self.cooldown > 0:
            self.cooldown -= 1
        elif score is not None and score >= self.threshold:
            fired = True
            self.start_cooldown()
        return score, fired


# ---------------------------------------------------------------------------
# Saving and loading the template
# ---------------------------------------------------------------------------
def save_template(template, path=TEMPLATE_PATH):
    """Write the template to flash: only when the person presses UP."""
    import os
    header = struct.pack("<4sBBH", MAGIC, K, B, features.EDGES_CHECK)
    temporary = path + ".tmp"
    with open(temporary, "wb") as f:
        f.write(header)
        f.write(template)                           # an array writes its raw bytes
    try:
        os.remove(path)
    except OSError:
        pass
    os.rename(temporary, path)


def load_template(path=TEMPLATE_PATH):
    """Returns the template array, or None if there is no usable file."""
    try:
        with open(path, "rb") as f:
            header = f.read(8)
            magic, k, b, check = struct.unpack("<4sBBH", header)
            if magic != MAGIC or k != K or b != B or check != features.EDGES_CHECK:
                return None
            template = array("f", [0.0] * (K * B))
            f.readinto(template)
            return template
    except (OSError, ValueError):
        return None
