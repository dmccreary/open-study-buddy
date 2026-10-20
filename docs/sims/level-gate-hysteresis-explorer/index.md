---
title: "Level Gate Hysteresis Explorer"
description: "The learner will calculate how many times a single-threshold gate and a hysteresis gate change state on 3 loudness traces, matching the correct counts in 5 of 6 answers."
status: built
library: p5.js
bloom_level: Apply
image: /sims/level-gate-hysteresis-explorer/level-gate-hysteresis-explorer.png
og:image: /sims/level-gate-hysteresis-explorer/level-gate-hysteresis-explorer.png
twitter:image: /sims/level-gate-hysteresis-explorer/level-gate-hysteresis-explorer.png
social:
   cards: false
quality_score: 95
---

# Level Gate Hysteresis Explorer

<iframe src="main.html" width="100%" height="587px" scrolling="no"></iframe>

[Run the Level Gate Hysteresis Explorer MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/level-gate-hysteresis-explorer/main.html" width="100%" height="587px" scrolling="no"></iframe>
```

## Description

A level gate decides frame by frame whether the microphone hears speech. A single threshold opens at 15.0 bits and closes the moment the level dips back under it, so a voice that wobbles around the line makes the gate flutter. A hysteresis gate opens at the open level but closes only below a lower close level, so small dips inside a phrase do not close it.

The plot shows a 20-frame loudness trace with the open and close levels as dashed lines. Below it, one row of cells shows when the single-threshold gate is open and another shows the hysteresis gate, with each state change marked and counted. In explore mode you pick a trace and move both levels. In the quiz you count the state changes of both gates on three traces before the rows are revealed. The traces are synthetic; trace A is the wobble trace from `09-calibration-selftest.py`.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 3 challenges / Back to explore**: Switch between exploring and the quiz.
- **Single changes and Hysteresis changes boxes, Submit**: Type both counts and submit. One attempt per challenge, two answers each.
- **Next challenge / See score**: Move on after the feedback.
- **Trace menu, Open and Close sliders**: Explore only: traces A to C; open 13.0 to 18.0 bits and close 12.0 to 18.0 bits in steps of 0.1 (close is kept at or below open).

## Lesson Plan

### Learning Objective

The learner will calculate how many times a single-threshold gate and a hysteresis gate change state on 3 loudness traces, matching the correct counts in 5 of 6 answers.

**Bloom's Taxonomy level:** Apply (calculate)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

loudness in bits, frame, speech floor gate, level gate, hysteresis (all defined in this chapter above the block).

### Activities

1. **Exploration (5 min):** On trace A, raise the close level until it equals the open level and watch the hysteresis row become the single-threshold row.
2. **Guided practice (5 min):** For challenge 1, write each frame's state for both gates in two rows on paper before counting the changes.
3. **Assessment (5 min):** Complete all three challenges. Mastery is 5 of the 6 counts correct on the first attempt.

### Common Misconceptions Addressed

(1) Hysteresis makes a gate less sensitive to speech. (2) Hysteresis removes every false opening. (3) The gate closes at the same level that it opens at.

### Discussion Questions

1. Does hysteresis make the gate less sensitive to speech? What does it change?
2. Why did hysteresis not help in challenge 3?
3. Why does the gate open with >= and close with < ?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 11</summary>

```text
Type: microsim
**sim-id:** level-gate-hysteresis-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate how many times a single-threshold gate and a hysteresis gate change state on 3 loudness traces, matching the correct counts in 5 of 6 answers.

**Prerequisites:** loudness in bits, frame, speech floor gate, level gate, hysteresis (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 3 challenge traces, the learner types two whole numbers before the sim reveals them: the number of state changes of the single-threshold gate, and the number of state changes of the hysteresis gate. A state change is any frame whose open/closed state differs from the frame before it (the state before frame 0 counts as closed). An answer is correct when it equals the value in the Content table. Mastery is 5 of 6 answers correct on the first attempt. Moving the threshold controls in exploration is exploration, not evidence.

**Misconceptions:** (1) Hysteresis makes a gate less sensitive to speech. (2) Hysteresis removes every false opening. (3) The gate closes at the same level that it opens at.

**Instructional Rationale:** Apply-level calculation needs a procedure the learner can run and check, so the learner traces the two gates frame by frame in their head, commits two counts, and only then sees the sim's trace. Challenge 3 is built so that hysteresis does not help, which exposes misconception 2.

**Content:**

The sim shows one loudness trace of 20 frames at a time, as a line of bits against frame number, with the open level and the close level drawn as two horizontal lines. Loudness values are in bits. All 3 traces are synthetic and the sim labels them "synthetic".

| Frame | Trace A | Trace B | Trace C |
|-------|---------|---------|---------|
| 0 | 14.8 | 13.0 | 13.0 |
| 1 | 15.1 | 13.1 | 13.4 |
| 2 | 14.9 | 15.6 | 14.2 |
| 3 | 15.2 | 16.8 | 13.6 |
| 4 | 14.7 | 17.2 | 14.9 |
| 5 | 15.0 | 14.8 | 13.2 |
| 6 | 14.9 | 16.9 | 15.1 |
| 7 | 15.3 | 17.4 | 13.3 |
| 8 | 14.6 | 15.2 | 14.7 |
| 9 | 15.1 | 14.6 | 13.1 |
| 10 | 15.4 | 16.5 | 14.4 |
| 11 | 15.6 | 17.0 | 13.2 |
| 12 | 15.2 | 16.2 | 14.8 |
| 13 | 14.9 | 14.4 | 13.0 |
| 14 | 15.1 | 13.2 | 13.3 |
| 15 | 14.8 | 13.0 | 13.1 |
| 16 | 14.2 | 13.1 | 13.0 |
| 17 | 13.4 | 12.9 | 13.2 |
| 18 | 13.2 | 13.0 | 13.1 |
| 19 | 13.5 | 13.1 | 13.0 |

| # | Trace | Open level | Close level | Single-threshold changes | Hysteresis changes | Why (shown as feedback) |
|---|-------|------------|-------------|--------------------------|--------------------|-------------------------|
| 1 | A | 15.0 | 14.5 | 12 | 2 | The level crosses 15.0 twelve times, but it never falls below 14.5 until frame 16, so the gate opens at frame 1 and closes at frame 16. |
| 2 | B | 15.0 | 14.5 | 6 | 2 | Dips to 14.8 and 14.6 inside the phrase flip the single threshold, but they stay above 14.5. The gate opens at frame 2 and closes at frame 13, when 14.4 is below 14.5. |
| 3 | C | 14.5 | 14.0 | 8 | 8 | Each spike (14.9, 15.1, 14.7, 14.8) rises over 14.5 and then falls to 13.6 or lower, below the close level, so both gates open and close four times. Hysteresis helps only with wobble near the line. |

**Provenance:** Trace A is the wobble trace in `09-calibration-selftest.py` and the chapter table above. Traces B and C are synthetic, written for this sim. The change counts were computed with `levels.LevelGate` in `src/chapters/11-mic-calibration-push-to-talk/levels.py`.

**Rules:** The single-threshold gate is open when bits >= open level. The hysteresis gate starts closed, opens when bits >= open level, and closes when bits < close level. Exploration range for the open level: 13.0 to 18.0 bits, step 0.1, default 15.0. For the close level: 12.0 to 18.0 bits, step 0.1, default 14.5, and never above the open level. A change in the open level moves the close level down if needed to keep close <= open. The 3 challenge settings in the table override the controls.

**Learner Activity:**

1. The learner chooses a trace and moves the open and close levels. The sim shades the frames where each gate is open and shows both change counts. The learner should notice that raising the close level toward the open level makes the hysteresis gate behave like the single threshold.
2. The learner starts the 3 challenges. For challenge 1 the sim shows trace A and the two levels but hides both gates.
3. The learner types the two counts and submits.
4. The sim shades both gates, shows the counts, and shows the Why text.
5. After challenge 3, the sim shows the score and the learner should notice that a spike that falls all the way back to the floor flips both gates.

**Feedback:** 3 challenges, fixed order, one attempt each, 2 answers per challenge, 6 answers in all. Correct: "Correct: <Why>". Incorrect: "Not quite. The counts are <single> and <hysteresis>: <Why>". The counts are revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** Trace A is shown with the open level at 15.0 and the close level at 14.5, both gates shaded, and the question "Which gate flutters?"

**Chapter Anchors:** The chapter states that the single threshold flips 12 times and the gate flips twice on trace A (open at frame 1, close at frame 16), that the gate opens with `>=` and closes with `<`, and that hysteresis does not remove spikes that fall back to the floor.
```

</details>

## References

1. [Hysteresis](https://en.wikipedia.org/wiki/Hysteresis) - Wikipedia - Why two thresholds stop a switch from chattering.
2. [Schmitt trigger](https://en.wikipedia.org/wiki/Schmitt_trigger) - Wikipedia - The electronic circuit that uses the same open and close idea.
3. [Noise gate](https://en.wikipedia.org/wiki/Noise_gate) - Wikipedia - Audio gates with separate open and close levels.

## Related Resources

- [Chapter 11: Microphone Calibration and Push-to-Talk](../../chapters/11-mic-calibration-push-to-talk/index.md)
