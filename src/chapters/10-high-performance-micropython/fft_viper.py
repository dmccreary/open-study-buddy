# fft_viper.py -- a fixed-point (Q15) FFT in @micropython.viper (Chapter 10)
#
# The same 512-point, radix-2, in-place FFT as dsp.fft(), but every number is a
# whole number in a machine register and nothing is allocated while it runs.
#
# Q15 means "15 bits after the binary point": the whole number 16384 stands
# for 0.5 and 32768 stands for 1.0. A Q15 product needs a shift right by 15
# to come back to Q15.
#
# SCALING. Every butterfly output is halved (>> 1), so after the 9 stages of a
# 512-point FFT the results are the true FFT divided by 512. That keeps every
# number inside 16 bits (no overflow, ever) and costs resolution: tones that
# are only a few units tall at the input are partly lost in rounding. The
# chapter measures this against the floating-point FFT. For a full-scale sine
# with the Hann window the peak bin reads 8,192 (= 32768 * 0.25), and
# DBFS_REFERENCE_POWER below is that squared.
#
# HOW BIG CAN A NUMBER GET? Inputs are limited to +-32768 (the loader clamps).
# Each butterfly keeps |re + j im| <= 32768. A twiddle product re*c + im*s is at
# most |z| * 32768 <= 1.53e9, which fits a signed 32-bit register (2.147e9),
# so no step can overflow.
#
# Needs a MicroPython board. The functions are written to run in real
# MicroPython on a computer as well (unix port) so they can be checked.

import math
import micropython
from array import array

N = 512
DBFS_REFERENCE_POWER = 8192 * 8192      # power of a full-scale sine's peak bin


def make_q15_tables(n=N):
    """Returns (rev, cos_t, sin_t, hann). Build them once at start-up.

    rev    array('H')  bit-reversal table
    cos_t  array('i')  cos(2*pi*k/n) * 32768, k = 0 .. n/2 - 1
    sin_t  array('i')  sin(2*pi*k/n) * 32768
    hann   array('i')  the Hann window in Q15 (0 .. 32767)"""
    bits = 0
    while (1 << bits) < n:
        bits += 1
    rev = array("H", [0] * n)
    for i in range(n):
        value = i
        r = 0
        for _ in range(bits):
            r = (r << 1) | (value & 1)
            value >>= 1
        rev[i] = r
    half = n // 2
    cos_t = array("i", [0] * half)
    sin_t = array("i", [0] * half)
    for k in range(half):
        angle = 2 * math.pi * k / n
        cos_t[k] = int(round(math.cos(angle) * 32768))
        sin_t[k] = int(round(math.sin(angle) * 32768))
    hann = array("i", [0] * n)
    for i in range(n):
        v = int(round((0.5 - 0.5 * math.cos(2 * math.pi * i / n)) * 32768))
        hann[i] = 32767 if v > 32767 else v
    return rev, cos_t, sin_t, hann


@micropython.viper
def load_frame_q15(buf: ptr32, window: ptr32, re: ptr32, im: ptr32,
                   stats: ptr32, n: int, shift: int):
    """Microphone frame -> windowed, DC-free Q15 input.

    buf    the raw frame: n signed 32-bit words straight from readinto()
    shift  16 turns the 24-bit sample into a 16-bit one; smaller values add
           gain (12 multiplies by 16) and clip loud sounds at +-32767
    stats  array('i') of 4 numbers that this call fills in:
           stats[0] the DC offset removed
           stats[1] and stats[2] the sum of squares, as stats[1] * 2**30 + stats[2]
           (two parts, because the full sum does not fit in 32 bits)"""
    total = 0
    i = 0
    while i < n:
        x = int(buf[i]) >> shift
        if x > 32767:
            x = 32767
        if x < -32768:
            x = -32768
        total += x
        i += 1
    dc = total // n
    hi = 0
    lo = 0
    i = 0
    while i < n:
        x = (int(buf[i]) >> shift) - dc
        if x > 32767:
            x = 32767
        if x < -32768:
            x = -32768
        lo += x * x
        if lo >= 1073741824:          # carry into the high part every 2**30
            lo -= 1073741824
            hi += 1
        re[i] = (x * int(window[i])) >> 15
        im[i] = 0
        i += 1
    stats[0] = dc
    stats[1] = hi
    stats[2] = lo


@micropython.viper
def fft_q15(re: ptr32, im: ptr32, rev: ptr16, cos_t: ptr32, sin_t: ptr32, n: int):
    """In-place radix-2 FFT of n Q15 numbers; every stage halves its results."""
    i = 0
    while i < n:                              # step 1: bit-reversal reorder
        j = int(rev[i])
        if j > i:
            t = int(re[i])
            re[i] = int(re[j])
            re[j] = t
            t = int(im[i])
            im[i] = int(im[j])
            im[j] = t
        i += 1
    half = 1
    stride = n >> 1                           # twiddle step; halves every stage
    while half < n:                           # step 2: log2(n) stages
        start = 0
        while start < n:
            k = 0
            while k < half:
                a = start + k
                b = a + half
                c = int(cos_t[k * stride])
                s = int(sin_t[k * stride])
                rb = int(re[b])
                ib = int(im[b])
                tr = (rb * c + ib * s + 16384) >> 15       # twiddle * second number
                ti = (ib * c - rb * s + 16384) >> 15
                ra = int(re[a])
                ia = int(im[a])
                re[b] = (ra - tr + 1) >> 1                  # difference, halved
                im[b] = (ia - ti + 1) >> 1
                re[a] = (ra + tr + 1) >> 1                  # sum, halved
                im[a] = (ia + ti + 1) >> 1
                k += 1
            start += 2 * half
        half <<= 1
        stride >>= 1


@micropython.viper
def power_q15(re: ptr32, im: ptr32, out: ptr32, count: int):
    """out[k] = re[k]**2 + im[k]**2 for k < count (cannot overflow: |z| <= 32768)."""
    k = 0
    while k < count:
        r = int(re[k])
        m = int(im[k])
        out[k] = r * r + m * m
        k += 1


@micropython.viper
def band_sums(power: ptr32, edges: ptr16, out: ptr32, bands: int):
    """out[i] = sum of power[k] for k in edges[i] .. edges[i+1] - 1."""
    i = 0
    while i < bands:
        total = 0
        k = int(edges[i])
        stop = int(edges[i + 1])
        while k < stop:
            total += int(power[k])
            k += 1
        out[i] = total
        i += 1


def rms_from_stats(stats, n=N):
    """RMS (in 16-bit units) from the two-part sum of squares load_frame_q15 made."""
    return math.sqrt((stats[1] * 1073741824 + stats[2]) / n)
