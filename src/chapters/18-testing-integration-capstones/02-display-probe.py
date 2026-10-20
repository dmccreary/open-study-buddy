# Chapter 18, Probe 02: Display
# Checks the display one layer at a time and tells you which layer failed:
#   1. the SPI rate you really got (the rate you ask for is not always the rate you get)
#   2. backlight on and off (BL on GP7)
#   3. full-screen fills in red, green, and blue, timed
#   4. the visible-area test: a green ring at SAFE_RADIUS, a red ring at the glass edge
# Then it asks you what you saw. Needs only the display.
#
# PASS: you see three solid colors, then the rings, and answer UP (yes). If you
# answer DOWN, the probe prints what to check, in order.

NAME = "02-display-probe.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin, SPI

import checks
import config
import shapes

spi = SPI(config.SPI_ID, baudrate=config.BAUDRATE,
          sck=Pin(config.SCK_PIN), mosi=Pin(config.MOSI_PIN))
print("1. SPI as created :", spi)
print("   you asked for  :", config.BAUDRATE, "Hz")

display = config.init_display()
print("2. backlight off for 1 s ...")
config.set_backlight(False)
time.sleep_ms(1000)
config.set_backlight(True)
print("   backlight on")

print("3. full-screen fills (best case 86.4 ms at 24 MHz; Chapter 5 measured 129 ms)")
for name, color in (("red", config.RED), ("green", config.GREEN), ("blue", config.BLUE)):
    t0 = time.ticks_ms()
    display.fill(color)
    print("   {:<5} fill took {} ms".format(name, time.ticks_diff(time.ticks_ms(), t0)))
    time.sleep_ms(700)

print("4. visible-area test")
display.fill(config.BLACK)
shapes.ring(display, config.CENTER_X, config.CENTER_Y, config.RADIUS, config.RED, 2)
shapes.ring(display, config.CENTER_X, config.CENTER_Y, config.SAFE_RADIUS, config.GREEN, 2)
config.centered_text(display, config.BIG_FONT, "DISPLAY".center(14), 150, config.WHITE)

answer = checks.ask_yes_no(config, display, "Red, green, blue, then rings?")
print()
if answer:
    print("RESULT: PASS (a person saw all four stages)")
else:
    print("RESULT: {}".format("FAIL" if answer is False else "ASK (nobody answered)"))
    print("Check, in this order:")
    print("  - Is the screen lit at all? No light: BL to GP7, VCC to 3V3, GND (Chapter 4).")
    print("  - Lit but black or noise: SCL GP2, SDA GP3, RST GP4, DC GP5, CS GP6.")
    print("  - Speckled or torn: wires too long for the SPI rate; set BAUDRATE to 12_000_000.")
    print("  - Part of the picture missing: the corners are hidden; stay inside SAFE_RADIUS (168).")
    print("  - Picture turned or mirrored: the rotation argument in config.init_display().")
