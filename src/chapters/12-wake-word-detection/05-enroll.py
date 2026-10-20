# Chapter 12, Test 05: Enroll "Hey Pico"
# Teaches the device what YOUR "Hey Pico" looks like. Hold MODE and say "Hey
# Pico" five times, one recording each, about a second of speaking per
# recording. Each recording is trimmed by voice activity detection, turned
# into a window of 25 frames x 16 band features, mean-subtracted and made length
# 1. The five are averaged into one template, which is made length 1 again.
# Then:
#   UP    save the template to wake_template.bin in flash
#   DOWN  throw it away and enroll again
#   MODE  leave without saving
# Needs the display, the buttons and the microphone. Run Chapter 11's
# 04-calibrate.py first so the level gate matches your room.
#
# The plain-Python FFT is slower than real time, so after each recording the
# device spends a few seconds computing features. It says so on the screen.
#
# PASS: five recordings are accepted, the console prints each one's
# consistency (its score against the finished template) and the average, and
# after UP the file reads back. If an utterance is rejected the screen says why
# (too short, clipped, no speech): just do it again.
# WRITE DOWN: the five consistency numbers. They are the first honest look at
# how repeatable your own "Hey Pico" is.
# The file is written ONLY when you press UP.

NAME = "05-enroll.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import calibration
import config
import detector
import features
import recorder
import ui
import wake
from buttons import Button

COUNT = 5                      # utterances to enroll
OUTLIER_BELOW = 0.5            # a starting value: flag a consistency under this

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

rec = recorder.new_buffer()
extractor = features.Extractor()
cal = calibration.load()
if not cal["calibrated"]:
    print("No calibration.json: using the DEFAULT guesses. Run Chapter 11's 04-calibrate.py first.")

display = config.init_display()
config.set_backlight(True)
led = config.init_led()
pins = config.init_buttons()
mode_button, up_button, down_button = [Button(p) for p in pins]
bar = ui.LevelBar(display, config.CENTER_X - 100, 190, 200, 22, 9, 21)


def say(title, color, line1="", line2="", line3="", line4=""):
    ui.put(display, title, 100, BIG, color, 14)
    ui.put(display, line1, 148, SMALL, DIM, 30)
    ui.put(display, line2, 225, SMALL, DIM, 30)
    ui.put(display, line3, 243, SMALL, DIM, 30)
    ui.put(display, line4, 261, SMALL, DIM, 30)


def wait_for(*buttons):
    while True:
        for b in buttons:
            if b.update() == "release":
                return b
        time.sleep_ms(5)


def record_one(number):
    """One accepted utterance: returns its K x B feature window."""
    while True:
        say("Say it", config.YELLOW, "{} of {}: hold MODE,".format(number, COUNT),
            "say Hey Pico, let go")
        while mode_button.update() != "press":
            time.sleep_ms(5)
        led.value(1)
        say("REC", config.RED, "{} of {}".format(number, COUNT))
        result = recorder.record(rec, mode_button, cal, bar=bar, use_vad=True)
        led.value(0)
        bar.set(0, config.YELLOW)
        problem = None
        if result["start_index"] is None:
            problem = "no speech heard"
        elif result["clipped_frames"] or result["limited"]:
            problem = "too loud: move back"
        window = None
        if problem is None:
            say("working", config.CYAN, "computing features...")
            started = time.ticks_ms()
            window = wake.enrollment_window(extractor, rec, result["frames"], result["start_index"])
            if window is None:
                problem = "too short: keep holding"
            else:
                print("  features for {} frames took {:.1f} s".format(
                    detector.K, time.ticks_diff(time.ticks_ms(), started) / 1000))
        if problem is None:
            print("  accepted: speech starts at frame {}, window starts at frame {}".format(
                result["start_index"], max(0, result["start_index"] - detector.LEAD_FRAMES)))
            return window
        print("  rejected ({}): do it again.".format(problem))
        say("Again", config.YELLOW, problem)
        time.sleep_ms(1200)


try:
    while True:
        display.fill(config.BLACK)
        ui.put(display, "ENROLL", 70, SMALL, config.CYAN, 20)
        bar.frame()
        windows = []
        for number in range(1, COUNT + 1):
            print("Utterance {} of {}: hold MODE, say 'Hey Pico', let go.".format(number, COUNT))
            windows.append(record_one(number))

        template, consistency = detector.build_template(windows)
        average = sum(consistency) / len(consistency)
        print()
        print("Consistency (each utterance against the finished template):")
        for i, c in enumerate(consistency):
            flag = "   <-- low: this one differs from the others" if c < OUTLIER_BELOW else ""
            print("  {}: {:.3f}{}".format(i + 1, c, flag))
        print("  average {:.3f}   lowest {:.3f}".format(average, min(consistency)))

        say("Done", config.GREEN, "consistency {:.2f} avg, {:.2f} low".format(average, min(consistency)),
            "", "", "UP save DOWN again MODE quit")
        choice = wait_for(mode_button, up_button, down_button)
        if choice is mode_button:
            break
        if choice is up_button:
            detector.save_template(template)         # the ONLY flash write in this program
            print("saved wake_template.bin")
            say("Saved", config.GREEN, "wake_template.bin written")
            time.sleep_ms(1500)
            break
finally:
    led.value(0)

check = detector.load_template()
print("wake_template.bin reads back:", "ok" if check is not None else "not found")
