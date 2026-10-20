# Chapter 13, Test 05: POST a question to the buddy server with a plain socket
# Joins Wi-Fi, opens a TCP connection to the buddy server, sends the request
# from test 04 as raw bytes, reads the reply, and closes the socket in a
# finally block. No library needed. Start the server first on your computer:
#     cd server && python3 buddy_server.py
# and put the address it prints into buddy_config.py (BUDDY_HOST).
#
# PASS: status 200, a reply with speak / show / next_mode, the round trip time
# is printed, and the last line says PASS. Write down the round trip time.

NAME = "05-socket-post.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import json
import socket
import time

import buddy_config
import rawhttp
import wifi_link

REPLY_FIELDS = {"speak", "show", "next_mode"}

try:
    wlan = wifi_link.connect(timeout_ms=buddy_config.CONNECT_TIMEOUT_MS,
                             hostname=buddy_config.HOSTNAME)
except wifi_link.WifiError as e:
    print("FAIL: Wi-Fi: {}".format(e.reason))
    raise SystemExit
print("Pico address:", wlan.ifconfig()[0])

request = {"device": buddy_config.DEVICE_ID, "kind": "question",
           "text": "when is my next test"}
raw = rawhttp.build_post(buddy_config.BUDDY_HOST, buddy_config.BUDDY_PORT,
                         "/v1/ask", request)

gc.collect()
before = gc.mem_free()
addr = socket.getaddrinfo(buddy_config.BUDDY_HOST, buddy_config.BUDDY_PORT)[0][-1]
sock = socket.socket()
sock.settimeout(buddy_config.REQUEST_TIMEOUT_S)     # every wait gives up
ok = False
try:
    started = time.ticks_ms()
    sock.connect(addr)
    connected = time.ticks_diff(time.ticks_ms(), started)
    sock.send(raw)
    status, headers, body = rawhttp.read_response(sock, buddy_config.MAX_REPLY_BYTES)
    total = time.ticks_diff(time.ticks_ms(), started)
    print()
    print("status      :", status)
    print("body        :", body.decode())
    print("connect took {} ms, whole round trip {} ms".format(connected, total))
    reply = json.loads(body)
    ok = status == 200 and set(reply) == REPLY_FIELDS
except OSError as e:
    print("FAIL: network error {} (is the server running? is BUDDY_HOST right?)".format(e))
finally:
    sock.close()                                    # always, even after an error
gc.collect()
print("heap: {} bytes free before, {} after".format(before, gc.mem_free()))

print()
print("PASS" if ok else "CHECK: no valid reply")
wifi_link.disconnect(wlan)

# Try This
#   1. Stop the server and run again. How long until the error appears, and
#      which error number is it? (Compare with REQUEST_TIMEOUT_S.)
#   2. Change BUDDY_PORT to 9999. Compare this failure with the one above.
