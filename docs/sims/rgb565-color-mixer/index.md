---
title: "RGB565 Color Mixer"
description: "The learner will calculate the 16-bit RGB565 value for 6 given colors, using the packing rule, with at least 5 of 6 correct within two attempts each."
status: built
library: p5.js
bloom_level: Apply
image: sims/rgb565-color-mixer/rgb565-color-mixer.png
og:image: sims/rgb565-color-mixer/rgb565-color-mixer.png
twitter:image: sims/rgb565-color-mixer/rgb565-color-mixer.png
social:
   cards: false
---

# RGB565 Color Mixer

<iframe src="main.html" width="100%" height="592px" scrolling="no"></iframe>

[Run the RGB565 Color Mixer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

You can include this MicroSim on your website using the following `iframe`:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/rgb565-color-mixer/main.html" width="100%" height="592px" scrolling="no"></iframe>
```

## Description

The round display in the kit stores each pixel in **RGB565**: 5 bits of red,
6 bits of green, and 5 bits of blue packed into one 16-bit number. This mixer
runs the same packing rule as the kit's `color565()` function in
`src/kits/study-buddy-base/lib/gc9b72.py`:

```python
value = (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3
```

For each color strength the sim shows all 8 input bits. The bits that are kept
are outlined in the color's own hue, and the low bits that are dropped are grayed
and struck out. Below them, the 16 packed bits show where each group lands: red
in bits 15 to 11, green in bits 10 to 5, and blue in bits 4 to 0. The sim also
shows the hexadecimal value and the two bytes the driver sends, high byte first.

Two swatches sit side by side. The left one is the full 24-bit color you mixed.
The right one is the color the display can actually show after the low bits are
dropped, so you can see when the difference is visible and when it is not.

## How to Use

1. Drag the **Red**, **Green**, and **Blue** sliders. The swatches, the kept bits,
   the 16-bit value, and the hex value all update together. The sim opens on
   orange (255, 128, 0), which packs to `0xFC00`.
2. Press **Start Challenges**. Each challenge shows a color and its (R, G, B)
   numbers. The sliders lock and the bits are hidden.
3. Type the RGB565 value in hexadecimal (for example `F800` or `0xF800`; upper or
   lower case both work) and press **Check** or the Enter key.
4. If your first answer is wrong, you get one more try. After a second wrong
   answer the sim shows the correct value and why. The bits are revealed after
   each challenge so you can check your work.
5. After challenge 6 the sim shows your score out of 6. Mastery is 5 of 6.
   Press **Try Challenges Again** to repeat, or keep exploring with the sliders.

## Lesson Plan

**Learning objective:** Students will calculate the 16-bit RGB565 value for six
given colors using the packing rule, with at least 5 of 6 correct within two
attempts each (Bloom's Taxonomy: Apply).

**Audience:** High school students building the Open Study Buddy kit (grades 9-12).

**Duration:** 15 to 20 minutes.

**Prerequisites:** pixels, binary and hexadecimal numbers, bit masking and
shifting (Chapter 5 section "RGB565 Color").

### Activities

1. **Warm-up (3 minutes).** With the sim on orange, ask: "Which bits does each
   color keep?" Have students name the kept groups (5, 6, 5) before touching a slider.
2. **Explore (5 minutes).** Students set red to 255 and slowly lower it to 248.
   The 16-bit value does not change. Then go one step lower to 247. Ask them to
   explain why using the struck-out bits.
3. **Green gets the extra bit (2 minutes).** Repeat with green from 255 down to
   252, then 251. Green changes every 4 steps, red and blue every 8.
4. **Challenges (8 minutes).** Students work the six challenges, writing each
   step on paper: mask, shift, combine, convert to hex.

### Discussion Questions

1. Why does RGB565 give green 6 bits instead of red or blue?
2. Gray (110, 110, 110) is not the same 16-bit pattern for each color group.
   Why do the red and blue groups match but green differ?
3. The kit sends `FC 00` for orange. What would go wrong if the driver sent the
   low byte first?
4. How many different colors can RGB565 show, and how many does 24-bit color show?

### Assessment

- The challenge score (target 5 of 6 within two attempts each) is the evidence
  of mastery. Moving the sliders is exploration and is not scored.
- Exit ticket: "Pack cyan (0, 255, 255) into RGB565 and show each step."
  (Answer: `0x07FF`.)

## References

- [Chapter 5: Display Basics: Pixels, Color, and Frame Size](../../chapters/05-display-basics/index.md) - the RGB565 Color section explains the packing rule used here.
- [High color (Wikipedia)](https://en.wikipedia.org/wiki/High_color) - background on 16-bit color formats, including 5-6-5.
- [Bitwise operation (Wikipedia)](https://en.wikipedia.org/wiki/Bitwise_operation) - AND masks and bit shifts.

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
