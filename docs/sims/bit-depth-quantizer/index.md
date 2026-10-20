---
title: "Bit Depth Quantizer"
description: "The learner will calculate the number of levels available at a given bit depth, and the smallest bit depth that provides a required number of levels, for 5 challenge questions, with all 5 correct within two attempts each."
status: scaffold
library: p5.js
bloom_level: Apply
---

# Bit Depth Quantizer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 3: Sound and Digital Audio Basics](../../chapters/03-sound-and-digital-audio/index.md).

```text
Type: microsim
**sim-id:** bit-depth-quantizer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the number of levels available at a given bit depth, and the smallest bit depth that provides a required number of levels, for 5 challenge questions, with all 5 correct within two attempts each.

**Prerequisites:** bit depth, levels, quantization error, powers of two (all defined in the section "Bit Depth" above this block).

**Evidence of Mastery:** For each of the 5 challenge questions the learner types a number. An answer is correct when it equals the Answer column in Content exactly. Mastery is 5 of 5 correct, with up to two attempts per question. Moving the bit-depth control and watching the staircase is exploration, not evidence.

**Misconceptions:** (1) Each extra bit adds a fixed number of levels instead of doubling them. (2) A higher bit depth makes the sound's pitch more accurate. (3) 8 bits is half as good as 16 bits.

**Instructional Rationale:** Apply-level calculation of 2 to the power n needs repeated practice with a check. Seeing the staircase get finer as the number of levels doubles gives the learner a mental picture to check the arithmetic against.

**Content:**

The sim draws one cycle of a sine wave and the staircase of its quantized version. The learner chooses the bit depth for exploration: minimum 1, maximum 16, step 1, unit bits, default 4. The sim shows the number of levels for the chosen bit depth after the learner changes it.

Challenge questions, in this order:

| # | Question | Answer | Why (shown as feedback) |
|---|---|---|---|
| 1 | How many levels does 3-bit audio have? | 8 | 2 x 2 x 2 = 8. |
| 2 | How many levels does 8-bit audio have? | 256 | 2 to the power 8 is 256. |
| 3 | How many levels does the Pico's 12-bit ADC have? | 4096 | 2 to the power 12 is 4,096. |
| 4 | How many levels does 16-bit audio have? | 65536 | 2 to the power 16 is 65,536. |
| 5 | What is the smallest bit depth with at least 1,000 levels? | 10 | 2 to the power 9 is 512, which is too few, and 2 to the power 10 is 1,024. |

**Provenance:** The levels follow from the formula levels = 2 to the power n given in the chapter. The 12-bit figure is the RP2350 ADC resolution mentioned in the chapter.

**Rules:** levels = 2 to the power n. The quantized value of a sample x between -1.0 and +1.0 is the nearest of the evenly spaced levels between -1.0 and +1.0, with spacing 2 / (levels - 1). A sample exactly halfway between two levels rounds up. Answers are whole numbers typed without commas.

**Learner Activity:**

1. The learner moves the bit-depth control from 1 to 16 and watches the staircase get finer and the level count double each step.
2. The learner starts the challenges and types an answer to question 1.
3. The sim says whether the answer is correct. After a wrong first answer, the learner may try once more.
4. After a second wrong answer, the sim shows the answer and the Why text, and the question counts as missed.
5. After question 5, the sim shows the score. The learner should notice that adding one bit always doubles the number of levels.

**Feedback:** 5 questions, fixed order, two attempts each. Correct: "Correct: <Why>". First incorrect: "Not quite. Think about doubling for each bit. Try again." Second incorrect: "The answer is <answer>: <Why>". A running score "n of 5" is shown.

**Starting State:** The sine wave and its 4-bit staircase are shown with the text "16 levels" and the question "What happens to the staircase as you add bits?"

**Chapter Anchors:** The chapter states that n bits give 2 to the power n levels, that 16 bits give 65,536 levels, and that each extra bit adds about 6 dB.
```

## Related Resources

- [Chapter 3: Sound and Digital Audio Basics](../../chapters/03-sound-and-digital-audio/index.md)
