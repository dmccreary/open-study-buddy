# Chapter 18, Probe 03: Microphone
# Reads 40 ms frames for about 5 seconds and prints, once per second, the
# spread (highest minus lowest sample), the DC offset, the loudness in bits,
# and how many samples sit at full scale. Clap once near the end.
# Needs only the microphone (the display is optional and unused).
#
# What the numbers tell you:
#   spread 0                  a flat line: the microphone is not sending audio
#   loudness barely moves     L/R on 3V3, or the mute switch is on (Chapter 17)
#   samples at full scale     too loud, or the SD wire is picking up noise
#   DC offset a big number    normal; it wanders (Chapter 8). The loudness
#                             code subtracts it.
#
# PASS: the verdict line says PASS, the spread is above 0, and the loudness
# jumps by several bits when you clap.

NAME = "03-mic-probe.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import checks
import config

verdict, detail, stats = checks.check_mic(config, frames=125)   # 125 frames = 5 s
print()
print("{:>3} {:>10} {:>10} {:>7} {:>8}".format("sec", "spread", "DC offset", "bits", "clipped"))
for second in range(len(stats) // 25):
    chunk = stats[second * 25:(second + 1) * 25]
    print("{:>3} {:>10,} {:>10,} {:>7.1f} {:>8}".format(
        second + 1,
        max(s["max"] for s in chunk) - min(s["min"] for s in chunk),
        sum(s["dc"] for s in chunk) // len(chunk),
        sum(s["bits"] for s in chunk) / len(chunk),
        sum(s["clipped"] for s in chunk)))
if stats:
    bits = sorted(s["bits"] for s in stats)
    median, loudest = bits[len(bits) // 2], bits[-1]
    print()
    print("median frame {:.1f} bits; loudest frame {:.1f} bits; difference {:.1f} bits".format(
        median, loudest, loudest - median))
print()
print("RESULT:", verdict, "-", detail)
