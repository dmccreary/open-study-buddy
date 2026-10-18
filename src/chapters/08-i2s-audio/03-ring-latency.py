# Chapter 8, Test 03: Does the ring buffer behave like the chapter's model?
# Reads microphone frames in a loop that takes LOOP_MS per pass (a busy wait
# stands in for slow display or DSP work). Once a second the speaker plays a
# short click; the microphone hears it; the program prints how long after
# the click the loud frame was READ. That delay is the backlog waiting in the
# microphone's ring buffer.
#
# Chapter 8's model says: if LOOP_MS <= 40 the delay stays small (about one
# frame, 40 to 80 ms). If LOOP_MS = 50 the backlog grows 10 ms per pass,
# so the delay grows by about 200 ms per second until the ring (40,000 bytes,
# about 0.78 s of audio) is full, about 3.95 s into the run. Then it should
# stop growing, or something else should happen. THAT is what to find out.
#
# Needs the INMP441 microphone AND the amplifier + speaker, close to each
# other (a few centimeters). Raise VOLUME in config.py if clicks are not heard.
# Try LOOP_MS = 30, 40, 50, 60, 86 in turn and write down the delay curves.

NAME = "03-ring-latency.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from machine import I2S, Pin

import config

LOOP_MS = 50              # <- change me: 30, 40, 50, 60, 86
RUN_SECONDS = 14
CLICK_EVERY_MS = 1000
THRESHOLD_BITS = 3        # a click must be this many bits above the floor
RATE = config.MIC_SAMPLE_RATE
FRAME_SAMPLES = 512
LOG2 = math.log(2)


def loudness(buf):
    samples = [s >> config.MIC_SAMPLE_SHIFT for s in struct.unpack("<512i", buf)]
    middle = sum(samples) // FRAME_SAMPLES
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2


def make_click(ms=8, freq=1500):
    count = RATE * ms // 1000
    out = bytearray(count * 2)
    for i in range(count):
        value = int(32000 * math.sin(2 * math.pi * freq * i / RATE))
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
    print("If the delay keeps growing then levels off near 780 ms, the ring behaves")
    print("like the chapter says. Note what it does at the top.")
finally:
    mic.deinit()
    speaker.deinit()
