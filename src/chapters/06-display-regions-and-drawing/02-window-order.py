# Chapter 6, Test 02: Pixels fill a window in reading order
# Sends a buffer whose first 120 pixels are red, next 120 green, next 120 blue,
# and so on, into a 120 x 60 window. Because the window fills row by row, you
# see clean horizontal stripes. Then it sends the SAME buffer into a window
# that is one pixel too narrow, to show what a wrong-sized buffer does: the
# stripes shear. Needs the display.
#
# PASS: the top block shows straight red, green, blue stripes. The bottom block
# shows slanted stripes. The sheared block is the "Buffer of the Wrong Size"
# warning made visible.

NAME = "02-window-order.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config

W, H = 120, 60
colors = (config.RED, config.GREEN, config.BLUE)

buf = bytearray(W * H * 2)
for i in range(W * H):
    row = i // W
    color = colors[row % 3]
    buf[i * 2] = color >> 8
    buf[i * 2 + 1] = color & 255

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

config.centered_text(display, config.SMALL_FONT, "width 120 (correct)", 44, config.WHITE)
display.blit_buffer(buf, 120, 62, W, H)

config.centered_text(display, config.SMALL_FONT, "width 119 (wrong)", 210, config.WHITE)
display.blit_buffer(buf, 120, 228, W - 1, H)

print("Top block: window", W, "x", H, "-> straight stripes.")
print("Bottom block: window", W - 1, "x", H, "with the same buffer -> sheared stripes.")
print("The buffer has", len(buf), "bytes; a", W - 1, "x", H, "window needs", (W - 1) * H * 2, ".")
