# Lab 15: Envelopes -- Why a Piano Doesn't Sound Like an Organ
# Plays the same four notes four different ways and draws the shape of
# each one's loudness over time. The pitch never changes; only the shape
# does, and that is enough to make it sound like a different instrument.
#
# THE IDEA: AN ENVELOPE is how loud a note is at each moment, from 0 to 1.
# Multiply every sample of a plain wave by it, and the wave takes on the
# envelope's shape:
#
#     sample = wave(t) * envelope(t)
#
#   PLUCK   instant start, then dies away fast      (a guitar string)
#   ORGAN   quick start, holds steady, quick stop   (air through a pipe)
#   SWELL   fades in slowly, then stops             (a bowed violin)
#   BELL    instant start, rings for a long time    (a struck bell)
#
# Musicians describe envelopes in four parts: Attack (how fast it gets
# loud), Decay (how fast it drops after that), Sustain (the level it holds
# while the key is down), and Release (how fast it fades after). PLUCK is
# nearly all decay; ORGAN is nearly all sustain.
#
# Working out a curve like exp() for every one of 16000 samples a second
# would be slow, so the envelope is worked out once per millisecond into a
# table, and each sample looks up its millisecond.
#
#   UP / DOWN   next / previous envelope (it plays)
#   MODE        play it again
#
# Parts: the speaker and the display (and the buttons).
#
# PASS: four very different sounds from the same four notes, each with its
# envelope drawn as a curve.

NAME = "15-sound-envelopes.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from machine import I2S, Pin

import config

RATE = 16000
NOTE_MS = 500
NOTES = (523, 659, 784, 1047)         # C5 E5 G5 C6: a C major arpeggio
VOLUME = config.VOLUME

PLOT_X, PLOT_W = 50, 260
PLOT_TOP, PLOT_H = 120, 110

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
pins = config.init_buttons()
config.set_gain()
audio = I2S(config.I2S_SPEAKER_ID, sck=Pin(config.I2S_BCLK_PIN),
            ws=Pin(config.I2S_LRC_PIN), sd=Pin(config.I2S_DIN_PIN),
            mode=I2S.TX, bits=16, format=I2S.MONO, rate=RATE, ibuf=8192)


# Each envelope: a function from milliseconds-since-the-note-started (t)
# to loudness 0..1, for a note NOTE_MS long.
def pluck(t):
    return math.exp(-t / 90)


def organ(t):
    return min(1.0, t / 15, (NOTE_MS - t) / 30)


def swell(t):
    return min(t / (NOTE_MS * 0.8), 1.0, (NOTE_MS - t) / 20)


def bell(t):
    return math.exp(-t / 400) * min(1.0, t / 2 + 0.01)


ENVELOPES = (("PLUCK", pluck, config.YELLOW, "a guitar string"),
             ("ORGAN", organ, config.GREEN, "a pipe organ"),
             ("SWELL", swell, config.CYAN, "a bowed violin"),
             ("BELL", bell, config.MAGENTA, "a struck bell"))


def put(text, y, color, font=SMALL, width=26):
    text = text[:width]
    pad = width - len(text)
    text = " " * (pad // 2) + text + " " * (pad - pad // 2)
    config.centered_text(display, font, text, y, color)


def table(shape):
    """The envelope, one value per millisecond, clamped to 0..1."""
    return [max(0.0, min(1.0, shape(t))) for t in range(NOTE_MS)]


def plot(levels, color):
    display.fill_rect(PLOT_X, PLOT_TOP, PLOT_W, PLOT_H + 1, config.BLACK)
    display.hline(PLOT_X, PLOT_TOP + PLOT_H, PLOT_W, DIM)     # time axis
    display.vline(PLOT_X, PLOT_TOP, PLOT_H, DIM)              # loudness axis
    previous = None
    for x in range(PLOT_W):
        y = PLOT_TOP + PLOT_H - int(levels[x * NOTE_MS // PLOT_W] * PLOT_H)
        if previous is not None:
            display.line(PLOT_X + x - 1, previous, PLOT_X + x, y, color)
        previous = y


def note(freq, levels):
    """One note: a sine wave, each sample times its millisecond's level."""
    count = RATE * NOTE_MS // 1000
    peak = 32767 * VOLUME / 100
    step = 2 * math.pi * freq / RATE
    buf = bytearray(count * 2)
    for i in range(count):
        level = levels[i * 1000 // RATE]
        struct.pack_into("<h", buf, i * 2, int(peak * level * math.sin(step * i)))
    return buf


def show(index):
    name, shape, color, like = ENVELOPES[index]
    levels = table(shape)
    put(name, 56, color, BIG, 8)
    put("like " + like, 92, DIM)
    plot(levels, color)
    print("{}: like {}".format(name, like))
    # Make all four notes first, then play them back to back, so there is
    # no gap while the Pico works out the next one.
    notes = [note(freq, levels) for freq in NOTES]
    for buf in notes:
        audio.write(buf)


put("0 ms" + " " * 20 + "%d ms" % NOTE_MS, PLOT_TOP + PLOT_H + 6, DIM,
    width=30)
put("UP/DOWN envelope  MODE again", 270, DIM, width=30)
index = 0
show(index)

last = [1, 1, 1]
try:
    while True:
        for i in range(3):
            value = pins[i].value()
            if value == 0 and last[i] == 1:
                if i == 1:
                    index = (index + 1) % len(ENVELOPES)
                elif i == 2:
                    index = (index - 1) % len(ENVELOPES)
                show(index)
            last[i] = value
        time.sleep_ms(20)
finally:
    audio.deinit()

# Try This
#   1. Make PLUCK die faster (change 90 to 30), then slower (to 300). At
#      what point does it stop sounding plucked?
#   2. Write your own envelope: a "tremolo" that wobbles,
#      0.6 + 0.4 * math.sin(t / 20). Add it to ENVELOPES.
#   3. Give BELL two waves at once -- the note and a quieter one at 2.76
#      times its frequency -- the way a real bell rings. Does it sound
#      more like a bell?
