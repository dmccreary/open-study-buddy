# Chapter 10, Test 02: How slow is the pure-Python FFT?
# Times the Chapter 9 library (dsp.py) on the Pico: the FFT alone on plain lists
# and on array('f'), the same FFT at 128, 256 and 512 points (to check the
# N log N scaling), and every other step of the Chapter 9 pipeline. Then it
# adds them up and compares the total with the 40 ms frame budget. Needs only
# the Pico. No microphone: the input is a synthetic 1,000 Hz tone.
#
# PASS: the peak bin is 40 in every case, and you have a table of numbers.
# WRITE DOWN: the "fft 512, array" time, and the pipeline total. They are the
# first row of the chapter's results table.

NAME = "02-fft-pure-python-bench.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import math
import struct
from array import array

import bench
import config
import dsp

RATE = config.MIC_SAMPLE_RATE
N = config.FFT_SIZE
FRAME_US = N * 1_000_000 // RATE
bench.enable_dwt()
print("DWT cycle counter: {}".format("yes" if bench.HAS_DWT else "no (times are in microseconds only)"))


def tone_frame(n, freq=1000):
    """n microphone-style 32-bit words holding a 1 kHz tone plus a DC offset."""
    buf = bytearray(n * 4)
    for i in range(n):
        value = 15000 + int(200000 * math.sin(2 * math.pi * freq * i / RATE))
        struct.pack_into("<i", buf, i * 4, value << 8)
    return buf


def peak_bin(mag):
    best = 2
    for k in range(2, len(mag)):
        if mag[k] > mag[best]:
            best = k
    return best


frame = tone_frame(N)
ok = True

print()
print("The FFT alone")
print("{:<34} {:>13} {:>19} {:>16}".format("case", "time", "cycles", "frame budget"))
for size in (128, 256, 512):
    tables = dsp.make_tables(size)
    window = dsp.hann_table(size)
    sub = tone_frame(size)
    re = array("f", [0.0] * size)
    im = array("f", [0.0] * size)
    dsp.load_frame(sub, re, im, window, config.MIC_SAMPLE_SHIFT)
    saved_re = array("f", re)

    def run_fft(re=re, im=im, saved=saved_re, tables=tables, size=size):
        # restore the input first (the FFT is in place), then transform
        for i in range(size):
            re[i] = saved[i]
            im[i] = 0.0
        dsp.fft(re, im, tables)

    us, cyc = bench.bench("fft {} points, array('f')".format(size), run_fft, repeat=3,
                          budget_us=FRAME_US)
    butterflies = size // 2 * int(math.log(size) / math.log(2) + 0.5)
    print("    -> {:.1f} us per butterfly ({:,} butterflies)".format(us / butterflies, butterflies))
    if size == N:
        fft512_us = us
        mags = array("f", [0.0] * (size // 2))
        dsp.magnitudes(re, im, mags)
        ok = ok and peak_bin(mags) == 40

# The same 512-point FFT on plain lists
tables = dsp.make_tables(N)
window = dsp.hann_table(N)
re_a = array("f", [0.0] * N)
im_a = array("f", [0.0] * N)
dsp.load_frame(frame, re_a, im_a, window, config.MIC_SAMPLE_SHIFT)
re_l = list(re_a)
im_l = [0.0] * N
saved_l = list(re_a)


def run_fft_lists():
    for i in range(N):
        re_l[i] = saved_l[i]
        im_l[i] = 0.0
    dsp.fft(re_l, im_l, tables)


bench.bench("fft 512 points, plain lists", run_fft_lists, repeat=3, budget_us=FRAME_US)

# Every step of the pipeline, in the order the loop runs them
print()
print("The whole Chapter 9 pipeline, step by step (512 points, array('f'))")
re = array("f", [0.0] * N)
im = array("f", [0.0] * N)
mag = array("f", [0.0] * (N // 2))
energy = array("f", [0.0] * 16)
edges = dsp.log_band_edges(16, 100, RATE // 2, RATE, N)
reference = dsp.dbfs_reference(N)


def step_load():
    dsp.load_frame(frame, re, im, window, config.MIC_SAMPLE_SHIFT)


def step_mag():
    dsp.magnitudes(re, im, mag)


def step_bands():
    dsp.band_energies(mag, edges, energy)
    for i in range(16):
        dsp.to_db(energy[i], reference * reference, power=True)


load_us, _ = bench.bench("load_frame (DC, RMS, window)", step_load, repeat=3, budget_us=FRAME_US)
dsp.fft(re, im, tables)                    # leave a real spectrum in re/im for the next two steps
mag_us, _ = bench.bench("magnitudes (256 square roots)", step_mag, repeat=3, budget_us=FRAME_US)
bands_us, _ = bench.bench("band energies + 16 dB values", step_bands, repeat=3, budget_us=FRAME_US)
total_us = load_us + fft512_us + mag_us + bands_us
print()
print("pipeline total: {:.1f} ms = {:.0f}% of the {} ms frame budget".format(
    total_us / 1000, 100 * total_us / FRAME_US, FRAME_US // 1000))
print("(the display redraw of Chapter 9 test 07 comes on top of this)")

print()
print("memory free:", gc.mem_free())
print("PASS" if ok else "CHECK: the 1,000 Hz tone did not land in bin 40.")
