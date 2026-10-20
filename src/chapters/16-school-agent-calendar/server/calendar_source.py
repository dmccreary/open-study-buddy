"""Load a school calendar from events.json, a calendar.ics file, or an ICS URL
(Chapter 16). Standard library only; runs on the SERVER.

Three sources, one result: a Calendar holding a list of Events in the school's
time zone, plus the course list. Everything downstream (queries, briefings,
reminders) works on Calendar and never knows where the events came from.

Polling a feed politely: the server fetches a URL at most once per
`poll_minutes`, sends the ETag / Last-Modified it saw last time so an unchanged
feed costs a tiny "304 Not Modified" answer, and keeps using its saved copy if
the feed is down. The Pico never talks to the feed.
"""
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from zoneinfo import ZoneInfo

from events import CATEGORIES, Event, categorize, course_of, make_local
from ics_parser import parse_ics

USER_AGENT = "OpenStudyBuddy-calendar/1.0 (school server; polite poller)"


@dataclass
class Calendar:
    school: str
    tz: ZoneInfo
    courses: list                      # [{"course": ..., "teacher": ..., "room": ...}]
    events: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    source: str = ""                   # what was loaded, for messages

    def course_names(self):
        return [c["course"] for c in self.courses]


def json_problems(data):
    """Check an events.json structure. Returns a list of plain-English problems."""
    problems = []
    if not isinstance(data, dict):
        return ["the file must hold one JSON object"]
    for key in ("school", "timezone", "events"):
        if key not in data:
            problems.append("missing top-level key %r" % key)
    if problems:
        return problems
    try:
        ZoneInfo(data["timezone"])
    except Exception:
        problems.append("timezone %r is not an IANA name such as America/Chicago" % data["timezone"])
    seen = set()
    for i, ev in enumerate(data["events"], 1):
        where = "event %d (%s)" % (i, ev.get("title", "no title") if isinstance(ev, dict) else "?")
        if not isinstance(ev, dict):
            problems.append("%s: not an object" % where)
            continue
        for key in ("id", "title", "date"):
            if not ev.get(key):
                problems.append("%s: missing %r" % (where, key))
        if ev.get("id") in seen:
            problems.append("%s: duplicate id %r" % (where, ev.get("id")))
        seen.add(ev.get("id"))
        try:
            first = date.fromisoformat(ev["date"])
            last = date.fromisoformat(ev.get("end_date") or ev["date"])
            if last < first:
                problems.append("%s: end_date is before date" % where)
        except (KeyError, ValueError, TypeError):
            problems.append("%s: date must look like 2026-10-20" % where)
        if ev.get("all_day", True) is False:
            for key in ("start",):
                value = ev.get(key)
                if not isinstance(value, str) or len(value) != 5 or value[2] != ":":
                    problems.append("%s: a timed event needs start like \"08:00\"" % where)
        if ev.get("category") and ev["category"] not in CATEGORIES:
            problems.append("%s: category %r is not one of %s" % (where, ev["category"], ", ".join(CATEGORIES)))
    return problems


def from_json(data, courses_extra=None):
    """Build a Calendar from the parsed contents of events.json."""
    problems = json_problems(data)
    if problems:
        raise ValueError("events.json: " + "; ".join(problems))
    tz = ZoneInfo(data["timezone"])
    courses = [dict(c) for c in data.get("courses", [])]
    if courses_extra:
        by_name = {c["course"]: c for c in courses}
        for extra in courses_extra:
            by_name.setdefault(extra["course"], {}).update(extra)
        courses = list(by_name.values())
    names = [c["course"] for c in courses]
    cal = Calendar(school=data["school"], tz=tz, courses=courses, source="events.json")
    for ev in data["events"]:
        first = date.fromisoformat(ev["date"])
        last = date.fromisoformat(ev.get("end_date") or ev["date"])
        category = ev.get("category") or categorize(ev["title"])
        course = ev.get("course") or course_of(ev["title"], names)[0]
        common = dict(uid=ev["id"], title=ev["title"], category=category,
                      location=ev.get("location"), course=course)
        if ev.get("all_day", True):
            cal.events.append(Event(all_day=True, start_date=first, end_date=last, **common))
        else:
            start = make_local(first, ev["start"], tz)
            end = make_local(last, ev.get("end") or ev["start"], tz)
            cal.events.append(Event(all_day=False, start_date=first, end_date=last,
                                    start_utc=start, end_utc=end, **common))
    return cal


def from_ics(text, school, tz_name, courses, source="calendar.ics"):
    tz = ZoneInfo(tz_name)
    names = [c["course"] for c in courses]
    parsed = parse_ics(text, tz, names)
    return Calendar(school=school, tz=tz, courses=[dict(c) for c in courses],
                    events=parsed.events, warnings=parsed.warnings, source=source)


class FeedCache:
    """Fetch a URL politely and keep a copy on disk."""

    def __init__(self, url, cache_path, min_interval_s=3600, timeout_s=10, clock=time.time):
        self.url = url
        self.cache_path = cache_path
        self.meta_path = cache_path + ".meta.json"
        self.min_interval_s = min_interval_s
        self.timeout_s = timeout_s
        self.clock = clock
        self.requests_made = 0

    def _meta(self):
        try:
            with open(self.meta_path) as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def _save(self, meta):
        with open(self.meta_path, "w") as f:
            json.dump(meta, f)

    def text(self):
        """Returns (feed text, status). status says what happened:
        'fetched', 'not-modified', 'recent' (inside the polling interval, no
        request made), or 'stale' (the fetch failed; the old copy is used).
        Raises OSError if there is neither a fresh nor a saved copy."""
        meta = self._meta()
        now = self.clock()
        have_copy = os.path.exists(self.cache_path)
        if have_copy and now < meta.get("next_check", 0):
            return self._read(), "recent"
        request = urllib.request.Request(self.url, headers={"User-Agent": USER_AGENT})
        if have_copy and meta.get("etag"):
            request.add_header("If-None-Match", meta["etag"])
        if have_copy and meta.get("last_modified"):
            request.add_header("If-Modified-Since", meta["last_modified"])
        self.requests_made += 1
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                body = response.read()
                with open(self.cache_path, "wb") as f:
                    f.write(body)
                self._save({"etag": response.headers.get("ETag"),
                            "last_modified": response.headers.get("Last-Modified"),
                            "fetched_at": now, "next_check": now + self.min_interval_s})
                return body.decode("utf-8"), "fetched"
        except urllib.error.HTTPError as error:
            if error.code == 304 and have_copy:
                meta["next_check"] = now + self.min_interval_s
                self._save(meta)
                return self._read(), "not-modified"
            problem = error
        except (urllib.error.URLError, OSError) as error:
            problem = error
        if have_copy:                       # the feed is down: use the old copy, and wait before asking again
            meta["next_check"] = now + min(self.min_interval_s, 300)
            self._save(meta)
            return self._read(), "stale"
        raise OSError("could not fetch %s and there is no saved copy: %s" % (self.url, problem))

    def _read(self):
        with open(self.cache_path, encoding="utf-8") as f:
            return f.read()
