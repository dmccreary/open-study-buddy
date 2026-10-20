# Chapter 13, Test 08: Can this Pico find "buddy.local"? (mDNS)
# mDNS lets a device find another by a ".local" name instead of a number. The
# chapter says support for RESOLVING .local names on the Pico 2 W is uncertain,
# so this script simply asks: it tries to resolve each name in NAMES and prints
# the answer, or the error, and how long it took. Then it shows the fallback:
# the fixed address in buddy_config.py. Needs Wi-Fi only; the server need not run.
#
# PASS: the script finishes and prints a result for every name, and the last
# line says PASS. Either answer for ".local" is useful. Write down what your
# firmware did and which MicroPython version it was (the chapter has a TODO
# for this).

NAME = "08-mdns-check.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import sys
import socket
import time
import network

import buddy_config
import wifi_link

# Edit these: the ".local" name is whatever your server computer calls itself
# (a Raspberry Pi called "raspberrypi" answers to raspberrypi.local).
NAMES = ("buddy.local", "raspberrypi.local", buddy_config.BUDDY_HOST)


def looks_like_ip(text):
    parts = text.split(".")
    return len(parts) == 4 and all(p.isdigit() and int(p) < 256 for p in parts)


def resolve(name, port):
    """Return the IP address for name, or None. A dotted address needs no lookup."""
    if looks_like_ip(name):
        return name
    try:
        return socket.getaddrinfo(name, port)[0][-1][0]
    except OSError:
        return None


try:
    wlan = wifi_link.connect(timeout_ms=buddy_config.CONNECT_TIMEOUT_MS,
                             hostname=buddy_config.HOSTNAME)
except wifi_link.WifiError as e:
    print("FAIL: Wi-Fi: {}".format(e.reason))
    raise SystemExit

print("MicroPython  :", sys.version)
try:
    own_name = network.hostname()
except AttributeError:
    own_name = "?"
print("Pico address :", wlan.ifconfig()[0], "(hostname {})".format(own_name))
print()
print("{:<24} {:<16} {}".format("name", "answer", "time"))
for name in NAMES:
    started = time.ticks_ms()
    try:
        answer = resolve(name, buddy_config.BUDDY_PORT)
    except Exception as e:                      # some firmware raises other errors
        answer = None
        print("  ({} raised {!r})".format(name, e))
    ms = time.ticks_diff(time.ticks_ms(), started)
    print("{:<24} {:<16} {} ms".format(name, answer or "not found", ms))

print()
print("Fallback: use the fixed address BUDDY_HOST = {!r}.".format(buddy_config.BUDDY_HOST))
print("Keep that address from changing with a DHCP reservation on the router,")
print("or give the server a fixed address outside the router's DHCP range.")
print()
print("PASS")
wifi_link.disconnect(wlan)
