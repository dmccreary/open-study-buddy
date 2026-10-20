---
title: "Daily Briefing Composer"
description: "The learner will apply the daily briefing rules to 8 Cedar Ridge events on the morning of Monday, October 19, 2026, by sorting each into the part of the briefing it appears in or \"Not mentioned,\" with at least 7 of the 8 correct."
status: scaffold
library: p5.js
bloom_level: Apply
---

# Daily Briefing Composer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 16: Configuring the School Agent and Calendar](../../chapters/16-school-agent-calendar/index.md).

```text
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
```

## Related Resources

- [Chapter 16: Configuring the School Agent and Calendar](../../chapters/16-school-agent-calendar/index.md)
