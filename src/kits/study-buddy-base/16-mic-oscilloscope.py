# Lab 16: A Microphone Oscilloscope
# Draws the sound the microphone hears as a wave across the screen, 25
# times a second. Hum, whistle, or say "ahhh" and watch its shape.
#
# THE IDEA: WHAT A MICROPHONE SAMPLE IS. The INMP441 measures the air
# pressure on its tiny membrane 12800 times a second and sends each
# measurement as a number. Plot the numbers left to right and you see the
# sound wave itself. Three things to notice:
#
#   DC OFFSET. Silence is not 0. This microphone adds a constant (around
#   15000) to everything it sends. Subtracting the average of a frame puts
#   silence back on the middle line.
#
#   GAIN. Speech is small numbers next to the full 24-bit range, so the
#   picture is scaled up. UP and DOWN zoom in and out.
#
#   TRIGGER. Each frame starts at a random point in the wave, so a steady
#   hum would jump around from frame to frame. A trigger waits for the wave
#   to cross the middle line going UP and starts drawing there, so every
#   frame of a steady note starts at the same place in its cycle and the
#   picture holds still. MODE turns the trigger on and off -- try a steady
#   whistle both ways.
#
# The I2S buffer here is small (ibuf 4096 bytes, 80 ms of sound), unlike
# the big one in config.init_microphone(). Drawing is slower than the
# sound arrives, and a big buffer would let the picture fall further and
# further behind what you are doing.
#
# Parts: the microphone and the display (and the buttons).
#
# PASS: a flat line when it is quiet, a wave that grows when you make a
# sound, and a steady hum or whistle holds still while the trigger is on.

NAME = "16-mic-oscilloscope.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import struct
import time
from machine import I2S, Pin

import config

RATE = config.MIC_SAMPLE_RATE           # 12800 samples a second
FRAME = 512                             # 40 ms
SHOWN = 256                             # samples drawn: 20 ms of sound
PLOT_X, PLOT_W = 52, 256                # one sample per pixel
PLOT_MID, PLOT_HALF = 180, 80

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
GRID = config.color565(40, 40, 40)
TRACE = config.GREEN

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
pins = config.init_buttons()

mic = I2S(config.MIC_I2S_ID, sck=Pin(config.MIC_SCK_PIN),
          ws=Pin(config.MIC_WS_PIN), sd=Pin(config.MIC_SD_PIN),
          mode=I2S.RX, bits=32, format=I2S.MONO, rate=RATE, ibuf=4096)
buf = bytearray(FRAME * 4)


def put(text, y, color, width=28):
    text = text[:width]
    pad = width - len(text)
    text = " " * (pad // 2) + text + " " * (pad - pad // 2)
    config.centered_text(display, SMALL, text, y, color)


def grid():
    display.hline(PLOT_X, PLOT_MID, PLOT_W, GRID)
    for x in range(PLOT_X, PLOT_X + PLOT_W + 1, 64):     # 5 ms per square
        display.vline(x, PLOT_MID - PLOT_HALF, 2 * PLOT_HALF, GRID)


put("SCOPE: 5 ms per square", 52, DIM)
put("UP/DOWN zoom, MODE trigger", 288, DIM)
grid()

zoom = 2                 # the wave is multiplied by this before drawing
trigger = True
old = [PLOT_MID] * SHOWN  # the y of each point drawn last time
last = [1, 1, 1]
frames = 0

try:
    while True:
        mic.readinto(buf)
        # 32-bit samples; the real 24 bits are at the top, so shift by 8.
        samples = [s >> config.MIC_SAMPLE_SHIFT
                   for s in struct.unpack("<%di" % FRAME, buf)]
        offset = sum(samples) // FRAME              # the DC offset
        peak = max(abs(s - offset) for s in samples)

        # Find a trigger point: below the middle, then at or above it.
        start = 0
        if trigger:
            for i in range(1, FRAME - SHOWN):
                if samples[i - 1] < offset <= samples[i]:
                    start = i
                    break

        # Erase the old trace and draw the new one, one column at a time:
        # each column is a vertical line from the last point to this one,
        # so the wave stays joined up even where it is steep.
        scale = zoom * PLOT_HALF
        previous_old = old[0]
        previous_new = None
        for x in range(SHOWN):
            value = (samples[start + x] - offset) * scale // 65536
            y = PLOT_MID - max(-PLOT_HALF, min(PLOT_HALF - 1, value))
            if previous_new is None:
                previous_new = y
            top = min(previous_old, old[x])
            display.vline(PLOT_X + x, top, max(previous_old, old[x]) - top + 1,
                          config.BLACK)
            top = min(previous_new, y)
            display.vline(PLOT_X + x, top, max(previous_new, y) - top + 1,
                          TRACE)
            previous_old = old[x]
            previous_new = y
            old[x] = y
        if frames % 8 == 0:
            grid()                                   # repair the grid lines

        frames += 1
        if frames % 5 == 0:
            put("offset %d   peak %d" % (offset, peak), 74, config.YELLOW)
            put("zoom x%d   trigger %s" % (zoom, "ON" if trigger else "off"),
                266, config.CYAN)

        for i in range(3):
            value = pins[i].value()
            if value == 0 and last[i] == 1:
                if i == 0:
                    trigger = not trigger
                elif i == 1:
                    zoom = min(256, zoom * 2)
                else:
                    zoom = max(1, zoom // 2)
            last[i] = value
finally:
    mic.deinit()

# Try This
#   1. Whistle as steady a note as you can and count the waves in one 5 ms
#      square. 5 waves in 5 ms is 1000 waves a second: 1000 Hz. What pitch
#      is your whistle?
#   2. Remove "- offset" from the value line. Where does the trace go?
#   3. Say "sss" and then "ooo". Which one looks like a smooth wave and
#      which looks like noise? Which is easier for a computer to recognize?
