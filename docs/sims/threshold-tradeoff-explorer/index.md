---
title: "Threshold Trade-Off Explorer"
description: "The learner will judge which detection threshold, if any, meets stated limits on false rejects and false accepts in 4 scenarios, choosing the correct threshold or 'none' in at least 3 of 4."
status: built
library: p5.js
bloom_level: Evaluate
image: /sims/threshold-tradeoff-explorer/threshold-tradeoff-explorer.png
og:image: /sims/threshold-tradeoff-explorer/threshold-tradeoff-explorer.png
twitter:image: /sims/threshold-tradeoff-explorer/threshold-tradeoff-explorer.png
social:
   cards: false
quality_score: 95
---

# Threshold Trade-Off Explorer

<iframe src="main.html" width="100%" height="562px" scrolling="no"></iframe>

[Run the Threshold Trade-Off Explorer MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/threshold-tradeoff-explorer/main.html" width="100%" height="562px" scrolling="no"></iframe>
```

## Description

Every wake-word detector needs a threshold: a score at or above it wakes the device. Raising the threshold cuts false accepts (other sounds that wake it by mistake) but adds false rejects (real "Hey Pico" phrases it misses). No setting removes both, so choosing a threshold is a judgment against stated limits.

The histograms show 1,000 synthetic "Hey Pico" scores and 1,000 other-sound scores, regenerated in the browser with the same fixed-seed generator as `01-detector-math-test.py`, so the error rates match the chapter's table exactly. The bright bars are the errors at the current threshold. In explore mode you move the threshold. In the quiz you choose the best threshold, or none, for four scenarios.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 4 scenarios / Back to explore**: Switch between the slider and the quiz.
- **Threshold menu and Submit**: Choose a threshold from 0.50 to 0.90, or none. One attempt per scenario.
- **Next scenario / See score**: Move on after the feedback.
- **Threshold slider**: Explore only: 0.50 to 0.90 in steps of 0.05, default 0.70.

## Lesson Plan

### Learning Objective

The learner will judge which detection threshold, if any, meets stated limits on false rejects and false accepts in 4 scenarios, choosing the correct threshold or "none" in at least 3 of 4.

**Bloom's Taxonomy level:** Evaluate (judge)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

detection threshold, score, false accept, false reject, threshold trade-off (all defined in this chapter above the block).

### Activities

1. **Exploration (5 min):** Move the threshold from 0.50 to 0.90 and record both error rates at 0.60, 0.70 and 0.80.
2. **Guided practice (5 min):** For scenario 3, mark every threshold that meets each limit separately, then look for one that meets both.
3. **Assessment (5 min):** Complete all four scenarios. Mastery is 3 of 4 correct on the first attempt.

### Common Misconceptions Addressed

(1) A higher threshold is always safer. (2) There is always a threshold that satisfies both limits. (3) A false-accept rate per attempt is the same as per hour.

### Discussion Questions

1. Is a higher threshold always safer?
2. Why can no threshold satisfy scenario 3, and what would?
3. Why is a false-accept rate per attempt not the same as per hour?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 12</summary>

```text
Type: microsim
**sim-id:** threshold-tradeoff-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Evaluate<br/>
**Bloom Verb:** judge<br/>
**Learning Objective:** The learner will judge which detection threshold, if any, meets stated limits on false rejects and false accepts in 4 scenarios, choosing the correct threshold or "none" in at least 3 of 4.

**Prerequisites:** detection threshold, score, false accept, false reject, threshold trade-off (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 4 scenarios the learner chooses one threshold from the table in Content, or "none", before the sim reveals the answer. A choice is correct when it equals the Answer column. Mastery is 3 of 4 correct on the first attempt. Moving the threshold control and watching the two error rates in exploration is exploration, not evidence.

**Misconceptions:** (1) A higher threshold is always safer. (2) There is always a threshold that satisfies both limits. (3) A false-accept rate per attempt is the same as per hour.

**Instructional Rationale:** Evaluate-level judgment means deciding against criteria, so each scenario states limits and the learner must test candidate thresholds against them. Scenario 3 has no valid answer, which makes the learner judge rather than pick the middle option.

**Content:**

The sim shows two score distributions as histograms: 1,000 scores for "Hey Pico" and 1,000 for other sounds, and a threshold line. All scores are synthetic and labelled "synthetic". For each threshold the sim shows the false-reject percentage (wake scores below the threshold) and the false-accept percentage (other scores at or above it).

| Threshold | False rejects | False accepts |
|-----------|---------------|---------------|
| 0.50 | 0.0% | 16.6% |
| 0.55 | 0.1% | 9.1% |
| 0.60 | 0.8% | 5.3% |
| 0.65 | 3.5% | 2.4% |
| 0.70 | 11.2% | 0.8% |
| 0.75 | 26.2% | 0.5% |
| 0.80 | 49.3% | 0.1% |
| 0.85 | 74.3% | 0.0% |
| 0.90 | 90.1% | 0.0% |

Scenarios, in this order. Among the thresholds that meet every limit, the answer is the one with the smallest sum of the two percentages; if no threshold meets every limit, the answer is "none".

| # | Scenario | Limits | Answer | Why (shown as feedback) |
|---|----------|--------|--------|--------------------------|
| 1 | A quiet bedroom where missing the phrase is annoying | False rejects at most 5% | 0.65 | 0.50 to 0.65 meet the limit; 0.65 has the fewest false accepts of them (2.4%). |
| 2 | A busy classroom where a false wake-up is disruptive | False accepts at most 1% | 0.70 | 0.70 and higher meet the limit; 0.70 has the fewest false rejects of them (11.2%). |
| 3 | A demo that must almost never miss and almost never wake by mistake | False rejects at most 10% and false accepts at most 1% | none | At 0.65 false accepts are 2.4% (too many) and at 0.70 false rejects are 11.2% (too many). No threshold meets both; the detector needs to be better, not retuned. |
| 4 | A shared class device with a patient user | False rejects at most 25% and false accepts at most 1% | 0.70 | 0.70 gives 11.2% and 0.8%. 0.75 has false rejects of 26.2%, which is over the limit. |

**Provenance:** The scores are synthetic: 1,000 "Hey Pico" scores drawn near mean 0.80 with standard deviation 0.08 (capped at 1.0) and 1,000 other scores near mean 0.35 with standard deviation 0.15, from the fixed-seed generator (seed 77) in `src/chapters/12-wake-word-detection/01-detector-math-test.py`. The percentages in the table are that script's output.

**Rules:** False reject = wake score < threshold. False accept = other score >= threshold. The threshold control has the range 0.50 to 0.90, step 0.05, default 0.70, unit score. Percentages are shown to 1 decimal. The scenario answer is chosen as stated in Content.

**Learner Activity:**

1. The learner moves the threshold and watches the two histograms' tails and the two percentages. The learner should notice that the two numbers move in opposite directions.
2. The learner starts the 4 scenarios. Scenario 1 is shown with its limits.
3. The learner chooses a threshold or "none" and submits.
4. The sim marks the threshold on the histograms, shows both percentages at the chosen value and at the answer, and shows the Why text.
5. After scenario 4, the sim shows the score. The learner should notice that scenario 3 cannot be solved by moving the threshold.

**Feedback:** 4 scenarios, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 4" is shown.

**Starting State:** The threshold is at 0.70 with both histograms visible and the question "How many of each error would you accept?"

**Chapter Anchors:** The chapter's trade-off table has the same 9 rows. It states that 0.70 gives 11.2% false rejects and 0.8% false accepts.
```

</details>

## References

1. [False positives and false negatives](https://en.wikipedia.org/wiki/False_positives_and_false_negatives) - Wikipedia - The two kinds of detection error.
2. [Receiver operating characteristic](https://en.wikipedia.org/wiki/Receiver_operating_characteristic) - Wikipedia - The standard picture of a threshold trade-off.
3. [Keyword spotting](https://en.wikipedia.org/wiki/Keyword_spotting) - Wikipedia - Wake-word detection in speech systems.

## Related Resources

- [Chapter 12: Wake-Word Detection](../../chapters/12-wake-word-detection/index.md)
