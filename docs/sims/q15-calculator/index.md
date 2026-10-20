---
title: "Q15 Calculator"
description: "The learner will calculate the Q15 product (a x b) >> 15 of 6 pairs of Q15 integers, and state whether the result fits in 16 bits, with at least 5 of 6 correct."
status: scaffold
library: p5.js
bloom_level: Apply
---

# Q15 Calculator



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 10: High-Performance MicroPython](../../chapters/10-high-performance-micropython/index.md).

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

## Related Resources

- [Chapter 10: High-Performance MicroPython](../../chapters/10-high-performance-micropython/index.md)
