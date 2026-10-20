---
title: "RGB565 Color Mixer"
description: "The learner will calculate the 16-bit RGB565 value for 6 given colors, using the packing rule, with at least 5 of 6 correct within two attempts each."
status: scaffold
library: p5.js
bloom_level: Apply
---

# RGB565 Color Mixer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 5: Display Basics: Pixels, Color, and Frame Size](../../chapters/05-display-basics/index.md).

```text
Type: microsim
**sim-id:** rgb565-color-mixer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/learning-python/tree/main/docs/sims/rgb-color-mixer<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the 16-bit RGB565 value for 6 given colors, using the packing rule, with at least 5 of 6 correct within two attempts each.

**Prerequisites:** pixel, RGB565, bit masking and shifting (all defined in the section "RGB565 Color" above this block).

**Evidence of Mastery:** For each of the 6 colors the learner types the RGB565 value in hexadecimal. An answer is correct when it equals the RGB565 value column in Content, ignoring upper or lower case and a leading "0x". Mastery is 5 of 6 correct, with up to two attempts per color. Moving the exploration sliders and watching the bits is exploration, not evidence.

**Misconceptions:** (1) RGB565 stores 8 bits per color. (2) The extra bit goes to blue. (3) The low bits of each color are kept and the high bits are dropped.

**Instructional Rationale:** Apply-level calculation of a bit-packed value needs the learner to follow the masking and shifting rule step by step. Seeing the 16 bits change with the three color strengths gives the learner a way to check the arithmetic.

**Content:**

For exploration, the learner sets red, green, and blue strengths from 0 to 255 in steps of 1 (unit: none, default 255, 128, 0). The sim shows the color, the three kept bit groups (5, 6, and 5 bits), and the 16-bit value in binary and hexadecimal.

Challenge colors, in this order:

| # | Color | (R, G, B) | RGB565 value | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | Red | (255, 0, 0) | F800 | Red keeps its top 5 bits (11111) in the top of the number. |
| 2 | Green | (0, 255, 0) | 07E0 | Green keeps its top 6 bits (111111) in the middle. |
| 3 | Blue | (0, 0, 255) | 001F | Blue keeps its top 5 bits (11111) in the bottom. |
| 4 | Yellow | (255, 255, 0) | FFE0 | Red 11111 and green 111111 together make FFE0. |
| 5 | Orange | (255, 128, 0) | FC00 | Green 128 keeps 100000, so the green bits are 0x0400 and red is 0xF800. |
| 6 | Gray | (110, 110, 110) | 6B6D | Red 01101, green 011011, and blue 01101 pack to 0110101101101101. |

**Provenance:** The packing rule is `color565` from `src/kits/study-buddy-base/lib/gc9b72.py`. The values in the table were computed with that function.

**Rules:** value = ((R AND 0xF8) shifted left 8) OR ((G AND 0xFC) shifted left 3) OR (B shifted right 3), with R, G, and B whole numbers from 0 to 255. The result is a number from 0 to 65535 shown as four hexadecimal digits.

**Learner Activity:**

1. The learner drags the red, green, and blue controls and sees the color, the kept bit groups, and the 16-bit value update together.
2. The learner starts the challenges. Challenge 1 shows the color and its (R, G, B) numbers.
3. The learner types the RGB565 value in hexadecimal and submits.
4. If it is wrong the first time, the learner may try once more. After a second wrong answer the sim shows the correct value and the Why text.
5. After challenge 6, the sim shows the score. The learner should notice that the 16-bit value only changes when a color crosses a multiple of 8 (or of 4 for green).

**Feedback:** 6 challenges, fixed order, two attempts each. Correct: "Correct: <Why>". First incorrect: "Not quite. Check which bits each color keeps (5, 6, 5). Try again." Second incorrect: "The value is <answer>: <Why>". A running score "n of 6" is shown.

**Starting State:** The mixer shows orange (255, 128, 0) with its bits, and the question "Which bits does each color keep?"

**Chapter Anchors:** The chapter states that RGB565 uses 5, 6, and 5 bits, has 65,536 colors, and that orange (255, 128, 0) is 0xFC00.
```

## Related Resources

- [Chapter 5: Display Basics: Pixels, Color, and Frame Size](../../chapters/05-display-basics/index.md)
