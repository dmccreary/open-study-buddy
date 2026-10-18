# Chapter 3, Test 01: Hear aliasing
# Plays pure tones through the speaker at a sample rate of 12,800 Hz, whose
# Nyquist limit is 6,400 Hz. Tones below the limit sound like the pitch asked
# for. Tones above it fold down: 7,000 Hz is heard as 12,800 - 7,000 = 5,800 Hz.
# Needs the MAX98357A amplifier and speaker. Keep VOLUME low in config.py.
#
# PASS: you hear steady tones, each higher or lower than the last in the order
# the table prints. The 9,000 Hz tone should sound LOWER than the 7,000 Hz one
# (it folds to 3,800 Hz), which is the proof of aliasing.

NAME = "01-alias-tone.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from machine import I2S, Pin

import config

RATE = 12800
IBUF = 8192
FADE = RATE // 100            # 10 ms fades so tones do not click
NYQUIST = RATE // 2


def apparent(freq):
    """The frequency the samples actually describe."""
    f = freq % RATE
    return f if f <= NYQUIST else RATE - f


def make_tone(freq, ms, volume=config.VOLUME):
    count = RATE * ms // 1000
    amplitude = 32767 * volume / 100
    out = bytearray(count * 2)
    for i in range(count):
        fade = min(1.0, i / FADE, (count - i) / FADE)
        value = int(amplitude * fade * math.sin(2 * math.pi * freq * i / RATE))
        struct.pack_into("<h", out, i * 2, value)
    return out


TONES = (1000, 3000, 6000, 7000, 9000, 11000)

print()
print("Sample rate {} Hz, Nyquist limit {} Hz".format(RATE, NYQUIST))
print("{:>9} {:>9}   {}".format("true Hz", "heard Hz", "note"))
for f in TONES:
    note = "ok" if f < NYQUIST else "ALIASED"
    print("{:>9} {:>9}   {}".format(f, apparent(f), note))

config.set_gain()
audio = I2S(config.I2S_SPEAKER_ID,
            sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
            sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
            format=I2S.MONO, rate=RATE, ibuf=IBUF)
try:
    for f in TONES:
        print("playing {} Hz (should sound like {} Hz)".format(f, apparent(f)))
        audio.write(make_tone(f, 900))
        audio.write(bytes(RATE * 300 // 1000 * 2))
    audio.write(bytes(RATE * 100 // 1000 * 2))
    time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)
finally:
    audio.deinit()
print("Done.")

# Try This
#   1. Add 12800 and 13300 to TONES. 13,300 Hz is above the sample rate: what
#      pitch do you hear? (apparent() says: 13300 % 12800 = 500 Hz.)
#   2. Change RATE to 8000. Which of the tones are aliased now?
