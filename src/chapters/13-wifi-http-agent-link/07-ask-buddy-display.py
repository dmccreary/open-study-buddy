# Chapter 13, Test 07: Ask the buddy from the device, with the link on the screen
# Joins Wi-Fi, then each press of MODE sends the next question in QUESTIONS to
# the buddy server and shows the reply's "show" text on the round display.
# The status region (top) says what the link is doing: Wi-Fi state, asking,
# ok, or an error. The message region (bottom) shows the answer.
# Needs the display, the MODE button, and the buddy server running.
#
# PASS: the status region walks through "joining" -> "online"; pressing MODE
# shows "asking..." and then the server's answer; stopping the server and
# pressing MODE shows an error in the status region (and the device keeps
# running instead of crashing).

NAME = "07-ask-buddy-display.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import json
import socket
import time

import config
import buddy_config
import rawhttp
import wifi_link

SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
# Regions from Chapter 6: status bar and agent message (x, y, width in characters)
STATUS = (120, 30, 15)
MESSAGE = (60, 240, 30)
QUESTIONS = ("when is my next test", "what is due this week", "do I have anything big this week")

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
button = config.init_buttons()[0]       # MODE


def put(region, text, color):
    """Draw text in a region, padded with spaces so the old text is covered."""
    x, y, width = region
    display.text(SMALL, text[:width].ljust(width), x, y, color, config.BLACK)


def status(text, color=config.YELLOW):
    print("status:", text)
    put(STATUS, text, color)


def ask(text):
    """One POST. Returns the reply dict, or raises OSError / ValueError."""
    request = {"device": buddy_config.DEVICE_ID, "kind": "question", "text": text}
    raw = rawhttp.build_post(buddy_config.BUDDY_HOST, buddy_config.BUDDY_PORT,
                             "/v1/ask", request)
    addr = socket.getaddrinfo(buddy_config.BUDDY_HOST, buddy_config.BUDDY_PORT)[0][-1]
    sock = socket.socket()
    sock.settimeout(buddy_config.REQUEST_TIMEOUT_S)
    try:
        sock.connect(addr)
        sock.send(raw)
        code, headers, body = rawhttp.read_response(sock, buddy_config.MAX_REPLY_BYTES)
    finally:
        sock.close()
    if code != 200:
        raise ValueError("server said {}".format(code))
    return json.loads(body)


config.centered_text(display, SMALL, "ASK BUDDY", 90, config.CYAN)
status("joining")
try:
    wlan = wifi_link.connect(timeout_ms=buddy_config.CONNECT_TIMEOUT_MS,
                             hostname=buddy_config.HOSTNAME,
                             show=lambda t: status(t.split(" (")[0], config.YELLOW))
except wifi_link.WifiError as e:
    status("Wi-Fi error", config.RED)
    put(MESSAGE, e.reason, config.RED)
    raise SystemExit
status("online", config.GREEN)
put(MESSAGE, "press MODE to ask", DIM)

index = 0
while True:
    if button.value() != 0:
        time.sleep_ms(10)
        continue
    time.sleep_ms(30)                                 # crude debounce
    if button.value() != 0:
        continue
    question = QUESTIONS[index % len(QUESTIONS)]
    index += 1
    put(MESSAGE, question, DIM)
    status("asking...", config.YELLOW)
    started = time.ticks_ms()
    try:
        if not wlan.isconnected():
            raise OSError("Wi-Fi lost")
        reply = ask(question)
        status("ok {} ms".format(time.ticks_diff(time.ticks_ms(), started)), config.GREEN)
        put(MESSAGE, reply["show"], config.WHITE)
        print("speak:", reply["speak"])
    except (OSError, ValueError, KeyError) as e:
        status("error", config.RED)
        put(MESSAGE, str(e), config.RED)
        print("error:", e)
    gc.collect()
    while button.value() == 0:                         # wait for release
        time.sleep_ms(10)

# Try This
#   1. Stop the server. How long does "asking..." last before "error"? Compare
#      with REQUEST_TIMEOUT_S and with test 05's refused-connection time.
#   2. Move the "ok ... ms" number into the message region. Which region redraw
#      is cheaper, and why? (Chapter 6.)
