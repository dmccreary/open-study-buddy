---
title: "Kit Wiring Fault Finder"
description: "The learner will examine 6 wiring listings against the pin assignment table and identify the one wrong connection in each, with at least 5 of 6 correct on the first attempt."
status: scaffold
library: p5.js
bloom_level: Analyze
---

# Kit Wiring Fault Finder



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 4: The Pico Kit Hardware and Wiring](../../chapters/04-pico-kit-hardware/index.md).

```text
Type: microsim
**sim-id:** kit-wiring-fault-finder<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** examine<br/>
**Learning Objective:** The learner will examine 6 wiring listings against the pin assignment table and identify the one wrong connection in each, with at least 5 of 6 correct on the first attempt.

**Prerequisites:** pin assignment table, ground wiring, pull-up resistor, the I2S neighbor rule, the 3.3 V rule for the microphone (all defined in the sections above this block).

**Evidence of Mastery:** For each listing the learner selects the one line that does not match the pin assignment table. A selection is correct when it equals the Faulty line column in Content. Mastery is 5 of 6 on the first attempt. Reading the pin assignment table while answering is allowed, and is not scored.

**Misconceptions:** (1) A wiring mistake always produces an error message. (2) Any 5 V part can use the 5 V pin. (3) The two I2S pins can be assigned in either order.

**Instructional Rationale:** Analyze-level examination requires comparing a whole against a reference and locating the departure. A listing with exactly one fault trains the learner to check each line against the table, which is the same skill used when debugging a real kit.

**Content:**

Each listing shows the wires of one part as "part pin to Pico pin or rail." The reference is the table "The Pin Assignment Table" in this chapter.

| # | Part | Listing shown | Faulty line | Correct connection | What the learner would see (shown as feedback) |
|---|---|---|---|---|---|
| 1 | Microphone | SCK to GP10; WS to GP11; SD to GP12; L/R to GND; VDD to VBUS (5 V); GND to GND | VDD to VBUS (5 V) | VDD to 3V3 | The INMP441 is a 3.3 V part. A 5 V supply can damage it. |
| 2 | Microphone | SCK to GP10; WS to GP13; SD to GP12; L/R to GND; VDD to 3V3; GND to GND | WS to GP13 | WS to GP11 | I2S() raises "invalid ws (must be sck+1)", and GP13 is also the MODE button. |
| 3 | Amplifier | BCLK to GP20; LRC to GP22; DIN to GP19; GAIN to GP18; VIN to VBUS; GND to GND | LRC to GP22 | LRC to GP21 | I2S() raises an error because the left/right clock must be the pin right after the bit clock. |
| 4 | Button MODE | One leg to GP13; the leg on the opposite side to 3V3 | Opposite leg to 3V3 | Opposite leg to GND | With a pull-up, the pin always reads 1, so test 03 never reports a press. |
| 5 | Display | SCL to GP2; SDA to GP3; RST to GP4; DC to GP5; CS to GP6; BL not connected; VCC to 3V3; GND to GND | BL not connected | BL to GP7 | The screen stays dark in test 04 because the backlight never turns on. |
| 6 | Amplifier | BCLK to GP20; LRC to GP21; DIN to GP19; GAIN to GP18; VIN to VBUS; GND not connected | GND not connected | GND to GND | Test 05 is silent because the amplifier has no ground return. |

**Provenance:** The listings and symptoms come from the kit README and the headers of tests 03, 04, and 05 in `src/kits/study-buddy-base/`, and from the table "The Pin Assignment Table" in this chapter.

**Rules:** Each listing has exactly one faulty line. A selection is correct only if it is the faulty line. The reference table is always available to the learner.

**Learner Activity:**

1. The learner reads listing 1 and selects the line that does not match the pin assignment table.
2. The sim shows whether it was correct, the correct connection, and the symptom text.
3. The learner continues through listing 6.
4. After listing 6, the sim shows the score. The learner should notice that only some mistakes produce an error message.

**Feedback:** 6 listings, fixed order, one attempt each. Correct: "Correct: <symptom text>". Incorrect: "Not quite. The faulty line is <faulty line>: <symptom text>". The correct line is revealed right after each selection, and a running score "n of 6" is shown.

**Starting State:** Listing 1 is shown with the pin assignment table beside it and the question "Which line does not match the table?"

**Chapter Anchors:** The chapter states the microphone pins SCK GP10, WS GP11, SD GP12, the amplifier pins BCLK GP20, LRC GP21, DIN GP19, GAIN GP18, the display backlight on GP7, and the MODE button on GP13.
```

## Related Resources

- [Chapter 4: The Pico Kit Hardware and Wiring](../../chapters/04-pico-kit-hardware/index.md)
