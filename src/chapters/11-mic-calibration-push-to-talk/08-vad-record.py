# Chapter 11, Test 08: Find the start and end of an utterance
# Hold MODE and say something, with a pause before and after if you like. The
# recorder runs voice activity detection (VAD) on every frame: speech STARTS
# after START_FRAMES loud frames in a row and ENDS after END_FRAMES quiet frames
# in a row. When you let go, it prints the boundaries, keeps a little before
# (pre-roll) and after (hang-over), and plays back only the part it kept.
# Set AUTO_STOP = True and it stops recording by itself when the speech ends.
# Needs the display, the buttons, the microphone and the speaker.
#
# PASS: a console picture of the recording with the start (S), end (E), and kept
# range ([ ]) marked; the playback begins just before your first word and ends
# just after your last one, with the silence trimmed. Whisper, cough, and tap
# the table to see what the VAD does with them. WRITE DOWN: for a phrase you
# say, the kept length versus the recorded length.
#
# The digits under "loudness" are the frame's loudness above the noise floor
# in bits, 0 to 9 (9 means 9 or more).

NAME = "08-vad-record.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import I2S, Pin

import calibration
import config
import levels
import recorder
import ui
import vad
from buttons import Button

AUTO_STOP = False              # True: stop when the VAD hears the speech end
IBUF = 8192
RATE = config.MIC_SAMPLE_RATE

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

rec = recorder.new_buffer()
view = memoryview(rec)

cal = calibration.load()
if not cal["calibrated"]:
    print("No calibration.json: using DEFAULT guesses. Run 04-calibrate.py first.")
print("START_FRAMES {} ({} ms), END_FRAMES {} ({} ms), pre-roll {} frames, hang-over {} frames".format(
    vad.START_FRAMES, vad.START_FRAMES * levels.FRAME_MS,
    vad.END_FRAMES, vad.END_FRAMES * levels.FRAME_MS,
    vad.PRE_ROLL_FRAMES, vad.HANG_OVER_FRAMES))

display = config.init_display()
config.set_backlight(True)
led = config.init_led()
config.set_gain()
mode_button = Button(config.init_buttons()[0])
bar = ui.LevelBar(display, config.CENTER_X - 100, 190, 200, 22, 9, 21)
bar.frame()
bar.tick(cal["speech_floor"], config.GREEN)
bar.tick(cal["gate_close"], config.YELLOW)


def screen(title, color, line1="", line2="", line3=""):
    ui.put(display, title, 100, BIG, color, 14)
    ui.put(display, line1, 148, SMALL, DIM, 30)
    ui.put(display, line2, 225, SMALL, DIM, 30)
    ui.put(display, line3, 243, SMALL, DIM, 30)


def show_state(n, bits, gate_open):
    if n % 5 == 0:                              # one small text region, 5 times a second
        ui.put(display, "gate OPEN" if gate_open else "gate closed", 148, SMALL,
               config.GREEN if gate_open else DIM, 30)


def play(first_byte, stop_byte):
    speaker = I2S(config.I2S_SPEAKER_ID,
                  sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
                  sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                  format=I2S.MONO, rate=RATE, ibuf=IBUF)
    try:
        speaker.write(view[first_byte:stop_byte])
        speaker.write(bytes(RATE * 100 // 1000 * 2))
        time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)
    finally:
        speaker.deinit()


def picture(result, first, stop):
    """Two lines: loudness above the floor, and the markers."""
    floor = cal["noise_floor"]
    digits = ""
    marks = ""
    for i in range(result["frames"]):
        d = max(0, min(9, int(result["bits"][i] - floor)))
        digits += str(d)
        c = " "
        if i == first:
            c = "["
        if i == result["start_index"]:
            c = "S"
        if i == result["end_index"]:
            c = "E"
        if i == stop - 1 and c == " ":
            c = "]"
        marks += c
    print("loudness " + digits)
    print("markers  " + marks)


screen("Hold MODE", config.YELLOW, "talk, then let go")
print("Hold MODE and talk. AUTO_STOP is {}.".format(AUTO_STOP))
while True:
    if mode_button.update() != "press":
        time.sleep_ms(5)
        continue
    led.value(1)
    screen("REC", config.RED)
    result = recorder.record(rec, mode_button, cal, bar=bar, use_vad=True,
                             auto_stop=AUTO_STOP, on_frame=show_state)
    led.value(0)
    while mode_button.down:
        mode_button.update()
        time.sleep_ms(5)
    bar.set(0, config.YELLOW)

    total = result["frames"]
    print()
    print("Recorded {} frames = {:.2f} s, stopped by {}.".format(
        total, result["seconds"], result["stopped"]))
    if result["start_index"] is None:
        screen("No speech", config.YELLOW, "the gate never stayed open", "for {} frames".format(vad.START_FRAMES))
        print("No speech found: the gate never stayed open for {} frames.".format(vad.START_FRAMES))
        picture(result, -1, 0)
    else:
        first, stop = vad.boundaries(result["start_index"], result["end_index"], total)
        picture(result, first, stop)
        kept = stop - first
        print("Speech starts at frame {} ({} ms), ends at frame {} ({} ms).".format(
            result["start_index"], result["start_index"] * levels.FRAME_MS,
            result["end_index"], result["end_index"] * levels.FRAME_MS))
        print("Keep frames {} to {} = {} frames = {:.2f} s of {:.2f} s ({} bytes of {}).".format(
            first, stop - 1, kept, kept * levels.FRAME_MS / 1000, result["seconds"],
            kept * levels.FRAME16_BYTES, result["bytes"]))
        screen("Playing", config.GREEN, "kept {:.1f} s of {:.1f} s".format(
            kept * levels.FRAME_MS / 1000, result["seconds"]))
        play(first * levels.FRAME16_BYTES, stop * levels.FRAME16_BYTES)
    screen("Hold MODE", config.YELLOW, "talk, then let go")
