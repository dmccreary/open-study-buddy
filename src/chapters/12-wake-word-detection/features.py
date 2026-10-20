# features.py -- per-frame features for the wake-word detector (Chapter 12)
#
# One 40 ms frame (512 samples) goes in; 16 numbers come out, one per band:
# the natural log of the energy in that band. That is a "log band energy"
# feature, in the family of the MFCC features used by speech systems; the
# chapter explains what is missing (the DCT step), and dct() below is the bridge.
#
# The steps, in order, and where the time goes:
#   1. load      unpack the samples, remove the DC offset, apply a Hann window
#   2. transform an FFT of the 512 real samples (the slow step in plain Python)
#   3. power     |X[k]|^2 for the 256 useful bins
#   4. bands     add up the power in 16 log-spaced bands (100 to 6,400 Hz)
#   5. log       take the natural log (and subtract a constant, FEATURE_OFFSET)
#
# STEP 2 IS PLAIN PYTHON HERE, so it is far too slow for a 40 ms frame; it is
# a reference you can check, not the fast version. Chapter 10 builds the fast
# one. To use yours, write a function  fast(re, im, power)  that reads the
# frame's Hann-windowed, DC-free samples from `re` (512 floats; `im` is zeros)
# and fills `power` (256 floats) with |X[k]|^2, then pass it as
# Extractor(spectrum_fn=fast). Steps 3 to 5 do not change.
#
# The band layout (16 log-spaced bands, 100 to 6,400 Hz) is the same layout
# Chapter 9 draws on the spectrum display. The detector does not depend on
# Chapter 9's code: enrollment and detection both use THIS file's table.

import math
import struct
from array import array

import levels

N = levels.FRAME_SAMPLES            # 512
HALF = N // 2                       # 256 useful bins
BANDS = 16
F_LOW = 100                         # Hz
F_HIGH = 6400                       # Hz: half the 12,800 Hz sample rate
FEATURE_OFFSET = 20.0               # subtracted from every feature; mean subtraction
                                    # removes it, and it keeps the sums small


def band_edges(bands=BANDS, f_low=F_LOW, f_high=F_HIGH):
    """Bin numbers of the band edges: band i holds bins edges[i] .. edges[i+1]-1.

    The edges are spaced by a constant ratio. A band narrower than one bin is
    stretched to one bin."""
    ratio = (f_high / f_low) ** (1.0 / bands)
    edges = []
    for i in range(bands + 1):
        k = int(round(f_low * ratio ** i * N / levels.RATE))
        if edges and k <= edges[-1]:
            k = edges[-1] + 1
        edges.append(k)
    return edges


EDGES = band_edges()
EDGES_CHECK = sum(EDGES) & 0xFFFF   # stored in a template file, to catch a changed band table


def dct(values, count):
    """Discrete cosine transform (type II) of `values`, first `count` coefficients.

    Applied to the 16 log band energies of ONE frame it gives MFCC-like
    coefficients. Adding the same number to every value changes only
    coefficient 0, which is why MFCCs shrug off a change in overall gain."""
    n = len(values)
    out = []
    for k in range(count):
        total = 0.0
        for i in range(n):
            total += values[i] * math.cos(math.pi * k * (2 * i + 1) / (2 * n))
        out.append(total)
    return out


class Extractor:
    def __init__(self, spectrum_fn=None):
        self.spectrum_fn = spectrum_fn          # your fast version, or None
        self.re = array("f", [0.0] * N)
        self.im = array("f", [0.0] * N)
        self.power = array("f", [0.0] * HALF)
        self.window = array("f", [0.0] * N)     # Hann: 0.5 - 0.5 cos(2 pi i / N)
        for i in range(N):
            self.window[i] = 0.5 - 0.5 * math.cos(2 * math.pi * i / N)
        self.rev = array("H", [0] * N)          # bit-reversal table
        bits = 0
        while (1 << bits) < N:
            bits += 1
        for i in range(N):
            value, rev = i, 0
            for _ in range(bits):
                rev = (rev << 1) | (value & 1)
                value >>= 1
            self.rev[i] = rev
        self.cos_t = array("f", [math.cos(2 * math.pi * k / N) for k in range(HALF)])
        self.sin_t = array("f", [math.sin(2 * math.pi * k / N) for k in range(HALF)])

    # -- step 1 ------------------------------------------------------------
    def load32(self, buf, offset=0):
        """Load a frame of 32-bit microphone words (as read from the I2S driver)."""
        raw = struct.unpack_from(levels.FRAME_FORMAT, buf, offset)
        self._load([s >> levels.SHIFT for s in raw])

    def load16(self, buf, offset=0):
        """Load a frame of 16-bit samples (as stored by recorder.record)."""
        self._load(struct.unpack_from("<%dh" % N, buf, offset))

    def _load(self, samples):
        dc = sum(samples) // N
        re, im, win = self.re, self.im, self.window
        for i in range(N):
            re[i] = (samples[i] - dc) * win[i]
            im[i] = 0.0

    # -- steps 2 and 3 -----------------------------------------------------
    def transform(self):
        """In-place FFT of (re, im): the plain-Python reference (2,304 butterflies)."""
        re, im, rev = self.re, self.im, self.rev
        cos_t, sin_t = self.cos_t, self.sin_t
        for i in range(N):                       # reorder by the bit-reversal table
            j = rev[i]
            if j > i:
                re[i], re[j] = re[j], re[i]
                im[i], im[j] = im[j], im[i]
        size = 2
        while size <= N:
            half = size >> 1
            step = N // size
            for start in range(0, N, size):
                k = 0
                for a in range(start, start + half):
                    b = a + half
                    wr = cos_t[k]
                    wi = -sin_t[k]
                    tr = re[b] * wr - im[b] * wi
                    ti = re[b] * wi + im[b] * wr
                    re[b] = re[a] - tr
                    im[b] = im[a] - ti
                    re[a] += tr
                    im[a] += ti
                    k += step
            size <<= 1

    def to_power(self):
        re, im, power = self.re, self.im, self.power
        for k in range(HALF):
            power[k] = re[k] * re[k] + im[k] * im[k]

    # -- steps 4 and 5 -----------------------------------------------------
    def bands_log(self, out, out_offset=0):
        """Write the 16 log band energies into out[out_offset:out_offset+16]."""
        power = self.power
        for i in range(BANDS):
            total = 0.0
            for k in range(EDGES[i], EDGES[i + 1]):
                total += power[k]
            out[out_offset + i] = math.log(total + 1.0) - FEATURE_OFFSET

    # -- all five steps ----------------------------------------------------
    def finish(self, out, out_offset=0):
        """Steps 2 to 5 on the frame that was just loaded."""
        if self.spectrum_fn is not None:
            self.spectrum_fn(self.re, self.im, self.power)
        else:
            self.transform()
            self.to_power()
        self.bands_log(out, out_offset)

    def extract32(self, buf, out, out_offset=0, offset=0):
        self.load32(buf, offset)
        self.finish(out, out_offset)

    def extract16(self, buf, out, out_offset=0, offset=0):
        self.load16(buf, offset)
        self.finish(out, out_offset)
