# Chapter 12, Test 03: How long does one frame of features take?
# Times each step of feature extraction on one synthetic frame, repeated 5
# times, and then the window update and score. Compares the total with the
# 40 ms frame budget from Chapter 8. Needs only the Pico (no microphone).
#
# The FFT here is the PLAIN-PYTHON reference, so expect the transform to be
# far over budget. The point is to measure it, and to measure again after you
# plug in the fast transform from Chapter 10 (Extractor(spectrum_fn=...)).
#
# PASS: the table prints. "fits in 40 ms" is the goal; if it says it does not,
# the live detector (09) will lose audio, and you now know by how much.
# WRITE DOWN: the transform ms and the total ms, with and without Chapter 10's
# fast transform.

NAME = "03-feature-timing.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from array import array

import detector
import features
import levels
import synth

REPEATS = 5
BUDGET_US = levels.FRAME_MS * 1000

extractor = features.Extractor()                 # add spectrum_fn=your_fast_function here
frame = synth.speech_frame(synth.Rng(3), 17.0)   # one synthetic 40 ms frame (bytes)
feats = array("f", [0.0] * features.BANDS)
window = detector.Window()
template = array("f", [0.01] * (detector.K * detector.B))
for _ in range(detector.K):                      # fill the window so score() has work to do
    window.push(feats, True)

steps = {"load (unpack, DC, Hann)": 0, "transform (FFT)": 0, "power": 0,
         "bands and log": 0, "window push": 0, "window score": 0}
for _ in range(REPEATS):
    t0 = time.ticks_us()
    extractor.load32(frame)
    t1 = time.ticks_us()
    if extractor.spectrum_fn is not None:
        extractor.spectrum_fn(extractor.re, extractor.im, extractor.power)
        t2 = t3 = time.ticks_us()
    else:
        extractor.transform()
        t2 = time.ticks_us()
        extractor.to_power()
        t3 = time.ticks_us()
    extractor.bands_log(feats)
    t4 = time.ticks_us()
    window.push(feats, True)
    t5 = time.ticks_us()
    window.score(template)
    t6 = time.ticks_us()
    for name, a, b in (("load (unpack, DC, Hann)", t0, t1), ("transform (FFT)", t1, t2),
                       ("power", t2, t3), ("bands and log", t3, t4),
                       ("window push", t4, t5), ("window score", t5, t6)):
        steps[name] += time.ticks_diff(b, a)

print()
print("{:<26} {:>10}".format("step (average of {})".format(REPEATS), "ms"))
total = 0
for name in ("load (unpack, DC, Hann)", "transform (FFT)", "power", "bands and log",
             "window push", "window score"):
    ms = steps[name] / REPEATS / 1000
    total += steps[name] / REPEATS
    print("{:<26} {:>10.2f}".format(name, ms))
print("{:<26} {:>10.2f}".format("total", total / 1000))
print("{:<26} {:>10.2f}".format("frame budget", BUDGET_US / 1000))
print()
if total <= BUDGET_US:
    print("PASS: one frame of features and a score fits in the {} ms budget "
          "({:.0f}% used).".format(levels.FRAME_MS, 100 * total / BUDGET_US))
    print("Add the ~10 ms the loudness calculation took in Chapter 8, and the display, "
          "before you call it safe.")
else:
    print("OVER BUDGET: {:.1f} frames of audio pass for every frame this computes. "
          "The live loop would lose audio.".format(total / BUDGET_US))
    print("Use 07-score-trace.py (record first, score afterwards) until the "
          "transform is fast enough.")
