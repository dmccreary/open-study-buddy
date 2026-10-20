# Chapter 11, Test 04: Calibrate the microphone
# A guided calibration on the display. Press MODE to start, stay quiet for 4
# seconds, then say "Hey Pico, what is due tomorrow?" for 4 seconds. The screen
# shows the noise floor, speech level, SNR, and the gate levels it chose. Then:
#   UP    save the result to calibration.json in flash
#   DOWN  throw it away and measure again
#   MODE  leave without saving
# Needs the display, the three buttons, and the microphone.
#
# PASS: a result screen with numbers, and after UP the console says
# "saved calibration.json" and the file reads back the same values. If the
# screen says "CLIPPING", "TOO NOISY", or "SNR LOW", it tells you what to try.
# The file is written ONLY when you press UP (flash can be rewritten a limited
# number of times; never save from a loop).
#
# The level bar shows the live loudness while you calibrate. Nothing is drawn
# on the screen except the bar and a few lines of text, and the bar redraws only
# the columns that changed.

NAME = "04-calibrate.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import calibration
import config
import levels
import ui
from buttons import Button

DISTANCE_CM = 30              # EDIT: your mouth to the microphone, in cm
QUIET_FRAMES = 100            # 4 seconds
SPEECH_FRAMES = 100           # 4 seconds
SETTLE_FRAMES = 8

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

display = config.init_display()
config.set_backlight(True)
led = config.init_led()
config.set_gain()
pins = config.init_buttons()
mode_button, up_button, down_button = [Button(p) for p in pins]

bar = ui.LevelBar(display, config.CENTER_X - 100, 190, 200, 22, 9, 21)


def say(title, color, line1="", line2="", line3="", line4=""):
    """Redraw the text regions (not the bar). Lines are at most 30 characters."""
    ui.put(display, title, 100, BIG, color, 14)
    ui.put(display, line1, 148, SMALL, DIM, 30)
    ui.put(display, line2, 225, SMALL, DIM, 30)
    ui.put(display, line3, 243, SMALL, DIM, 30)
    ui.put(display, line4, 261, SMALL, DIM, 30)


def wait_for(*buttons):
    """Block until one of the buttons is released. Returns that button."""
    while True:
        for b in buttons:
            if b.update() == "release":
                return b
        time.sleep_ms(5)


def collect(mic, frame, count, color):
    """Read count frames, show each on the bar. Returns (bits, dev_peak, clipped_frames)."""
    bits_list = []
    peak = 0
    clipped_frames = 0
    for _ in range(count):
        mic.readinto(frame)
        bits, dc, dev_peak, clipped = levels.frame_stats(frame)
        bits_list.append(bits)
        peak = max(peak, dev_peak)
        if clipped >= levels.CLIP_MIN_SAMPLES:
            clipped_frames += 1
        bar.set(bits, color)
    return bits_list, peak, clipped_frames


def measure():
    """One guided run. Returns (cal, problems)."""
    frame = bytearray(levels.FRAME_BYTES)
    mic = config.init_microphone()
    led.value(1)                                  # the microphone is open
    try:
        for _ in range(SETTLE_FRAMES):
            mic.readinto(frame)
        say("Be quiet", config.CYAN, "measuring the room's noise", "4 seconds")
        print("Stay quiet for 4 seconds...")
        quiet, _, _ = collect(mic, frame, QUIET_FRAMES, config.CYAN)
        say("SPEAK", config.YELLOW, "Hey Pico, what is due tomorrow", "say it again and again")
        print("Speak now for 4 seconds: 'Hey Pico, what is due tomorrow?'")
        speech, peak, clipped_frames = collect(mic, frame, SPEECH_FRAMES, config.YELLOW)
    finally:
        mic.deinit()
        led.value(0)
    return levels.make_calibration(quiet, speech, peak, clipped_frames, DISTANCE_CM)


MESSAGES = {
    "clipping": ("CLIPPING", "move back or speak softer"),
    "room_not_quiet": ("TOO NOISY", "the quiet part was not quiet"),
    "snr_low": ("SNR LOW", "move closer or quiet the room"),
    "too_few_frames": ("TOO SHORT", "not enough frames"),
}

try:
    while True:
        display.fill(config.BLACK)
        ui.put(display, "CALIBRATE", 70, SMALL, config.CYAN, 20)
        bar.frame()
        say("Press MODE", config.YELLOW, "at {} cm from the mic".format(DISTANCE_CM))
        print("Press MODE to start the calibration.")
        wait_for(mode_button)

        cal, problems = measure()
        floor = cal["noise_floor"]
        level = cal["speech_level"]
        print()
        print("noise floor    {:.2f} bits".format(floor))
        print("noise ceiling  {:.2f} bits".format(cal["noise_ceiling"]))
        print("speech level   {:.2f} bits".format(level))
        print("SNR            {:.2f} bits = {:.1f} dB".format(
            levels.snr_bits(level, floor), levels.snr_db(level, floor)))
        print("speech floor   {:.2f} bits (gate opens)".format(cal["speech_floor"]))
        print("gate close     {:.2f} bits (gate closes)".format(cal["gate_close"]))
        print("record_shift   {}".format(cal["record_shift"]))
        print("problems:      {}".format(problems if problems else "none"))

        if problems:
            title, advice = MESSAGES[problems[0]]
            say(title, config.RED, advice, "", "DOWN again   MODE quit")
            print("{}: {}".format(title, advice))
        else:
            say("Done", config.GREEN,
                "floor {:.1f} speech {:.1f} {:.0f} dB".format(
                    floor, level, levels.snr_db(level, floor)),
                "gate opens at {:.1f} bits".format(cal["speech_floor"]),
                "", "UP save DOWN again MODE quit")
        bar.tick(cal["noise_floor"], config.CYAN)
        bar.tick(cal["speech_floor"], config.GREEN)
        bar.tick(cal["speech_level"], config.YELLOW)

        choice = wait_for(mode_button, up_button, down_button)
        if choice is mode_button:
            break
        if choice is up_button and not problems:
            calibration.save(cal)               # the ONLY flash write in this program
            print("saved calibration.json")
            say("Saved", config.GREEN, "calibration.json written")
            time.sleep_ms(1500)
            break
        # DOWN (or UP with problems): measure again
finally:
    led.value(0)

stored = calibration.load()
print("calibration.json now holds:", {k: stored[k] for k in stored})
