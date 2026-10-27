---
title: "VAD Boundary Finder"
description: "Run the four-state voice activity detector on loudness traces and find the first and last speech frames of each recording."
status: built
library: p5.js
bloom_level: Apply
image: /sims/vad-boundary-finder/vad-boundary-finder.png
og:image: /sims/vad-boundary-finder/vad-boundary-finder.png
twitter:image: /sims/vad-boundary-finder/vad-boundary-finder.png
social:
   cards: false
quality_score: 95
---

# VAD Boundary Finder

<iframe src="main.html" width="100%" height="637px" scrolling="no"></iframe>

[Run the VAD Boundary Finder MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/vad-boundary-finder/main.html" width="100%" height="637px" scrolling="no"></iframe>
```

## Description

Voice activity detection finds where speech starts and ends inside a push-to-talk recording. The chapter's VAD is a four-state machine (SILENCE, STARTING, SPEECH, ENDING) driven by the hysteresis gate: 3 loud frames in a row start speech, 15 quiet frames in a row end it. The start is the first loud frame of that run and the end is the last loud frame, and the device keeps 4 frames of pre-roll and 5 of hang-over around them.

The bar chart shows each frame's loudness colored loud or quiet, with the gate levels drawn. Stepping processes one frame at a time while the state machine highlights the current state and shows the loud and quiet counts; the start, end and kept range appear as they are found. In explore mode you can also change START_FRAMES and END_FRAMES. In the quiz you find the start and end frames, or none, for five synthetic traces.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 5 traces / Back to explore**: Switch between exploring and the quiz.
- **Start frame and End frame boxes, Submit**: Type two frame numbers, or none in both boxes. One attempt per trace.
- **Next trace / See score**: Move on after the feedback.
- **Step, Back to start, Run to end**: Step through the frames (in the quiz, after submitting).
- **START and END sliders**: Explore only: START_FRAMES 1 to 6, END_FRAMES 5 to 30.

## Lesson Plan

### Learning Objective

The learner will execute the voice activity detection rules on 5 loudness traces to find each trace's first and last speech frame, matching both frames in at least 4 of 5 traces.

**Bloom's Taxonomy level:** Apply (execute)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

loudness in bits, frame, level gate, hysteresis, voice activity detection, start frames, end frames, state machine (all defined in this chapter above the block).

### Activities

1. **Exploration (5 min):** Step through trace 1 and note the frame at which the start is signaled and the frame at which the end is signaled.
2. **Guided practice (5 min):** For trace 5, write the length of every loud and quiet run before deciding whether the pause ends the speech.
3. **Assessment (5 min):** Complete all five traces. Mastery is 4 of 5 traces fully correct on the first attempt.

### Common Misconceptions Addressed

(1) Speech starts at the frame where the VAD signals "start". (2) Any loud frame starts speech. (3) Any quiet frame ends speech. (4) A trace that is still loud at its last frame has no end.

### Discussion Questions

1. Why is the start reported earlier than the frame at which it is signaled?
2. Why does a single loud click never start speech?
3. What is the end of a trace that is still loud at its last frame?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 11</summary>

```text
Type: microsim
**sim-id:** vad-boundary-finder<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** execute<br/>
**Learning Objective:** The learner will execute the voice activity detection rules on 5 loudness traces to find each trace's first and last speech frame, matching both frames in at least 4 of 5 traces.

**Prerequisites:** loudness in bits, frame, level gate, hysteresis, voice activity detection, start frames, end frames, state machine (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 5 traces, the learner types the start frame (the index of the first loud frame of the run that started the speech) and the end frame (the index of the last loud frame of the speech), or "none" when the VAD finds no speech, before the sim reveals them. A trace is correct when both entries equal the Start and End columns in Content. Mastery is 4 of 5 traces correct on the first attempt. Stepping through the example trace in exploration is exploration, not evidence.

**Misconceptions:** (1) Speech starts at the frame where the VAD signals "start". (2) Any loud frame starts speech. (3) Any quiet frame ends speech. (4) A trace that is still loud at its last frame has no end.

**Instructional Rationale:** Apply-level execution needs the learner to run the rules on data and get a checkable answer, so the learner counts runs of loud and quiet frames before the sim steps the state machine. The five traces each break one misconception.

**Content:**

The sim uses these fixed rules: the gate opens at 15.0 bits (bits >= 15.0) and closes below 14.5 bits (bits < 14.5); START_FRAMES is 3; END_FRAMES is 15; pre-roll is 4 frames; hang-over is 5 frames. Each trace is written as runs of "count at level", in order. Frames are numbered from 0. All 5 traces are synthetic, and the sim labels them "synthetic".

| # | Trace (frames at bits) | Total frames | Start | End | Kept frames (first to last) | Why (shown as feedback) |
|---|------------------------|--------------|-------|-----|-----------------------------|-------------------------|
| 1 | 5 at 13.0, 8 at 17.0, 6 at 13.0, 8 at 17.0, 20 at 13.0 | 47 | 5 | 26 | 1 to 31 | The 6 quiet frames in the middle are fewer than 15, so the two words are one utterance. The last loud frame is 26 (5 + 8 + 6 + 8 - 1), and the first is 5. |
| 2 | 10 at 13.0, 1 at 18.0, 30 at 13.0 | 41 | none | none | none | One loud frame is fewer than 3 in a row, so the click never starts speech. |
| 3 | 6 at 13.0, 2 at 17.0, 1 at 13.0, 2 at 17.0, 1 at 13.0, 2 at 17.0, 30 at 13.0 | 44 | none | none | none | Each loud run is 2 frames and a quiet frame resets the count, so the count never reaches 3. |
| 4 | 8 at 13.0, 40 at 17.0 | 48 | 8 | 47 | 4 to 47 | The speech is still going when the trace ends, so the end is the last loud frame, 47. The kept range stops at the last frame of the recording. |
| 5 | 3 at 13.0, 10 at 17.0, 14 at 13.0, 10 at 17.0, 25 at 13.0 | 62 | 3 | 36 | 0 to 41 | A pause of 14 frames is one short of 15, so it does not end the speech. The pre-roll would start at frame -1, so it stops at frame 0. |

The kept frames are computed as: first kept frame = max(0, start - 4); last kept frame = min(total - 1, end + 5).

The state machine has 4 states, SILENCE, STARTING, SPEECH, and ENDING, with the transitions given in the chapter table; the sim draws it and highlights the current state in the stepping mode. For each frame stepped, the sim shows the frame's bits, whether the gate is open, the loud count, the quiet count, and the state.

**Provenance:** The rules are those in `src/chapters/11-mic-calibration-push-to-talk/vad.py` and `levels.py`. The Start, End, and Kept columns were computed by running `vad.VAD` and `vad.boundaries` on the traces. The traces are synthetic.

**Rules:** Loud means the hysteresis gate is open after processing the frame. Start = the index of the first frame of the run of loud frames that reaches 3 in a row. End = the index of the last frame at which the gate was open, taken when 15 quiet frames in a row have been counted, or at the end of the trace if the speech is still going. A quiet frame while counting loud frames resets the loud count to 0. A loud frame while counting quiet frames resets the quiet count to 0. Exploration controls: START_FRAMES 1 to 6, step 1, default 3, unit frames; END_FRAMES 5 to 30, step 1, default 15, unit frames. The challenge answers use the defaults.

**Learner Activity:**

1. The learner steps through trace 1 one frame at a time and watches the state, the counts, and the gate. The learner should notice that the start is signaled 2 frames after the speech began and the end 15 frames after it finished.
2. The learner starts the 5 traces. Trace 1 is shown as a plot of bits against frame number with the gate levels drawn, and the state machine is hidden.
3. The learner types the start and end frames, or "none", and submits.
4. The sim steps through the trace, shows the state machine, the kept range, and the Why text.
5. After trace 5, the sim shows the score. The learner should notice that traces 1 and 5 differ only in whether the pause is under or over 15 frames in the rule.

**Feedback:** 5 traces, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. Start <start>, end <end>: <Why>". The answers are revealed right after each submission, and a running score "n of 5" is shown.

**Starting State:** Trace 1 is shown stopped at frame 0 with the question "Where does the speech start and where does it end?"

**Chapter Anchors:** The chapter states that START_FRAMES is 3 (120 ms), END_FRAMES is 15 (600 ms), the pre-roll is 4 frames, and the hang-over is 5 frames; that the start is signaled 2 frames after the first loud frame; that the end is reported at the last loud frame; and that a click and a 240 ms pause do not break an utterance.
```

</details>

## References

1. [Voice activity detection](https://en.wikipedia.org/wiki/Voice_activity_detection) - Wikipedia - What a VAD does and where it is used.
2. [Finite-state machine](https://en.wikipedia.org/wiki/Finite-state_machine) - Wikipedia - The four-state machine behind the rules.
3. [Hysteresis](https://en.wikipedia.org/wiki/Hysteresis) - Wikipedia - Why the gate uses separate open and close levels.

## Related Resources

- [Chapter 11: Microphone Calibration and Push-to-Talk](../../chapters/11-mic-calibration-push-to-talk/index.md)
