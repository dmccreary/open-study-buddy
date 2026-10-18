# Chapter 3, Test 03: Audio clipping
# Multiplies a sine wave of peak 6,000 by several gains and counts how many
# samples hit the limit of a signed 16-bit number (32,767). Then, if you have a
# speaker, it plays the low-gain and high-gain versions so you can hear the
# crackle. Counting needs no hardware; playing needs the amplifier and speaker.
#
# PASS: gain 2 and gain 4 have 0 clipped samples; gain 8 and gain 24 have many,
# and the peak stays at the limit (32,767 or 32,768). If PLAY is True you hear a smooth tone, then a
# harsh one.

NAME = "03-clipping-demo.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct

PLAY = True            # set False to only print the table
RATE = 12800
FREQ = 440
PEAK = 6000
LIMIT_HIGH = 32767
LIMIT_LOW = -32768


def clipped_tone(gain, ms=700):
    count = RATE * ms // 1000
    out = bytearray(count * 2)
    clipped = 0
    peak = 0
    for i in range(count):
        value = int(PEAK * math.sin(2 * math.pi * FREQ * i / RATE)) * gain
        if value > LIMIT_HIGH or value < LIMIT_LOW:
            clipped += 1
        value = max(LIMIT_LOW, min(LIMIT_HIGH, value))
        peak = max(peak, abs(value))
        struct.pack_into("<h", out, i * 2, value)
    return out, clipped, count, peak


print()
print("{:>5} {:>8} {:>9} {:>8}".format("gain", "clipped", "of", "peak"))
tones = {}
for gain in (2, 4, 8, 24):
    data, clipped, count, peak = clipped_tone(gain)
    tones[gain] = data
    print("{:>5} {:>8} {:>9} {:>8}".format(gain, clipped, count, peak))

if PLAY:
    try:
        import time
        from machine import I2S, Pin
        import config
        config.set_gain()
        audio = I2S(config.I2S_SPEAKER_ID,
                    sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
                    sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                    format=I2S.MONO, rate=RATE, ibuf=8192)
        try:
            for gain in (2, 8):
                print("playing gain", gain, "(keep the speaker away from your ear)")
                audio.write(tones[gain])
                audio.write(bytes(RATE * 300 // 1000 * 2))
            audio.write(bytes(RATE * 100 // 1000 * 2))
            time.sleep_ms(8192 * 1000 // (RATE * 2) + 50)
        finally:
            audio.deinit()
    except ImportError:
        print("(no machine module: skipping playback)")
print("Done.")

# Try This
#   1. Change PEAK to 2000 and repeat. At what gain does clipping start now?
#      (32767 / 2000 = 16.4, so gain 17.)
#   2. Why does a clipped sine wave sound harsher even though it is not louder
#      than a gain of 4? (It gains new high-frequency content: Chapter 9.)
