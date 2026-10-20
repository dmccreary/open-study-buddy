# Chapter 18, Probe 06: Wi-Fi
# Lists the networks the radio can see (strongest first, with channel), then
# tries to join the one in secrets.py if there is one. The password is never
# printed. Needs only the Pico.
#
# PASS: your school network is in the list on a channel 1 to 14, and (with a
# secrets.py) the verdict says joined. The Pico 2 W radio is 2.4 GHz only
# (Chapter 4): a 5 GHz-only network will never appear.

NAME = "06-wifi-probe.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import network

import checks
import config

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
found = sorted(wlan.scan(), key=lambda n: -n[3])
print("{:<24} {:>4} {:>6}".format("network", "chan", "dBm"))
for ssid, bssid, channel, rssi, security, hidden in found:
    print("{:<24} {:>4} {:>6}".format(ssid.decode() or "(hidden)", channel, rssi))
verdict, detail = checks.check_wifi(config)
print()
print("RESULT:", verdict, "-", detail)
