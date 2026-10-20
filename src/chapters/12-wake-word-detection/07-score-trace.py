# Chapter 12, Test 07: Record, then score: the score trace
# Hold MODE and say something (up to 6 seconds). When you let go, the detector
# is slid across the recording one frame at a time and the score of every
# frame is printed as a CSV line and drawn as a small graph with the threshold
# line. This is how you SEE what the detector thinks: where the score rises as
# you say "Hey Pico", how high it gets, and what other phrases do.
# Needs the display, the buttons and the microphone, plus wake_template.bin
# from 05-enroll.py.
#
# It scores AFTER the recording, so it works even though the plain-Python FFT
# is slower than real time. The console prints the time it took.
#
# PASS: for "Hey Pico" the best score is clearly higher than for a different
# phrase, a cough, or a tap on the table. The CSV (frame,bits,fill,score)
# can be pasted into a spreadsheet. A score of "-" means the frame was not
# scored: the window was not full, or too few of its frames were loud.
# WRITE DOWN: best score for "Hey Pico" (5 tries), and for 5 other phrases.

NAME = "07-score-trace.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import detector
import features
import levels
import recorder
import ui
import wake
from buttons import Button

PLOT_X = config.CENTER_X - 75          # 150 frames, one pixel wide each
PLOT_Y = 195
PLOT_H = 50

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

rec = recorder.new_buffer()
extractor = features.Extractor()
cal, template = wake.load_setup()
if template is None:
    raise SystemExit("Run 05-enroll.py first.")

display = config.init_display()
config.set_backlight(True)
led = config.init_led()
mode_button = Button(config.init_buttons()[0])


def plot(scores):
    display.fill_rect(PLOT_X, PLOT_Y, 150, PLOT_H, config.color565(30, 30, 30))
    line_y = PLOT_Y + PLOT_H - int(PLOT_H * detector.THRESHOLD)
    display.hline(PLOT_X, line_y, 150, config.YELLOW)
    for n in range(len(scores)):
        if scores[n] is not None:
            height = max(0, min(PLOT_H - 1, int(PLOT_H * scores[n])))
            display.fill_rect(PLOT_X + n, PLOT_Y + PLOT_H - height, 1, height + 1, config.GREEN)


display.fill(config.BLACK)
ui.put(display, "SCORE TRACE", 70, SMALL, config.CYAN, 20)
ui.put(display, "Hold MODE, say a phrase", 100, SMALL, config.YELLOW, 30)
print("Hold MODE, say a phrase, let go. Threshold {}.".format(detector.THRESHOLD))
while True:
    if mode_button.update() != "press":
        time.sleep_ms(5)
        continue
    led.value(1)
    ui.put(display, "REC", 100, BIG, config.RED, 14)
    result = recorder.record(rec, mode_button, cal)
    led.value(0)
    frames = result["frames"]
    ui.put(display, "scoring {} frames".format(frames), 100, SMALL, DIM, 30)
    started = time.ticks_ms()
    scores = wake.score_recording(extractor, rec, frames, result["bits"], template, cal)
    seconds = time.ticks_diff(time.ticks_ms(), started) / 1000
    best, where = wake.best_score(scores)

    print()
    print("frame,bits,fill,score")
    for n in range(frames):
        fill = min(100, 100 * (n + 1) // detector.K)
        s = scores[n]
        print("{},{:.2f},{},{}".format(n, result["bits"][n], fill,
                                      "-" if s is None else "{:.3f}".format(s)))
    print()
    if where < 0:
        print("Nothing was scored: the recording was shorter than {} frames, or the gate never opened "
              "for {} frames of a window.".format(detector.K, detector.MIN_ACTIVE_FRAMES))
        ui.put(display, "not scored", 100, BIG, config.YELLOW, 14)
    else:
        verdict = "WOULD FIRE" if best >= detector.THRESHOLD else "below threshold"
        print("Best score {:.3f} at frame {} ({} ms into the recording): {}.".format(
            best, where, where * levels.FRAME_MS, verdict))
        ui.put(display, "best {:.2f}".format(best), 100, BIG,
               config.GREEN if best >= detector.THRESHOLD else config.YELLOW, 14)
    print("Scoring {} frames took {:.1f} s ({:.3f} s per frame; budget 0.040).".format(
        frames, seconds, seconds / max(1, frames)))
    plot(scores)
