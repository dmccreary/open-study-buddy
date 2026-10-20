r"""A small, careful iCalendar (RFC 5545) reader for school calendars (Chapter 16).

Standard library only. It runs on the SERVER, never on the Pico.

What it handles
  * line unfolding (a line that starts with a space or tab continues the one before)
  * parameters, including quoted values:  DTSTART;TZID="America/Chicago":2026...
  * text escapes  \\, \; \\\\ \\n
  * VEVENT blocks only; everything inside VTIMEZONE (and VALARM) is skipped
  * all-day events (VALUE=DATE; the end date is EXCLUSIVE in iCalendar)
  * UTC times ending in Z, TZID times, and "floating" times with no zone
    (read as the school's local time)
  * STATUS:CANCELLED events are dropped

What it deliberately does NOT handle (it warns and carries on)
  * RRULE / RDATE / EXDATE recurrence: the event is kept once, marked recurring
  * time zones the system's zoneinfo database does not know (Windows zone
    names such as "Central Standard Time"): the event is skipped
  * the definitions inside VTIMEZONE: we trust the IANA name in TZID instead
  * DURATION instead of DTEND (a missing end means a zero-length event)
For recurring events or messy feeds from Outlook or Google, use the
`icalendar` and `recurring-ical-events` packages instead.
"""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from events import UTC, Event, categorize, course_of


def unfold(text):
    """Split into logical lines, joining continuation lines."""
    lines = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        elif raw != "":
            lines.append(raw)
    return lines


def parse_line(line):
    """'DTSTART;TZID=America/Chicago:20261020T080000' ->
    ('DTSTART', {'TZID': 'America/Chicago'}, '20261020T080000').
    The first ':' that is not inside double quotes ends the name and parameters."""
    in_quotes = False
    for i, ch in enumerate(line):
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == ":" and not in_quotes:
            head, value = line[:i], line[i + 1:]
            break
    else:
        raise ValueError("no ':' in line: %r" % line[:40])
    parts, current, in_quotes = [], "", False
    for ch in head:
        if ch == '"':
            in_quotes = not in_quotes
            current += ch
        elif ch == ";" and not in_quotes:
            parts.append(current)
            current = ""
        else:
            current += ch
    parts.append(current)
    params = {}
    for part in parts[1:]:
        if "=" in part:
            key, val = part.split("=", 1)
            params[key.upper()] = val.strip('"')
    return parts[0].upper(), params, value


def unescape(value):
    out, i = [], 0
    while i < len(value):
        ch = value[i]
        if ch == "\\" and i + 1 < len(value):
            nxt = value[i + 1]
            out.append("\n" if nxt in "nN" else nxt)
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def parse_when(value, params, school_tz):
    """Returns ('date', date) or ('time', aware UTC datetime)."""
    if params.get("VALUE") == "DATE" or (len(value) == 8 and value.isdigit()):
        return "date", date(int(value[:4]), int(value[4:6]), int(value[6:8]))
    stamp = value.rstrip("Z")
    naive = datetime(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:8]),
                     int(stamp[9:11]), int(stamp[11:13]), int(stamp[13:15] or 0))
    if value.endswith("Z"):
        return "time", naive.replace(tzinfo=UTC)
    zone = school_tz
    if "TZID" in params:
        zone = ZoneInfo(params["TZID"])                 # may raise ZoneInfoNotFoundError
    return "time", naive.replace(tzinfo=zone, fold=0).astimezone(UTC)


class ParseResult:
    def __init__(self):
        self.events = []
        self.warnings = []


def parse_ics(text, school_tz, courses=()):
    """Parse feed text into Events. `school_tz` is a ZoneInfo."""
    result = ParseResult()
    depth_skip = 0            # >0 while inside VTIMEZONE / VALARM
    current = None            # dict of properties while inside a VEVENT
    for line in unfold(text):
        try:
            name, params, value = parse_line(line)
        except ValueError as error:
            result.warnings.append("skipped a line: %s" % error)
            continue
        if name == "BEGIN":
            kind = value.upper()
            if kind == "VEVENT" and depth_skip == 0:
                current = {"_params": {}}
            elif kind in ("VTIMEZONE", "VALARM"):
                depth_skip += 1
            continue
        if name == "END":
            kind = value.upper()
            if kind in ("VTIMEZONE", "VALARM"):
                depth_skip = max(0, depth_skip - 1)
            elif kind == "VEVENT" and current is not None:
                _finish(current, school_tz, courses, result)
                current = None
            continue
        if current is not None and depth_skip == 0 and name not in current:
            current[name] = value
            current["_params"][name] = params
    return result


def _finish(props, school_tz, courses, result):
    uid = props.get("UID", "")
    title = unescape(props.get("SUMMARY", "")).strip()
    label = title or uid or "(no title)"
    if props.get("STATUS", "").upper() == "CANCELLED":
        return
    if "DTSTART" not in props:
        result.warnings.append("%s: no DTSTART, skipped" % label)
        return
    try:
        kind, start = parse_when(props["DTSTART"], props["_params"]["DTSTART"], school_tz)
        end = None
        if "DTEND" in props:
            end_kind, end = parse_when(props["DTEND"], props["_params"]["DTEND"], school_tz)
            if end_kind != kind:
                result.warnings.append("%s: DTSTART and DTEND are different kinds, end ignored" % label)
                end = None
    except ZoneInfoNotFoundError as error:
        result.warnings.append("%s: unknown time zone %s, skipped" % (label, error))
        return
    except (ValueError, IndexError) as error:
        result.warnings.append("%s: bad date or time (%s), skipped" % (label, error))
        return
    recurring = any(key in props for key in ("RRULE", "RDATE"))
    if recurring:
        result.warnings.append("%s: has a recurrence rule; kept once, not expanded" % label)
    declared = unescape(props.get("CATEGORIES", "")).split(",")[0] or None
    location = unescape(props["LOCATION"]).strip() or None if "LOCATION" in props else None
    course, _ = course_of(title, courses)
    common = dict(uid=uid or label, title=title, category=categorize(title, declared),
                  location=location, course=course, recurring=recurring)
    if kind == "date":
        last = (end - timedelta(days=1)) if end else start        # DTEND is exclusive
        if last < start:
            last = start
        result.events.append(Event(all_day=True, start_date=start, end_date=last, **common))
    else:
        end = end or start
        result.events.append(Event(
            all_day=False, start_date=start.astimezone(school_tz).date(),
            end_date=end.astimezone(school_tz).date(), start_utc=start, end_utc=end, **common))
