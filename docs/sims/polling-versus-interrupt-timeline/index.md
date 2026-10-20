---
title: "Polling Versus Interrupt Timeline"
description: "The learner will compare a polling loop with an interrupt by predicting, for 6 button presses, whether a loop that checks the pin every P milliseconds sees the press, and observing that an interrupt sees all 6."
status: scaffold
library: p5.js
bloom_level: Understand
---

# Polling Versus Interrupt Timeline



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 2: MicroPython Review for Embedded Systems](../../chapters/02-micropython-review/index.md).

```text
Type: microsim
**sim-id:** polling-versus-interrupt-timeline<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** compare<br/>
**Learning Objective:** The learner will compare a polling loop with an interrupt by predicting, for 6 button presses, whether a loop that checks the pin every P milliseconds sees the press, and observing that an interrupt sees all 6.

**Prerequisites:** polling, interrupt, interrupt service routine, falling edge (all defined in the section "Interrupts and Interrupt Service Routines" above this block).

**Evidence of Mastery:** For each of the 6 cases, the learner commits to "seen" or "missed" for the polling loop before the result is shown. A prediction is correct when it matches the Polling result column in Content. Mastery is 5 of 6 correct. Switching to interrupt mode and watching is exploration, not evidence.

**Misconceptions:** (1) A faster loop always catches every press. (2) A very short press is always missed. (3) An interrupt makes the main loop run faster.

**Instructional Rationale:** An Understand-level comparison needs the learner to infer an outcome from a rule rather than watch it. Predicting before the result forces the learner to apply the rule "a poll sees the press only if a check lands inside it," and the interrupt mode then shows why that rule does not apply to hardware edges.

**Content:**

A timeline runs from 0 ms to 220 ms. Polling checks happen at 0 ms and then every P ms. A press is a time interval [start, end) during which the pin reads 0. The polling loop sees a press when at least one check time t satisfies start <= t < end.

| # | P (ms) | Press start (ms) | Press end (ms) | Press length (ms) | Check times inside the press | Polling result | Why (shown as feedback) |
|---|---|---|---|---|---|---|---|
| 1 | 5 | 12 | 22 | 10 | 15, 20 | seen | Two checks land inside the press. |
| 2 | 20 | 12 | 22 | 10 | 20 | seen | The check at 20 ms lands inside the press, by luck. |
| 3 | 20 | 22 | 32 | 10 | none (checks at 20 and 40) | missed | The press starts just after one check and ends before the next. |
| 4 | 100 | 30 | 80 | 50 | none (checks at 0 and 100) | missed | A 50 ms press fits entirely between two checks 100 ms apart. |
| 5 | 100 | 90 | 210 | 120 | 100, 200 | seen | A press longer than P always contains a check. |
| 6 | 50 | 55 | 95 | 40 | none (checks at 50 and 100) | missed | A press shorter than P can fall between two checks. |

In interrupt mode every case is seen at its press start, because the hardware notices the falling edge.

**Provenance:** The numbers are illustrative and the sim labels them "illustrative." The rule that a polling loop misses a press that fits between two checks comes from the chapter section "Interrupts and Interrupt Service Routines."

**Rules:** Checks occur at 0, P, 2P, and so on up to 220 ms. A press is seen by polling when start <= kP < end for some integer k >= 0. In interrupt mode a press is seen at its start time for every case. A press longer than P is always seen by polling.

**Learner Activity:**

1. The learner reads case 1 (P and the press interval) and chooses "seen" or "missed."
2. The sim draws the check times and the press, then shows the result and the Why text.
3. The learner continues through case 6, then sees the score.
4. The learner switches the display to interrupt mode and steps through the six cases again, noticing that every press is marked at its start time.

**Feedback:** 6 cases, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The polling loop <seen or missed> this press: <Why>". The result is revealed after each answer, and a running score "n of 6" is shown.

**Starting State:** Case 1 is shown with the checks marked on the timeline and the question "Will the polling loop see this press?"

**Chapter Anchors:** The chapter states that polling can miss a press that starts and ends between two checks, that an interrupt cannot miss it, and that an ISR should only set a flag.
```

## Related Resources

- [Chapter 2: MicroPython Review for Embedded Systems](../../chapters/02-micropython-review/index.md)
