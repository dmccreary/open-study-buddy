#!/usr/bin/env python3
"""Tests for the whole calendar pipeline (Chapter 16). Standard library only.

    python3 test_pipeline.py

Uses the real Cedar Ridge files (events.json and calendar.ics) and a local web
server for the feed tests. Prints one line per check and exits 1 on any failure.
"""
import http.server
import json
import os
import shutil
import tempfile
import threading
import urllib.request
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import agent_config
import alerts
import calendar_source
import compose
import events
import ics_parser
import query
from load_calendar import load_calendar

HERE = os.path.dirname(os.path.abspath(__file__))
CT = ZoneInfo("America/Chicago")
failures = []


def check(name, got, want=True):
    ok = got == want
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        print("       got   :", got)
        print("       wanted:", want)
        failures.append(name)


cfg = agent_config.load(os.path.join(HERE, "agent.toml"))

# --- 1. the two sources agree, event for event --------------------------------
json_cfg = json.loads(json.dumps({k: v for k, v in cfg.items() if k != "_dir"}))
json_cfg["_dir"] = cfg["_dir"]
json_cfg["calendar"]["source"] = "json"
cal_json, _ = load_calendar(json_cfg)
cal_ics, _ = load_calendar(cfg)


def key(e):
    return (e.short_id, e.title, e.category, e.all_day, e.start_date, e.end_date,
            e.start_utc, e.end_utc, e.location, e.course)


check("92 events from each source", (len(cal_json.events), len(cal_ics.events)), (92, 92))
a = sorted(map(key, cal_json.events))
b = sorted(map(key, cal_ics.events))
check("events.json and calendar.ics give identical events", a == b)
check("no parser warnings on the real feed", cal_ics.warnings, [])
test_event = next(e for e in cal_ics.events if e.short_id == "crhs-018")
check("crhs-018 is TEST: Algebra II Unit 3 on 2026-10-20 at 13:00 UTC",
      (test_event.title, test_event.start_utc.isoformat()),
      ("TEST: Algebra II Unit 3 - Quadratics", "2026-10-20T13:00:00+00:00"))
check("its course is Algebra II", test_event.course, "Algebra II")

# --- 2. parser details -----------------------------------------------------------
SNIPPET = "\r\n".join([
    "BEGIN:VCALENDAR", "BEGIN:VTIMEZONE", "TZID:America/Chicago", "BEGIN:STANDARD",
    "DTSTART:19701101T020000", "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU", "END:STANDARD", "END:VTIMEZONE",
    "BEGIN:VEVENT", "UID:a@x", "SUMMARY:Football vs. Eastbrook\\, the Eagles\\; at home",
    "DTSTART;TZID=\"America/Chicago\":20261023T190000", "DTEND;TZID=America/Chicago:20261023T210000",
    "LOCATION:Griffin Field", "END:VEVENT",
    "BEGIN:VEVENT", "UID:folded@x", "SUMMARY:A very long title that the calendar program had to fold onto a",
    " second line because it passed seventy-five characters", "DTSTART;VALUE=DATE:20261101", "END:VEVENT",
    "BEGIN:VEVENT", "UID:allday@x", "SUMMARY:No school", "DTSTART;VALUE=DATE:20261125", "DTEND;VALUE=DATE:20261128", "END:VEVENT",
    "BEGIN:VEVENT", "UID:utc@x", "SUMMARY:TEST: Biology", "DTSTART:20261110T160200Z", "END:VEVENT",
    "BEGIN:VEVENT", "UID:float@x", "SUMMARY:Floating", "DTSTART:20261110T080000", "END:VEVENT",
    "BEGIN:VEVENT", "UID:ny@x", "SUMMARY:Webinar", "DTSTART;TZID=America/New_York:20261110T090000", "END:VEVENT",
    "BEGIN:VEVENT", "UID:weekly@x", "SUMMARY:Weekly club", "DTSTART;TZID=America/Chicago:20261110T150000",
    "RRULE:FREQ=WEEKLY;COUNT=10", "END:VEVENT",
    "BEGIN:VEVENT", "UID:cancelled@x", "SUMMARY:DUE: Biology lab", "DTSTART;VALUE=DATE:20261112", "STATUS:CANCELLED", "END:VEVENT",
    "BEGIN:VEVENT", "UID:winzone@x", "SUMMARY:Outlook zone", "DTSTART;TZID=Central Standard Time:20261110T090000", "END:VEVENT",
    "BEGIN:VEVENT", "UID:nostart@x", "SUMMARY:No start", "END:VEVENT",
    "END:VCALENDAR", ""])
res = ics_parser.parse_ics(SNIPPET, CT, ["Biology"])
by = {e.uid: e for e in res.events}
check("VTIMEZONE's DTSTART is not an event; cancelled/unknown-zone/no-start are dropped",
      sorted(by), ["a@x", "allday@x", "float@x", "folded@x", "ny@x", "utc@x", "weekly@x"])
check("escaped comma and semicolon are unescaped", by["a@x"].title, "Football vs. Eastbrook, the Eagles; at home")
check("quoted TZID works: 7 PM CDT is 00:00 UTC next day", by["a@x"].start_utc.isoformat(), "2026-10-24T00:00:00+00:00")
check("folded line is joined without the fold space",
      by["folded@x"].title, "A very long title that the calendar program had to fold onto a" "second line because it passed seventy-five characters")
check("all-day DTEND is exclusive: Nov 25-27", (by["allday@x"].start_date, by["allday@x"].end_date, by["allday@x"].all_day),
      (date(2026, 11, 25), date(2026, 11, 27), True))
check("all-day with no DTEND is one day", (by["folded@x"].start_date, by["folded@x"].end_date), (date(2026, 11, 1), date(2026, 11, 1)))
check("Z time is UTC and shows as 10:02 AM CST", by["utc@x"].local_start(CT).strftime("%H:%M %Z"), "10:02 CST")
check("TEST: prefix gives category test and course Biology", (by["utc@x"].category, by["utc@x"].course), ("test", "Biology"))
check("floating time is read as school-local (8:00 CST = 14:00 UTC)", by["float@x"].start_utc.hour, 14)
check("another zone is converted (9:00 EST = 14:00 UTC)", by["ny@x"].start_utc.hour, 14)
check("RRULE event is kept once and flagged", (by["weekly@x"].recurring, len([w for w in res.warnings if "recurrence" in w])), (True, 1))
check("warnings name the unknown zone and the missing start",
      sorted(w.split(":")[0] for w in res.warnings if "time zone" in w or "DTSTART" in w), ["No start", "Outlook zone"])
check("LF-only line endings parse the same", len(ics_parser.parse_ics(SNIPPET.replace("\r\n", "\n"), CT, []).events), len(res.events))
check("parse_line keeps a colon inside quotes",
      ics_parser.parse_line('X;NAME="a:b";TZID=Z:value:with:colons'), ("X", {"NAME": "a:b", "TZID": "Z"}, "value:with:colons"))

# --- 3. time zones and daylight saving ----------------------------------------------
check("8:00 AM on Oct 20 (CDT) is 13:00 UTC", events.make_local(date(2026, 10, 20), "08:00", CT).hour, 13)
check("8:00 AM on Dec 1 (CST) is 14:00 UTC", events.make_local(date(2026, 12, 1), "08:00", CT).hour, 14)
gap = events.make_local(date(2027, 3, 14), "02:30", CT)
check("2:30 AM on 2027-03-14 does not exist; it becomes 08:30 UTC = 3:30 AM CDT",
      (gap.isoformat(), gap.astimezone(CT).strftime("%H:%M %Z")), ("2027-03-14T08:30:00+00:00", "03:30 CDT"))
dup = events.make_local(date(2026, 11, 1), "01:30", CT)
check("1:30 AM on 2026-11-01 happens twice; we take the first (CDT) = 06:30 UTC",
      (dup.isoformat(), dup.astimezone(CT).strftime("%H:%M %Z")), ("2026-11-01T06:30:00+00:00", "01:30 CDT"))
day_after = events.make_local(date(2026, 11, 2), "08:00", CT)
check("8:00 AM the Monday after the change is 14:00 UTC (CST)", day_after.hour, 14)
check("the day of the change is 25 hours long",
      (datetime(2026, 11, 2, tzinfo=CT).astimezone(events.UTC) - datetime(2026, 11, 1, tzinfo=CT).astimezone(events.UTC)),
      timedelta(hours=25))
holiday = next(e for e in cal_ics.events if e.title == "NO SCHOOL: Labor Day")
other = ics_parser.parse_ics("BEGIN:VEVENT\r\nUID:h\r\nSUMMARY:H\r\nDTSTART;VALUE=DATE:20260907\r\nEND:VEVENT\r\n",
                             ZoneInfo("Pacific/Auckland")).events[0]
check("an all-day date is the same date in any school zone", (holiday.start_date, other.start_date), (date(2026, 9, 7), date(2026, 9, 7)))

# --- 4. queries (demo morning: Monday 2026-10-19) ------------------------------------
now = datetime(2026, 10, 19, 9, 0, tzinfo=CT)
nt = query.next_of(cal_ics, now, "test")
check("next test is Algebra II Unit 3, tomorrow", (nt.short_id, nt.start_date), ("crhs-018", date(2026, 10, 20)))
check("next Biology test is Unit 2 on Nov 10", query.next_of(cal_ics, now, "test", "Biology").start_date, date(2026, 11, 10))
due = query.upcoming(cal_ics, now, days=7, categories=("due",))
check("due this week: English draft, Biology lab report", [e.start_date.day for e in due], [21, 22])
check("a test is upcoming at 07:59 and not at 08:05 on its day",
      (query.is_upcoming(nt, datetime(2026, 10, 20, 7, 59, tzinfo=CT)), query.is_upcoming(nt, datetime(2026, 10, 20, 8, 5, tzinfo=CT))),
      (True, False))
check("Oct 15-16 is fall break, not a school day", (query.is_school_day(cal_ics, date(2026, 10, 15)), query.is_school_day(cal_ics, date(2026, 10, 19))), (False, True))
check("Saturday is not a school day; the next school day after Thu Oct 15 is Mon Oct 19",
      (query.is_school_day(cal_ics, date(2026, 10, 17)), query.next_school_day(cal_ics, date(2026, 10, 15))), (False, date(2026, 10, 19)))
check("an ongoing multi-day event is upcoming mid-way (Homecoming Week on Sep 16)",
      any(e.title == "Homecoming Week" for e in query.upcoming(cal_ics, datetime(2026, 9, 16, 9, 0, tzinfo=CT), days=1)))
check("a new server in UTC still says 'today' by the school's date",
      datetime(2026, 10, 20, 2, 30, tzinfo=events.UTC).astimezone(CT).date(), date(2026, 10, 19))

# --- 5. answers, briefing, reminders --------------------------------------------------------
def ask(text, when=now):
    return compose.answer(text, cal_ics, when, cfg)


check("answer: next test", ask("When is my next test?")["speak"],
      "Your next test is Algebra II Unit 3, Quadratics, tomorrow at 8 AM.")
check("answer: due this week", ask("What is due this week?")["speak"],
      "English 10 personal narrative draft is due on Wednesday. Biology osmosis lab report is due on Thursday.")
check("answer: school on Friday", ask("Is there school on Friday?")["speak"],
      "Yes, there is school on Friday. Football versus Eastbrook Eagles is on Friday at 7 PM. Location: Griffin Field.")
check("answer: no school on a holiday", ask("is there school on thursday", datetime(2026, 10, 12, 9, tzinfo=CT))["speak"],
      "No, there is no school on Thursday: Fall Break.")
check("answer: end of quarter", ask("When does the quarter end?")["speak"], "End of Quarter 1 is on Friday, October 30.")
check("answer: tonight has nothing on Monday", ask("What's happening tonight?")["speak"], "Nothing is on the calendar tonight.")
check("answer: a question it was not built for gets an apology", ask("Do I have anything big coming up this week?")["speak"].startswith("Sorry"))
check("answer: Biology test by course name", ask("when is my biology test")["speak"], "Your next test is Biology Unit 2, Genetics, on Tuesday, November 10 at 10:02 AM.")
check("every reply has the Chapter 1 shape and a 30-character show line",
      all(set(ask(q)) == {"speak", "show", "next_mode"} and len(ask(q)["show"]) <= 30
          for q in ("next test", "what is due", "school tomorrow", "what is happening today", "hello")))

brief = compose.daily_briefing(cal_ics, now, cfg)
check("briefing for the demo morning", brief["speak"],
      "Good morning from Cedar Ridge. Picture Retake Day is today. Location: Library. "
      "Your next Algebra II test is tomorrow at 8 AM. English 10 personal narrative draft is due on Wednesday. "
      "Biology osmosis lab report is due on Thursday. Griffins aim high!")
check("no briefing on a no-school day", compose.daily_briefing(cal_ics, datetime(2026, 10, 15, 7, 30, tzinfo=CT), cfg), None)
check("no briefing on a Sunday", compose.daily_briefing(cal_ics, datetime(2026, 10, 18, 7, 30, tzinfo=CT), cfg), None)
check("the briefing fits an alert: whole sentences within 300 characters",
      len(compose.fit_sentences(brief["sentences"], alerts.MAX_TEXT_BRIEFING)) <= 300)

rem = compose.reminders(cal_ics, now, cfg)
check("reminders on Oct 19: the Algebra II test, to room 118",
      [(r, a["id"], a["type"]) for r, a in rem], [(("room", "118"), "20261019-crhs-018-d1", "test")])
check("run twice, same ids", [a["id"] for _, a in compose.reminders(cal_ics, now, cfg)], [a["id"] for _, a in rem])
week_ahead = compose.reminders(cal_ics, datetime(2026, 10, 13, 7, 30, tzinfo=CT), cfg)
check("Oct 13: a week-ahead reminder for the Oct 20 test", [(a["id"], a["when"]) for _, a in week_ahead],
      [("20261013-crhs-018-d7", "Tue Oct 20 8:00 AM")])
all_alerts = []
day = date(2026, 8, 25)
while day <= date(2027, 6, 3):
    all_alerts += [a for _, a in compose.reminders(cal_ics, datetime.combine(day, datetime.min.time(), tzinfo=CT), cfg)]
    day += timedelta(days=1)
check("every reminder of the school year is a valid alert", [alerts.problems(a) for a in all_alerts], [[]] * len(all_alerts))
check("the year produces 31 tests x (d7, d1) + 19 due + 9 no-school = 90 reminders, none lost to a break",
      len(all_alerts), 31 * 2 + 19 + 9)
check("the Biology test on Tue Nov 10: its week-ahead reminder falls on election day (no school), so it is sent Mon Nov 2",
      [a["id"] for a in all_alerts if a["id"].endswith("crhs-029-d7")], ["20261102-crhs-029-d7"])
check("no two reminders in the year share an id", len({a["id"] for a in all_alerts}), len(all_alerts))
check("the longest encoded reminder fits the 512-byte limit",
      max(len(alerts.encode_alert(a).encode()) for a in all_alerts) <= alerts.MAX_PAYLOAD)

# --- 6. configuration checks -----------------------------------------------------------------
errors, warnings = agent_config.check(cfg)
check("the shipped agent.toml has no errors", errors, [])


def broken(**sections):
    c = json.loads(json.dumps({k: v for k, v in cfg.items()}))
    for dotted, value in sections.items():
        a, b = dotted.split("__")
        c[a][b] = value
    return agent_config.check(c)


check("bad timezone is an error", any("IANA" in e for e in broken(school__timezone="CST")[0]))
check("bad school id is an error", any("lowercase" in e for e in broken(school__id="Cedar Ridge")[0]))
check("missing calendar file is an error", any("does not exist" in e for e in broken(calendar__ics_path="nope.ics")[0]))
check("unknown placeholder is an error", any("{nmae}" in e for e in broken(voice__greeting="Hi {nmae}")[0]))
check("a 20-word sentence earns a warning",
      any("over 15 words" in w for w in broken(voice__greeting="Good morning from {school} and welcome to another wonderful day of learning and growing together here")[1]))
check("short wake phrase earns a warning", any("syllable" in w for w in broken(wake__phrase="Go")[1]))
check("non-default wake phrase says to re-enroll", any("enroll" in w for w in broken(wake__phrase="Hey Gale the Griffin")[1]))
check("poll under 15 minutes earns a warning", any("impolite" in w for w in broken(calendar__poll_minutes=1)[1]))
check("wrong mascot size is an error", any("needs" in e for e in broken(mascot__size=100)[0]), True)
check("a negative reminder lead is an error", any("reminders" in e for e in broken(reminders__test_days_before=[-1])[0]))
bad_json = {"school": "S", "timezone": "America/Chicago", "events": [{"id": "1", "title": "t", "date": "10/20/2026"}, {"id": "1", "title": "u", "date": "2026-10-20", "category": "party"}]}
check("events.json checker: bad date, duplicate id, unknown category",
      [p.split(": ", 1)[1][:16] for p in calendar_source.json_problems(bad_json)],
      ["date must look l", "duplicate id '1'", "category 'party'"])

# --- 7. polite feed polling against a local web server ------------------------------------------
with open(os.path.join(HERE, cfg["calendar"]["ics_path"]), "rb") as f:
    FEED = f.read()
hits = {"get": 0, "304": 0}


class FeedHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        hits["get"] += 1
        if self.headers.get("If-None-Match") == '"v1"':
            hits["304"] += 1
            self.send_response(304)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("ETag", '"v1"')
        self.send_header("Content-Length", str(len(FEED)))
        self.end_headers()
        self.wfile.write(FEED)


server = http.server.HTTPServer(("127.0.0.1", 0), FeedHandler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = "http://127.0.0.1:%d/calendar.ics" % server.server_port
tmp = tempfile.mkdtemp()
fake_time = [1000.0]
feed = calendar_source.FeedCache(url, os.path.join(tmp, "feed.ics"), min_interval_s=3600, clock=lambda: fake_time[0])
text, status = feed.text()
check("first poll fetches (200)", (status, len(text) > 1000, hits["get"]), ("fetched", True, 1))
text, status = feed.text()
fake_time[0] += 600
text, status = feed.text()
check("polls inside the interval make no request", (status, hits["get"]), ("recent", 1))
fake_time[0] += 3600
text, status = feed.text()
check("after the interval the ETag gets a 304 and the saved copy is used", (status, hits["304"], hits["get"], len(text) > 1000),
      ("not-modified", 1, 2, True))
check("the downloaded feed parses to the same 92 events",
      len(calendar_source.from_ics(text, "S", "America/Chicago", cfg["courses"] and [{"course": c["name"]} for c in cfg["courses"]]).events), 92)
server.shutdown()
server.server_close()
fake_time[0] += 7200
text, status = feed.text()
check("with the feed down, the saved copy is used ('stale')", (status, len(text) > 1000), ("stale", True))
fake_time[0] += 10
text, status = feed.text()
check("and it does not hammer the dead feed", status, "recent")
gone = calendar_source.FeedCache("http://127.0.0.1:1/none.ics", os.path.join(tmp, "none.ics"), clock=lambda: 0)
try:
    gone.text()
    check("no copy and no feed raises OSError", False)
except OSError:
    check("no copy and no feed raises OSError", True)
shutil.rmtree(tmp)

# --- 8. the minimal HTTP server --------------------------------------------------------------------
import buddy_server_min
from http.server import ThreadingHTTPServer

handler = buddy_server_min.make_handler(cfg, datetime(2026, 10, 19, 9, 0), ["old-token", "s3cret"])
srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = "http://127.0.0.1:%d" % srv.server_port


def post(body, token="s3cret"):
    req = urllib.request.Request(base + "/v1/ask", data=json.dumps(body).encode(), method="POST",
                                 headers={"X-Buddy-Token": token} if token else {})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


check("POST /v1/ask with a token from the list returns Chapter 1's reply",
      post({"device": "desk-07", "kind": "question", "text": "when is my next test"}),
      (200, {"speak": "Your next test is Algebra II Unit 3, Quadratics, tomorrow at 8 AM.",
             "show": "Algebra II test: tomorrow 8 AM", "next_mode": "clock"}))
check("no token is refused (401)", post({"text": "x"}, token=None)[0], 401)
check("wrong token is refused (401)", post({"text": "x"}, token="nope")[0], 401)
check("body without text is refused (400)", post({"device": "d"})[0], 400)
srv.shutdown()
srv.server_close()

print()
print("FAILED: %d" % len(failures) if failures else "PASS: all pipeline checks")
raise SystemExit(1 if failures else 0)
