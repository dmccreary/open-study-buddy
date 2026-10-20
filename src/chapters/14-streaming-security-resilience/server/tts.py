"""Text-to-speech hook.

synthesize(text, rate) returns 16-bit mono little-endian PCM bytes at `rate`
samples per second, at full scale (the server applies the device's volume).

Choose a backend with the BUDDY_TTS environment variable:

  stub     (default) Does NOT speak. It plays one short tone per word, rising in
           pitch, so you can hear that audio arrived and how long a sentence is.
  service  Your real text-to-speech. The place to write it is marked below.

A real service rarely returns exactly what the Pico plays. The Pico's speaker is
set up for 16-bit mono at 12,800 Hz (config.MIC_SAMPLE_RATE), so the server must
convert: to_device_pcm() below turns a service's 16-bit mono samples at any rate
into samples at the device's rate. (MP3 and Opus must be decoded first; the Pico
cannot decode them.)
"""

import array
import math
import os


def stub_synthesize(text, rate):
    words = text.split() or ["."]
    out = array.array("h")
    for i, _ in enumerate(words):
        freq = 400 + 40 * (i % 12)
        n = rate * 120 // 1000
        fade = rate * 10 // 1000
        for k in range(n):
            edge = min(1.0, k / fade, (n - k) / fade)
            out.append(int(32767 * 0.9 * edge * math.sin(2 * math.pi * freq * k / rate)))
        out.extend([0] * (rate * 40 // 1000))
    return out.tobytes()


def to_device_pcm(pcm, src_rate, dst_rate):
    """Resample 16-bit mono PCM from src_rate to dst_rate by linear interpolation.
    Good enough for speech; going DOWN loses the highest frequencies (above half of
    dst_rate), which is what the Pico's speaker could not play anyway."""
    src = array.array("h")
    src.frombytes(pcm[: len(pcm) - len(pcm) % 2])
    if src_rate == dst_rate or not src:
        return src.tobytes()
    count = max(1, len(src) * dst_rate // src_rate)
    out = array.array("h", bytes(2 * count))
    step = src_rate / dst_rate
    for i in range(count):
        pos = i * step
        j = int(pos)
        frac = pos - j
        a = src[min(j, len(src) - 1)]
        b = src[min(j + 1, len(src) - 1)]
        out[i] = int(a + (b - a) * frac)
    return out.tobytes()


def apply_volume(pcm, percent):
    """Scale 16-bit PCM by percent (0-100), so the Pico does no per-sample work."""
    percent = max(0, min(100, percent))
    samples = array.array("h")
    samples.frombytes(pcm)
    for i, s in enumerate(samples):
        samples[i] = s * percent // 100
    return samples.tobytes()


def service_synthesize(text, rate):
    # ------------------------------------------------------------------
    # PUT YOUR REAL SERVICE HERE.
    #   1. key = os.environ["TTS_API_KEY"]        (server environment only)
    #   2. ask your provider for 16-bit mono PCM (or WAV) of `text`
    #   3. return to_device_pcm(samples, provider_rate, rate)
    # ------------------------------------------------------------------
    if not os.environ.get("TTS_API_KEY"):
        raise RuntimeError("TTS_API_KEY is not set in the server's environment")
    raise NotImplementedError("write service_synthesize() for your provider")


def synthesize(text, rate):
    backend = os.environ.get("BUDDY_TTS", "stub")
    if backend == "stub":
        return stub_synthesize(text, rate)
    if backend == "service":
        return service_synthesize(text, rate)
    raise RuntimeError("unknown BUDDY_TTS={!r}".format(backend))
