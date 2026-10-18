# Chapter 8, Test 05: Stored audio playback from flash
# 1. Writes one second of a 440 Hz tone to tone.raw (raw 16-bit mono samples)
#    and to tone.wav (the same samples with a 44-byte WAV header).
# 2. Plays tone.raw with play_file() at the right rate.
# 3. Plays tone.wav, skipping the header with seek(44).
# 4. Plays tone.raw again at HALF the right rate, so you hear what a rate
#    mismatch sounds like (lower and twice as long).
# Needs the amplifier and speaker.
#
# PASS: steps 2 and 3 sound the same and take about a second each. Step 4 is
# an octave lower and takes twice as long. The printout shows the times.

NAME = "05-play-file.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import array
import math
import os
import struct
import time
from machine import I2S, Pin

import config

RATE = 16000
IBUF = 8192
N = 256
SINE = array.array("h", [int(32767 * math.sin(2 * math.pi * i / N)) for i in range(N)])


def wav_header(data_bytes, rate=16000, bits=16, channels=1):
    byte_rate = rate * channels * bits // 8
    block = channels * bits // 8
    return struct.pack("<4sI4s4sIHHIIHH4sI",
                       b"RIFF", 36 + data_bytes, b"WAVE",
                       b"fmt ", 16, 1, channels, rate, byte_rate, block, bits,
                       b"data", data_bytes)


def make_files():
    count = RATE            # one second
    fade = RATE // 100
    step = 440 * N / RATE
    phase = 0.0
    samples = array.array("h", [0] * count)
    for i in range(count):
        edge = min(1.0, i / fade, (count - i) / fade)
        samples[i] = int(SINE[int(phase) % N] * config.VOLUME // 100 * edge)
        phase += step
    with open("tone.raw", "wb") as f:
        f.write(samples)
    with open("tone.wav", "wb") as f:
        f.write(wav_header(len(samples) * 2, RATE))
        f.write(samples)


def play_file(audio, path, chunk=1024, skip=0):
    buf = bytearray(chunk)
    view = memoryview(buf)
    with open(path, "rb") as f:
        if skip:
            f.seek(skip)
        while True:
            n = f.readinto(buf)
            if not n:
                break
            audio.write(view[:n])


def open_speaker(rate):
    return I2S(config.I2S_SPEAKER_ID,
               sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
               sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
               format=I2S.MONO, rate=rate, ibuf=IBUF)


def finish(audio, rate):
    audio.write(bytes(rate * 100 // 1000 * 2))
    time.sleep_ms(IBUF * 1000 // (rate * 2) + 50)


make_files()
print("tone.raw: {} bytes (expect 32000)".format(os.stat("tone.raw")[6]))
print("tone.wav: {} bytes (expect 32044)".format(os.stat("tone.wav")[6]))
config.set_gain()

for label, path, skip, rate in (
        ("2. tone.raw at the right rate (16000 Hz)", "tone.raw", 0, RATE),
        ("3. tone.wav, skipping the 44-byte header", "tone.wav", 44, RATE),
        ("4. tone.raw at HALF the rate (8000 Hz)", "tone.raw", 0, RATE // 2)):
    print(label)
    audio = open_speaker(rate)
    try:
        start = time.ticks_ms()
        play_file(audio, path, skip=skip)
        finish(audio, rate)
        print("   took {} ms".format(time.ticks_diff(time.ticks_ms(), start)))
    finally:
        audio.deinit()
    time.sleep_ms(300)
print("Done.")
