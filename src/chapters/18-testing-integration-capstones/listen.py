# listen.py -- Chapter 18: the microphone and the speaker, kept small
#
#   Mic     opens the microphone with the LED already on, closes it before the LED
#           goes off, shifts and measures every frame, and can calibrate.
#   beep    plays a short tone, then lets the speaker's buffer drain (Chapter 8).
#
# Chapter 17 builds the full version of the Mic idea (Listener): a status-bar
# indicator, a mute switch, and a test that proves the indicator cannot lie. The
# capstones here only light the onboard LED, which is the minimum.
#
# This file imports config, so it needs the Pico (or a fake Pico layer). The logic
# it calls lives in detectors.py, which runs anywhere.

import math
import struct
import time

import config
from detectors import bits_from_samples, mean_std
from overrun import OverrunCounter

FRAME_BYTES = 2048          # 512 samples x 4 bytes = 40 ms (Chapter 8)
SKIP_FRAMES = 8             # the microphone's start-up (kit test 06)


class Mic:
    def __init__(self, count_overruns=True):
        self.led = config.init_led()
        self.count_overruns = count_overruns
        self.mic = None
        self.buf = bytearray(FRAME_BYTES)

    def open(self):
        self.led.value(1)                       # 1. say we are listening
        try:
            raw = config.init_microphone()      # 2. then listen
        except Exception:
            self.led.value(0)
            raise
        self.mic = OverrunCounter(raw) if self.count_overruns else raw
        for _ in range(SKIP_FRAMES):
            self.mic.readinto(self.buf)
        if self.count_overruns:
            self.mic.reset()                    # do not count the start-up

    def close(self):
        if self.mic is not None:
            self.mic.deinit()                   # 1. stop listening
            self.mic = None
        self.led.value(0)                       # 2. only then turn the light off

    def bits(self):
        """Read one 40 ms frame; return its loudness in bits."""
        self.mic.readinto(self.buf)
        samples = [s >> config.MIC_SAMPLE_SHIFT for s in struct.unpack("<512i", self.buf)]
        return bits_from_samples(samples)

    def calibrate(self, frames=50):
        """Measure the room. Returns (floor, spread) in bits: the mean and the
        standard deviation of `frames` frames (50 frames = 2 seconds). Stay quiet."""
        return mean_std([self.bits() for _ in range(frames)])

    def overrun_summary(self):
        return self.mic.summary() if self.count_overruns and self.mic else ""


def beep(freq=1000, ms=200, volume=30):
    """A short tone at the microphone's sample rate. Do not call while the
    microphone is listening to something that must not hear it (Chapter 8)."""
    from machine import I2S, Pin
    rate = config.MIC_SAMPLE_RATE
    amp = 32767 * min(volume, config.VOLUME) // 100
    count = rate * ms // 1000
    fade = max(1, rate // 100)                          # 10 ms fades: no clicks
    data = bytearray(count * 2)
    for i in range(count):
        edge = min(1.0, i / fade, (count - i) / fade)
        struct.pack_into("<h", data, i * 2,
                         int(amp * edge * math.sin(2 * math.pi * freq * i / rate)))
    config.set_gain()
    speaker = I2S(config.I2S_SPEAKER_ID, sck=Pin(config.I2S_BCLK_PIN),
                  ws=Pin(config.I2S_LRC_PIN), sd=Pin(config.I2S_DIN_PIN),
                  mode=I2S.TX, bits=16, format=I2S.MONO, rate=rate, ibuf=8192)
    try:
        speaker.write(data)
        speaker.write(bytes(256))
        time.sleep_ms(8192 * 1000 // (rate * 2) + 50)   # let the buffer drain
    finally:
        speaker.deinit()
