---
title: "Template Score Explorer"
description: "The learner will calculate the template score of 4 small windows by mean subtraction, unit normalization and a dot product, within 0.02 of the correct value in at least 3 of the 4."
status: built
library: p5.js
bloom_level: Apply
image: /sims/template-score-explorer/template-score-explorer.png
og:image: /sims/template-score-explorer/template-score-explorer.png
twitter:image: /sims/template-score-explorer/template-score-explorer.png
social:
   cards: false
quality_score: 95
---

# Template Score Explorer

<iframe src="main.html" width="100%" height="552px" scrolling="no"></iframe>

[Run the Template Score Explorer MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/template-score-explorer/main.html" width="100%" height="552px" scrolling="no"></iframe>
```

## Description

The wake-word detector compares a window of features with an enrolled template. It first subtracts each band's mean over the window, so a steady offset does not matter; then divides by the length of what is left, so loudness does not matter; and finally takes the dot product with the template, which is already mean-subtracted and length 1. The score runs from -1 (the opposite pattern) to +1 (the same pattern).

This MicroSim uses tiny windows of 3 frames and 2 bands so every number can be checked by hand. In explore mode you step through the worked window E in three stages. In the quiz you calculate the score of four windows, each built to break one misconception. All windows are synthetic.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 4 challenges / Back to explore**: Switch between the worked window and the quiz.
- **Score box and Submit**: Type the score to 2 decimals; within 0.02 counts. One attempt per window.
- **Next challenge / See score**: Move on after the feedback.
- **Next stage / Back to start**: Explore only: reveal the three stages of the worked window.

## Lesson Plan

### Learning Objective

The learner will calculate the template score of 4 small windows by mean subtraction, unit normalization and a dot product, within 0.02 of the correct value in at least 3 of the 4.

**Bloom's Taxonomy level:** Apply (calculate)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

feature, window, mean subtraction, unit normalization, dot product score, template (all defined in this chapter above the block).

### Activities

1. **Exploration (5 min):** Step through window E. After stage 1, explain why band 0 contributes nothing to the score.
2. **Guided practice (5 min):** Before challenge 4, write the two band means as fractions (13/3 and 21/3) to keep the arithmetic exact.
3. **Assessment (5 min):** Complete all four challenges. Mastery is 3 of 4 correct on the first attempt.

### Common Misconceptions Addressed

(1) A louder or stronger window scores higher. (2) A steady offset in a band changes the score. (3) A negative score means "no similarity" instead of "the opposite pattern". (4) The order of the frames does not matter.

### Discussion Questions

1. Why do W1 and W2 score the same even though W2 is twice as strong?
2. What does a score of -1 mean?
3. Why does the order of the frames matter?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 12</summary>

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

</details>

## References

1. [Dot product](https://en.wikipedia.org/wiki/Dot_product) - Wikipedia - The sum of products at the heart of the score.
2. [Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) - Wikipedia - Why dividing by the length makes strength irrelevant.
3. [Template matching](https://en.wikipedia.org/wiki/Template_matching) - Wikipedia - Comparing a signal with a stored pattern.

## Related Resources

- [Chapter 12: Wake-Word Detection](../../chapters/12-wake-word-detection/index.md)
