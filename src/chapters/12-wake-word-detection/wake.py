# wake.py -- helpers shared by the Chapter 12 tests that work on a recording
#
# Everything here is "record first, then score": it takes the 16-bit recording
# that recorder.record() made and runs the feature extractor over it AFTER the
# button is released. That is slower than real time with the plain-Python FFT,
# which is fine for enrollment and for studying score traces; the live loop in
# 09-live-detector.py is the one that must keep up with the microphone.

import time
from array import array

import calibration
import detector
import features
import levels

B = features.BANDS
K = detector.K


def load_setup():
    """Returns (calibration, template or None)."""
    cal = calibration.load()
    if not cal["calibrated"]:
        print("No calibration.json: using the DEFAULT guesses. Run Chapter 11's 04-calibrate.py.")
    template = detector.load_template()
    if template is None:
        print("No wake_template.bin: run 05-enroll.py first.")
    return cal, template


def features_for(extractor, rec, first, count):
    """Features of `count` frames of the recording, starting at frame `first`.
    Returns an array of count * B numbers, frame by frame."""
    out = array("f", [0.0] * (count * B))
    for i in range(count):
        extractor.extract16(rec, out, i * B, (first + i) * levels.FRAME16_BYTES)
    return out


def score_recording(extractor, rec, frames, bits, template, cal, progress=None):
    """Slide the detector over a recording, one frame at a time.

    bits is the per-frame loudness the recorder kept. Returns a list with, for
    every frame, the score (a float) or None when the frame could not be scored
    (window not full yet, or not enough speech in it). The detector's threshold
    is set impossibly high so that only the scores are collected."""
    det = detector.Detector(template, calibration.gate_from(cal), threshold=2.0)
    feats = array("f", [0.0] * B)
    scores = []
    for n in range(frames):
        extractor.extract16(rec, feats, 0, n * levels.FRAME16_BYTES)
        score, _ = det.update(feats, bits[n])
        scores.append(score)
        if progress is not None:
            progress(n, frames)
    return scores


def enrollment_window(extractor, rec, frames, start_index):
    """The K-frame window for one enrolled utterance, or None if the recording
    is too short. It starts LEAD_FRAMES before the first loud frame, so the same
    stretch of 'Hey Pico' lands in the same rows of the template every time."""
    first = max(0, start_index - detector.LEAD_FRAMES)
    if first + K > frames:
        return None
    return features_for(extractor, rec, first, K)


def best_score(scores):
    """(highest score, frame it happened at); (0.0, -1) if nothing was scored."""
    best, where = 0.0, -1
    for n in range(len(scores)):
        if scores[n] is not None and (where < 0 or scores[n] > best):
            best, where = scores[n], n
    return best, where
