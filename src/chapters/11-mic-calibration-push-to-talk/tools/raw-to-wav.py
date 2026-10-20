# Run this on your COMPUTER, not on the Pico.
#
#   mpremote fs cp :utterance.raw .          (copy the file off the Pico)
#   python3 raw-to-wav.py utterance.raw utterance.wav
#
# 07-ptt-record.py saves a recording as raw 16-bit signed little-endian mono
# samples at 12,800 per second, with no header (UP after the playback saves
# it). This wraps those samples in a 44-byte WAV header (Chapter 3) so any
# player can open it, and prints the length and the peak so you can check the
# recording before you listen. Nothing is changed in the samples.

import sys
import wave

RATE = 12800                     # config.MIC_SAMPLE_RATE


def convert(src, dst):
    data = open(src, "rb").read()
    if len(data) % 2:
        data = data[:-1]                       # a whole number of 16-bit samples
    samples = len(data) // 2
    with wave.open(dst, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data)
    peak = 0
    for i in range(0, len(data), 2):
        value = int.from_bytes(data[i:i + 2], "little", signed=True)
        peak = max(peak, abs(value))
    print("{} samples = {:.2f} s, peak {} of 32767, wrote {}".format(
        samples, samples / RATE, peak, dst))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python3 raw-to-wav.py input.raw output.wav")
    convert(sys.argv[1], sys.argv[2])
