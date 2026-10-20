# Chapter 14, Test 07: What does HTTPS cost on the Pico, and what does it check?
# Opens three connections to the buddy server and prints, for each, how long the
# connection took, how much heap it used, and whether it worked:
#   1. plain HTTP                                   (no encryption)
#   2. HTTPS, certificate NOT checked (CERT_NONE)   (encrypted; anyone can be the server)
#   3. HTTPS, certificate checked against ca.der    (encrypted; the server is who it claims)
# Then it points case 3 at a certificate it should NOT trust, to prove the check
# does something. LAB DEMO: this is the least-tested part of the book on the real
# kit. Needs Wi-Fi and, on the server computer:
#     cd server && ./make-cert.sh <server address>
#     BUDDY_TOKENS=... python3 buddy_server.py --port 8080 &
#     BUDDY_TOKENS=... python3 buddy_server.py --port 8443 --tls server.pem server.key
# and ca.der copied to the Pico:  mpremote fs cp server/ca.der :ca.der
# The Pico's clock must be roughly right for case 3 (a certificate has dates).
# This script tries NTP (needs internet); on a school LAN set it from your
# computer instead:  mpremote rtc --set
#
# PASS: cases 1 and 2 print "ok"; case 3 prints "ok" when ca.der is the server's
# certificate and the clock is right; the last case prints "refused (good)".
# Write down the heap and time columns: the chapter's TLS cost is an estimate.

NAME = "07-tls-probe.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import time

import buddy_config as cfg
import buddy_http
import wifi_link

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

try:
    import ntptime
    ntptime.settime()
    print("clock set by NTP:", time.localtime()[:6])
except Exception as e:
    print("NTP failed ({}). Clock says {}. If case 3 fails with a date error, run "
          "`mpremote rtc --set` on your computer.".format(e, time.localtime()[:6]))

try:
    with open(cfg.CA_FILE, "rb") as f:
        CA = f.read()
    print("{} loaded: {} bytes".format(cfg.CA_FILE, len(CA)))
except OSError:
    CA = None
    print("No {} on the Pico: case 3 will be skipped.".format(cfg.CA_FILE))


def probe(label, port, tls, cadata):
    gc.collect()
    before = gc.mem_free()
    started = time.ticks_ms()
    try:
        sock = buddy_http.open_socket(cfg.BUDDY_HOST, port, cfg.REQUEST_TIMEOUT_S, tls, cadata)
    except buddy_http.NetError as e:
        print("{:<34} {:<22} {}".format(label, "-", "{}: {}".format(e.kind, e.detail[:60])))
        return False
    connect_ms = time.ticks_diff(time.ticks_ms(), started)
    used = before - gc.mem_free()
    sock.close()
    gc.collect()
    print("{:<34} {:>6} ms {:>9,} B  ok".format(label, connect_ms, used))
    return True


print()
print("{:<34} {:>9} {:>11}".format("case", "connect", "heap used"))
results = []
results.append(probe("1. plain HTTP", cfg.BUDDY_PORT, False, None))
results.append(probe("2. HTTPS, certificate not checked", cfg.BUDDY_TLS_PORT, True, None))
if CA:
    results.append(probe("3. HTTPS, certificate checked", cfg.BUDDY_TLS_PORT, True, CA))
    # A certificate that is not the server's: flip one byte in the middle of ours.
    bad = bytearray(CA)
    bad[len(bad) // 2] ^= 0xFF
    refused = not probe("4. wrong certificate (must fail)", cfg.BUDDY_TLS_PORT, True, bytes(bad))
    print("   -> {}".format("refused (good)" if refused else "ACCEPTED (BAD: nothing is being checked)"))
    results.append(refused)

print()
print("Case 2 is encrypted but would also connect to an impostor. Only case 3 checks who is there.")
print("PASS" if all(results) else "CHECK: see the lines above")
wifi_link.disconnect(wlan)

# Try This
#   1. Run it again. Is the second HTTPS connection faster or slower? Why might
#      the first be different?
#   2. Look at "heap used" for case 2. Compare it with your free heap from
#      Chapter 2's memory report: how many seconds of 16-bit audio is that?
