# Chapter 15 code: MQTT and Push Alerts

Chapter: `docs/chapters/15-mqtt-push-alerts/index.md`

```bash
cd src/chapters
./upload-chapter.sh 15 03-link-listener.py
```

## One-time setup

1. **A broker.** Follow the chapter's "Mosquitto on a School Raspberry Pi" section,
   using `server/mosquitto.conf` and `server/study-buddy.acl` as the starting
   point. Create one account for the server, one for a dashboard, and one per
   device (user name = device id, for example `desk-07`).
2. **Add these lines to the kit's `src/kits/study-buddy-base/secrets.py`**
   (never committed). `upload-chapter.sh` copies that file to the Pico:

   ```python
   mqtt_host = "192.168.1.50"      # the broker's IP address, not a name
   mqtt_user = "desk-07"
   mqtt_pass = "a-long-unique-password"
   # optional; these are the defaults:
   # school_id = "crhs"
   # room = "214"
   # device_id = "desk-07"
   ```

3. **Install the MQTT library on the Pico** (once; the Pico must be on Wi-Fi, and
   the command needs a MicroPython release with `mip`, 1.20 or newer):

   ```bash
   mpremote mip install umqtt.simple
   ```

4. **On your computer or the Pi**, for the tools in `server/`:

   ```bash
   pip install paho-mqtt
   export MQTT_HOST=192.168.1.50 MQTT_USER=buddy-server MQTT_PASSWORD=...
   ```

## Files

The numbered files run on the Pico (01 also runs on a computer). `topics.py`,
`alerts.py`, `backoff.py`, `wifi_link.py`, `mqtt_common.py` and `alert_view.py` are helper modules that the
numbered files import; they are uploaded with them. Everything in `server/`
runs on a computer and is **not** uploaded.

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-topic-matcher.py` | none (also runs on a computer) | All 8 rows match the hand-written table, PASS |
| `02-mqtt-hello.py` | Pico + Wi-Fi + broker | "connected", "subscribed", "published online"; an alert you send prints; PASS |
| `03-link-listener.py` | Pico + Wi-Fi + broker | Alerts print once; stopping the broker for 20 s gives LINK DOWN, longer waits between tries, LINK UP |
| `04-check-msg-cost.py` | Pico + Wi-Fi + broker | Idle and delivery costs in microseconds; PASS (write the numbers down) |
| `05-alert-display.py` | Display | Six alerts readable inside the round screen; long title ends in "..." |
| `06-alert-audio-loop.py` | Microphone + speaker + display + Wi-Fi + broker | About 25 frames per second, no overruns, one beep per new alert, none for a repeat |
| `07-status-heartbeat.py` | Pico + Wi-Fi + broker | `watch.py` shows `online` (R) once, telemetry every 30 s, `offline` after unplugging |
| `08-echo-rtt.py` | Pico + Wi-Fi + broker + `server/echo_responder.py` | Fastest / median / slowest round trip in ms; PASS |

| Helper | What it holds |
|--------|---------------|
| `topics.py` | topic names, `slug()`, `valid_filter()`, the `+`/`#` matcher `topic_matches()` |
| `alerts.py` | the alert format: limits, `make_alert()`, `decode_alert()`, `Seen` (de-duplication) |
| `mqtt_common.py` | settings from `secrets.py`, `connect_wifi()` (calls `wifi_link`), `retry_wait_ms()`, the `Link` class |
| `backoff.py`, `wifi_link.py` | Copies of Chapter 14's backoff helper (`delay_ms()`: doubling ceiling, full jitter) and Chapter 13's `connect()` for Wi-Fi |
| `alert_view.py` | `show_alert()` and `clear_alert()` for the agent-message region |

| `server/` file | What it does |
|----------------|--------------|
| `mosquitto.conf`, `study-buddy.acl` | Example broker settings and access rules for a school Pi |
| `publish_alert.py` | Publish (or `--clear`) an alert; `--dry-run` prints without connecting |
| `watch.py` | Subscribe and print: the tiny subscriber for testing |
| `echo_responder.py` | Answers `08-echo-rtt.py` |
| `ha_discovery.py`, `home-assistant.yaml` | Home Assistant examples (not run against Home Assistant) |
| `test_topics.py` | Tests for `topics.py` and `alerts.py`; compares with paho's matcher if paho is installed |

## The most important tests for the book

`04` and `06` check the claim the chapter depends on: that polling for MQTT
messages fits inside the 40 ms audio frame. Please record:

- From `04`: the idle `check_msg()` average and slowest, and the slowest pass
  that delivered a message (microseconds).
- From `06`: "worst work" in the second an alert arrived, whether any overrun
  was reported, and (Try This 1) how long the loop froze during a failed
  connect attempt with the broker stopped.
- From `08`: fastest / median / slowest round trip, with your Wi-Fi conditions.
- From `07`: how long after unplugging the Pico the broker published `offline`
  (the chapter expects about 45 s = 1.5 x the 30 s keepalive).

## What has been checked, and what has not

- `topics.py` matches the MQTT specification's example table and agrees with
  paho-mqtt's matcher on all 4,095 filter/topic pairs of a small alphabet
  (`server/test_topics.py`).
- `01` and `server/test_topics.py` run on a computer. `server/publish_alert.py`,
  `watch.py`, `echo_responder.py` and `ha_discovery.py` ran against a small
  test broker written for the book's authors (paho-mqtt 2.1.0 on the client
  side). **They have not run against Mosquitto**: no Mosquitto was available.
- `02` to `08` and `mqtt_common.py` ran on a computer against a fake Pico layer
  (pins, I2S, SPI, Wi-Fi, a clock) with the **real** `umqtt.simple` from
  micropython-lib (version 1.8.1 in its manifest) and the same test broker.
  That checked the MQTT bytes sent, the last will, retained and duplicate
  handling, ping and silence detection, and reconnecting. It checks typos and
  logic, not timing.
- `mosquitto.conf`, `study-buddy.acl` and `home-assistant.yaml` were written
  from the Mosquitto and Home Assistant documentation and **have not been run**
  on a Pi or a Home Assistant.
- Nothing here has run on the Pico yet. Every timing, free-memory and
  Wi-Fi-reliability question in the chapter is open until `04`, `06`, `07` and
  `08` have run on the board.
