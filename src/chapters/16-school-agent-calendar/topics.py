# topics.py -- topic names and the wildcard matcher (Chapter 15)
#
# Plain Python with no hardware, so the same file runs on the Pico and on your
# computer (the server tools import it too). The scheme it builds:
#
#   school/<school>/alert                          school-wide alerts
#   school/<school>/class/<room>/alert             one classroom's alerts
#   school/<school>/device/<device>/status         online / offline (retained)
#   school/<school>/device/<device>/telemetry      volume, uptime, free memory
#   school/<school>/device/<device>/echo           round-trip test (device -> server)
#   school/<school>/device/<device>/echo-reply     round-trip test (server -> device)
#
# Each level is made of lowercase letters, digits and hyphens only: no spaces,
# no "/", no "+" or "#", and never a leading "$".

ROOT = "school"


def slug(text):
    """'Lab 130' -> 'lab-130'. Anything that is not a letter or digit becomes
    one hyphen; hyphens never start, end or repeat."""
    out = []
    dash = False
    for ch in str(text).lower():
        if ("a" <= ch <= "z") or ("0" <= ch <= "9"):
            out.append(ch)
            dash = False
        elif out and not dash:
            out.append("-")
            dash = True
    while out and out[-1] == "-":
        out.pop()
    return "".join(out)


def valid_level(level):
    """True if `level` may be used as one level of a topic name."""
    if not level or level != slug(level):
        return False
    return True


def school_alert(school):
    return "%s/%s/alert" % (ROOT, school)


def room_alert(school, room):
    return "%s/%s/class/%s/alert" % (ROOT, school, room)


def device_topic(school, device, leaf):
    return "%s/%s/device/%s/%s" % (ROOT, school, device, leaf)


def device_status(school, device):
    return device_topic(school, device, "status")


def device_telemetry(school, device):
    return device_topic(school, device, "telemetry")


def valid_topic_name(topic):
    """A topic a publisher may use: not empty, no wildcards, no NUL."""
    if not topic or "+" in topic or "#" in topic or "\x00" in topic:
        return False
    return len(topic.encode()) <= 65535


def valid_filter(filt):
    """A subscription filter: '+' must be a whole level, '#' must be a whole
    level and the last one."""
    if not filt or "\x00" in filt or len(filt.encode()) > 65535:
        return False
    parts = filt.split("/")
    for i, part in enumerate(parts):
        if part == "#":
            if i != len(parts) - 1:
                return False
        elif "#" in part:
            return False
        elif "+" in part and part != "+":
            return False
    return True


def topic_matches(filt, topic):
    """Does subscription filter `filt` select topic name `topic`?
    '+' matches exactly one level. '#' matches the parent level and
    everything below it, and may only be the last level. A topic that starts
    with '$' (the broker's own) is not matched by a filter that starts with
    a wildcard."""
    if not valid_filter(filt) or not valid_topic_name(topic):
        return False
    f = filt.split("/")
    t = topic.split("/")
    if t[0].startswith("$") and (f[0] == "+" or f[0] == "#"):
        return False
    for i in range(len(f)):
        part = f[i]
        if part == "#":
            return True
        if i >= len(t):
            return False
        if part != "+" and part != t[i]:
            return False
    return len(t) == len(f)
