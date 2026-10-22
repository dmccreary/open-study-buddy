---
title: "Frame Size and Update Time Calculator"
description: "The learner will calculate the number of bytes in a rectangle of pixels and the time to send it over SPI at a given baud rate, for 6 challenges, with at least 5 of 6 correct."
status: built
library: p5.js
bloom_level: Apply
image: sims/frame-size-calculator/frame-size-calculator.png
og:image: sims/frame-size-calculator/frame-size-calculator.png
twitter:image: sims/frame-size-calculator/frame-size-calculator.png
social:
   cards: false
---

# Frame Size and Update Time Calculator

<iframe src="main.html" width="100%" height="622px" scrolling="no"></iframe>

[Run the Frame Size and Update Time Calculator MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

You can include this MicroSim on your website using the following `iframe`:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/frame-size-calculator/main.html" width="100%" height="622px" scrolling="no"></iframe>
```

## Description

Every picture you send to the kit's 360 by 360 round display is a rectangle of
pixels, and every pixel costs bytes. This calculator turns the two formulas from
Chapter 5 into something you can change and watch:

- **bytes** = width x height x bytes per pixel
- **bits** = bytes x 8
- **time in milliseconds** = bits / baud rate x 1000

The picture on the left shows the 360 by 360 frame with the visible round glass
in black and the corners hidden under the bezel. The orange rectangle is the
part you are sending, drawn at its center. Note that a full frame sends the
hidden corners too, so the time depends on the pixels sent, not on the pixels
you can see.

The time shown is **wire time only**. It leaves out the command bytes that set
the drawing window and the Python overhead between SPI calls, so a real
`display.fill()` takes longer than the number here.

## How to Use

1. Move the **Width** and **Height** sliders (1 to 360 pixels), and choose the
   **Bytes per pixel** (1, 2, or 3) and the **Baud rate** (8, 12, or 24 million
   bits per second). The sim opens on a full frame at 2 bytes per pixel and
   24,000,000 bits per second: 259,200 bytes and 86.40 ms.
2. Press **Start Challenges**. Each challenge sets the controls to match the
   question, locks them, and hides the results.
3. Type a number (no units; commas are fine) and press **Check** or Enter. Byte
   answers must be exact. Time answers must be within 0.1 ms.
4. The sim shows whether you were right, the worked calculation, and the formula
   lines. Press **Next** for the next challenge.
5. After challenge 6 the sim shows your score out of 6. Mastery is 5 of 6.

## Lesson Plan

**Learning objective:** Students will calculate the number of bytes in a
rectangle of pixels and the time to send it over SPI at a given baud rate, for
six challenges, with at least 5 of 6 correct (Bloom's Taxonomy: Apply).

**Audience:** High school students building the Open Study Buddy kit (grades 9-12).

**Duration:** 15 to 20 minutes.

**Prerequisites:** pixels, RGB565, frame size calculation, baud rate (Chapter 5).

### Activities

1. **Predict (3 minutes).** With the default full frame showing, cover the
   result and ask: "How long does it take to send this?" Collect guesses, then
   reveal 86.40 ms.
2. **Explore (5 minutes).** Set the rectangle to the 100 by 30 clock-digit box
   and then to the 200 by 22 level meter from test 06. Compare their times with
   the full frame. How many small boxes could you redraw in the time of one full frame?
3. **Bytes per pixel (2 minutes).** Switch between 1, 2, and 3 bytes per pixel.
   Which setting does the kit use, and what would 3 bytes cost?
4. **Challenges (8 minutes).** Students work the six challenges and write the
   multiplication and division for each one.

### Discussion Questions

1. A 24 MHz SPI clock sends 24 million *bits* per second. How many *bytes* per
   second is that?
2. Why does sending only the part of the screen that changed make an animation
   smoother?
3. The calculator leaves out command bytes and Python overhead. Would the real
   time be longer or shorter, and why?
4. At 12,000,000 bits per second, how many full frames per second could the
   wire carry at most?

### Assessment

- The challenge score (target 5 of 6 on the first attempt) is the evidence of
  mastery. Moving the controls is exploration and is not scored.
- Exit ticket: "How many milliseconds does it take to send a 16 by 32 letter at
  2 bytes per pixel at 24,000,000 bits per second?" (Answer: 1,024 bytes,
  8,192 bits, about 0.34 ms.)

## References

- [Chapter 5: Display Basics: Pixels, Color, and Frame Size](../../chapters/05-display-basics/index.md) - the Frame Size Calculation and Update Bandwidth sections give the formulas used here.
- [Serial Peripheral Interface (Wikipedia)](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface) - how SPI clocks one bit per pulse.
- [Framebuffer (Wikipedia)](https://en.wikipedia.org/wiki/Framebuffer) - why a full frame buffer is costly on a small microcontroller.

## Specification

The full specification below is extracted from
[Chapter 5: Display Basics: Pixels, Color, and Frame Size](../../chapters/05-display-basics/index.md).

```text
Type: microsim
**sim-id:** frame-size-calculator<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the number of bytes in a rectangle of pixels and the time to send it over SPI at a given baud rate, for 6 challenges, with at least 5 of 6 correct.

**Prerequisites:** pixel, RGB565, frame size calculation, baud rate (all defined in the sections above this block). The time formula is given in the Rules field and shown to the learner after the first challenge.

**Evidence of Mastery:** For each of the 6 challenges the learner types one number. An answer is correct when it is within the tolerance in the Content table. Mastery is 5 of 6 correct on the first attempt. Changing the exploration controls and watching the totals is exploration, not evidence.

**Misconceptions:** (1) A pixel is one byte. (2) Sending data at 24 MHz means 24 million bytes per second. (3) Time depends on how many pixels are visible rather than how many are sent.

**Instructional Rationale:** Apply-level calculation of bytes and time needs repetition with immediate checking. Linking each answer to the same two formulas shows the learner that every display question reduces to a multiplication and a division.

**Content:**

For exploration, the learner sets the width (1 to 360, step 1, unit pixels, default 360), the height (1 to 360, step 1, unit pixels, default 360), the bytes per pixel (1, 2, or 3, default 2), and the baud rate (8,000,000, 12,000,000, or 24,000,000 bits per second, default 24,000,000). The sim shows the bytes, the bits, and the time in milliseconds.

Challenges, in this order:

| # | Question | Answer | Tolerance | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | Bytes in a full 360 by 360 frame at 2 bytes per pixel | 259200 | exactly | 360 x 360 x 2 = 259,200. |
| 2 | Bytes in the 100 by 30 clock-digit box at 2 bytes per pixel | 6000 | exactly | 100 x 30 x 2 = 6,000. |
| 3 | Bytes in a full 360 by 360 frame at 3 bytes per pixel | 388800 | exactly | 360 x 360 x 3 = 388,800. |
| 4 | Bytes in the 200 by 22 level meter at 2 bytes per pixel | 8800 | exactly | 200 x 22 x 2 = 8,800. |
| 5 | Milliseconds to send the 100 by 30 box at 24,000,000 bits per second | 2.0 | within 0.1 | 6,000 bytes x 8 = 48,000 bits, divided by 24,000,000 is 0.002 s. |
| 6 | Milliseconds to send a full 2-byte frame at 12,000,000 bits per second | 172.8 | within 0.1 | 259,200 x 8 = 2,073,600 bits, divided by 12,000,000 is 0.1728 s. |

**Provenance:** The sizes come from the chapter sections "Pixels and Coordinates" and "Frame Size Calculation," and the 200 by 22 meter is the `METER_WIDTH` by `METER_HEIGHT` of test 06. The times use the formula in Rules and ignore command overhead.

**Rules:** bytes = width x height x bytes per pixel. bits = bytes x 8. time in seconds = bits / baud rate. Milliseconds = seconds x 1000. The sim does not include command bytes or Python overhead, and says so.

**Learner Activity:**

1. The learner changes the width, height, bytes per pixel, and baud rate, and sees the bytes, bits, and milliseconds update.
2. The learner starts the challenges. Challenge 1 is shown.
3. The learner types a number and submits.
4. The sim shows whether it is correct and the Why text, then moves to the next challenge.
5. After challenge 6, the sim shows the score. The learner should notice that a full frame takes about 86 ms of wire time at 24 MHz with the default settings, while the small box takes about 2 ms. The calculator leaves out Python overhead, and says so.

**Feedback:** 6 challenges, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The calculator shows the full frame at 2 bytes per pixel and 24,000,000 bits per second, with the question "How long does it take to send this?"

**Chapter Anchors:** The chapter states a full frame is 259,200 bytes, a full frame at 24 MHz takes 86.4 ms, the 100 by 30 box is 6,000 bytes, and the 200 by 22 meter is 8,800 bytes.
```
