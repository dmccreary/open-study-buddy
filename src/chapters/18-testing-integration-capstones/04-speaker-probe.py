# Chapter 18, Probe 04: Speaker
# Plays a quiet beep, then (if the microphone is wired) plays a 1 kHz tone and
# listens to it with the microphone: the device hearing itself (Chapter 8) is a
# way to check the speaker without a human. Needs the amplifier and speaker;
# the microphone is optional.
#
# PASS: you hear the beep, and the microphone line says it heard the tone at
# least 2.0 bits above the room. If the microphone cannot judge, the result is
# ASK and you decide.

NAME = "04-speaker-probe.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import checks
import config

print("Beep: a quiet 1 kHz tone for 1 second.")
speaker = checks.open_speaker(config)
chunk = checks.tone_chunk(config)
try:
    for _ in range(25):
        speaker.write(chunk)
finally:
    checks.close_speaker(speaker, config)
time.sleep_ms(300)

print("Loopback: the microphone listens while the tone plays.")
verdict, detail, rise = checks.check_speaker(config, with_mic=True)
print()
print("RESULT:", verdict, "-", detail)
if verdict != checks.PASS:
    print("If you heard nothing, check (Chapter 4): amplifier VIN and GND, then BCLK GP20,")
    print("LRC GP21, DIN GP19. If it buzzes or crackles, lower VOLUME in config.py.")
