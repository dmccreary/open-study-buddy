# Chapter 9, Test 04: Spectral leakage, with and without the Hann window
# Builds pure test tones (no microphone), takes their 512-point FFT with and
# without the Hann window, and prints how far each tone "leaks" into
# neighboring bins. Also finds the peak frequency of a 440 Hz tone, with and
# without refinement. Runs on the Pico or on your computer
# (python3 04-leakage-hann.py). Needs no hardware.
#
# PASS: a tone exactly on a bin (1,000 Hz) has no leakage without a window
# (1 loud bin) and a three-bin peak with Hann; a tone between bins
# (1,012.5 Hz) leaks into many bins without a window and into far fewer
# with Hann; the last line says PASS.

NAME = "04-leakage-hann.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
from array import array

import dsp

RATE = 12800
N = 512
AMPLITUDE = 1000.0
tables = dsp.make_tables(N)
hann = dsp.hann_table(N)
mag = array("f", [0.0] * (N // 2))


def spectrum(freq, window):
    """Magnitude spectrum of a sine of the given frequency (window None = none).
    Fills `mag` and returns the number of the loudest bin."""
    re = array("f", [0.0] * N)
    im = array("f", [0.0] * N)
    for i in range(N):
        x = AMPLITUDE * math.sin(2 * math.pi * freq * i / RATE)
        re[i] = x * window[i] if window is not None else x
    dsp.fft(re, im, tables)
    dsp.magnitudes(re, im, mag)
    peak = 0
    for k in range(N // 2):
        if mag[k] > mag[peak]:
            peak = k
    return peak


def loud_bins(fraction):
    """How many bins are at least `fraction` of the loudest bin."""
    top = max(mag)
    count = 0
    for k in range(N // 2):
        if mag[k] >= fraction * top:
            count += 1
    return count


print()
print("Sine of amplitude {:.0f}, N = {}, bin width {} Hz".format(AMPLITUDE, N, RATE / N))
print()
print("{:>8} {:>7} {:>5} {:>10} {:>14} {:>16}".format(
    "tone Hz", "window", "peak", "peak size", "bins >= 10%", "20 bins away"))
results = {}
for freq in (1000.0, 1006.25, 1012.5, 1037.5):
    for name, window in (("none", None), ("Hann", hann)):
        peak = spectrum(freq, window)
        top = mag[peak]
        far_db = dsp.to_db(mag[peak + 20], top)
        count = loud_bins(0.10)
        results[(freq, name)] = (peak, top, count, far_db)
        print("{:>8} {:>7} {:>5} {:>10,.0f} {:>14} {:>13.1f} dB".format(
            freq, name, peak, top, count, far_db))

print()
print("On a bin center the peak is A*N/2 = {:,.0f} without a window and half".format(AMPLITUDE * N / 2))
print("of that with Hann (the window's average height is 0.5).")

print()
print("Peak frequency of a 440 Hz tone (bin 17.6) with the Hann window:")
spectrum(440.0, hann)
plain, bin_plain = dsp.peak_frequency(mag, RATE, N, refine=False)
refined, _ = dsp.peak_frequency(mag, RATE, N, refine=True)
print("  loudest bin {}  -> {:.1f} Hz (error {:+.1f} Hz)".format(bin_plain, plain, plain - 440))
print("  refined          -> {:.1f} Hz (error {:+.1f} Hz)".format(refined, refined - 440))

on_rect = results[(1000.0, "none")]
on_hann = results[(1000.0, "Hann")]
off_rect = results[(1012.5, "none")]
off_hann = results[(1012.5, "Hann")]
ok = (on_rect[2] == 1 and on_hann[2] == 3 and off_rect[2] > off_hann[2]
      and off_hann[3] < off_rect[3] - 20
      and abs(refined - 440) < abs(plain - 440))
print()
print("PASS" if ok else "CHECK: the leakage numbers do not match the chapter.")
