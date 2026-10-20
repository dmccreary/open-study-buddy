#!/usr/bin/env python3
"""Build the Cedar Ridge High School calendar files from one source list.

Writes three views of the same data into docs/schools/cedar-ridge-high-school/:

    events.json   hand-editable event list for the buddy server (Chapter 16)
    calendar.ics  iCalendar feed with the same events
    calendar.md   human-readable month-by-month calendar page

Run from the repo root:  python scripts/build-school-calendar.py
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs/schools/cedar-ridge-high-school"
SCHOOL = "Cedar Ridge High School"
TZ = "America/Chicago"
YEAR = "2026-2027"
DEMO_DATE = date(2026, 10, 19)  # suggested "today" for a live demo

CATEGORIES = {
    "no-school": "No school",
    "test": "Test",
    "due": "Project due",
    "academic": "Academic milestone",
    "event": "School event",
    "sports": "Sports",
}

COURSES = {
    "Algebra II": "Ms. Okafor",
    "English 10": "Mr. Lindqvist",
    "Biology": "Dr. Tran",
    "World History": "Ms. Alvarez",
    "Spanish II": "Sr. Moreno",
    "Physical Computing": "Mr. Brandt",
}

EVENTS = []


def ev(cat, d, title, start=None, end=None, loc=None, end_date=None, course=None, desc=None):
    d = date.fromisoformat(d)
    end_date = date.fromisoformat(end_date) if end_date else d
    EVENTS.append(dict(cat=cat, date=d, end_date=end_date, title=title, start=start,
                       end=end, loc=loc, course=course, desc=desc))


def test(d, course, what, start="08:00"):
    ev("test", d, f"TEST: {course} {what}", start=start, course=course, loc=None)


def due(d, course, what):
    ev("due", d, f"DUE: {course} {what}", course=course)


# ---- August / September -------------------------------------------------
ev("academic", "2026-08-25", "First Day of School")
due("2026-08-28", "Physical Computing", "signed lab-safety form")
ev("no-school", "2026-09-07", "NO SCHOOL: Labor Day")
ev("event", "2026-09-10", "Back-to-School Night", "18:30", "20:00", "Auditorium")
ev("event", "2026-09-14", "Homecoming Week", end_date="2026-09-18")
test("2026-09-15", "Algebra II", "Unit 1 - Linear Review")
ev("sports", "2026-09-18", "Homecoming Football vs. Lakeside Lions", "19:00", "21:00", "Griffin Field")
ev("event", "2026-09-19", "Homecoming Dance", "19:00", "22:00", "Main Gym")
test("2026-09-22", "Biology", "Unit 1 - Cells")
due("2026-09-25", "World History", "river-valley map project")
test("2026-09-29", "Algebra II", "Unit 2 - Functions")
# ---- October ------------------------------------------------------------
due("2026-10-02", "Spanish II", "vocabulary portfolio")
test("2026-10-06", "Spanish II", "Unit 2 oral quiz", "12:39")
test("2026-10-08", "World History", "Unit 1 - Ancient River Valleys", "11:03")
ev("event", "2026-10-09", "Fall Picture Day", loc="Library")
ev("no-school", "2026-10-15", "NO SCHOOL: Fall Break", end_date="2026-10-16")
ev("event", "2026-10-19", "Picture Retake Day", loc="Library")
test("2026-10-20", "Algebra II", "Unit 3 - Quadratics")
due("2026-10-21", "English 10", "personal narrative draft")
due("2026-10-22", "Biology", "osmosis lab report")
ev("sports", "2026-10-23", "Football vs. Eastbrook Eagles", "19:00", "21:00", "Griffin Field")
ev("event", "2026-10-26", "Maker Club: Study Buddy Build Night", "15:30", "17:00", "Room 214")
ev("event", "2026-10-28", "PSAT 10", "08:00", "11:30", "Main Gym")
ev("event", "2026-10-30", "Spirit Day: Green and Gold")
ev("academic", "2026-10-30", "End of Quarter 1")
# ---- November -----------------------------------------------------------
ev("no-school", "2026-11-03", "NO SCHOOL: Election Day / Staff Development")
ev("academic", "2026-11-05", "Quarter 1 Report Cards Posted")
ev("event", "2026-11-09", "Maker Club: Study Buddy Build Night", "15:30", "17:00", "Room 214")
test("2026-11-10", "Biology", "Unit 2 - Genetics", "10:02")
ev("event", "2026-11-11", "Veterans Day Assembly", "09:00", "09:45", "Auditorium")
due("2026-11-12", "World History", "primary-source essay")
ev("event", "2026-11-13", "Fall Play: Our Town", "19:00", "21:00", "Auditorium")
test("2026-11-17", "Spanish II", "Unit 3", "12:39")
ev("event", "2026-11-19", "Parent-Teacher Conferences", "16:00", "20:00", "Main Hallway")
due("2026-11-20", "Algebra II", "Parabola in the Wild project")
ev("event", "2026-11-23", "Maker Club: Study Buddy Build Night", "15:30", "17:00", "Room 214")
ev("no-school", "2026-11-25", "NO SCHOOL: Thanksgiving Break", end_date="2026-11-27")
# ---- December -----------------------------------------------------------
test("2026-12-01", "Algebra II", "Unit 4 - Polynomials")
due("2026-12-03", "Biology", "genetics poster")
test("2026-12-08", "World History", "Unit 2 - Classical Civilizations", "11:03")
ev("event", "2026-12-10", "Winter Concert", "19:00", "20:30", "Auditorium")
due("2026-12-11", "English 10", "personal narrative final")
ev("academic", "2026-12-18", "Early Dismissal 12:00 PM (Winter Break Begins)")
ev("no-school", "2026-12-21", "NO SCHOOL: Winter Break", end_date="2027-01-01")
# ---- January ------------------------------------------------------------
ev("academic", "2027-01-04", "School Resumes")
due("2027-01-07", "Spanish II", "skit script")
due("2027-01-08", "Physical Computing", "sensor-project writeup")
test("2027-01-12", "Algebra II", "Semester 1 Final", "08:00")
test("2027-01-13", "English 10", "Semester 1 Final", "08:00")
test("2027-01-14", "Biology", "Semester 1 Final", "08:00")
test("2027-01-15", "World History", "Semester 1 Final", "08:00")
test("2027-01-15", "Spanish II", "Semester 1 Final", "10:30")
ev("academic", "2027-01-15", "End of Semester 1")
ev("no-school", "2027-01-18", "NO SCHOOL: Martin Luther King Jr. Day")
ev("academic", "2027-01-19", "Semester 2 Begins")
test("2027-01-28", "Biology", "Unit 3 - Cell Energy", "10:02")
# ---- February -----------------------------------------------------------
due("2027-02-04", "English 10", "research paper outline")
test("2027-02-09", "Algebra II", "Unit 5 - Exponentials")
ev("no-school", "2027-02-15", "NO SCHOOL: Presidents' Day")
due("2027-02-17", "Biology", "science-fair project board")
ev("event", "2027-02-18", "Science Fair", "16:00", "19:00", "Main Gym")
test("2027-02-23", "World History", "Unit 3 - Medieval World", "11:03")
due("2027-02-26", "Spanish II", "Unit 5 project")
# ---- March --------------------------------------------------------------
test("2027-03-04", "Spanish II", "Unit 6", "12:39")
test("2027-03-09", "Algebra II", "Unit 6 - Logarithms")
due("2027-03-12", "English 10", "research paper draft")
test("2027-03-16", "Biology", "Unit 4 - Evolution", "10:02")
ev("event", "2027-03-19", "Spring Musical", "19:00", "21:30", "Auditorium")
due("2027-03-25", "World History", "debate preparation packet")
ev("academic", "2027-03-26", "End of Quarter 3")
ev("no-school", "2027-03-29", "NO SCHOOL: Spring Break", end_date="2027-04-02")
# ---- April --------------------------------------------------------------
ev("academic", "2027-04-05", "School Resumes (Quarter 4 Begins)")
ev("academic", "2027-04-08", "Quarter 3 Report Cards Posted")
test("2027-04-13", "Algebra II", "Unit 7 - Trigonometry")
due("2027-04-16", "English 10", "research paper final")
test("2027-04-20", "Biology", "Unit 5 - Ecology", "10:02")
ev("event", "2027-04-24", "Prom", "19:00", "23:00", "Main Gym")
test("2027-04-27", "Spanish II", "Unit 7", "12:39")
# ---- May / June ---------------------------------------------------------
ev("event", "2027-05-04", "AP Exams", end_date="2027-05-14")
due("2027-05-06", "World History", "final project")
test("2027-05-11", "World History", "Unit 5 - Revolutions", "11:03")
test("2027-05-18", "Algebra II", "Unit 8 - Statistics")
due("2027-05-21", "Biology", "ecology field journal")
ev("no-school", "2027-05-25", "NO SCHOOL: Memorial Day")
ev("event", "2027-05-27", "Spring Concert", "19:00", "20:30", "Auditorium")
ev("event", "2027-05-29", "Graduation", "10:00", "12:00", "Griffin Field")
test("2027-06-01", "Algebra II", "Final Exam", "08:00")
test("2027-06-01", "English 10", "Final Exam", "10:30")
test("2027-06-02", "Biology", "Final Exam", "08:00")
test("2027-06-02", "World History", "Final Exam", "10:30")
test("2027-06-03", "Spanish II", "Final Exam", "08:00")
ev("academic", "2027-06-03", "Last Day of School (Early Dismissal 12:00 PM)")

EVENTS.sort(key=lambda e: (e["date"], e["start"] or "00:00", e["title"]))
for i, e in enumerate(EVENTS, 1):
    e["id"] = f"crhs-{i:03d}"


def days(e):
    d = e["date"]
    while d <= e["end_date"]:
        yield d
        d += timedelta(days=1)


def check():
    off = {d for e in EVENTS if e["cat"] == "no-school" for d in days(e)}
    for e in EVENTS:
        if e["cat"] in ("test", "due"):
            assert e["date"].weekday() < 5, f"weekend: {e['title']} {e['date']}"
            assert e["date"] not in off, f"on a no-school day: {e['title']} {e['date']}"
        if e["cat"] == "no-school":
            assert e["date"].weekday() < 5, f"break starts on a weekend: {e['title']}"
        assert e["title"].startswith("TEST:") == (e["cat"] == "test")
        assert e["title"].startswith("DUE:") == (e["cat"] == "due")


check()


def fmt_time(t):
    h, m = map(int, t.split(":"))
    return f"{(h - 1) % 12 + 1}:{m:02d} {'AM' if h < 12 else 'PM'}"


def when(e):
    if not e["start"]:
        return "All day"
    s = fmt_time(e["start"])
    return f"{s}–{fmt_time(e['end'])}" if e["end"] else s


# ---- events.json --------------------------------------------------------
def to_json(e):
    return {
        "id": e["id"], "title": e["title"], "category": e["cat"],
        "date": e["date"].isoformat(), "end_date": e["end_date"].isoformat(),
        "all_day": e["start"] is None, "start": e["start"], "end": e["end"],
        "location": e["loc"], "course": e["course"],
    }


(OUT / "events.json").write_text(json.dumps({
    "school": SCHOOL, "school_year": YEAR, "timezone": TZ,
    "courses": [{"course": c, "teacher": t} for c, t in COURSES.items()],
    "events": [to_json(e) for e in EVENTS],
}, indent=2) + "\n")

# ---- calendar.ics -------------------------------------------------------
def fold(line):
    out, b = [], line.encode()
    while len(b) > 75:
        cut = 75
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode())
        b = b[cut:]
        b = b" " + b
    out.append(b.decode())
    return "\r\n".join(out)


def esc(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def stamp(d, t):
    return d.strftime("%Y%m%d") + "T" + t.replace(":", "") + "00"


lines = [
    "BEGIN:VCALENDAR", "VERSION:2.0",
    "PRODID:-//Open Study Buddy//Cedar Ridge High School//EN",
    "CALSCALE:GREGORIAN", f"X-WR-CALNAME:{SCHOOL} {YEAR}", f"X-WR-TIMEZONE:{TZ}",
    "BEGIN:VTIMEZONE", f"TZID:{TZ}",
    "BEGIN:DAYLIGHT", "TZOFFSETFROM:-0600", "TZOFFSETTO:-0500", "TZNAME:CDT",
    "DTSTART:19700308T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU", "END:DAYLIGHT",
    "BEGIN:STANDARD", "TZOFFSETFROM:-0500", "TZOFFSETTO:-0600", "TZNAME:CST",
    "DTSTART:19701101T020000", "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU", "END:STANDARD",
    "END:VTIMEZONE",
]
for e in EVENTS:
    lines += ["BEGIN:VEVENT", f"UID:{e['id']}@cedar-ridge.open-study-buddy.example",
              "DTSTAMP:20261018T000000Z", f"SUMMARY:{esc(e['title'])}"]
    if e["start"]:
        lines.append(f"DTSTART;TZID={TZ}:{stamp(e['date'], e['start'])}")
        lines.append(f"DTEND;TZID={TZ}:{stamp(e['end_date'], e['end'] or e['start'])}")
    else:
        lines.append(f"DTSTART;VALUE=DATE:{e['date'].strftime('%Y%m%d')}")
        lines.append(f"DTEND;VALUE=DATE:{(e['end_date'] + timedelta(days=1)).strftime('%Y%m%d')}")
    if e["loc"]:
        lines.append(f"LOCATION:{esc(e['loc'])}")
    lines.append(f"CATEGORIES:{CATEGORIES[e['cat']].upper().replace(' ', '_')}")
    lines.append("END:VEVENT")
lines.append("END:VCALENDAR")
(OUT / "calendar.ics").write_bytes(("\r\n".join(fold(l) for l in lines) + "\r\n").encode())

# ---- calendar.md --------------------------------------------------------
BADGE = {"no-school": "🚫", "test": "📝", "due": "📦", "academic": "🎓", "event": "🎉", "sports": "🏈"}


def row(e):
    d = e["date"]
    ds = d.strftime("%a %b ") + str(d.day)
    if e["end_date"] != d:
        ds += "–" + (e["end_date"].strftime("%b ") if e["end_date"].month != d.month else "") + str(e["end_date"].day)
    loc = e["loc"] or ""
    return f"| {ds} | {BADGE[e['cat']]} {e['title']} | {when(e)} | {loc} |"


md = [
    "---",
    f"title: {SCHOOL} Calendar {YEAR}",
    f"description: The synthetic {YEAR} school calendar for {SCHOOL}, used to demo the Open Study Buddy kit.",
    "---",
    f"# {SCHOOL} Calendar, {YEAR}",
    "",
    "This calendar is **synthetic**: every date, class, and teacher is invented for testing the",
    "Open Study Buddy kit. The same events exist in three forms, all generated from one source list",
    "by [`scripts/build-school-calendar.py`](https://github.com/dmccreary/open-study-buddy/blob/main/scripts/build-school-calendar.py):",
    "",
    "| File | Used for |",
    "|------|----------|",
    "| [events.json](events.json) | The hand-edited JSON event file the buddy server reads first |",
    "| [calendar.ics](calendar.ics) | The iCalendar feed the server parses later (time zone `America/Chicago`) |",
    "| this page | A readable copy for students and teachers |",
    "",
    "Titles follow the `TEST:` and `DUE:` convention, so the agent can answer *\"When is my next test?\"*",
    "and *\"What is due this week?\"* by matching the title prefix.",
    "",
    "| Icon | Category |",
    "|------|----------|",
    *[f"| {BADGE[k]} | {v} |" for k, v in CATEGORIES.items()],
    "",
    "## Key Dates",
    "",
    "| Milestone | Date |",
    "|-----------|------|",
    "| First day of school | Tue Aug 25, 2026 |",
    "| End of Quarter 1 | Fri Oct 30, 2026 |",
    "| End of Semester 1 (Quarter 2) | Fri Jan 15, 2027 |",
    "| End of Quarter 3 | Fri Mar 26, 2027 |",
    "| Graduation | Sat May 29, 2027 |",
    "| Last day of school | Thu Jun 3, 2027 |",
    "",
    "## Suggested Demo Date",
    "",
    f"Set the device (or the buddy server's \"today\") to **{DEMO_DATE.strftime('%A, %B ')}{DEMO_DATE.day}, {DEMO_DATE.year}**."
    " The next two weeks then hold a good mix of tests, due dates, and events:",
    "",
    "| Date | Event | Time | Location |",
    "|------|-------|------|----------|",
]
for e in EVENTS:
    if DEMO_DATE <= e["date"] <= DEMO_DATE + timedelta(days=13):
        md.append(row(e))
md.append("")
cur = None
for e in EVENTS:
    key = (e["date"].year, e["date"].month)
    if key != cur:
        cur = key
        md += ["", f"## {e['date'].strftime('%B %Y')}", "",
               "| Date | Event | Time | Location |", "|------|-------|------|----------|"]
    md.append(row(e))
md.append("")
(OUT / "calendar.md").write_text("\n".join(md))

n = {k: sum(e["cat"] == k for e in EVENTS) for k in CATEGORIES}
print(len(EVENTS), "events", n)
