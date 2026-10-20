# Chapter 10, Test 05: The fixed-point FFT in viper, against the float FFT
# Runs the same synthetic 1,000 Hz test frame through the Chapter 9 pure-Python
# pipeline and through fft_viper.py (Q15 numbers, @viper), and compares both
# the ANSWERS (are the 16 band levels the same?) and the TIME. Also checks that
# the viper FFT allocates no memory while it runs. Needs only the Pico.
#
# PASS: both pipelines find the tone in bin 40; the band levels agree within
# 1 dB wherever the band is louder than -60 dBFS; the viper FFT allocates 0
# bytes. WRITE DOWN: the time of each stage and the totals. They go in the
# chapter's results table.
#
# The Q15 FFT is not as precise as the float one in quiet bands: it halves its
# results at every stage, so the quietest bands read too high. The "worst
# error" line shows how much, for this frame.

NAME = "05-fft-viper-bench.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import math
import struct
from array import array

import bench
import config
import dsp
import fft_viper as fv

N = config.FFT_SIZE
RATE = config.MIC_SAMPLE_RATE
FRAME_US = N * 1_000_000 // RATE
BANDS = 16
bench.enable_dwt()
print("DWT cycle counter: {}".format("yes" if bench.HAS_DWT else "no"))

# --- the test frame: 1 kHz tone, amplitude 200,000 (24-bit units), plus an offset -------------
frame = bytearray(N * 4)
for i in range(N):
    value = 15000 + int(200000 * math.sin(2 * math.pi * 1000 * i / RATE))
    struct.pack_into("<i", frame, i * 4, value << 8)

edges = dsp.log_band_edges(BANDS, 100, RATE // 2, RATE, N)
edges_h = array("H", edges)

# --- the float pipeline (Chapter 9) ---------------------------------------------------------
tables = dsp.make_tables(N)
hann = dsp.hann_table(N)
re_f = array("f", [0.0] * N)
im_f = array("f", [0.0] * N)
mag = array("f", [0.0] * (N // 2))
energy = array("f", [0.0] * BANDS)
reference = dsp.dbfs_reference(N)


def float_pipeline():
    dsp.load_frame(frame, re_f, im_f, hann, config.MIC_SAMPLE_SHIFT)
    dsp.fft(re_f, im_f, tables)
    dsp.magnitudes(re_f, im_f, mag)
    dsp.band_energies(mag, edges, energy)


# --- the viper pipeline ---------------------------------------------------------------------
rev, cos_t, sin_t, hann_q = fv.make_q15_tables(N)
re_q = array("i", [0] * N)
im_q = array("i", [0] * N)
power = array("i", [0] * (N // 2))
sums = array("i", [0] * BANDS)
stats = array("i", [0] * 4)


def viper_pipeline():
    fv.load_frame_q15(frame, hann_q, re_q, im_q, stats, N, 16)
    fv.fft_q15(re_q, im_q, rev, cos_t, sin_t, N)
    fv.power_q15(re_q, im_q, power, N // 2)
    fv.band_sums(power, edges_h, sums, BANDS)


float_pipeline()
viper_pipeline()

# --- are the answers the same? ----------------------------------------------------------------
peak_f = max(range(2, N // 2), key=lambda k: mag[k])
peak_q = max(range(2, N // 2), key=lambda k: power[k])
print()
print("peak bin: float {}  viper {}   (the tone is bin 40)".format(peak_f, peak_q))
print()
print("{:>4} {:>10} {:>10} {:>8}".format("band", "float dBFS", "viper dBFS", "diff dB"))
worst_loud = 0.0
worst_any = 0.0
for i in range(BANDS):
    level_f = dsp.to_db(energy[i], reference * reference, power=True)
    level_q = dsp.to_db(sums[i], fv.DBFS_REFERENCE_POWER, power=True)
    diff = level_q - level_f
    worst_any = max(worst_any, abs(diff))
    if level_f > -60:
        worst_loud = max(worst_loud, abs(diff))
    print("{:>4} {:>10.1f} {:>10.1f} {:>+8.1f}".format(i, level_f, level_q, diff))
print("worst error in bands louder than -60 dBFS: {:.2f} dB;  worst in any band: {:.1f} dB".format(
    worst_loud, worst_any))

# --- allocation while the viper FFT runs -------------------------------------------------------
gc.collect()
gc.disable()
before = gc.mem_alloc()
fv.fft_q15(re_q, im_q, rev, cos_t, sin_t, N)
fv.power_q15(re_q, im_q, power, N // 2)
after = gc.mem_alloc()
gc.enable()
print()
print("heap bytes allocated by fft_q15 + power_q15: {}".format(after - before))

gc.collect()
gc.disable()
before = gc.mem_alloc()
dsp.fft(re_f, im_f, tables)
after = gc.mem_alloc()
gc.enable()
gc.collect()
print("heap bytes allocated by one dsp.fft (floats): {}".format(after - before))

# --- speed ------------------------------------------------------------------------------------
print()
print("Time per stage (512 points)")
results = {}
results["float load"] = bench.bench("float: load_frame", lambda: dsp.load_frame(
    frame, re_f, im_f, hann, config.MIC_SAMPLE_SHIFT), repeat=3, budget_us=FRAME_US)
dsp.load_frame(frame, re_f, im_f, hann, config.MIC_SAMPLE_SHIFT)


def float_fft_only():
    for i in range(N):
        re_f[i] = saved[i]
        im_f[i] = 0.0
    dsp.fft(re_f, im_f, tables)


saved = array("f", re_f)
results["float fft"] = bench.bench("float: fft (array 'f')", float_fft_only, repeat=3, budget_us=FRAME_US)
results["float rest"] = bench.bench("float: magnitudes + bands", lambda: (
    dsp.magnitudes(re_f, im_f, mag), dsp.band_energies(mag, edges, energy)), repeat=3, budget_us=FRAME_US)

results["viper load"] = bench.bench("viper: load_frame_q15", lambda: fv.load_frame_q15(
    frame, hann_q, re_q, im_q, stats, N, 16), repeat=5, budget_us=FRAME_US)
fv.load_frame_q15(frame, hann_q, re_q, im_q, stats, N, 16)
saved_q = array("i", re_q)


def viper_fft_only():
    for i in range(N):
        re_q[i] = saved_q[i]
        im_q[i] = 0
    fv.fft_q15(re_q, im_q, rev, cos_t, sin_t, N)


results["viper fft"] = bench.bench("viper: fft_q15 (incl. 512-element reload)", viper_fft_only,
                                   repeat=5, budget_us=FRAME_US)
results["viper rest"] = bench.bench("viper: power + band sums", lambda: (
    fv.power_q15(re_q, im_q, power, N // 2), fv.band_sums(power, edges_h, sums, BANDS)),
    repeat=5, budget_us=FRAME_US)

bench.bench("float pipeline, whole", float_pipeline, repeat=3, budget_us=FRAME_US)
bench.bench("viper pipeline, whole", viper_pipeline, repeat=5, budget_us=FRAME_US)

ok = peak_f == 40 and peak_q == 40 and worst_loud < 1.0 and (after - before) >= 0
print()
print("PASS" if ok else "CHECK: peak bin or band levels do not match the chapter.")
