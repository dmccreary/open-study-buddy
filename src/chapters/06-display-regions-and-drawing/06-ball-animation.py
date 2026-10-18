# Chapter 6, Test 06: Animate by redrawing only what moved
# Slides a 20 x 20 square across the screen by erasing a 4 pixel strip behind
# it and filling a 4 pixel strip in front, instead of redrawing the square.
# Then does the same move by erasing and redrawing the whole box, and compares
# bytes per frame. Needs the display.
#
# PASS: the strip method sends 342 bytes per frame (two 4 x 20 strips: 2 x (160 data
# + 11 command bytes)); the whole-box method sends 1,622 (two 20 x 20 boxes:
# 2 x (800 + 11)). Both look the same on screen.

NAME = "06-ball-animation.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config

BALL = 20
STEP = 4
Y = 90
LEFT, RIGHT = 40, 280


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


def strips():
    x = LEFT
    display.fill_rect(x, Y, BALL, BALL, config.CYAN)
    counter.bytes = 0
    frames = 0
    start = time.ticks_us()
    while x < RIGHT:
        display.fill_rect(x, Y, STEP, BALL, config.BLACK)                  # erase the strip
        x += STEP
        display.fill_rect(x + BALL - STEP, Y, STEP, BALL, config.CYAN)     # new strip
        frames += 1
        time.sleep_ms(10)
    elapsed = time.ticks_diff(time.ticks_us(), start) / 1000 - frames * 10
    return counter.bytes // frames, elapsed / frames


def whole_box():
    x = LEFT
    display.fill_rect(x, Y + 40, BALL, BALL, config.YELLOW)
    counter.bytes = 0
    frames = 0
    start = time.ticks_us()
    while x < RIGHT:
        display.fill_rect(x, Y + 40, BALL, BALL, config.BLACK)             # erase the box
        x += STEP
        display.fill_rect(x, Y + 40, BALL, BALL, config.YELLOW)            # draw it again
        frames += 1
        time.sleep_ms(10)
    elapsed = time.ticks_diff(time.ticks_us(), start) / 1000 - frames * 10
    return counter.bytes // frames, elapsed / frames


display.fill(config.BLACK)
counter.bytes = 0
a = strips()
b = whole_box()
print("strips   : {:>4} bytes/frame, {:.2f} ms/frame of drawing".format(*a))
print("whole box: {:>4} bytes/frame, {:.2f} ms/frame of drawing".format(*b))
print("PASS" if a[0] < b[0] else "CHECK: the strip method should send fewer bytes")
