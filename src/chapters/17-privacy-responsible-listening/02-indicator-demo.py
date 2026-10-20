# Chapter 17, Test 02: Hold MODE to listen, and the device says so
# The first version of the listening indicator you can SEE. Hold MODE and the
# microphone opens through the Listener: the onboard LED lights and the status
# bar shows LISTENING. Let go and both go off. If a mute switch is wired to GP9
# (see test 01), flipping it on shows "MIC OFF" and the microphone stays closed.
#
# Parts: display, MODE button, microphone. Optional: the GP9 mute switch.
#
# PASS: the LED and the status bar change the moment you press MODE, and go
# back the moment you let go, every time. Try to catch the indicator being wrong.
# Then run 03-indicator-test.py to prove why it cannot be.
# Press Stop (Ctrl-C) to end it; the microphone is closed on the way out.

NAME = "02-indicator-demo.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

import config
from listening_indicator import Listener, LedIndicator, StatusBarIndicator, OFF

MUTE_SENSE_PIN = 9

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "Hold MODE", 120, config.YELLOW)
config.centered_text(display, config.SMALL_FONT, "to talk (push-to-talk)", 165,
                     config.GRAY)

mode = config.init_buttons()[0]
mute_pin = Pin(MUTE_SENSE_PIN, Pin.IN, Pin.PULL_UP)
led = config.init_led()
listener = Listener(config.init_microphone,
                    [LedIndicator(led), StatusBarIndicator(display, config)],
                    mute_pin)
buf = bytearray(2048)
shown = None                                        # last state we printed
try:
    while True:
        if mode.value() == 0:                       # MODE is held
            if not listener.is_open():
                listener.start()                    # may stay muted
            if listener.is_open():
                listener.readinto(buf)              # blocks 40 ms per frame
            else:
                time.sleep_ms(40)                   # muted: nothing to read
        elif listener.is_open() or listener.state != OFF:
            listener.stop()
            time.sleep_ms(5)
        else:
            time.sleep_ms(5)
        if listener.state != shown:
            shown = listener.state
            print("indicator ->", shown)
finally:
    listener.stop()
