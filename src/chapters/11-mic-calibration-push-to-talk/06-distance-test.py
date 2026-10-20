# Chapter 11, Test 06: The microphone distance effect
# Measures your speech level at three distances and compares it with a simple
# model: every time the distance doubles, the level drops by 1 bit (6.02 dB).
# For each distance it asks you to speak for 3 seconds; you set the distances in
# DISTANCES_CM and use a ruler. It measures the room noise once at the start.
# Needs the INMP441 microphone only.
#
# The 1-bit-per-doubling rule is a MODEL (sound from a small source spreads out,
# so it gets weaker with distance). A real room adds echoes and background noise,
# so your numbers will not match it exactly. How far they miss is the result.
#
# PASS: a table with one row per distance: the measured speech level, what the
# model predicted from the first row, the difference, and the SNR. The level
# should fall as the distance grows, and the SNR should fall with it.
# WRITE DOWN the whole table, and the room you did it in.

NAME = "06-distance-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math

import config
import levels

DISTANCES_CM = (10, 20, 40)   # EDIT: three distances, nearest first
QUIET_FRAMES = 75             # 3 seconds
SPEECH_FRAMES = 75            # 3 seconds per distance
SETTLE_FRAMES = 8
PAUSE_FRAMES = 75             # 3 seconds to move before each speech step

frame = bytearray(levels.FRAME_BYTES)
mic = config.init_microphone()
rows = []
try:
    for _ in range(SETTLE_FRAMES):
        mic.readinto(frame)
    print("Stay QUIET for 3 seconds (measuring the room)...")
    quiet = []
    for _ in range(QUIET_FRAMES):
        mic.readinto(frame)
        quiet.append(levels.frame_stats(frame)[0])
    floor = levels.percentile(quiet, 50)
    print("Noise floor {:.2f} bits.".format(floor))

    for distance in DISTANCES_CM:
        print()
        print("Get your mouth {} cm from the microphone. Starting in 3 seconds...".format(distance))
        for _ in range(PAUSE_FRAMES):
            mic.readinto(frame)                 # keep reading so the buffer never fills
        print("SPEAK for 3 seconds: 'Hey Pico, what is due tomorrow?'")
        speech = []
        clipped_frames = 0
        for _ in range(SPEECH_FRAMES):
            mic.readinto(frame)
            bits, dc, dev_peak, clipped = levels.frame_stats(frame)
            speech.append(bits)
            if clipped >= levels.CLIP_MIN_SAMPLES:
                clipped_frames += 1
        rows.append((distance, levels.percentile(speech, 90), clipped_frames))
finally:
    mic.deinit()

first_distance, first_level, _ = rows[0]
print()
print("Noise floor: {:.2f} bits.  Model: level = {:.2f} - log2(distance / {}).".format(
    floor, first_level, first_distance))
print()
print("{:>9} {:>9} {:>9} {:>8} {:>7} {:>9} {:>8}".format(
    "distance", "measured", "model", "miss", "SNR", "SNR dB", "clipped"))
for distance, level, clipped_frames in rows:
    model = first_level - math.log(distance / first_distance) / levels.LOG2
    print("{:>6} cm {:>9.2f} {:>9.2f} {:>+8.2f} {:>7.2f} {:>9.1f} {:>8}".format(
        distance, level, model, level - model, level - floor,
        levels.snr_db(level, floor), clipped_frames))
print()
print("'miss' is measured minus model, in bits. Positive: louder than the model says.")
print("PASS if the level falls as the distance grows (the model is only a guide).")
