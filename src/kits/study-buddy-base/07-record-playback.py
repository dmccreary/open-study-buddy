# Test 07: Hold to Record, Release to Play Back
# Hold the MODE button and talk. The microphone records while you hold it.
# Let go, and the speaker plays back what it heard. This is the first test
# that uses everything at once: button, microphone, speaker, and display.
#
# Run tests 03, 04, 05, and 06 first. If any of them fails, this one will too,
# and those tests will tell you which part to fix.
#
# PASS: you say something, let go of MODE, and hear your voice come back.
# If it comes back silent, the recording was too quiet: speak closer to the
# microphone, or raise PLAYBACK_GAIN.
# If it comes back crackly, it is too loud: lower PLAYBACK_GAIN or VOLUME.
# If it sounds like a chipmunk or a monster, the two sample rates do not
# match -- both come from MIC_SAMPLE_RATE in config.py.
#
# How it works
#   While the button is down, readinto() fills a big buffer with the
#   microphone's 32-bit samples. We keep them as they arrive and only
#   convert later, because Python is too slow to do math on every sample in
#   real time. After release, we convert the buffer to the 16-bit samples
#   the amplifier wants, one block at a time and IN PLACE: each 16-bit
#   result is half the size of its 32-bit original, so it always lands in
#   space we have already read. That halves the memory this test needs.

NAME = "07-record-playback.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import struct
import time
from machine import I2S, Pin

import config

MAX_SECONDS = 3            # the buffer holds this much sound
MIN_SECONDS = 0.2          # shorter than this is a bump, not a recording
SKIP_MS = 100              # the microphone's first moments are not real sound
PLAYBACK_GAIN = 8          # 24-bit -> 16-bit makes speech very quiet; this
                           # multiplies it back up (8 = 18 dB louder)
CHUNK = 1024               # bytes per read: 256 samples, 20 ms
BLOCK = 256                # samples converted at a time
IBUF = 8192                # the speaker's buffer: 320 ms at 12800 Hz

RATE = config.MIC_SAMPLE_RATE
SHIFT = config.MIC_SAMPLE_SHIFT

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
TRACK = config.color565(40, 40, 40)
BAR_WIDTH = 200
BAR_X = config.CENTER_X - BAR_WIDTH // 2
BAR_Y = 215

display = config.init_display()
config.set_backlight(True)
button = config.init_buttons()[0]          # MODE
led = config.init_led()
config.set_gain()

gc.collect()
raw = bytearray(MAX_SECONDS * RATE * 4)    # 3 s of 32-bit samples, 150 KB
view = memoryview(raw)


def put(text, y, font, color, width):
    """Draw text centered, padded to a fixed width so it covers whatever
    was there before."""
    config.centered_text(display, font, text.center(width), y, color)


def screen(status, color, hint):
    display.fill(config.BLACK)
    put("TEST 07", 70, SMALL, config.CYAN, 20)
    put(status, 130, BIG, color, 14)
    put(hint, 180, SMALL, DIM, 34)
    display.fill_rect(BAR_X, BAR_Y, BAR_WIDTH, 14, TRACK)


def record():
    """Fill the buffer while MODE is held. Returns the number of samples."""
    mic = config.init_microphone()
    position = 0
    skip = SKIP_MS * RATE * 4 // 1000
    drawn = 0
    try:
        while position < len(raw) and button.value() == 0:
            got = mic.readinto(view[position:position + CHUNK])
            if skip > 0:                   # throw away the start-up sound
                skip -= got
                continue
            position += got
            width = BAR_WIDTH * position // len(raw)
            if width > drawn:              # grow the red bar
                display.fill_rect(BAR_X + drawn, BAR_Y, width - drawn, 14,
                                  config.RED)
                drawn = width
    finally:
        mic.deinit()
    return position // 4


def convert(count):
    """Turn the first count 32-bit samples into 16-bit ones, in place.

    Pass 1 finds the microphone's DC offset, the constant it adds to
    everything. Pass 2 removes it, applies the gain, and writes 16-bit
    samples over the front of the buffer."""
    total = 0
    for start in range(0, count, BLOCK):
        n = min(BLOCK, count - start)
        total += sum(s >> SHIFT for s in
                     struct.unpack_from("<%di" % n, raw, start * 4))
    offset = total // count

    for start in range(0, count, BLOCK):
        n = min(BLOCK, count - start)
        samples = struct.unpack_from("<%di" % n, raw, start * 4)
        louder = [max(-32768, min(32767, ((s >> SHIFT) - offset) * PLAYBACK_GAIN >> 8))
                  for s in samples]
        struct.pack_into("<%dh" % n, raw, start * 2, *louder)
    return offset


def play(count):
    """Play the first count 16-bit samples through the speaker."""
    audio = I2S(config.I2S_SPEAKER_ID,
                sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
                sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                format=I2S.MONO, rate=RATE, ibuf=IBUF)
    try:
        audio.write(view[:count * 2])
        audio.write(bytes(RATE * 100 // 1000 * 2))      # a quiet tail
        time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)   # let it finish
    finally:
        audio.deinit()


print("Hold MODE (GP{}) and talk, up to {} seconds. Let go to hear it.".format(
    config.BUTTON_MODE_PIN, MAX_SECONDS))
screen("Hold MODE", config.YELLOW, "talk, then let go to hear it")

while True:
    if button.value() != 0:                # waiting for a press
        time.sleep_ms(10)
        continue

    # ---- recording ----
    led.value(1)
    screen("RECORDING", config.RED, "let go of MODE to stop")
    print("Recording...")
    started = time.ticks_ms()
    count = record()
    led.value(0)
    seconds = count / RATE
    print("Recorded {:.2f} s ({} samples) in {} ms.".format(
        seconds, count, time.ticks_diff(time.ticks_ms(), started)))

    if seconds < MIN_SECONDS:
        print("Too short -- hold the button while you talk.")
        screen("Too short", config.YELLOW, "hold MODE while you talk")
        while button.value() == 0:
            time.sleep_ms(10)
        time.sleep_ms(1000)
        screen("Hold MODE", config.YELLOW, "talk, then let go to hear it")
        continue

    # ---- playing back ----
    screen("Playing", config.GREEN, "{:.1f} seconds".format(seconds))
    offset = convert(count)
    print("Playing back (microphone offset was {}).".format(offset))
    play(count)

    # Wait for the button to be let go, in case the buffer filled up while
    # it was still held, so one long hold is one recording, not many.
    while button.value() == 0:
        time.sleep_ms(10)
    print("Hold MODE and talk again.")
    screen("Hold MODE", config.YELLOW, "talk, then let go to hear it")

# Try This
#   1. Change PLAYBACK_GAIN to 2, then to 24. Where does it get too quiet or
#      too crackly? What is happening to the numbers when it crackles?
#   2. Change MAX_SECONDS to 5. Does the buffer still fit in RAM? Run test 02
#      to see how much memory is left.
#   3. Play the recording back at half the rate: in play(), change
#      rate=RATE to rate=RATE // 2. Is your voice higher or lower? Why?
