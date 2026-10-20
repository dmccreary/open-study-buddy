# Chapter 9, Test 07: A live spectrum on the round screen
# Reads microphone frames, runs the pure-Python pipeline (DC removal, Hann
# window, FFT, magnitudes, band energies), and draws 16 log-spaced bars. Each
# bar is redrawn by changed slice only (the Chapter 6 idea). The peak
# frequency is printed under the bars. Needs the display and the microphone.
#
# The pure-Python FFT is expected to take longer than one 40 ms frame, so the
# loop uses dsp.latest_frame() to skip stale frames. Watch the serial
# summary: "work ms" and "skipped" are the numbers Chapter 10 improves.
#
# PASS: whistle a steady note and one bar (and its neighbors) rises while the
# others stay low; sweep the whistle upward and the tall bar moves right.
# The peak frequency under the bars follows the note to within about 25 Hz.

NAME = "07-spectrum-display.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from array import array

import config
import dsp

N = config.FFT_SIZE
RATE = config.MIC_SAMPLE_RATE
FRAME_US = N * 1_000_000 // RATE
BANDS = 16
ANALYSES = 150
PEAK_GATE_DBFS = -50              # below this a "peak" is just noise (tune for your room)
DB_FLOOR = -90                    # empty bar (tune for your room)
DB_CEIL = -30                     # full bar

BAR_WIDTH = 12
BAR_GAP = 3
BAR_HEIGHT = 120
BARS_X = config.CENTER_X - (BANDS * (BAR_WIDTH + BAR_GAP) - BAR_GAP) // 2     # 61
BASELINE = 250                    # the bottom edge of every bar
DIM = config.color565(150, 150, 150)

tables = dsp.make_tables(N)
window = dsp.hann_table(N)
re = array("f", [0.0] * N)
im = array("f", [0.0] * N)
mag = array("f", [0.0] * (N // 2))
energy = array("f", [0.0] * BANDS)
edges = dsp.log_band_edges(BANDS, 100, RATE // 2, RATE, N)
reference = dsp.dbfs_reference(N)
shown = [0] * BANDS               # the bar heights currently on the glass
colors = [config.color565(40 + 13 * i, 220 - 8 * i, 255 - 10 * i) for i in range(BANDS)]

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "Spectrum", 60, config.YELLOW)
config.centered_text(display, config.SMALL_FONT, "16 bands, 100 Hz to 6.4 kHz", 100, DIM)
display.hline(BARS_X - 3, BASELINE + 1, BANDS * (BAR_WIDTH + BAR_GAP) + 3, DIM)
display.text(config.SMALL_FONT, "100", BARS_X, BASELINE + 6, DIM, config.BLACK)
display.text(config.SMALL_FONT, "800", BARS_X + 8 * (BAR_WIDTH + BAR_GAP), BASELINE + 6, DIM, config.BLACK)
display.text(config.SMALL_FONT, "6.4k", BARS_X + BANDS * (BAR_WIDTH + BAR_GAP) - BAR_GAP - 32,
             BASELINE + 6, DIM, config.BLACK)


def draw_bar(i, height):
    """Paint only the slice of bar i that changed."""
    old = shown[i]
    if height == old:
        return
    x = BARS_X + i * (BAR_WIDTH + BAR_GAP)
    if height > old:
        display.fill_rect(x, BASELINE - height, BAR_WIDTH, height - old, colors[i])
    else:
        display.fill_rect(x, BASELINE - old, BAR_WIDTH, old - height, config.BLACK)
    shown[i] = height


mic = config.init_microphone()
buf = bytearray(N * 4)
try:
    for _ in range(8):
        mic.readinto(buf)
    shown_peak = None
    work_total = 0
    worst = 0
    skipped_total = 0
    for n in range(ANALYSES):
        skipped_total += dsp.latest_frame(mic, buf)
        started = time.ticks_us()
        dc, rms = dsp.load_frame(buf, re, im, window, config.MIC_SAMPLE_SHIFT)
        dsp.fft(re, im, tables)
        dsp.magnitudes(re, im, mag)
        dsp.band_energies(mag, edges, energy)
        for i in range(BANDS):
            level = dsp.to_db(energy[i], reference * reference, power=True)
            draw_bar(i, dsp.scale(level, DB_FLOOR, DB_CEIL, BAR_HEIGHT))
        dbfs = dsp.to_db(rms, 1 << (config.MIC_SAMPLE_BITS - config.MIC_SAMPLE_SHIFT - 1))
        if dbfs > PEAK_GATE_DBFS:
            text = "{:.0f} Hz".format(dsp.peak_frequency(mag, RATE, N)[0])
        else:
            text = "quiet"
        if text != shown_peak:
            config.centered_text(display, config.SMALL_FONT, text.center(14), 285, config.WHITE)
            shown_peak = text
        used = time.ticks_diff(time.ticks_us(), started)
        work_total += used
        worst = max(worst, used)
        if n % 10 == 0:
            print("{:>4} {:>7.1f} dBFS  {:>9}  work {:>6.1f} ms".format(n, dbfs, text, used / 1000))
    print()
    print("work per analyzed frame: mean {:.1f} ms, worst {:.1f} ms (budget {} ms)".format(
        work_total / ANALYSES / 1000, worst / 1000, FRAME_US // 1000))
    print("frames skipped to stay current: {} of {}".format(
        skipped_total, skipped_total + ANALYSES))
finally:
    mic.deinit()
print("Done.")
