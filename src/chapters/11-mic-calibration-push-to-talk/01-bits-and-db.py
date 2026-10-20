# Chapter 11, Test 01: Bits, decibels, and signal-to-noise ratio
# Checks the arithmetic the whole chapter rests on, with no hardware:
#   * 1 bit of loudness is a doubling, which is 6.02 dB
#   * the "bits" meter is a mean-absolute-distance measure, not RMS, so bits
#     and dB agree to about 1 dB, not exactly
#   * signal-to-noise ratio is a subtraction in bits, times 6.02 for dB
# It runs on your computer (python3 01-bits-and-db.py) and on the Pico.
#
# PASS: the last line says PASS. Every number comes from SYNTHETIC frames
# (synth.py, fixed seed), not from a microphone.

NAME = "01-bits-and-db.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math

import levels
import synth

ok = True


def check(label, good):
    global ok
    ok = ok and good
    print("  {:<58} {}".format(label, "ok" if good else "FAIL"))


# ---------------------------------------------------------------------------
print()
print("1. One bit is a doubling, and a doubling is 6.02 dB")
print()
print("{:>10} {:>14} {:>10}".format("bits more", "times bigger", "dB more"))
for bits_more in (1, 2, 3, 4, 6, 8):
    ratio = 2 ** bits_more
    db = 20 * math.log10(ratio)
    print("{:>10} {:>14} {:>10.2f}".format(bits_more, ratio, db))
print()
check("20 * log10(2) is 6.0206 (to 4 places)", abs(levels.DB_PER_BIT - 6.0206) < 0.00005)

# ---------------------------------------------------------------------------
print()
print("2. A frame twice as big reads exactly one bit higher")
rng = synth.Rng(1)
quiet = synth.noise_frame(rng, 13.0)
loud = synth.noise_frame(synth.Rng(1), 14.0)       # same random numbers, doubled
bits_quiet = levels.frame_stats(quiet)[0]
bits_loud = levels.frame_stats(loud)[0]
print("  quiet frame {:.3f} bits, doubled frame {:.3f} bits, difference {:.3f}".format(
    bits_quiet, bits_loud, bits_loud - bits_quiet))
check("difference is 1.00 bit (within 0.01)", abs(bits_loud - bits_quiet - 1.0) < 0.01)

# ---------------------------------------------------------------------------
print()
print("3. Bits measure the mean distance, not RMS: how far apart can they be?")
n = 4000
rng = synth.Rng(7)
noise = [rng.gauss() for _ in range(n)]
sine = [math.sin(2 * math.pi * i / 64) for i in range(n)]


def mad(x):
    middle = sum(x) / len(x)
    return sum([abs(v - middle) for v in x]) / len(x)


def rms(x):
    middle = sum(x) / len(x)
    return math.sqrt(sum([(v - middle) ** 2 for v in x]) / len(x))


print("  Gaussian noise: mean distance / RMS = {:.4f}".format(mad(noise) / rms(noise)))
print("  Sine wave:      mean distance / RMS = {:.4f}".format(mad(sine) / rms(sine)))
gap_db = 20 * math.log10((mad(sine) / rms(sine)) / (mad(noise) / rms(noise)))
print("  A tone and noise with the SAME RMS differ by {:.2f} dB on the bits scale.".format(gap_db))
check("that gap is under 1.2 dB", abs(gap_db) < 1.2)

# ---------------------------------------------------------------------------
print()
print("4. Signal-to-noise ratio from synthetic frames")
rng = synth.Rng(3)
floor_readings = [levels.frame_stats(synth.noise_frame(rng, 13.0 + 0.1 * rng.gauss()))[0]
                  for _ in range(40)]
speech_readings = [levels.frame_stats(synth.speech_frame(rng, 17.0, phase=i * 512))[0]
                   for i in range(40)]
floor = levels.percentile(floor_readings, 50)
level = levels.percentile(speech_readings, 90)
print("  noise floor (median of 40 frames)   {:6.2f} bits  ({:6.1f} dB re full scale)".format(
    floor, levels.bits_to_db(floor)))
print("  speech level (90th percentile)      {:6.2f} bits  ({:6.1f} dB re full scale)".format(
    level, levels.bits_to_db(level)))
print("  SNR = {:.2f} bits = {:.1f} dB".format(
    levels.snr_bits(level, floor), levels.snr_db(level, floor)))
check("SNR in dB is 6.0206 times SNR in bits",
      abs(levels.snr_db(level, floor) - 6.0206 * levels.snr_bits(level, floor)) < 1e-6)
check("the synthetic speech (17.0 bits) reads 4.0 bits above the floor, +/- 0.3",
      abs(levels.snr_bits(level, floor) - 4.0) < 0.3)

print()
print("PASS" if ok else "FAIL")
