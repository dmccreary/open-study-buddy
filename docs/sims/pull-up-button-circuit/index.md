---
title: "Pull-Up Button Circuit"
description: "The learner will infer the value a GPIO input pin reads for 6 button circuits, given the pin's pull setting, what the button's other leg connects to, and whether the button is pressed, with at least 5 of 6 correct."
status: scaffold
library: p5.js
bloom_level: Understand
---

# Pull-Up Button Circuit



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

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

## Related Resources

- [Chapter 4: The Pico Kit Hardware and Wiring](../../chapters/04-pico-kit-hardware/index.md)
