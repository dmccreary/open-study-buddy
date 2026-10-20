---
title: "Speed-Up Chooser"
description: "The learner will recommend, for 6 scenarios, the simplest implementation whose worst-case pass time fits within the frame budget minus the display reserve, or state that none fits, with at least 5 of 6 correct."
status: built
library: p5.js
bloom_level: Evaluate
image: /sims/speedup-chooser/speedup-chooser.png
og:image: /sims/speedup-chooser/speedup-chooser.png
twitter:image: /sims/speedup-chooser/speedup-chooser.png
social:
   cards: false
quality_score: 95
---

# Speed-Up Chooser

<iframe src="main.html" width="100%" height="557px" scrolling="no"></iframe>

[Run the Speed-Up Chooser MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/speedup-chooser/main.html" width="100%" height="557px" scrolling="no"></iframe>
```

## Description

Faster code is not always better code. Each 40 ms audio frame leaves 30 ms for the audio work after a 10 ms display reserve, and the right implementation is the simplest one whose worst-case pass time fits that limit: plain Python first, then viper, then inline assembly. If even assembly is too slow, the work itself must shrink.

The bar at the top splits one frame into the audio-work limit and the display reserve. Below it, three bars show the worst-case time of each option against the limit (dashed green) and the budget (gray). In explore mode you set the budget, reserve and three times. In the quiz you recommend an option, or None fits, for six scenarios. All times are illustrative, not measurements of the kit.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 6 scenarios / Back to explore**: Switch between the sliders and the quiz.
- **Recommendation menu and Submit**: Choose Plain Python, Viper, Assembly or None fits. One attempt per scenario.
- **Next scenario / See score**: Move on after the feedback.
- **Budget, Reserve, Plain, Viper and Asm sliders**: Explore only: budget 10 to 80 ms (step 5), reserve 0 to 20 ms (step 5), times 1 to 300 ms.

## Lesson Plan

### Learning Objective

The learner will recommend, for 6 scenarios, the simplest implementation whose worst-case pass time fits within the frame budget minus the display reserve, or state that none fits, with at least 5 of 6 correct.

**Bloom's Taxonomy level:** Evaluate (recommend)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

frame budget, display reserve, worst-case pass time, viper code, inline assembly, performance trade-offs (all defined in this chapter above the block).

### Activities

1. **Exploration (5 min):** Starting from scenario 1's numbers, raise the reserve until Viper stops fitting. Note the reserve at which it changes.
2. **Guided practice (5 min):** For each scenario, write limit = budget - reserve first, then check the options from the top down.
3. **Assessment (5 min):** Complete all six scenarios. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) The fastest implementation is always the best choice. (2) An implementation that fits on average fits the deadline. (3) Assembly is always needed for real-time audio.

### Discussion Questions

1. In scenario 2 the fastest option was not the right one. Why?
2. Why does the average pass time not decide whether an option fits?
3. What should you do when no option fits?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 10</summary>

```text
Type: microsim
**sim-id:** speedup-chooser<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Evaluate<br/>
**Bloom Verb:** recommend<br/>
**Learning Objective:** The learner will recommend, for 6 scenarios, the simplest implementation whose worst-case pass time fits within the frame budget minus the display reserve, or state that none fits, with at least 5 of 6 correct.

**Prerequisites:** frame budget, display reserve, worst-case pass time, viper code, inline assembly, performance trade-offs (all defined in this chapter above the block).

**Evidence of Mastery:** For each scenario the learner chooses one of "Plain Python", "Viper", "Assembly", or "None fits" and submits. A choice is correct when it matches the Answer column in Content. Mastery is 5 of 6 correct on the first attempt. Changing the numbers in the exploration panel is exploration, not evidence.

**Misconceptions:** (1) The fastest implementation is always the best choice. (2) An implementation that fits on average fits the deadline. (3) Assembly is always needed for real-time audio.

**Instructional Rationale:** Evaluate-level recommendation requires the learner to apply a stated criterion to evidence and justify the choice. The scenarios put a boundary case (an implementation that fits by exactly zero margin), a case where the simplest option already fits, and a case where nothing fits, so the learner cannot recommend by habit.

**Content:**

The numbers in this activity are **illustrative** and are not measurements of the kit. Each scenario gives the frame budget, the display reserve, and the worst-case pass time of three implementations, all in milliseconds. The complexity order from simplest to hardest is Plain Python, Viper, Assembly. The fitting limit is the budget minus the reserve; an implementation fits when its worst-case time is less than or equal to the limit.

| # | Budget (ms) | Reserve (ms) | Limit (ms) | Plain Python | Viper | Assembly | Answer | Why (shown as feedback) |
|---|---|---|---|---|---|---|---|---|
| 1 | 40 | 10 | 30 | 120 | 6 | 4 | Viper | Plain Python is over the limit; viper and assembly both fit, and viper is the simpler. |
| 2 | 40 | 10 | 30 | 18 | 5 | 3 | Plain Python | Plain Python already fits, so any faster option costs readability for nothing. |
| 3 | 40 | 10 | 30 | 90 | 34 | 12 | Assembly | Viper at 34 ms is over the 30 ms limit; assembly at 12 ms fits. |
| 4 | 40 | 10 | 30 | 200 | 80 | 45 | None fits | Even assembly at 45 ms is over the limit, so the work itself must be reduced. |
| 5 | 20 | 5 | 15 | 60 | 14 | 7 | Viper | Viper at 14 ms is within the 15 ms limit, so assembly is not needed. |
| 6 | 40 | 10 | 30 | 31 | 12 | 9 | Viper | Plain Python at 31 ms is just over the limit of 30 ms; viper at 12 ms fits. |

For exploration the learner sets the budget (10 to 80 ms, step 5, default 40), the reserve (0 to 20 ms, step 5, default 10), and the three times (1 to 300 ms, step 1, defaults 90, 20, 10), and the sim shows which options fit.

**Provenance:** The scenario numbers are illustrative and invented for this activity. The 40 ms budget and 10 ms reserve are the values used in the chapter section "The Real-Time Constraint and the Frame Overrun". The sim labels all times "illustrative, not measured."

**Rules:** limit = budget - reserve. An option fits when its time <= limit. The answer is the first option that fits in the order Plain Python, Viper, Assembly; if none fits the answer is None fits. Budget: min 10, max 80, step 5, default 40, unit ms. Reserve: min 0, max 20, step 5, default 10, unit ms. Times: min 1, max 300, step 1, unit ms.

**Learner Activity:**

1. The learner changes the numbers in the exploration panel and watches which options fit.
2. The learner notices that raising the reserve can make a fitting option stop fitting.
3. The learner starts the 6 scenarios. Scenario 1 is shown.
4. The learner chooses a recommendation and submits.
5. The sim shows the limit, which options fit, the correct answer, and the Why text.

**Feedback:** 6 scenarios, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The exploration panel shows scenario 1's numbers with the limit of 30 ms and the three options marked fits or does not fit, and the question "Which is the simplest option that fits?"

**Chapter Anchors:** The chapter states that the audio work gets 30 ms of the 40 ms frame after a 10 ms display reserve, that the simplest approach that passes timing verification on the worst pass is the right one, and that the numbers in this activity are illustrative.
```

</details>

## References

1. [Maximising MicroPython speed](https://docs.micropython.org/en/latest/reference/speed_python.html) - MicroPython documentation - The native and viper code emitters.
2. [Inline assembler for Thumb2 architectures](https://docs.micropython.org/en/latest/reference/asm_thumb2_index.html) - MicroPython documentation - Writing assembly functions in MicroPython.
3. [Real-time computing](https://en.wikipedia.org/wiki/Real-time_computing) - Wikipedia - Why the worst case, not the average, sets the deadline.

## Related Resources

- [Chapter 10: High-Performance MicroPython](../../chapters/10-high-performance-micropython/index.md)
