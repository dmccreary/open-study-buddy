# Chapter 9, Test 02: The FFT agrees with the DFT, and does far less work
# Checks dsp.fft() against dsp.naive_dft() on 64 random numbers, then prints
# how many multiplications each method needs for several sizes. Runs on the
# Pico or on your computer (python3 02-fft-vs-dft.py). Needs no hardware.
# It does not time anything: how fast the FFT runs on the Pico is the subject
# of Chapter 10.
#
# PASS: the two methods agree to better than 0.0001, the 512-point row shows
# 262,144 versus 2,304 butterflies, and the last line says PASS.

NAME = "02-fft-vs-dft.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import random

import dsp

N = 64
tables = dsp.make_tables(N)
random.seed(1)
x = [random.random() * 2 - 1 for _ in range(N)]

re = list(x)
im = [0.0] * N
dsp.fft(re, im, tables)
slow_re, slow_im = dsp.naive_dft(x)

worst = 0.0
for k in range(N):
    worst = max(worst, abs(re[k] - slow_re[k]), abs(im[k] - slow_im[k]))
print()
print("Largest difference between fft() and naive_dft() over {} bins: {:.2e}".format(N, worst))
ok = worst < 1e-4

print()
print("{:>6} {:>14} {:>22} {:>10}".format("N", "DFT: N x N", "FFT: N/2 x log2(N)", "ratio"))
for size in (8, 64, 256, 512, 1024):
    stages = int(round(math.log(size) / math.log(2)))
    dft_ops = size * size
    fft_ops = size // 2 * stages
    print("{:>6,} {:>14,} {:>22,} {:>9.1f}x".format(size, dft_ops, fft_ops, dft_ops / fft_ops))
    if size == 512:
        ok = ok and dft_ops == 262144 and fft_ops == 2304

print()
print("Each FFT 'operation' above is one butterfly (4 multiplications and 6 additions);")
print("each DFT 'operation' is one multiply-add of a sample by a cosine and a sine.")
print("The two are not the same size, so read the ratio as 'about 100 times less work'.")
print()
print("PASS" if ok else "CHECK: fft() and naive_dft() disagree, or a count is wrong.")
