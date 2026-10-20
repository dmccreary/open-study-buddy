# offline.py -- what the device can still do when the network is gone
#
# The Pico cannot turn speech into words by itself, so offline it cannot
# understand a spoken question. What it CAN do is answer a few fixed questions
# from a copy of the school events that it saved while the network was up.
# This is Chapter 1's rule-based decide(), small enough for the Pico.

import json

CACHE_FILE = "events_cache.json"
FALLBACK = [{"title": "TEST: (no data yet)", "day": "unknown"}]


def save_events(events):
    """Write the events to flash, but only if they changed (flash wears out)."""
    text = json.dumps(events)
    try:
        with open(CACHE_FILE) as f:
            if f.read() == text:
                return False
    except OSError:
        pass
    with open(CACHE_FILE, "w") as f:
        f.write(text)
    return True


def load_events():
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return FALLBACK


def _first(events, prefix):
    for event in events:
        if event["title"].startswith(prefix):
            return event["title"][len(prefix):].strip(), event["day"]
    return None


def decide(text, events):
    """Returns (speak, show)."""
    words = text.lower()
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
    return "I am offline and only know tests and due dates.", "Offline: tests, due"
