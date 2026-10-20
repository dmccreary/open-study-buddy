# Chapter 12, Test 01: The detector math test
# Checks the wake-word math on SYNTHETIC feature windows (seeded, no hardware):
# mean subtraction, unit normalization, the dot-product score, the running-sums
# shortcut against the textbook steps, the window fill percentage, cooldown,
# the template file, and the false-accept / false-reject trade-off on made-up
# score distributions. It runs on your computer (python3 01-detector-math-test.py);
# it also runs on the Pico, but the random numbers take a while there.
#
# PASS: the last line says PASS. Every number is synthetic: it shows how the math
# behaves, not how well "Hey Pico" will be detected on the kit.

NAME = "01-detector-math-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import os
from array import array

import detector
import features
import levels
import synth

K, B = detector.K, detector.B
N_NOISE = 200
ok = True


def check(label, good):
    global ok
    ok = ok and good
    print("  {:<64} {}".format(label, "ok" if good else "FAIL"))


def blob(i, j, ci, cj, wi, wj, height):
    return height * math.exp(-((i - ci) / wi) ** 2 - ((j - cj) / wj) ** 2)


def pattern(stretch=1.0, shift=0.0):
    """A smooth K x B feature pattern with three blobs, standing in for a
    spoken phrase. stretch > 1 slows it down, shift moves it later (in frames)."""
    x = array("f", [0.0] * (K * B))
    for i in range(K):
        t = (i - shift) / stretch
        for j in range(B):
            x[i * B + j] = (blob(t, j, 7, 4, 2.5, 2.0, 3.0)
                            + blob(t, j, 12, 9, 2.5, 2.5, 2.5)
                            + blob(t, j, 17, 6, 2.5, 3.0, 2.0)
                            + 8.0 - 0.2 * j)        # a steady colouring: lower bands louder
    return x


def noise_window(rng):
    return array("f", [rng.gauss() for _ in range(K * B)])


def mean_std(values):
    m = sum(values) / len(values)
    return m, math.sqrt(sum([(v - m) ** 2 for v in values]) / len(values))


template_raw = pattern()
template = array("f", template_raw)
detector.mean_subtract(template)
detector.normalize(template)

# ---------------------------------------------------------------------------
print()
print("1. Mean subtraction, unit normalization, self score")
copy = array("f", template_raw)
detector.mean_subtract(copy)
worst_mean = max([abs(sum([copy[i * B + j] for i in range(K)]) / K) for j in range(B)])
print("  largest band mean after subtraction: {:.2e}".format(worst_mean))
check("every band's mean is 0 after mean subtraction (< 1e-5)", worst_mean < 1e-5)
size = detector.normalize(copy)
print("  length before normalizing {:.3f}, after {:.6f}".format(size, detector.length(copy)))
check("the length after normalizing is 1 (within 1e-5)", abs(detector.length(copy) - 1) < 1e-5)
self_score = detector.score_direct(template_raw, template)
print("  score of the template's own window: {:.6f}".format(self_score))
check("a window scores 1.0 against its own template", abs(self_score - 1.0) < 1e-5)

# ---------------------------------------------------------------------------
print()
print("2. What the score ignores, and what it does not")
louder = array("f", [v + 3.0 for v in template_raw])
colored = array("f", template_raw)
for i in range(K):
    for j in range(B):
        colored[i * B + j] += 0.4 * j - 2.0         # a different steady band-by-band colouring
s_louder = detector.score_direct(louder, template)
s_colored = detector.score_direct(colored, template)
print("  every feature +3.0 (the whole sound much louder): {:.6f}".format(s_louder))
print("  a steady per-band offset (different room/microphone colouring): {:.6f}".format(s_colored))
check("adding one number to every feature leaves the score at 1.0", abs(s_louder - 1) < 1e-5)
check("a steady per-band offset leaves the score at 1.0", abs(s_colored - 1) < 1e-5)
scaled = array("f", [(v - 8.0) * 0.5 + 8.0 for v in template_raw])
print("  the pattern's changes halved in size (flatter speech): {:.6f}".format(
    detector.score_direct(scaled, template)))
check("shrinking the pattern's depth also leaves the score at 1.0 (length is normalized)",
      abs(detector.score_direct(scaled, template) - 1) < 1e-5)
inverted = array("f", [-(v - 8.0) + 8.0 for v in template_raw])
s_inv = detector.score_direct(inverted, template)
print("  the pattern turned upside down: {:.6f}".format(s_inv))
check("the upside-down pattern scores near -1", s_inv < -0.95)

# ---------------------------------------------------------------------------
print()
print("3. Random windows (no speech) against the template: {} windows".format(N_NOISE))
rng = synth.Rng(5)
noise_scores = [detector.score_direct(noise_window(rng), template) for _ in range(N_NOISE)]
mean, std = mean_std(noise_scores)
dof = (K - 1) * B
print("  mean {:+.4f}, standard deviation {:.4f}, largest {:.4f}".format(mean, std, max(noise_scores)))
print("  theory for random windows: std about 1/sqrt({}) = {:.4f}".format(dof, 1 / math.sqrt(dof)))
check("the mean is within 0.02 of 0", abs(mean) < 0.02)
check("the spread is within 25% of 1/sqrt(384)", abs(std - 1 / math.sqrt(dof)) < 0.25 / math.sqrt(dof))

# ---------------------------------------------------------------------------
print()
print("4. The same pattern shifted in time and stretched (synthetic pattern only)")
print("  {:<26} {:>7}".format("change", "score"))
for label, window in (("shifted 1 frame later", pattern(shift=1)),
                      ("shifted 2 frames later", pattern(shift=2)),
                      ("shifted 3 frames later", pattern(shift=3)),
                      ("shifted 5 frames later", pattern(shift=5)),
                      ("10% slower", pattern(stretch=1.1)),
                      ("20% slower", pattern(stretch=1.2)),
                      ("10% faster", pattern(stretch=0.9)),
                      ("20% faster", pattern(stretch=0.8))):
    print("  {:<26} {:>7.3f}".format(label, detector.score_direct(window, template)))
s1 = detector.score_direct(pattern(shift=1), template)
s20 = detector.score_direct(pattern(stretch=1.2), template)
check("1 frame of shift costs less than 20% of a slower pace", s1 > s20)
check("a 20% change in pace scores lower than 1.0", s20 < 0.9)
print("  (These come from a smooth made-up pattern. Real speech changes faster and slower")
print("   than this, so the shape is the lesson, not the numbers.)")

# ---------------------------------------------------------------------------
print()
print("5. The running-sums score against the textbook steps")
window = detector.Window()
rng = synth.Rng(9)
worst = 0.0
frames = 700                                           # passes the 250-frame resync twice
for n in range(frames):
    feats = array("f", [8.0 + 2.0 * rng.gauss() + 0.3 * j for j in range(B)])
    window.push(feats, n % 3 == 0)
    if window.is_full() and n % 7 == 0:
        fast = window.score(template)
        slow = detector.score_direct(window.flat(), template)
        worst = max(worst, abs(fast - slow))
print("  largest difference over {} frames: {:.2e}".format(frames, worst))
check("running sums match the textbook steps (< 1e-4)", worst < 1e-4)

# ---------------------------------------------------------------------------
print()
print("6. Window fill percentage")
window = detector.Window()
fills = []
for n in range(K + 1):
    fills.append((n, window.fill_percent(), window.score(template) is None))
    window.push(array("f", [1.0] * B), True)
print("  frames in the window -> fill: " + ", ".join(
    ["{}={}%".format(n, f) for n, f, _ in fills if n in (0, 1, 5, 10, 20, 24, 25)]))
check("0 frames is 0%", fills[0][1] == 0)
check("12 frames is 48%", fills[12][1] == 48)
check("24 frames is 96% and still not scored", fills[24][1] == 96 and fills[24][2])
check("25 frames is 100% and can be scored", fills[25][1] == 100 and not fills[25][2])
window.reset()
check("reset() empties the window (0%)", window.fill_percent() == 0)

# ---------------------------------------------------------------------------
print()
print("7. Threshold, cooldown, and speech present")
scores_stream = [0.1, 0.2, 0.3, 0.65, 0.78, 0.91, 0.88, 0.74, 0.40, 0.2, 0.1, 0.8, 0.2]
fires_no_cooldown = sum([1 for s in scores_stream if s >= 0.70])
cooling = 0
fires = 0
for s in scores_stream:
    if cooling > 0:
        cooling -= 1
    elif s >= 0.70:
        fires += 1
        cooling = 4
print("  score stream: {}".format(scores_stream))
print("  fires without cooldown {}, with a 4-frame cooldown {}".format(fires_no_cooldown, fires))
check("without a cooldown the one phrase fires 5 times (4 in a row, then 1)", fires_no_cooldown == 5)
check("a cooldown turns the 4-in-a-row into one detection", fires == 2)
det = detector.Detector(template, levels.LevelGate(15.0, 14.5), threshold=0.70)
fired = []
for n in range(K + 5):                                  # silence: gate never opens
    score, f = det.update(array("f", template_raw[(n % K) * B:(n % K) * B + B]), 13.0)
    fired.append(f)
check("a full window with no speech frames is never scored or fired",
      det.last_score is None and not any(fired))
det.reset()
for n in range(K):                                      # replay the template with the gate open
    score, f = det.update(array("f", template_raw[n * B:(n + 1) * B]), 17.0)
print("  template replayed with the gate open: score {:.4f}, fired {}".format(score, f))
check("the replayed template scores 1.0 and fires on the 25th frame", abs(score - 1) < 1e-4 and f)
exact = detector.Detector(template, levels.LevelGate(15.0, 14.5), threshold=score)
for n in range(K):
    last_score, last_fired = exact.update(array("f", template_raw[n * B:(n + 1) * B]), 17.0)
check("a score exactly equal to the threshold fires (>=)", last_fired)

# ---------------------------------------------------------------------------
print()
print("8. Template file")
path = "wake_template_selftest.bin"
detector.save_template(template, path)
back = detector.load_template(path)
size_bytes = os.stat(path)[6]
os.remove(path)
print("  file size {} bytes = 8 header + {} x {} x 4".format(size_bytes, K, B))
check("what is loaded equals what was saved", back is not None and list(back) == list(template))
check("the file is 1,608 bytes", size_bytes == 8 + K * B * 4 == 1608)
check("a missing file gives None", detector.load_template("no-such-file.bin") is None)

# ---------------------------------------------------------------------------
print()
print("9. False accepts and false rejects on SYNTHETIC score distributions")
rng = synth.Rng(77)
wake = [min(1.0, 0.80 + 0.08 * rng.gauss()) for _ in range(1000)]
other = [min(1.0, 0.35 + 0.15 * rng.gauss()) for _ in range(1000)]
print("  1,000 'Hey Pico' scores ~ mean 0.80, sd 0.08; 1,000 other-sound scores ~ mean 0.35, sd 0.15")
print("  {:>9} {:>14} {:>14}".format("threshold", "false reject", "false accept"))
rows = []
for t in (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90):
    fr = sum([1 for s in wake if s < t]) / len(wake)
    fa = sum([1 for s in other if s >= t]) / len(other)
    rows.append((t, fr, fa))
    print("  {:>9.2f} {:>13.1f}% {:>13.1f}%".format(t, 100 * fr, 100 * fa))
check("raising the threshold never lowers false rejects", all([rows[i][1] <= rows[i + 1][1] for i in range(len(rows) - 1)]))
check("raising the threshold never raises false accepts", all([rows[i][2] >= rows[i + 1][2] for i in range(len(rows) - 1)]))

# ---------------------------------------------------------------------------
print()
print("10. The DCT bridge to MFCCs")
base = [3.0, 4.0, 5.5, 5.0, 4.0, 3.5, 3.0, 2.0, 1.5, 1.0, 0.5, 0.2, 0.0, -0.5, -1.0, -1.5]
louder_bands = [v + 2.0 for v in base]
d0 = features.dct(base, 12)
d1 = features.dct(louder_bands, 12)
changed = [k for k in range(12) if abs(d1[k] - d0[k]) > 1e-9]
print("  adding 2.0 to all 16 band values changes DCT coefficients: {}".format(changed))
check("only coefficient 0 changes", changed == [0])
check("coefficient 0 changes by 2.0 x 16 = 32", abs(d1[0] - d0[0] - 32.0) < 1e-9)

# ---------------------------------------------------------------------------
print()
print("11. Band table")
e = features.EDGES
print("  band edges (bins):", e)
check("17 edges, strictly increasing", len(e) == 17 and all([e[i] < e[i + 1] for i in range(16)]))
check("the bands cover bins 4 to 255 (100 Hz to 6,400 Hz)", e[0] == 4 and e[-1] == 256)

print()
print("PASS" if ok else "FAIL")
