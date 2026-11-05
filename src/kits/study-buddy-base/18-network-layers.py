# Lab 18: From Radio Waves to the Weather -- Network Layers
# Goes from nothing to today's temperature in five steps, and ticks each
# one off on the screen as it works. When something fails, the step that
# failed tells you where to look.
#
# THE IDEA: LAYERS. Getting one number off the internet takes a stack of
# jobs, each one built on the one below it:
#
#   1. RADIO    join the WiFi network (name and password from secrets.py).
#               The signal strength, RSSI, is in dBm: -50 is strong, -80 weak.
#   2. ADDRESS  the router hands the Pico an IP address, like a street
#               address, so replies can find their way back.
#   3. TIME     ask a time server (NTP) what time it is. It answers in UTC;
#               the time zone in config.py turns that into local time.
#   4. HTTP     send a request for a web address, like a browser does, and
#               get back a status code (200 means OK) and some bytes.
#   5. JSON     those bytes are text in JSON, a format of names and values;
#               .json() turns it into a Python dictionary.
#
# The weather comes from Open-Meteo, a free service with no account and no
# key. The request names exactly the numbers it wants, so the answer is
# only a few hundred bytes.
#
# Parts: the Pico 2 W's WiFi and the display. Needs secrets.py (copy
# secrets-template.py and fill it in). The Pico only joins 2.4 GHz networks.
#
# PASS: five green OKs and the temperature where you are (set LATITUDE and
# LONGITUDE in config.py).

NAME = "18-network-layers.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
ROW_Y = 76              # the rows start low enough to fit the round glass
ROW_PITCH = 26
LABEL_X = 70
RESULT_X = 150

URL = ("http://api.open-meteo.com/v1/forecast?latitude={}&longitude={}"
       "&current=temperature_2m,wind_speed_10m"
       "&temperature_unit={}&wind_speed_unit={}")

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
config.centered_text(display, SMALL, "NETWORK LAYERS", 44, DIM)

STEPS = ("radio", "address", "time", "HTTP", "JSON")
for i, label in enumerate(STEPS):
    y = ROW_Y + i * ROW_PITCH
    display.text(SMALL, "%d %s" % (i + 1, label), LABEL_X, y, DIM,
                 config.BLACK)


def result(step, ok, text):
    """Fill in one row: OK or FAIL, then what it found."""
    y = ROW_Y + step * ROW_PITCH
    display.text(SMALL, ("OK  " if ok else "FAIL") + " " + text[:15],
                 RESULT_X, y, config.GREEN if ok else config.RED,
                 config.BLACK)
    print("{} {:8} {}".format("OK  " if ok else "FAIL", STEPS[step], text))
    return ok


def finish(lines, color):
    for i, line in enumerate(lines):
        config.centered_text(display, BIG if i == 0 else SMALL, line,
                             216 + i * 40, color)


def run():
    # ---- 1. radio -------------------------------------------------------
    try:
        import secrets
    except ImportError:
        result(0, False, "no secrets.py")
        return finish(["No WiFi", "copy secrets-template.py"], config.RED)
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(secrets.wifi_ssid, secrets.wifi_pass)
        started = time.ticks_ms()
        while not wlan.isconnected() and wlan.status() >= 0:
            if time.ticks_diff(time.ticks_ms(), started) > 15000:
                break
            time.sleep_ms(250)
    if not wlan.isconnected():
        result(0, False, "status %d" % wlan.status())
        wlan.active(False)
        return finish(["No WiFi", "check the name, password,",
                       "and 2.4 GHz"], config.RED)
    try:
        rssi = wlan.status("rssi")
        result(0, True, "%d dBm" % rssi)
    except (ValueError, OSError):
        result(0, True, secrets.wifi_ssid)

    try:
        # ---- 2. address -------------------------------------------------
        ip = wlan.ifconfig()[0]
        result(1, True, ip)

        # ---- 3. time ----------------------------------------------------
        import ntptime
        import wifi_time
        try:
            ntptime.settime()                     # the RTC is now UTC
            utc = time.time()
            local = time.localtime(utc + wifi_time.utc_offset_hours(utc)
                                   * 3600)
            result(2, True, "%02d:%02d local" % (local[3], local[4]))
        except OSError as error:
            result(2, False, str(error))          # carry on without it

        # ---- 4. HTTP ----------------------------------------------------
        import requests
        fahrenheit = config.TEMPERATURE_UNIT == "fahrenheit"
        url = URL.format(config.LATITUDE, config.LONGITUDE,
                         config.TEMPERATURE_UNIT,
                         "mph" if fahrenheit else "kmh")
        print("GET", url)
        try:
            response = requests.get(url, timeout=10)
        except OSError as error:
            result(3, False, str(error))
            return finish(["No answer", "is the internet up?"], config.RED)
        try:
            text = response.text
            status = response.status_code
        finally:
            response.close()
        if not result(3, status == 200, "%d, %d bytes" % (status, len(text))):
            return finish(["HTTP %d" % status], config.RED)

        # ---- 5. JSON ----------------------------------------------------
        import json
        try:
            current = json.loads(text)["current"]
            temperature = current["temperature_2m"]
            wind = current["wind_speed_10m"]
        except (ValueError, KeyError) as error:
            result(4, False, "bad reply")
            print(text)
            return finish(["Bad reply"], config.RED)
        result(4, True, "%d keys" % len(current))
        unit = "F" if fahrenheit else "C"
        finish(["%d %s" % (round(temperature), unit),
                "wind %d %s" % (round(wind), "mph" if fahrenheit else "km/h")],
               config.CYAN)
    finally:
        wlan.disconnect()                         # the radio uses the most
        wlan.active(False)                        # power on the board


run()

# Try This
#   1. Paste the URL the shell printed into a web browser. Find
#      temperature_2m in what comes back. What else is in there?
#   2. Add "relative_humidity_2m" to the &current= list (separated by a
#      comma) and show it on the screen.
#   3. Change LATITUDE and LONGITUDE in config.py to a city on the other
#      side of the world. Is it warmer or colder there right now?
