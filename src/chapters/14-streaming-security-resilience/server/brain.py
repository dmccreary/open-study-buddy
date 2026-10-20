"""The buddy's brain: Chapter 1's rule-based decide(), shared by the HTTP and
WebSocket servers. Swap this module and nothing else changes (the swappable
brain). Chapter 16 replaces load_events() with a real school calendar."""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_SHOW = 30        # characters that fit the message region of the round display


def load_events(path=None):
    with open(path or os.path.join(HERE, "events.json"), encoding="utf-8") as f:
        return json.load(f)


def _first(events, prefix):
    for event in events:
        if event["title"].startswith(prefix):
            return event["title"][len(prefix):].strip(), event["day"]
    return None


def decide(text, events):
    """Return (speak, show)."""
    words = text.lower().strip()
    if not words:
        return "Sorry, I did not catch that.", "Did not catch that"
    if "test" in words:
        found = _first(events, "TEST:")
        if found:
            return ("Your next test is {} on {}.".format(*found),
                    "{} test: {}".format(*found))
        return "I do not see a test coming up.", "No tests coming up"
    if "due" in words:
        found = _first(events, "DUE:")
        if found:
            return ("{} is due on {}.".format(*found), "{} due: {}".format(*found))
        return "Nothing is due soon.", "Nothing due soon"
    return ("Sorry, I only know about tests and due dates.", "I only know tests, due")


def make_reply(text, events):
    speak, show = decide(text, events)
    return {"speak": speak, "show": show[:MAX_SHOW], "next_mode": "clock"}
