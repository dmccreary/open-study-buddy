---
title: "Template Score Explorer"
description: "The learner will calculate the template score of 4 small windows by mean subtraction, unit normalization and a dot product, within 0.02 of the correct value in at least 3 of the 4."
status: scaffold
library: p5.js
bloom_level: Apply
---

# Template Score Explorer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 12: Wake-Word Detection](../../chapters/12-wake-word-detection/index.md).

```text
Type: microsim
**sim-id:** template-score-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the template score of 4 small windows by mean subtraction, unit normalization and a dot product, within 0.02 of the correct value in at least 3 of the 4.

**Prerequisites:** feature, window, mean subtraction, unit normalization, dot product score, template (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 4 challenge windows the learner types a score before the sim reveals it. A score is correct when it is within 0.02 of the Score column in Content. Mastery is 3 of 4 correct on the first attempt. Stepping through the worked window in exploration is exploration, not evidence.

**Misconceptions:** (1) A louder or stronger window scores higher. (2) A steady offset in a band changes the score. (3) A negative score means "no similarity" instead of "the opposite pattern". (4) The order of the frames does not matter.

**Instructional Rationale:** Apply-level calculation needs a procedure with a checkable answer. The windows are small enough (3 frames, 2 bands) to calculate by hand, and four challenges are chosen so that each breaks one of the misconceptions.

**Content:**

All windows have 3 frames and 2 bands. Each frame is written (band 0, band 1). The template is already mean-subtracted and length 1: (-0.5, 0.5), (0, 0), (0.5, -0.5). The sim labels all windows "synthetic".

The worked window, used in exploration: E = (10, 2), (10, 4), (10, 6). Band means 10 and 4. After subtraction: (0, -2), (0, 0), (0, 2). Length 2.83. Dot with the template -2.00. Score -0.71.

| # | Window | Band means | After subtraction | Length | Dot | Score | Why (shown as feedback) |
|---|--------|------------|--------------------|--------|-----|-------|-------------------------|
| 1 | W1: (3, 9), (4, 8), (5, 7) | 4, 8 | (-1, 1), (0, 0), (1, -1) | 2.00 | 2.00 | 1.00 | Subtracting the band means leaves exactly the template's shape, so the angle is 0. |
| 2 | W2: (2, 12), (4, 10), (6, 8) | 4, 10 | (-2, 2), (0, 0), (2, -2) | 4.00 | 4.00 | 1.00 | Twice the strength, same shape: normalizing divides by 4 and gives the template, so strength does not matter. |
| 3 | W3: (5, 7), (4, 8), (3, 9) | 4, 8 | (1, -1), (0, 0), (-1, 1) | 2.00 | -2.00 | -1.00 | The same band movements in the opposite order are the opposite pattern, so the score is -1. |
| 4 | W4: (3, 6), (4, 8), (6, 7) | 4.33, 7 | (-1.33, -1), (-0.33, 1), (1.67, 0) | 2.58 | 1.00 | 0.39 | Only partly the same shape: the dot product is 1.00 but the length is 2.58, so the score is 1.00 / 2.58. |

**Provenance:** Synthetic windows written for this sim; the arithmetic matches the chapter's toy-window sections and was checked with Python.

**Rules:** Band mean = sum of that band's values over the 3 frames, divided by 3. After subtraction = value - band mean. Length = square root of the sum of squares of the 6 subtracted numbers. Dot = sum over the 6 entries of subtracted value times template value. Score = dot divided by length, or 0 if the length is below 0.000001. Scores are shown to 2 decimals and compared with a tolerance of 0.02.

**Learner Activity:**

1. The learner steps through the worked window E in three stages: mean subtraction, normalization, dot product. At each stage the sim shows the numbers. The learner should notice that the band that never moves (band 0 of E) contributes nothing.
2. The learner starts the 4 challenges. Window W1 is shown with the template.
3. The learner types the score and submits.
4. The sim shows the three stages with their numbers and the Why text.
5. After challenge 4, the sim shows the score. The learner should notice that W1 and W2 differ in strength and colouring but score the same, and that W3 has the same numbers as W1 in a different order.

**Feedback:** 4 challenges, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The score is <score>: <Why>". The score is revealed right after each submission, and a running score "n of 4" is shown.

**Starting State:** The worked window E is shown before any stage, with the question "What does this window score against the template?"

**Chapter Anchors:** The chapter states that W1 and W2 score 1.00, W3 scores -1.00, W4 scores 0.39, and that the template is (-0.5, 0.5), (0, 0), (0.5, -0.5).
```

## Related Resources

- [Chapter 12: Wake-Word Detection](../../chapters/12-wake-word-detection/index.md)
