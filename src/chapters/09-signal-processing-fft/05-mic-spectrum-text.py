# Chapter 9, Test 05: Hear the spectrum as text
# Reads microphone frames, removes the DC offset, finds the RMS loudness,
# windows the frame with Hann, runs the pure-Python FFT, and prints one line
# per analyzed frame: loudness in dBFS, the peak frequency, and 16 log-spaced
# band levels as digits 0 to 9. No display needed. Needs the microphone.
#
# The pure-Python FFT is expected to take MORE than one 40 ms frame, so the
# loop uses dsp.latest_frame() to skip the frames that piled up while it was
# busy. The last column says how many it skipped. That number, and the
# "work ms" column, are what Chapter 10 sets out to shrink.
#
# PASS: whistle or play a steady tone near the microphone and the peak column
# settles near its frequency (within about 25 Hz) while one band digit rises;
# a quiet room shows low digits and "--" for the peak.

NAME = "05-mic-spectrum-text.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time
from array import array

import config
import dsp

N = config.FFT_SIZE
RATE = config.MIC_SAMPLE_RATE
BANDS = 16
ANALYSES = 60                     # how many frames to analyze before stopping
PEAK_GATE_DBFS = -50              # below this a "peak" is just noise (tune for your room)
DB_FLOOR = -90                    # band level shown as digit 0
DB_CEIL = -30                     # band level shown as digit 9

tables = dsp.make_tables(N)
window = dsp.hann_table(N)
re = array("f", [0.0] * N)
im = array("f", [0.0] * N)
mag = array("f", [0.0] * (N // 2))
energy = array("f", [0.0] * BANDS)
edges = dsp.log_band_edges(BANDS, 100, RATE // 2, RATE, N)
reference = dsp.dbfs_reference(N)         # 0 dBFS: the peak of a full-scale sine

buf = bytearray(N * 4)
mic = config.init_microphone()
try:
    for _ in range(8):                    # the microphone's start-up
        mic.readinto(buf)
    print()
    print("{:>4} {:>6} {:>7} {:>8}  {}  {:>7} {:>6}".format(
        "n", "dc", "dBFS", "peak Hz", "bands 100 Hz -> 6.4 kHz", "work ms", "skipped"))
    total_work = 0
    total_skipped = 0
    for n in range(ANALYSES):
        skipped = dsp.latest_frame(mic, buf)
        started = time.ticks_us()
        dc, rms = dsp.load_frame(buf, re, im, window, config.MIC_SAMPLE_SHIFT)
        dsp.fft(re, im, tables)
        dsp.magnitudes(re, im, mag)
        dsp.band_energies(mag, edges, energy)
        work_ms = time.ticks_diff(time.ticks_us(), started) / 1000
        dbfs = dsp.to_db(rms, 1 << (config.MIC_SAMPLE_BITS - config.MIC_SAMPLE_SHIFT - 1))
        if dbfs > PEAK_GATE_DBFS:
            peak = "{:>8.0f}".format(dsp.peak_frequency(mag, RATE, N)[0])
        else:
            peak = "      --"
        digits = ""
        for i in range(BANDS):
            level = dsp.to_db(energy[i], reference * reference, power=True)
            digits += str(dsp.scale(level, DB_FLOOR, DB_CEIL, 9))
        total_work += work_ms
        total_skipped += skipped
        print("{:>4} {:>6} {:>7.1f} {}  {}  {:>7.1f} {:>6}".format(
            n, dc, dbfs, peak, digits + " " * 8, work_ms, skipped))
    print()
    print("average work per analyzed frame: {:.1f} ms (budget per frame: {} ms)".format(
        total_work / ANALYSES, N * 1000 // RATE))
    print("frames skipped to stay current: {}".format(total_skipped))
finally:
    mic.deinit()
print("Done.")
