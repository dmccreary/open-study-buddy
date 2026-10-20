---
title: "Configuring the School Agent and Calendar"
description: "How to configure the buddy server for one school: an agent.toml file, events from a JSON file and an iCalendar feed parsed on the server, TEST and DUE title conventions, time zones, upcoming-event queries, daily briefings and reminders, voice and tone, the school mascot on the round display, and a custom wake phrase."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 13:26:12"
version: 1.11
---

# Configuring the School Agent and Calendar

## Summary

This chapter configures the agent behind the device for a school. Students read events from a JSON file and then an iCalendar feed parsed on the server, use TEST and DUE title conventions, and build daily briefings and reminders. They also personalize the voice, tone, mascot, and wake phrase for their own school.

## Concepts Covered

This chapter covers the following 24 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Agent Configuration File | 2 |
| School Calendar | 33 |
| iCalendar Format | 18 |
| Events JSON File | 13 |
| Course Information | 1 |
| ICS Feed | 4 |
| Event Parsing | 12 |
| Event Categories | 1 |
| Voice and Prompts | 2 |
| OAuth | 2 |
| TEST and DUE Prefixes | 3 |
| Time Zones | 1 |
| Upcoming Events Query | 5 |
| Calendar Polling | 1 |
| Server-Side Parsing | 1 |
| Language and Tone | 1 |
| Google Calendar API | 1 |
| Test Date Detection | 1 |
| Project Due Date | 1 |
| Daily Briefing | 3 |
| Reminder | 2 |
| Per-School Customization | 1 |
| School Mascot Design | 1 |
| Custom Wake Phrase | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../01-personal-agents-architecture/index.md)
- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 5: Display Basics: Pixels, Color, and Frame Size](../05-display-basics/index.md)
- [Chapter 6: Drawing Directly to Display Regions](../06-display-regions-and-drawing/index.md)
- [Chapter 8: I2S Audio: Recording and Playing Sound](../08-i2s-audio/index.md)
- [Chapter 12: Wake-Word Detection](../12-wake-word-detection/index.md)
- [Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../13-wifi-http-agent-link/index.md)
- [Chapter 14: Streaming Speech, Security, and Network Resilience](../14-streaming-security-resilience/index.md)
- [Chapter 15: MQTT and Push Alerts](../15-mqtt-push-alerts/index.md)

---

## A Buddy That Knows Your School

The first fifteen chapters built a device that listens, shows, speaks, and receives pushed alerts. It still knows nothing about *your* school: which tests are coming, when the next holiday is, what the mascot looks like, or how the school likes to talk. This chapter gives the buddy server that knowledge. Along the way you will read a calendar two ways (a hand-edited JSON file and a standard calendar feed), turn titles like `TEST: Algebra II` into spoken reminders, compose a morning briefing, and dress the device in the school's name and mascot.

Our worked example is [Cedar Ridge High School](../../schools/cedar-ridge-high-school/index.md), a synthetic school invented for demos, with [Gale the Griffin](../../schools/cedar-ridge-high-school/mascot.md) as its mascot and its real 2026-2027 calendar of 92 events. Everything here runs on those real files, and the code you will read is in `src/chapters/16-school-agent-calendar/`.

!!! mascot-welcome "Make It Yours"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter your device will greet students by your school's name, show your mascot, and announce your tests and due dates, all from one file you can edit. You will build the whole pipeline on your computer first, with real output at every step. Let's listen closely!

## One File Configures the School

An **agent configuration file** is a single file that holds every choice that makes one school's agent different from another's. This book uses `agent.toml`, written in TOML, a plain-text format with `[sections]`, `key = value` lines, and comments that start with `#`. TOML suits a file that people edit by hand because, unlike JSON, it allows comments and does not need quotes around every name. Python 3.11 and newer read it with the standard library module `tomllib`, so the server needs nothing to install.

**Per-school customization** means that making a Study Buddy for a different school changes this file and nothing in the code. Here is the shape of Cedar Ridge's file, shortened. The sections, not the values, are the point.

```toml
schema = 1

[school]
name = "Cedar Ridge High School"
short_name = "Cedar Ridge"
id = "crhs"
slogan = "Aim high. Listen closely."
timezone = "America/Chicago"

[calendar]
source = "ics"                  # "json" or "ics"
poll_minutes = 60

[[courses]]
name = "Algebra II"
teacher = "Ms. Okafor"
room = "118"

[features]
briefing = true
test_alerts = true

[reminders]
test_days_before = [7, 1]       # a week ahead and the day before

[voice]
greeting = "Good morning from {school}."
mascot_flavor = true

[mascot]
name = "Gale"
file = "griffin.rgb565"
size = 240

[wake]
phrase = "Hey Pico"
```

| Section | Decides |
|---------|---------|
| `[school]` | The name, the id used in every MQTT topic, the slogan, and the time zone |
| `[calendar]` | Where events come from (JSON file, ICS file, or ICS web address) and how often to check |
| `[[courses]]` | One block per course, with teacher and the room that receives its reminders |
| `[features]` | Which things the agent does: answers, briefing, test alerts, due alerts, no-school notices |
| `[briefing]`, `[reminders]` | When and how far ahead to announce |
| `[voice]` | Greeting, reminder wording, mascot lines, the instruction for an LLM brain, and speech replacements |
| `[mascot]`, `[wake]` | The picture file and size, and the wake phrase |

A configuration file is only trustworthy if it is checked, because a typo in it fails at 7:30 on a school morning. `check_config.py` loads the file, validates each section, and then loads the calendar it names. Each message is plain English. Here it is on the real file, and then on a copy with a wrong time zone name, a misspelled `{schol}` placeholder in the greeting, and a 5-minute polling interval.

```text
$ python3 check_config.py
Calendar: .../docs/schools/cedar-ridge-high-school/calendar.ics, 92 events (file)
  academic 11, due 19, event 20, no-school 9, sports 2, test 31
0 error(s), 0 warning(s)

$ python3 check_config.py broken.toml
ERROR  : [school] timezone 'CST' is not an IANA name such as America/Chicago
ERROR  : [voice] greeting uses unknown placeholder(s) {schol}; allowed: {mascot}, {school}, {sentence}
warning: [calendar] poll_minutes is 5: feeds change a few times a day, so under 15 is impolite
2 error(s), 1 warning(s)
```

The rest of the chapter explains what each section does, in the order the data flows.

## The School Calendar

A **school calendar** is the list of dated things a school wants its students to know: tests, project due dates, holidays, game nights, report-card days. A calendar is usually kept by the office in a program like Google Calendar or a school information system, and the agent has to read it from there, because a second hand-typed copy goes stale.

Every item is an *event*, and each event needs four facts: a title, a date, optionally a time, and a **category**. **Event categories** group events by what the agent should do with them. This book uses six: `test`, `due`, `no-school`, `academic` (milestones such as "End of Quarter 1"), `event` (concerts, picture day), and `sports`.

The categories come from a title convention. **TEST and DUE prefixes** are the rule that a title beginning `TEST:` is a test, one beginning `DUE:` is a project or assignment due date, and one beginning `NO SCHOOL:` is a day off. The convention is deliberately low-tech: any teacher who can type a title in any calendar program can follow it, with no special field to find. The code in `events.py` matches the prefix without caring about capitals or spacing, so `test : algebra` works too, and the prefix wins over any category the calendar program attached. Two reasons: teachers type titles, and different programs name their categories differently.

**Test date detection** and **project due date** detection are then just that rule applied: the next test is the earliest upcoming event whose category is `test`, and the due dates are the events whose category is `due`. Nothing is guessed from the words "exam" or "quiz" in a title.

**Course information** (a course's name and its teacher) comes after the prefix. In `TEST: Algebra II Unit 3 - Quadratics` the course is `Algebra II` and the topic is `Unit 3 - Quadratics`. The server matches the longest course name from the `[[courses]]` list at the start of the rest of the title, so the agent can say "Your Algebra II test" and answer "when is my biology test?". A title that names no listed course still works; it just has no course.

*Worked example.* This is what the code makes of two real Cedar Ridge titles:

| Title | Category | Course | Rest of the title |
|-------|----------|--------|-------------------|
| `TEST: Algebra II Unit 3 - Quadratics` | test | Algebra II | `Unit 3 - Quadratics` |
| `DUE: Biology osmosis lab report` | due | Biology | `osmosis lab report` |
| `NO SCHOOL: Labor Day` | no-school | none | `Labor Day` |
| `Picture Retake Day` | event | none | the whole title |

Real calendars reach the server in two forms, and the book builds both, in this order. The first is the easiest to understand and the second is the one a school will really have.

## Step One: A Hand-Edited events.json

An **events JSON file** is a calendar written by hand as a JSON list. You have used JSON since Chapter 13. A file like this needs no other program and can be edited in any text editor, which makes it the right first source: you can read every character of it. Cedar Ridge's file, `events.json`, has a header and then 92 events. Here is one, with its fields explained after it:

```json
{
  "id": "crhs-018",
  "title": "TEST: Algebra II Unit 3 - Quadratics",
  "category": "test",
  "date": "2026-10-20",
  "end_date": "2026-10-20",
  "all_day": false,
  "start": "08:00",
  "end": null,
  "location": null,
  "course": "Algebra II"
}
```

| Field | Meaning |
|-------|---------|
| `id` | Unique within the file. It also becomes part of the alert id (Chapter 15). |
| `title` | The full title, prefix included. |
| `category` | One of the six categories; if left out, it comes from the prefix. |
| `date`, `end_date` | `YYYY-MM-DD`; `end_date` is the last day, inclusive, so a one-day event repeats the date. |
| `all_day` | `true` for holidays and due dates, which have no time. |
| `start`, `end` | `"HH:MM"` school-local time, 24-hour; only for events that are not all-day. |
| `location`, `course` | Optional. |

The header carries `school`, `timezone` (an IANA name like `America/Chicago`), and the `courses` list. Because a hand-edited file will contain mistakes, `calendar_source.json_problems()` checks it and reports each one in words: a missing `title`, a date that does not look like `2026-10-20`, an `end_date` before the `date`, a duplicate `id`, a category that is not one of the six. The pipeline test feeds it a file with a bad date, a repeated id, and a category `party`, and gets back exactly those three complaints.

The weakness of a hand-edited file is that it is a second copy of the calendar. Every change the office makes in its real calendar must be repeated here by someone, and eventually someone forgets. That leads to the second source.

## Step Two: An iCalendar Feed, Parsed on the Server

The **iCalendar format**, also called ICS after its `.ics` file extension and defined by RFC 5545, is the standard text format that calendar programs use to exchange events. Google Calendar, Apple Calendar, Outlook, and most school systems can export one. An **ICS feed** is an iCalendar file published at a web address, which a program can fetch again and again to stay current. The office edits its calendar as usual, and the feed changes by itself.

**Server-side parsing** is the rule that this reading happens on the buddy server and never on the Pico. Parsing an ICS file means unfolding lines, handling time zones, and following dozens of special cases. That is hundreds of lines of code and a lot of RAM, which the Pico should spend on the microphone. The server does it once for all devices, and what reaches a desk is the short alert from Chapter 15 or a one-sentence reply.

An ICS file is lines of text. Each line is a *property*: a name, optional parameters after semicolons, a colon, and a value. Properties are grouped between `BEGIN:` and `END:` lines into components. Here is the real Cedar Ridge feed for the algebra test, and for the first lines of the file:

```text
BEGIN:VCALENDAR
VERSION:2.0
X-WR-TIMEZONE:America/Chicago
BEGIN:VTIMEZONE
TZID:America/Chicago
BEGIN:DAYLIGHT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
...
END:VTIMEZONE
BEGIN:VEVENT
UID:crhs-018@cedar-ridge.open-study-buddy.example
DTSTAMP:20261018T000000Z
SUMMARY:TEST: Algebra II Unit 3 - Quadratics
DTSTART;TZID=America/Chicago:20261020T080000
DTEND;TZID=America/Chicago:20261020T080000
CATEGORIES:TEST
END:VEVENT
```

| Property | Meaning |
|----------|---------|
| `VEVENT` | One event. Everything else in this table lives inside one. |
| `UID` | A unique id for the event, stable across edits |
| `DTSTAMP` | When this version of the event was written, in UTC |
| `SUMMARY` | The title |
| `DTSTART`, `DTEND` | When it starts and ends |
| `LOCATION`, `CATEGORIES` | Where, and the program's own categories |
| `VTIMEZONE` | A definition of a time zone's rules. Notice it contains a `DTSTART` that is *not* an event. |

Five details make an ICS parser harder than splitting lines on colons, and the book's `ics_parser.py` handles each:

1. **Line folding.** A line longer than 75 bytes is split, and the continuation starts with a space or tab. The reader must join them first, and drop that one space.
2. **Escapes.** A comma, semicolon, or backslash inside text is written `\,`, `\;`, `\\`, and a newline `\n`.
3. **Parameters.** `DTSTART;TZID=America/Chicago:2026...` has a parameter before the colon, and a quoted parameter value may itself contain a colon.
4. **Two kinds of date.** `DTSTART;VALUE=DATE:20261125` is an *all-day* event, a date with no time. A value with a time may end in `Z` (UTC), carry a `TZID`, or have neither (a "floating" time, read as the school's local time). For all-day events, `DTEND` is the day *after* the last day, so Nov 25 to Nov 28 means Nov 25, 26, 27.
5. **Nested components.** The `DTSTART` inside `VTIMEZONE` must not become an event.

Doing all five and then building the result is **event parsing**: turning the lines of one `VEVENT` into a single `Event` with a title, a category, a course, dates, and, for timed events, UTC start and end times. The reader is about 180 lines of standard-library Python, and it is honest about its limits. It does not expand **recurrence rules** (`RRULE`, such as "every Tuesday for 10 weeks"): it keeps the event once, marks it recurring, and adds a warning. It does not read the time-zone definitions inside `VTIMEZONE`, trusting the IANA name in `TZID` instead, so a feed that uses a name like `Central Standard Time` (common from Outlook) has those events skipped with a warning. It ignores `DURATION`. These are the cases where you should stop writing your own parser and install the `icalendar` package together with `recurring-ical-events`, which expands repeats correctly. For a school calendar built from one-off dates, like Cedar Ridge's, the small reader is enough, and it is short enough for a student to read and check.

*Worked example.* Does the parser agree with the JSON file? Both files came from the same source list, so the test is exact: parse each, and compare every field of every event.

```text
ok   92 events from each source
ok   events.json and calendar.ics give identical events
ok   no parser warnings on the real feed
ok   crhs-018 is TEST: Algebra II Unit 3 on 2026-10-20 at 13:00 UTC
```

Two completely different readers produced identical events: the same ids, titles, categories, dates, UTC times, locations, and courses for all 92. That is the strongest evidence the book can offer that the parser is right *for this feed*. It is not evidence about feeds from other programs, which is why `check_config.py` prints the parser's warnings every time.

Step through the parser yourself on a small feed before you trust it.

#### Diagram: ICS Line Parser Stepper

<details markdown="1">
<summary>ICS Line Parser Stepper</summary>
Type: microsim
**sim-id:** ics-line-parser-stepper<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** execute<br/>
**Learning Objective:** The learner will execute the iCalendar parsing rules on the 14 lines of a small feed by choosing what the parser does with each line, with at least 12 of the 14 choices correct.

**Prerequisites:** property, parameter, VEVENT, VTIMEZONE, line folding, all-day date, exclusive end date, UTC, TZID (all defined in the section "Step Two: An iCalendar Feed, Parsed on the Server" above this block).

**Evidence of Mastery:** For each of the 14 lines, in order, the learner chooses one action from the Actions list, then submits. A choice is correct when it equals the Answer column. Mastery is 12 of 14 correct on the first submission of each line. Stepping through the finished parse in exploration is not evidence.

**Misconceptions:** (1) The DTSTART inside a VTIMEZONE is an event. (2) A line that starts with a space is a new property. (3) The end date of an all-day event is its last day. (4) A time with a TZID is already in UTC.

**Instructional Rationale:** Executing a procedure means following its rules on concrete input. The learner commits each line's action before the parser state is revealed, so a wrong rule shows as a wrong action, and the running state of the parse (inside a time zone or not, the event being built) shows why.

**Content:**

The Actions, always shown:

| Id | Action |
|----|--------|
| A | Start skipping a time-zone definition |
| B | Skip: it is inside a time-zone definition |
| C | Stop skipping |
| D | Start a new event |
| E | Set the title |
| F | Join onto the line before it (a fold) |
| G | Set a timed start, converted to UTC |
| H | Set an all-day first day |
| I | Set the last day (the end date minus one day) |
| J | Set the location |
| K | Finish the event |

The 14 lines, in order. A line that begins with a space is shown with a visible space marker ("␣").

| # | Line | Answer | Why (shown as feedback) |
|---|------|--------|-------------------------|
| 1 | `BEGIN:VTIMEZONE` | A | Everything until the matching END belongs to a time-zone definition. |
| 2 | `DTSTART:19701101T020000` | B | This DTSTART describes a rule of the zone, not an event, so it is skipped. |
| 3 | `END:VTIMEZONE` | C | The zone definition is over; events count again. |
| 4 | `BEGIN:VEVENT` | D | A new event starts with empty fields. |
| 5 | `SUMMARY:TEST: Biology Unit 2 - Gene` | E | The title so far is "TEST: Biology Unit 2 - Gene". The second colon belongs to the value. |
| 6 | `␣tics` | F | A line that starts with a space continues the line before it, and that one space is dropped, even in the middle of a word. The title becomes "TEST: Biology Unit 2 - Genetics". |
| 7 | `DTSTART;TZID=America/Chicago:20261110T100200` | G | 10:02 in Chicago on Nov 10 is CST, UTC minus 6 hours, so 16:02 UTC. |
| 8 | `LOCATION:Lab 130` | J | Plain text property. |
| 9 | `END:VEVENT` | K | The event is complete. Its title begins "TEST:", so its category is test, and its course is Biology. |
| 10 | `BEGIN:VEVENT` | D | A second event starts. |
| 11 | `SUMMARY:NO SCHOOL: Thanksgiving Break` | E | The prefix "NO SCHOOL:" will make its category no-school. |
| 12 | `DTSTART;VALUE=DATE:20261125` | H | VALUE=DATE means all-day: the date is Nov 25 with no time and no time zone. |
| 13 | `DTEND;VALUE=DATE:20261128` | I | The end date is exclusive, so the last day is Nov 27. |
| 14 | `END:VEVENT` | K | The event is complete: Nov 25 to Nov 27. |

After line 14 the sim shows the two finished events: "TEST: Biology Unit 2 - Genetics", category test, course Biology, 2026-11-10 16:02 UTC, location Lab 130; and "NO SCHOOL: Thanksgiving Break", category no-school, all-day, 2026-11-25 to 2026-11-27.

**Provenance:** The line forms come from the real Cedar Ridge feed (`docs/schools/cedar-ridge-high-school/calendar.ics`) and from the parser rules in `src/chapters/16-school-agent-calendar/server/ics_parser.py`. The title of the Biology test is adapted by hand to include a fold. The sim labels the feed "adapted from the Cedar Ridge feed."

**Rules:** Lines are processed in order. While inside a VTIMEZONE (between A and C), every property is skipped. A line that starts with a space or tab is joined to the previous line with its first character removed, before any other rule applies. A DTSTART with a TZID is a local time in that zone and is converted to UTC. A DTSTART with VALUE=DATE is an all-day date and is not converted. A DTEND with VALUE=DATE gives the last day as the date minus one day. A title starting TEST: has category test, DUE: has category due, NO SCHOOL: has category no-school.

**Learner Activity:**

1. The learner reads the Actions list and the feed, then steps through a finished example parse once, seeing the state after each line.
2. The learner starts the 14 lines. Line 1 is highlighted, with the parser state ("outside any event, not in a zone") shown.
3. The learner chooses an action and submits.
4. The sim applies the correct action, updates the parser state and the event being built, and shows the Why text.
5. After line 14, the sim shows the score and the two finished events. The learner should notice that lines 2 and 6 are the two that look like events or properties but are not.

**Feedback:** 14 lines, fixed order, one choice each. Correct: "Correct: <Why>". Incorrect: "Not quite. The parser does this: <the answer's action>. <Why>". The answer is revealed right after each submission, and a running score "n of 14" is shown.

**Starting State:** The 14 lines are shown with line 1 highlighted, nothing parsed, and the question "What does the parser do with this line?"

**Chapter Anchors:** The chapter states that a line starting with a space continues the line before it, that a DTSTART inside a VTIMEZONE is not an event, that all-day events have an exclusive end date, and that a TZID time is converted to UTC.
</details>

!!! mascot-thinking "Convert at the Edge"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Notice the pattern in this chapter: messy, varied inputs get converted at the edge into one clean shape, and everything inside only knows the clean shape. The Pico sits one step further out, so it never sees JSON, ICS, or time zones at all.

## Time Zones and Daylight Saving

A **time zone** is a region's agreement about what the clock says, and it is the source of the quietest bugs in calendar code. Cedar Ridge's tests start at 8:00 AM, but "8:00 AM" is not a moment until you say where, and where's offset from UTC (Coordinated Universal Time, the same everywhere) changes during the year because of daylight saving time. Chicago is five hours behind UTC in summer (CDT) and six hours behind in winter (CST).

The rule the book follows has three parts. Store a *timed* event as a UTC instant. Keep an *all-day* event as a plain date, because "Labor Day" is Sept 7 everywhere and is not a moment at all; converting it to UTC by mistake would move it to the wrong day for a school west of Greenwich. And convert to the school's zone only at the edge, when producing words for a student, using the IANA zone name (`America/Chicago`) with Python's `zoneinfo`. Never store a fixed offset such as `-06:00` as if it were the zone, because it is only right for half the year. (On Windows, `zoneinfo` needs the `tzdata` package; Linux and macOS have the database built in.)

*Worked example.* Algebra II's tests start at 8:00 AM all year. The UTC time of that same wall-clock hour changes:

| School-local time | Zone in force | UTC |
|-------------------|---------------|-----|
| Tue Oct 20, 2026, 8:00 AM | CDT (UTC-5) | 13:00 |
| Tue Dec 1, 2026, 8:00 AM | CST (UTC-6) | 14:00 |

Daylight saving also makes two kinds of local time that cannot be turned into UTC without a rule. When clocks spring forward, a stretch of local time does not exist. In 2027 Chicago jumps from 2:00 AM to 3:00 AM on March 14, so "2:30 AM" never happens. When clocks fall back, a stretch happens twice: on November 1, 2026, "1:30 AM" occurs once in CDT and again an hour later in CST. A school calendar rarely uses these hours, but a feed can, and a program that crashes or guesses differently each time is worse than one with a fixed rule. The book's rule, which is the one Python's `zoneinfo` applies with `fold=0` and which the iCalendar standard (RFC 5545) states for `DTSTART` values, is to read a time that does not exist using the offset from before the gap, and to read a time that happens twice as the first one. The tests check every case:

| School-local time | What it is | UTC | Reads back as |
|-------------------|------------|-----|---------------|
| 2026-11-01 01:30 | happens twice; take the first | 06:30 | 1:30 AM CDT |
| 2026-11-01 02:30 | after the change, once | 08:30 | 2:30 AM CST |
| 2027-03-14 01:30 | before the change | 07:30 | 1:30 AM CST |
| 2027-03-14 02:30 | does not exist | 08:30 | 3:30 AM CDT |
| 2027-03-14 03:30 | after the change | 08:30 | 3:30 AM CDT |

The nonexistent 2:30 AM and the real 3:30 AM land on the same UTC instant, which is the visible sign of the rule. The day of the change is also 25 hours long in the fall, which the tests confirm.

The same care applies to the word "today". A server computer is often set to UTC. At 2:30 AM UTC on October 20 it is still the evening of October 19 in Chicago, and a briefing built on the server's own date would announce the wrong day. Every query in this chapter therefore takes a `now` that is already converted to the school's zone, and `today` means the school's today.

Try the conversions yourself, including the two awkward hours.

#### Diagram: Time Zone and UTC Converter

<details markdown="1">
<summary>Time Zone and UTC Converter</summary>
Type: microsim
**sim-id:** school-time-utc-converter<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the UTC time of 8 school-local times, including 3 that fall at a daylight-saving change, with at least 7 of the 8 exactly right.

**Prerequisites:** UTC, time zone, daylight saving time, offset, CDT, CST, EDT, a time that does not exist, a time that happens twice (all defined in the section "Time Zones and Daylight Saving" above this block).

**Evidence of Mastery:** For each of the 8 local times, in order, the learner types the UTC time as hours and minutes (24-hour clock) and the UTC date, then submits. An answer is correct when both the time and the date equal the Answer column. Mastery is 7 of 8 correct on the first submission of each item. Using the exploration clock before the items is exploration, not evidence.

**Misconceptions:** (1) The offset from UTC is the same all year. (2) A time that does not exist is an error. (3) A time that happens twice has no answer. (4) The same wall-clock time in two cities is the same instant.

**Instructional Rationale:** Calculating with offsets requires the learner to first decide which offset is in force on a given date, and the edge cases force the learner to apply a stated rule rather than a memorized offset. Committing a number before the answer is shown exposes the wrong-offset habit.

**Content:**

The two rules for awkward times, always shown: (1) a local time that does not exist is read with the offset in force before the gap; (2) a local time that happens twice is read as its first occurrence. The zone rules for America/Chicago: CDT is UTC minus 5 hours from the second Sunday in March at 2:00 AM until the first Sunday in November at 2:00 AM; CST is UTC minus 6 hours the rest of the year. For America/New_York the offsets are EDT UTC minus 4 and EST UTC minus 5, on the same dates.

The 8 items, in order:

| # | Local time and zone | Answer (UTC) | Why (shown as feedback) |
|---|---------------------|--------------|-------------------------|
| 1 | Tue 2026-10-20 08:00, America/Chicago | 2026-10-20 13:00 | October 20 is before the first Sunday in November, so CDT applies: 8 + 5 = 13. |
| 2 | Tue 2026-12-01 08:00, America/Chicago | 2026-12-01 14:00 | December is CST: 8 + 6 = 14. The same wall-clock hour is one hour later in UTC than in October. |
| 3 | Sun 2026-11-01 01:30, America/Chicago | 2026-11-01 06:30 | 1:30 AM happens twice that morning. Rule 2 takes the first, which is CDT: 1:30 + 5 = 6:30. |
| 4 | Sun 2026-11-01 02:30, America/Chicago | 2026-11-01 08:30 | After the clocks fall back at 2:00 AM CDT the zone is CST, and 2:30 AM happens once: 2:30 + 6 = 8:30. |
| 5 | Sun 2027-03-14 01:30, America/Chicago | 2027-03-14 07:30 | Before the 2:00 AM jump it is still CST: 1:30 + 6 = 7:30. |
| 6 | Sun 2027-03-14 02:30, America/Chicago | 2027-03-14 08:30 | 2:30 AM does not exist that day. Rule 1 uses the offset from before the gap, CST: 2:30 + 6 = 8:30. |
| 7 | Sun 2027-03-14 03:30, America/Chicago | 2027-03-14 08:30 | After the jump it is CDT: 3:30 + 5 = 8:30, the same instant as item 6. |
| 8 | Tue 2026-10-20 09:00, America/New_York | 2026-10-20 13:00 | New York is on EDT: 9 + 4 = 13. It is the same instant as item 1: the same instant is a different wall-clock time in a different zone. |

**Provenance:** The zone rules are the published US daylight-saving rules for these zones, and the answers were computed with Python's `zoneinfo` in `src/chapters/16-school-agent-calendar/server/test_pipeline.py`, which checks items 1 to 7 and item 8's offset.

**Rules:** UTC time = local time minus the zone's offset (offset is negative west of Greenwich, so local time plus the number of hours behind). Which offset applies depends on the date and the zone's rule. The UTC date may differ from the local date when the sum passes midnight. Rules 1 and 2 above decide the nonexistent and repeated local times.

**Learner Activity:**

1. The learner opens the exploration clock, picks a zone and a local date and time, and sees the UTC time, the offset in force, and a note when the time does not exist or happens twice.
2. The learner starts the 8 items. Item 1 is shown with an empty answer.
3. The learner types the UTC date and time and submits.
4. The sim shows the correct UTC time, the offset used, and the Why text.
5. After item 8, the sim shows the score. The learner should notice that items 6 and 7 give one instant for two different local times.

**Feedback:** 8 items, fixed order, one submission each. Correct: "Correct: <Why>". Incorrect: "Not quite. The UTC time is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** The exploration clock shows America/Chicago, 2026-10-20 08:00, with the question "What time is this in UTC?"

**Chapter Anchors:** The chapter states that 8:00 AM on Oct 20, 2026 in Chicago is 13:00 UTC and on Dec 1, 2026 is 14:00 UTC, that 2:30 AM on 2027-03-14 does not exist and is read with the offset from before the gap, and that 1:30 AM on 2026-11-01 happens twice and the first is taken.
</details>

!!! mascot-warning "A Holiday Is a Date, Not a Moment"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If you convert an all-day event to UTC, "Labor Day" can slide to the wrong day for some zones. Keep all-day events as plain dates and convert only events that have a time. The parser's `Event` stores them in different fields so that you cannot mix them up by accident.

## Keeping Up With the Feed: Polling and Caching

**Calendar polling** is the server fetching the feed on a schedule to pick up changes. How often matters for two reasons. A calendar changes a few times a day at most, so asking every few seconds buys nothing, and a feed belongs to someone: Google, the school office, a web host. Hammering it can get your server blocked.

The book's `FeedCache` class makes a polite poller out of four rules, all visible in `calendar_source.py`:

1. **Never ask more often than `poll_minutes`.** Inside the interval, the saved copy is used and no request is made at all. The default is 60 minutes, which is 24 requests a day for the whole school, whatever the number of devices, because the *server* polls and the devices just receive alerts. If each of 30 devices polled the feed every 5 minutes instead, the feed would see \( 30 \times 288 = 8{,}640 \) requests a day for the same information.
2. **Ask "has it changed?"** Each fetch remembers the feed's `ETag` and `Last-Modified` headers and sends them back next time as `If-None-Match` and `If-Modified-Since`. An unchanged feed answers `304 Not Modified` with no body, and the server keeps its saved copy.
3. **Identify yourself.** The request carries a `User-Agent` naming the project, so a feed owner who sees traffic can tell what it is.
4. **If the feed is down, keep going.** The saved copy is used, the next attempt waits five minutes (or the polling interval, if that is shorter) instead of hammering a dead address, and only a server with neither a fresh nor a saved copy gives up.

The test suite checks all four against a small local web server that serves the real Cedar Ridge feed:

```text
ok   first poll fetches (200)
ok   polls inside the interval make no request
ok   after the interval the ETag gets a 304 and the saved copy is used
ok   the downloaded feed parses to the same 92 events
ok   with the feed down, the saved copy is used ('stale')
ok   and it does not hammer the dead feed
```

To use a real feed, put its address in `ics_url` in `agent.toml`; to keep using the file, leave `ics_url` empty and set `ics_path`.

!!! mascot-warning "Your Feed Is Not Cedar Ridge's"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Cedar Ridge's file was generated by a script and is tidy; a real export may hold Windows zone names, recurring events, and folded lines, and the reader skips what it cannot handle. Run `check_config.py` on your real feed and read every warning before the first school morning, and compare the event count with what the calendar shows.

## Google Calendar, OAuth, and Why a School May Skip Both

Many schools keep their calendar in Google Calendar, so two questions come up. How does the server get the events out? And what is OAuth, which every Google tutorial mentions?

The simplest way needs no program-to-program trust at all. Every Google calendar has a **secret address in iCal format** (under Settings, then Integrate calendar). It is an ICS feed at a long unguessable web address, and `ics_url` accepts it directly. Anyone who has the address can read the calendar, so Google tells you to keep it private, and you can reset it, which makes the old address stop working. For a calendar that is already public, such as a published academic calendar, the public address works the same way. For most schools this is the right choice: one read-only address, no accounts, no secrets other than the address itself.

The **Google Calendar API** is the other way. Instead of a file, the server makes requests such as `GET https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events` and gets JSON back. It is more work, and it buys three things the feed cannot. It can read a *private* calendar for which no secret address is available. It can expand recurring events on Google's side (with `singleEvents=true`, which also lets you sort with `orderBy=startTime`), so your server does not have to implement recurrence. And it can do things beyond reading, such as writing events, if you ask for permission to.

**OAuth** is the standard way a program gets that permission without ever seeing a person's password. The flow, in outline:

1. The program sends the user to Google's own page, naming the *scopes* it wants. A scope is one permission. For reading calendars the narrowest one that Google lists for `events.list` is `https://www.googleapis.com/auth/calendar.readonly` (several narrower read-only ones exist; check the documentation for the current list).
2. The user signs in to Google, reads what is being requested, and approves.
3. Google gives the program an **access token**, a string that proves the approval and works for a short time, and usually a **refresh token** that can fetch new access tokens without asking the user again.
4. The program sends the access token with each API request.

Two things in that list are secrets: the refresh token, and the *client secret* that identifies the program to Google. Anyone who holds them can read the calendar as that user. They belong on the server only, in an environment variable or a file that only the server's account can read, never in the repository, and **never on the Pico**. The Pico is a device that students carry and open, and a secret copied onto it is a secret copied onto every student's desk. A school's Google Workspace administrator can also arrange access for a whole organization without each person clicking through approval screens; that is an administrator task and is beyond this book. Chapter 17 covers keeping secrets out of the wrong places.

This book does not ask you to call Google: nothing in this chapter's code or tests contacts it, and the `events.list` details above come from Google's documentation, not from a run. The point of describing it is the design decision: choose the simplest source that gives the data you need. A published or secret ICS address is a smaller attack surface than a long-lived OAuth token on a server, which is a good reason for a school to prefer it.

!!! mascot-tip "Treat a Secret Calendar Address Like a Password"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Put a secret iCal address in the `SCHOOL_ICS_URL` environment variable on the server, which the code reads before `ics_url`, so it never lands in a file you commit. If it is ever pasted somewhere public, reset it in Google Calendar. A secret address in a public repository is the same as posting the calendar.

## Asking the Calendar

An **upcoming events query** is a question put to the calendar: which events have not finished yet, starting soonest, within some number of days, perhaps limited to one category or one course. Every spoken question in this chapter reduces to one. "When is my next test?" asks for the first upcoming event of category `test`. "What is due this week?" asks for events of category `due` within 7 days.

Two details of `query.py` are worth stating, because they are where simple code goes wrong. First, *upcoming* means "not over yet," not "starts later than now." Homecoming Week, a multi-day all-day event, is still upcoming on Wednesday of that week, and a test is no longer upcoming at 8:05 AM on its day, though it was at 7:59. The Cedar Ridge tests have a start time and no end time, so the code treats them as zero-length: upcoming only until they begin. Second, `now` is in the school's zone (see the time-zone section), so a server running in UTC still answers about the school's day.

The answers come back in Chapter 1's reply shape, `{"speak": ..., "show": ..., "next_mode": ...}`, from `compose.answer()`, which is the rule-based `decide()` of Chapter 1 grown up. Here are the questions from the Cedar Ridge demo script, asked on the suggested demo morning (Monday, October 19, 2026, 9:00 AM), with the real output of `ask.py`:

| Question | `speak` | `show` |
|----------|---------|--------|
| When is my next test? | Your next test is Algebra II Unit 3, Quadratics, tomorrow at 8 AM. | Algebra II test: tomorrow 8 AM |
| What is due this week? | English 10 personal narrative draft is due on Wednesday. Biology osmosis lab report is due on Thursday. | 2 due this week |
| Is there school on Friday? | Yes, there is school on Friday. Football versus Eastbrook Eagles is on Friday at 7 PM. Location: Griffin Field. | School Friday |
| When does the quarter end? | End of Quarter 1 is on Friday, October 30. | End of Quarter 1 |
| What's happening tonight? | Nothing is on the calendar tonight. | Nothing tonight |
| When is Thanksgiving break? | Sorry, I only know about tests, due dates, and school days. | Try: next test? |
| Do I have anything big coming up this week? | Sorry, I only know about tests, due dates, and school days. | Try: next test? |

The last two rows are the point. The rules recognize "test," "due," "school on," "tonight," and "quarter," and nothing else. The Thanksgiving question is easy for a person but falls through, as Chapter 1's "anything big" question did, and that gap is exactly what a Level 2 LLM brain fills. The reply is honest instead of invented: when the rules do not know, they say so. Chapter 1's agent progression is the plan for closing the gap, and the data this chapter prepares (events with categories, courses, and normalized times) is what you would hand to the LLM as facts, so that the date in its answer comes from the calendar and not from its imagination. Notice that the spoken answer repairs the title for speech: `Unit 3 - Quadratics` becomes "Unit 3, Quadratics," a pause instead of a spoken "dash." That is the `[voice.say]` table in `agent.toml`, covered below.

Chapter 14's buddy server calls two functions of a module named `brain.py`: `load_events()` once at start-up and `make_reply(text, events)` for each question, and that chapter says Chapter 16 replaces them. `calendar_brain.py` is the replacement. Copy it over `brain.py`, together with this folder's other server modules and `agent.toml`, and the same server answers from the calendar. For the Pico's offline cache, `load_events()` still returns a plain list of `{"title", "day"}` items (the next 12 tests and due dates), so Chapter 14's `/v1/events` endpoint keeps working. The book checked exactly this: a scratch copy of Chapter 14's `buddy_server.py` with only `brain.py` replaced answered `POST /v1/ask` with "Your next test is Algebra II Unit 3, Quadratics, tomorrow at 8 AM.", refused a request with no token, and served the offline list. For trying the calendar brain without voice or WebSocket, `buddy_server_min.py` is a smaller server with just `/v1/ask` and `/v1/health`, using the same `/v1/` paths and `X-Buddy-Token` header as Chapters 13 and 14.

## The Daily Briefing and Reminders

A **daily briefing** is a short spoken summary of the day, composed on the server each school morning and pushed to every device. A **reminder** is a pushed alert sent ahead of one specific event: a test or a due date. Both are the same machinery as Chapter 15's alerts with the calendar added, and the server builds them, because the server knows the date and the rules. The device does nothing but show and speak what arrives.

The briefing follows a fixed shape that the `[briefing]` section controls: a greeting, what is on today (up to `max_items` events), the next test within `upcoming_days`, and what is due within `upcoming_days`, with one optional mascot line at the end. It is not sent on weekends or no-school days. Here is the real briefing for the demo morning, as `push_daily.py` would publish it:

```text
$ python3 push_daily.py --now 2026-10-19T07:30
Mon 2026-10-19 07:30 (America/Chicago): 2 message(s)

school/crhs/alert
  {"id":"20261019-briefing","type":"briefing","title":"Good morning, Cedar Ridge","when":"Test tomorrow",
   "text":"Good morning from Cedar Ridge. Picture Retake Day is today. Location: Library. Your next Algebra II test is tomorrow at 8 AM. English 10 personal narrative draft is due on Wednesday. Biology osmosis lab report is due on Thursday. Griffins aim high!"}  (361 bytes)

school/crhs/class/118/alert
  {"id":"20261019-crhs-018-d1","type":"test","title":"Algebra II test","when":"Tomorrow 8:00 AM","text":"Heads up. Your Algebra II test is tomorrow at 8 AM. You've got this.","at":"2026-10-20T13:00Z"}  (198 bytes)
```

(The line breaks inside the first message are added for the page; the real output is one line each.) Look at how the pieces connect to Chapter 15. The briefing goes to the school-wide topic and is longer than a normal alert, so the format allows 300 characters of `text` for type `briefing`. The test reminder goes to `school/crhs/class/118/alert`, the room of the Algebra II course from `[[courses]]`, so only devices in that room beep for it. And its `id`, `20261019-crhs-018-d1`, is built from the date, the event, and the lead time ("1 day before"), the same id the Chapter 15 sample used. Run `push_daily.py` twice on the same morning and every id repeats, so a device that already showed the alert ignores the second, which is why the job is safe to run twice and why a cron job that retries after a failure cannot spam anyone.

Which reminders fire is set by `[reminders]`: Cedar Ridge sends a test reminder 7 days and 1 day ahead, a due reminder 1 day ahead, and a no-school notice 1 day ahead. The job only runs on school days, so a reminder whose day is a weekend or a holiday would be lost. The code handles it by sending on the *last school day before*. Two real cases from Cedar Ridge show it. The Biology Unit 2 test is on Tuesday, November 10, so its week-ahead reminder would be due on Tuesday, November 3, Election Day, a no-school day; it goes out on Monday, November 2 instead, in the same run as the notice that there is no school the next day. Across the whole school year, 31 tests with two reminders each, 19 due dates, and 9 no-school notices produce exactly 90 reminders, every one a valid alert under 512 bytes, and no two share an id; the test suite checks each of those.

!!! mascot-tip "Preview Before You Send"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Run `push_daily.py --now 2026-10-19T07:30` with no `--send` and read the output aloud to someone. If a sentence trips your tongue, a speech engine will trip too; fix it in `agent.toml` and run it again.

Now apply the briefing rules to a day.

#### Diagram: Daily Briefing Composer

<details markdown="1">
<summary>Daily Briefing Composer</summary>
Type: microsim
**sim-id:** daily-briefing-composer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** apply<br/>
**Learning Objective:** The learner will apply the daily briefing rules to 8 Cedar Ridge events on the morning of Monday, October 19, 2026, by sorting each into the part of the briefing it appears in or "Not mentioned," with at least 7 of the 8 correct.

**Prerequisites:** daily briefing, event category, today's events, next test, due soon, upcoming_days, max_items (all defined in the section "The Daily Briefing and Reminders" above this block).

**Evidence of Mastery:** For each of the 8 events, in order, the learner chooses one of four places: Today, Next test, Due soon, or Not mentioned, then submits. A choice is correct when it equals the Answer column. Mastery is 7 of 8 correct on the first submission of each event. Changing the date or the settings afterward in exploration is not evidence.

**Misconceptions:** (1) The briefing lists every upcoming event. (2) A test on the same day goes under "Next test." (3) A due date 10 days away is "due soon." (4) A test tomorrow is not mentioned because it is not today.

**Instructional Rationale:** Applying rules to cases needs cases that sit on each side of every rule boundary: today versus later, a category the briefing reads versus one it ignores, inside versus outside the window. The learner commits a place for each event before the briefing text is shown, so a misread rule appears as a wrong place.

**Content:**

The settings for the exercise are fixed: today is Monday 2026-10-19, `max_items` = 3, `upcoming_days` = 7. The rules: "Today" holds today's events of category test, due, event, sports, or academic, up to 3. "Next test" is the first test after today and within 7 days. "Due soon" holds due events after today and within 7 days, up to 3. Everything else is "Not mentioned." Events of category no-school do not appear in the briefing.

The 8 events, in order:

| # | Event (title, date, category) | Answer | Why (shown as feedback) |
|---|-------------------------------|--------|-------------------------|
| 1 | Picture Retake Day, Mon Oct 19, event | Today | It is today and its category is event. |
| 2 | TEST: Algebra II Unit 3 - Quadratics, Tue Oct 20 8:00 AM, test | Next test | It is the first test after today, 1 day away. |
| 3 | DUE: English 10 personal narrative draft, Wed Oct 21, due | Due soon | A due date 2 days away is inside the 7-day window. |
| 4 | DUE: Biology osmosis lab report, Thu Oct 22, due | Due soon | 3 days away, and it is the second due item, within the limit of 3. |
| 5 | Football vs. Eastbrook Eagles, Fri Oct 23, sports | Not mentioned | A sports event is announced only on its own day. |
| 6 | Maker Club: Study Buddy Build Night, Mon Oct 26 3:30 PM, event | Not mentioned | An event on a later day is not in the briefing. It is also 7 days away, at the edge of the window. |
| 7 | TEST: Biology Unit 2 - Genetics, Tue Nov 10 10:02 AM, test | Not mentioned | 22 days away, outside the 7-day window. |
| 8 | End of Quarter 1, Fri Oct 30, academic | Not mentioned | An academic milestone is announced only on its own day. |

After the last event, the sim shows the composed briefing for these rules: "Good morning from Cedar Ridge. Picture Retake Day is today. Location: Library. Your next Algebra II test is tomorrow at 8 AM. English 10 personal narrative draft is due on Wednesday. Biology osmosis lab report is due on Thursday. Griffins aim high!"

**Provenance:** The events and dates are from the real Cedar Ridge calendar (`docs/schools/cedar-ridge-high-school/calendar.ics`). The rules and the final text come from `src/chapters/16-school-agent-calendar/server/compose.py` and are checked by `test_pipeline.py`.

**Rules:** An event is "Today" if its date range includes the briefing date and its category is test, due, event, sports, or academic, counting up to `max_items`. "Next test" is the earliest event of category test with a start date after today and a start before today plus `upcoming_days` days. "Due soon" is events of category due with a start date after today and before today plus `upcoming_days` days, up to `max_items`. For exploration the learner may change the date to any school day of 2026-2027 (weekends and no-school days produce no briefing), `max_items` from 1 to 5 in steps of 1 (default 3), and `upcoming_days` from 1 to 14 in steps of 1 (default 7); the text is rebuilt by the same rules. The mascot line is added last and dropped first if the text would exceed 300 characters.

**Learner Activity:**

1. The learner reads the rules and the 8 events, then opens exploration, changes `upcoming_days` and the date, and watches which events enter or leave the briefing.
2. The learner starts the 8 events. Event 1 is shown with the four places.
3. The learner chooses a place and submits.
4. The sim shows the correct place and the Why text, and adds or leaves out the event's sentence in the briefing being built.
5. After event 8, the sim shows the score and the complete briefing. The learner should notice that only 4 of the 8 events are spoken, and that sports and academic events appear only on their own day.

**Feedback:** 8 events, fixed order, one choice each. Correct: "Correct: <Why>". Incorrect: "Not quite. This event goes in <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** The 8 events are listed with the settings (today Monday 2026-10-19, 3 items, 7 days) and the question "Which part of the briefing is this event in?"

**Chapter Anchors:** The chapter's briefing for 2026-10-19 is the text shown above, 361 bytes as published; the sim reproduces its wording. The chapter states that the briefing is not sent on weekends or no-school days, and that the mascot line is added last.
</details>

## Voice, Language, and Tone

Everything the device says was written by a program, so a school's choices about *how* it speaks live in `[voice]`. **Voice and prompts** means two things in this book. The first is the *templates* the rule-based server fills in: the greeting `Good morning from {school}.`, the reminder openers `Heads up.` and `Reminder.`, and the one-line mascot flavor for each category. The second is the *prompt* an LLM-backed brain (Chapter 1, Level 2) receives with every question: the `system_prompt` string that tells it who it is and how to answer. Both come from the same file so that the rule-based and LLM brains sound like the same buddy.

**Language and tone** is the set of writing rules that make the words work for ears and for teenagers. The rules the book follows for grades 9 to 12, and that `compose.py` is written around:

- **Short sentences, one idea each.** About 12 words or fewer. The checker warns when a template has a sentence over 15 words, because a listener cannot reread.
- **Say it as a person would.** "8 AM," not "08:00." "Tomorrow" and "Wednesday," not "2026-10-21." A day more than a week away gets its full name ("Tuesday, November 10"), because "next Tuesday" means different dates to different people.
- **Fix what a speech engine reads badly.** The `[voice.say]` table replaces text before speaking: `vs.` becomes "versus," ` - ` becomes a comma (a pause), and `PSAT 10` can be spelled out. Every school has its own awkward titles.
- **Be calm.** Tell, do not scold. "Reminder. Biology lab report is due tomorrow." is fine, and "You'd better finish your lab report!" is not. The mascot's line is encouragement, one short sentence, and `mascot_flavor = false` turns it off.
- **Say "I do not know."** When the rules cannot answer, the reply says so. An invented answer about a test is worse than none.

The LLM prompt follows the same rules in a sentence. Cedar Ridge's reads, in part: "Answer in one or two short sentences that sound natural when spoken aloud. Use only the calendar facts you are given. If you do not know, say so. Be friendly and calm, never scolding." Whether an LLM keeps to that is something to test, not assume: the book does not call one here, and Chapter 18 has the testing discipline to apply.

Because wording is configuration, adapting it is an edit to `greeting` and the flavor lines.

## School Mascot Design

**School mascot design** is making a picture that works on the round display, and "works" is more demanding than it sounds. The glass is 360 by 360 pixels, but the bezel hides everything outside a circle of radius `SAFE_RADIUS` = 168 pixels around the center (Chapter 6, and `config.py`). A square picture loses its corners, and a round badge that fills the whole 360-pixel frame loses its outer ring.

Cedar Ridge's Gale the Griffin is exactly such a badge: a circle that fills the 360 by 360 frame, with transparent corners. `mascot_check.py` measures the picture against the glass, from the real file:

```text
$ python3 mascot_check.py
griffin-360.png: 360 x 360
  non-transparent pixels      : 102269
  outside the safe circle (r>168): 13569 (13.3%)
  farthest pixel from center  : 180.6

  size                            bytes
  full frame 360 x 360          259,200
  safe circle 336 x 336         225,792
  configured 240 x 240          115,200
  small 120 x 120                28,800
  layout region 64 x 64           8,192
```

If the full image were drawn at 360 by 360, 13.3 percent of its pixels, mostly the green background and the outer gold ring, would sit under the bezel, and the badge would look clipped. Three design rules follow, and they apply to any school's mascot:

1. **Make the picture fit the circle, not the square.** Scale a round badge so its diameter is at most \( 2 \times 168 = 336 \) pixels, or smaller for a splash screen with text below it. Everything the student must see stays inside the glass.
2. **Keep it bold and simple.** The display is small and viewed from a desk. Thick outlines, flat colors, and no text inside the picture (the device draws the name itself in a font it can control) survive shrinking. Gale's image prompt (`docs/schools/cedar-ridge-high-school/mascot-image-prompt.md`) lists these rules for generating art.
3. **Count the bytes.** An RGB565 pixel is 2 bytes (Chapter 5), so a square picture of side \( s \) costs \( s \times s \times 2 \) bytes of flash and the same number of bytes to send over SPI:

\[ 240 \times 240 \times 2 = 115{,}200 \text{ bytes}, \qquad \frac{115{,}200 \times 8}{24{,}000{,}000} = 38.4 \text{ ms at the 24 MHz display clock.} \]

That is the *wire-time minimum* for drawing it once, and it is paid when the splash screen appears, not every frame. A full 360 by 360 frame is 259,200 bytes, about 6 percent of the Pico 2 W's 4 MB of flash (\( 259{,}200 / 4{,}194{,}304 = 0.062 \)), so a school could store a handful, but the 64 by 64 version that fits the layout's mascot region (8,192 bytes) is the one a running device redraws.

The book makes the 240 by 240 file with `mascot_check.py --write`, which scales the picture, blacks out everything outside its inscribed circle, and writes raw RGB565 with the high byte first, the same format as Chapter 6's loader. Two Pico tests use it. `01-show-school-mascot.py` loads the file ten rows at a time with `blit_buffer()` and prints how long the draw took. `02-edition-splash.py` builds the whole splash screen (mascot, school name, slogan) and *checks before it draws* that every piece fits the visible circle:

```text
mascot  circle reaches 162 px from the center: inside
name    184 x 16 box at  88,266: inside
slogan  200 x 16 box at  80,286: inside
PASS: all 3 items inside the safe circle. Look at the screen.
```

That output is from the book's fake-Pico test layer, which runs the real display driver but no glass, so it proves the geometry and not the look. The arithmetic behind the slogan line is a good exercise. Its bottom corners, at row 301, are \( \sqrt{100^2 + 121^2} \approx 157 \) pixels from the center, inside 168. But the visible chord at that row is only \( 2 \sqrt{168^2 - 121^2} \approx 233 \) pixels wide, room for 29 characters of the 8-pixel font, so a 40-character slogan would not fit, and the check names the line that fails.

Where does the device learn its mascot, name, and slogan? Not from TOML. The Pico never reads `agent.toml`. `make_edition.py` writes a small Python file, `edition.py`, from the same configuration, with the school's name, slogan, id, colors (converted to RGB565), mascot file and size, and wake phrase. The device imports it like `config.py`, so the server and every device are built from one source and cannot disagree about the school's id or the mascot file.

!!! mascot-encourage "Tuning a Look Takes Iterations"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Fitting art to a round screen rarely works on the first try: a badge that looks perfect on a computer loses its ring on the glass. Run the check, adjust the size, upload, and look. Each pass takes a minute, and you already know how to measure what changed.

## A Custom Wake Phrase

The last piece of per-school customization is what the student says to wake the device. A **custom wake phrase** replaces the default "Hey Pico" with something of the school's own, such as "Hey Gale." The setting is one line, `phrase = "Hey Pico"` in `[wake]`, and it is copied into `edition.py` as `WAKE_PHRASE`, so the screen can say "Say 'Hey Gale'." But changing the words does *not* change what the detector listens for. That is the trap.

Chapter 12's wake-word detector is a template matcher: it compares the incoming sound with a stored recording of someone saying the phrase. A new phrase therefore needs five things:

1. **Enrollment again.** Record the new phrase and build a new template, as Chapter 12 does for "Hey Pico." The old template does not match the new words.
2. **A new threshold.** Where the score is high enough to wake depends on the phrase and the speaker. Chapter 12's false accept and false reject measurements have to be repeated for the new phrase, because the best threshold for one phrase is not the best for another.
3. **A phrase that fits.** The detector compares a fixed-length window of sound, so a phrase much longer than that window cannot be matched whole. Check the window length in Chapter 12 before choosing.
4. **Approval.** Always-on listening needs approval from a parent, teacher, or school (Chapter 17), and a new phrase does not change that: it only changes the words the approval covers.
5. **The honest limits.** Template matching works best for the person who enrolled and degrades for other voices (Chapter 12's single-speaker limits). A custom phrase gives no relief from that.

Which phrase is a good one? A phrase with more distinct sounds gives the template more to compare and fewer accidents, because a short, common sound pattern is easier to trigger by mistake, which is a false accept. A longer, more distinctive phrase is generally easier to detect reliably, as long as it still fits the window and students will actually say it. "Hey Pico" has about three syllables. "Hey Gale" has two and "Hey Cedar Ridge" has four. The configuration checker applies a rough syllable count (vowel groups, which miscounts some words) as a *hint*, and says so. On this book's checker, "Hey Pico" passes quietly, "Hey Gale" earns "about 2 syllable(s); a longer phrase gives the detector more to compare," and every non-default phrase gets "enroll it again (Chapter 12) and re-test false accepts." The checker cannot tell you whether a phrase works. Only Chapter 12's tests can, and the book has not run any phrase other than the default.

## Putting It All Together

An office publishes a calendar (or someone types `events.json`). The server reads it into one list of events with categories, courses, UTC times, and plain dates. `agent.toml` says what to do with them, and a daily job composes a briefing and reminders and publishes them over MQTT with ids that make repeats harmless. The desk device shows and speaks what arrives, wearing the school's name, colors, and mascot from `edition.py`. To adapt all of this to another school, change `agent.toml` and the calendar source, run `check_config.py` until it says `0 error(s)`, run `test_pipeline.py`, and preview the briefing with `--now`, without touching any Python.

Key takeaways:

- One `agent.toml` holds every school-specific choice; `check_config.py` turns a typo into a plain-English message before it fails on a school morning.
- Titles beginning `TEST:`, `DUE:`, and `NO SCHOOL:` give events their categories. A hand-edited `events.json` is the first source and an ICS feed is the one a school will really have.
- Parse calendars on the server, never on the Pico. The small reader handles folding, escapes, all-day and timed events, and warns about recurrence and unknown zones; use `icalendar` with `recurring-ical-events` when you need those.
- Store timed events as UTC and all-day events as dates; convert at the edge. Daylight saving needs two rules for times that do not exist or happen twice.
- Poll politely: at most once per `poll_minutes`, with ETags, and fall back to the saved copy. A published or secret ICS address is often simpler and safer than the Google Calendar API and OAuth, and OAuth secrets never go on the Pico.
- Briefings and reminders are built on the server with alert ids made of the date, the event, and the lead time, so running a job twice is harmless.
- Write for ears: short sentences, spoken times and days, replacements for things a speech engine reads badly, and an honest "I do not know."
- A round display shows a circle of radius 168: fit the mascot to it, and count the bytes. A new wake phrase needs a new enrollment and a new threshold.

Test yourself with these three questions, and click each one to reveal its answer.

??? question "The office adds a multi-day all-day event, Spirit Week, from Mon Oct 26 to Fri Oct 30, written in the feed as `DTSTART;VALUE=DATE:20261026` and `DTEND;VALUE=DATE:20261031`. What are the first and last days the parser stores? Click to expand"
    Oct 26 and Oct 30. In an ICS file the end date of an all-day event is exclusive, so the last day is the `DTEND` date minus one day. The first day is the `DTSTART` date, with no time-zone conversion.

??? question "A test is at 8:00 AM Central on the day after the clocks fall back. Why can't you store its UTC time as a fixed 13:00? Click to expand"
    Because the offset changes. In CDT, 8:00 AM Central is 13:00 UTC, but after the fall change the zone is CST, and 8:00 AM is 14:00 UTC. Store the instant computed with the zone's rule for that date, and convert back with the zone name, never with a fixed offset.

??? question "The server's briefing job runs twice by accident one morning. What stops every device from announcing the test twice? Click to expand"
    The alert id. It is built from the date, the event id, and the lead time, so both runs produce the same id, and the device's `Seen` list from Chapter 15 drops the second alert as a repeat.

!!! mascot-celebration "A Buddy With a School of Its Own"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just built a pipeline that reads a real school calendar from a JSON file or an iCalendar feed, converts times safely, composes spoken briefings and reminders, and dresses the device in a school's mascot and voice. The server does the hard parts and the Pico only has to show and speak, which is exactly how this should be divided.

In Chapter 17 we ask what a device that listens and connects to a school should and should not be allowed to do.
