# Chapter 3, Test 04: Bit depth and quantization error
# Rounds one cycle of a sine wave to 2^n levels for several bit depths and
# prints the number of levels, the step size, and the worst rounding error.
# Runs on the Pico or on your computer. Needs no hardware.
#
# PASS: levels double with each added bit (4, 16, 256, 4096, 65536), and the
# worst error halves each time a bit is added.

NAME = "04-bit-depth-quantizer.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math

POINTS = 256


def quantize(x, bits):
    """Round x (between -1 and +1) to the nearest of 2**bits evenly spaced levels."""
    levels = 2 ** bits
    step = 2 / (levels - 1)
    index = int((x + 1) / step + 0.5)
    return -1 + index * step


print()
print("{:>5} {:>9} {:>12} {:>14}".format("bits", "levels", "step", "worst error"))
previous = None
ok = True
for bits in (2, 4, 8, 12, 16):
    worst = 0.0
    for i in range(POINTS):
        x = math.sin(2 * math.pi * i / POINTS)
        worst = max(worst, abs(quantize(x, bits) - x))
    levels = 2 ** bits
    print("{:>5} {:>9} {:>12.6f} {:>14.6f}".format(bits, levels, 2 / (levels - 1), worst))
    if previous is not None and not worst < previous:
        ok = False
    previous = worst

print()
print("Each extra bit doubles the levels and adds about 6.02 dB of range:")
for bits in (8, 12, 16, 24):
    print("  {:>2} bits -> {:>14} levels, about {:.1f} dB".format(
        bits, "{:,}".format(2 ** bits), 6.02 * bits))
print()
print("PASS" if ok else "FAIL: the error did not shrink as bits were added")
