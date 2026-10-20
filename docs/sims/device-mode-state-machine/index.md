---
title: "Device Mode State Machine"
description: "The learner will use the device's state transition table to find the final mode and the final volume after 6 sequences of button events, with at least 5 of 6 correct on the first attempt."
status: scaffold
library: p5.js
bloom_level: Apply
---

# Device Mode State Machine



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 7: Buttons, State Machines, and Device Modes](../../chapters/07-buttons-and-device-modes/index.md).

```text
Type: microsim
**sim-id:** device-mode-state-machine<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/automating-instructional-design/tree/main/docs/sims/state-machine-template<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** use<br/>
**Learning Objective:** The learner will use the device's state transition table to find the final mode and the final volume after 6 sequences of button events, with at least 5 of 6 correct on the first attempt.

**Prerequisites:** device mode, state, event, transition, short press, long press, volume clamping (all defined in the sections above this block, with the table in the section "The State Machine").

**Evidence of Mastery:** For each of the 6 sequences the learner picks the final mode from the five modes and the final volume from the values 30, 40, 50, and 60. An answer is correct when both match the Final mode and Final volume columns in Content. Mastery is 5 of 6 on the first attempt. Stepping through the example sequence in exploration is exploration, not evidence.

**Misconceptions:** (1) A button does the same thing in every mode. (2) Releasing MODE always sends the recording to the server. (3) A long press of UP in CLOCK also changes the volume.

**Instructional Rationale:** Apply-level use of a table requires the learner to carry the state forward one event at a time. Keeping volume as a second answer makes the learner track more than one thing, as a real state machine does.

**Content:**

The sim starts every sequence in CLOCK with a volume of 40. The transition table is the one in the chapter section "The State Machine." The volume changes by 10 for each volume-up or volume-down step, between 0 and 100.

Sequences, in this order:

| # | Event sequence shown | Final mode | Final volume | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | MODE pressed; MODE released after 1.5 s | THINKING | 40 | The hold is at least 0.2 s, so releasing sends the question and waits for the reply. |
| 2 | MODE pressed; MODE released after 0.1 s | CLOCK | 40 | The hold is under 0.2 s, so it was a bump, and the device returns to the clock. |
| 3 | MODE pressed; MODE released after 1.5 s; reply arrives | SPEAKING | 40 | A reply in THINKING moves the device to SPEAKING. |
| 4 | UP held for 1 s (a long press); DOWN pressed; MODE pressed and released after 0.1 s | SETTINGS | 30 | The long press of UP opens SETTINGS, DOWN lowers the value of the first setting (volume) by 10, and a short MODE press only moves to the next setting. |
| 5 | MODE pressed; MODE released after 1.5 s; MODE pressed again | CLOCK | 40 | A MODE press in THINKING cancels and returns to the clock. |
| 6 | UP pressed and released after 0.1 s; UP pressed and released after 0.1 s | CLOCK | 60 | Each short UP press in CLOCK raises the volume by 10, from 40 to 50 to 60. |

**Provenance:** The table and rules come from the chapter section "The State Machine." The sequences are illustrative, and the sim labels them "illustrative."

**Rules:** The mode changes only as the transition table says. Volume is limited to the range 0 to 100 and changes in steps of 10. A long press is 800 ms or more. In SETTINGS the first setting is Volume. A mode is unchanged by an event the table lists as "ignored."

**Learner Activity:**

1. The learner explores a sample sequence and steps through it, watching the mode highlight on a diagram of the five modes and the volume number change.
2. The learner starts the 6 sequences. Sequence 1 is shown as a list of events.
3. The learner picks a final mode and a final volume, then submits.
4. The sim replays the sequence on the diagram, showing the mode after each event, and shows the Why text.
5. After sequence 6, the sim shows the score. The learner should notice that the same button has different effects in CLOCK, THINKING, and SETTINGS.

**Feedback:** 6 sequences, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The device ends in <mode> at volume <volume>: <Why>". The replay is shown after every submission, and a running score "n of 6" is shown.

**Starting State:** The five modes are shown with CLOCK highlighted and volume 40, with the first sequence and the question "Where does the device end up?"

**Chapter Anchors:** The chapter states that the device has five modes (CLOCK, LISTENING, THINKING, SPEAKING, SETTINGS), that a long press is 800 ms or more, that a hold shorter than 0.2 s returns to CLOCK, and that the volume starts at 40 and moves in steps of 10 between 0 and 100.
```

## Related Resources

- [Chapter 7: Buttons, State Machines, and Device Modes](../../chapters/07-buttons-and-device-modes/index.md)
