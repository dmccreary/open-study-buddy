# demo_listen.py -- demo 7 of 20-demo-template.py: a sound meter.
#
# An arc of 29 lights, like the needle meter on a stereo (a "VU meter"),
# that swings with how loud the room is: green, then yellow, then red. A
# white light hangs on at the loudest point for a moment ("peak hold"),
# and "I hear you!" comes up when someone speaks.
#
# It works exactly like test 06: one frame of 512 samples (40 ms of
# sound) at a time, the frame's average distance from the middle, then
# log base 2 of that -- "bits", where each bit is twice as loud. Here the
# bits are also shown as decibels (6 dB per bit), the unit sound meters
# use. The first second is quiet time, to learn how noisy the room is.
#
#   UP or DOWN   learn the room's noise again

import math
import struct
import time

import config
from demo_kit import (BLACK, WHITE, DIM, FAINT, TRACK, SMALL, BIG, CX, put,
                      centered, menu_hint)
from watchparts import TickRing, TextLine

FRAME_SAMPLES = 512
FRAME_FORMAT = "<512i"
CALIBRATE_FRAMES = 25          # one second
SPEECH_ABOVE_FLOOR = 2.0       # bits above the noise floor that count as talking
METER_MIN_BITS = 9
METER_MAX_BITS = 21
PEAK_HOLD_MS = 900
LOG2 = math.log(2)

# The arc: ticks 46..59 and 0..14 of a 60-tick ring, the top half.
ARC_CY = 200
ARC_TICKS = tuple((46 + k) % 60 for k in range(29))
SEGMENTS = len(ARC_TICKS)

TITLE_Y = 100
LEVEL_Y = 124
STATUS_Y = 176
FLOOR_Y = 220
TIP_Y = 244
MENU_Y = 296


def segment_color(k):
    fraction = k / SEGMENTS
    return (config.GREEN if fraction < 0.6 else
            config.YELLOW if fraction < 0.85 else config.RED)


def start(display, kit, saved):
    global _display, _kit, mic, buf, ring, floor, lit, peak, peak_at
    global heard, calibrating, frames, total, level
    _display = display
    _kit = kit
    display.fill(BLACK)
    centered(display, SMALL, "SOUND METER", TITLE_Y, DIM)
    menu_hint(display, MENU_Y)
    ring = TickRing(display, CX, ARC_CY, 150, 112, 112, half_width=4)
    for tick in ARC_TICKS:
        ring.paint(tick, TRACK)
    # TextLine repaints only the letters that change, so the number can
    # be updated 25 times a second without slowing the meter down.
    level = TextLine(display, BIG, CX, LEVEL_Y, 6, WHITE)
    buf = bytearray(FRAME_SAMPLES * 4)
    lit = 0
    peak = 0
    peak_at = 0
    heard = None
    floor = 0.0
    try:
        mic = config.init_microphone()
    except (OSError, ValueError) as error:
        print("No microphone:", error)
        mic = None
        put(display, BIG, "No mic", STATUS_Y, config.RED, 12)
        return
    begin_calibration()


def begin_calibration():
    global calibrating, frames, total
    calibrating = True
    frames = -8                    # skip the microphone's start-up frames
    total = 0.0
    put(_display, BIG, "Quiet please", STATUS_Y, config.CYAN, 12)
    put(_display, SMALL, "learning how loud the room is", FLOOR_Y, DIM, 32)
    put(_display, SMALL, "", TIP_Y, DIM, 32)


def loudness_bits():
    samples = [s >> config.MIC_SAMPLE_SHIFT
               for s in struct.unpack(FRAME_FORMAT, buf)]
    middle = sum(samples) // FRAME_SAMPLES       # the microphone's DC offset
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2


def show_meter(count, now):
    """Light the first `count` segments, and keep the loudest one of the
    last PEAK_HOLD_MS lit in white. Only segments that change are sent."""
    global lit, peak, peak_at
    if count >= peak or time.ticks_diff(now, peak_at) > PEAK_HOLD_MS:
        if peak > count:                 # the old peak light goes out
            ring.paint(ARC_TICKS[peak - 1], TRACK)
        peak = count
        peak_at = now
    for k in range(min(lit, count), max(lit, count)):
        if k != peak - 1:
            ring.paint(ARC_TICKS[k], segment_color(k) if k < count else TRACK)
    lit = count
    if peak > count:
        ring.paint(ARC_TICKS[peak - 1], WHITE)
    elif peak > 0:
        ring.paint(ARC_TICKS[peak - 1], segment_color(peak - 1))


def update(now):
    global calibrating, frames, total, floor, heard
    if mic is None:
        return
    if _kit.up.pressed(now) or _kit.down.pressed(now):
        begin_calibration()
    mic.readinto(buf)
    bits = loudness_bits()

    if calibrating:
        frames += 1
        if frames > 0:
            total += bits
        if frames >= CALIBRATE_FRAMES:
            calibrating = False
            floor = total / CALIBRATE_FRAMES
            heard = None
            print("Noise floor: {:.1f} bits".format(floor))
            put(_display, SMALL, "quiet room: {:.0f} dB".format(floor * 6.02),
                FLOOR_Y, DIM, 32)
            put(_display, SMALL, "talk, clap, or whistle", TIP_Y,
                config.YELLOW, 32)
        return

    fraction = (bits - METER_MIN_BITS) / (METER_MAX_BITS - METER_MIN_BITS)
    count = int(SEGMENTS * max(0.0, min(1.0, fraction)) + 0.5)
    show_meter(count, now)
    level.show("%d dB" % round(bits * 6.02))

    is_loud = bits > floor + SPEECH_ABOVE_FLOOR
    if is_loud != heard:
        heard = is_loud
        if is_loud:
            put(_display, BIG, "I hear you!", STATUS_Y, config.GREEN, 12)
        else:
            put(_display, BIG, "Listening...", STATUS_Y, DIM, 12)


def stop():
    if mic is not None:
        mic.deinit()
    return None
