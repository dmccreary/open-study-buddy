# alerts.py -- the alert message format (Chapter 15)
#
# Plain Python with no hardware: it runs on the Pico (the device decodes and
# de-duplicates alerts) and on your computer (the server builds and checks
# them). One alert is one small JSON object:
#
#   {"id":"20261019-crhs-018-d1","type":"test","title":"Algebra II test",
#    "when":"Tomorrow 8:00 AM","text":"Algebra II test tomorrow at 8 AM.",
#    "at":"2026-10-20T13:00Z"}
#
#   id     string, unique per alert. A device ignores an id it has seen.
#   type   "test", "due", "event", "notice" or "briefing"
#   title  at most 30 characters: line 1 on the display
#   when   at most 30 characters, already formatted: line 2 on the display
#   text   at most 120 characters (300 for a "briefing"): what the speaker
#          says (Chapter 14's text-to-speech turns it into audio)
#   at     optional, UTC, "YYYY-MM-DDTHH:MMZ": for dashboards such as Home
#          Assistant. The Pico never parses it.

import json

TYPES = ("test", "due", "event", "notice", "briefing")
REQUIRED = ("id", "type", "title", "when", "text")
MAX_PAYLOAD = 512          # bytes; anything larger is dropped unread
MAX_ID = 40
MAX_TITLE = 30
MAX_WHEN = 30
MAX_TEXT = 120
MAX_TEXT_BRIEFING = 300    # the morning briefing is several sentences


def problems(alert):
    """List what is wrong with an alert dict. An empty list means it is fine."""
    found = []
    if not isinstance(alert, dict):
        return ["not a JSON object"]
    for key in REQUIRED:
        if key not in alert:
            found.append("missing " + key)
        elif not isinstance(alert[key], str):
            found.append(key + " is not text")
    if found:
        return found
    if alert["type"] not in TYPES:
        found.append("type must be one of " + ", ".join(TYPES))
    text_limit = MAX_TEXT_BRIEFING if alert["type"] == "briefing" else MAX_TEXT
    for key, limit in (("id", MAX_ID), ("title", MAX_TITLE),
                       ("when", MAX_WHEN), ("text", text_limit)):
        if len(alert[key]) > limit:
            found.append("%s is %d characters, limit %d" % (key, len(alert[key]), limit))
    if not alert["id"]:
        found.append("id is empty")
    return found


def make_alert(alert_id, kind, title, when, text, at=None):
    """Build an alert dict (server side). Raises ValueError if it is invalid."""
    alert = {"id": alert_id, "type": kind, "title": title, "when": when, "text": text}
    if at:
        alert["at"] = at
    found = problems(alert)
    if found:
        raise ValueError("; ".join(found))
    return alert


def encode_alert(alert):
    """Compact JSON text for publishing (no spaces after ':' or ',')."""
    text = json.dumps(alert, separators=(",", ":"))
    if len(text.encode()) > MAX_PAYLOAD:
        raise ValueError("alert is %d bytes, limit %d" % (len(text.encode()), MAX_PAYLOAD))
    return text


def decode_alert(payload):
    """Device side. `payload` is the bytes umqtt hands to the callback.
    Returns an alert dict, or None for an empty, oversized or invalid message
    (an empty retained message is how a server clears an old alert)."""
    if not payload or len(payload) > MAX_PAYLOAD:
        return None
    try:
        alert = json.loads(payload.decode())
    except (ValueError, UnicodeError):
        return None
    if problems(alert):
        return None
    return alert


class Seen:
    """Remember the last few alert ids so a repeat can be ignored.

    Repeats are normal: QoS 1 delivers at least once, a retained alert comes
    back after every reconnect, and a server may re-run a reminder job."""

    def __init__(self, size=8):
        self.ids = [None] * size
        self.next = 0

    def is_new(self, alert_id):
        """True the first time an id is seen (and remembers it)."""
        if alert_id in self.ids:
            return False
        self.ids[self.next] = alert_id
        self.next = (self.next + 1) % len(self.ids)
        return True
