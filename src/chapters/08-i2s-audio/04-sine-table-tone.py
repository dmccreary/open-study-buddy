# Chapter 8, Test 04: Sine table versus math.sin
# Builds a 440 Hz, 250 ms tone two ways, times each, compares the samples,
# and plays both so you can hear whether they differ. Needs the amplifier and
# speaker (the timing and comparison also work without them).
#
# PASS: the table version is faster than math.sin; the largest difference
# between the two is small compared to the 13,107 peak; the two beeps sound
# the same. Write down both times.

NAME = "04-sine-table-tone.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import array
import math
import time

RATE = 16000
N = 256
FREQ = 440
MS = 250
VOLUME = 40

SINE = array.array("h", [int(32767 * math.sin(2 * math.pi * i / N)) for i in range(N)])
print("table: {} entries, {} bytes".format(N, N * 2))


def tone_math(freq, ms, volume):
    count = RATE * ms // 1000
    out = array.array("h", [0] * count)
    for i in range(count):
        out[i] = int(32767 * volume / 100 * math.sin(2 * math.pi * freq * i / RATE))
    return out


def tone_table(freq, ms, volume):
    count = RATE * ms // 1000
    out = array.array("h", [0] * count)
    step = freq * N / RATE
    phase = 0.0
    for i in range(count):
        out[i] = SINE[int(phase) % N] * volume // 100
        phase += step
    return out


start = time.ticks_us()
a = tone_math(FREQ, MS, VOLUME)
t_math = time.ticks_diff(time.ticks_us(), start) / 1000
start = time.ticks_us()
b = tone_table(FREQ, MS, VOLUME)
t_table = time.ticks_diff(time.ticks_us(), start) / 1000

worst = max(abs(x - y) for x, y in zip(a, b))
print("samples      : {}".format(len(a)))
print("math.sin     : {:.1f} ms".format(t_math))
print("sine table   : {:.1f} ms  ({:.1f}x faster)".format(t_table, t_math / t_table))
print("largest difference between the two: {} (peak is {})".format(worst, 32767 * VOLUME // 100))
print("table step per sample at {} Hz: {:.2f} positions".format(FREQ, FREQ * N / RATE))

try:
    from machine import I2S, Pin
    import config
    config.set_gain()
    audio = I2S(config.I2S_SPEAKER_ID,
                sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
                sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                format=I2S.MONO, rate=RATE, ibuf=8192)
    try:
        silence = bytes(RATE * 300 // 1000 * 2)
        print("playing math.sin version, then table version")
        audio.write(a)
        audio.write(silence)
        audio.write(b)
        audio.write(silence)
        audio.write(bytes(RATE * 100 // 1000 * 2))
        time.sleep_ms(8192 * 1000 // (RATE * 2) + 50)
    finally:
        audio.deinit()
except ImportError:
    print("(no speaker on this machine: skipped playback)")
print("PASS if the table was faster and both beeps sounded alike.")
