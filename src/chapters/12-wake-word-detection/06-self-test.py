# Chapter 12, Test 06: Detector self-test
# Checks the enrolled template and the cost of running it:
#   1. the template scores 1.0000 against itself
#   2. it still scores well when the window is off by 1, 2, 3 frames (how
#      forgiving the alignment is) and badly when it is turned upside down
#   3. random windows score near 0 (about 0.05 either way)
#   4. a second of your room's own noise scores low (needs the microphone)
#   5. the time for one frame of features plus the window update and score,
#      against the 40 ms frame budget (a frame overrun check)
# If wake_template.bin does not exist it uses a SYNTHETIC template and says so.
# Needs the Pico; the microphone is used if it is present.
#
# PASS: "self score 1.0000", the shifted scores fall off smoothly, the noise
# scores stay low, and the budget line tells you honestly whether the live
# detector can keep up. WRITE DOWN: the shifted scores (they measure how
# sensitive YOUR template is), the noise numbers, and the total ms per frame.

NAME = "06-self-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time
from array import array

import calibration
import config
import detector
import features
import levels
import synth

K, B = detector.K, detector.B
ok = True


def check(label, good):
    global ok
    ok = ok and good
    print("  {:<62} {}".format(label, "ok" if good else "FAIL"))


template = detector.load_template()
source = "your enrolled template"
if template is None:
    source = "a SYNTHETIC template (run 05-enroll.py to use your own)"
    template = array("f", [0.0] * (K * B))
    for i in range(K):
        for j in range(B):
            template[i * B + j] = (math.exp(-((i - 8) / 3.0) ** 2 - ((j - 5) / 2.5) ** 2)
                                   + math.exp(-((i - 16) / 3.0) ** 2 - ((j - 10) / 3.0) ** 2))
    detector.mean_subtract(template)
    detector.normalize(template)
print("Using", source)
cal = calibration.load()


def window_of(rows):
    """Push K rows (each a list of B numbers) into a fresh Window; return it."""
    w = detector.Window()
    for r in rows:
        w.push(r, True)
    return w


def rows_of(flat, shift=0):
    """The template's rows, moved `shift` frames later (earlier if negative),
    repeating the edge row so nothing is zero."""
    rows = []
    for i in range(K):
        s = min(K - 1, max(0, i - shift))
        rows.append(array("f", flat[s * B:(s + 1) * B]))
    return rows


# 1 and 2 ---------------------------------------------------------------
print()
print("1. Self score and alignment")
own = window_of(rows_of(template)).score(template)
print("  self score {:.4f}".format(own))
check("the template scores 1.0 against itself (within 0.0005)", abs(own - 1.0) < 0.0005)
print("  {:>14} {:>8}".format("shift (frames)", "score"))
shifted = {}
for shift in (-3, -2, -1, 0, 1, 2, 3):
    shifted[shift] = window_of(rows_of(template, shift)).score(template)
    print("  {:>14} {:>8.3f}".format(shift, shifted[shift]))
check("a shift of 1 frame scores lower than 0 shift", shifted[1] < shifted[0] and shifted[-1] < shifted[0])
upside = array("f", [-v for v in template])
check("the upside-down template scores below -0.9", window_of(rows_of(upside)).score(template) < -0.9)

# 3 ---------------------------------------------------------------------
print()
print("2. Random windows")
rng = synth.Rng(8)
scores = []
for _ in range(30):
    rows = [array("f", [rng.gauss() for _ in range(B)]) for _ in range(K)]
    scores.append(window_of(rows).score(template))
mean = sum(scores) / len(scores)
std = math.sqrt(sum([(s - mean) ** 2 for s in scores]) / len(scores))
print("  30 random windows: mean {:+.3f}, std {:.3f}, highest {:.3f}".format(mean, std, max(scores)))
check("the mean is near 0 (within 0.05)", abs(mean) < 0.05)
check("the highest random score is under 0.35", max(scores) < 0.35)

# 4 ---------------------------------------------------------------------
print()
print("3. A second of this room's own noise")
extractor = features.Extractor()
try:
    mic = config.init_microphone()
except Exception as error:                      # no microphone wired
    mic = None
    print("  (no microphone: skipped: {})".format(error))
if mic is not None:
    frame = bytearray(levels.FRAME_BYTES)
    gate = calibration.gate_from(cal)
    det = detector.Detector(template, gate, threshold=2.0)
    feats = array("f", [0.0] * B)
    try:
        for _ in range(8):                          # microphone start-up
            mic.readinto(frame)
        print("  Stay quiet for about {} frames...".format(K + 5))
        for _ in range(K + 5):
            mic.readinto(frame)
            bits = levels.frame_stats(frame)[0]
            extractor.extract32(frame, feats)
            det.update(feats, bits)
        raw_score = det.window.score(template)
        print("  window of room noise: score {:.3f}, frames with the gate open {} of {}".format(
            raw_score, det.window.active_count, K))
        check("room noise scores under the threshold {}".format(detector.THRESHOLD),
              raw_score < detector.THRESHOLD)
        check("the level gate kept the window 'not scored' (fewer than {} loud frames)".format(
            detector.MIN_ACTIVE_FRAMES), det.last_score is None)
    finally:
        mic.deinit()

# 5 ---------------------------------------------------------------------
print()
print("4. Time per frame against the {} ms budget".format(levels.FRAME_MS))
frame = synth.speech_frame(synth.Rng(2), 17.0)
feats = array("f", [0.0] * B)
window = window_of(rows_of(template))
t0 = time.ticks_us()
extractor.extract32(frame, feats)
t1 = time.ticks_us()
window.push(feats, True)
score = window.score(template)
t2 = time.ticks_us()
extract_ms = time.ticks_diff(t1, t0) / 1000
window_ms = time.ticks_diff(t2, t1) / 1000
print("  features {:.2f} ms + window update and score {:.2f} ms = {:.2f} ms".format(
    extract_ms, window_ms, extract_ms + window_ms))
if extract_ms + window_ms <= levels.FRAME_MS:
    print("  fits in the budget, with {:.1f} ms to spare for loudness, display and the rest".format(
        levels.FRAME_MS - extract_ms - window_ms))
else:
    print("  OVER BUDGET by {:.1f} ms: the live detector would lose audio. "
          "Use Chapter 10's fast transform.".format(extract_ms + window_ms - levels.FRAME_MS))
check("the window update and score alone fit in 40 ms", window_ms <= levels.FRAME_MS)

print()
print("PASS" if ok else "CHECK: one of the rows above failed")
