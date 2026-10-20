---
title: "Button Bounce and Debounce Visualizer"
description: "The learner will execute the debounce rule on 6 recorded pin traces by counting the presses accepted at a given debounce time, with at least 5 of 6 correct on the first attempt."
status: built
library: p5.js
bloom_level: Apply
image: /sims/debounce-bounce-visualizer/debounce-bounce-visualizer.png
og:image: /sims/debounce-bounce-visualizer/debounce-bounce-visualizer.png
twitter:image: /sims/debounce-bounce-visualizer/debounce-bounce-visualizer.png
social:
   cards: false
quality_score: 95
---

# Button Bounce and Debounce Visualizer

<iframe src="main.html" width="100%" height="522px" scrolling="no"></iframe>

[Run the Button Bounce and Debounce Visualizer MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/debounce-bounce-visualizer/main.html" width="100%" height="522px" scrolling="no"></iframe>
```

## Description

A real button does not go cleanly from released (1) to pressed (0): its contacts bounce for a few milliseconds. The debounce rule from test 03 accepts a change only when the pin state differs from the accepted state and more than the debounce time has passed since the last accepted change.

The trace shows the pin sampled every 5 ms. Green lines mark accepted presses, blue lines accepted releases, the gold band after each accepted change is the debounce window, and orange dots are changes the rule ignored. In explore mode you change the debounce time on trace B. In the quiz you count the presses the rule accepts for six trace and debounce-time pairs, then see the accepted changes marked. The traces are illustrative; the rule is the logic in `src/kits/study-buddy-base/03-buttons.py`.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 6 items / Back to explore**: Switch between exploring trace B and the six-item quiz.
- **Answer box and Submit**: Type the number of presses the rule counts and submit (Enter also submits). One attempt per item.
- **Next item / See score**: Move on after the feedback.
- **Debounce time slider**: Explore only: 0 to 100 ms in steps of 10 ms, default 30 ms.

## Lesson Plan

### Learning Objective

The learner will execute the debounce rule on 6 recorded pin traces by counting the presses accepted at a given debounce time, with at least 5 of 6 correct on the first attempt.

**Bloom's Taxonomy level:** Apply (execute)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

bounce, debounce time, falling edge, `ticks_diff` (all defined in the sections above this block). The debounce rule is shown in the Rules field and on screen throughout.

### Activities

1. **Exploration (5 min):** Set the debounce time to 0, 10, 30 and 100 ms on trace B and record how many presses are counted each time.
2. **Guided practice (5 min):** Before item 1, step through trace A sample by sample on paper with a 30 ms debounce, writing down the accepted state and the time of the last accepted change.
3. **Assessment (5 min):** Complete all six items. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) Every 0 in the trace is a separate press. (2) A longer debounce time is always safer. (3) Debouncing is only needed when a button is pressed, not when it is released.

### Discussion Questions

1. Item 4 used 100 ms and item 5 used 30 ms. Which was too long and which was too short?
2. Why does the rule need debouncing on release as well as on press (item 6)?
3. What debounce time would count trace D as two presses and trace E as one?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 7</summary>

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

</details>

## References

1. [Switch: contact bounce](https://en.wikipedia.org/wiki/Switch#Contact_bounce) - Wikipedia - Why mechanical contacts bounce and the common fixes.
2. [time: time related functions (ticks_ms, ticks_diff)](https://docs.micropython.org/en/latest/library/time.html) - MicroPython documentation - The wrap-safe timing functions the debounce rule uses.
3. [Signal edge](https://en.wikipedia.org/wiki/Signal_edge) - Wikipedia - Rising and falling edges, the moments the rule reacts to.

## Related Resources

- [Chapter 7: Buttons, State Machines, and Device Modes](../../chapters/07-buttons-and-device-modes/index.md)
