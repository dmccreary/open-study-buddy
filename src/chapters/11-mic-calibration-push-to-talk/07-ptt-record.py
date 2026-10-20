# Chapter 11, Test 07: Push-to-talk recording
# Hold MODE and talk. The microphone is open only while you hold the button.
# When you let go (or after 6 seconds) the microphone closes, the recording is
# played back through the speaker, and the screen shows what was recorded. UP
# afterwards saves a copy to flash as utterance.raw. Needs the display, the
# buttons, the microphone and the speaker.
#
# The recording goes into ONE buffer that is allocated once, at the start,
# before anything can fragment the heap: 6 seconds of 16-bit samples, 153,600
# bytes (the same size as kit test 07's 3 seconds of 32-bit samples).
#
# PASS: "REC" shows only while MODE is held; the level bar moves while you
# talk; the playback sounds like you; the summary shows the length, bytes,
# peak, clipped frames, and the work time per frame. A tap shorter than 0.2 s
# says "too short". WRITE DOWN: work ms avg and max (the 40 ms budget is the
# limit; "overruns" must be 0).
#
# The microphone is CLOSED before the speaker is opened. Never play while
# listening: the device would hear itself (Chapter 8).

NAME = "07-ptt-record.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import time
from machine import I2S, Pin

import calibration
import config
import levels
import recorder
import ui
from buttons import Button

REVIEW_MS = 4000               # how long UP can save a copy after playback
IBUF = 8192                    # the speaker's buffer: 320 ms at 12,800 Hz
RATE = config.MIC_SAMPLE_RATE

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

# 1. The big buffer FIRST, while the heap is still in one piece (Chapter 2).
rec = recorder.new_buffer()
view = memoryview(rec)
print("Recording buffer: {} bytes ({} s of 16-bit samples). Free heap now: {}".format(
    len(rec), recorder.MAX_SECONDS, gc.mem_free()))

cal = calibration.load()
if not cal["calibrated"]:
    print("No calibration.json: using DEFAULT guesses. Run 04-calibrate.py first.")

display = config.init_display()
config.set_backlight(True)
led = config.init_led()
config.set_gain()
pins = config.init_buttons()
mode_button, up_button = Button(pins[0]), Button(pins[1])

bar = ui.LevelBar(display, config.CENTER_X - 100, 190, 200, 22, 9, 21)


def screen(title, color, line1="", line2="", line3="", line4=""):
    ui.put(display, title, 100, BIG, color, 14)
    ui.put(display, line1, 148, SMALL, DIM, 30)
    ui.put(display, line2, 225, SMALL, DIM, 30)
    ui.put(display, line3, 243, SMALL, DIM, 30)
    ui.put(display, line4, 261, SMALL, DIM, 30)


def show_time(n, bits, gate_open):
    if n % 5 == 0:                              # 200 ms: one small text region
        ui.put(display, "{:.1f} s".format(n * levels.FRAME_MS / 1000), 148, SMALL, DIM, 30)


def play(count_bytes):
    """Play the first count_bytes of the recording. The microphone is closed."""
    speaker = I2S(config.I2S_SPEAKER_ID,
                  sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
                  sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                  format=I2S.MONO, rate=RATE, ibuf=IBUF)
    try:
        speaker.write(view[:count_bytes])
        speaker.write(bytes(RATE * 100 // 1000 * 2))        # a quiet tail
        time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)       # let the buffer drain
    finally:
        speaker.deinit()


def save_copy(count_bytes):
    """The only flash write: the person pressed UP."""
    with open("utterance.raw", "wb") as f:
        f.write(view[:count_bytes])
    print("saved utterance.raw ({} bytes). On your computer: tools/raw-to-wav.py".format(count_bytes))


display.fill(config.BLACK)
ui.put(display, "PUSH TO TALK", 70, SMALL, config.CYAN, 20)
bar.frame()
screen("Hold MODE", config.YELLOW, "talk, then let go")
print("Hold MODE and talk (up to {} s). Let go to hear it.".format(recorder.MAX_SECONDS))

while True:
    event = mode_button.update()
    if event != "press":
        time.sleep_ms(5)
        continue

    # ---- LISTENING: the microphone is open only inside record() ----
    led.value(1)
    screen("REC", config.RED, "0.0 s")
    bar.set(0, config.YELLOW)
    result = recorder.record(rec, mode_button, cal, bar=bar, on_frame=show_time)
    led.value(0)                                 # the microphone is closed now
    n_bytes = result["bytes"]
    print("Recorded {:.2f} s = {} bytes, stopped by {}.".format(
        result["seconds"], n_bytes, result["stopped"]))
    print("  peak {} of 32767 after record_shift {}, microphone-clipped frames {}".format(
        result["peak16"], cal["record_shift"], result["clipped_frames"]))
    if result["limited"]:
        print("  The recording was cut off at the 16-bit limit: speak softer or run 04-calibrate.py.")
    print("  work per frame: avg {:.1f} ms, max {:.1f} ms of {} ms; overruns {}".format(
        result["work_ms_avg"], result["work_ms_max"], levels.FRAME_MS, result["overruns"]))

    while mode_button.down:                      # if the buffer filled while held
        mode_button.update()
        time.sleep_ms(5)
    bar.set(0, config.YELLOW)

    if result["frames"] < recorder.MIN_FRAMES:
        screen("Too short", config.YELLOW, "hold MODE while you talk")
        print("Too short (under 200 ms): hold MODE while you talk.")
    else:
        screen("Playing", config.GREEN, "{:.1f} s  {} bytes".format(result["seconds"], n_bytes),
               "peak {}  clipped {}".format(result["peak16"], result["clipped_frames"]),
               "work {:.0f}/{:.0f} ms of {}".format(result["work_ms_avg"],
                                                  result["work_ms_max"], levels.FRAME_MS),
               "UP: save a copy")
        play(n_bytes)
        deadline = time.ticks_add(time.ticks_ms(), REVIEW_MS)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            if up_button.update() == "release":
                save_copy(n_bytes)
                break
            time.sleep_ms(5)
    screen("Hold MODE", config.YELLOW, "talk, then let go")
    print("Hold MODE and talk again.")
