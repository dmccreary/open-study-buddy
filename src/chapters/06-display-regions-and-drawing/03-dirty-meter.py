# Chapter 6, Test 03: Dirty regions save bytes
# Drives a 200 x 22 level meter with a moving value, three ways, for 150 frames
# each, and counts the SPI bytes and time per frame:
#   A  redraw the whole meter (bar + empty track) every frame
#   B  test 06's rule: redraw the bar and track only when the width changed by
#      2 pixels or more
#   C  draw only the slice that changed
# No microphone is needed; a smooth sine wave drives the meter. Needs the display.
#
# PASS: A sends 8,800+ bytes every frame, B sends fewer, C sends the fewest.
# Write down the bytes per frame for A and C.

NAME = "03-dirty-meter.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time

import config

WIDTH, HEIGHT = 200, 22
X = config.CENTER_X - WIDTH // 2
Y = 190
FRAMES = 150
TRACK = config.color565(40, 40, 40)
BAR = config.GREEN


class CountingSPI:
    def __init__(self, spi):
        self.spi = spi
        self.bytes = 0

    def write(self, data):
        self.bytes += len(data)
        return self.spi.write(data)


display = config.init_display()
config.set_backlight(True)
counter = CountingSPI(display.spi)
display.spi = counter


def value(frame):
    """A smooth 0..200 pattern: slow swells with a little wobble."""
    return int(100 + 80 * math.sin(frame / 12) + 20 * math.sin(frame / 3))


def clear():
    display.fill(config.BLACK)
    display.fill_rect(X, Y, WIDTH, HEIGHT, TRACK)


def run(label, draw):
    clear()
    counter.bytes = 0
    shown = [0]
    start = time.ticks_us()
    for frame in range(FRAMES):
        draw(max(0, min(WIDTH, value(frame))), shown)
    elapsed = time.ticks_diff(time.ticks_us(), start) / 1000
    print("{}  {:>9,} bytes total  {:>7,} bytes/frame  {:>6.1f} ms/frame".format(
        label, counter.bytes, counter.bytes // FRAMES, elapsed / FRAMES))
    return counter.bytes


def draw_a(width, shown):
    display.fill_rect(X, Y, width, HEIGHT, BAR)
    display.fill_rect(X + width, Y, WIDTH - width, HEIGHT, TRACK)
    shown[0] = width


def draw_b(width, shown):
    if abs(width - shown[0]) >= 2:
        draw_a(width, shown)


def draw_c(width, shown):
    old = shown[0]
    if width > old:
        display.fill_rect(X + old, Y, width - old, HEIGHT, BAR)
    elif width < old:
        display.fill_rect(X + width, Y, old - width, HEIGHT, TRACK)
    shown[0] = width


print()
a = run("A  redraw everything ", draw_a)
b = run("B  test 06's rule    ", draw_b)
c = run("C  changed slice only", draw_c)
print()
print("PASS" if a > b > c else "CHECK: expected A > B > C")
print("C sent {:.0f}% of what A sent.".format(100 * c / a))
