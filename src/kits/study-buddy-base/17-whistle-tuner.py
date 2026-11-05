# Lab 17: A Whistle Tuner -- Measuring Pitch
# Whistle (or hum, or sing "ooo") and the screen shows the frequency, the
# nearest musical note, and a needle that says whether you are sharp or
# flat.
#
# THE IDEA: FREQUENCY FROM ZERO CROSSINGS. A steady note is a wave that
# crosses the middle line going upward once every cycle. Count the upward
# crossings in a frame and time how far apart they are:
#
#     frequency = (crossings - 1) * RATE / (samples from first to last)
#
# Two tricks make it work on real sound:
#
#   HYSTERESIS. Near the middle line, noise wiggles the signal back and
#   forth across it, making false crossings. So a crossing only counts once
#   the signal has gone properly low (below -LEVEL) and then properly high
#   (above +LEVEL), where LEVEL is a fraction of the frame's peak.
#
#   A NOISE GATE. A quiet room has no pitch at all, so frames that are not
#   clearly louder than the room are ignored instead of shown as nonsense
#   numbers. The first second is spent measuring how loud the room is
#   (its "noise floor"); a frame must be GATE times louder to count.
#
# Then from frequency to note: every note is 2^(1/12) higher than the one
# below it, 12 to an octave, and A4 is 440 Hz. So
#
#     note number = 69 + 12 * log2(frequency / 440)
#
# The whole part is the nearest note; the rest, times 100, is how many
# "cents" sharp (+) or flat (-) you are. 100 cents make one note.
#
# A whistle is almost a pure sine wave, which is why this simple method
# works for it. A voice has many waves at once, and zero crossings get
# confused by the extra ones -- that is what the FFT in Chapter 9 is for.
#
# Parts: the microphone and the display.
#
# PASS: whistling shows a steady frequency (usually 500-3000 Hz) and a note
# name; the needle moves when you slide the pitch up and down.

NAME = "17-whistle-tuner.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
from machine import I2S, Pin

import config

RATE = config.MIC_SAMPLE_RATE           # 12800
FRAME = 1024                            # 80 ms: enough waves to count
GATE = 4                                # this many times the room's noise
CALIBRATE_FRAMES = 12                   # about one second of quiet
HYSTERESIS = 0.3                        # LEVEL as a fraction of the peak
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
CX = config.CENTER_X
BAR_W, BAR_Y, BAR_H = 240, 218, 20

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
mic = I2S(config.MIC_I2S_ID, sck=Pin(config.MIC_SCK_PIN),
          ws=Pin(config.MIC_WS_PIN), sd=Pin(config.MIC_SD_PIN),
          mode=I2S.RX, bits=32, format=I2S.MONO, rate=RATE, ibuf=8192)
buf = bytearray(FRAME * 4)


def put(text, y, color, font=SMALL, width=24):
    text = text[:width]
    pad = width - len(text)
    text = " " * (pad // 2) + text + " " * (pad - pad // 2)
    config.centered_text(display, font, text, y, color)


def loudness(samples, offset):
    """The average distance from the middle line."""
    return sum(abs(s - offset) for s in samples) // len(samples)


def pitch(samples, floor):
    """Returns (frequency, peak). frequency is None if it cannot tell."""
    offset = sum(samples) // len(samples)
    if loudness(samples, offset) < floor * GATE:
        return None, 0
    peak = max(abs(s - offset) for s in samples)
    level = int(peak * HYSTERESIS)
    low = offset - level
    high = offset + level
    armed = False                 # True once the signal has gone low
    first = last = None
    crossings = 0
    for i in range(len(samples)):
        s = samples[i]
        if s < low:
            armed = True
        elif s > high and armed:  # low, then high: one upward crossing
            armed = False
            crossings += 1
            if first is None:
                first = i
            last = i
    if crossings < 3:
        return None, peak
    return (crossings - 1) * RATE / (last - first), peak


def note_of(frequency):
    """(name, cents) of the nearest note."""
    number = 69 + 12 * math.log(frequency / 440) / math.log(2)
    nearest = round(number)
    cents = round((number - nearest) * 100)
    name = NOTE_NAMES[nearest % 12] + str(nearest // 12 - 1)
    return name, cents


def needle(cents):
    """A bar from -50 to +50 cents with a marker; green when in tune."""
    x0 = CX - BAR_W // 2
    display.fill_rect(x0, BAR_Y, BAR_W, BAR_H, config.color565(40, 40, 40))
    display.vline(CX, BAR_Y - 4, BAR_H + 8, DIM)
    if cents is None:
        return
    x = CX + cents * (BAR_W // 2) // 50
    color = config.GREEN if abs(cents) <= 5 else (
        config.YELLOW if abs(cents) <= 20 else config.RED)
    display.fill_rect(x - 3, BAR_Y, 7, BAR_H, color)


put("WHISTLE TUNER", 56, DIM)
config.centered_text(display, SMALL, "flat" + " " * 22 + "sharp",
                     BAR_Y + BAR_H + 8, DIM)
put("whistle a steady note", 280, DIM)
needle(None)
shown = None


def read_frame():
    mic.readinto(buf)
    return [s >> config.MIC_SAMPLE_SHIFT
            for s in struct.unpack("<%di" % FRAME, buf)]


try:
    put("quiet please...", 96, config.CYAN, BIG, 15)
    read_frame()                                # skip the start-up sound
    total = 0
    for _ in range(CALIBRATE_FRAMES):
        samples = read_frame()
        total += loudness(samples, sum(samples) // FRAME)
    floor = max(1, total // CALIBRATE_FRAMES)
    print("Room noise: {} -- a note must be over {}".format(floor,
                                                            floor * GATE))
    put("", 96, DIM, BIG, 15)
    put("--", 96, DIM, BIG, 9)
    while True:
        samples = read_frame()
        frequency, peak = pitch(samples, floor)
        if frequency is None:
            if shown is not None:
                put("--", 96, DIM, BIG, 9)
                put("", 144, DIM, BIG, 6)
                needle(None)
                shown = None
            continue
        name, cents = note_of(frequency)
        put("%d Hz" % frequency, 96, config.WHITE, BIG, 9)
        put(name, 144, config.CYAN, BIG, 6)
        needle(cents)
        shown = name
        print("{:7.1f} Hz  {:3}  {:+3d} cents  (peak {})".format(
            frequency, name, cents, peak))
finally:
    mic.deinit()

# Try This
#   1. Whistle the same note and watch the cents. How steady can you hold
#      it? Professional singers stay within about 10 cents.
#   2. Set HYSTERESIS to 0. Whistle softly. What happens to the reading,
#      and why?
#   3. Play a note from a phone tuner app next to the microphone (try A4,
#      440 Hz). How close does this tuner get?
