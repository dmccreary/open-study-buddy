# Chapter 8, Test 06: Measure the self-hearing problem
# Plays a 1 kHz tone (at most 30% of full scale: it is kept quiet) through the speaker while reading the microphone, and
# prints the microphone's loudness for every 40 ms frame: before the tone, while
# it plays, and after it stops. Tells you how loud the device hears itself and
# how long the "quiet tail" must be before the microphone can be trusted again.
# Needs the microphone AND the amplifier + speaker in their normal places.
#
# PASS: the loudness during the tone is clearly above the floor (the device
# hears itself), and it falls back to within 1 bit of the floor some frames
# after the tone's last write. Write down the "quiet tail" number.
#
# The speaker's buffer holds 8,192 bytes (320 ms at 12,800 Hz), so sound keeps
# playing for a while after the last write; the tail includes that.

NAME = "06-self-hearing.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from machine import I2S, Pin

import config

RATE = config.MIC_SAMPLE_RATE
FRAME_SAMPLES = 512
TONE_FRAMES = 25            # one second of tone
LEAD_FRAMES = 10
TAIL_FRAMES = 25
LOG2 = math.log(2)
TONE_VOLUME = min(config.VOLUME, 30)     # percent of full scale; kept low on purpose


def loudness(buf):
    samples = [s >> config.MIC_SAMPLE_SHIFT for s in struct.unpack("<512i", buf)]
    middle = sum(samples) // FRAME_SAMPLES
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2


# One 40 ms chunk of a 1 kHz sine, reused for every frame of the tone
chunk = bytearray(FRAME_SAMPLES * 2)
for i in range(FRAME_SAMPLES):
    struct.pack_into("<h", chunk, i * 2,
                     int(32767 * TONE_VOLUME / 100 * math.sin(2 * math.pi * 1000 * i / RATE)))
silence = bytes(FRAME_SAMPLES * 2)

config.set_gain()
speaker = I2S(config.I2S_SPEAKER_ID,
              sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
              sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
              format=I2S.MONO, rate=RATE, ibuf=8192)
mic = config.init_microphone()
buf = bytearray(FRAME_SAMPLES * 4)
try:
    for _ in range(8):
        mic.readinto(buf)
    levels = []
    labels = []
    for n in range(LEAD_FRAMES + TONE_FRAMES + TAIL_FRAMES):
        if LEAD_FRAMES <= n < LEAD_FRAMES + TONE_FRAMES:
            speaker.write(chunk)
            labels.append("tone ")
        else:
            speaker.write(silence)
            labels.append("quiet")
        mic.readinto(buf)
        levels.append(loudness(buf))

    floor = sum(levels[:LEAD_FRAMES]) / LEAD_FRAMES
    print("Noise floor before the tone: {:.1f} bits".format(floor))
    print()
    print("{:>5} {:>6} {:>6}  {}".format("frame", "what", "bits", "above floor"))
    for n, (label, bits) in enumerate(zip(labels, levels)):
        print("{:>5} {:>6} {:>6.1f}  {:+.1f}".format(n, label, bits, bits - floor))

    during = levels[LEAD_FRAMES + 5:LEAD_FRAMES + TONE_FRAMES]
    heard_bits = sum(during) / len(during)
    print()
    print("Average while the tone plays: {:.1f} bits = {:.1f} above the floor "
          "({:.0f}x louder)".format(heard_bits, heard_bits - floor, 2 ** (heard_bits - floor)))

    # The tail ends at the first run of 3 quiet frames in a row, so one noisy
    # frame in a room does not stretch the answer.
    tone_end = LEAD_FRAMES + TONE_FRAMES
    tail = None
    for n in range(tone_end, len(levels) - 2):
        if all(levels[n + k] <= floor + 1 for k in range(3)):
            tail = (n - tone_end) * 40
            break
    if tail is None:
        tail = TAIL_FRAMES * 40
        print("(the microphone never settled within {} ms)".format(tail))
    print("Quiet tail needed after the last write: about {} ms".format(tail))
    print("PASS if the tone was clearly louder than the floor." if heard_bits - floor > 2
          else "CHECK: the microphone barely heard the speaker (it may be far away or the volume low).")
finally:
    mic.deinit()
    speaker.deinit()
