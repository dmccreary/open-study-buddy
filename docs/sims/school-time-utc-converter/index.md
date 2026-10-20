---
title: "Time Zone and UTC Converter"
description: "The learner will calculate the UTC time of 8 school-local times, including 3 that fall at a daylight-saving change, with at least 7 of the 8 exactly right."
status: scaffold
library: p5.js
bloom_level: Apply
---

# Time Zone and UTC Converter



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 16: Configuring the School Agent and Calendar](../../chapters/16-school-agent-calendar/index.md).

```text
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
```

## Related Resources

- [Chapter 16: Configuring the School Agent and Calendar](../../chapters/16-school-agent-calendar/index.md)
