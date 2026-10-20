---
title: "VAD Boundary Finder"
description: "The learner will execute the voice activity detection rules on 5 loudness traces to find each trace's first and last speech frame, matching both frames in at least 4 of 5 traces."
status: scaffold
library: p5.js
bloom_level: Apply
---

# VAD Boundary Finder



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 11: Microphone Calibration and Push-to-Talk](../../chapters/11-mic-calibration-push-to-talk/index.md).

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

## Related Resources

- [Chapter 11: Microphone Calibration and Push-to-Talk](../../chapters/11-mic-calibration-push-to-talk/index.md)
