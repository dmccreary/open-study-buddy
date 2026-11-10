---
title: "Lab 18: From Radio Waves to the Weather"
description: "Go from nothing to today's temperature in five steps (radio, address, time, HTTP, JSON), with each layer ticked off on the display so you can see exactly where a failure happens."
---

# Lab 18: From Radio Waves to the Weather

!!! mascot-welcome "Reach Out to the World"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Your Study Buddy has a secret superpower: a WiFi radio. In this lab it will join your network, find out what time it is, and ask the internet for the temperature outside, ticking off each step on the screen as it goes. Let's listen closely!

| | |
|---|---|
| **Program** | `18-network-layers.py` |
| **Parts needed** | The Pico 2 W's WiFi, the display, and a `secrets.py` file |
| **Time** | 30 minutes |
| **Makes sound?** | No |
| **How to stop** | The program ends by itself |

## Before You Start

You need a file named `secrets.py` on the Pico with your WiFi name and password. Copy
`secrets-template.py` to `secrets.py` and fill in:

```python
wifi_ssid = "YourNetworkName"
wifi_pass = "YourPassword"
```

The Pico only joins **2.4 GHz** networks. A network that is 5 GHz only will not work. Also set
`LATITUDE` and `LONGITUDE` in `config.py` to where you live. Search for "your town latitude
longitude". North and east are positive, so the United States has a **negative** longitude.

!!! mascot-warning "Keep secrets.py Secret"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    `secrets.py` holds your real WiFi password, so it is listed in `.gitignore` to keep it out of GitHub. Never paste its contents into a chat, a screenshot, or a lab report, and if you ever do, change your WiFi password.

## What You Will Learn

* How getting one number from the internet takes a **stack of layers**
* What an **IP address**, **NTP**, **HTTP**, and **JSON** each do
* How to find where a network problem is by **which step failed**
* How to read a **status code**

## The Big Idea: Layers

Getting the temperature from a server takes a stack of jobs, each built on the one below it.
You used pieces of this in the
[Wireless Connectivity and IoT](https://dmccreary.github.io/learning-micropython/chapters/19-wireless-iot/)
chapter. Here, you will see all five at once:

| # | Layer | What it does | What it gives you |
|---|-------|--------------|-------------------|
| 1 | **Radio** | Joins the WiFi network | Signal strength (RSSI), in dBm |
| 2 | **Address** | The router hands the Pico an **IP address**, like a street address, so replies can find their way back | An address such as `192.168.1.42` |
| 3 | **Time** | Asks a time server (**NTP**) what time it is | The time in UTC, then local time |
| 4 | **HTTP** | Sends a request for a web address, as a browser does | A **status code** and some bytes |
| 5 | **JSON** | Turns the bytes into names and values | A Python dictionary |

Each layer **depends on the one below**. If layer 1 fails, layers 2 to 5 cannot work. So when
something goes wrong, the step that failed tells you where to look.

!!! mascot-thinking "A Stack Fails from the Bottom"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    When a web page will not load, the cause could be your WiFi, your address, your time, the server, or the reply, and people waste hours guessing. Checking the layers from the bottom up turns a vague "it's broken" into "layer 3 failed", which is something you can actually fix.

## Walking Through the Code

### Drawing the checklist

```python
STEPS = ("radio", "address", "time", "HTTP", "JSON")
for i, label in enumerate(STEPS):
    y = ROW_Y + i * ROW_PITCH
    display.text(SMALL, "%d %s" % (i + 1, label), LABEL_X, y, DIM, config.BLACK)
```

The five labels are drawn in gray. A function called `result()` later fills in a green **OK** or
a red **FAIL** next to each one, with a short message, and also prints it to the shell.

### 1. Radio

```python
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.wifi_ssid, secrets.wifi_pass)
```

`network.STA_IF` means "station interface": the Pico acting as a *client* of a WiFi network (not
as an access point). The program then waits up to 15 seconds for the connection:

```python
while not wlan.isconnected() and wlan.status() >= 0:
    if time.ticks_diff(time.ticks_ms(), started) > 15000:
        break
    time.sleep_ms(250)
```

The loop also gives up if `wlan.status()` goes **negative**, which means the connection failed. If
it does fail, the screen shows the status number:

| Status | Meaning |
|--------|---------|
| `-1` | The connection failed |
| `-2` | No network with that name was found |
| `-3` | The password is wrong |

On success it reads the signal strength with `wlan.status("rssi")`. It is in **dBm**:
about **-50 is strong**, and **-80 is weak**. The numbers are negative and count toward zero as the signal improves.

### 2. Address

```python
ip = wlan.ifconfig()[0]
```

The first item of `ifconfig()` is the Pico's IP address, handed out by your router.

### 3. Time

```python
ntptime.settime()                     # the RTC is now UTC
utc = time.time()
local = time.localtime(utc + wifi_time.utc_offset_hours(utc) * 3600)
```

`ntptime.settime()` asks a time server and sets the Pico's clock. NTP servers only ever answer in
**UTC**. The `TIMEZONE_HOURS` and `USE_US_DST` settings in `config.py`, with `wifi_time.py`, turn
UTC into your local time, including daylight saving. This step is wrapped in `try ... except OSError`, so if the time server does not
answer, the program records a FAIL and **carries on**, because the weather does not need the time.

### 4. HTTP

```python
url = URL.format(config.LATITUDE, config.LONGITUDE, config.TEMPERATURE_UNIT, ...)
response = requests.get(url, timeout=10)
text = response.text
status = response.status_code
response.close()
```

The weather comes from [Open-Meteo](https://open-meteo.com/), a free service with no account and
no key. The URL names exactly the numbers it wants, so the answer is only a few hundred bytes:

```
http://api.open-meteo.com/v1/forecast?latitude=44.98&longitude=-93.27
    &current=temperature_2m,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph
```

The **status code** says how it went: **200** means OK, **404** means not found, and **500**
means the server had a problem. The program shows `200, N bytes` in green when it works.

!!! mascot-tip "Always Close the Response"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    A response holds a network connection open until you call `response.close()`, and the Pico only has a few of them. The program wraps the reading in `try ... finally` so the close always happens, even when something goes wrong.

### 5. JSON

```python
current = json.loads(text)["current"]
temperature = current["temperature_2m"]
wind = current["wind_speed_10m"]
```

JSON is text made of names and values, like a Python dictionary. The reply looks something like this
(an example, shortened):

```json
{"latitude": 44.98, "longitude": -93.27, "current": {"time": "2026-11-04T10:00",
 "interval": 900, "temperature_2m": 41.3, "wind_speed_10m": 8.2}}
```

`json.loads()` ("load string") turns it into a dictionary, and the square brackets pick out
`"current"`, and then `"temperature_2m"`. Square brackets with a name are how you look up
a value in a dictionary, as you learned in the course.

### Always turn the radio off

```python
finally:
    wlan.disconnect()
    wlan.active(False)
```

The radio is the biggest user of power on the board. The `finally` makes sure it is switched
off whatever happened, even after an error.

## Run It

Open `18-network-layers.py` and press Run. Watch the rows turn green one at a time.

## What PASS Looks Like

* Five rows, each with a green **OK**: the signal strength, your IP address, the local time, an
  HTTP `200`, and the number of JSON keys.
* Below the rows, the **temperature** in big cyan numbers, and the wind speed under it.
* The shell prints each step, and the full web address that it asked for.

## If Something Goes Wrong

| Failed step | What it means | What to try |
|-------------|---------------|-------------|
| `no secrets.py` | The file is missing | Copy `secrets-template.py` to `secrets.py` and fill it in |
| 1 radio, status `-3` | Wrong password | Check `wifi_pass` for typos (it is case-sensitive) |
| 1 radio, status `-2` | Network not found | Check the name; make sure it is 2.4 GHz |
| 3 time | Time server did not answer | Try again; the weather can still work |
| 4 HTTP, `No answer` | No internet, or a blocked network | Check the router; a school network may block it |
| 4 HTTP, other than 200 | The server complained | Check that `LATITUDE` and `LONGITUDE` are numbers in range |
| 5 JSON, `bad reply` | The reply was not what was expected | The program prints it in the shell; read it |

## Try This

1. **Open the URL.** Paste the URL the shell printed into a web browser. Find `temperature_2m`
   in what comes back. What else is in there?
2. **More weather.** Add `relative_humidity_2m` to the `&current=` list (separated by a comma)
   and show it on the screen.
3. **Far away.** Change `LATITUDE` and `LONGITUDE` in `config.py` to a city on the other side
   of the world. Is it warmer or colder there right now?
4. **Celsius.** Set `TEMPERATURE_UNIT = "celsius"` in `config.py` and run again. Check the answer
   with the formula C = (F - 32) x 5 / 9.

??? tip "Hint for number 2"
    Add `,relative_humidity_2m` to the end of the `&current=` part of `URL`. Then read it with
    `current["relative_humidity_2m"]` and add another line to the `finish([...])` call. The
    reply has one more key, so the JSON row says one more key too.

## Check Your Understanding

1. In what order do the five layers run, from bottom to top?
2. What does an HTTP status code of 200 mean?
3. Why does the program turn the WiFi radio off at the end?
4. Why does NTP answer in UTC, and what turns it into your local time?

??? question "Answers"
    1. Radio, address, time, HTTP, JSON.
    2. The request worked (OK).
    3. The radio uses the most power on the board, so turning it off saves battery.
    4. UTC is the same everywhere, so servers do not need to know your location. The
       `TIMEZONE_HOURS` and `USE_US_DST` settings in `config.py` do the conversion.

## Where Next

You have used every part of the kit and every big idea. [Lab 19](19-pattern-game.md) puts them all
into one program: a memory game.

*Review in the course:* [Wireless Connectivity and IoT](https://dmccreary.github.io/learning-micropython/chapters/19-wireless-iot/),
including the [get weather lab](https://dmccreary.github.io/learning-micropython/hands-on-labs/19-wireless-iot/08-get-weather/)
and the [WiFi clock lab](https://dmccreary.github.io/learning-micropython/hands-on-labs/19-wireless-iot/10-wifi-clock/).
Also see [Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../../chapters/13-wifi-http-agent-link/index.md) in this book.
