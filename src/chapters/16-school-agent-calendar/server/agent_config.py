"""Load and check agent.toml (Chapter 16). Standard library only (Python 3.11+)."""
import os
import re
import tomllib
from zoneinfo import ZoneInfo

import topics

DEFAULTS = {
    "features": {"questions": True, "briefing": True, "test_alerts": True,
                 "due_alerts": True, "no_school_notices": True},
    "briefing": {"time": "07:30", "max_items": 3, "upcoming_days": 7},
    "reminders": {"test_days_before": [1], "due_days_before": [1], "no_school_days_before": [1]},
    "voice": {"tone": "friendly", "greeting": "Good morning from {school}.", "mascot_flavor": False,
              "reminder_test": "Heads up. {sentence}", "reminder_due": "Reminder. {sentence}",
              "reminder_notice": "{sentence}", "system_prompt": "", "flavor": {}, "say": {}},
    "mascot": {"name": "Buddy", "file": "", "size": 240, "source_png": ""},
    "wake": {"phrase": "Hey Pico"},
    "mqtt": {"alert_topic_scope": "room"},
    "calendar": {"source": "json", "json_path": "", "ics_path": "", "ics_url": "",
                 "poll_minutes": 60, "cache_dir": "cache"},
}
KNOWN_PLACEHOLDERS = {"school", "mascot", "sentence"}


def load(path):
    """Read agent.toml and fill in defaults. cfg['_dir'] is the folder holding it,
    which relative paths inside the file are measured from."""
    with open(path, "rb") as f:
        raw = tomllib.load(f)
    cfg = {}
    for section, defaults in DEFAULTS.items():
        merged = dict(defaults)
        merged.update(raw.get(section, {}))
        cfg[section] = merged
    cfg["school"] = dict(raw.get("school", {}))
    cfg["courses"] = [dict(c) for c in raw.get("courses", [])]
    cfg["schema"] = raw.get("schema")
    cfg["_dir"] = os.path.dirname(os.path.abspath(path))
    return cfg


def resolve(cfg, relative):
    return os.path.normpath(os.path.join(cfg["_dir"], relative))


def syllables(word):
    """A rough count (runs of vowels). Good enough to compare phrases, not a dictionary."""
    word = re.sub(r"[^a-z]", "", word.lower())
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and count > 1:
        # a silent final e ("gale") does not add a syllable, but consonant + "le" ("table") does
        if not (word.endswith("le") and len(word) > 2 and word[-3] not in "aeiouy"):
            count -= 1
    return max(1, count) if word else 0


def check(cfg):
    """Returns (errors, warnings), each a list of plain-English strings."""
    errors, warnings = [], []

    def need(ok, message):
        if not ok:
            errors.append(message)

    if cfg.get("schema") != 1:
        errors.append("schema must be 1")
    school = cfg["school"]
    for key in ("name", "id", "timezone"):
        need(school.get(key), "[school] %s is missing" % key)
    if school.get("id"):
        need(topics.valid_level(school["id"]),
             "[school] id %r must be lowercase letters, digits, and hyphens only" % school["id"])
    if school.get("timezone"):
        try:
            ZoneInfo(school["timezone"])
        except Exception:
            errors.append("[school] timezone %r is not an IANA name such as America/Chicago" % school["timezone"])
    for key in ("primary_color", "accent_color"):
        if school.get(key) and not re.fullmatch(r"#[0-9A-Fa-f]{6}", school[key]):
            errors.append("[school] %s must look like #1F5D3A" % key)

    cal = cfg["calendar"]
    need(cal["source"] in ("json", "ics"), '[calendar] source must be "json" or "ics"')
    if cal["source"] == "json":
        need(cal["json_path"] and os.path.exists(resolve(cfg, cal["json_path"])),
             "[calendar] json_path %r does not exist" % cal["json_path"])
    elif cal["source"] == "ics":
        url = os.environ.get("SCHOOL_ICS_URL") or cal["ics_url"]
        if url:
            need(re.match(r"https?://", url), "[calendar] the ICS address must start with http:// or https://")
        else:
            need(cal["ics_path"] and os.path.exists(resolve(cfg, cal["ics_path"])),
                 "[calendar] ics_path %r does not exist" % cal["ics_path"])
    need(isinstance(cal["poll_minutes"], int) and cal["poll_minutes"] >= 1, "[calendar] poll_minutes must be a whole number")
    if isinstance(cal["poll_minutes"], int) and 1 <= cal["poll_minutes"] < 15:
        warnings.append("[calendar] poll_minutes is %d: feeds change a few times a day, so under 15 is impolite" % cal["poll_minutes"])

    names = [c.get("name") for c in cfg["courses"]]
    need(len(names) == len(set(names)), "[[courses]] names must be unique")
    for c in cfg["courses"]:
        need(c.get("name"), "a [[courses]] block has no name")
        if c.get("room"):
            need(topics.valid_level(topics.slug(c["room"])), "course %r: room %r cannot make a topic" % (c.get("name"), c["room"]))
        else:
            warnings.append("course %r has no room: its reminders go to the whole school" % c.get("name"))

    for key, value in cfg["features"].items():
        need(isinstance(value, bool), "[features] %s must be true or false" % key)
    need(re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", str(cfg["briefing"]["time"])), '[briefing] time must look like "07:30"')
    need(isinstance(cfg["briefing"]["max_items"], int) and 1 <= cfg["briefing"]["max_items"] <= 5,
         "[briefing] max_items must be 1 to 5")
    for key, leads in cfg["reminders"].items():
        ok = isinstance(leads, list) and all(isinstance(n, int) and 0 <= n <= 30 for n in leads)
        need(ok, "[reminders] %s must be a list of whole numbers from 0 to 30" % key)

    voice = cfg["voice"]
    need(voice["tone"] in ("friendly", "neutral"), '[voice] tone must be "friendly" or "neutral"')
    for key in ("greeting", "reminder_test", "reminder_due", "reminder_notice"):
        text = voice[key]
        bad = set(re.findall(r"\{(\w*)\}", text)) - KNOWN_PLACEHOLDERS
        need(not bad, "[voice] %s uses unknown placeholder(s) %s; allowed: %s" % (
            key, ", ".join("{%s}" % b for b in sorted(bad)), ", ".join("{%s}" % p for p in sorted(KNOWN_PLACEHOLDERS))))
        for sentence in re.split(r"(?<=[.!?])\s+", text.replace("{sentence}", "").replace("{school}", "School").strip()):
            if len(sentence.split()) > 15:
                warnings.append("[voice] %s has a sentence over 15 words; short sentences are easier to hear" % key)
    for key, flavor in voice["flavor"].items():
        if len(flavor) > 40:
            warnings.append("[voice.flavor] %s is %d characters; keep mascot lines short" % (key, len(flavor)))

    mascot = cfg["mascot"]
    if mascot["file"]:
        path = resolve(cfg, mascot["file"])
        # the file lives beside the Pico code, one folder up from server/
        alt = os.path.join(os.path.dirname(cfg["_dir"]), mascot["file"])
        found = path if os.path.exists(path) else alt if os.path.exists(alt) else None
        if not found:
            warnings.append("[mascot] %s not found yet; run mascot_check.py --write to make it" % mascot["file"])
        else:
            expected = mascot["size"] * mascot["size"] * 2
            actual = os.path.getsize(found)
            need(actual == expected, "[mascot] %s is %d bytes but size %d needs %d" % (mascot["file"], actual, mascot["size"], expected))
    need(isinstance(mascot["size"], int) and 16 <= mascot["size"] <= 336,
         "[mascot] size must be 16 to 336 (336 is the diameter of the safe circle)")

    phrase = cfg["wake"]["phrase"]
    if not re.fullmatch(r"[A-Za-z' ]+", phrase.strip() or "?"):
        errors.append("[wake] phrase must be words made of letters")
    else:
        count = sum(syllables(w) for w in phrase.split())
        if count < 3:
            warnings.append("[wake] %r has about %d syllable(s); a longer phrase gives the detector more to compare" % (phrase, count))
        if phrase.strip().lower() != "hey pico":
            warnings.append("[wake] %r is not the default: enroll it again (Chapter 12) and re-test false accepts" % phrase)
    return errors, warnings
