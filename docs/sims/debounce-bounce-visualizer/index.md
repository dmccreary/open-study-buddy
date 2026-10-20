---
title: "Button Bounce and Debounce Visualizer"
description: "The learner will execute the debounce rule on 6 recorded pin traces by counting the presses accepted at a given debounce time, with at least 5 of 6 correct on the first attempt."
status: scaffold
library: p5.js
bloom_level: Apply
---

# Button Bounce and Debounce Visualizer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 7: Buttons, State Machines, and Device Modes](../../chapters/07-buttons-and-device-modes/index.md).

```text
Type: microsim
**sim-id:** debounce-bounce-visualizer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** execute<br/>
**Learning Objective:** The learner will execute the debounce rule on 6 recorded pin traces by counting the presses accepted at a given debounce time, with at least 5 of 6 correct on the first attempt.

**Prerequisites:** bounce, debounce time, falling edge, `ticks_diff` (all defined in the sections above this block). The debounce rule is shown in the Rules field and on screen throughout.

**Evidence of Mastery:** For each of the 6 items the learner types the number of presses the rule counts for the trace and debounce time shown. An answer is correct when it equals the Presses counted column in Content. Mastery is 5 of 6 on the first attempt. Changing the debounce time in the exploration trace is exploration, not evidence.

**Misconceptions:** (1) Every 0 in the trace is a separate press. (2) A longer debounce time is always safer. (3) Debouncing is only needed when a button is pressed, not when it is released.

**Instructional Rationale:** Apply-level execution of a rule requires the learner to step through data by hand. Seeing both a too-short and a too-long debounce time fail on the same kind of trace makes the learner see the trade-off, rather than memorize a number.

**Content:**

Each trace is the pin value (1 released, 0 down) sampled every 5 ms starting at 0 ms. The traces are listed with the sample number starting at 0.

| Trace | Samples (every 5 ms) | Description |
|---|---|---|
| A | 1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1 | A clean press |
| B | 1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0 | Press with 20 ms of bounce |
| C | 1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,1,1,1,1,1,1,1 | Clean press, then a bouncy release |
| D | 1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1 | Two real presses 40 ms apart |
| E | 1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0 | A noisy switch that chatters for 55 ms |

Items, in this order:

| # | Trace | Debounce time (ms) | Presses counted | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | A | 30 | 1 | A clean press has no bounce, so one press is counted. |
| 2 | B | 0 | 3 | With no debounce every flicker to 0 counts: at 10, 20, and 30 ms. |
| 3 | B | 30 | 1 | The press is accepted at 10 ms and the flicker up to 30 ms is ignored. |
| 4 | D | 100 | 1 | The release at 50 ms is ignored because it is within 100 ms of the press at 10 ms, so the second press is never separate. |
| 5 | E | 30 | 2 | The chatter lasts 55 ms, which is longer than 30 ms, so a later flicker is counted as a second press at 75 ms. |
| 6 | C | 10 | 2 | The bounce on release lasts longer than 10 ms, so the release is accepted and a second press is counted at 90 ms. |

**Provenance:** The traces are illustrative, and the sim labels them "illustrative." The rule is the logic of the debounce in `src/kits/study-buddy-base/03-buttons.py`. The counts were computed by executing the rule on each trace.

**Rules:** The state starts as released with the last accepted change set to a time long before 0 ms. At each sample time t with pin value v: if (v equals 0) differs from the state, and t minus the time of the last accepted change is greater than the debounce time, the state flips and the last accepted change becomes t; a flip to pressed adds 1 to the press count. For exploration the debounce time ranges from 0 to 100 ms in steps of 10 ms, default 30 ms.

**Learner Activity:**

1. The learner explores trace B: changes the debounce time and watches the accepted presses (marked on the trace) change.
2. The learner starts the 6 items. Item 1 shows trace A and the debounce time.
3. The learner types the number of presses and submits.
4. The sim marks each accepted change on the trace and shows the Why text.
5. After item 6, the sim shows the score. The learner should notice that traces D and E break a debounce time that is too long or too short.

**Feedback:** 6 items, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The rule counts <answer>: <Why>". The accepted changes are shown after each submission, and a running score "n of 6" is shown.

**Starting State:** Trace B is shown with a debounce time of 30 ms and the question "How many presses does the rule count?"

**Chapter Anchors:** The chapter states that test 03 uses a 30 ms debounce, that an unfiltered bouncy press can count three times, and that too long a debounce merges quick taps.
```

## Related Resources

- [Chapter 7: Buttons, State Machines, and Device Modes](../../chapters/07-buttons-and-device-modes/index.md)
