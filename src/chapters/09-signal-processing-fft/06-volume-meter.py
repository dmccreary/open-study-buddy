# Chapter 9, Test 06: A volume meter on the round screen
# Reads 40 ms microphone frames, finds the RMS loudness (no FFT needed), turns
# it into dBFS (decibels relative to full scale), and draws a bar plus a number.
# The bar is redrawn by changed slice only (the Chapter 6 idea): when the level
# rises, only the new part is painted; when it falls, only the part that
# vanished is erased. Needs the display and the microphone.
#
# PASS: the bar sits low in a quiet room and swings right when you clap or
# talk; the number reads about -55 to -60 dBFS in a quiet room (your room
# will differ); the serial summary shows the work per frame well under 40 ms
# and zero skipped frames.

NAME = "06-volume-meter.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import dsp

N = config.FFT_SIZE
FRAME_US = N * 1_000_000 // config.MIC_SAMPLE_RATE
FULL_SCALE = 1 << (config.MIC_SAMPLE_BITS - config.MIC_SAMPLE_SHIFT - 1)   # 2^23
FRAMES = 500                      # 20 seconds
METER_MIN_DBFS = -70              # left end of the bar (tune for your room)
METER_MAX_DBFS = -20              # right end of the bar
METER_WIDTH = 200
METER_HEIGHT = 26
METER_X = config.CENTER_X - METER_WIDTH // 2
METER_Y = 170
TRACK = config.color565(40, 40, 40)
DIM = config.color565(150, 150, 150)

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "Volume", 70, config.YELLOW)
config.centered_text(display, config.SMALL_FONT, "RMS loudness in dBFS", 112, DIM)
display.rect(METER_X - 2, METER_Y - 2, METER_WIDTH + 4, METER_HEIGHT + 4, config.WHITE)
display.fill_rect(METER_X, METER_Y, METER_WIDTH, METER_HEIGHT, TRACK)
display.text(config.SMALL_FONT, "{:d}".format(METER_MIN_DBFS), METER_X, 204, DIM, config.BLACK)
display.text(config.SMALL_FONT, "{:d}".format(METER_MAX_DBFS), METER_X + METER_WIDTH - 24, 204,
             DIM, config.BLACK)

shown_width = 0
shown_text = None


def bar_color(width):
    fraction = width / METER_WIDTH
    return config.GREEN if fraction < 0.6 else (config.YELLOW if fraction < 0.85 else config.RED)


def draw_bar(width):
    """Paint only the slice of the bar that changed since the last frame.
    (Crossing a color zone repaints the whole bar so the colors stay right.)"""
    global shown_width
    old = shown_width
    if width == old:
        return
    if bar_color(width) != bar_color(old):
        display.fill_rect(METER_X, METER_Y, width, METER_HEIGHT, bar_color(width))
        display.fill_rect(METER_X + width, METER_Y, METER_WIDTH - width, METER_HEIGHT, TRACK)
    elif width > old:
        display.fill_rect(METER_X + old, METER_Y, width - old, METER_HEIGHT, bar_color(width))
    else:
        display.fill_rect(METER_X + width, METER_Y, old - width, METER_HEIGHT, TRACK)
    shown_width = width


mic = config.init_microphone()
buf = bytearray(N * 4)
try:
    for _ in range(8):
        mic.readinto(buf)
    work_total = 0
    worst = 0
    late = 0
    for frame in range(FRAMES):
        mic.readinto(buf)
        started = time.ticks_us()
        dc, rms = dsp.frame_rms(buf, N, config.MIC_SAMPLE_SHIFT)
        dbfs = dsp.to_db(rms, FULL_SCALE)
        width = METER_WIDTH * dsp.scale(dbfs, METER_MIN_DBFS, METER_MAX_DBFS, 100) // 100
        draw_bar(width)
        text = "{:+.0f} dBFS".format(dbfs)
        if text != shown_text:                           # redraw the number only when it changes
            config.centered_text(display, config.BIG_FONT, text.center(10), 235, config.WHITE)
            shown_text = text
        used = time.ticks_diff(time.ticks_us(), started)
        work_total += used
        worst = max(worst, used)
        if used > FRAME_US:
            late += 1
        if frame % 25 == 0:
            print("{:>4} dc {:>7} rms {:>9.1f} {:>6.1f} dBFS  work {:>5.1f} ms".format(
                frame, dc, rms, dbfs, used / 1000))
    print()
    print("work per frame: mean {:.1f} ms, worst {:.1f} ms, budget {} ms, frames over budget: {}".format(
        work_total / FRAMES / 1000, worst / 1000, FRAME_US // 1000, late))
finally:
    mic.deinit()
print("Done.")
