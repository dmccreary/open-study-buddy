---
title: "Retry and Backoff Timeline Explorer"
description: "The learner will calculate the longest time a request can take under 8 retry settings, to within 0.05 s, with at least 7 of 8 correct."
status: built
library: p5.js
bloom_level: Apply
image: /sims/retry-backoff-explorer/retry-backoff-explorer.png
og:image: /sims/retry-backoff-explorer/retry-backoff-explorer.png
twitter:image: /sims/retry-backoff-explorer/retry-backoff-explorer.png
social:
   cards: false
quality_score: 95
---

# Retry and Backoff Timeline Explorer

<iframe src="main.html" width="100%" height="577px" scrolling="no"></iframe>

[Run the Retry and Backoff Timeline Explorer MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/retry-backoff-explorer/main.html" width="100%" height="577px" scrolling="no"></iframe>
```

## Description

When the network fails, the Pico retries with exponential backoff: each wait ceiling doubles from a base until it reaches a cap, and there is no wait after the last attempt. The worst case, every attempt timing out and every wait taking its full ceiling, is N x T plus the sum of the N - 1 ceilings. With full jitter each real wait is a random number up to its ceiling, so a jittered run is never longer than the worst case.

The timeline draws each attempt and each wait as a block, with the total marked. In explore mode you set the base, cap, number of attempts and timeout, and can draw one random jittered run below. In the quiz you calculate the worst-case total for eight settings. The defaults are the chapter's `backoff.py` values; the other settings are illustrative.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 8 settings / Back to explore**: Switch between the sliders and the quiz.
- **Seconds box and Submit**: Type the worst-case total; within 0.05 s counts. One attempt per setting.
- **Next setting / See score**: Move on after the feedback.
- **One random run**: Draw one jittered run below the worst case (a new run each time it is turned on).
- **Base, Cap, Attempts N, Timeout T sliders**: Explore only: base 100 to 1,000 ms, cap 800 to 8,000 ms, N 1 to 7, T 1 to 8 s.

## Lesson Plan

### Learning Objective

The learner will calculate the longest time a request can take under 8 retry settings, to within 0.05 s, with at least 7 of 8 correct.

**Bloom's Taxonomy level:** Apply (calculate)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

timeout, retry, exponential backoff, ceiling, attempt (all defined in this chapter above this block).

### Activities

1. **Exploration (5 min):** From the defaults, raise N from 4 to 7 and watch where the cap starts making the waits equal.
2. **Guided practice (5 min):** For setting 3, list the four wait ceilings before adding them to 5 x 3 s.
3. **Assessment (5 min):** Complete all eight settings. Mastery is 7 of 8 correct on the first attempt.

### Common Misconceptions Addressed

(1) The wait doubles for ever. (2) The last attempt is followed by a wait. (3) Jitter makes the worst case longer. (4) The waits are the only time a retry costs.

### Discussion Questions

1. Does the wait keep doubling for ever?
2. Why is there no wait after the last attempt?
3. Can jitter make the worst case longer?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 14</summary>

```text
Type: microsim
**sim-id:** retry-backoff-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the longest time a request can take under 8 retry settings, to within 0.05 s, with at least 7 of 8 correct.

**Prerequisites:** timeout, retry, exponential backoff, ceiling, attempt (all defined in this chapter above this block).

**Evidence of Mastery:** For each of the 8 settings the learner types the worst-case total time in seconds. An answer is correct when it is within 0.05 s of the number in the Answer column. Mastery is 7 of 8 correct on the first attempt. Dragging the explorer's controls and watching the timeline is exploration, not evidence.

**Misconceptions:** (1) The wait doubles for ever. (2) The last attempt is followed by a wait. (3) Jitter makes the worst case longer. (4) The waits are the only time a retry costs.

**Instructional Rationale:** Apply-level calculation requires the learner to carry out the worst-case formula on new numbers. Seeing the same attempts laid out on a timeline, with the waits and the timeouts as separate segments, shows what each term in the formula stands for and why the last attempt has no wait after it.

**Content:**

The model: a request makes up to N attempts. Every attempt fails by timing out after T seconds. After each failed attempt except the last, the device waits. The wait after failed attempt k (k = 0 for the first) has a ceiling of \( \min(\text{cap}, \text{base} \times 2^k) \). The worst case is every attempt timing out and every wait taking its full ceiling, so the worst-case total is \( N \times T + \sum_{k=0}^{N-2} \min(\text{cap}, \text{base} \times 2^k) \). With jitter, each actual wait is a random number from 0 up to its ceiling, and never above it.

| # | Base (ms) | Cap (ms) | Attempts N | Timeout T (s) | Answer (s) | Why (shown as feedback) |
|---|---|---|---|---|---|---|
| 1 | 500 | 8,000 | 4 | 8 | 35.5 | 4 x 8 = 32 s of timeouts, plus waits of 0.5 + 1 + 2 = 3.5 s. |
| 2 | 500 | 8,000 | 3 | 5 | 16.5 | 3 x 5 = 15 s, plus waits of 0.5 + 1 = 1.5 s. |
| 3 | 1,000 | 4,000 | 5 | 3 | 26 | 5 x 3 = 15 s, plus waits of 1 + 2 + 4 + 4 = 11 s: the fourth wait would be 8 s but is capped at 4 s. |
| 4 | 500 | 2,000 | 4 | 2 | 11.5 | 4 x 2 = 8 s, plus waits of 0.5 + 1 + 2 = 3.5 s. |
| 5 | 250 | 8,000 | 6 | 4 | 31.75 | 6 x 4 = 24 s, plus waits of 0.25 + 0.5 + 1 + 2 + 4 = 7.75 s. |
| 6 | 500 | 8,000 | 1 | 8 | 8 | One attempt has no retry and no wait. |
| 7 | 500 | 8,000 | 7 | 8 | 79.5 | 7 x 8 = 56 s, plus waits of 0.5 + 1 + 2 + 4 + 8 + 8 = 23.5 s (the sixth would be 16 s but is capped at 8 s). |
| 8 | 100 | 800 | 4 | 1 | 4.7 | 4 x 1 = 4 s, plus waits of 0.1 + 0.2 + 0.4 = 0.7 s. |

For exploration the learner sets the base from 100 to 1,000 ms in steps of 50 (default 500), the cap from 800 to 8,000 ms in steps of 200 (default 8,000), N from 1 to 7 in steps of 1 (default 4), and T from 1 to 8 s in steps of 1 (default 8), and sees the timeline of attempts and waits with the worst-case total. A switch shows one random jittered run beneath the worst case, labeled "one random run."

**Provenance:** The formula and the default values (500 ms, 8,000 ms, 4 attempts, 8 s) are the chapter's `backoff.py` and `buddy_config.py` settings, and the default row matches `02-backoff-table.py`, which prints 35.5 s. The other settings are illustrative, and the sim labels them "illustrative."

**Rules:** Ceiling of the wait after failed attempt k is \( \min(\text{cap}, \text{base} \times 2^k) \) in milliseconds. There is no wait after the last attempt. Worst-case total in seconds is \( N \times T + (\text{sum of the } N - 1 \text{ ceilings}) / 1000 \). A jittered wait is a whole number of milliseconds from 0 to its ceiling. For N = 1 there are no waits.

**Learner Activity:**

1. The learner drags the four controls and watches the timeline lengthen or shorten.
2. The learner turns on the "one random run" switch and sees that the jittered run is never longer than the worst case.
3. The learner starts the 8 settings. Setting 1 is shown.
4. The learner types the worst-case total in seconds and submits.
5. The sim draws that setting's timeline and shows the Why text.
6. After setting 8, the sim shows the score. The learner should notice that in settings 3 and 7 the cap makes later waits equal, and that setting 6 has no waits at all.

**Feedback:** 8 settings, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The worst case is <answer> s: <Why>". The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** The default setting (500 ms, 8,000 ms, 4 attempts, 8 s) is drawn as a timeline with the question "What is the longest this request can take?"

**Chapter Anchors:** The chapter states that with a base of 500 ms, a cap of 8,000 ms, 4 attempts and an 8 s timeout the longest a request can take is 35.5 s; that the ceilings of the first six retries are 500, 1,000, 2,000, 4,000, 8,000 and 8,000 ms; and that with full jitter each wait is a random number from 0 to its ceiling.
```

</details>

## References

1. [Exponential backoff](https://en.wikipedia.org/wiki/Exponential_backoff) - Wikipedia - Doubling waits between retries.
2. [Timeout (computing)](https://en.wikipedia.org/wiki/Timeout_(computing)) - Wikipedia - Why every network call needs one.
3. [Jitter](https://en.wikipedia.org/wiki/Jitter) - Wikipedia - Random variation in timing.

## Related Resources

- [Chapter 14: Streaming Speech, Security, and Network Resilience](../../chapters/14-streaming-security-resilience/index.md)
