#!/usr/bin/env python3
"""Tests for topics.py and alerts.py (Chapter 15). Runs on your computer:
    python3 test_topics.py
If paho-mqtt is installed, topic_matches() is also compared with paho's own
matcher on every combination of a small topic alphabet.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import alerts   # noqa: E402
import topics   # noqa: E402

failures = []


def check(name, got, want):
    if got != want:
        failures.append("%s: got %r, wanted %r" % (name, got, want))


# --- the MQTT specification's own examples -------------------------------
SPEC = [
    ("sport/tennis/player1/#", "sport/tennis/player1", True),
    ("sport/tennis/player1/#", "sport/tennis/player1/ranking", True),
    ("sport/tennis/player1/#", "sport/tennis/player1/score/wimbledon", True),
    ("sport/#", "sport", True),
    ("sport/tennis/+", "sport/tennis/player1", True),
    ("sport/tennis/+", "sport/tennis/player1/ranking", False),
    ("sport/+", "sport", False),
    ("sport/+", "sport/", True),
    ("+/+", "/finance", True),
    ("/+", "/finance", True),
    ("+", "/finance", False),
    ("#", "$SYS/monitor/Clients", False),
    ("+/monitor/Clients", "$SYS/monitor/Clients", False),
    ("$SYS/#", "$SYS/monitor/Clients", True),
    ("$SYS/monitor/+", "$SYS/monitor/Clients", True),
]
for f, t, want in SPEC:
    check("spec %s vs %s" % (f, t), topics.topic_matches(f, t), want)

# --- invalid filters and names -------------------------------------------
for bad in ("a/#/b", "a#", "a+/b", "", "#/a", "a/b+"):
    check("bad filter %r" % bad, topics.valid_filter(bad), False)
for good in ("#", "+", "a/#", "+/+", "a/+/c"):
    check("good filter %r" % good, topics.valid_filter(good), True)
for bad in ("", "a/+", "a/#", "a\x00b"):
    check("bad name %r" % bad, topics.valid_topic_name(bad), False)

# --- slug ------------------------------------------------------------------
for text, want in (("Lab 130", "lab-130"), ("214", "214"), ("  Room--A/B  ", "room-a-b"),
                   ("Ünï", "n"), ("", "")):
    check("slug %r" % text, topics.slug(text), want)

# --- optional: compare with paho's matcher on a small alphabet -------------
try:
    from paho.mqtt.client import topic_matches_sub
except ImportError:
    topic_matches_sub = None
if topic_matches_sub:
    alphabet = ["a", "b", "+", "#", "$x"]
    names = [l for l in alphabet if l not in ("+", "#")]
    tested = 0
    for nf in range(1, 4):
        for fparts in itertools.product(alphabet, repeat=nf):
            filt = "/".join(fparts)
            if not topics.valid_filter(filt):
                continue
            for nt in range(1, 4):
                for tparts in itertools.product(names, repeat=nt):
                    topic = "/".join(tparts)
                    mine = topics.topic_matches(filt, topic)
                    theirs = topic_matches_sub(filt, topic)
                    tested += 1
                    if mine != theirs:
                        failures.append("paho disagrees: %s vs %s (mine %s, paho %s)"
                                        % (filt, topic, mine, theirs))
    print("compared with paho's matcher on %d filter/topic pairs" % tested)
else:
    print("paho-mqtt not installed: skipped the comparison with paho's matcher")

# --- alerts ----------------------------------------------------------------
ok = alerts.make_alert("a1", "test", "Algebra II test", "Tomorrow 8:00 AM", "Algebra II test tomorrow at 8 AM.")
text = alerts.encode_alert(ok)
check("round trip", alerts.decode_alert(text.encode()), ok)
check("compact JSON", text.startswith('{"id":"a1","type":"test",'), True)
check("empty payload", alerts.decode_alert(b""), None)
check("not json", alerts.decode_alert(b"online"), None)
check("not an object", alerts.decode_alert(b"[1,2]"), None)
check("missing id", alerts.decode_alert(b'{"type":"test","title":"t","when":"w","text":"x"}'), None)
check("bad type", alerts.decode_alert(b'{"id":"1","type":"party","title":"t","when":"w","text":"x"}'), None)
check("bytes of non-text", alerts.decode_alert(b"\xff\xfe\x00"), None)
check("too big", alerts.decode_alert(b"x" * 600), None)
try:
    alerts.make_alert("a2", "test", "T" * 31, "w", "x")
    failures.append("31-character title was accepted")
except ValueError as error:
    check("title limit message", "limit 30" in str(error), True)
check("briefing may carry 300 characters of text",
      alerts.problems({"id": "b", "type": "briefing", "title": "t", "when": "w", "text": "x" * 300}), [])
check("other types may not", alerts.problems({"id": "b", "type": "test", "title": "t", "when": "w", "text": "x" * 121}) != [], True)
worst = {"id": "i" * 40, "type": "briefing", "title": "t" * 30, "when": "w" * 30, "text": "x" * 300, "at": "2026-10-20T13:00Z"}
check("worst-case alert fits the 512-byte limit", len(alerts.encode_alert(worst).encode()) <= alerts.MAX_PAYLOAD, True)
seen = alerts.Seen(size=3)
check("first id", seen.is_new("a"), True)
check("repeat id", seen.is_new("a"), False)
for i in ("b", "c", "d"):
    seen.is_new(i)
check("forgotten after 3 newer ids", seen.is_new("a"), True)

if failures:
    for line in failures:
        print("FAIL:", line)
    sys.exit(1)
print("PASS: topics and alerts tests")
