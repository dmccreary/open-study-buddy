"""calendar_brain.py: the school calendar as the buddy server's brain (Chapter 16).

A drop-in replacement for Chapter 14's server/brain.py. That server calls only
    brain.load_events()            once at start-up
    brain.make_reply(text, events) for every question
so copying this file and the other server/ modules next to Chapter 14's
buddy_server.py and saving this file under the name brain.py makes the same
server answer from the real calendar. Nothing else changes.

    cp calendar_brain.py <chapter 14 server folder>/brain.py   (plus the other .py files and agent.toml)
    export SCHOOL_AGENT_CONFIG=/path/to/agent.toml              (default: agent.toml beside this file)
    export SCHOOL_NOW=2026-10-19T09:00                          (demos only: pretend it is this school-local time)

load_events() returns a LIST of {"title", "day"} items, because Chapter 14's
/v1/events endpoint sends it to the Pico for its offline cache, and the Pico's
offline answers read exactly those two fields. The list also carries the
Calendar, which make_reply() uses.
"""
import os
from datetime import datetime

import agent_config
import compose
from load_calendar import load_calendar

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_SHOW = 30
OFFLINE_ITEMS = 12                      # how many upcoming tests and due dates the Pico may cache


class SchoolEvents(list):
    """What /v1/events sends, plus the objects make_reply needs."""
    cfg = None


def _now(cal):
    fixed = os.environ.get("SCHOOL_NOW")
    return datetime.fromisoformat(fixed).replace(tzinfo=cal.tz) if fixed else datetime.now(cal.tz)


def load_events(path=None):
    cfg = agent_config.load(path or os.environ.get("SCHOOL_AGENT_CONFIG") or os.path.join(HERE, "agent.toml"))
    cal, _ = load_calendar(cfg)
    now = _now(cal)
    items = SchoolEvents()
    items.cfg = cfg
    for event in compose.upcoming(cal, now, days=60, categories=("test", "due"), limit=OFFLINE_ITEMS):
        day = event.local_start(cal.tz)
        items.append({"title": event.title,
                      "day": "%s, %s %d" % (compose.WEEKDAYS[day.weekday()], compose.MONTHS[day.month - 1], day.day)})
    return items


def make_reply(text, events):
    """{"speak", "show", "next_mode"}: Chapter 1's reply. The calendar is read
    again on every question (a URL feed is still polled only every poll_minutes)."""
    cfg = events.cfg
    cal, _ = load_calendar(cfg)
    reply = compose.answer(text, cal, _now(cal), cfg)
    reply["show"] = reply["show"][:MAX_SHOW]
    return reply
