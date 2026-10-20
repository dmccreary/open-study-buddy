# Chapter 18, Capstone 11: Classroom noise monitor
# Shows how loud the room is as QUIET, TALKING, or LOUD with a bar, and prints a
# one-line summary every 60 seconds (seconds spent in each band).
#
# PRIVACY: this program measures LEVEL ONLY. It keeps one smoothed number and
# three counters. It never stores audio, never stores words, and writes no file.
# The screen says so (Chapter 17). Tell the people in the room before you run it.
#
# Needs: display, microphone. The bands are in bits above the room's own
# quiet level, which the program measures first (Quiet please...). The band
# limits are starting values to tune with your class, not facts about classrooms.
#
# PASS: after calibration the word is QUIET and the bar is nearly empty; talking
# near the microphone brings TALKING; shouting or clapping repeatedly brings
# LOUD; going quiet returns to QUIET within a couple of seconds. WRITE DOWN
# the floor and the smoothed level at three classroom activities.

NAME = "11-noise-monitor.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
from detectors import NoiseMonitor, QUIET, TALKING, LOUD
from listen import Mic
from log import Log, INFO

BIG, SMALL = config.BIG_FONT, config.SMALL_FONT
DIM = config.color565(150, 150, 150)
TRACK = config.color565(40, 40, 40)
BAR_W, BAR_H = 200, 22
BAR_X, BAR_Y = config.CENTER_X - BAR_W // 2, 200
COLORS = {QUIET: config.GREEN, TALKING: config.YELLOW, LOUD: config.RED}
SUMMARY_MS = 60000

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
log = Log(level=INFO, ring=20)                       # RAM only: no file


def put(text, y, font, color, width):
    config.centered_text(display, font, text.center(width), y, color)


put("Noise monitor", 70, BIG, config.YELLOW, 14)
put("Level only. No audio saved.", 290, SMALL, DIM, 30)
put("Quiet please...", 130, BIG, config.CYAN, 14)
display.rect(BAR_X - 2, BAR_Y - 2, BAR_W + 4, BAR_H + 4, config.WHITE)
display.fill_rect(BAR_X, BAR_Y, BAR_W, BAR_H, TRACK)

mic = Mic()
mic.open()
try:
    floor, spread = mic.calibrate(50)
    mon = NoiseMonitor(floor)
    log.info("floor %.2f bits", floor)
    put("floor {:.1f} bits".format(floor), 245, SMALL, DIM, 30)
    band = None
    drawn_w = -1
    next_summary = time.ticks_add(time.ticks_ms(), SUMMARY_MS)
    while True:
        new_band = mon.update(mic.bits())
        width = int(BAR_W * mon.fraction())
        if abs(width - drawn_w) >= 2 or new_band != band:     # dirty-region rule
            color = COLORS[new_band]
            display.fill_rect(BAR_X, BAR_Y, width, BAR_H, color)
            display.fill_rect(BAR_X + width, BAR_Y, BAR_W - width, BAR_H, TRACK)
            drawn_w = width
        if new_band != band:
            band = new_band
            put(band, 130, BIG, COLORS[band], 14)
            log.info("band %s", band)
        if time.ticks_diff(time.ticks_ms(), next_summary) >= 0:
            seconds = mon.summary()
            log.info("last minute: quiet %.0f s, talking %.0f s, loud %.0f s",
                     seconds[QUIET], seconds[TALKING], seconds[LOUD])
            print(mic.overrun_summary())
            next_summary = time.ticks_add(next_summary, SUMMARY_MS)
finally:
    mic.close()

# Try This
#   1. Change NoiseMonitor's talking and loud limits (2.0 and 4.0 bits). Which
#      numbers does your class agree on as "too loud for quiet work"?
#   2. Change tau_ms from 1000 to 125. What happens to the bar? Which is easier to watch?
#   3. Ask a classmate: does the screen, by itself, tell you what the device does
#      with the sound? Does the sentence at the bottom help?
