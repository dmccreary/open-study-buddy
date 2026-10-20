---
title: Cedar Ridge High School
description: A synthetic high school with a name, slogan, mascot, and school calendar for demonstrating the Open Study Buddy kit.
image: schools/cedar-ridge-high-school/img/griffin-360.png
---
# Cedar Ridge High School

![Gale the Griffin, mascot of Cedar Ridge High School](img/griffin.svg){ width="220" align="right" }

> **Aim high. Listen closely.**

Cedar Ridge High School is **not a real school**. It is a synthetic school invented so the
Open Study Buddy kit has something realistic to talk about during demos and tests: a name to
greet students with, a mascot to draw on the round display, and a full year of tests, due
dates, and events for the agent to announce.

## School Facts

| | |
|---|---|
| Name | Cedar Ridge High School |
| Slogan | Aim high. Listen closely. |
| Mascot | Gale the Griffin ([mascot page](mascot.md)) |
| Teams | The Cedar Ridge Griffins |
| School colors | Forest green `#1F5D3A` and gold `#F2B632` |
| Grades | 9–12 |
| School year | 2026–2027 (first day Aug 25, 2026; last day Jun 3, 2027) |
| Time zone | America/Chicago |
| Suggested wake phrase | "Hey Pico" (the kit default) |

The slogan does double duty: *aim high* is the school's motto, and *listen closely* is a nod
to what the device does.

## Classes and Teachers

A demo student takes these six classes. The `TEST:` and `DUE:` entries in the
[calendar](calendar.md) use these course names.

| Period | Class | Teacher | Room |
|--------|-------|---------|------|
| 1 | Algebra II | Ms. Okafor | 118 |
| 2 | English 10 | Mr. Lindqvist | 205 |
| 3 | Biology | Dr. Tran | Lab 130 |
| 4 | World History | Ms. Alvarez | 220 |
| 5 | Spanish II | Sr. Moreno | 226 |
| 6 | Physical Computing | Mr. Brandt | 214 |

## Bell Schedule

| Block | Time |
|-------|------|
| Period 1 | 8:00–8:55 AM |
| Period 2 | 9:01–9:56 AM |
| Period 3 | 10:02–10:57 AM |
| Period 4 | 11:03–11:58 AM |
| Lunch | 11:58 AM–12:33 PM |
| Period 5 | 12:39–1:34 PM |
| Period 6 | 1:40–2:35 PM |

Exams in the calendar start at the beginning of the class period they belong to, so
"TEST: Biology Unit 2" at 10:02 AM means third period.

## What Is in This Folder

| File | What it is |
|------|------------|
| [Mascot](mascot.md) | Gale the Griffin: personality, colors, and how to put the image on the 360 × 360 display |
| [Calendar](calendar.md) | The 2026–2027 calendar, with a suggested demo date |
| [events.json](events.json) | The calendar as a JSON event file for the buddy server |
| [calendar.ics](calendar.ics) | The same calendar as an iCalendar feed |
| [img/griffin.svg](img/griffin.svg) | Mascot source art (vector) |
| [img/griffin-360.png](img/griffin-360.png) | Mascot at the display's native 360 × 360 size, transparent corners |

## Demo Script

Set the server's "today" to **Monday, October 19, 2026** (see the
[calendar](calendar.md#suggested-demo-date)), then try:

| Say | The agent should find |
|-----|----------------------|
| "When is my next test?" | TEST: Algebra II Unit 3 - Quadratics, tomorrow at 8:00 AM |
| "What is due this week?" | English 10 personal narrative draft (Wed), Biology osmosis lab report (Thu) |
| "Is there school on Friday?" | Yes, and the Griffins play Eastbrook at 7:00 PM on Griffin Field |
| "When does the quarter end?" | Friday, October 30, which is also Spirit Day (green and gold) |
| "What's happening tonight?" | Nothing on Monday evening; the next event is the Friday football game |
| "When is Thanksgiving break?" | No school Nov 25–27 |

To change the data, edit `scripts/build-school-calendar.py` and rerun it from the repo root.
It regenerates `events.json`, `calendar.ics`, and `calendar.md` together so they never
disagree.

!!! note "Instructor note"
    Cedar Ridge is fictional. Any resemblance to a real school, teacher, or event is
    coincidental. When you build a real school edition, replace the name, slogan, mascot,
    and calendar, and keep the `TEST:` and `DUE:` title prefixes.
