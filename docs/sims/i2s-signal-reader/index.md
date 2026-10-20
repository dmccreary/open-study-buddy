---
title: "I2S Signal Reader"
description: "The learner will interpret simplified I2S waveforms by reading the value of the left-channel sample from the serial data line in 6 waveforms, with at least 5 of 6 correct."
status: built
library: p5.js
bloom_level: Understand
image: /sims/i2s-signal-reader/i2s-signal-reader.png
og:image: /sims/i2s-signal-reader/i2s-signal-reader.png
twitter:image: /sims/i2s-signal-reader/i2s-signal-reader.png
social:
   cards: false
quality_score: 95
---

# I2S Signal Reader

<iframe src="main.html" width="100%" height="542px" scrolling="no"></iframe>

[Run the I2S Signal Reader MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/i2s-signal-reader/main.html" width="100%" height="542px" scrolling="no"></iframe>
```

## Description

I2S carries audio on three wires. The bit clock ticks once per bit, the word select line says which channel the bits belong to (low = left, high = right), and the serial data line carries the bits themselves, most significant bit first. A bit is sampled at each rising edge of the bit clock.

This simplified waveform uses 8-bit words so you can read them by eye; the real microphone uses 32-bit slots. In explore mode you step one bit-clock tick at a time and watch each bit drop into the left-word register, whose weights (-128, 64, 32 ... 1) show how a signed two's-complement value is built. In the quiz you read the signed value of the left-channel word from six waveforms; after you submit, the left word is highlighted and its bits are written under the data line. The word length and values are illustrative.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 6 waveforms / Back to explore**: Switch between the example waveform and the quiz.
- **Answer box and Submit**: Type the signed left value (-128 to 127). One attempt per waveform.
- **Next waveform / See score**: Move on after the feedback.
- **Step one tick / Back to start**: Explore only: advance one rising edge, or return to tick 0.

## Lesson Plan

### Learning Objective

The learner will interpret simplified I2S waveforms by reading the value of the left-channel sample from the serial data line in 6 waveforms, with at least 5 of 6 correct.

**Bloom's Taxonomy level:** Understand (interpret)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

I2S, bit clock, word select, serial data line, most significant bit first, signed 8-bit numbers (all defined in this chapter above the block, and in Chapter 3 for bit depth).

### Activities

1. **Exploration (5 min):** Step through all 16 ticks of the example. Note on which tick the word select line changes and what that means.
2. **Guided practice (5 min):** For waveform 2, write the 8 bits, multiply each by its weight, and add them before submitting.
3. **Assessment (5 min):** Complete all six waveforms. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) The word select line carries audio. (2) The least significant bit is sent first. (3) Both channels are always sent in the same word.

### Discussion Questions

1. Which wire tells the receiver whose sample the bits are?
2. Waveforms 5 and 6 are 45 and -45. How do you get one bit pattern from the other?
3. What would go wrong if the receiver read the bits least significant bit first?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 8</summary>

```text
Type: microsim
**sim-id:** i2s-signal-reader<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** interpret<br/>
**Learning Objective:** The learner will interpret simplified I2S waveforms by reading the value of the left-channel sample from the serial data line in 6 waveforms, with at least 5 of 6 correct.

**Prerequisites:** I2S, bit clock, word select, serial data line, most significant bit first, signed 8-bit numbers (all defined in this chapter above the block, and in Chapter 3 for bit depth).

**Evidence of Mastery:** For each of the 6 waveforms the learner enters the signed decimal value of the left-channel word. An answer is correct when it equals the Left value column in Content. Mastery is 5 of 6 correct on the first attempt. Stepping through the example waveform in exploration is exploration, not evidence.

**Misconceptions:** (1) The word select line carries audio. (2) The least significant bit is sent first. (3) Both channels are always sent in the same word.

**Instructional Rationale:** Understand-level interpretation requires the learner to apply the roles of the three wires to a concrete waveform. Reading the bits in the order they arrive, and noticing that the word-select level says which channel they belong to, ties each wire to its role.

**Content:**

The simplified waveform has three traces: the bit clock, the word select, and the serial data. Each word has 8 bits. While word select is low, the 8 bits on the data line are the left-channel word; while word select is high, the next 8 bits are the right-channel word. A bit is sampled at each rising edge of the bit clock. Bits are sent most significant bit first, and the value is a signed 8-bit number (two's complement: the first bit is the sign, and values with a first bit of 1 are negative, from -128 to -1).

| # | Left word bits (first to last) | Left value | Why (shown as feedback) |
|---|---|---|---|
| 1 | 00000000 | 0 | All bits are zero, so the value is 0. |
| 2 | 01111111 | 127 | The sign bit is 0 and all other bits are 1: 64+32+16+8+4+2+1 = 127. |
| 3 | 10000000 | -128 | The sign bit is 1 and the rest are 0, the most negative value. |
| 4 | 11111111 | -1 | All ones in two's complement is -1. |
| 5 | 00101101 | 45 | 32 + 8 + 4 + 1 = 45. |
| 6 | 11010011 | -45 | The sign bit is 1. Flipping all bits gives 00101100, adding 1 gives 00101101 = 45, so the value is -45. |

The right-channel word for each waveform is 00000000 (silent) and is shown so the learner can see the word select line change.

**Provenance:** The word length of 8 bits is a simplification for teaching and the values are illustrative. The sim labels both "illustrative." The roles of the three wires come from the chapter sections above.

**Rules:** The left word is the 8 bits sampled while word select is low. The value is the signed 8-bit number: the bits read as an unsigned number n from 0 to 255, minus 256 if n is 128 or more.

**Learner Activity:**

1. The learner explores an example waveform: steps forward one bit-clock tick at a time and watches which wire changes and which bit is collected.
2. The learner starts the 6 waveforms. Waveform 1 shows the three traces.
3. The learner enters the left-channel value and submits.
4. The sim highlights the 8 bits in the left word, then shows the correct value and the Why text.
5. After waveform 6, the sim shows the score. The learner should notice that waveforms 5 and 6 give 45 and -45, values with the same size and opposite signs.

**Feedback:** 6 waveforms, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The left value is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The example waveform is shown stopped at the start, with the question "Which wire says whose sample this is?"

**Chapter Anchors:** The chapter states that the three wires are the bit clock, the word select, and the serial data line, that word select low means the left channel, and that the most significant bit is sent first.
```

</details>

## References

1. [I2S](https://en.wikipedia.org/wiki/I%C2%B2S) - Wikipedia - The three-wire audio bus and its timing.
2. [Two's complement](https://en.wikipedia.org/wiki/Two%27s_complement) - Wikipedia - How signed samples are stored.
3. [machine.I2S](https://docs.micropython.org/en/latest/library/machine.I2S.html) - MicroPython documentation - The class the kit uses to read the microphone.

## Related Resources

- [Chapter 8: I2S Audio: Recording and Playing Sound](../../chapters/08-i2s-audio/index.md)
