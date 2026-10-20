# Chapter 13, Test 01: Join the school Wi-Fi in station mode
# Joins the network named in secrets.py (wifi_ssid, wifi_pass), prints each
# state change with the time it took, then prints the four numbers the Pico
# was given: IP address, netmask, gateway, and DNS server. Needs only the Pico
# and a 2.4 GHz network. It does not talk to the buddy server.
#
# PASS: the last state is "connected", an IP address is printed, and the last
# line says PASS. If it fails, the message says why (wrong password, network
# not found, or a timeout) -- fix that and run it again.
# Never print the password. This file only prints the network NAME.

NAME = "01-wifi-connect.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import network

import buddy_config
import wifi_link

try:
    import secrets
    NETWORK_NAME = secrets.wifi_ssid
except ImportError:
    NETWORK_NAME = None
    print("No secrets.py on the Pico. Create one with wifi_ssid and wifi_pass.")

start = time.ticks_ms()


def show(text):
    print("  {:>6} ms  {}".format(time.ticks_diff(time.ticks_ms(), start), text))


print()
print("Joining '{}' ...".format(NETWORK_NAME))
try:
    wlan = wifi_link.connect(timeout_ms=buddy_config.CONNECT_TIMEOUT_MS,
                             hostname=buddy_config.HOSTNAME, show=show)
except wifi_link.WifiError as e:
    print()
    print("FAIL: {} (status {})".format(e.reason, e.code))
    raise SystemExit

ip, netmask, gateway, dns = wlan.ifconfig()
print()
print("IP address : {}".format(ip))
print("netmask    : {}".format(netmask))
print("gateway    : {}".format(gateway))
print("DNS server : {}".format(dns))
print("signal     : {} dBm".format(wlan.status("rssi")))
print("isconnected: {}".format(wlan.isconnected()))
try:
    print("hostname   : {}".format(network.hostname()))
except AttributeError:
    pass

print()
print("PASS" if wlan.isconnected() and ip != "0.0.0.0" else "CHECK: no IP address")
wifi_link.disconnect(wlan)

# Try This
#   1. Run it twice in a row. The second time is usually faster. Why?
#   2. In a copy of this file, call wifi_link.connect("not-a-network", "x").
#      Which message do you get, and how long did it take?
#   3. Move the Pico farther from the access point and watch the dBm number.
