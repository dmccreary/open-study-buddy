# Chapter 14, Test 04: Hold to talk, upload in chunks, hear the answer
# The whole push-to-talk round trip over HTTP. Hold MODE and talk; on release the
# recording (16-bit mono, 12,800 Hz) is POSTed to /v1/voice in UPLOAD_CHUNK_BYTES
# pieces with the token in an X-Buddy-Token header; the server turns it into text
# (speech-to-text), decides on an answer, and makes speech (text-to-speech); the
# Pico shows the answer and streams the speech to the speaker in chunks. Press MODE
# while it speaks to stop it (barge-in). Needs the whole kit and the buddy server:
#     export BUDDY_TOKENS="the-same-token-as-in-secrets.py"
#     cd server && python3 buddy_server.py
# and  buddy_token = "..."  in secrets.py. With the server's stub speech-to-text
# the answer is always about "when is my next test": it checks the pipeline, not
# your voice. The speech is a row of beeps, one per word.
#
# PASS: the display walks through recording -> uploading -> thinking -> speaking
# -> ready, the console prints the timings below, and you hear beeps. Write down
# the timings: the chapter's latency table is an estimate until you do.

NAME = "04-upload-voice.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import time

import config
import buddy_client
import buddy_config
import buddy_http
import utterance
import wifi_link
from screen import Screen

screen = Screen("PUSH TO TALK")
button = config.init_buttons()[0]       # MODE

screen.status("joining", config.YELLOW)
try:
    wlan = wifi_link.connect(timeout_ms=buddy_config.CONNECT_TIMEOUT_MS,
                             hostname=buddy_config.HOSTNAME)
except wifi_link.WifiError as e:
    screen.status("Wi-Fi error", config.RED)
    screen.message(e.reason, config.RED)
    raise SystemExit

pcm = utterance.make_buffer(buddy_config.MAX_UTTERANCE_S)     # allocated once, first
chunk_buf = bytearray(buddy_config.UPLOAD_CHUNK_BYTES)        # reused for every piece of speech


class Interrupted(Exception):
    pass


def play(path):
    """Stream the speech into the speaker. Returns (bytes, ms_to_first_audio, interrupted)."""
    speaker = None
    state = {"bytes": 0, "first": None, "t0": time.ticks_ms()}

    def sink(view):
        nonlocal speaker
        if button.value() == 0 and state["bytes"]:           # barge-in
            raise Interrupted()
        if speaker is None:
            speaker = utterance.Speaker()
        speaker.write(view)
        if state["first"] is None:
            state["first"] = time.ticks_diff(time.ticks_ms(), state["t0"])
        state["bytes"] += len(view)

    interrupted = False
    try:
        buddy_client.speech(path, config.VOLUME, sink, chunk_buf)
    except Interrupted:
        interrupted = True
    finally:
        if speaker:
            speaker.finish(drain=not interrupted)           # Chapter 8: let it drain, unless interrupted
    return state["bytes"], state["first"], interrupted


def on_wait(n, total, wait, error):
    screen.status("retry {}/{}".format(n, total - 1), config.YELLOW)
    screen.message("{} - wait {} ms".format(error.kind, wait), config.YELLOW)


while True:
    screen.status("hold MODE", config.GREEN)
    screen.message("press and talk", config.GRAY)
    while button.value() != 0:
        time.sleep_ms(10)

    screen.status("recording", config.RED)
    t0 = time.ticks_ms()
    count, stats = utterance.record(button, pcm)
    t_record = time.ticks_diff(time.ticks_ms(), t0)
    if count < utterance.RATE * 2 // 5:                      # under 0.2 s: a bump, not a question
        screen.message("too short", config.YELLOW)
        time.sleep_ms(800)
        continue

    screen.status("uploading", config.YELLOW)
    t1 = time.ticks_ms()
    try:
        reply = buddy_client.voice(
            pcm, count, utterance.RATE, on_wait=on_wait,
            on_progress=lambda sent, total: screen.message(
                "{} of {} KB".format(sent // 1024, total // 1024), config.YELLOW)
            if sent % 16384 < buddy_config.UPLOAD_CHUNK_BYTES else None)
    except buddy_http.NetError as e:
        screen.status("bad token" if e.kind == "auth" else e.kind, config.RED)
        screen.message(e.detail or str(e), config.RED)
        time.sleep_ms(2000)
        continue
    t_reply = time.ticks_diff(time.ticks_ms(), t1)

    screen.status("speaking", config.CYAN)
    screen.message(reply["show"], config.WHITE)
    print("heard  :", reply.get("heard"))
    print("answer :", reply["speak"])
    try:
        n, first, interrupted = play(reply["audio"])
    except buddy_http.NetError as e:
        screen.status(e.kind, config.RED)
        n, first, interrupted = 0, None, False
    gc.collect()

    print("record {} ms ({:,} bytes) | upload+server {} ms | first audio {} ms after the reply | "
          "speech {:,} bytes{} | heap {:,}".format(
              t_record, count, t_reply, first, n, " INTERRUPTED" if interrupted else "", gc.mem_free()))
    while button.value() == 0 and not interrupted:
        time.sleep_ms(10)
    # An interrupted answer leaves MODE held: the loop goes straight to recording.
    if interrupted:
        screen.status("recording", config.RED)

# Try This
#   1. Hold MODE for 1 s and then for 5 s. How does "upload+server" change? Is it
#      proportional to the bytes?
#   2. Set UPLOAD_CHUNK_BYTES to 512 in buddy_config.py and compare upload time.
#   3. Stop the server mid-way and press MODE. Which status words do you see?
