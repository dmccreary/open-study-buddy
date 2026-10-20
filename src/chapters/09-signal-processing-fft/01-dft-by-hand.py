# Chapter 9, Test 01: The DFT by hand
# Computes the DFT of the chapter's four-number example [0, 1, 0, -1] one
# output at a time, showing every term, then does a second example with two
# tones added together. Runs on the Pico or on your computer
# (python3 01-dft-by-hand.py). Needs no hardware.
#
# PASS: the first example gives X = [0, -2j, 0, +2j] (magnitudes 0, 2, 0, 2),
# the second shows energy in exactly the bins the tones were put in, and the
# last line says PASS.

NAME = "01-dft-by-hand.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math


def dft_terms(x, k):
    """The n terms x[t] * (cos - j sin) that add up to X[k], as (re, im) pairs."""
    n = len(x)
    terms = []
    for t in range(n):
        angle = 2 * math.pi * k * t / n
        terms.append((x[t] * math.cos(angle), -x[t] * math.sin(angle)))
    return terms


def clean(value):
    """Round away floating-point dust such as 1.2e-16."""
    return 0.0 if abs(value) < 1e-9 else value


print()
print("Example 1: x = [0, 1, 0, -1]  (one cycle of a sine, 4 samples)")
x = [0, 1, 0, -1]
ok = True
for k in range(4):
    terms = dft_terms(x, k)
    total_re = clean(sum(t[0] for t in terms))
    total_im = clean(sum(t[1] for t in terms))
    print("  X[{}] = {:+.1f} {:+.1f}j     magnitude {:.1f}".format(
        k, total_re, total_im, math.sqrt(total_re ** 2 + total_im ** 2)))
    expected = {0: (0, 0), 1: (0, -2), 2: (0, 0), 3: (0, 2)}[k]
    ok = ok and abs(total_re - expected[0]) < 1e-9 and abs(total_im - expected[1]) < 1e-9
print("  Bins 1 and 3 are mirror images: a real signal's spectrum is symmetric,")
print("  so only the first half of the bins carry new information.")

print()
print("Example 2: 16 samples of (sine at bin 2) + half as much (sine at bin 5)")
n = 16
x = [math.sin(2 * math.pi * 2 * t / n) + 0.5 * math.sin(2 * math.pi * 5 * t / n)
     for t in range(n)]
print("  {:>3} {:>9}   {}".format("bin", "magnitude", "(n/2 times the tone's amplitude)"))
loud = []
for k in range(n // 2 + 1):
    terms = dft_terms(x, k)
    magnitude = math.sqrt(sum(t[0] for t in terms) ** 2 + sum(t[1] for t in terms) ** 2)
    if magnitude > 1e-9:
        loud.append(k)
    print("  {:>3} {:>9.3f}   {}".format(k, magnitude, "#" * int(round(magnitude * 4))))
print("  Bins with energy:", loud)
ok = ok and loud == [2, 5]

print()
print("PASS" if ok else "CHECK: the DFT did not give the expected bins.")
