---
title: "ICS Line Parser Stepper"
description: "The learner will execute the iCalendar parsing rules on the 14 lines of a small feed by choosing what the parser does with each line, with at least 12 of the 14 choices correct."
status: scaffold
library: p5.js
bloom_level: Apply
---

# ICS Line Parser Stepper



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 16: Configuring the School Agent and Calendar](../../chapters/16-school-agent-calendar/index.md).

```text
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
```

## Related Resources

- [Chapter 16: Configuring the School Agent and Calendar](../../chapters/16-school-agent-calendar/index.md)
