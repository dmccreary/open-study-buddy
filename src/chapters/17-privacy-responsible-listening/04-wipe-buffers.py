# Chapter 17, Test 04: Wipe the audio buffer when you are done with it
# "Audio not stored" starts on the device. A recording sits in RAM until
# something overwrites it. wipe() overwrites it with zeros, one small chunk at
# a time (no big temporary allocation), and checks that the result is all zero.
# Runs on the Pico or on a computer; needs no other parts.
#
# PASS: the buffer holds a nonzero pattern before, all zeros after, and the last
# line says PASS. On the Pico, WRITE DOWN the "wipe ms" for the 150 KB buffer:
# the chapter does not claim a number.

NAME = "04-wipe-buffers.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

CHUNK = 1024
ZEROS = bytes(CHUNK)


def wipe(buf):
    """Overwrite every byte of buf with 0, without allocating a big copy."""
    view = memoryview(buf)
    n = len(buf)
    i = 0
    while i + CHUNK <= n:
        view[i:i + CHUNK] = ZEROS
        i += CHUNK
    if i < n:
        view[i:n] = bytes(n - i)


def all_zero(buf):
    return not any(buf)


SIZE = 3 * 12800 * 4                      # the 3 s recording buffer of test 07
raw = bytearray(SIZE)
for i in range(0, SIZE, 997):             # a fake "voice": a nonzero pattern
    raw[i] = (i // 997) % 250 + 1
print("before: {} bytes, all zero? {}".format(SIZE, all_zero(raw)))

try:
    start = time.ticks_us()
    wipe(raw)
    ms = time.ticks_diff(time.ticks_us(), start) / 1000
except AttributeError:                    # CPython has no ticks_us
    wipe(raw)
    ms = None
print("after : all zero? {}".format(all_zero(raw)))
if ms is not None:
    print("wipe ms: {:.1f}".format(ms))
odd = bytearray(b"abc" * 700 + b"x")      # a length that is not a multiple of 1024
wipe(odd)
print("odd length ok? {}".format(all_zero(odd)))
print("PASS" if all_zero(raw) and all_zero(odd) else "FAIL")
