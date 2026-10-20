# Chapter 8, Test 03: Does the ring buffer behave like the chapter's model?
# Reads microphone frames in a loop that takes LOOP_MS per pass (a busy wait
# stands in for slow display or DSP work). Once a second the speaker plays a
# short click; the microphone hears it; the program prints how long after
# the click the loud frame was READ. That delay is the backlog waiting in the
# microphone's ring buffer.
#
# What Chapter 8 says, from the first measurements on the test board:
#   LOOP_MS = 30: the delay stays flat at about 50 ms.
#   LOOP_MS = 50: the delay grows about 10 ms per pass (about 200 ms per second),
#                 then stops near 460 ms, and some clicks are never heard (lost).
# So the ring is only about 0.4 s deep (about 9.8 frames), not the 0.78 s that
# 40,000 bytes would hold at 4 bytes per sample. Chapter 8 offers one
# explanation, still unconfirmed: MONO mode stores 8 bytes per sample time.
# Runs at LOOP_MS = 40, 60 and 130 are still needed. At 130 ms (a full-screen
# redraw) the model predicts audio is lost after about 0.65 s.
#
# Needs the INMP441 microphone AND the amplifier + speaker, close to each
# other (a few centimeters). The click is QUIET on purpose: it plays at 75% of
# VOLUME in config.py, for 80 ms, once a second. If clicks are not heard, move
# the speaker closer to the microphone before raising the volume.
# Try LOOP_MS = 30, 40, 50, 60, 130 in turn and write down the delay curves.

NAME = "03-ring-latency.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from machine import I2S, Pin

import config

LOOP_MS = 50              # <- change me: 30, 40, 50, 60, 130
RUN_SECONDS = 14
CLICK_EVERY_MS = 1000
THRESHOLD_BITS = 2        # a click must be this many bits above the floor
CLICK_VOLUME = config.VOLUME * 3 // 4     # percent of full scale; quiet on purpose
CLICK_MS = 80
RATE = config.MIC_SAMPLE_RATE
FRAME_SAMPLES = 512
LOG2 = math.log(2)


def loudness(buf):
    samples = [s >> config.MIC_SAMPLE_SHIFT for s in struct.unpack("<512i", buf)]
    middle = sum(samples) // FRAME_SAMPLES
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2


def make_click(ms=CLICK_MS, freq=1000):
    count = RATE * ms // 1000
    out = bytearray(count * 2)
    for i in range(count):
        value = int(32767 * CLICK_VOLUME / 100 * math.sin(2 * math.pi * freq * i / RATE))
        struct.pack_into("<h", out, i * 2, value)
    return out


click = make_click()
buf = bytearray(FRAME_SAMPLES * 4)
config.set_gain()
speaker = I2S(config.I2S_SPEAKER_ID,
              sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
              sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
              format=I2S.MONO, rate=RATE, ibuf=4096)
mic = config.init_microphone()
try:
    for _ in range(8):
        mic.readinto(buf)
    total = 0
    for _ in range(25):
        mic.readinto(buf)
        total += loudness(buf)
    floor = total / 25
    print("Noise floor {:.1f} bits; a click counts above {:.1f} bits.".format(
        floor, floor + THRESHOLD_BITS))
    print("LOOP_MS = {}  (a frame is 40 ms)".format(LOOP_MS))
    print()
    print("{:>9} {:>14}".format("run time", "delay to read click"))

    started = time.ticks_ms()
    last_click = time.ticks_add(started, -CLICK_EVERY_MS)
    sent_at = None
    heard = 0
    missed = 0
    while time.ticks_diff(time.ticks_ms(), started) < RUN_SECONDS * 1000:
        pass_start = time.ticks_ms()
        if time.ticks_diff(pass_start, last_click) >= CLICK_EVERY_MS:
            if sent_at is not None:
                missed += 1
                print("{:>7} ms   click not heard (move the speaker closer?)".format(
                    time.ticks_diff(pass_start, started)))
            speaker.write(click)
            sent_at = time.ticks_ms()
            last_click = pass_start
        mic.readinto(buf)
        if sent_at is not None and loudness(buf) > floor + THRESHOLD_BITS:
            now = time.ticks_ms()
            heard += 1
            print("{:>7} ms   {:>6} ms".format(
                time.ticks_diff(now, started), time.ticks_diff(now, sent_at)))
            sent_at = None
        while time.ticks_diff(time.ticks_ms(), pass_start) < LOOP_MS:
            pass                                   # pretend to do slow work
    print()
    print("clicks heard {}, missed {}".format(heard, missed))
    print("Chapter 8 expects the delay to level off near 460 ms (a ring about 0.4 s deep),")
    print("with some clicks lost. Note where yours levels off and how many clicks are missed.")
finally:
    mic.deinit()
    speaker.deinit()
