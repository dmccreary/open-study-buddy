# Test 04: Hello World on the Display
# The smallest program that proves the round GC9B72 display works: start it,
# clear it, draw "Hello World!" in the middle. Only the display is needed.
#
# PASS: the screen goes black, then shows a cyan ring, "Hello World!" in
# big yellow letters, and a small caption underneath. All the letters
# should be inside the ring and none cut off by the bezel.
#
# If the screen stays dark, check the backlight wire (BL, GP7) and power.
# If it lights up white or shows noise, check the SPI wires (SCL GP2, SDA
# GP3) and the control wires (RST GP4, DC GP5, CS GP6).

NAME = "04-hello-world.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import config
import shapes

display = config.init_display()
config.set_backlight(True)

display.fill(config.BLACK)

# The edge of the glass that we can safely draw to.
shapes.ring(display, config.CENTER_X, config.CENTER_Y, config.SAFE_RADIUS,
            config.CYAN, 3)

# The big font is 16 x 32 pixels per letter, so "Hello World!" is
# 12 * 16 = 192 pixels wide. centered_text() works out the left edge.
config.centered_text(display, config.BIG_FONT, "Hello World!",
                     config.CENTER_Y - 16, config.YELLOW)
config.centered_text(display, config.SMALL_FONT, "Study Buddy is alive",
                     config.CENTER_Y + 30, config.WHITE)

print("Drawn: look at the screen.")

# Try This
#   1. Change "Hello World!" to your own name. How long can a name be
#      before it runs off the ring?
#   2. Swap BIG_FONT for SMALL_FONT. How many more letters fit across?
#   3. Change config.YELLOW to config.color565(255, 128, 0) for orange.
