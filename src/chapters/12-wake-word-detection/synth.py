# synth.py -- synthetic microphone frames for the Chapter 11 checks
#
# Pure Python. It makes frames of 32-bit microphone words from a random-number
# generator with a fixed seed, so every run on every machine gives the same
# frames. These frames are SYNTHETIC: they let the loudness, calibration, gate
# and VAD code be tested without a microphone. They are not recordings of any
# room or voice.

import math
import struct

import levels


class Rng:
    """A tiny linear congruential generator: same numbers on a computer and on the Pico."""

    def __init__(self, seed):
        self.state = seed & 0xFFFFFFFF

    def uniform(self):
        self.state = (self.state * 1664525 + 1013904223) & 0xFFFFFFFF
        return (self.state >> 8) / 16777216.0

    def gauss(self):
        """About normal, mean 0, standard deviation 1 (sum of 12 uniforms)."""
        return sum([self.uniform() for _ in range(12)]) - 6.0


def pack(values24):
    """Pack 24-bit sample values into a frame of 32-bit microphone words."""
    words = [max(-(1 << 23), min((1 << 23) - 1, int(v))) << 8 for v in values24]
    return struct.pack(levels.FRAME_FORMAT, *words)


def _scale_to_bits(raw, bits):
    """Scale a list so its average distance from the middle is 2**bits."""
    middle = sum(raw) / len(raw)
    average = sum([abs(v - middle) for v in raw]) / len(raw)
    scale = (2 ** bits) / average
    return [(v - middle) * scale for v in raw]


def noise_frame(rng, bits, dc=15000):
    """Random noise of about the given loudness (bits), plus a DC offset."""
    raw = [rng.gauss() for _ in range(levels.FRAME_SAMPLES)]
    return pack([v + dc for v in _scale_to_bits(raw, bits)])


def speech_frame(rng, bits, noise_bits=12.9, dc=15000, phase=0):
    """A voiced-sound stand-in: a 120 Hz tone with harmonics plus noise."""
    n = levels.FRAME_SAMPLES
    rate = levels.RATE
    tone = []
    for i in range(n):
        t = (phase + i) / rate
        tone.append(math.sin(2 * math.pi * 120 * t)
                    + 0.6 * math.sin(2 * math.pi * 240 * t + 1.0)
                    + 0.4 * math.sin(2 * math.pi * 480 * t + 2.0))
    tone = _scale_to_bits(tone, bits)
    hiss = _scale_to_bits([rng.gauss() for _ in range(n)], noise_bits)
    return pack([a + b + dc for a, b in zip(tone, hiss)])


def clipped_frame(rng, noise_bits=12.9):
    """A frame whose peaks hit the rails, like a shout into the microphone."""
    n = levels.FRAME_SAMPLES
    values = []
    for i in range(n):
        v = 12_000_000 * math.sin(2 * math.pi * 200 * i / levels.RATE)
        values.append(v + rng.gauss() * 2 ** noise_bits)
    return pack(values)
