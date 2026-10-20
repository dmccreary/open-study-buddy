#!/usr/bin/env python3
"""Chapter 17: follow the data. Prints, for each hop of a spoken question,
what travels, who can see it, where it is stored, and how long (the DESIGN
default this book recommends), then does the audio-volume arithmetic.

Run on your computer:  python3 data_flow.py            (push-to-talk)
                       python3 data_flow.py --always   (always-on streaming)

Nothing here is measured. The "who can see" and "stored" columns are design
choices to check against YOUR school's setup; edit HOPS to match it.
"""
import sys

# hop, what travels, who can see it, stored where, kept how long (design default)
HOPS = [
    ("1 Microphone -> Pico", "digital audio samples", "the Pico only",
     "RAM buffer, overwritten", "about 0.4 s ring + the recording buffer"),
    ("2 Pico -> Wi-Fi -> server", "audio chunks after a button press",
     "anyone who can capture the school Wi-Fi traffic, unless HTTPS (Ch. 14)",
     "not stored by the network", "none"),
    ("3 Server: speech-to-text", "the audio, then the words",
     "the server's admin; the STT service if it is a cloud vendor",
     "memory only (rule: audio not stored)", "0 days for audio"),
    ("4 Server: the agent / LLM", "the question text (+ calendar items)",
     "the server's admin; the LLM vendor if it is hosted",
     "transcript log: OFF by default", "7 days at most if turned on"),
    ("5 Server: text-to-speech", "the reply text, then reply audio",
     "the server's admin; the TTS service if it is a cloud vendor",
     "memory only", "0 days"),
    ("6 Server -> Pico", "reply text + reply audio", "same as hop 2",
     "RAM, then overwritten", "none"),
    ("7 MQTT alerts", "event text such as 'TEST: Biology'",
     "everyone subscribed to the topic; the broker's admin",
     "retained message on the broker", "until replaced"),
    ("8 Device status (MQTT)", "online/offline, volume, last wake time",
     "the broker's admin and subscribers", "retained message", "until replaced"),
]

def show():
    for hop, what, who, stored, kept in HOPS:
        print(hop)
        print("    travels :", what)
        print("    sees it :", who)
        print("    stored  :", stored)
        print("    kept    :", kept)

def arithmetic(always):
    rate, bytes_per_sample = 12800, 2          # 16-bit mono at the mic rate
    per_second = rate * bytes_per_sample
    print()
    print("Audio volume (16-bit mono at {} Hz = {:,} bytes per second):".format(rate, per_second))
    if always:
        per_hour = per_second * 3600
        # Cedar Ridge day: 8:00 to 2:35 pm = 6 h 35 min
        hours = 6 + 35 / 60
        devices = 25
        total = per_hour * hours * devices
        print("  streaming all the time: {:,} bytes per hour per device".format(per_hour))
        print("  25 devices, {:.2f} school hours: {:.1f} GB leave the classroom per day".format(
            hours, total / 1e9))
    else:
        question_s, questions = 4, 10          # ILLUSTRATIVE assumptions
        sent = per_second * question_s * questions
        print("  assume {} questions of {} s in a class period (illustrative)".format(
            questions, question_s))
        print("  push-to-talk sends {:,} bytes = {:.0f} KB per device per period".format(
            sent, sent / 1000))
        hours = 55 / 60                        # one 55-minute period
        stream = per_second * 3600 * hours
        print("  streaming the same period would send {:,.0f} bytes = {:.1f} MB ({:.0f} times more)".format(
            stream, stream / 1e6, stream / sent))

if __name__ == "__main__":
    always = "--always" in sys.argv
    show()
    arithmetic(always)
