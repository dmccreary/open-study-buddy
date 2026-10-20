# Chapter 10, Test 07: What does the second core buy you?
# Starts a worker thread, which MicroPython on the Pico runs on core 1, and
# measures four things: (A) how fast core 0 can count when it is alone,
# (B) how long the worker's FFTs take when it is alone, (C) both at the same
# time, using a viper FFT that allocates no memory, and (D) both at the same
# time, using the pure-Python float FFT, which allocates a lot. Needs only the
# Pico. The worker never touches the microphone, the speaker, the display, or
# any Pin: that is the safe pattern the chapter recommends.
#
# PASS: the script finishes with no error and prints four results. What to look
# for (EXPECTED, not yet measured): in C, core 0 counts at close to its solo
# rate and the worker takes close to its solo time (true parallelism); in D,
# either or both are slower than solo, because both cores share one heap and one
# garbage collector. WRITE DOWN all four ratios.
#
# If starting the second thread fails ("can't create thread"), a previous run
# left core 1 busy: press the reset button and run again.

NAME = "07-dual-core.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import _thread
import gc
import time
from array import array

import dsp
import fft_viper as fv

N = 512
K_VIPER = 20          # FFTs the worker does in experiment B and C
K_PURE = 3            # ... and in experiment D (the pure-Python FFT is slow)
SOLO_MS = 1000

# Buffers for the worker, made BEFORE the thread starts (no allocation in the thread's loop)
rev, cos_t, sin_t, hann_q = fv.make_q15_tables(N)
re_q = array("i", [0] * N)
im_q = array("i", [0] * N)
tables = dsp.make_tables(N)
re_f = array("f", [0.0] * N)
im_f = array("f", [0.0] * N)
for i in range(N):
    re_q[i] = (i * 37) % 2000 - 1000
    re_f[i] = float((i * 37) % 2000 - 1000)

state = [0, 0]        # [0] 0 = running, 1 = finished;  [1] elapsed microseconds


def worker_viper():
    t0 = time.ticks_us()
    for _ in range(K_VIPER):
        fv.fft_q15(re_q, im_q, rev, cos_t, sin_t, N)
    state[1] = time.ticks_diff(time.ticks_us(), t0)
    state[0] = 1


def worker_pure():
    t0 = time.ticks_us()
    for _ in range(K_PURE):
        dsp.fft(re_f, im_f, tables)
    state[1] = time.ticks_diff(time.ticks_us(), t0)
    state[0] = 1


def worker_idle():
    """Does nothing on core 1 for a second, so core 0 can count 'alone'."""
    t0 = time.ticks_us()
    time.sleep_ms(SOLO_MS)
    state[1] = time.ticks_diff(time.ticks_us(), t0)
    state[0] = 1


def run_with_worker(worker):
    """Start the worker on the other core and count on this core until it finishes.
    Returns (counts per second on core 0, worker microseconds)."""
    state[0] = 0
    gc.collect()
    started = time.ticks_us()
    _thread.start_new_thread(worker, ())
    n = 0
    while state[0] == 0:
        n += 1
    elapsed = time.ticks_diff(time.ticks_us(), started)
    time.sleep_ms(50)                 # let the worker's thread finish cleaning up
    return n * 1_000_000 / elapsed, state[1]


print()
solo_rate, _ = run_with_worker(worker_idle)      # same counting loop as in C and D
print("A  core 0 alone:            {:>12,.0f} passes per second".format(solo_rate))

# B: the worker alone (core 0 just sleeps)
state[0] = 0
_thread.start_new_thread(worker_viper, ())
while state[0] == 0:
    time.sleep_ms(5)
time.sleep_ms(50)
solo_us = state[1]
print("B  viper FFT x{} alone:     {:>12,.1f} ms ({:.2f} ms per FFT)".format(
    K_VIPER, solo_us / 1000, solo_us / 1000 / K_VIPER))

rate_c, us_c = run_with_worker(worker_viper)
print("C  viper FFT, both busy:    core 0 {:>10,.0f} per s ({:.0f}% of solo); worker {:.1f} ms ({:.0f}% of solo)".format(
    rate_c, 100 * rate_c / solo_rate, us_c / 1000, 100 * us_c / solo_us))

# D: pure Python FFT on the worker (allocates floats), measured alone first
state[0] = 0
_thread.start_new_thread(worker_pure, ())
while state[0] == 0:
    time.sleep_ms(5)
time.sleep_ms(50)
pure_solo_us = state[1]
rate_d, us_d = run_with_worker(worker_pure)
print("D  pure FFT x{} alone:       {:>12,.1f} ms".format(K_PURE, pure_solo_us / 1000))
print("D  pure FFT, both busy:     core 0 {:>10,.0f} per s ({:.0f}% of solo); worker {:.1f} ms ({:.0f}% of solo)".format(
    rate_d, 100 * rate_d / solo_rate, us_d / 1000, 100 * us_d / pure_solo_us))

print()
print("RESULT|dual|{:.0f}|{}|{:.0f}|{}|{:.0f}|{}|{}".format(
    solo_rate, solo_us, rate_c, us_c, rate_d, pure_solo_us, us_d))
print("Done. Read C and D against 100%: near 100% means the cores did not get in each other's way.")
