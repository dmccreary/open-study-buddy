"""Turn calendar facts into short sentences (Chapter 16): answers to questions,
the daily briefing, and reminder alerts. Standard library only.

Writing rules for a device that SPEAKS to grades 9 to 12:
  * one idea per sentence, about 12 words or fewer
  * say times the way people do: "8 AM", "11:03 AM", not "08:00"
  * say days the way people do: "tomorrow", "Wednesday", "next Tuesday"
  * nothing a speech engine reads badly ("vs." becomes "versus", " - " a pause)
  * calm and friendly: tell, do not scold
All the wording that is a choice lives in agent.toml, so a school changes it there.
"""
from datetime import timedelta

import alerts
import topics
from events import split_title
from query import is_school_day, next_of, on_day, upcoming

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


# ---- words for times and days --------------------------------------------------
def clock_words(dt):
    """8 AM, 11:03 AM, 12:39 PM: the way a person says it."""
    hour12 = dt.hour % 12 or 12
    suffix = "AM" if dt.hour < 12 else "PM"
    return "%d %s" % (hour12, suffix) if dt.minute == 0 else "%d:%02d %s" % (hour12, dt.minute, suffix)


def clock_short(dt):
    """8:00 AM: for the display, where a steady width reads better."""
    return "%d:%02d %s" % (dt.hour % 12 or 12, dt.minute, "AM" if dt.hour < 12 else "PM")


def day_words(day, today):
    """today, tomorrow, Wednesday (within a week), or Tuesday, November 10.
    There is no "next Tuesday": people disagree about what it means."""
    gap = (day - today).days
    if gap == 0:
        return "today"
    if gap == 1:
        return "tomorrow"
    if 2 <= gap <= 6:
        return WEEKDAYS[day.weekday()]
    return "%s, %s %d" % (WEEKDAYS[day.weekday()], MONTHS[day.month - 1], day.day)


def shorten(text, limit):
    return text if len(text) <= limit else text[:limit - 3].rstrip() + "..."


def speakable(text, say):
    """Apply the school's text-to-speech replacements, e.g. 'vs.' -> 'versus'."""
    for old, new in say.items():
        text = text.replace(old, new)
    return " ".join(text.split())


def sentence_case(text):
    return text[:1].upper() + text[1:]


# ---- one event, in words ----------------------------------------------------------
def when_phrase(event, tz, today):
    """'tomorrow at 8 AM', 'on Wednesday', 'today'. All-day events have no time."""
    start = event.local_start(tz)
    day = day_words(start.date(), today)
    on = "" if day in ("today", "tomorrow") else "on "
    if event.all_day:
        return on + day
    return "%s%s at %s" % (on, day, clock_words(start))


def name_of(event):
    """The event's name without TEST:/DUE:. A test becomes 'Algebra II test'."""
    _, rest = split_title(event.title)
    if event.category == "test" and event.course:
        return event.course + " test"
    return rest


def sentence_for(event, tz, today, say):
    """One or two short sentences about an event."""
    name = speakable(name_of(event), say)
    when = when_phrase(event, tz, today)
    if event.category == "test":
        return "Your %s is %s." % (name, when)
    if event.category == "due":
        return "%s is due %s." % (sentence_case(name), when)
    if event.category == "no-school":
        return "No school %s: %s." % (when, speakable(split_title(event.title)[1], say))
    where = " Location: %s." % speakable(event.location, say) if event.location else ""
    return "%s is %s.%s" % (sentence_case(name), when, where)


def display_when(event, tz, today):
    """Line 2 of the display, 30 characters at most: 'Tomorrow 8:00 AM', 'Due Wednesday'."""
    start = event.local_start(tz)
    gap = (start.date() - today).days
    if gap == 0:
        day = "Today"
    elif gap == 1:
        day = "Tomorrow"
    elif 2 <= gap <= 6:
        day = WEEKDAYS[start.weekday()]
    else:
        day = "%s %s %d" % (WEEKDAYS[start.weekday()][:3], MONTHS[start.month - 1][:3], start.day)
    if event.category == "due":
        return shorten("Due " + (day.lower() if gap in (0, 1) else day), 30)
    if event.category == "no-school" and event.end_date != event.start_date:
        end = event.end_date
        return shorten("%s to %s %s %d" % (day, WEEKDAYS[end.weekday()][:3], MONTHS[end.month - 1][:3], end.day), 30)
    if event.all_day:
        return shorten(day, 30)
    return shorten("%s %s" % (day, clock_short(start)), 30)


# ---- answers -------------------------------------------------------------------------
def _reply(speak, show, mode="clock"):
    return {"speak": speak, "show": shorten(show, 30), "next_mode": mode}


def _course_in(text, cal):
    low = text.lower()
    for name in sorted(cal.course_names(), key=len, reverse=True):
        if name.lower() in low:
            return name
    return None


def _weekday_in(low):
    for i, name in enumerate(WEEKDAYS):
        if name.lower() in low:
            return i
    return None


def answer(text, cal, now, cfg):
    """A rule-based answer to a spoken question, in Chapter 1's reply shape:
    {"speak": ..., "show": ..., "next_mode": ...}. Anything it does not
    recognise gets an honest apology: that gap is what an LLM brain fills."""
    say = cfg["voice"].get("say", {})
    tz, today = cal.tz, now.date()
    low = text.lower()
    course = _course_in(text, cal)

    if "school" in low and (_weekday_in(low) is not None or "tomorrow" in low or "today" in low):
        if "tomorrow" in low:
            day = today + timedelta(days=1)
        elif "today" in low:
            day = today
        else:
            day = today + timedelta(days=(_weekday_in(low) - today.weekday()) % 7)
        word = day_words(day, today)
        label = word if word in ("today", "tomorrow") else "on " + WEEKDAYS[day.weekday()]
        if is_school_day(cal, day):
            extras = [e for e in on_day(cal, day) if e.category in ("sports", "event", "test")]
            tail = " " + sentence_for(extras[0], tz, today, say) if extras else ""
            return _reply("Yes, there is school %s.%s" % (label, tail), "School %s" % label.replace("on ", ""))
        reason = [e for e in on_day(cal, day) if e.category == "no-school"]
        why = ": " + speakable(split_title(reason[0].title)[1], say) if reason else ""
        return _reply("No, there is no school %s%s." % (label, why), "No school %s" % label.replace("on ", ""))

    if "test" in low or "exam" in low:
        event = next_of(cal, now, "test", course)
        if not event:
            return _reply("I do not see a test coming up.", "No tests ahead")
        _, rest = split_title(event.title)
        return _reply("Your next test is %s, %s." % (speakable(rest, say), when_phrase(event, tz, today)),
                      "%s: %s" % (name_of(event), when_phrase(event, tz, today).replace(" at ", " ")))

    if any(word in low for word in ("due", "homework", "project", "assignment")):
        found = upcoming(cal, now, days=7, categories=("due",), course=course, limit=3)
        if not found:
            return _reply("Nothing is due in the next week.", "Nothing due this week")
        return _reply(" ".join(sentence_for(e, tz, today, say) for e in found), "%d due this week" % len(found))

    if "end" in low and ("quarter" in low or "semester" in low):
        word = "quarter" if "quarter" in low else "semester"
        for event in upcoming(cal, now, days=366, categories=("academic",)):
            if "end of" in event.title.lower() and word in event.title.lower():
                return _reply("%s is %s." % (speakable(event.title, say), when_phrase(event, tz, today)), event.title)

    if any(word in low for word in ("today", "tonight", "tomorrow", "happening")):
        day = today + timedelta(days=1) if "tomorrow" in low else today
        label = "tomorrow" if day != today else ("tonight" if "tonight" in low else "today")
        found = on_day(cal, day)
        if "tonight" in low:
            found = [e for e in found if not e.all_day and e.local_start(tz).hour >= 17]
        if not found:
            return _reply("Nothing is on the calendar %s." % label, "Nothing %s" % label)
        speak = " ".join(sentence_for(e, tz, today, say) for e in found[:3])
        return _reply(speak, "%d event%s %s" % (len(found), "" if len(found) == 1 else "s", label))

    return _reply("Sorry, I only know about tests, due dates, and school days.", "Try: next test?")


# ---- the daily briefing -----------------------------------------------------------------
def daily_briefing(cal, now, cfg):
    """{"speak", "show"} for the morning of now.date(), or None when it is not
    a school day (a weekend or a no-school day)."""
    tz, today = cal.tz, now.date()
    if not is_school_day(cal, today):
        return None
    voice, brief = cfg["voice"], cfg["briefing"]
    say = voice.get("say", {})
    school = cfg["school"].get("short_name") or cfg["school"]["name"]
    limit = brief["max_items"]
    sentences = [voice["greeting"].format(school=school, mascot=cfg["mascot"]["name"])]

    todays = [e for e in on_day(cal, today) if e.category in ("test", "due", "event", "sports", "academic")]
    if todays:
        sentences += [sentence_for(e, tz, today, say) for e in todays[:limit]]
        if len(todays) > limit:
            sentences.append("%d more things are on the calendar today." % (len(todays) - limit))
    else:
        sentences.append("Nothing special is on the calendar today.")

    window = brief["upcoming_days"]
    tests = [e for e in upcoming(cal, now, days=window, categories=("test",)) if e.start_date > today]
    if tests:
        sentences.append(sentence_for(tests[0], tz, today, say).replace("Your ", "Your next ", 1))
    dues = [e for e in upcoming(cal, now, days=window, categories=("due",)) if e.start_date > today]
    sentences += [sentence_for(e, tz, today, say) for e in dues[:limit]]
    if voice.get("mascot_flavor") and voice.get("flavor", {}).get("briefing"):
        sentences.append(voice["flavor"]["briefing"])

    soon = upcoming(cal, now, days=2, categories=("test",))
    if soon:
        show = "Test " + day_words(soon[0].start_date, today)
    else:
        show = "%d thing%s today" % (len(todays), "" if len(todays) == 1 else "s") if todays else "Quiet day"
    return {"speak": " ".join(sentences), "sentences": sentences, "show": shorten(show, 30)}


def fit_sentences(sentences, limit):
    """Join as many whole sentences as fit in `limit` characters, in order.
    Never cuts a sentence in half; the last ones (the optional mascot line, the
    farthest due dates) are the first to go."""
    out = ""
    for sentence in sentences:
        joined = (out + " " + sentence) if out else sentence
        if len(joined) > limit:
            break
        out = joined
    return out


# ---- reminders -------------------------------------------------------------------------------
def _room_route(event, cfg):
    """('room', slug) for the event's course, else ('school', None)."""
    for course in cfg["courses"]:
        if course["name"] == event.course and course.get("room"):
            return "room", topics.slug(course["room"])
    return "school", None


def send_day(cal, wanted):
    """The day a reminder wanted for `wanted` is really sent: that day if it is a
    school day, else the last school day before it (so a Monday test is
    reminded on Friday, not on a Sunday when the job does not run)."""
    day = wanted
    for _ in range(14):
        if is_school_day(cal, day):
            return day
        day -= timedelta(days=1)
    return wanted


def reminders(cal, now, cfg):
    """The alerts to send today: one per (event, lead time) whose send day (see
    send_day) is now.date(). Ids are built from the date, the event, and the lead, so
    running the job twice on the same day sends the same ids and the device
    drops the repeat. Returns [(route, alert dict)] where route is
    ('school', None) or ('room', slug)."""
    tz, today = cal.tz, now.date()
    voice, rules, features = cfg["voice"], cfg["reminders"], cfg["features"]
    say = voice.get("say", {})
    out = []
    plan = (("test", rules["test_days_before"], features["test_alerts"], voice["reminder_test"]),
            ("due", rules["due_days_before"], features["due_alerts"], voice["reminder_due"]),
            ("no-school", rules["no_school_days_before"], features["no_school_notices"], voice["reminder_notice"]))
    for category, leads, enabled, template in plan:
        if not enabled:
            continue
        for event in cal.events:
            if event.category != category or event.recurring:
                continue
            for lead in leads:
                if send_day(cal, event.start_date - timedelta(days=lead)) != today:
                    continue
                sentence = sentence_for(event, tz, today, say)
                text = template.format(sentence=sentence)
                flavor = voice.get("flavor", {}).get(category) if voice.get("mascot_flavor") else None
                if flavor and len(text) + 1 + len(flavor) <= alerts.MAX_TEXT:
                    text = text + " " + flavor
                if category == "no-school":
                    title = shorten("No school " + day_words(event.start_date, today), alerts.MAX_TITLE)
                    when_line = shorten(split_title(event.title)[1], alerts.MAX_WHEN)
                else:
                    title = shorten(name_of(event), alerts.MAX_TITLE)
                    when_line = display_when(event, tz, today)
                at = event.start_utc.strftime("%Y-%m-%dT%H:%MZ") if event.start_utc else None
                alert = alerts.make_alert(
                    "%s-%s-d%d" % (today.strftime("%Y%m%d"), event.short_id, lead),
                    "notice" if category == "no-school" else category,
                    title, when_line, shorten(text, alerts.MAX_TEXT), at)
                out.append((_room_route(event, cfg) if category != "no-school" else ("school", None), alert))
    return out
