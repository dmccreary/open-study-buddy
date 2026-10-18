# Chapter 4, Test 05: What Wi-Fi networks can the Pico see?
# Scans for networks and prints each one's name, channel, signal strength, and
# whether it is a 2.4 GHz network. The Pico 2 W's radio only supports 2.4 GHz
# (channels 1 to 14), so a school network must offer one. Needs only the Pico.
# It does not connect to anything and does not need secrets.py.
#
# PASS: at least one network is listed. Look for your school's name and check
# that its channel is 14 or lower. A network that never appears may be 5 GHz
# only, or too far away.

NAME = "05-wifi-scan.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import network

SECURITY = {0: "open", 1: "WEP", 2: "WPA", 3: "WPA2", 4: "WPA/WPA2", 5: "WPA3?"}

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
time.sleep_ms(500)

print("Scanning ...")
found = wlan.scan()          # (ssid, bssid, channel, RSSI, security, hidden)
found.sort(key=lambda n: n[3], reverse=True)

print()
print("{:<28} {:>3} {:>5}  {:<9} {}".format("name", "ch", "dBm", "security", "band"))
for ssid, bssid, channel, rssi, security, hidden in found:
    name = ssid.decode() if ssid else "(hidden)"
    band = "2.4 GHz" if 1 <= channel <= 14 else "other"
    print("{:<28} {:>3} {:>5}  {:<9} {}".format(
        name[:28], channel, rssi, SECURITY.get(security, str(security)), band))

print()
print("{} network(s) found.".format(len(found)))
wlan.active(False)
