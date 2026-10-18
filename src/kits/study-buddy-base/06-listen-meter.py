# Test 06: Listen with the Microphone
# Shows "Say 'Hey Pico'" on the round display and listens on the INMP441
# microphone. A level meter under the words moves with how loud the room is,
# and the status line changes to "I hear you!" when you speak up.
#
# This is NOT wake-word detection yet. It only measures loudness. Chapter 12
# builds the real thing. The point of this test is to prove the whole path
# works before that chapter needs it: microphone -> I2S -> Pico -> display.
#
# It needs the display and the microphone, nothing else.
#
# PASS: the meter bounces when you talk, clap, or tap near the microphone and
# sits low when the room is quiet. "I hear you!" appears when you speak.
# If the meter never moves, run test 02 -- section 7 checks the microphone.
# If it is stuck at full, the room may be loud, or the SD wire is picking up
# noise.
#
# How the meter works
#   The microphone sends 32-bit numbers, 12800 of them each second. The real
#   24-bit audio is in the top of each number, so we shift right by 8. A
#   frame of 512 numbers is 40 ms of sound. For each frame we find the average
#   distance from the middle (the loudness), then take log base 2. Each
#   "bit" is a doubling of loudness, which is how ears hear it too.

NAME = "06-listen-meter.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time

import config

FRAME_SAMPLES = 512
FRAME_FORMAT = "<512i"
FRAME_BYTES = FRAME_SAMPLES * 4

CALIBRATE_FRAMES = 25        # one second of quiet to learn the room's noise
SPEECH_ABOVE_FLOOR = 2.0     # bits above the noise floor that counts as "heard"
METER_MIN_BITS = 9           # the bottom of the meter (about 500)
METER_MAX_BITS = 21          # the top of the meter (about 2,000,000)

METER_WIDTH = 200
METER_HEIGHT = 22
METER_X = config.CENTER_X - METER_WIDTH // 2
METER_Y = 190

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
TRACK = config.color565(40, 40, 40)
LOG2 = math.log(2)

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)


def put(text, y, font, color, width):
    """Draw text centered, padded to a fixed width so it covers whatever
    was there before."""
    config.centered_text(display, font, text.center(width), y, color)


put("Say 'Hey Pico'", 100, BIG, config.YELLOW, 14)
put("a level meter, not a wake word yet", 145, SMALL, DIM, 36)
display.rect(METER_X - 2, METER_Y - 2, METER_WIDTH + 4, METER_HEIGHT + 4,
             config.WHITE)
display.fill_rect(METER_X, METER_Y, METER_WIDTH, METER_HEIGHT, TRACK)


def loudness_bits(buf):
    """Returns the loudness of one frame, in bits (log base 2)."""
    samples = [s >> config.MIC_SAMPLE_SHIFT
               for s in struct.unpack(FRAME_FORMAT, buf)]
    middle = sum(samples) // FRAME_SAMPLES        # the microphone's DC offset
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2


def meter_fraction(bits):
    fraction = (bits - METER_MIN_BITS) / (METER_MAX_BITS - METER_MIN_BITS)
    return max(0.0, min(1.0, fraction))


mic = config.init_microphone()
buf = bytearray(FRAME_BYTES)
try:
    # ------------------------------------------------------------------
    # Learn the room's noise floor, so "loud" means louder than THIS room.
    # ------------------------------------------------------------------
    put("Quiet please...", 255, BIG, config.CYAN, 14)
    print("Calibrating for 1 second -- stay quiet.")
    for _ in range(8):                     # skip the microphone's start-up
        mic.readinto(buf)
    total = 0
    for _ in range(CALIBRATE_FRAMES):
        mic.readinto(buf)
        total += loudness_bits(buf)
    floor = total / CALIBRATE_FRAMES
    print("Noise floor: {:.1f} bits. Now say 'Hey Pico'.".format(floor))

    # ------------------------------------------------------------------
    # Listen forever.
    # ------------------------------------------------------------------
    heard = None                           # what the status line shows now
    drawn_width = -1                       # what the meter shows now
    frame = 0
    peak = 0.0
    while True:
        mic.readinto(buf)
        bits = loudness_bits(buf)
        peak = max(peak, bits)

        width = int(METER_WIDTH * meter_fraction(bits))
        if abs(width - drawn_width) >= 2:
            fraction = width / METER_WIDTH
            color = (config.GREEN if fraction < 0.5 else
                     config.YELLOW if fraction < 0.8 else config.RED)
            display.fill_rect(METER_X, METER_Y, width, METER_HEIGHT, color)
            display.fill_rect(METER_X + width, METER_Y,
                              METER_WIDTH - width, METER_HEIGHT, TRACK)
            drawn_width = width

        is_loud = bits > floor + SPEECH_ABOVE_FLOOR
        if is_loud != heard:
            heard = is_loud
            if is_loud:
                put("I hear you!", 255, BIG, config.GREEN, 14)
            else:
                put("Listening...", 255, BIG, DIM, 14)
            put("floor {:.1f}   loud > {:.1f} bits".format(
                floor, floor + SPEECH_ABOVE_FLOOR), 225, SMALL, DIM, 36)

        frame += 1
        if frame % 5 == 0:                 # 5 frames = 200 ms
            print("{:5.1f} bits  {}".format(bits, "#" * int(bits)))
finally:
    mic.deinit()

# Try This
#   1. Make SPEECH_ABOVE_FLOOR 1.0, then 3.0. How does "I hear you!" change?
#      Which setting would a noisy classroom need?
#   2. Clap once. Does the meter jump and fall back? Whistle a steady note.
#      What does the meter do?
#   3. Play a steady tone from a phone next to the microphone. Does the
#      meter hold still, or wobble like it does for speech?
