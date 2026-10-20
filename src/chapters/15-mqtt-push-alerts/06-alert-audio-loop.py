# Chapter 15, Test 06: Alerts inside the 40 ms audio loop
# The Chapter 8 loop (read a 40 ms microphone frame, do the loudness work) with
# MQTT added: one link.service() per pass, which polls with check_msg(). When
# an alert arrives it is drawn in the message region and a short beep plays.
# While the beep plays, and for a quiet tail after it, the microphone frames
# are read but ignored, so the device does not hear itself (Chapter 8).
# Needs the microphone, speaker, display, Wi-Fi and a broker.
#
# PASS: the line printed every second keeps "frames" at about 25, "worst work"
# stays under 40 ms, and no pass is reported as an overrun, even while you
# publish alerts:
#   python3 server/publish_alert.py --room 214 --type test --title "Algebra II test" \
#       --when "Tomorrow 8:00 AM" --text "Algebra II test tomorrow."
# Each new alert id shows on the display and beeps once; a repeated id does not.
# WRITE DOWN: the worst work (ms) in the second an alert arrived, and whether
# any pass was an overrun (an overrun can lose microphone audio).

NAME = "06-alert-audio-loop.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from machine import I2S, Pin

import alert_view
import config
import mqtt_common as mc

RUN_SECONDS = 60
FRAME_SAMPLES = 512
FRAME_BYTES = FRAME_SAMPLES * 4
FRAME_US = FRAME_SAMPLES * 1_000_000 // config.MIC_SAMPLE_RATE        # 40000
SHOW_MS = 8000                  # how long an alert stays on screen
BEEP_HZ = 880
BEEP_MS = 120
BEEP_VOLUME = min(config.VOLUME, 30)       # percent; kept quiet on purpose
TAIL_MS = 120                   # Chapter 8's quiet tail (measured 80 to 120 ms)
SPEAKER_IBUF = 8192
LOG2 = math.log(2)


def loudness(buf):
    """Chapter 8's calculation: the stand-in for the real per-frame work."""
    samples = [s >> config.MIC_SAMPLE_SHIFT for s in struct.unpack("<512i", buf)]
    middle = sum(samples) // FRAME_SAMPLES
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2


def make_beep(rate=config.MIC_SAMPLE_RATE):
    """BEEP_MS of a sine at BEEP_HZ, 16-bit mono, with a 10 ms fade at each end."""
    count = rate * BEEP_MS // 1000
    fade = rate * 10 // 1000
    out = bytearray(count * 2)
    for i in range(count):
        gain = min(1.0, i / fade, (count - 1 - i) / fade)
        value = int(32767 * BEEP_VOLUME / 100 * gain * math.sin(2 * math.pi * BEEP_HZ * i / rate))
        struct.pack_into("<h", out, i * 2, value)
    return out


BEEP = make_beep()
speaker = None
speaker_off_at = 0
deaf_until = 0


def start_beep():
    """Queue the beep; it plays by itself while the loop keeps reading frames."""
    global speaker, speaker_off_at, deaf_until
    if speaker is None:
        config.set_gain()
        speaker = I2S(config.I2S_SPEAKER_ID,
                      sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
                      sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                      format=I2S.MONO, rate=config.MIC_SAMPLE_RATE, ibuf=SPEAKER_IBUF)
    speaker.write(BEEP)          # 3,072 bytes fit in the 8,192-byte buffer: returns quickly
    speaker_off_at = time.ticks_add(time.ticks_ms(), BEEP_MS + 50)    # let it drain
    deaf_until = time.ticks_add(speaker_off_at, TAIL_MS)


mc.connect_wifi()
link = mc.Link()
display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
mic = config.init_microphone()
buf = bytearray(FRAME_BYTES)
print("Frame {} us. Beep {} bytes. Listening for {} s.".format(FRAME_US, len(BEEP), RUN_SECONDS))

shown_until = None
frames = deaf_frames = overruns = shown = 0
worst_work = 0
second_start = time.ticks_ms()
end = time.ticks_add(second_start, RUN_SECONDS * 1000)
try:
    for _ in range(8):                                   # the microphone's start-up
        mic.readinto(buf)
    while time.ticks_diff(time.ticks_ms(), end) < 0:
        mic.readinto(buf)                                # blocks until a frame is ready
        t0 = time.ticks_us()
        now = time.ticks_ms()

        link.service()                                   # MQTT: never sleeps
        alert = link.take()
        if alert:
            alert_view.show_alert(display, alert)
            start_beep()
            shown_until = time.ticks_add(now, SHOW_MS)
            shown += 1
            print("ALERT [{}] {} | {}".format(alert["type"], alert["title"], alert["when"]))

        if speaker is not None and time.ticks_diff(now, speaker_off_at) >= 0:
            speaker.deinit()
            speaker = None
        if shown_until is not None and time.ticks_diff(now, shown_until) >= 0:
            alert_view.clear_alert(display)
            shown_until = None

        if time.ticks_diff(now, deaf_until) < 0:
            deaf_frames += 1                             # our own beep: do not listen
        else:
            loudness(buf)

        work = time.ticks_diff(time.ticks_us(), t0)
        worst_work = max(worst_work, work)
        if work > FRAME_US:
            overruns += 1
        frames += 1
        if time.ticks_diff(now, second_start) >= 1000:
            print("frames {:>2}  deaf {:>2}  worst work {:>5.1f} ms  overruns {}  link {}  "
                  "dupes {}  shown {}".format(
                      frames, deaf_frames, worst_work / 1000, overruns,
                      "up" if link.up else "DOWN", link.dupes, shown))
            frames = deaf_frames = 0
            worst_work = 0
            second_start = now
finally:
    mic.deinit()
    if speaker is not None:
        speaker.deinit()
    alert_view.clear_alert(display)
    link.close()
print("Done. {} alert(s) shown, {} overrun(s) in the last second printed.".format(shown, overruns))

# Try This
#   1. Stop the broker for 20 seconds. Look at "worst work" during the connect
#      attempts. How long does one failed attempt freeze the loop, and how many
#      40 ms frames is that? (CONNECT_TIMEOUT_S in mqtt_common.py sets the limit.)
#   2. Set TAIL_MS to 0. Does the device hear its own beep? (Raise
#      BEEP_VOLUME to make it obvious, but keep your ears away from the speaker.)
#   3. Add a button check from Chapter 7 so that a long press of MODE hides the
#      alert early.
