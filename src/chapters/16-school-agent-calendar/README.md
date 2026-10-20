# Chapter 16 code: Configuring the School Agent and Calendar

Chapter: `docs/chapters/16-school-agent-calendar/index.md`

Most of this chapter runs on a **computer** (the school server), because the
Pico never reads a calendar. Everything in `server/` is standard-library
Python 3.11 or newer (`tomllib` and `zoneinfo`), except two optional tools that
need `paho-mqtt` (sending) or `pillow` (the mascot tool). Nothing in `server/`
is uploaded to the Pico.

```bash
cd src/chapters/16-school-agent-calendar/server
python3 check_config.py                                   # validate agent.toml and the calendar
python3 test_pipeline.py                                  # 78 checks, no network, no hardware
python3 ask.py "when is my next test" --now 2026-10-19T09:00
python3 ask.py --briefing --now 2026-10-19T07:30
python3 push_daily.py --now 2026-10-19T07:30              # prints what it WOULD send
```

The worked example is Cedar Ridge High School. `agent.toml` points at the
author's real files in `docs/schools/cedar-ridge-high-school/` (`events.json`
and `calendar.ics`), reached by relative paths, so run the tools from a
checkout of the repository. To adapt this to your school, copy `server/`,
change `agent.toml`, and run `check_config.py` until it prints
`0 error(s)`.

## Server files (`server/`, run on a computer)

| File | What it does |
|------|--------------|
| `agent.toml` | The one configuration file: school, calendar source, courses, features, reminders, voice, mascot, wake phrase |
| `check_config.py`, `agent_config.py` | Load and validate `agent.toml` and the calendar it names, in plain English |
| `ics_parser.py` | The iCalendar reader: unfolding, VEVENT, all-day and timed events, UTC and `TZID` times; warns about what it skips |
| `events.py` | The `Event` shape, TEST:/DUE: categories, course matching, local time to UTC |
| `calendar_source.py`, `load_calendar.py` | Read `events.json`, an `.ics` file, or an ICS URL (with ETag caching and a polling interval) |
| `query.py` | Upcoming events, next test, events on a day, school days |
| `compose.py` | Answers, the daily briefing, reminder alerts (the wording rules live here and in `agent.toml`) |
| `ask.py` | Ask one question from the command line |
| `push_daily.py` | Compose today's briefing and reminders and publish them (`--send`, needs paho-mqtt and Chapter 15's broker) |
| `calendar_brain.py` | Drop-in replacement for Chapter 14's `server/brain.py`: `load_events()` and `make_reply()` backed by the calendar |
| `buddy_server_min.py` | A tiny server with `POST /v1/ask` and `GET /v1/health` (Chapter 13/14 paths, `X-Buddy-Token` header, `BUDDY_TOKENS`) |
| `make_edition.py` | Writes `../edition.py`, the few constants the Pico needs |
| `mascot_check.py` | Reports how much of a mascot picture is hidden by the bezel and byte sizes; `--write` makes `../griffin.rgb565` |
| `test_pipeline.py` | Checks everything above (78 checks) |
| `alerts.py`, `topics.py` | Copies of Chapter 15's alert format and topic names |

## Pico files (uploaded)

```bash
cd src/chapters
./upload-chapter.sh 16 02-edition-splash.py
```

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-show-school-mascot.py` | Display | Gale centered inside the round screen, ring complete, under 100 ms |
| `02-edition-splash.py` | Display | Printout says mascot, name and slogan are inside the safe circle; nothing clipped on screen |
| `03-briefing-display.py` | Display (Wi-Fi + broker + `push_daily.py --send` for the real thing) | Title, then the briefing two lines at a time, then the screen goes quiet; a repeated briefing id is ignored |

| Helper | What it holds |
|--------|---------------|
| `edition.py` | **Generated** by `server/make_edition.py` from `agent.toml`: school name, slogan, id, room, device id, colors, mascot file and size, wake phrase |
| `griffin.rgb565` | Gale the Griffin, 240 x 240 raw RGB565 (115,200 bytes), made by `server/mascot_check.py --write` |
| `mqtt_common.py`, `topics.py`, `alerts.py`, `alert_view.py`, `backoff.py`, `wifi_link.py` | Copies of Chapter 15's helpers (`backoff.py` is Chapter 14's, `wifi_link.py` is Chapter 13's); `03` needs them. `mqtt_common.py` reads `edition.py` first, then `secrets.py` |

Run `make_edition.py --room 118 --device desk-12` to make a second device's
`edition.py`. The Wi-Fi and broker settings (`mqtt_host`, `mqtt_user`,
`mqtt_pass`) stay in the kit's `secrets.py`, as in Chapter 15.

## The most important checks for the book

- `server/test_pipeline.py` proves the two calendar sources agree (the same 92
  events from `events.json` and from `calendar.ics`) and that every reminder
  for the school year is a valid alert. Run it again after you edit the
  calendar or the wording.
- `03-briefing-display.py` and `02-edition-splash.py` on a board: record
  whether the text really fits the glass (the bezel clips about 12 pixels, but
  panels differ) and how long `02` takes to draw (`wire time` for the mascot
  alone is 38.4 ms at 24 MHz).

## What has been checked, and what has not

- **Checked, on a computer, for real:** the whole server pipeline against the
  real Cedar Ridge `events.json` and `calendar.ics`; the parser against hand-made
  feeds (folding, escapes, quoted parameters, all-day and timed events, UTC,
  floating and foreign time zones, recurrence, cancelled events, unknown
  zones); daylight-saving cases; feed polling against a local web server
  (200, 304 by ETag, inside-interval, feed down); `buddy_server_min.py`
  against real HTTP requests (token list, bad body); and Chapter 14's own
  `buddy_server.py`, copied to a scratch folder with only `brain.py` replaced by
  `calendar_brain.py`, answering `/v1/ask` and serving `/v1/events` over real
  HTTP (the original files were not edited).
- **Checked on a computer against a fake Pico layer only:** `01` to `03`
  (real display driver with a recording SPI, a test MQTT broker for `03`).
  That catches typos and logic errors, not timing or fit on the real glass.
- **Not checked:** anything on the Pico itself; a live Google Calendar or any
  OAuth flow (Chapter 16 explains them and this folder has no code for them);
  feeds from Outlook, Apple Calendar or Google beyond the two hand-made
  samples (their time-zone names and recurrence rules are the usual trouble);
  real text-to-speech of the briefing; changing the wake phrase (Chapter 12's
  enrollment).
