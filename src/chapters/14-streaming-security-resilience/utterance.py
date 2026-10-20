# utterance.py -- a small push-to-talk recorder and speaker for the network chapters
#
# record():  while the button is held, read the microphone's 32-bit samples
#            (INMP441: 24 real bits in the top of each word), convert them to
#            16-bit mono on the fly, and either keep them in one buffer or hand
#            them to a function piece by piece (for streaming).
# Speaker:   plays 16-bit mono PCM, with the Chapter 8 rules built in: let the
#            buffer drain before deinit(), and close the speaker before the
#            microphone is ever opened again.
#
# Chapter 11 builds the full push-to-talk recorder (noise floor, voice activity
# detection). This is the small version these chapters need, so they stand alone.

import gc
import struct
import time
from machine import I2S, Pin

import config

RATE = config.MIC_SAMPLE_RATE            # 12,800 samples per second
SHIFT = config.MIC_SAMPLE_SHIFT          # 8: 32-bit word -> 24-bit sample
READ_BYTES = 1024                        # 256 samples = 20 ms of microphone words
READ_SAMPLES = READ_BYTES // 4
OUT_BYTES = READ_SAMPLES * 2             # 512 bytes of 16-bit audio per read
SKIP_READS = 5                           # throw away the first 100 ms (start-up sound)
GAIN = 8                                 # 24-bit -> 16-bit makes speech quiet; x8 = +18 dB
SPEAKER_IBUF = 8192                      # 320 ms at 12,800 Hz, 16-bit
QUIET_TAIL_MS = 120                      # Chapter 8: ignore the microphone this long after sound

_UNPACK = "<%di" % READ_SAMPLES
_PACK = "<%dh" % READ_SAMPLES


def make_buffer(seconds):
    """Allocate the recording buffer FIRST, before the heap fragments (Chapter 2)."""
    gc.collect()
    return bytearray(int(seconds * RATE * 2))


def convert(raw, out, pos):
    """256 microphone words in raw -> 256 16-bit samples written to out at pos.
    Removes this chunk's average (the microphone's DC offset), applies GAIN, clips."""
    shifted = [v >> SHIFT for v in struct.unpack(_UNPACK, raw)]
    mean = sum(shifted) // READ_SAMPLES
    struct.pack_into(_PACK, out, pos,
                     *[max(-32768, min(32767, ((x - mean) * GAIN) >> 8)) for x in shifted])


def record(button, out, chunk_sink=None, on_progress=None):
    """Record while button.value() == 0. Returns (bytes_recorded, stats).

    chunk_sink=None : samples fill `out` from the start; stops when `out` is full.
    chunk_sink=fn   : `out` is only a staging area (use 1,024 bytes); each time it
                      fills, fn(memoryview) is called and the area is reused. Nothing
                      is kept, so any length of speech fits.
    stats: reads, worst_us, total_us -- the time the conversion took, to compare
           with the 20 ms (20,000 us) each read has to fit in."""
    raw = bytearray(READ_BYTES)
    view = memoryview(out)
    mic = config.init_microphone()
    pos = 0
    total = 0
    reads = worst = spent = 0
    try:
        for _ in range(SKIP_READS):
            mic.readinto(raw)
        while button.value() == 0:
            if chunk_sink is None and pos + OUT_BYTES > len(out):
                break
            mic.readinto(raw)
            t = time.ticks_us()
            convert(raw, out, pos)
            used = time.ticks_diff(time.ticks_us(), t)
            reads += 1
            spent += used
            worst = max(worst, used)
            pos += OUT_BYTES
            total += OUT_BYTES
            if chunk_sink is not None and pos + OUT_BYTES > len(out):
                chunk_sink(view[:pos])
                pos = 0
            if on_progress and reads % 10 == 0:
                on_progress(total)
        if chunk_sink is not None and pos:
            chunk_sink(view[:pos])
    finally:
        mic.deinit()                         # always release the microphone (Chapter 2)
    return total, {"reads": reads, "worst_us": worst, "total_us": spent}


class Speaker:
    def __init__(self, rate=RATE):
        config.set_gain()
        self.rate = rate
        self.i2s = I2S(config.I2S_SPEAKER_ID,
                       sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
                       sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                       format=I2S.MONO, rate=rate, ibuf=SPEAKER_IBUF)

    def write(self, view):
        self.i2s.write(view)

    def finish(self, drain=True):
        """drain=True: the sound ended naturally, so let the last of it play.
        drain=False: the listener interrupted (barge-in), so stop at once."""
        try:
            if drain:
                self.i2s.write(bytes(self.rate * 100 // 1000 * 2))        # 100 ms of silence
                time.sleep_ms(SPEAKER_IBUF * 1000 // (self.rate * 2) + 50)
        finally:
            self.i2s.deinit()
        time.sleep_ms(QUIET_TAIL_MS)         # let the room go quiet before listening again
