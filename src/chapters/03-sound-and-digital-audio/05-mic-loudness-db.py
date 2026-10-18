# Chapter 3, Test 05: Microphone loudness in bits and decibels
# Calibrates the room's noise floor for one second, then prints the loudness of
# every fifth frame for 20 seconds as "bits" (log base 2, the unit kit test 06
# uses), as decibels relative to full scale, and as a multiple of the floor.
# Needs the INMP441 microphone.
#
# PASS: in a quiet room the floor is about 12 to 13 bits (the README measured
# 12.5), about -63 dB below full scale. Speaking raises the reading by several
# bits. Each +1 bit should be about +6 dB and 2x the floor.
#
# Write down your floor: Chapter 11 sets thresholds from it.

NAME = "05-mic-loudness-db.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time

import config

FRAME_SAMPLES = 512
FRAME_FORMAT = "<512i"
FULL_SCALE = 2 ** 23              # biggest 24-bit sample
LOG2 = math.log(2)
RUN_SECONDS = 20


def loudness(buf):
    """Returns (bits, average) for one frame."""
    samples = [s >> config.MIC_SAMPLE_SHIFT for s in struct.unpack(FRAME_FORMAT, buf)]
    middle = sum(samples) // FRAME_SAMPLES
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2, average


buf = bytearray(FRAME_SAMPLES * 4)
mic = config.init_microphone()
try:
    for _ in range(8):                      # skip the microphone's start-up
        mic.readinto(buf)
    print("Calibrating for 1 second: stay quiet.")
    total = 0
    for _ in range(25):
        mic.readinto(buf)
        total += loudness(buf)[0]
    floor = total / 25
    floor_db = 20 * math.log10(2 ** floor / FULL_SCALE)
    print("Noise floor: {:.1f} bits = {:.1f} dB below full scale".format(floor, -floor_db))
    print()
    print("{:>5} {:>7} {:>9} {:>11}".format("sec", "bits", "dBFS", "x floor"))

    start = time.ticks_ms()
    frame = 0
    while time.ticks_diff(time.ticks_ms(), start) < RUN_SECONDS * 1000:
        mic.readinto(buf)
        bits, average = loudness(buf)
        frame += 1
        if frame % 5 == 0:
            seconds = time.ticks_diff(time.ticks_ms(), start) / 1000
            db = 20 * math.log10(max(average, 1) / FULL_SCALE)
            print("{:5.1f} {:7.1f} {:9.1f} {:11.1f}".format(
                seconds, bits, db, 2 ** (bits - floor)))
finally:
    mic.deinit()
print("Done.")
