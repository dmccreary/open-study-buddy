# Chapter 11, Test 03: Measure the speech level and the signal-to-noise ratio
# Step 1: 3 seconds of quiet, to learn the noise floor.
# Step 2: 4 seconds in which you say "Hey Pico, what is due tomorrow?" over and
#         over at the distance you set in DISTANCE_CM.
# Then it prints the speech level (the 90th percentile of the speech frames),
# the signal-to-noise ratio in bits and in dB, the biggest sample it saw, and
# whether anything clipped. Needs the INMP441 microphone only.
#
# Measure the distance from your mouth to the microphone with a ruler and type
# it into DISTANCE_CM. Chapter 11 asks you to run this at several distances.
#
# PASS: it prints the numbers and "no clipping". Speech should read well above
# the floor (the rule of kit test 06 is at least 2.0 bits). If it says
# "CLIPPING", move farther back or speak more softly and run it again.
# WRITE DOWN: distance, floor, speech level, SNR.

NAME = "03-speech-level.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import config
import levels

DISTANCE_CM = 30              # EDIT: how far your mouth is from the microphone
QUIET_FRAMES = 75             # 3 seconds
SPEECH_FRAMES = 100           # 4 seconds
SETTLE_FRAMES = 8

frame = bytearray(levels.FRAME_BYTES)
mic = config.init_microphone()
quiet = []
speech = []
peak = 0
clipped_frames = 0
try:
    for _ in range(SETTLE_FRAMES):
        mic.readinto(frame)
    print("Distance: {} cm. Stay QUIET for 3 seconds...".format(DISTANCE_CM))
    for _ in range(QUIET_FRAMES):
        mic.readinto(frame)
        quiet.append(levels.frame_stats(frame)[0])
    print("NOW SPEAK for 4 seconds: 'Hey Pico, what is due tomorrow?'")
    for _ in range(SPEECH_FRAMES):
        mic.readinto(frame)
        bits, dc, dev_peak, clipped = levels.frame_stats(frame)
        speech.append(bits)
        peak = max(peak, dev_peak)
        if clipped >= levels.CLIP_MIN_SAMPLES:
            clipped_frames += 1
finally:
    mic.deinit()

floor = levels.percentile(quiet, 50)
print()
print("Noise floor (median of {} quiet frames): {:.2f} bits".format(len(quiet), floor))
print()
print("Speech frames, in bits:")
for label, p in (("median", 50), ("75th percentile", 75), ("90th percentile", 90)):
    print("  {:<16} {:6.2f}".format(label, levels.percentile(speech, p)))
print("  {:<16} {:6.2f}".format("highest", max(speech)))

level = levels.percentile(speech, 90)
above = sum([1 for b in speech if b >= floor + levels.MIN_SNR_BITS])
print()
print("Speech level (90th percentile)  {:.2f} bits".format(level))
print("Signal-to-noise ratio           {:.2f} bits = {:.1f} dB".format(
    levels.snr_bits(level, floor), levels.snr_db(level, floor)))
print("Frames at least {:.1f} bits over the floor: {} of {}".format(
    levels.MIN_SNR_BITS, above, len(speech)))
print("Biggest sample, away from the DC offset: {} of {} (full scale)".format(
    peak, levels.FULL_SCALE))
print("At {} cm.  Write these down.".format(DISTANCE_CM))
if clipped_frames:
    print("CLIPPING in {} frames: move back or speak more softly, then run again.".format(
        clipped_frames))
elif levels.snr_bits(level, floor) < levels.MIN_SNR_BITS:
    print("CHECK: speech is under {} bits above the floor. Move closer or quiet the room.".format(
        levels.MIN_SNR_BITS))
else:
    print("PASS: no clipping, and speech stands out from the noise.")
