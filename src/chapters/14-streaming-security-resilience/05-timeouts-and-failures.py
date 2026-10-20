# Chapter 14, Test 05: What does each kind of network failure look like?
# Makes six requests that are meant to go wrong and prints, for each, the kind
# of failure the Pico saw, whether a retry could help, and how long it took to
# find out. This is the table the chapter's timeout advice depends on. Needs
# Wi-Fi and the buddy server started with --debug:
#     cd server && BUDDY_TOKENS=... python3 buddy_server.py --debug
# Case 4 needs the address UNREACHABLE_HOST to answer nothing; the default
# (a reserved documentation address) normally does.
#
# PASS: every case ends the way its "expected" column says, and the last line
# says PASS. Write down the milliseconds: they are different on every network.

NAME = "05-timeouts-and-failures.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import buddy_config as cfg
import buddy_http
import wifi_link

UNREACHABLE_HOST = "192.0.2.1"      # TEST-NET-1: reserved, never assigned to a real machine
SHORT = 3                           # seconds: use a short timeout so the lab is quick

try:
    import secrets
    TOKEN = getattr(secrets, "buddy_token", "")
except ImportError:
    TOKEN = ""

try:
    wlan = wifi_link.connect(timeout_ms=cfg.CONNECT_TIMEOUT_MS, hostname=cfg.HOSTNAME)
except wifi_link.WifiError as e:
    print("FAIL: Wi-Fi: {}".format(e.reason))
    raise SystemExit

GOOD = {"X-Buddy-Token": TOKEN}
# (label, host, port, path, headers, timeout_s, expected kind or "ok")
CASES = (
    ("server is fine", cfg.BUDDY_HOST, cfg.BUDDY_PORT, "/v1/health", GOOD, SHORT, "ok"),
    ("wrong port", cfg.BUDDY_HOST, 9, "/v1/health", GOOD, SHORT, "refused"),
    ("server too slow (12 s)", cfg.BUDDY_HOST, cfg.BUDDY_PORT, "/v1/slow?ms=12000", GOOD, SHORT, "timeout"),
    ("no machine at address", UNREACHABLE_HOST, cfg.BUDDY_PORT, "/v1/health", GOOD, SHORT, "timeout"),
    ("wrong token", cfg.BUDDY_HOST, cfg.BUDDY_PORT, "/v1/events", {"X-Buddy-Token": "wrong"}, SHORT, "auth"),
    ("server error (flaky)", cfg.BUDDY_HOST, cfg.BUDDY_PORT, "/v1/flaky?fail=1", GOOD, SHORT, "busy"),
)

ok = True
print()
print("{:<24} {:<10} {:<9} {:>7}  {:<9} {}".format("case", "kind", "retry?", "ms", "expected", "check"))
for label, host, port, path, headers, timeout_s, expected in CASES:
    started = time.ticks_ms()
    try:
        status, _, body = buddy_http.request("GET", path, host, port, headers,
                                             timeout_s=timeout_s, total_s=timeout_s + 2)
        buddy_http.check_status(status, body)
        kind, retry = "ok", "-"
    except buddy_http.NetError as e:
        kind, retry = e.kind, "yes" if e.retryable else "no"
    ms = time.ticks_diff(time.ticks_ms(), started)
    good = kind == expected
    ok = ok and good
    print("{:<24} {:<10} {:<9} {:>7,}  {:<9} {}".format(label, kind, retry, ms, expected, "ok" if good else "DIFFERENT"))

# Reset the flaky counter so the next lab starts clean
try:
    buddy_http.request("GET", "/v1/flaky?fail=1", cfg.BUDDY_HOST, cfg.BUDDY_PORT, GOOD, timeout_s=SHORT)
except buddy_http.NetError:
    pass

print()
print("PASS" if ok else "CHECK: a case ended differently; the kind names the difference")
wifi_link.disconnect(wlan)

# Try This
#   1. Change SHORT to 8 (REQUEST_TIMEOUT_S). Which cases get slower, which do not?
#      Why does "wrong port" take almost no time?
#   2. A student's device is on the wrong network. Which row does that look like?
