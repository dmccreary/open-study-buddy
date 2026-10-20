"""Events: the one shape every calendar source is turned into (Chapter 16).

Standard library only (Python 3.9 or newer; the book's server uses 3.11+).

An Event is either
  * all-day: a date range with NO time and NO time zone (a holiday is a date,
    not an instant), or
  * timed: a start (and end) stored as an aware UTC datetime.
Times are stored in UTC and converted to the school's zone only when shown.
"""
import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

UTC = timezone.utc

CATEGORIES = ("test", "due", "no-school", "academic", "event", "sports")

# Category names an iCalendar feed may carry in its CATEGORIES line.
ICS_CATEGORY_MAP = {
    "TEST": "test",
    "PROJECT_DUE": "due",
    "NO_SCHOOL": "no-school",
    "ACADEMIC_MILESTONE": "academic",
    "SCHOOL_EVENT": "event",
    "SPORTS": "sports",
}

# "TEST: Algebra II Unit 3" -> kind "test". A teacher types the prefix, so it
# wins over any category the calendar program attached.
PREFIXES = {"TEST": "test", "DUE": "due", "NO SCHOOL": "no-school"}
_PREFIX_RE = re.compile(r"^\s*(TEST|DUE|NO\s+SCHOOL)\s*:\s*(.*)$", re.IGNORECASE)


@dataclass(frozen=True)
class Event:
    uid: str
    title: str                       # the full title, prefix included
    category: str
    all_day: bool
    start_date: date                 # first day, in the school's zone
    end_date: date                   # last day, inclusive
    start_utc: Optional[datetime] = None      # timed events only
    end_utc: Optional[datetime] = None
    location: Optional[str] = None
    course: Optional[str] = None
    recurring: bool = False          # the feed had an RRULE we do not expand

    @property
    def short_id(self):
        """A compact id for alert ids: crhs-018 from crhs-018@cedar-ridge...;
        a hash when the uid is long or has odd characters."""
        base = self.uid.split("@")[0]
        if re.fullmatch(r"[A-Za-z0-9_-]{1,24}", base):
            return base
        return hashlib.sha1(self.uid.encode()).hexdigest()[:10]

    def local_start(self, tz):
        """Start as an aware datetime in `tz`. All-day events start at midnight."""
        if self.start_utc is not None:
            return self.start_utc.astimezone(tz)
        return datetime.combine(self.start_date, time(0), tzinfo=tz)

    def local_end(self, tz):
        """When the event is over, in `tz`. All-day: midnight after the last day."""
        if self.end_utc is not None:
            return self.end_utc.astimezone(tz)
        return datetime.combine(self.end_date + timedelta(days=1), time(0), tzinfo=tz)


def split_title(title):
    """('test', 'Algebra II Unit 3 - Quadratics') for 'TEST: Algebra II ...';
    (None, title) when there is no prefix."""
    match = _PREFIX_RE.match(title)
    if not match:
        return None, title.strip()
    kind = PREFIXES[re.sub(r"\s+", " ", match.group(1).upper())]
    return kind, match.group(2).strip()


def categorize(title, declared=None):
    """Category from the title prefix, else from the feed's own category
    (ICS names such as PROJECT_DUE, or our own such as 'due'), else 'event'."""
    kind, _ = split_title(title)
    if kind:
        return kind
    if declared:
        key = declared.strip()
        if key.upper() in ICS_CATEGORY_MAP:
            return ICS_CATEGORY_MAP[key.upper()]
        if key.lower() in CATEGORIES:
            return key.lower()
    return "event"


def course_of(title, courses):
    """Find the course a title is about. `courses` is a list of course names.
    Returns (course name or None, the rest of the title after the course)."""
    _, rest = split_title(title)
    for name in sorted(courses, key=len, reverse=True):          # longest first
        if rest.lower().startswith(name.lower()):
            remainder = rest[len(name):].strip()
            return name, remainder
    return None, rest


def make_local(day, hhmm, tz):
    """A school-local wall-clock time as an aware UTC datetime.

    Daylight saving needs two rules for local times that are not unique:
      * a time that does not exist (2:30 AM on the spring-forward day) is read
        with the offset in force before the change, which lands one hour later
        on the clock;
      * a time that happens twice (1:30 AM on the fall-back day) means the
        first one, the daylight-time one.
    Python's zoneinfo does exactly this with fold=0, which we rely on."""
    hour, minute = (int(x) for x in hhmm.split(":"))
    local = datetime(day.year, day.month, day.day, hour, minute, tzinfo=tz, fold=0)
    return local.astimezone(UTC)
