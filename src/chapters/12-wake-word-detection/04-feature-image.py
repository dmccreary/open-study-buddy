# Chapter 12, Test 04: See the features of "Hey Pico" as a picture
# Hold MODE and say "Hey Pico" (about 1.6 seconds), let go, and the screen shows
# 40 frames x 16 bands as a small heat map after mean subtraction: one column
# per 40 ms frame, one row per band (high frequencies at the top). Blue is
# below the band's own average, red is above. Needs the display, the buttons
# and the microphone.
#
# It takes a while to appear, because the plain-Python FFT is slower than real
# time: the console prints the progress and the time per frame.
#
# PASS: the picture appears and looks the same each time you say the phrase,
# with the red patches in about the same places. Say something else and they move.
# WRITE DOWN: seconds per frame (the budget is 0.040).

NAME = "04-feature-image.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import calibration
import config
import detector
import features
import levels
import recorder
import ui
import wake
from buttons import Button

FRAMES = 40                    # 1.6 seconds
CELL = 6                       # pixels per cell
IMAGE_W = FRAMES * CELL        # 240
IMAGE_H = features.BANDS * CELL    # 96
X0 = config.CENTER_X - IMAGE_W // 2
Y0 = 128

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

rec = recorder.new_buffer()
extractor = features.Extractor()
cal = calibration.load()

display = config.init_display()
config.set_backlight(True)
led = config.init_led()
mode_button = Button(config.init_buttons()[0])


def heat(value):
    """Blue below the average, red above, dark near it. value is about -3 to +3."""
    f = max(-1.0, min(1.0, value / 3.0))
    if f >= 0:
        return config.color565(int(255 * f), 0, 0)
    return config.color565(0, 0, int(255 * -f))


def draw(image):
    """image: FRAMES x BANDS features (frame by frame), mean-subtracted already."""
    display.fill_rect(X0, Y0, IMAGE_W, IMAGE_H, config.BLACK)
    for i in range(FRAMES):
        for j in range(features.BANDS):
            y = Y0 + (features.BANDS - 1 - j) * CELL      # band 15 at the top
            display.fill_rect(X0 + i * CELL, y, CELL, CELL, heat(image[i * features.BANDS + j]))


display.fill(config.BLACK)
ui.put(display, "FEATURE IMAGE", 70, SMALL, config.CYAN, 20)
ui.put(display, "Hold MODE, say Hey Pico", 100, SMALL, config.YELLOW, 30)
print("Hold MODE and say 'Hey Pico', then let go.")
while True:
    if mode_button.update() != "press":
        time.sleep_ms(5)
        continue
    led.value(1)
    ui.put(display, "REC", 100, BIG, config.RED, 14)
    result = recorder.record(rec, mode_button, cal)
    led.value(0)
    if result["frames"] < FRAMES:
        ui.put(display, "Hold longer (1.6 s)", 100, SMALL, config.YELLOW, 30)
        print("Only {} frames; hold MODE for 1.6 s ({} frames).".format(result["frames"], FRAMES))
        continue
    ui.put(display, "working...", 100, SMALL, DIM, 30)
    started = time.ticks_ms()
    image = wake.features_for(extractor, rec, 0, FRAMES)
    seconds = time.ticks_diff(time.ticks_ms(), started) / 1000
    detector.mean_subtract(image, FRAMES, features.BANDS)
    draw(image)
    ui.put(display, "{:.1f} s for {} frames".format(seconds, FRAMES), 100, SMALL, DIM, 30)
    print("Features of {} frames took {:.2f} s = {:.3f} s per frame (budget 0.040).".format(
        FRAMES, seconds, seconds / FRAMES))
    print("Hold MODE and try again, or say something else to compare.")
