# levels.py -- loudness measures, calibration math and the level gate (Chapter 11)
#
# Pure Python. It needs no display or pins, so the same file runs on the Pico
# and on your computer (09-calibration-selftest.py does both).
#
# Units: LOUDNESS IS MEASURED IN "BITS", as in Chapters 3 and 8 and kit test 06:
#   bits = log2(1 + average distance of the frame's samples from their middle)
# One bit more means the sound is twice as big, which is 6.02 dB.
#
# The main pieces:
#   frame_stats()       one pass over a 40 ms frame: loudness, DC offset, peak,
#                       clipped samples, and (optionally) the 16-bit copy
#   percentile()        the p-th percentile of a list of readings
#   make_calibration()  turns a quiet recording and a speech recording into
#                       the calibration values the device stores
#   LevelGate           the gate with hysteresis that says "loud enough to be
#                       speech" frame by frame
#
# This file is copied unchanged into src/chapters/12-wake-word-detection/ so
# each chapter folder uploads on its own.

import math
import struct

try:
    import config
    SHIFT = config.MIC_SAMPLE_SHIFT          # 8: 32-bit word -> 24-bit sample
    RATE = config.MIC_SAMPLE_RATE            # 12800 samples per second
    FRAME_SAMPLES = config.FFT_SIZE          # 512 samples = one 40 ms frame
except ImportError:                          # on a computer, without the kit
    SHIFT, RATE, FRAME_SAMPLES = 8, 12800, 512

FRAME_FORMAT = "<%di" % FRAME_SAMPLES
FRAME_BYTES = FRAME_SAMPLES * 4              # 2,048 bytes of 32-bit words
FRAME16_BYTES = FRAME_SAMPLES * 2            # 1,024 bytes once packed to 16 bits
FRAME_MS = FRAME_SAMPLES * 1000 // RATE      # 40
LOG2 = math.log(2)
DB_PER_BIT = 20 * math.log10(2)              # 6.0206 dB for each doubling

FULL_SCALE = 1 << 23                         # biggest 24-bit magnitude: 8,388,608
CLIP_LEVEL = FULL_SCALE * 95 // 100          # "at the rail": 95% of full scale
CLIP_MIN_SAMPLES = 2                         # one stray sample is not clipping

MIN_SNR_BITS = 2.0                           # speech must beat the noise by 2 bits
MAX_NOISE_SPREAD = 1.5                       # ceiling - floor above this: room not quiet
GATE_FRACTION = 0.4                          # speech floor sits 40% of the way up
GATE_MARGIN = 1.0                            # ...and at least 1 bit above the ceiling
HYSTERESIS = 0.5                             # open and close levels are 0.5 bit apart
TARGET_PEAK16 = 16384                        # aim for speech peaks at half of 16-bit full scale
DEFAULT_SHIFT = 5                            # 24-bit -> 16-bit with +18 dB, as kit test 07


def frame_stats(buf, out=None, out_offset=0, record_shift=DEFAULT_SHIFT):
    """Analyze one frame of 32-bit microphone words.

    Returns (bits, dc, dev_peak, clipped):
      bits      loudness in bits (log base 2)
      dc        the microphone's DC offset, in 24-bit units
      dev_peak  the biggest distance from the DC offset in this frame
      clipped   samples at or beyond CLIP_LEVEL (0 for nearly every frame)
    If out is given (a bytearray), the frame is also written there as 16-bit
    samples starting at byte out_offset: DC removed, shifted right by
    record_shift, and limited to the 16-bit range."""
    samples = [s >> SHIFT for s in struct.unpack(FRAME_FORMAT, buf)]
    dc = sum(samples) // FRAME_SAMPLES
    average = sum([abs(s - dc) for s in samples]) // FRAME_SAMPLES
    high = max(samples)
    low = min(samples)
    dev_peak = max(high - dc, dc - low)
    clipped = 0
    if high >= CLIP_LEVEL or low <= -CLIP_LEVEL:     # rare: count only then
        clipped = sum([1 for s in samples if s >= CLIP_LEVEL or s <= -CLIP_LEVEL])
    if out is not None:
        if (dev_peak >> record_shift) > 32767:       # would not fit: limit each one
            packed = [max(-32768, min(32767, (s - dc) >> record_shift)) for s in samples]
        else:
            packed = [(s - dc) >> record_shift for s in samples]
        struct.pack_into("<%dh" % FRAME_SAMPLES, out, out_offset, *packed)
    return math.log(average + 1) / LOG2, dc, dev_peak, clipped


def loudness_bits(buf):
    """Just the loudness of a frame, in bits."""
    return frame_stats(buf)[0]


def bits_to_db(bits):
    """Decibels relative to full scale for a loudness in bits (Chapter 3)."""
    return DB_PER_BIT * (bits - 23)


def percentile(values, p):
    """The p-th percentile (0 to 100) of a list, with linear interpolation."""
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        raise ValueError("no readings")
    k = (n - 1) * p / 100
    low = int(k)
    high = min(low + 1, n - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (k - low)


def snr_bits(speech, floor):
    """Signal-to-noise ratio in bits: how far speech sits above the floor."""
    return speech - floor


def snr_db(speech, floor):
    """The same ratio in decibels (6.02 dB per bit)."""
    return DB_PER_BIT * (speech - floor)


def record_shift_for(dev_peak):
    """The smallest right-shift that puts a peak of dev_peak (24-bit units)
    at or below half of the 16-bit range. Smaller shift = louder recording."""
    shift = 0
    while (dev_peak >> shift) > TARGET_PEAK16 and shift < 8:
        shift += 1
    return shift


def make_calibration(quiet_bits, speech_bits, speech_dev_peak, clipped_frames,
                     distance_cm):
    """Turn two lists of frame loudness readings into calibration values.

    quiet_bits       readings from a quiet room
    speech_bits      readings while the person says the phrase
    speech_dev_peak  the biggest dev_peak seen while speaking
    clipped_frames   how many speech frames had clipped samples
    Returns (cal, problems). cal is the dict the device stores; problems is a
    list of short strings ("clipping", "snr_low", "room_not_quiet", ...). An
    empty list means the calibration is good."""
    floor = percentile(quiet_bits, 50)
    ceiling = percentile(quiet_bits, 95)
    level = percentile(speech_bits, 90)
    problems = []
    if len(quiet_bits) < 20 or len(speech_bits) < 20:
        problems.append("too_few_frames")
    if ceiling - floor > MAX_NOISE_SPREAD:
        problems.append("room_not_quiet")
    if clipped_frames > 0:
        problems.append("clipping")
    if level - floor < MIN_SNR_BITS:
        problems.append("snr_low")
    speech_floor = max(floor + GATE_FRACTION * (level - floor), ceiling + GATE_MARGIN)
    hysteresis = min(HYSTERESIS, (speech_floor - ceiling) / 2)
    cal = {
        "version": 1,
        "noise_floor": round(floor, 2),
        "noise_ceiling": round(ceiling, 2),
        "speech_level": round(level, 2),
        "speech_floor": round(speech_floor, 2),
        "gate_close": round(speech_floor - hysteresis, 2),
        "record_shift": record_shift_for(speech_dev_peak),
        "distance_cm": distance_cm,
    }
    return cal, problems


class LevelGate:
    """A switch that is open while the sound is loud enough to be speech.

    It opens when a frame's loudness reaches open_at, and closes only when a
    frame falls BELOW close_at. open_at is higher than close_at, so a level
    that hovers near one threshold cannot make the gate flutter."""

    def __init__(self, open_at, close_at):
        self.open_at = open_at
        self.close_at = close_at
        self.is_open = False

    def update(self, bits):
        """Feed one frame's loudness. Returns True if the gate is open."""
        if self.is_open:
            if bits < self.close_at:
                self.is_open = False
        elif bits >= self.open_at:
            self.is_open = True
        return self.is_open
