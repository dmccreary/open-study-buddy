# Chapter 12, Test 02: The band table and the memory it costs
# Prints the 16 log-spaced bands the detector uses (bins and Hz), and the
# memory arithmetic for the feature extractor, the rolling window, and the
# template. On the Pico it also reports the heap the objects actually took.
# No hardware needed. It also runs on a computer.
#
# PASS: 16 bands covering bins 4 to 255 (100 to 6,400 Hz), a window of 25 frames
# = 1.00 s, and a memory table that adds up. On the Pico the "measured" line is
# in the same range as the arithmetic.

NAME = "02-band-table.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc

import detector
import features
import levels

BIN_HZ = levels.RATE / levels.FRAME_SAMPLES
edges = features.EDGES
ok = True

print()
print("{:>4} {:>11} {:>16} {:>6}".format("band", "bins", "frequencies (Hz)", "width"))
for i in range(features.BANDS):
    lo, hi = edges[i], edges[i + 1]
    print("{:>4} {:>5} to {:<3} {:>7.0f} to {:<6.0f} {:>4}".format(
        i, lo, hi - 1, lo * BIN_HZ, hi * BIN_HZ, hi - lo))
ok = ok and edges[0] == 4 and edges[-1] == 256 and len(edges) == 17
print()
print("Bin width {:.0f} Hz.  The window is {} frames x {} ms = {:.2f} s.".format(
    BIN_HZ, detector.K, levels.FRAME_MS, detector.K * levels.FRAME_MS / 1000))

B, K = features.BANDS, detector.K
rows = (
    ("one frame's features", B * 4, "16 floats"),
    ("rolling window ring", K * B * 4, "25 frames x 16 floats"),
    ("template", K * B * 4, "25 x 16 floats"),
    ("window's running sums", 2 * B * 4 + K, "2 x 16 floats + 25 flags"),
    ("extractor: re and im", 2 * features.N * 4, "2 x 512 floats"),
    ("extractor: power", features.HALF * 4, "256 floats"),
    ("extractor: Hann window", features.N * 4, "512 floats"),
    ("extractor: bit-reversal table", features.N * 2, "512 x 2 bytes"),
    ("extractor: cos and sin tables", 2 * features.HALF * 4, "2 x 256 floats"),
)
print()
print("{:<32} {:>8}   {}".format("what", "bytes", "made of"))
total = 0
for name, size, made_of in rows:
    total += size
    print("{:<32} {:>8}   {}".format(name, size, made_of))
print("{:<32} {:>8}".format("total", total))

if hasattr(gc, "mem_alloc"):
    gc.collect()
    before = gc.mem_alloc()
    extractor = features.Extractor()
    window = detector.Window()
    template = detector.array("f", [0.0] * (K * B))
    gc.collect()
    used = gc.mem_alloc() - before
    print()
    print("Measured on this board: the three objects took {} bytes of heap "
          "(arithmetic above: {}).".format(used, total - B * 4))
    print("Free heap now: {} bytes.".format(gc.mem_free()))

print()
print("PASS" if ok else "CHECK: the band table is not what the chapter shows")
