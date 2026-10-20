# Chapter 11, Test 02: Measure the noise floor
# Listens to a quiet room for 100 frames (4 seconds), then prints how loud the
# "silence" really is: the lowest, median, mean, 90th and 95th percentile, and
# highest frame, in bits. It also prints one line per second so you can see the
# readings wander. Needs the INMP441 microphone only.
#
# Stay quiet and still while it runs. Do not type on a keyboard next to it.
#
# PASS: it prints the table and a "noise floor" (the median) and a "noise
# ceiling" (the 95th percentile). In a quiet room expect the floor near 12.5 to
# 13.1 bits (the two kit boards measured 12.5 and 13.1) and the ceiling less
# than 1.5 bits above the floor. WRITE DOWN your floor and ceiling.
#
# Try the same run again while someone claps once: the highest reading jumps by
# several bits, the median hardly moves. That is why the chapter uses the
# median for the floor and the 95th percentile for the ceiling.

NAME = "02-noise-floor.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import config
import levels

FRAMES = 100                  # 4 seconds
SETTLE_FRAMES = 8             # throw away the microphone's start-up, as kit test 06 does

frame = bytearray(levels.FRAME_BYTES)
mic = config.init_microphone()
readings = []
offsets = []
try:
    print("Stay quiet for {} seconds...".format(FRAMES * levels.FRAME_MS // 1000))
    for _ in range(SETTLE_FRAMES):
        mic.readinto(frame)
    print()
    print("{:>4} {:>7} {:>7} {:>7} {:>10}".format("sec", "min", "mean", "max", "DC offset"))
    for n in range(FRAMES):
        mic.readinto(frame)
        bits, dc, dev_peak, clipped = levels.frame_stats(frame)
        readings.append(bits)
        offsets.append(dc)
        if (n + 1) % 25 == 0:                       # one line per second
            second = readings[-25:]
            print("{:>4} {:>7.2f} {:>7.2f} {:>7.2f} {:>10}".format(
                (n + 1) // 25, min(second), sum(second) / 25, max(second), dc))
finally:
    mic.deinit()

print()
print("Over all {} frames, in bits (and as a multiple of the median):".format(len(readings)))
floor = levels.percentile(readings, 50)
for label, value in (("lowest", min(readings)),
                     ("median", floor),
                     ("mean", sum(readings) / len(readings)),
                     ("90th percentile", levels.percentile(readings, 90)),
                     ("95th percentile", levels.percentile(readings, 95)),
                     ("highest", max(readings))):
    print("  {:<16} {:6.2f} bits   {:5.2f}x   {:6.1f} dB re full scale".format(
        label, value, 2 ** (value - floor), levels.bits_to_db(value)))

ceiling = levels.percentile(readings, 95)
print()
print("Noise floor   (median)          {:.2f} bits".format(floor))
print("Noise ceiling (95th percentile) {:.2f} bits".format(ceiling))
print("Spread (ceiling - floor)        {:.2f} bits".format(ceiling - floor))
print("DC offset ranged from {} to {}".format(min(offsets), max(offsets)))
if ceiling - floor > levels.MAX_NOISE_SPREAD:
    print("CHECK: the spread is over {} bits. Something made noise; run again.".format(
        levels.MAX_NOISE_SPREAD))
else:
    print("PASS: a steady room. Use these numbers in 04-calibrate.py.")
