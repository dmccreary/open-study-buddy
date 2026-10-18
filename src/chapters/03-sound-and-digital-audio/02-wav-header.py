# Chapter 3, Test 02: Build and write a WAV file
# Builds the 44-byte WAV header from the chapter, writes one second of a 440 Hz
# tone to a file, and reads the header back. Runs on the Pico (it writes
# tone.wav to flash) or on your computer (it writes tone.wav in the current
# folder). Needs no hardware.
#
# PASS: the printed header is 44 bytes, the file is 44 + 25,600 = 25,644 bytes,
# and the last line says PASS. To HEAR it, copy the file to your computer
# and double-click it:   mpremote fs cp :tone.wav tone.wav

NAME = "02-wav-header.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import os
import struct

RATE = 12800
FREQ = 440
SECONDS = 1


def wav_header(data_bytes, rate=12800, bits=16, channels=1):
    byte_rate = rate * channels * bits // 8
    block = channels * bits // 8
    return struct.pack("<4sI4s4sIHHIIHH4sI",
                       b"RIFF", 36 + data_bytes, b"WAVE",
                       b"fmt ", 16, 1, channels, rate, byte_rate, block, bits,
                       b"data", data_bytes)


count = RATE * SECONDS
samples = bytearray(count * 2)
for i in range(count):
    struct.pack_into("<h", samples, i * 2,
                     int(13000 * math.sin(2 * math.pi * FREQ * i / RATE)))

header = wav_header(len(samples), RATE)
print("header length:", len(header), "bytes (expect 44)")
print("header bytes :", " ".join("{:02x}".format(b) for b in header))

with open("tone.wav", "wb") as f:
    f.write(header)
    f.write(samples)

size = os.stat("tone.wav")[6]
print("tone.wav size:", size, "bytes (expect", 44 + count * 2, ")")

# Read it back and decode the fields
with open("tone.wav", "rb") as f:
    head = f.read(44)
(riff, total, wave, fmt, fmt_len, code, channels, rate, byte_rate,
 block, bits, data, data_len) = struct.unpack("<4sI4s4sIHHIIHH4sI", head)
print("riff={} wave={} fmt={!r} data={!r}".format(riff, wave, fmt, data))
print("format code {}, channels {}, rate {}, bytes/s {}, bits {}, data bytes {}".format(
    code, channels, rate, byte_rate, bits, data_len))

ok = (len(header) == 44 and size == 44 + count * 2 and riff == b"RIFF"
      and wave == b"WAVE" and rate == RATE and bits == 16 and channels == 1
      and data_len == count * 2 and total == size - 8)
print()
print("PASS" if ok else "FAIL: a field does not match the chapter's table")
