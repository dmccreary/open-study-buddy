---
title: "Audio Frame Time Budget Explorer"
description: "The learner will examine 6 loop timings against the 40 ms frame budget to decide whether each keeps up with the microphone and, for those that do not, calculate the time until the first audio is lost, to within 0.1 s."
status: scaffold
library: p5.js
bloom_level: Analyze
---

# Audio Frame Time Budget Explorer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 8: I2S Audio: Recording and Playing Sound](../../chapters/08-i2s-audio/index.md).

```text
Type: microsim
**sim-id:** audio-frame-budget-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** examine<br/>
**Learning Objective:** The learner will examine 6 loop timings against the 40 ms frame budget to decide whether each keeps up with the microphone and, for those that do not, calculate the time until the first audio is lost, to within 0.1 s.

**Prerequisites:** audio frame, ring buffer, frame time budget, backlog (all defined in the sections above this block). The model is stated in the Rules field and shown on screen.

**Evidence of Mastery:** For each of the 6 timings the learner types the seconds until the first sample is lost, or "never". An answer is correct when it equals "never" where the Answer column says never, or is within 0.1 s of the number in the Answer column. Mastery is 5 of 6 correct on the first attempt. Changing the exploration slider and watching the backlog is exploration, not evidence.

**Misconceptions:** (1) A loop that takes slightly longer than the frame is fine because the buffer is big. (2) A loop that is faster than the frame wastes audio. (3) The ring holds all the audio forever.

**Instructional Rationale:** Analyze-level examination requires the learner to relate parts of the system (the producer, the ring, the consumer) and reason about how a small rate difference accumulates. Using the same formula on six timings lets the learner see which one is the borderline case and why.

**Content:**

The model: one audio frame is 2,048 bytes and arrives every 40 ms. The ring holds 9.765625 frames (the depth measured in `03-ring-latency.py`, equal to 40,000 bytes at 8 bytes per sample time: 5,000 sample times, or 0.390625 s). Each pass of the loop takes P milliseconds of work and then reads one frame. If the loop is faster than 40 ms, it waits for the frame.

| # | Time per pass P (ms) | Answer | Why (shown as feedback) |
|---|---|---|---|
| 1 | 30 | never | The loop is faster than 40 ms, so it waits for each frame and the backlog stays at zero. |
| 2 | 40 | never | The loop exactly matches the audio rate, so there is no growth. |
| 3 | 45 | 3.56 | Growth 0.125 frames per pass, so it passes 9.77 frames on pass 79, and 79 x 45 ms = 3.56 s. |
| 4 | 50 | 2.0 | Growth 0.25 frames per pass, so it passes 9.77 on pass 40, and 40 x 50 ms = 2.0 s. |
| 5 | 60 | 1.2 | Growth 0.5 frames per pass, so it passes 9.77 on pass 20, and 20 x 60 ms = 1.2 s. |
| 6 | 130 | 0.65 | Growth 2.25 frames per pass, so it passes 9.77 on pass 5, and 5 x 130 ms = 0.65 s. |

For exploration the learner sets P from 10 to 100 ms in steps of 0.1 ms, default 40.0 ms. The sim shows the backlog in frames growing against the capacity of 9.765625 frames.

**Provenance:** The frame size and ring size are the values in `src/kits/study-buddy-base/config.py` (`FFT_SIZE`, `MIC_SAMPLE_RATE`, `MIC_BUFFER_BYTES`). The ring depth of 9.765625 frames comes from a measurement on the test board at 50 ms per pass (the delay stopped growing near 460 ms), and its cause is not confirmed. The model is a simplification, and the sim labels it "model, based on one board's measurement." The 130 ms value is the measured full-screen update time from Chapter 5.

**Rules:** Let T be the larger of P and 40 ms. The backlog after n passes is n x (T / 40 - 1) frames. The first sample is lost at the first whole number n for which the backlog is greater than 9.765625, and the time is n x T. If T equals 40, nothing is ever lost. Times are shown in seconds to two decimal places.

**Learner Activity:**

1. The learner moves the slider and watches the backlog line rise or stay flat against the capacity line.
2. The learner starts the 6 timings. Timing 1 is shown.
3. The learner types the seconds until the first loss, or "never," and submits.
4. The sim draws the backlog line for that timing and shows the Why text.
5. After timing 6, the sim shows the score. The learner should notice that a loop only 5 ms too slow still loses audio within 3.6 seconds.

**Feedback:** 6 timings, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The slider is at 40.0 ms with the backlog flat at zero, and the question "How long can this loop run before audio is lost?"

**Chapter Anchors:** The chapter states that a frame is 512 samples, 2,048 bytes, and 40 ms; that the microphone ring was created with 40,000 bytes but measured about 9.8 frames (0.4 s) deep; and that a 50 ms pass loses audio after about 2.0 s while a 130 ms pass loses it after about 0.65 s.
```

## Related Resources

- [Chapter 8: I2S Audio: Recording and Playing Sound](../../chapters/08-i2s-audio/index.md)
