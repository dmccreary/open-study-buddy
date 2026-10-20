# Chapter 17, Test 01: A mute switch you can see and measure
# Watches a mute switch wired between GP9 and GND, and (if the microphone is
# wired) opens it through the Listener and reports what the microphone sends.
# Runs for 30 seconds. Flip the switch a few times while it runs.
#
# Two kinds of mute switch, and this file shows the difference:
#
#   SOFTWARE-VISIBLE mute: a switch from GP9 to GND. Firmware reads the pin and
#   chooses to stop listening. The microphone is still powered, so the mute
#   only works as long as the program is honest. The Listener closes the
#   microphone when the pin reads 0 and the status shows "MIC OFF".
#
#   TRUE HARDWARE mute: a switch in series with the microphone's VDD (3V3)
#   wire. With the switch open the microphone has no power, whatever the
#   program does. Use a two-pole switch: one pole in the VDD wire, the other
#   pole from GP9 to GND so the firmware can still SHOW the state.
#
# Parts: Pico. Optional: a slide switch on GP9 (the other leg to GND), the
# microphone. GP9 is not used by anything in config.py (Chapter 4).
#
# PASS: with the switch off the pin reads 1 and the microphone opens; with the
# switch on the pin reads 0, the microphone closes, and the shell says MIC OFF.
# With a true VDD switch, WRITE DOWN what the microphone sends while its power
# is cut ("spread" below): the chapter does not claim a number.

NAME = "01-mute-switch.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import struct
import time
from machine import Pin

import config
from listening_indicator import Listener, LedIndicator, LISTENING

MUTE_SENSE_PIN = 9          # switch between this pin and GND; reads 0 = muted
RUN_SECONDS = 30
FRAME_BYTES = 2048          # 512 samples, 40 ms

mute_pin = Pin(MUTE_SENSE_PIN, Pin.IN, Pin.PULL_UP)
led = config.init_led()
listener = Listener(config.init_microphone, [LedIndicator(led)], mute_pin)
buf = bytearray(FRAME_BYTES)

print("Flip the mute switch. Pin GP{} reads 1 = not muted, 0 = muted.".format(MUTE_SENSE_PIN))
last_report = time.ticks_ms()
frames = 0
spread = 0
try:
    started = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), started) < RUN_SECONDS * 1000:
        if listener.state != LISTENING:
            if listener.start():
                print("microphone opened (indicator on)")
            else:
                time.sleep_ms(40)           # muted: nothing to read
        if listener.is_open():
            if listener.readinto(buf):
                samples = struct.unpack("<512i", buf)
                spread = (max(samples) - min(samples)) >> config.MIC_SAMPLE_SHIFT
                frames += 1
            else:
                spread = 0
                print("MIC OFF (mute switch on): microphone closed")
        if time.ticks_diff(time.ticks_ms(), last_report) >= 1000:
            last_report = time.ticks_ms()
            print("pin={} state={:<9} frames={:>2} last spread={}".format(
                mute_pin.value(), listener.state, frames, spread))
            frames = 0
finally:
    listener.stop()                         # always close and turn the LED off
print("Done.")
