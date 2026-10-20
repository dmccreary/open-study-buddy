# Chapter 14, Test 06: Retry with backoff, then fall back to the offline cache
# At start the device downloads the school events from the server and saves them
# in events_cache.json (only when they changed). Then:
#   MODE : ask "when is my next test" over the network, retrying with backoff;
#          if every attempt fails, answer from the cache instead and say OFFLINE
#   UP   : practice the retries: calls /v1/flaky?fail=2, which the server fails
#          twice before it answers (the server needs --debug)
# The status region always says which state the link is in. Needs the display,
# MODE and UP buttons, Wi-Fi, and the buddy server. To see the fallback, stop the
# server (or turn Wi-Fi off at the router) and press MODE.
#
# PASS: with the server up, MODE shows the server's answer and UP shows
# "retry 1/3", "retry 2/3" then "ok"; with the server stopped, MODE ends with
# "OFFLINE" and the cached answer after about the worst-case time in test 02.

NAME = "06-retry-fallback.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import time

import config
import buddy_client
import buddy_config as cfg
import buddy_http
import offline
import wifi_link
from screen import Screen

screen = Screen("BUDDY LINK")
mode_button, up_button, _ = config.init_buttons()

screen.status("joining", config.YELLOW)
try:
    wlan = wifi_link.connect(timeout_ms=cfg.CONNECT_TIMEOUT_MS, hostname=cfg.HOSTNAME)
    online = True
except wifi_link.WifiError as e:
    wlan, online = None, False
    screen.status("no Wi-Fi", config.RED)
    screen.message(e.reason, config.RED)


def on_wait(n, total, wait, error):
    screen.status("retry {}/{}".format(n, total - 1), config.YELLOW)
    screen.hint("{} - waiting {} ms".format(error.kind, wait))
    print("attempt {} failed ({}); waiting {} ms".format(n, error, wait))
    # nothing here draws a full screen: only the two text regions change


def sync_events():
    try:
        events = buddy_client.events()
        changed = offline.save_events(events)
        print("events synced: {} events, {}".format(len(events), "saved" if changed else "unchanged"))
        return True
    except buddy_http.NetError as e:
        print("could not sync events:", e)
        return False


def ask_with_fallback(text):
    started = time.ticks_ms()
    try:
        reply = buddy_client.ask(text, on_wait=on_wait)
        screen.status("online", config.GREEN)
        screen.message(reply["show"], config.WHITE)
        return "network", reply["speak"]
    except buddy_http.NetError as e:
        print("giving up on the network:", e)
        if e.kind == "auth":
            screen.status("bad token", config.RED)
            screen.message("check secrets.py", config.RED)
            return "error", str(e)
        speak, show = offline.decide(text, offline.load_events())
        screen.status("OFFLINE", config.MAGENTA)
        screen.message(show, config.WHITE)
        return "cache", speak
    finally:
        print("took {} ms".format(time.ticks_diff(time.ticks_ms(), started)))


if online:
    screen.status("syncing", config.YELLOW)
    if sync_events():
        screen.status("online", config.GREEN)
    else:
        screen.status("no server", config.MAGENTA)
else:
    screen.status("OFFLINE", config.MAGENTA)
screen.hint("MODE ask   UP practice")

while True:
    if mode_button.value() == 0:
        screen.hint("asking...")
        source, speak = ask_with_fallback("when is my next test")
        print("answer from the {}: {}".format(source, speak))
        screen.hint("MODE ask   UP practice")
        while mode_button.value() == 0:
            time.sleep_ms(10)
    elif up_button.value() == 0:
        started = time.ticks_ms()
        try:
            buddy_client._with_retry(
                lambda: buddy_client._json_call("GET", "/v1/flaky?fail=2"), on_wait, True)
            screen.status("ok", config.GREEN)
            screen.message("succeeded after retries", config.WHITE)
        except buddy_http.NetError as e:
            screen.status(e.kind, config.RED)
        print("flaky practice took {} ms".format(time.ticks_diff(time.ticks_ms(), started)))
        while up_button.value() == 0:
            time.sleep_ms(10)
    gc.collect()
    time.sleep_ms(20)
