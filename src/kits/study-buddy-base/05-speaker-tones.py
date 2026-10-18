# Test 05: Speaker Tones
# Plays three short sound checks on the MAX98357A amplifier and speaker.
# Only the amplifier and speaker are needed -- no display, no buttons.
#
#   1. One beep      A4, 440 Hz, a steady note
#   2. A scale       C major, eight notes going up
#   3. Three volumes the same note at 25%, 50%, and 100% of the loudness
#                    set by VOLUME in config.py
#
# The Pico cannot hear whether the speaker is working, so this test is
# checked with YOUR ears. The console prints each note as it plays.
#
# PASS: you hear a beep, a rising scale, then three beeps getting louder.
# If it is silent, check the amplifier's VIN and GND wires and the speaker
# wires, then the signal wires (BCLK GP20, LRC GP21, DIN GP19).
# If I2S() raises an error, LRC must be on the pin right after BCLK.
# If it buzzes or crackles at full volume, that is the speaker running out
# of room -- turn VOLUME down in config.py.

NAME = "05-speaker-tones.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from machine import I2S, Pin

import config

RATE = 16000                 # samples per second
IBUF = 8192                  # bytes the I2S driver holds: 256 ms of sound
FADE = RATE // 100           # 10 ms fades, so notes don't click

NOTES = (("C4", 262), ("D4", 294), ("E4", 330), ("F4", 349),
         ("G4", 392), ("A4", 440), ("B4", 494), ("C5", 523))


def make_tone(freq, ms, volume=config.VOLUME):
    """Returns 16-bit mono samples of one sine-wave note.

    volume is 0 to 100. A sine wave is the smoothest sound there is."""
    count = RATE * ms // 1000
    amplitude = 32767 * volume / 100
    out = bytearray(count * 2)
    for i in range(count):
        fade = min(1.0, i / FADE, (count - i) / FADE)
        value = int(amplitude * fade * math.sin(2 * math.pi * freq * i / RATE))
        struct.pack_into("<h", out, i * 2, value)
    return out


def silence(ms):
    return bytes(RATE * ms // 1000 * 2)


config.set_gain()
audio = I2S(config.I2S_SPEAKER_ID,
            sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
            sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
            format=I2S.MONO, rate=RATE, ibuf=IBUF)
print("I2S started at {} Hz, 16-bit mono. Listen now.".format(RATE))

try:
    print()
    print("1. One beep: A4 (440 Hz)")
    audio.write(make_tone(440, 800))
    audio.write(silence(300))

    print()
    print("2. A scale")
    # Build the whole scale first, then play it, so the speaker never
    # waits while the Pico is still calculating the next note.
    scale = b"".join(make_tone(freq, 250) + silence(30) for _, freq in NOTES)
    for name, freq in NOTES:
        print("   {}  {} Hz".format(name, freq))
    audio.write(scale)
    audio.write(silence(300))

    print()
    print("3. Three volumes")
    for percent in (25, 50, 100):
        level = config.VOLUME * percent // 100
        print("   {}% of VOLUME ({})".format(percent, level))
        audio.write(make_tone(440, 400, level) + silence(250))

    # write() returns once the last bytes are in the buffer, which is up
    # to one buffer-length before they finish playing. Let them finish.
    audio.write(silence(100))
    time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)
finally:
    audio.deinit()

print()
print("Done. Did you hear all three parts?")

# Try This
#   1. Change 440 in part 1 to 220, then to 880. What happens to the pitch
#      each time you double the frequency?
#   2. Add your own song: write a list of (name, frequency) pairs and play
#      them the way part 2 does. Twinkle Twinkle starts C C G G A A G.
#   3. Change config.GAIN_DB from 9 to 12, upload config.py, and rerun.
#      How much louder is it? (Check VOLUME first -- start low.)
