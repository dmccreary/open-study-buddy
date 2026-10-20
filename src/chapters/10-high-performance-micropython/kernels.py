# kernels.py -- the same small job in four speeds (Chapter 10)
#
# THE JOB: window a frame of 16-bit samples with a Q15 window.
#     out[i] = (x[i] * w[i]) >> 15
# x holds signed 16-bit samples, w holds the window in Q15 (0 .. 32767 means
# 0.0 .. 0.99997), and out gets the windowed samples.
#
# THE WAYS HERE
#   window_py     plain Python. Works on lists or on array('h').
#   window_viper  @micropython.viper: integers in machine registers, pointers
#                 into the arrays, no objects, no allocation.
#
# The assembly versions (window_asm, sum16_asm) live in kernels_asm.py, so that
# if your Pico's assembler rejects a line, this file and everything that uses
# it still import.
#
# ALSO HERE: sum16_py / sum16_viper, the smallest possible loop (add up an
# int16 array); sum16_asm in kernels_asm.py is the same loop in assembly.
#
# THE TWO GOTCHAS (both are in the chapter)
#   1. viper's ptr16 reads are UNSIGNED. A stored -1 reads back as 65535, so a
#      signed sample has to be sign-extended by hand (see window_viper).
#   2. viper and asm do no bounds checking. n bigger than the array corrupts
#      memory, and the asm loops run once even for n = 0. Always pass n > 0
#      and n <= len(array).
#
# Needs a MicroPython board (viper is not available on a computer's CPython).

import micropython
from array import array


def window_py(x, w, out, n):
    for i in range(n):
        out[i] = (x[i] * w[i]) >> 15


@micropython.viper
def window_viper(x: ptr16, w: ptr16, out: ptr16, n: int):
    i = 0
    while i < n:
        s = int(x[i])
        if s >= 32768:            # ptr16 reads are unsigned: sign-extend by hand
            s -= 65536
        out[i] = (s * int(w[i])) >> 15
        i += 1


def sum16_py(x, n):
    total = 0
    for i in range(n):
        total += x[i]
    return total


@micropython.viper
def sum16_viper(x: ptr16, n: int) -> int:
    total = 0
    i = 0
    while i < n:
        s = int(x[i])
        if s >= 32768:
            s -= 65536
        total += s
        i += 1
    return total


def q15_table(values):
    """Make an array('h') of Q15 numbers from floats between -1 and 1."""
    table = array("h", [0] * len(values))
    for i in range(len(values)):
        v = int(values[i] * 32768)
        table[i] = 32767 if v > 32767 else (-32768 if v < -32768 else v)
    return table
