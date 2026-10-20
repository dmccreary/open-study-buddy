# Chapter 9, Test 03: Bins, bin width, and band edges for the kit
# Prints the kit's bin arithmetic (12,800 Hz, 512 samples), a table of
# frequencies and the bins they land in, and the 16 log-spaced bands the
# spectrum display uses. Runs on the Pico or on your computer
# (python3 03-bin-calculator.py). Needs no hardware, but it does import the
# kit's constants from config.py if it can find one; otherwise it uses the
# same numbers directly.
#
# PASS: bin width 25 Hz, 256 useful bins, top frequency 6,400 Hz; 1,000 Hz is
# bin 40.0; 440 Hz is bin 17.6; the 16 bands cover bins 4 to 255 with no gaps.

NAME = "03-bin-calculator.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import dsp

try:
    import config
    RATE = config.MIC_SAMPLE_RATE
    N = config.FFT_SIZE
except ImportError:                       # running on a computer without the kit files
    RATE = 12800
    N = 512

BINS = N // 2
WIDTH = RATE / N
print()
print("sample rate      {:,} Hz".format(RATE))
print("FFT size         {} samples = {:.0f} ms of sound".format(N, N * 1000 / RATE))
print("bin width        {} / {} = {} Hz".format(RATE, N, WIDTH))
print("useful bins      {} / 2 = {}  (bin 0 is DC; bin {} is {:.0f} Hz)".format(
    N, BINS, BINS, dsp.freq_of(BINS, RATE, N)))
print("highest bin      {} = {:.0f} Hz;  the top of the range is {} Hz (Nyquist)".format(
    BINS - 1, dsp.freq_of(BINS - 1, RATE, N), RATE // 2))

print()
print("{:>8} {:>9} {:>10} {:>12}".format("tone Hz", "bin", "nearest", "off by (Hz)"))
for freq in (100, 440, 1000, 1012.5, 2000, 3500, 6375):
    exact = dsp.bin_of(freq, RATE, N)
    nearest = int(exact + 0.5)
    print("{:>8} {:>9.2f} {:>10} {:>+12.1f}".format(
        freq, exact, nearest, freq - dsp.freq_of(nearest, RATE, N)))

print()
print("Other frame sizes at the same sample rate:")
print("{:>6} {:>10} {:>11} {:>11}".format("size", "bin width", "frame ms", "useful bins"))
for size in (128, 256, 512, 1024):
    print("{:>6} {:>8.1f} Hz {:>8.0f} ms {:>11}".format(
        size, RATE / size, size * 1000 / RATE, size // 2))

BANDS = 16
F_LOW = 100
F_HIGH = RATE // 2
edges = dsp.log_band_edges(BANDS, F_LOW, F_HIGH, RATE, N)
print()
print("{} log-spaced bands from {} Hz to {} Hz (ratio {:.4f} per band)".format(
    BANDS, F_LOW, F_HIGH, (F_HIGH / F_LOW) ** (1 / BANDS)))
print("{:>4} {:>12} {:>14} {:>5}".format("band", "bins", "Hz", "count"))
for i in range(BANDS):
    low, high = edges[i], edges[i + 1]
    print("{:>4} {:>5} - {:<5} {:>6.0f}-{:<7.0f} {:>5}".format(
        i, low, high - 1, dsp.freq_of(low, RATE, N), dsp.freq_of(high, RATE, N), high - low))

ok = (WIDTH == 25 and BINS == 256 and RATE // 2 == 6400
      and dsp.bin_of(1000, RATE, N) == 40 and abs(dsp.bin_of(440, RATE, N) - 17.6) < 1e-9
      and edges[0] == 4 and edges[-1] == 256
      and all(edges[i + 1] > edges[i] for i in range(BANDS)))
print()
print("PASS" if ok else "CHECK: a number does not match the chapter.")
