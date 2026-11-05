# demo_record.py -- demo 8 of 20-demo-template.py: record and play back.
#
# Press a button, talk for three seconds, and hear it come back.
#
#   UP or MODE   record 3 seconds, then play it back
#   DOWN         play the last recording again
#
# This is test 07 with a fixed 3-second recording instead of hold-to-talk,
# so the demo works the same for everyone. Test 07 explains the two
# tricks: keep the microphone's raw 32-bit samples while recording (Python
# is too slow to convert them on the fly), then convert them to 16-bit
# IN PLACE afterwards, so one 150 KB buffer is all it needs.
#
# The buffer is made in start() and let go in stop(), so the other demos
# get that memory back. If it cannot be made (the Pico is short of RAM),
# the demo says so instead of crashing.

import gc
import struct
import time

import config
from demo_kit import (BLACK, WHITE, DIM, TRACK, SMALL, BIG, CX, put,
                      centered, menu_hint, settle, Speaker)

SECONDS = 3
SKIP_MS = 100              # the microphone's first moments are not real sound
PLAYBACK_GAIN = 8          # 24-bit -> 16-bit makes speech quiet; 8 = 18 dB louder
CHUNK = 1024               # bytes per microphone read: 256 samples, 20 ms
BLOCK = 256                # samples converted at a time
PLAY_CHUNK = 8192          # bytes per speaker write: 4096 samples, 320 ms

RATE = config.MIC_SAMPLE_RATE
SHIFT = config.MIC_SAMPLE_SHIFT

TITLE_Y = 60
STATUS_Y = 120
HINT_Y = 166
BAR_W, BAR_H = 220, 16
BAR_X = CX - BAR_W // 2
BAR_Y = 206
HINT2_Y = 240
MENU_Y = 296


def start(display, kit, saved):
    global _display, _kit, raw, view, count, led
    _display = display
    _kit = kit
    display.fill(BLACK)
    centered(display, SMALL, "RECORD & PLAY BACK", TITLE_Y, DIM)
    menu_hint(display, MENU_Y)
    led = config.init_led()
    count = 0
    gc.collect()
    try:
        raw = bytearray(SECONDS * RATE * 4)       # 150 KB of 32-bit samples
    except MemoryError:
        raw = None
        screen("Not enough RAM", config.RED, "free: %d KB" % (
            gc.mem_free() // 1024))
        return
    view = memoryview(raw)
    ready()


def screen(status, color, hint, hint2=""):
    put(_display, BIG, status, STATUS_Y, color, 14)
    put(_display, SMALL, hint, HINT_Y, DIM, 30)
    put(_display, SMALL, hint2, HINT2_Y, config.YELLOW, 30)


def bar(fraction, color, drawn=0):
    """Grow a bar from `drawn` pixels to `fraction` of the way across.
    Returns how many pixels are drawn now."""
    width = int(BAR_W * fraction)
    if width > drawn:
        _display.fill_rect(BAR_X + drawn, BAR_Y, width - drawn, BAR_H, color)
    return max(width, drawn)


def ready():
    _display.fill_rect(BAR_X, BAR_Y, BAR_W, BAR_H, TRACK)
    screen("Press UP", config.YELLOW, "then talk for %d seconds" % SECONDS,
           "DOWN: hear it again" if count else "")


def record():
    """Fill the buffer with SECONDS of sound. Returns the sample count."""
    mic = config.init_microphone()
    position = 0
    skip = SKIP_MS * RATE * 4 // 1000
    drawn = 0
    try:
        while position < len(raw):
            got = mic.readinto(view[position:position + CHUNK])
            if skip > 0:                   # throw away the start-up sound
                skip -= got
                continue
            position += got
            drawn = bar(position / len(raw), config.RED, drawn)
    finally:
        mic.deinit()
    return position // 4


def convert(n):
    """Turn the first n 32-bit samples into 16-bit ones, in place (see
    test 07): pass 1 finds the DC offset, pass 2 removes it and adds gain."""
    total = 0
    for first in range(0, n, BLOCK):
        size = min(BLOCK, n - first)
        total += sum(s >> SHIFT for s in
                     struct.unpack_from("<%di" % size, raw, first * 4))
    offset = total // n
    for first in range(0, n, BLOCK):
        size = min(BLOCK, n - first)
        samples = struct.unpack_from("<%di" % size, raw, first * 4)
        louder = [max(-32768, min(32767,
                                  ((s >> SHIFT) - offset) * PLAYBACK_GAIN >> 8))
                  for s in samples]
        struct.pack_into("<%dh" % size, raw, first * 2, *louder)
    return offset


def play(n):
    """Play the first n 16-bit samples, growing a green bar as it goes."""
    _display.fill_rect(BAR_X, BAR_Y, BAR_W, BAR_H, TRACK)
    speaker = Speaker(RATE)
    try:
        drawn = 0
        total = n * 2
        for first in range(0, total, PLAY_CHUNK):
            last = min(first + PLAY_CHUNK, total)
            speaker.write(view[first:last], (last - first) // 2)
            drawn = bar(last / total, config.GREEN, drawn)
    finally:
        speaker.deinit()                   # waits for the end, then frees I2S


def record_and_play():
    global count
    led.value(1)
    _display.fill_rect(BAR_X, BAR_Y, BAR_W, BAR_H, TRACK)
    screen("RECORDING", config.RED, "talk now!")
    print("Recording %d s..." % SECONDS)
    count = record()
    led.value(0)
    screen("Thinking...", config.CYAN, "getting it ready to play")
    offset = convert(count)
    print("Recorded %d samples; microphone offset %d." % (count, offset))
    screen("Playing", config.GREEN, "%.1f seconds" % (count / RATE))
    play(count)


def on_mode():
    global mode_pressed
    mode_pressed = True


mode_pressed = False


def update(now):
    global mode_pressed
    if raw is None:
        return
    record_now = _kit.up.pressed(now) or mode_pressed
    mode_pressed = False
    if record_now:
        record_and_play()
    elif _kit.down.pressed(now) and count:
        screen("Playing", config.GREEN, "the same %.1f seconds" % (
            count / RATE))
        play(count)
    else:
        return
    # Presses made while it was busy are old news: forget them.
    settle(_kit.buttons)
    ready()


def stop():
    global raw, view
    view = None
    raw = None                             # give the 150 KB back
    gc.collect()
    return None
