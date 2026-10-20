# Chapter 12, Test 09: The live wake-word detector
# Listens to the microphone one 40 ms frame at a time, scores a rolling window
# of the last 25 frames against your "Hey Pico" template, and when the score
# reaches the threshold it closes the microphone, plays a short confirmation
# beep, empties the window, and starts a cooldown. Needs the display, the
# buttons, the microphone and the speaker, plus wake_template.bin from 05.
#
# ALWAYS-ON LISTENING IS AN ADVANCED OPTION THAT NEEDS APPROVAL FIRST
# (Chapter 17). The default of this program is PUSH-TO-TALK: it listens ONLY
# while you hold MODE, so you can test the detector without leaving a
# microphone open. ALWAYS_ON_APPROVED below stays False unless a parent,
# teacher or school has approved always-on use for this device. A flag in a
# file is not an approval: follow Chapter 17's process, and keep the on-screen
# "ALWAYS ON" label and the LED, which show that the microphone is open.
#
# THIS LOOP MUST FINISH EACH FRAME IN 40 MS. With the plain-Python FFT it will
# not: it will lose audio and say how often ("overruns"). Plug in Chapter 10's
# fast transform (features.Extractor(spectrum_fn=...)) before relying on it; use
# 07-score-trace.py to judge the detector meanwhile.
#
# PASS: with a fast transform, holding MODE and saying "Hey Pico" shows the
# score rising, the beep plays, and the status says "Hey Pico!"; ordinary
# talk does not trigger it; the summary reports 0 overruns. WRITE DOWN: the
# frame time and the overruns.

NAME = "09-live-detector.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from array import array
from machine import I2S, Pin

import calibration
import config
import detector
import features
import levels
import ui
import wake
from buttons import Button

ALWAYS_ON_APPROVED = False     # leave False unless Chapter 17's approval is in place
THRESHOLD = detector.THRESHOLD
SKIP_FRAMES = 3                # the microphone's first moments after it opens
BEEP_HZ = 880
BEEP_MS = 120
IBUF = 8192
RATE = config.MIC_SAMPLE_RATE

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

cal, template = wake.load_setup()
if template is None:
    raise SystemExit("Run 05-enroll.py first.")
extractor = features.Extractor()                 # spectrum_fn=your_fast_function
gate = calibration.gate_from(cal)
det = detector.Detector(template, gate, threshold=THRESHOLD)

# the confirmation beep: made once, 880 Hz for 120 ms with 10 ms fades, quiet
volume = min(config.VOLUME, 30) / 100
beep = bytearray(RATE * BEEP_MS // 1000 * 2)
fade = RATE // 100
for i in range(len(beep) // 2):
    f = min(1.0, i / fade, (len(beep) // 2 - i) / fade)
    struct.pack_into("<h", beep, i * 2,
                     int(32767 * volume * f * math.sin(2 * math.pi * BEEP_HZ * i / RATE)))

display = config.init_display()
config.set_backlight(True)
led = config.init_led()
config.set_gain()
mode_button = Button(config.init_buttons()[0])
score_bar = ui.LevelBar(display, config.CENTER_X - 100, 190, 200, 22, 0.0, 1.0)

frame = bytearray(levels.FRAME_BYTES)
feats = array("f", [0.0] * features.BANDS)


def play_beep():
    """The microphone is CLOSED while this runs (the self-hearing rule)."""
    speaker = I2S(config.I2S_SPEAKER_ID,
                  sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
                  sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                  format=I2S.MONO, rate=RATE, ibuf=IBUF)
    try:
        speaker.write(beep)
        speaker.write(bytes(RATE * 100 // 1000 * 2))          # a quiet tail
        time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)         # let the buffer drain
    finally:
        speaker.deinit()


def text(title, color, line1="", line2=""):
    ui.put(display, title, 100, BIG, color, 14)
    ui.put(display, line1, 148, SMALL, DIM, 30)
    ui.put(display, line2, 225, SMALL, DIM, 30)


display.fill(config.BLACK)
ui.put(display, "WAKE WORD", 70, SMALL, config.CYAN, 20)
score_bar.frame()
score_bar.tick(THRESHOLD, config.YELLOW)
stats = {"frames": 0, "overruns": 0, "detections": 0, "work_max": 0}


def listen(keep_going):
    """Listen until keep_going() is False. Returns after closing the microphone."""
    mic = config.init_microphone()
    led.value(1)                                  # the microphone is open
    try:
        for _ in range(SKIP_FRAMES):
            mic.readinto(frame)
        shown_fill = -1
        while keep_going():
            mic.readinto(frame)
            t0 = time.ticks_us()
            bits = levels.frame_stats(frame)[0]
            extractor.extract32(frame, feats)
            score, fired = det.update(feats, bits)
            stats["frames"] += 1

            fill = det.window.fill_percent()
            value = 0.0 if score is None else max(0.0, score)
            score_bar.set(value, config.GREEN if gate.is_open else config.YELLOW)
            if fill != shown_fill and stats["frames"] % 5 == 0:
                shown_fill = fill
                ui.put(display, "window {}%  score {}".format(
                    fill, "-" if score is None else "{:.2f}".format(score)), 225, SMALL, DIM, 30)

            used = time.ticks_diff(time.ticks_us(), t0)
            stats["work_max"] = max(stats["work_max"], used)
            if used > levels.FRAME_MS * 1000:
                stats["overruns"] += 1
            if fired:
                stats["detections"] += 1
                print("Hey Pico! score {:.3f} (detection {})".format(score, stats["detections"]))
                return True
    finally:
        mic.deinit()
        led.value(0)
    return False


def on_detection():
    text("Hey Pico!", config.GREEN, "score above {:.2f}".format(THRESHOLD))
    play_beep()                                   # microphone is closed here
    det.reset()                                   # window back to 0% full
    det.start_cooldown()                          # and ignore the next 2 seconds
    time.sleep_ms(300)


try:
    if ALWAYS_ON_APPROVED:
        text("ALWAYS ON", config.RED, "the microphone is open")
        print("ALWAYS ON (approved). Stop with Ctrl-C.")
        while True:
            if listen(lambda: True):
                on_detection()
                text("ALWAYS ON", config.RED, "the microphone is open")
    else:
        text("Hold MODE", config.YELLOW, "to listen for Hey Pico")
        print("Push-to-talk test: hold MODE and say 'Hey Pico'. Ctrl-C to stop.")
        while True:
            if mode_button.update() == "press":
                det.reset()
                text("LISTENING", config.RED, "hold MODE")
                if listen(lambda: (mode_button.update() != "release")):
                    on_detection()
                    while mode_button.down:       # wait for the button to be let go
                        mode_button.update()
                        time.sleep_ms(5)
                text("Hold MODE", config.YELLOW, "to listen for Hey Pico")
            time.sleep_ms(5)
finally:
    print()
    print("Frames {}, detections {}, slowest frame {:.1f} ms of {} ms, overruns {}.".format(
        stats["frames"], stats["detections"], stats["work_max"] / 1000,
        levels.FRAME_MS, stats["overruns"]))
    if stats["overruns"]:
        print("OVERRUNS: this loop is too slow for the microphone. Use Chapter 10's fast transform.")
