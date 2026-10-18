# Chapter 8, Test 02: Read microphone frames and time them
# Reads 40 ms frames (512 samples, 2,048 bytes) for 10 seconds and prints, once
# per second: frames per second, how long readinto() waited for the frame,
# how long the Python loudness calculation took, the loudness, and the
# microphone's DC offset. Needs the INMP441 microphone.
#
# PASS: about 25.0 frames per second. "wait" plus "work" adds up to about 40 ms:
# the more your code works, the less readinto() waits. WRITE DOWN the "work"
# number: it is how much of the 40 ms budget a plain-Python loudness
# calculation uses, and it is the number Chapter 10 tries to shrink.

NAME = "02-mic-frame-reader.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time

import config

FRAME_SAMPLES = 512
FRAME_BYTES = FRAME_SAMPLES * 4
RUN_SECONDS = 10
LOG2 = math.log(2)


def analyze(buf):
    """Returns (loudness in bits, DC offset, first sample)."""
    samples = [s >> config.MIC_SAMPLE_SHIFT for s in struct.unpack("<512i", buf)]
    middle = sum(samples) // FRAME_SAMPLES
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2, middle, samples[0]


buf = bytearray(FRAME_BYTES)
mic = config.init_microphone()
frame_us = FRAME_SAMPLES * 1_000_000 // config.MIC_SAMPLE_RATE
print("Frame = {} samples = {} us.".format(FRAME_SAMPLES, frame_us))
try:
    for _ in range(8):                       # the microphone's start-up
        mic.readinto(buf)
    print()
    print("{:>3} {:>7} {:>9} {:>9} {:>7} {:>9}".format(
        "sec", "frames", "wait ms", "work ms", "bits", "DC offset"))
    second = 0
    frames = 0
    wait_us = work_us = 0
    last_bits = last_dc = 0
    started = time.ticks_us()
    window = started
    overruns = 0
    while second < RUN_SECONDS:
        t0 = time.ticks_us()
        mic.readinto(buf)
        t1 = time.ticks_us()
        last_bits, last_dc, _ = analyze(buf)
        t2 = time.ticks_us()
        wait_us += time.ticks_diff(t1, t0)
        work_us += time.ticks_diff(t2, t1)
        if time.ticks_diff(t2, t0) > frame_us:
            overruns += 1
        frames += 1
        if time.ticks_diff(t2, window) >= 1_000_000:
            second += 1
            print("{:>3} {:>7} {:>9.1f} {:>9.1f} {:>7.1f} {:>9}".format(
                second, frames, wait_us / frames / 1000, work_us / frames / 1000,
                last_bits, last_dc))
            frames = 0
            wait_us = work_us = 0
            window = t2
    print()
    print("passes longer than one frame (overruns): {}".format(overruns))
finally:
    mic.deinit()
print("Done.")
