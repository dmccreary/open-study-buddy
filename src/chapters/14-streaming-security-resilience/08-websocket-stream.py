# Chapter 14, Test 08: Stream the speech over a WebSocket, with barge-in
# Hold MODE and talk. Each 40 ms of speech is sent as it is converted (one
# 1,024-byte WebSocket frame), so nothing larger than a frame is ever held in
# memory and the server starts work the moment you let go. The reply and the
# spoken answer come back over the same connection. Press MODE while the answer
# is playing to interrupt it (barge-in): the Pico sends {"event": "cancel"},
# stops the speaker at once, and starts recording your next question. Needs the
# whole kit and the WebSocket server:
#     pip install websockets
#     cd server && BUDDY_TOKENS=... python3 ws_server.py
# This is the always-on style of link, driven here by a button. Listening
# without a button needs school and parent approval: see Chapter 17.
# UNTESTED ON THE KIT: wsclient.py was tested against the real server from a
# computer, never from the Pico. Report what you see.
#
# PASS: the status words walk through connecting -> recording -> streaming ->
# speaking -> done; the console prints the worst time one frame took to send
# (it must stay far below 400 ms or the microphone loses audio); and pressing
# MODE during the answer stops it within about one frame.

NAME = "08-websocket-stream.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import json
import time

import config
import backoff
import buddy_config as cfg
import buddy_http
import utterance
import wifi_link
import wsclient
from screen import Screen

screen = Screen("STREAMING")
button = config.init_buttons()[0]       # MODE

try:
    import secrets
    TOKEN = getattr(secrets, "buddy_token", "")
except ImportError:
    TOKEN = ""

screen.status("joining", config.YELLOW)
try:
    wlan = wifi_link.connect(timeout_ms=cfg.CONNECT_TIMEOUT_MS, hostname=cfg.HOSTNAME)
except wifi_link.WifiError as e:
    screen.status("Wi-Fi error", config.RED)
    screen.message(e.reason, config.RED)
    raise SystemExit

stage = bytearray(cfg.STREAM_CHUNK_BYTES)        # one frame: allocated once


def open_stream():
    def attempt():
        return wsclient.WebSocket.connect(
            cfg.BUDDY_HOST, cfg.BUDDY_WS_PORT, "/v1/stream",
            {"X-Buddy-Token": TOKEN}, cfg.REQUEST_TIMEOUT_S)
    return backoff.retry(attempt, cfg.RETRY_ATTEMPTS, cfg.BACKOFF_BASE_MS, cfg.BACKOFF_CAP_MS,
                         lambda n, t, wait, e: screen.status("retry {}/{}".format(n, t - 1), config.YELLOW))


def talk_and_listen(already_pressed):
    """One utterance. Returns True if the answer was interrupted (button still down)."""
    screen.status("connecting", config.YELLOW)
    ws = open_stream()
    speaker = None
    try:
        ws.send_text(json.dumps({"event": "start", "rate": utterance.RATE, "volume": config.VOLUME}))
        timing = {"worst_us": 0, "frames": 0}

        def send_frame(view):
            t = time.ticks_us()
            ws.send_binary(view)
            timing["worst_us"] = max(timing["worst_us"], time.ticks_diff(time.ticks_us(), t))
            timing["frames"] += 1

        screen.status("streaming", config.RED)
        count, stats = utterance.record(button, stage, chunk_sink=send_frame)
        ws.send_text('{"event": "end"}')
        print("sent {:,} bytes in {} frames; slowest frame {:,} us; conversion worst {:,} us".format(
            count, timing["frames"], timing["worst_us"], stats["worst_us"]))
        if count < utterance.RATE * 2 // 5:
            screen.message("too short", config.YELLOW)
            ws.send_text('{"event": "cancel"}')
            return False

        screen.status("thinking", config.YELLOW)
        interrupted = False
        got = 0
        while True:
            kind, payload = ws.recv()
            if kind == "text":
                message = json.loads(payload)
                if message["type"] == "reply":
                    screen.message(message["show"], config.WHITE)
                    screen.status("speaking", config.CYAN)
                    print("heard:", message.get("heard"), "| answer:", message["speak"])
                elif message["type"] == "audio_end":
                    break
            else:
                if button.value() == 0 and got:                  # barge-in
                    ws.send_text('{"event": "cancel"}')
                    interrupted = True
                    break
                if speaker is None:
                    speaker = utterance.Speaker()
                speaker.write(payload)
                got += len(payload)
        print("played {:,} bytes{}".format(got, " (interrupted)" if interrupted else ""))
        return interrupted
    finally:
        if speaker:
            speaker.finish(drain=False if button.value() == 0 else True)
        ws.close()


interrupted = False
while True:
    if not interrupted:
        screen.status("hold MODE", config.GREEN)
        screen.message("press and talk", config.GRAY)
        while button.value() != 0:
            time.sleep_ms(10)
    try:
        interrupted = talk_and_listen(interrupted)
    except (buddy_http.NetError, wsclient.WsClosed, OSError) as e:
        interrupted = False
        screen.status("link error", config.RED)
        screen.message(str(e)[:30], config.RED)
        print("error:", e)
        time.sleep_ms(2000)
    if not interrupted:
        while button.value() == 0:
            time.sleep_ms(10)

# Try This
#   1. Stop the server while you are mid-sentence. What does the display say, and
#      how long until it says it?
#   2. Compare the console's "slowest frame" with 400 ms. What would make it jump?
