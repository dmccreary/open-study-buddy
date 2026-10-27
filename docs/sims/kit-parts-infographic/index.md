---
title: "Kit Parts Infographic"
description: "A labeled picture of the five base-kit parts. Click a part to learn its job, then match five described jobs to the right part."
status: built
library: html
bloom_level: Remember
image: sims/kit-parts-infographic/kit-parts-infographic.png
og:image: sims/kit-parts-infographic/kit-parts-infographic.png
twitter:image: sims/kit-parts-infographic/kit-parts-infographic.png
social:
   cards: false
---

# Kit Parts Infographic

<iframe src="main.html" width="100%" height="542px" scrolling="no"></iframe>

[Run the Kit Parts Infographic MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

You can include this MicroSim on your website using the following `iframe`:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/kit-parts-infographic/main.html" width="100%" height="542px" scrolling="no"></iframe>
```

## Description

The Open Study Buddy base kit has five parts, and each one has a single clear
job. This infographic shows them as a labeled picture: the Raspberry Pi Pico 2 W,
the 360 by 360 round display, the INMP441 microphone, the MAX98357A amplifier
with its speaker, and the Mode, Up, and Down buttons.

Select any part to read its job. When you feel ready, start the check: five job
statements appear one at a time, and you pick the part that does each job. The
check is built to catch three common mix-ups: thinking the Pico itself has the
microphone and speaker, thinking the amplifier makes sound without a speaker,
and thinking the buttons are wired to the display.

## How to Use

1. Click (or tab to and press Enter on) any part in the picture. Its name and
   job appear in the panel below.
2. Press **Start the Check**. Job statement 1 appears with the five parts as
   buttons, always in the same order. During the check, the picture no longer
   shows descriptions.
3. Pick one part. The sim tells you whether you were right, outlines the correct
   part in green (and your pick in orange if it was wrong), and explains why.
4. Press **Next** for the next job. After job 5 the sim shows your score out
   of 5. Mastery is 4 of 5 on the first attempt.
5. Press **Retake the Check** to try again, or **Back to Explore** to review.

## Lesson Plan

**Learning objective:** Students will identify which of the five kit parts
performs each of five described jobs, with at least 4 of 5 correct on the first
attempt (Bloom's Taxonomy: Remember).

**Audience:** High school students starting the Open Study Buddy kit (grades 9-12).

**Duration:** 5 to 10 minutes.

**Prerequisites:** the table "The Kit Bill of Materials" in Chapter 4.

### Activities

1. **Explore (3 minutes).** Students select each part and say its job aloud in
   one word: brain, face, ear, voice, hands.
2. **Check (3 minutes).** Students take the check without looking back at the
   chapter table.
3. **Hands on (optional, 5 minutes).** With the real kit on the desk, students
   point to each physical board as a partner reads the job statements.

### Discussion Questions

1. The Pico runs every program. Why does the kit still need a separate board to
   turn sound into numbers?
2. What would you hear if the amplifier were wired up but the speaker were missing?
3. The buttons do not connect to the display. How does pressing MODE change what
   the screen shows?

### Assessment

- The check score (target 4 of 5 on the first attempt) is the evidence of
  mastery. Selecting parts beforehand is exploration and is not scored.
- Exit ticket: "Name the part that turns digital audio into power for the speaker."

## References

- [Chapter 4: The Pico Kit Hardware and Wiring](../../chapters/04-pico-kit-hardware/index.md) - the section "The Kit Bill of Materials" lists the five parts and their jobs.
- [Raspberry Pi Pico 2 W documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) - the board that runs the kit's MicroPython.
- [Bill of materials (Wikipedia)](https://en.wikipedia.org/wiki/Bill_of_materials) - what a parts list is and why projects keep one.

## Specification

The full specification below is extracted from
[Chapter 4: The Pico Kit Hardware and Wiring](../../chapters/04-pico-kit-hardware/index.md).

```text
Type: infographic
**sim-id:** kit-parts-infographic<br/>
**Library:** html<br/>
**Status:** Specified<br/>
**Bloom Level:** Remember<br/>
**Bloom Verb:** identify<br/>
**Learning Objective:** The learner will identify which of the five kit parts performs each of 5 described jobs, with at least 4 of 5 correct on the first attempt.

**Prerequisites:** the five parts and their one-line jobs, listed in the table "The Kit Bill of Materials" above this block.

**Evidence of Mastery:** The learner is shown 5 job statements one at a time and picks the matching part from the five. A pick is correct when it matches the Correct part column in Content. Mastery is 4 of 5 on the first attempt. Selecting a part to read its description beforehand is exploration, not evidence.

**Misconceptions:** (1) The Pico itself contains the microphone and speaker. (2) The amplifier makes the sound by itself. (3) The buttons are wired to the display.

**Instructional Rationale:** A Remember-level objective asks the learner to recall a fact accurately. Reading a labeled picture first, then answering a job question from memory, gives both a cue to learn from and a retrieval attempt that strengthens recall.

**Content:**

The infographic shows the five parts as a labeled picture. Selecting a part reveals its name and description.

| Part | Description shown on selection |
|---|---|
| Raspberry Pi Pico 2 W | The brain. It runs your MicroPython program and connects to Wi-Fi. |
| Round display | The face. A 360 by 360 color screen that shows text, shapes, and meters. |
| INMP441 microphone | The ear. It senses sound and sends 24-bit digital numbers to the Pico. |
| MAX98357A amplifier and speaker | The voice. The amplifier turns digital audio into power for the speaker. |
| Mode, Up, and Down buttons | The hands. Three switches you press to change modes, settings, and to talk. |

Job statements, in this order:

| # | Job statement shown to the learner | Correct part | Why (shown as feedback) |
|---|---|---|---|
| 1 | Turns room sound into digital numbers. | INMP441 microphone | The converter is built into the microphone board. |
| 2 | Runs the MicroPython program. | Raspberry Pi Pico 2 W | The Pico is the only part that runs your code. |
| 3 | Drives the speaker from digital audio. | MAX98357A amplifier and speaker | The amplifier takes I2S audio and powers the speaker. |
| 4 | Shows a level meter and text. | Round display | The display draws what the Pico tells it to draw. |
| 5 | Lets the student start push-to-talk. | Mode, Up, and Down buttons | A held button is read as a signal on a Pico pin. |

**Provenance:** The parts and jobs come from the chapter section "The Kit Bill of Materials."

**Rules:** Each job statement has exactly one correct part. The five parts are always offered together, in a fixed order.

**Learner Activity:**

1. The learner selects any part to read its description.
2. The learner starts the check. Job statement 1 is shown with the five parts as choices.
3. The learner picks one part.
4. The sim shows whether it was correct and the Why text, then moves to the next statement.
5. After statement 5, the sim shows the score.

**Feedback:** 5 statements, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. This is the job of the <correct part>: <Why>". The correct part is revealed right after each pick, and a running score "n of 5" is shown.

**Starting State:** The five parts are shown labeled and unselected, with the instruction "Select a part to learn its job."

**Chapter Anchors:** The chapter names the five parts as the Pico 2 W, the round display, the microphone, the amplifier with a speaker, and the three buttons.
```
