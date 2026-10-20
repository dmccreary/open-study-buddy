"""Questions you can ask a Calendar (Chapter 16). Standard library only.

`now` is always an aware datetime in the school's time zone, so "today" means
the school's today, whatever time zone the server computer is set to.
"""
from datetime import timedelta


def _sort_key(event, tz):
    return (event.local_start(tz), event.title)


def is_upcoming(event, now):
    """True if the event has not finished yet. A timed event that has started
    but not ended still counts; an all-day event counts through its last day."""
    end = event.local_end(now.tzinfo)
    if event.start_utc is not None and event.end_utc == event.start_utc:
        return event.local_start(now.tzinfo) >= now          # zero-length: only before it starts
    return end > now


def upcoming(cal, now, days=14, categories=None, course=None, limit=None):
    """Events that start within `days` days (or are under way), earliest first."""
    horizon = now + timedelta(days=days)
    found = []
    for event in cal.events:
        if categories and event.category not in categories:
            continue
        if course and event.course != course:
            continue
        if not is_upcoming(event, now):
            continue
        if event.local_start(cal.tz) >= horizon:
            continue
        found.append(event)
    found.sort(key=lambda e: _sort_key(e, cal.tz))
    return found[:limit] if limit else found


def next_of(cal, now, category, course=None):
    """The next event of one category (the next test, the next project due)."""
    horizon_days = 366
    found = upcoming(cal, now, days=horizon_days, categories=(category,), course=course, limit=1)
    return found[0] if found else None


def on_day(cal, day):
    """Events that include the calendar date `day` (a datetime.date), in order."""
    found = [e for e in cal.events if e.start_date <= day <= e.end_date]
    found.sort(key=lambda e: _sort_key(e, cal.tz))
    return found


def is_school_day(cal, day):
    """A weekday with no 'no-school' event covering it."""
    if day.weekday() >= 5:
        return False
    return not any(e.category == "no-school" for e in on_day(cal, day))


def next_school_day(cal, day):
    """The first school day after `day`."""
    probe = day + timedelta(days=1)
    for _ in range(400):
        if is_school_day(cal, probe):
            return probe
        probe += timedelta(days=1)
    return None
