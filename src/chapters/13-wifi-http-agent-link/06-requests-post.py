# Chapter 13, Test 06: The same POST, with the requests library
# Does what test 05 did in about five lines using requests.post(). If the
# library is not on the Pico yet, this script installs it with mip (which
# downloads one small file over your Wi-Fi from micropython.org). Needs the
# buddy server running, like test 05.
#
# PASS: status 200, the reply has speak / show / next_mode, the response is
# closed, and the last line says PASS. Write down the round trip time and the
# heap numbers.
#
# The library on the Pico depends on its version: older firmware has
# `urequests`, which has no timeout argument. This script says so if so.

NAME = "06-requests-post.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import time

import buddy_config
import wifi_link

REPLY_FIELDS = {"speak", "show", "next_mode"}

try:
    wlan = wifi_link.connect(timeout_ms=buddy_config.CONNECT_TIMEOUT_MS,
                             hostname=buddy_config.HOSTNAME)
except wifi_link.WifiError as e:
    print("FAIL: Wi-Fi: {}".format(e.reason))
    raise SystemExit

try:
    import requests
except ImportError:
    print("requests is not installed. Installing it with mip ...")
    import mip
    mip.install("requests")
    import requests

URL = "http://{}:{}/v1/ask".format(buddy_config.BUDDY_HOST, buddy_config.BUDDY_PORT)
request = {"device": buddy_config.DEVICE_ID, "kind": "question",
           "text": "what is due this week"}

gc.collect()
before = gc.mem_free()
ok = False
response = None
try:
    started = time.ticks_ms()
    response = requests.post(URL, json=request, timeout=buddy_config.REQUEST_TIMEOUT_S)
    elapsed = time.ticks_diff(time.ticks_ms(), started)
    print("status     :", response.status_code)
    reply = response.json()                 # reads the whole body: fine for ~100 bytes
    print("speak      :", reply["speak"])
    print("show       :", reply["show"])
    print("round trip : {} ms".format(elapsed))
    ok = response.status_code == 200 and set(reply) == REPLY_FIELDS
except TypeError as e:
    print("This version of the library does not accept timeout=: {}".format(e))
    print("Run  import mip; mip.install('requests')  to get a newer one.")
except OSError as e:
    print("FAIL: network error {}".format(e))
finally:
    if response is not None:
        response.close()                    # frees the socket; skip this and sockets run out
gc.collect()
print("heap: {} bytes free before, {} after".format(before, gc.mem_free()))

print()
print("PASS" if ok else "CHECK: no valid reply")
wifi_link.disconnect(wlan)

# Try This
#   1. Comment out response.close() and call requests.post() in a loop of 20.
#      What happens, and after how many calls?
#   2. Point URL at a path that does not exist (/v1/nothing). What is
#      response.status_code, and why is calling .json() on it risky?
