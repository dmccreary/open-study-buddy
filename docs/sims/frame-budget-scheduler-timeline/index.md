---
title: "Frame Budget Scheduler Timeline"
description: "The learner will examine 6 loop passes against the 40 ms frame budget by calculating each pass's total time to within 0.1 ms and deciding whether it overruns, with at least 5 of 6 fully correct."
status: scaffold
library: p5.js
bloom_level: Analyze
---

# Frame Budget Scheduler Timeline



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 18: Testing, Integration, and Capstone Projects](../../chapters/18-testing-integration-capstones/index.md).

```text
Type: microsim
**sim-id:** frame-budget-scheduler-timeline<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** examine<br/>
**Learning Objective:** The learner will examine 6 loop passes against the 40 ms frame budget by calculating each pass's total time to within 0.1 ms and deciding whether it overruns, with at least 5 of 6 fully correct.

**Prerequisites:** frame, frame budget, task, task budget, cooperative scheduler, deferral, overrun (all defined in the sections above this block).

**Evidence of Mastery:** For each of the 6 passes the learner types the total milliseconds the pass takes and chooses "overruns" or "fits" before the answer is revealed. A pass is fully correct when the number is within 0.1 ms of the Total column in Content and the choice matches the Overrun column. Mastery is 5 of 6 fully correct. Switching tasks on and off in the free-build timeline in exploration is not evidence.

**Misconceptions:** (1) A task with a big budget only costs its budget. (2) The scheduler can interrupt a task that runs too long. (3) A pass that fits in 40 ms on average cannot overrun. (4) Turning the scheduler on always makes every task run.

**Instructional Rationale:** Examining a pass at the Analyze level means relating its parts to the whole. Summing task costs to a total and comparing it with the frame makes the learner relate each task to the shared budget, and the case where the scheduler defers a task shows how the parts interact.

**Content:**

The tasks, with their cost per run and budget in milliseconds, in the order the scheduler considers them (earlier is more important):

| Order | Task | Cost (ms) | Budget (ms) |
|---|---|---|---|
| 1 | audio | 10.0 | 12 |
| 2 | buttons | 0.5 | 1 |
| 3 | spectrum | 8.5 | 9 |
| 4 | status | 3.0 | 4 |
| 5 | network | 2.0 | 3 |
| 6 | time | 3.8 | 4 |
| 7 | redraw (full screen) | 129.4 | 140 |
| 8 | slice (one eighth of the redraw) | 16.2 | 17 |

The frame budget is 40 ms. The 6 passes, in this order:

| # | Scheduler | Tasks due in the pass | Total (ms) | Overrun | Why (shown as feedback) |
|---|---|---|---|---|---|
| 1 | off | audio, buttons, spectrum | 19.0 | fits | 10.0 + 0.5 + 8.5 = 19.0, which leaves 21.0 ms. |
| 2 | off | audio, buttons, spectrum, status, network, time | 27.8 | fits | 19.0 + 3.0 + 2.0 + 3.8 = 27.8, which leaves 12.2 ms. |
| 3 | off | audio, buttons, spectrum, redraw | 148.4 | overruns | 19.0 + 129.4 = 148.4, which is 108.4 ms over the frame. |
| 4 | off | audio, buttons, spectrum, status, network, slice | 40.2 | overruns | 19.0 + 3.0 + 2.0 + 16.2 = 40.2, which is 0.2 ms over. |
| 5 | on | audio, buttons, spectrum, status, network, slice | 24.0 | fits | After network the pass has used 24.0 ms, which leaves 16.0 ms. The slice's budget is 17 ms, which does not fit, so it is deferred. |
| 6 | off | audio, buttons, spectrum, slice | 35.2 | fits | 19.0 + 16.2 = 35.2, which leaves 4.8 ms. |

**Provenance:** The costs for audio, spectrum, status, and time are the measurements in Chapters 8 and 6, the redraw cost is the Chapter 5 measurement, and the slice cost is 129.4 divided by 8, rounded to 16.2. The buttons and network costs, and all the budgets, are assumed values from `08-scheduler-demo.py`. The sim labels the costs "model inputs, not a measurement of your program."

**Rules:** Total = sum of the costs of the tasks that run in the pass. A pass overruns when Total > 40.0. With the scheduler on, tasks are considered in the Order column; a task is deferred (not run) when its budget is greater than 40.0 minus the total so far. With the scheduler off, every due task runs. Answers are in milliseconds with one decimal place.

**Learner Activity:**

1. The learner switches the 8 tasks on and off in a free-build timeline and flips the scheduler on and off. The timeline shows each task as a block along the 40 ms frame, and a block past 40 ms is marked as an overrun.
2. The learner starts the 6 passes. Pass 1 shows the scheduler setting and the due tasks.
3. The learner types the total and chooses overruns or fits, then submits.
4. The sim reveals the total, draws the pass on the timeline, marks any deferred task, and shows the Why text.
5. After pass 6, the sim shows the score. The learner should notice that passes 4 and 5 hold the same tasks and differ only in the scheduler.

**Feedback:** 6 passes, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The total is <Total> ms and it <overruns or fits>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The timeline shows the three always-due tasks (audio, buttons, spectrum) with the scheduler off, and the question "How much of the 40 ms is left?"

**Chapter Anchors:** The chapter states the task costs in the table "The Time Budget in Numbers"; that a typical pass is 19.0 ms and the worst scheduled pass is 27.8 ms; that a full-screen redraw makes a pass 148.4 ms; that the slice is about 16.2 ms and a pass with status, network, and the slice would be 40.2 ms; and that the scheduler defers the slice, leaving 24.0 ms.
```

## Related Resources

- [Chapter 18: Testing, Integration, and Capstone Projects](../../chapters/18-testing-integration-capstones/index.md)
