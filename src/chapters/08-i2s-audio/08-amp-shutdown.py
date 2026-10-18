# Chapter 8, Test 08 (OPTIONAL): Hardware mute with the amplifier's SD pin
# Only run this if you have wired the MAX98357A's SD (shutdown) pin to GP22.
# The base kit does NOT wire it. Plays a continuous quiet tone and, every two
# seconds, mutes it by pulling SD low and then resumes by turning GP22 back
# into an input (the board's own resistor turns the amplifier on).
#
# PASS: you hear 2 s of tone, 2 s of silence, 2 s of tone, 2 s of silence, 2 s
# of tone. If the tone never stops, SD is not wired to GP22. If it stops and
# never comes back, your board needs a pull-up on SD: check its documentation.

NAME = "08-amp-shutdown.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import array
import math
import time
from machine import I2S, Pin

import config

RATE = 16000
IBUF = 8192
SD_PIN = 22
N = 256
SINE = array.array("h", [int(32767 * math.sin(2 * math.pi * i / N)) for i in range(N)])

# 100 ms of 440 Hz, repeated: 440 Hz x 0.1 s = 44 whole cycles
count = RATE // 10
step = 440 * N / RATE
phase = 0.0
piece = array.array("h", [0] * count)
for i in range(count):
    piece[i] = SINE[int(phase) % N] * config.VOLUME // 100
    phase += step

config.set_gain()
audio = I2S(config.I2S_SPEAKER_ID,
            sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
            sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
            format=I2S.MONO, rate=RATE, ibuf=IBUF)


def play_for(ms):
    end = time.ticks_add(time.ticks_ms(), ms)
    while time.ticks_diff(time.ticks_ms(), end) < 0:
        audio.write(piece)


try:
    for round_number in range(3):
        print("tone on")
        play_for(2000)
        if round_number < 2:
            print("MUTE: SD low")
            Pin(SD_PIN, Pin.OUT, value=0)
            play_for(2000)
            print("RESUME: SD back to input")
            Pin(SD_PIN, Pin.IN)
            time.sleep_ms(20)
finally:
    Pin(SD_PIN, Pin.IN)
    audio.write(bytes(RATE * 100 // 1000 * 2))
    time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)
    audio.deinit()
print("Done.")
