# Lab 14: Samples Make Sound
# Builds a sine wave one number at a time, draws every one of those
# numbers as a dot, and plays them. UP and DOWN change the pitch, and you
# can SEE how many samples are left to make each wave.
#
# THE IDEA: SAMPLING. A speaker cone moves in and out smoothly, but the
# Pico can only send it a list of numbers, RATE of them each second
# (16000 here). Each number is one SAMPLE: where the cone should be at that
# instant. A note of frequency f repeats f times a second, so each cycle
# of the wave gets
#
#     samples per cycle = RATE / f          440 Hz: 16000 / 440 = 36.4
#
# The higher the note, the fewer dots draw it. At half the sample rate --
# the NYQUIST limit, 8000 Hz here -- there are only 2 samples per cycle:
# one up, one down, the least that can still be a wave. Above that, the
# samples cannot tell the wave apart from a LOWER one, and you hear the
# wrong note ("aliasing"). The last step, 10000 Hz, is above the limit:
# its samples are exactly those of a 6000 Hz wave (16000 - 10000), so it
# comes out LOWER than the 7000 Hz step before it.
#
#   UP / DOWN   next / previous frequency (it plays each time)
#   MODE        play the same one again
#
# Parts: the speaker and the display (and the buttons).
#
# PASS: each press plays a note and redraws the dots. Low notes are smooth
# curves of many dots; high notes are a few dots in a zig-zag. 10000 Hz
# sounds lower than 7000 Hz.

NAME = "14-samples-make-sound.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from machine import I2S, Pin

import config

RATE = 16000
NOTE_MS = 600
VOLUME = config.VOLUME
FREQS = (110, 220, 440, 880, 1760, 3520, 7000, 10000)

PLOT_X, PLOT_W = 40, 280            # the plot box
PLOT_MID, PLOT_HALF = 186, 52       # its middle line, and its height / 2
PLOT_SAMPLES = 72                   # how many samples to draw
DOT = 3

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


def put(text, y, color, font=SMALL, width=30):
    text = text[:width]
    pad = width - len(text)
    text = " " * (pad // 2) + text + " " * (pad - pad // 2)
    config.centered_text(display, font, text, y, color)


def sample(freq, i, volume=VOLUME):
    """Sample number i of a sine wave: where the cone is at time i / RATE."""
    return int(32767 * volume / 100 * math.sin(2 * math.pi * freq * i / RATE))


def plot(freq):
    """One dot per sample, PLOT_SAMPLES of them, evenly across the box."""
    display.fill_rect(PLOT_X, PLOT_MID - PLOT_HALF - DOT, PLOT_W,
                      2 * (PLOT_HALF + DOT), config.BLACK)
    display.hline(PLOT_X, PLOT_MID, PLOT_W, config.color565(50, 50, 50))
    for i in range(PLOT_SAMPLES):
        x = PLOT_X + i * PLOT_W // PLOT_SAMPLES
        y = PLOT_MID - sample(freq, i, 100) * PLOT_HALF // 32767
        display.fill_rect(x, y - 1, DOT, DOT, config.CYAN)


def play(freq):
    """Make NOTE_MS of samples, with 10 ms fades so it does not click."""
    count = RATE * NOTE_MS // 1000
    fade = RATE // 100
    buf = bytearray(count * 2)
    for i in range(count):
        level = min(1.0, i / fade, (count - i) / fade)
        struct.pack_into("<h", buf, i * 2, int(sample(freq, i) * level))
    audio.write(buf)


def show(index):
    freq = FREQS[index]
    per_cycle = RATE / freq
    put("%d Hz" % freq, 64, config.WHITE, BIG, 9)
    put("%.1f samples per cycle" % per_cycle, 104, config.YELLOW)
    plot(freq)
    if freq > RATE // 2:
        put("past Nyquist: heard as %d Hz" % (RATE - freq), 252, config.RED)
    elif per_cycle < 4:
        put("close to Nyquist", 252, config.color565(255, 140, 0))
    else:
        put("", 252, config.BLACK)
    print("{:5d} Hz  {:5.1f} samples per cycle".format(freq, per_cycle))
    play(freq)


put("UP/DOWN pitch   MODE again", 280, DIM)
put("first %d samples" % PLOT_SAMPLES, 126, DIM)
index = 2                                    # start at 440 Hz
show(index)

last = [1, 1, 1]
try:
    while True:
        for i in range(3):
            value = pins[i].value()
            if value == 0 and last[i] == 1:
                if i == 1:
                    index = min(len(FREQS) - 1, index + 1)
                elif i == 2:
                    index = max(0, index - 1)
                show(index)
            last[i] = value
        time.sleep_ms(20)
finally:
    audio.deinit()

# Try This
#   1. Change RATE to 8000 (and the I2S rate follows it). Which notes are
#      now above Nyquist? Does 440 Hz sound any different?
#   2. Add 9000 to FREQS. It should sound exactly like 7000 Hz. Print a
#      few samples of each: how are the two lists related?
#   3. Replace math.sin with a square wave: 1 if (freq * i / RATE) % 1 < 0.5
#      else -1. How do the dots change? How does the sound change?
