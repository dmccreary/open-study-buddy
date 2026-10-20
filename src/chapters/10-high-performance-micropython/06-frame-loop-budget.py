# Chapter 10, Test 06: Does the real loop fit in 40 ms?
# The timing-verification test. Runs the live microphone loop for 8 seconds
# with the pure-Python pipeline (Chapter 9) and then for 8 seconds with the
# viper Q15 pipeline (fft_viper.py). For every pass it records how long
# readinto() WAITED and how long your code WORKED, and then reports the mean,
# the 95th percentile, and the worst pass, the number of frame overruns, and a
# pass/fail verdict against the real-time constraint. Needs the microphone.
# (The display is not drawn; see the reserve below.)
#
# Definitions
#   frame budget   FRAME_US = 512 * 1,000,000 / 12,800 = 40,000 us
#   work           time between readinto() returning and the next readinto() call
#   overrun        a pass whose work is longer than the frame budget. The audio
#                  keeps arriving while you are busy, so the next readinto()
#                  returns at once with old data and the backlog grows
#   behind         readinto() returned in under 4 ms: the frame was already
#                  waiting, so the loop is behind real time
#   reserve        DISPLAY_RESERVE_US of the budget is kept for the screen
#                  update that is not drawn here (Chapter 6 measured 8.5 ms for
#                  the spectrum region; 10 ms leaves a little margin)
#
# PASS (per mode): zero overruns, and the worst pass is no longer than
# FRAME_US - DISPLAY_RESERVE_US. The pure-Python mode is EXPECTED to fail; that
# is the point of the chapter. WRITE DOWN both summaries.

NAME = "06-frame-loop-budget.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import time
from array import array

import bench
import config
import dsp
import fft_viper as fv

N = config.FFT_SIZE
RATE = config.MIC_SAMPLE_RATE
FRAME_US = N * 1_000_000 // RATE
DISPLAY_RESERVE_US = 10_000
RUN_MS = 8000
MAX_PASSES = 400
BANDS = 16
SHIFT = config.MIC_SAMPLE_SHIFT

bench.enable_dwt()

# --- pure Python buffers and tables (Chapter 9) ---
tables = dsp.make_tables(N)
hann = dsp.hann_table(N)
re_f = array("f", [0.0] * N)
im_f = array("f", [0.0] * N)
mag = array("f", [0.0] * (N // 2))
energy = array("f", [0.0] * BANDS)
edges = dsp.log_band_edges(BANDS, 100, RATE // 2, RATE, N)

# --- viper buffers and tables ---
rev, cos_t, sin_t, hann_q = fv.make_q15_tables(N)
re_q = array("i", [0] * N)
im_q = array("i", [0] * N)
power = array("i", [0] * (N // 2))
sums = array("i", [0] * BANDS)
stats = array("i", [0] * 4)
edges_h = array("H", edges)

frame = bytearray(N * 4)
work_us = array("I", [0] * MAX_PASSES)
wait_us = array("I", [0] * MAX_PASSES)


def process_pure():
    dsp.load_frame(frame, re_f, im_f, hann, SHIFT)
    dsp.fft(re_f, im_f, tables)
    dsp.magnitudes(re_f, im_f, mag)
    dsp.band_energies(mag, edges, energy)


def process_viper():
    fv.load_frame_q15(frame, hann_q, re_q, im_q, stats, N, 16)
    fv.fft_q15(re_q, im_q, rev, cos_t, sin_t, N)
    fv.power_q15(re_q, im_q, power, N // 2)
    fv.band_sums(power, edges_h, sums, BANDS)


def percentile(values, count, fraction):
    ordered = sorted(values[i] for i in range(count))
    return ordered[min(count - 1, int(fraction * count))]


def run(label, process):
    mic = config.init_microphone()
    gc.collect()
    prof = bench.Profiler()
    try:
        for _ in range(8):                        # the microphone's start-up
            mic.readinto(frame)
        passes = 0
        started = time.ticks_ms()
        prof.restart()
        while passes < MAX_PASSES and time.ticks_diff(time.ticks_ms(), started) < RUN_MS:
            t0 = time.ticks_us()
            mic.readinto(frame)
            t1 = time.ticks_us()
            prof.lap("wait (readinto)")
            process()
            t2 = time.ticks_us()
            prof.lap("work (process)")
            wait_us[passes] = time.ticks_diff(t1, t0)
            work_us[passes] = time.ticks_diff(t2, t1)
            passes += 1
    finally:
        mic.deinit()
    overruns = 0
    behind = 0
    total_work = 0
    worst = 0
    for i in range(passes):
        total_work += work_us[i]
        worst = max(worst, work_us[i])
        if work_us[i] > FRAME_US:
            overruns += 1
        if wait_us[i] < 4000:
            behind += 1
    limit = FRAME_US - DISPLAY_RESERVE_US
    print()
    print("== {} ==".format(label))
    print("passes in {} ms: {}   (a loop that keeps up would make {})".format(
        RUN_MS, passes, RUN_MS * 1000 // FRAME_US))
    print("work per pass: mean {:.2f} ms, 95th percentile {:.2f} ms, worst {:.2f} ms".format(
        total_work / passes / 1000, percentile(work_us, passes, 0.95) / 1000, worst / 1000))
    print("frame overruns (work > {} ms): {}   passes behind real time: {}".format(
        FRAME_US // 1000, overruns, behind))
    print("worst pass uses {:.0f}% of the 40 ms frame; the limit with the display reserve is {} ms".format(
        100 * worst / FRAME_US, limit // 1000))
    prof.report(passes, FRAME_US)
    passed = overruns == 0 and worst <= limit
    print("VERDICT: {}".format("PASS, the real-time constraint is met with room for the display."
                               if passed else
                               "FAIL, this loop does not keep up."))
    print("RESULT|{}|{}|{}|{}|{}".format(label, passes, total_work // passes, worst, overruns))
    return passed


print()
print("Frame budget {} us, display reserve {} us.".format(FRAME_US, DISPLAY_RESERVE_US))
run("pure Python (Chapter 9)", process_pure)
run("viper Q15 (fft_viper.py)", process_viper)
print()
print("Done. Compare the two VERDICT lines with the chapter's results table.")
