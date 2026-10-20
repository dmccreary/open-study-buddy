# dsp.py -- the pure-Python signal-processing toolbox from Chapter 9
#
# Chapter 10 keeps an IDENTICAL copy of this file (so each chapter folder is
# self-contained when it is uploaded). If you change one, change both.
#
# Everything here is plain MicroPython (it also runs on a computer):
#
#   make_tables(n)            bit-reversal table + twiddle factors for an n-point FFT
#   fft(re, im, tables)       in-place radix-2 FFT of n complex numbers
#   naive_dft(x)              the slow textbook DFT, for checking fft()
#   hann_table(n)             the Hann window as an array of n numbers
#   load_frame(...)           microphone bytes -> windowed, DC-free real input
#   magnitudes(re, im, out)   |X[k]| for the n/2 useful bins
#   bin_of(freq, rate, n)     which bin a frequency lands in (a float)
#   freq_of(k, rate, n)       the frequency at the center of bin k
#   peak_frequency(mag, ...)  the loudest frequency, with optional refinement
#   log_band_edges(...)       bin edges for log-spaced bands
#   band_energies(mag, edges) energy in each band
#   to_db / dbfs_reference    decibel helpers
#   scale(value, low, high, steps)   map a level onto 0 .. steps (bar heights)
#   frame_rms(buf, ...)       DC offset and RMS loudness only (no FFT)
#   latest_frame(mic, buf)    read the newest frame, skipping any backlog
#
# Conventions used throughout the chapter:
#   * A frame has n = 512 samples at 12,800 Hz, so each bin is 25 Hz wide.
#   * The FFT is "decimation in time": reorder by the bit-reversal table, then
#     do log2(n) = 9 stages of butterflies, in place.
#   * Twiddle factor W^k = cos(2*pi*k/n) - j*sin(2*pi*k/n). The tables store
#     the cosine and the (positive) sine, and fft() applies the minus sign.

import math
import struct
import time
from array import array


def make_tables(n):
    """Returns (rev, cos_t, sin_t) for an n-point FFT. n must be a power of 2.

    rev[i]   the position index i moves to (its bits written backwards)
    cos_t[k] cos(2*pi*k/n) for k = 0 .. n/2 - 1
    sin_t[k] sin(2*pi*k/n) for k = 0 .. n/2 - 1
    Build these ONCE at start-up; they never change."""
    bits = 0
    while (1 << bits) < n:
        bits += 1
    if (1 << bits) != n:
        raise ValueError("n must be a power of 2")
    rev = array("H", [0] * n)
    for i in range(n):
        value = i
        reversed_bits = 0
        for _ in range(bits):
            reversed_bits = (reversed_bits << 1) | (value & 1)
            value >>= 1
        rev[i] = reversed_bits
    half = n // 2
    cos_t = array("f", [0.0] * half)
    sin_t = array("f", [0.0] * half)
    for k in range(half):
        angle = 2 * math.pi * k / n
        cos_t[k] = math.cos(angle)
        sin_t[k] = math.sin(angle)
    return rev, cos_t, sin_t


def fft(re, im, tables):
    """In-place FFT. re and im hold the real and imaginary parts of n numbers
    (lists or array('f')); when the call returns they hold the n results.

    Step 1 puts the inputs in bit-reversed order. Step 2 runs 9 stages (for
    n = 512). Stage s combines pairs that are `half` apart, where half is
    1, 2, 4, ... n/2. Each pair is one butterfly: multiply the second number
    by a twiddle factor, then add it to and subtract it from the first."""
    rev, cos_t, sin_t = tables
    n = len(re)
    for i in range(n):                          # step 1: bit-reversal reorder
        j = rev[i]
        if j > i:
            re[i], re[j] = re[j], re[i]
            im[i], im[j] = im[j], im[i]
    half = 1
    while half < n:                             # step 2: log2(n) stages
        stride = n // (2 * half)                # twiddle step for this stage
        for start in range(0, n, 2 * half):
            for k in range(half):
                a = start + k
                b = a + half
                c = cos_t[k * stride]
                s = sin_t[k * stride]
                tr = re[b] * c + im[b] * s      # (re + j im) * (c - j s)
                ti = im[b] * c - re[b] * s
                re[b] = re[a] - tr
                im[b] = im[a] - ti
                re[a] += tr
                im[a] += ti
        half *= 2


def naive_dft(x):
    """The textbook DFT: n multiply-adds for each of n outputs, n*n in all.
    Returns (re, im) as lists. Use it only to check fft() on small n."""
    n = len(x)
    out_re = []
    out_im = []
    for k in range(n):
        sum_re = 0.0
        sum_im = 0.0
        for t in range(n):
            angle = 2 * math.pi * k * t / n
            sum_re += x[t] * math.cos(angle)
            sum_im -= x[t] * math.sin(angle)
        out_re.append(sum_re)
        out_im.append(sum_im)
    return out_re, out_im


def hann_table(n):
    """The (periodic) Hann window: 0 at both ends, 1 in the middle.
    w[i] = 0.5 - 0.5*cos(2*pi*i/n). Multiply the frame by it before the FFT."""
    table = array("f", [0.0] * n)
    for i in range(n):
        table[i] = 0.5 - 0.5 * math.cos(2 * math.pi * i / n)
    return table


def load_frame(buf, re, im, window, shift=8):
    """Turn one microphone frame (bytes of 32-bit samples) into FFT input.

    1. Shift each sample right by `shift` (8 for the INMP441) to get its 24-bit value.
    2. DC offset removal: subtract the frame's average.
    3. RMS loudness of the DC-free samples (before windowing).
    4. Windowing: multiply by the window; the imaginary part is zero.

    Returns (dc, rms)."""
    n = len(re)
    raw = struct.unpack_from("<%di" % n, buf)
    total = 0
    for i in range(n):
        total += raw[i] >> shift
    dc = total // n
    square_sum = 0
    for i in range(n):
        x = (raw[i] >> shift) - dc
        square_sum += x * x
        re[i] = x * window[i]
        im[i] = 0.0
    return dc, math.sqrt(square_sum / n)


def magnitudes(re, im, out):
    """out[k] = sqrt(re[k]^2 + im[k]^2) for k = 0 .. len(out)-1.
    For a real input, only the first n/2 bins are independent, so
    len(out) is normally n/2 (256 for the kit)."""
    for k in range(len(out)):
        out[k] = math.sqrt(re[k] * re[k] + im[k] * im[k])


def bin_of(freq, rate, n):
    """Where a frequency lands, as a float: 1,000 Hz at 12,800/512 -> 40.0."""
    return freq * n / rate


def freq_of(k, rate, n):
    """The frequency at the center of bin k."""
    return k * rate / n


def peak_frequency(mag, rate, n, first_bin=2, refine=True):
    """Frequency of the loudest bin at or above first_bin (skips the DC end).

    With refine=True, fit a parabola through the log-magnitudes of the peak
    bin and its two neighbors; the top of the parabola is usually closer to
    the true frequency than the bin center (see Chapter 9). Returns
    (frequency in Hz, peak bin number)."""
    best = first_bin
    for k in range(first_bin, len(mag) - 1):
        if mag[k] > mag[best]:
            best = k
    if not refine or best <= 0 or best >= len(mag) - 1:
        return freq_of(best, rate, n), best
    a = math.log(mag[best - 1] + 1e-9)
    b = math.log(mag[best] + 1e-9)
    c = math.log(mag[best + 1] + 1e-9)
    denominator = a - 2 * b + c
    offset = 0.5 * (a - c) / denominator if denominator != 0 else 0.0
    return freq_of(best + offset, rate, n), best


def log_band_edges(bands, f_low, f_high, rate, n):
    """Bin edges for `bands` log-spaced bands from f_low to f_high (Hz).

    Returns a list of bands + 1 bin numbers. Band i holds bins
    edges[i] .. edges[i+1] - 1. Every band gets at least one bin, so the
    lowest bands (narrower than one bin) are stretched to one bin wide."""
    ratio = (f_high / f_low) ** (1.0 / bands)
    edges = []
    for i in range(bands + 1):
        k = int(round(f_low * ratio ** i * n / rate))
        if edges and k <= edges[-1]:
            k = edges[-1] + 1
        edges.append(k)
    return edges


def band_energies(mag, edges, out):
    """out[i] = sum of mag[k]^2 over the bins of band i (its energy)."""
    for i in range(len(out)):
        total = 0.0
        for k in range(edges[i], edges[i + 1]):
            total += mag[k] * mag[k]
        out[i] = total


def to_db(value, reference=1.0, floor=-120.0, power=False):
    """Decibels. For an amplitude (or magnitude) use 20*log10(value/reference);
    for an energy or power (power=True) use 10*log10. Never below `floor`."""
    if value <= 0:
        return floor
    ratio = value / reference
    db = (10.0 if power else 20.0) * math.log10(ratio)
    return db if db > floor else floor


def dbfs_reference(n, bits=24, window_gain=0.5):
    """Magnitude of the FFT peak of a full-scale sine, the 0 dBFS reference.

    A sine of amplitude A gives a peak of A*n/2 with no window, and
    A*n/2*window_gain with one (0.5 for Hann). A is 2^(bits-1) for
    signed samples of that many bits."""
    return (1 << (bits - 1)) * n / 2 * window_gain


def scale(value, low, high, steps):
    """Map value from the range low .. high onto the whole numbers 0 .. steps.
    Values outside the range are clamped. Used for bar heights."""
    fraction = (value - low) / (high - low)
    if fraction < 0:
        return 0
    if fraction > 1:
        return steps
    return int(fraction * steps)


def frame_rms(buf, n=512, shift=8):
    """DC offset and RMS loudness of one microphone frame, without any FFT.
    Returns (dc, rms). This is all a volume meter needs."""
    raw = struct.unpack_from("<%di" % n, buf)
    total = 0
    for i in range(n):
        total += raw[i] >> shift
    dc = total // n
    square_sum = 0
    for i in range(n):
        x = (raw[i] >> shift) - dc
        square_sum += x * x
    return dc, math.sqrt(square_sum / n)


def latest_frame(mic, buf, instant_us=4000, limit=12):
    """Fill buf with the newest frame the microphone has, and return how many
    older frames were skipped to get it.

    readinto() blocks until a frame is ready. If the program was busy, frames
    are already waiting in the I2S ring buffer and readinto() returns almost
    at once; every call faster than instant_us therefore means "that frame was
    old". Keep reading until one call has to wait for fresh sound. Use this
    when the analysis takes longer than one frame (40 ms) and you would
    rather show the present than a stale past."""
    skipped = 0
    while skipped < limit:
        started = time.ticks_us()
        mic.readinto(buf)
        if time.ticks_diff(time.ticks_us(), started) >= instant_us:
            break
        skipped += 1
    return skipped
