"""Speech-to-text hook.

transcribe(pcm, rate) takes 16-bit mono little-endian PCM bytes and returns the
words as a string ("" if nothing was heard).

Choose a backend with the BUDDY_STT environment variable:

  stub     (default) Does NOT recognize speech. It checks that the recording is
           not silent and then returns a fixed phrase (BUDDY_STT_STUB_TEXT, default
           "when is my next test"). It exists so the whole pipeline can be tested
           with no account and no internet.
  service  Your real speech-to-text. The place to write it is marked below.

No key is stored in this file. A real service reads its key from an environment
variable on the server (STT_API_KEY), never on the Pico.
"""

import array
import io
import math
import os
import wave

SILENCE_RMS = 50          # below this the recording is treated as silence (16-bit units)


def rms(pcm):
    samples = array.array("h")
    samples.frombytes(pcm[: len(pcm) - len(pcm) % 2])
    if not samples:
        return 0.0
    return math.sqrt(sum(s * s for s in samples) / len(samples))


def pcm_to_wav(pcm, rate):
    """Most services want a WAV file, not raw samples. 44-byte header + the PCM."""
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return out.getvalue()


def stub_transcribe(pcm, rate):
    if rms(pcm) < SILENCE_RMS:
        return ""
    return os.environ.get("BUDDY_STT_STUB_TEXT", "when is my next test")


def service_transcribe(pcm, rate):
    # ------------------------------------------------------------------
    # PUT YOUR REAL SERVICE HERE.
    #   1. key = os.environ["STT_API_KEY"]        (set it in the server's shell)
    #   2. wav = pcm_to_wav(pcm, rate)
    #   3. send `wav` to your provider with urllib.request or the provider's
    #      package, and return the transcript text.
    # Use only a provider your school has approved (Chapter 17): the recording
    # leaves the classroom network when you do this.
    # ------------------------------------------------------------------
    if not os.environ.get("STT_API_KEY"):
        raise RuntimeError("STT_API_KEY is not set in the server's environment")
    raise NotImplementedError("write service_transcribe() for your provider")


def transcribe(pcm, rate):
    backend = os.environ.get("BUDDY_STT", "stub")
    if backend == "stub":
        return stub_transcribe(pcm, rate)
    if backend == "service":
        return service_transcribe(pcm, rate)
    raise RuntimeError("unknown BUDDY_STT={!r}".format(backend))
