# Run this on your COMPUTER, not on the Pico.
#
#   python3 pipeline-synthetic-test.py            (about a minute)
#   python3 pipeline-synthetic-test.py --quick    (fewer clips)
#
# An end-to-end test of the REAL detector code (features.py, detector.py,
# levels.py, vad.py) on SYNTHETIC speech-like audio. It builds "Hey Pico"-like
# and other phrases from a simple vowel-formant synthesizer, turns them into
# microphone words, enrolls a template from five of the enrolled speaker's
# utterances exactly as 05-enroll.py does, and then scores many clips.
#
# THE AUDIO IS SYNTHETIC. It has clean vowels and a handful of consonant-like
# sounds, and it is nothing like the mess of real speech. The numbers show that
# the pipeline works and show the SHAPE of the trade-offs (false accepts against
# false rejects, pace, speaker), not how well the kit will do on a real voice.
# That is what 08-threshold-sweep.py is for. Seeds are fixed, so a run repeats.
#
# It needs numpy and scipy (pip install numpy scipy). The fast transform here is
# numpy's, plugged into features.Extractor(spectrum_fn=...): the same hook your
# Chapter 10 transform uses. A check at the start compares it with the
# plain-Python reference on one frame.

import math
import os
import sys

import numpy as np
from scipy.signal import lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

import calibration
import detector
import features
import levels
import synth
import vad
from array import array

RATE = levels.RATE
QUICK = "--quick" in sys.argv
N = 25 if QUICK else 80          # clips per test group


# --------------------------------------------------------------------------
# A tiny formant synthesizer
# --------------------------------------------------------------------------
VOWELS = {"a": (750, 1200), "i": (300, 2300), "u": (320, 900), "e": (500, 1800),
          "o": (500, 900), "ae": (650, 1700)}


def resonator(freq, bandwidth):
    """Coefficients of a 2-pole resonator centered on freq (Hz)."""
    r = math.exp(-math.pi * bandwidth / RATE)
    theta = 2 * math.pi * freq / RATE
    return [1.0 - r], [1.0, -2 * r * math.cos(theta), r * r]


def voiced(rng, seconds, f1a, f2a, f1b, f2b, f0, jitter=0.01):
    """A vowel that glides from (f1a, f2a) to (f1b, f2b) over `seconds`."""
    n = max(8, int(seconds * RATE))
    t = np.arange(n) / RATE
    phase = np.cumsum(2 * np.pi * f0 * (1 + jitter * rng.standard_normal(n)) / RATE)
    source = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.3 * np.sin(3 * phase) + 0.2 * np.sin(4 * phase)
    out = np.zeros(n)
    block = 128
    zi1 = np.zeros(2)
    zi2 = np.zeros(2)
    for s in range(0, n, block):
        frac = (s + block / 2) / n
        f1 = f1a + (f1b - f1a) * frac
        f2 = f2a + (f2b - f2a) * frac
        b1, a1 = resonator(f1, 90)
        b2, a2 = resonator(f2, 140)
        seg = source[s:s + block]
        y1, zi1 = lfilter(b1, a1, seg, zi=zi1)
        y2, zi2 = lfilter(b2, a2, seg, zi=zi2)
        out[s:s + block] = y1 + 0.7 * y2
    env = np.sin(np.pi * np.arange(n) / n) ** 0.5
    return out * env


def noisy(rng, seconds, center, bandwidth=600, level=1.0):
    """Fricative or burst: noise shaped around `center` Hz."""
    n = max(8, int(seconds * RATE))
    b, a = resonator(center, bandwidth)
    x = lfilter(b, a, rng.standard_normal(n))
    env = np.hanning(n)
    return x * env * level * 3.0


def silence(seconds):
    return np.zeros(max(1, int(seconds * RATE)))


def build_phrase(rng, segments, f0, tract, rate):
    """segments: list of ("v", vowel_a, vowel_b, seconds) / ("n", center_hz, seconds, level)
    / ("s", seconds). `tract` scales formants (vocal-tract length), `rate` stretches time."""
    parts = []
    for seg in segments:
        kind = seg[0]
        if kind == "v":
            (f1a, f2a), (f1b, f2b) = VOWELS[seg[1]], VOWELS[seg[2]]
            parts.append(voiced(rng, seg[3] * rate, f1a * tract, f2a * tract,
                                f1b * tract, f2b * tract, f0))
        elif kind == "n":
            parts.append(noisy(rng, seg[2] * rate, seg[1] * tract, level=seg[3]))
        else:
            parts.append(silence(seg[1] * rate))
    return np.concatenate(parts)


# "Hey Pico": h, ey, (p), i, (k), o
WAKE = [("n", 1800, 0.06, 0.5), ("v", "e", "i", 0.22), ("s", 0.04), ("n", 3000, 0.015, 1.0),
        ("v", "i", "i", 0.16), ("s", 0.03), ("n", 1800, 0.015, 1.0), ("v", "o", "u", 0.22)]


def random_phrase(rng, near_miss=False):
    if near_miss:        # keep "Hey" and change the rest, or reorder the syllables
        kind = rng.integers(0, 3)
        if kind == 0:    # "Hey Pablo": a-o ending
            return WAKE[:5] + [("s", 0.03), ("n", 1800, 0.015, 1.0), ("v", "a", "o", 0.25)]
        if kind == 1:    # "Pico Hey"
            return WAKE[4:] + [("s", 0.05)] + WAKE[:4]
        return WAKE[:4] + [("v", "u", "i", 0.2), ("s", 0.03), ("n", 3000, 0.015, 1.0), ("v", "a", "a", 0.25)]
    count = int(rng.integers(3, 7))
    segments = []
    for _ in range(count):
        c = rng.integers(0, 4)
        if c == 0:
            segments.append(("n", float(rng.choice([1500, 2500, 4000])), float(rng.uniform(0.05, 0.12)), 0.6))
        elif c == 1:
            segments.append(("s", float(rng.uniform(0.02, 0.06))))
        vs = list(VOWELS)
        segments.append(("v", vs[rng.integers(0, len(vs))], vs[rng.integers(0, len(vs))],
                         float(rng.uniform(0.12, 0.28))))
    return segments


# --------------------------------------------------------------------------
# Clips and the detector
# --------------------------------------------------------------------------
def make_clip(rng, speech, speech_bits, noise_bits=12.9, lead=1.0, tail=1.2, color=0.0):
    """Speech (a float array) between noise, scaled so its loud part has
    about speech_bits of average deviation. Returns a list of 32-bit frames (bytes)."""
    if speech is not None and len(speech):
        mad = np.mean(np.abs(speech[np.abs(speech) > 0.2 * np.max(np.abs(speech))]))
        speech = speech / mad * (2 ** speech_bits) * 0.8
    n_lead, n_tail = int(lead * RATE), int(tail * RATE)
    body = speech if speech is not None else np.zeros(0)
    x = np.concatenate([np.zeros(n_lead), body, np.zeros(n_tail)])
    if color:                                   # steady channel colouring: a first-order tilt
        x = lfilter([1.0, color], [1.0], x)
    x = x + rng.standard_normal(len(x)) * (2 ** noise_bits / 0.7979) + 15000
    x = np.clip(np.round(x), -(1 << 23), (1 << 23) - 1).astype(np.int64)
    frames = []
    for s in range(0, len(x) - levels.FRAME_SAMPLES + 1, levels.FRAME_SAMPLES):
        words = (x[s:s + levels.FRAME_SAMPLES] << 8).astype("<i4")
        frames.append(words.tobytes())
    return frames


def numpy_spectrum(re, im, power):
    """The fast transform plugged into Extractor: numpy's rfft."""
    x = np.frombuffer(re, dtype=np.float32).astype(np.float64)
    spectrum = np.fft.rfft(x)
    p = (spectrum.real ** 2 + spectrum.imag ** 2)[:features.HALF]
    power[:] = array("f", p.tolist())


EXTRACTOR = features.Extractor(spectrum_fn=numpy_spectrum)
REFERENCE = features.Extractor()
GATE_OPEN, GATE_CLOSE = 14.7, 14.2


def clip_features(frames):
    feats = array("f", [0.0] * (len(frames) * features.BANDS))
    bits = []
    for i, f in enumerate(frames):
        bits.append(levels.frame_stats(f)[0])
        EXTRACTOR.extract32(f, feats, i * features.BANDS)
    return feats, bits


def start_of_speech(bits):
    detector_vad = vad.VAD(levels.LevelGate(GATE_OPEN, GATE_CLOSE))
    for b in bits:
        if detector_vad.update(b) == "start":
            return detector_vad.start_index
    return None


def enroll(rng, speaker, count=5):
    windows = []
    for _ in range(count):
        wave = build_phrase(rng, WAKE, speaker["f0"], speaker["tract"], rng.normal(1.0, 0.04))
        frames = make_clip(rng, wave, rng.uniform(16.5, 18.0), noise_bits=rng.uniform(12.6, 13.2))
        feats, bits = clip_features(frames)
        start = start_of_speech(bits)
        first = max(0, start - detector.LEAD_FRAMES)
        windows.append(array("f", feats[first * features.BANDS:(first + detector.K) * features.BANDS]))
    return detector.build_template(windows)


def best_score(template, frames):
    feats, bits = clip_features(frames)
    det = detector.Detector(template, levels.LevelGate(GATE_OPEN, GATE_CLOSE), threshold=2.0)
    best = 0.0
    row = array("f", [0.0] * features.BANDS)
    for i in range(len(frames)):
        for j in range(features.BANDS):
            row[j] = feats[i * features.BANDS + j]
        score, _ = det.update(row, bits[i])
        if score is not None and score > best:
            best = score
    return best


def wake_clip(rng, speaker, rate=1.0):
    wave = build_phrase(rng, WAKE, speaker["f0"], speaker["tract"], rate)
    return make_clip(rng, wave, rng.uniform(16.0, 18.5), noise_bits=rng.uniform(12.5, 13.5),
                     color=rng.uniform(-0.5, 0.5))


def sweep(wake_scores, other_scores, label_a, label_b):
    print("  {:>9} {:>20} {:>20}".format("threshold", "false reject (" + label_a + ")", "false accept (" + label_b + ")"))
    for t in (0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90):
        fr = sum([1 for s in wake_scores if s < t]) / len(wake_scores)
        fa = sum([1 for s in other_scores if s >= t]) / len(other_scores)
        print("  {:>9.2f} {:>19.1f}% {:>19.1f}%".format(t, 100 * fr, 100 * fa))


def main():
    ok = True
    # A check that the fast hook matches the reference
    probe = make_clip(np.random.default_rng(1), build_phrase(np.random.default_rng(2), WAKE, 110, 1.0, 1.0), 17.0)[30]
    a = array("f", [0.0] * features.BANDS)
    b = array("f", [0.0] * features.BANDS)
    EXTRACTOR.extract32(probe, a)
    REFERENCE.extract32(probe, b)
    worst = max([abs(a[i] - b[i]) for i in range(features.BANDS)])
    print("Fast (numpy) transform against the plain-Python reference, one frame: "
          "largest feature difference {:.5f}".format(worst))
    ok = ok and worst < 0.01

    enrolled = {"f0": 110.0, "tract": 1.0}
    rng = np.random.default_rng(2026)
    template, consistency = enroll(rng, enrolled)
    print("Enrolled from 5 synthetic utterances; consistency {}".format(
        ", ".join(["{:.3f}".format(c) for c in consistency])))

    print()
    print("1. Same speaker, normal pace ({} 'Hey Pico' clips), best score per clip".format(N))
    same = [best_score(template, wake_clip(rng, enrolled, rng.normal(1.0, 0.05))) for _ in range(N)]
    print("  mean {:.3f}, lowest {:.3f}, highest {:.3f}".format(np.mean(same), min(same), max(same)))
    unscored = sum([1 for s in same if s == 0.0])
    print("  clips that were never scored (the level gate or the speech-present rule): {} of {}".format(unscored, len(same)))

    print()
    print("2. Other phrases, same speaker ({} random phrases, {} near-misses, {} noise-only clips)".format(N, N // 2, N // 2))
    others = []
    for _ in range(N):
        wave = build_phrase(rng, random_phrase(rng), enrolled["f0"], enrolled["tract"], rng.normal(1.0, 0.05))
        others.append(best_score(template, make_clip(rng, wave, rng.uniform(16.0, 18.5), noise_bits=rng.uniform(12.5, 13.5), color=rng.uniform(-0.5, 0.5))))
    near = []
    for _ in range(N // 2):
        wave = build_phrase(rng, random_phrase(rng, near_miss=True), enrolled["f0"], enrolled["tract"], rng.normal(1.0, 0.05))
        near.append(best_score(template, make_clip(rng, wave, rng.uniform(16.0, 18.5), noise_bits=rng.uniform(12.5, 13.5), color=rng.uniform(-0.5, 0.5))))
    quiet = [best_score(template, make_clip(rng, None, 0, noise_bits=rng.uniform(12.5, 13.5), lead=2.0, tail=1.0))
             for _ in range(N // 2)]
    print("  random phrases: mean {:.3f}, highest {:.3f}".format(np.mean(others), max(others)))
    print("  near-misses:    mean {:.3f}, highest {:.3f}".format(np.mean(near), max(near)))
    print("  noise only:     highest {:.3f} (the gate keeps most windows from being scored at all)".format(max(quiet)))

    print()
    print("3. Threshold sweep: enrolled-speaker 'Hey Pico' against all the other clips")
    sweep(same, others + near + quiet, "wake", "other")

    print()
    print("4. A different speaker says 'Hey Pico' ({} clips per voice)".format(N))
    voices = (("higher voice, f0 200 Hz, shorter tract", {"f0": 200.0, "tract": 1.15}),
              ("lower voice, f0 90 Hz, longer tract", {"f0": 90.0, "tract": 0.9}))
    for label, speaker in voices:
        scores = [best_score(template, wake_clip(rng, speaker, rng.normal(1.0, 0.05))) for _ in range(N)]
        miss = sum([1 for s in scores if s < 0.70]) / len(scores)
        print("  {:<40} mean {:.3f}; rejected at 0.70: {:.0f}%".format(label, np.mean(scores), 100 * miss))

    print()
    print("5. Speaking pace (enrolled speaker, {} clips per pace)".format(N // 2))
    print("  {:>16} {:>10} {:>14}".format("pace (time x)", "mean best", "rejected at 0.70"))
    for rate in (0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3):
        scores = [best_score(template, wake_clip(rng, enrolled, rate * rng.normal(1.0, 0.02))) for _ in range(N // 2)]
        miss = sum([1 for s in scores if s < 0.70]) / len(scores)
        label = "{:.1f} ({})".format(rate, "faster" if rate < 1 else "slower" if rate > 1 else "enrolled")
        print("  {:>16} {:>10.3f} {:>13.0f}%".format(label, np.mean(scores), 100 * miss))

    print()
    print("DONE" if ok else "CHECK: the fast transform differs from the reference")


if __name__ == "__main__":
    main()
