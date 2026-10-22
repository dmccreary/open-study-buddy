---
title: "Pull-Up Button Circuit"
description: "The learner will infer the value a GPIO input pin reads for 6 button circuits, given the pin's pull setting, what the button's other leg connects to, and whether the button is pressed, with at least 5 of 6 correct."
status: built
library: p5.js
bloom_level: Understand
image: sims/pull-up-button-circuit/pull-up-button-circuit.png
og:image: sims/pull-up-button-circuit/pull-up-button-circuit.png
twitter:image: sims/pull-up-button-circuit/pull-up-button-circuit.png
social:
   cards: false
---

# Pull-Up Button Circuit

<iframe src="main.html" width="100%" height="562px" scrolling="no"></iframe>

[Run the Pull-Up Button Circuit MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

You can include this MicroSim on your website using the following `iframe`:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/pull-up-button-circuit/main.html" width="100%" height="562px" scrolling="no"></iframe>
```

## Description

A Pico input pin reads whatever voltage reaches it, and a button only connects
two wires while it is pressed. This MicroSim draws the circuit as a schematic:
the Pico's input pin with an optional internal pull resistor inside the chip,
and a push button outside whose other leg goes to GND or to 3V3. A box on the
left shows what the pin reads: 1, 0, or a value that keeps changing.

The rule the sim teaches is the one from the chapter section "The Pull-Up
Resistor": **a connected path through a pressed button beats the weak internal
pull.** With the button released, the pin reads the pull's level. With no pull
at all, the pin floats and reads unpredictably, which the sim shows as a value
flipping between 0 and 1. After the reading is revealed, the path that decides
it is drawn in orange.

The six challenge circuits are illustrative. The reality check at the end uses
the real measurement from the book's test board: on GP16 and GP17, a pull-down
kept reading 1 after the pin had been driven high, while pull-ups read 1 every time.

## How to Use

1. The sim opens on the sample circuit (pull-up, other leg to GND, button
   released), reading 1. Predict what the pin will read when the button is
   pressed, then press **Press Button** to check. Press it again to release.
2. Press **Start Challenges**. Each circuit shows its pull setting, where the
   other leg goes, and whether the button is pressed. The reading is hidden.
3. Pick **reads 1**, **reads 0**, or **unpredictable**. The sim reveals the
   reading, the winning path, and the reason. Press **Next**.
4. After circuit 6 the sim shows your score out of 6 (mastery is 5 of 6).
   Press **Reality Check** for the unscored question about the test board, and
   pick the sentence A or B that explains why the kit uses pull-ups.
5. Press **Back to Sample** at any time to return to the sample circuit.

## Lesson Plan

**Learning objective:** Students will infer the value a GPIO input pin reads for
six button circuits, given the pin's pull setting, what the button's other leg
connects to, and whether the button is pressed, with at least 5 of 6 correct
(Bloom's Taxonomy: Understand).

**Audience:** High school students wiring the Open Study Buddy buttons (grades 9-12).

**Duration:** 10 to 15 minutes.

**Prerequisites:** push button, pull-up resistor, floating pin, GPIO input
(Chapter 4 and Chapter 2).

### Activities

1. **Predict, then press (3 minutes).** On the sample circuit, students write
   down what the pin will read when the button is pressed before they press it.
2. **Challenges (6 minutes).** Students state the rule they used for each
   circuit in one sentence before picking an answer.
3. **Spot the dead button (2 minutes).** After the score appears, ask which
   circuit is the wiring mistake that makes a button seem dead (circuit 4).
4. **Reality check (3 minutes).** Discuss the test-board readings and why the kit
   chose pull-ups. If boards are available, run
   `src/chapters/04-pico-kit-hardware/03-floating-pin-demo.py`.

### Discussion Questions

1. Why is the internal pull resistor called "weak"? What would happen if it
   were a plain wire instead?
2. A floating pin on the test board happened to read 0. Why is that still not safe to rely on?
3. In circuit 4 the button is wired to 3V3 with a pull-up. What does the
   program see when you press it, and why does that look like a broken button?
4. If you needed a pull-down on the Pico 2 W, what two fixes does the chapter suggest?

### Assessment

- The challenge score (target 5 of 6 on the first attempt) is the evidence of
  mastery. Pressing the sample button is exploration and is not scored.
- Exit ticket: "A pin has a pull-up and the button's other leg is on GND. What
  does the pin read when the button is released, and when it is pressed?"

## References

- [Chapter 4: The Pico Kit Hardware and Wiring](../../chapters/04-pico-kit-hardware/index.md) - the sections "The Push Button" and "The Pull-Up Resistor" explain the rule and the test-board measurement.
- [Pull-up resistor (Wikipedia)](https://en.wikipedia.org/wiki/Pull-up_resistor) - how pull-up and pull-down resistors give an input a definite value.
- [RP2350 datasheet (Raspberry Pi)](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) - the chip's GPIO pads, pulls, and errata.

## Specification

The full specification below is extracted from
[Chapter 4: The Pico Kit Hardware and Wiring](../../chapters/04-pico-kit-hardware/index.md).

```text
Type: microsim
**sim-id:** pull-up-button-circuit<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** infer<br/>
**Learning Objective:** The learner will infer the value a GPIO input pin reads for 6 button circuits, given the pin's pull setting, what the button's other leg connects to, and whether the button is pressed, with at least 5 of 6 correct.

**Prerequisites:** push button, pull-up resistor, floating pin, GPIO input (all defined in the sections above this block and in Chapter 2).

**Evidence of Mastery:** For each of the 6 circuits the learner commits to "reads 1", "reads 0", or "unpredictable" before the result is shown. A prediction is correct when it matches the Pin reads column in Content. Mastery is 5 of 6 on the first attempt. Pressing the button in the example circuit and watching the reading is exploration, not evidence.

**Misconceptions:** (1) A button always reads 1 when pressed. (2) A pin with nothing attached reads 0. (3) The pull-up is what makes the pin read 1 even while the button is pressed to ground. (4) A pull-down always pulls the pin to 0, even after the pin has been high.

**Instructional Rationale:** An Understand-level inference needs the learner to reason from a circuit's parts to a result. Predicting before the result is shown makes the learner apply the rule that a connected path wins over a pull.

**Content:**

The circuit shows a Pico input pin, an optional internal pull, and a button whose other leg connects to GND or to 3V3.

| # | Pin pull setting | Button's other leg connects to | Button | Pin reads | Why (shown as feedback) |
|---|---|---|---|---|---|
| 1 | Pull-up | GND | Released | 1 | Nothing pulls the pin down, so the pull-up holds it at 1. |
| 2 | Pull-up | GND | Pressed | 0 | The button connects the pin to GND, which beats the weak pull-up. |
| 3 | None (floating) | GND | Released | unpredictable | With no pull and no connection, the pin picks up stray signals. |
| 4 | Pull-up | 3V3 | Pressed | 1 | Both the pull-up and the button push the pin toward 3.3 V. |
| 5 | Pull-down | 3V3 | Pressed | 1 | The button connects the pin to 3V3, which beats the weak pull-down. |
| 6 | Pull-down (pin was low before) | 3V3 | Released | 0 | Nothing pulls the pin up, so the pull-down holds it at 0, as long as the pin was low before. |

**Provenance:** The reasoning rule comes from the chapter section "The Pull-Up Resistor." The six circuits are illustrative, and the sim labels them "illustrative." The reality check after circuit 6 comes from the measurement on GP16 and GP17 in the same section.

**Rules:** A connection from the pin to GND or 3V3 through a pressed button overrides the pin's internal pull (pull-up or pull-down). With a released button and a pull setting, the pin reads the pull's level (1 for pull-up, 0 for pull-down). With a released button and no pull, the pin reads an unpredictable value that the sim shows as alternating 0 and 1. A pull-down only pulls the pin to 0 if the pin was low before; the reality check shows the case where it was high.

**Learner Activity:**

1. The learner explores a sample circuit (pull-up, GND, button released) and presses the button to watch the reading change from 1 to 0.
2. The learner starts the challenges. Circuit 1 is shown with the button state.
3. The learner picks "reads 1," "reads 0," or "unpredictable."
4. The sim shows the reading and the Why text, then moves to the next circuit.
5. After circuit 6, the sim shows the score. The learner should notice that circuit 4 is the wiring mistake that makes a button seem dead.
6. The sim then shows an unscored reality check: a pin set to pull-down after it was driven high still reads 1 on the test board (GP16 and GP17), while a pull-up always reads 1. The learner is asked to explain, from a choice of two sentences, why the kit uses pull-ups. The correct sentence is "Pull-ups worked every time on the test board, and the pull-down did not." The other sentence is "Pull-ups and pull-downs behaved the same on the test board."

**Feedback:** 6 circuits, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The pin reads <answer>: <Why>". The answer is revealed right after each pick, and a running score "n of 6" is shown. The reality check is not scored: a wrong choice shows the correct sentence and the table of readings.

**Starting State:** The sample circuit is shown with the button released and the pin reading 1, with the question "What will the pin read when the button is pressed?"

**Chapter Anchors:** The chapter states that with a pull-up and the button to ground, a released button reads 1 and a pressed button reads 0, and that the kit uses the pull-up built into the Pico. The chapter also states that on the test board a pull-down on GP16 and GP17 kept reading 1 after the pin had been driven high, and that pull-ups were not affected.
```
