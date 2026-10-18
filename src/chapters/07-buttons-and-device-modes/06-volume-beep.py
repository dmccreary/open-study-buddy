# Chapter 7, Test 06: Volume control with feedback
# UP and DOWN change the volume in steps of 10 (0 to 100). Each change updates
# the status bar and plays a short beep at the NEW volume, so you hear what you
# set. Hold MODE for one second to quit. Needs the display, the three buttons,
# and the amplifier and speaker.
#
# PASS: each tap of UP makes the beep louder and the number bigger; at 100 and
# at 0 the number stops. Keep the speaker away from your ear at high volumes.

NAME = "06-volume-beep.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import array
import math
import time
from machine import I2S, Pin

import config
from buttons import Button

RATE = 16000
IBUF = 8192
N = 256
SINE = array.array("h", [int(32767 * math.sin(2 * math.pi * i / N)) for i in range(N)])

STATUS = (120, 30, 120, 20)          # the status-bar region from Chapter 6


def tone(freq, ms, volume):
    count = RATE * ms // 1000
    out = array.array("h", [0] * count)
    step = freq * N / RATE
    phase = 0.0
    fade = RATE // 100
    for i in range(count):
        edge = min(1.0, i / fade, (count - i) / fade)
        out[i] = int(SINE[int(phase) % N] * volume // 100 * edge)
        phase += step
    return out


display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
mode, up, down = config.init_buttons()
buttons = (("mode", Button(mode)), ("up", Button(up)), ("down", Button(down)))
config.set_gain()
audio = I2S(config.I2S_SPEAKER_ID,
            sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
            sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
            format=I2S.MONO, rate=RATE, ibuf=IBUF)

volume = config.VOLUME


def show():
    x, y, w, h = STATUS
    text = "Vol {}".format(volume).center(w // 8)
    display.text(config.SMALL_FONT, text, x, y + 2, config.YELLOW, config.BLACK)
    bar = w * volume // 100
    display.fill_rect(x, y + h - 4, bar, 4, config.GREEN)
    display.fill_rect(x + bar, y + h - 4, w - bar, 4, config.GRAY)


def beep():
    audio.write(tone(660, 120, volume))
    audio.write(bytes(RATE * 60 // 1000 * 2))


print("UP / DOWN change the volume. Hold MODE for 1 s to quit.")
show()
beep()
try:
    running = True
    while running:
        for name, button in buttons:
            event = button.update()
            if name == "mode" and event == "long":
                running = False
            elif event == "press" and name != "mode":
                volume = max(0, min(100, volume + (10 if name == "up" else -10)))
                print("volume", volume)
                show()
                beep()
        time.sleep_ms(5)
finally:
    audio.write(bytes(RATE * 100 // 1000 * 2))
    time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)
    audio.deinit()
    print("Stopped. Final volume", volume)
