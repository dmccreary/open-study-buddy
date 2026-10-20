---
title: "Q15 Calculator"
description: "The learner will calculate the Q15 product (a x b) >> 15 of 6 pairs of Q15 integers, and state whether the result fits in 16 bits, with at least 5 of 6 correct."
status: built
library: p5.js
bloom_level: Apply
image: /sims/q15-calculator/q15-calculator.png
og:image: /sims/q15-calculator/q15-calculator.png
twitter:image: /sims/q15-calculator/q15-calculator.png
social:
   cards: false
quality_score: 95
---

# Q15 Calculator

<iframe src="main.html" width="100%" height="532px" scrolling="no"></iframe>

[Run the Q15 Calculator MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/q15-calculator/main.html" width="100%" height="532px" scrolling="no"></iframe>
```

## Description

Q15 stores a number from -1.0 up to just under +1.0 as a 16-bit integer q that stands for q / 32,768, so 16,384 is 0.5. Multiplying two Q15 numbers gives a 30-bit product that must be shifted right by 15 bits to return to Q15: result = (a x b) >> 15. The shift keeps the sign and rounds toward minus infinity, and one product (-1.0 x -1.0) does not fit back into 16 bits.

The calculator shows the full product, the shifted result, the real values each integer stands for, whether the result fits, and a number line from -1 to +1. In explore mode you type any two Q15 integers. In the quiz you compute six products from the chapter's table; for pair 6 you also say whether the result fits in 16 bits.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 6 pairs / Back to explore**: Switch between the calculator and the quiz.
- **Result box, fit menu (pair 6) and Submit**: Type the whole-number result; for pair 6 also choose whether it fits. One attempt per pair.
- **Next pair / See score**: Move on after the feedback.
- **a and b boxes**: Explore only: any whole numbers from -32,768 to 32,767 (out-of-range values are clamped).

## Lesson Plan

### Learning Objective

The learner will calculate the Q15 product (a x b) >> 15 of 6 pairs of Q15 integers, and state whether the result fits in 16 bits, with at least 5 of 6 correct.

**Bloom's Taxonomy level:** Apply (calculate)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

fixed-point math, Q15 format, arithmetic shift right (all defined in this chapter above the block).

### Activities

1. **Exploration (5 min):** Try 32767 x 32767 and then -32768 x -32768. One fits in 16 bits and one does not.
2. **Guided practice (5 min):** For pair 5 (-3 x 3), write -9 / 32,768 as a decimal and decide which whole number is below it before submitting.
3. **Assessment (5 min):** Complete all six pairs. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) The product of two Q15 numbers is already Q15. (2) A shift right always rounds toward zero. (3) Q15 can hold exactly 1.0.

### Discussion Questions

1. Is the product of two Q15 numbers already a Q15 number?
2. Why is (-3 x 3) >> 15 equal to -1 and not 0?
3. Why can Q15 hold -1.0 but not +1.0?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 10</summary>

```text
Type: microsim
**sim-id:** q15-calculator<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the Q15 product (a x b) >> 15 of 6 pairs of Q15 integers, and state whether the result fits in 16 bits, with at least 5 of 6 correct.

**Prerequisites:** fixed-point math, Q15 format, arithmetic shift right (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 6 pairs the learner types the whole-number result and submits. A result is correct when it equals the Answer column in Content. For pair 6 the learner must also choose "Fits in 16 bits" or "Does not fit", and the pair counts as correct only when both are right. Mastery is 5 of 6 correct on the first attempt. Using the exploration calculator is exploration, not evidence.

**Misconceptions:** (1) The product of two Q15 numbers is already Q15. (2) A shift right always rounds toward zero. (3) Q15 can hold exactly 1.0.

**Instructional Rationale:** Apply-level calculation needs practice on cases that differ in kind: a normal product, a vanishing product, a negative rounding case, and an overflow. Committing a number before the result is shown makes the learner carry out the shift, not recognize it.

**Content:**

The sim shows the formula result = (a x b) >> 15, where >> is an arithmetic shift right that keeps the sign and rounds toward minus infinity. A 16-bit signed Q15 number fits when it is from -32768 to 32767.

| # | a | b | Answer | Fits in 16 bits? | Why (shown as feedback) |
|---|---|---|---|---|---|
| 1 | 16384 | 16384 | 8192 | yes | 16384 x 16384 = 268,435,456, and 268,435,456 >> 15 = 8192. |
| 2 | 32767 | 32767 | 32766 | yes | 32767 x 32767 = 1,073,676,289, and >> 15 gives 32766. |
| 3 | -16384 | 16384 | -8192 | yes | The product -268,435,456 >> 15 is -8192. |
| 4 | 3 | 3 | 0 | yes | 3 x 3 = 9, and 9 >> 15 is 0: the result is smaller than one Q15 step. |
| 5 | -3 | 3 | -1 | yes | -9 >> 15 rounds toward minus infinity, giving -1, not 0. |
| 6 | -32768 | -32768 | 32768 | no | The product is +1,073,741,824, and >> 15 gives 32768, one more than the largest 16-bit value. |

For exploration the learner enters any two Q15 integers from -32768 to 32767 (step 1, default 16384 and 16384) and sees the full product, the shifted result, the real values (integer / 32768) and whether the result fits.

**Provenance:** The six pairs are the rows of the table in the chapter section "Fixed-Point Math", produced by `src/chapters/10-high-performance-micropython/08-q15-fixed-point.py`.

**Rules:** result = floor(a x b / 32768). real value = integer / 32768. A result fits in 16 bits when -32768 <= result <= 32767. Inputs: min -32768, max 32767, step 1, unit none (Q15 integer).

**Learner Activity:**

1. The learner enters pairs in the exploration calculator and watches the full product and the shifted result.
2. The learner tries 32767 x 32767 and -32768 x -32768 and notices that one fits and the other does not.
3. The learner starts the 6 pairs. Pair 1 is shown.
4. The learner types the result (and, for pair 6, the fit choice) and submits.
5. The sim shows the correct answer and the Why text.

**Feedback:** 6 pairs, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The exploration calculator shows 16384 x 16384 = 8192 with the real values 0.5 x 0.5 = 0.25, and the question "What do you get when you multiply two Q15 numbers?"

**Chapter Anchors:** The chapter states that 16384 stands for 0.5, that 16384 x 16384 >> 15 is 8192, that 3 x 3 >> 15 is 0, and that -32768 x -32768 >> 15 is 32768, which does not fit in 16 bits.
```

</details>

## References

1. [Q (number format)](https://en.wikipedia.org/wiki/Q_(number_format)) - Wikipedia - The Qm.n notation and Q15 multiplication.
2. [Fixed-point arithmetic](https://en.wikipedia.org/wiki/Fixed-point_arithmetic) - Wikipedia - Why fixed point avoids float allocation.
3. [Arithmetic shift](https://en.wikipedia.org/wiki/Arithmetic_shift) - Wikipedia - Why >> rounds toward minus infinity for negative numbers.

## Related Resources

- [Chapter 10: High-Performance MicroPython](../../chapters/10-high-performance-micropython/index.md)
