# Chapter 12, Test 08: Measure false rejects and false accepts
# A guided measurement. It asks you to say "Hey Pico" 20 times (each should be
# detected) and then 20 DIFFERENT other phrases, coughs, claps or sentences
# (none should be). For every attempt it records the best score in that
# attempt. At the end it sweeps the threshold from 0.50 to 0.95 and prints how
# many "Hey Pico" attempts would have been missed (false rejects) and how many
# other attempts would have been accepted (false accepts) at each setting.
# Needs the display, the buttons and the microphone, plus wake_template.bin.
#
# THIS IS THE MEASUREMENT BEHIND THE CHAPTER'S HONEST-LIMITS MESSAGE. The chapter
# gives no real accuracy numbers because none exist yet; this script produces them.
# Vary what you test: set SPEAKER and PACE below before each run, and run it
# again for a different speaker, a faster pace, a slower pace, a noisy room.
#
# Every attempt prints a line  RESULT,<kind>,<best score>,<speaker>,<pace>  that
# you can save to a file and feed to tools/threshold-sweep.py on your computer.
#
# PASS: both lists are filled and the table prints. WRITE DOWN: the table, the
# SPEAKER, the PACE, the room, and the distance. Also write down how much
# non-"Hey Pico" audio you tested (the script totals the seconds).

NAME = "08-threshold-sweep.py"
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

SPEAKER = "me"                 # EDIT: who is speaking this run
PACE = "normal"                # EDIT: "normal", "fast" or "slow"
WAKE_ATTEMPTS = 20
OTHER_ATTEMPTS = 20
THRESHOLDS = (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)

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


def say(title, color, line1="", line2=""):
    ui.put(display, title, 100, BIG, color, 14)
    ui.put(display, line1, 148, SMALL, DIM, 30)
    ui.put(display, line2, 225, SMALL, DIM, 30)


def one_attempt(kind, number, total):
    """Record one attempt and return (best score, seconds recorded)."""
    prompt = "say Hey Pico" if kind == "wake" else "say anything else"
    say("{} {}/{}".format(kind, number, total), config.YELLOW, "hold MODE, " + prompt)
    while mode_button.update() != "press":
        time.sleep_ms(5)
    led.value(1)
    say("REC", config.RED, "{} {}/{}".format(kind, number, total))
    result = recorder.record(rec, mode_button, cal)
    led.value(0)
    say("scoring", config.CYAN, "{} frames".format(result["frames"]))
    scores = wake.score_recording(extractor, rec, result["frames"], result["bits"], template, cal)
    best, _ = wake.best_score(scores)
    return best, result["seconds"]


display.fill(config.BLACK)
ui.put(display, "THRESHOLD SWEEP", 70, SMALL, config.CYAN, 20)
wake_scores = []
other_scores = []
other_seconds = 0.0
print("Speaker {}, pace {}.".format(SPEAKER, PACE))
for n in range(1, WAKE_ATTEMPTS + 1):
    best, seconds = one_attempt("wake", n, WAKE_ATTEMPTS)
    wake_scores.append(best)
    print("RESULT,wake,{:.3f},{},{}".format(best, SPEAKER, PACE))
for n in range(1, OTHER_ATTEMPTS + 1):
    best, seconds = one_attempt("other", n, OTHER_ATTEMPTS)
    other_scores.append(best)
    other_seconds += seconds
    print("RESULT,other,{:.3f},{},{}".format(best, SPEAKER, PACE))

print()
print("Speaker {}, pace {}.  {} wake attempts, {} other attempts ({:.0f} s of other audio).".format(
    SPEAKER, PACE, len(wake_scores), len(other_scores), other_seconds))
print("{:>9} {:>14} {:>14}".format("threshold", "false rejects", "false accepts"))
for t in THRESHOLDS:
    fr = sum([1 for s in wake_scores if s < t])
    fa = sum([1 for s in other_scores if s >= t])
    print("{:>9.2f} {:>8} of {:<3} {:>8} of {:<3}".format(
        t, fr, len(wake_scores), fa, len(other_scores)))
print()
print("A false accept per attempt is not a rate per hour. If {:.0f} s of other audio "
      "gave F false accepts, that is F / {:.4f} h.".format(other_seconds, other_seconds / 3600))
say("Done", config.GREEN, "see the console table")
