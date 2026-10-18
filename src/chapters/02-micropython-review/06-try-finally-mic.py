# Chapter 2, Test 06: try / finally releases the microphone
# Reads microphone frames and prints how loud each is, until you press Ctrl-C.
# The `finally` block runs when you stop, so the I2S hardware is released.
# Needs the INMP441 microphone (and the kit's config.py and lib/).
#
# PASS: you see one line per frame, about 25 per second. Press Ctrl-C. You see
# "Stopped by you", then "microphone released". Run it again immediately:
# it starts again with no error.

NAME = "06-try-finally-mic.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import struct
import time

import config

FRAME_SAMPLES = 512
FRAME_BYTES = FRAME_SAMPLES * 4

buf = bytearray(FRAME_BYTES)
mic = config.init_microphone()          # created BEFORE the try, so finally can use it
print("Listening. Make some noise, then press Ctrl-C.")
try:
    count = 0
    while True:
        mic.readinto(buf)
        samples = struct.unpack("<512i", buf)
        top = max(abs(s >> config.MIC_SAMPLE_SHIFT) for s in samples)
        count += 1
        print("frame {:4d}  peak {:8d}".format(count, top))
except KeyboardInterrupt:
    print("Stopped by you after", count, "frames.")
finally:
    mic.deinit()
    print("microphone released.")
