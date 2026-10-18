# Chapter 6, Test 05: Opaque versus keyed sprites
# Builds a 16 x 16 cyan disc on a black background with shapes.sprite() and
# sprite_pixel(), then stamps it over a gray gradient two ways: blit_buffer()
# (opaque: you see a black square) and shapes.blit_keyed() (transparent: you
# see only the disc). Needs the display.
#
# PASS: left sprite shows a black square around the disc; right sprite shows
# only the disc. The printout shows keyed blitting sends many more writes.

NAME = "05-sprite-keyed.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import shapes

SIZE = 16

sprite = shapes.sprite(SIZE, SIZE, config.BLACK)
for y in range(SIZE):
    for x in range(SIZE):
        if (x - 8) ** 2 + (y - 8) ** 2 <= 49:
            shapes.sprite_pixel(sprite, SIZE, x, y, config.CYAN)
print("sprite buffer:", len(sprite), "bytes (expect", SIZE * SIZE * 2, ")")

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
for i in range(0, 240, 4):                       # a gray gradient background
    shade = 40 + i // 2
    display.fill_rect(60, 80 + i // 2, 240, 3, config.color565(shade, shade, shade))

start = time.ticks_us()
display.blit_buffer(sprite, 120, 140, SIZE, SIZE)
opaque_ms = time.ticks_diff(time.ticks_us(), start) / 1000

start = time.ticks_us()
shapes.blit_keyed(display, sprite, 220, 140, SIZE, SIZE)
keyed_ms = time.ticks_diff(time.ticks_us(), start) / 1000

display.text(config.SMALL_FONT, "opaque", 100, 165, config.WHITE, config.BLACK)
display.text(config.SMALL_FONT, "keyed", 204, 165, config.WHITE, config.BLACK)
print("opaque blit_buffer: {:.2f} ms".format(opaque_ms))
print("keyed blit_keyed  : {:.2f} ms ({:.1f}x slower)".format(keyed_ms, keyed_ms / opaque_ms))
