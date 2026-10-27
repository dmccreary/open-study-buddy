---
title: "FFT Bin Calculator"
description: "Find the FFT bin for a tone, or the center frequency of a bin, with a 12,800 Hz sample rate and a 512-point FFT (25 Hz per bin)."
status: built
library: p5.js
bloom_level: Apply
image: /sims/fft-bin-calculator/fft-bin-calculator.png
og:image: /sims/fft-bin-calculator/fft-bin-calculator.png
twitter:image: /sims/fft-bin-calculator/fft-bin-calculator.png
social:
   cards: false
quality_score: 95
---

# FFT Bin Calculator

<iframe src="main.html" width="100%" height="532px" scrolling="no"></iframe>

[Run the FFT Bin Calculator MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/fft-bin-calculator/main.html" width="100%" height="532px" scrolling="no"></iframe>
```

## Description

With a sample rate of 12,800 Hz and an FFT size of 512, every FFT bin is 12,800 / 512 = 25 Hz wide, and the useful bins run from 0 to 255 (the Nyquist limit of 6,400 Hz would be bin 256). Two formulas cover everything: bin = frequency / 25, and bin center = bin number x 25.

The top strip shows the whole spectrum; the zoom row shows eleven bins around the tone, each with its number and center frequency, and the red line is the tone. In explore mode you move the tone from 0 to 6,400 Hz and read the decimal bin, the nearest bin and the difference from its center. In the quiz you find the nearest bin for four tones and the center frequency of two bins. The values match `src/kits/study-buddy-base/config.py`.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 6 challenges / Back to explore**: Switch between the slider and the quiz.
- **Answer box and Submit**: Type a whole number. One attempt per challenge.
- **Next challenge / See score**: Move on after the feedback.
- **Tone frequency slider**: Explore only: 0 to 6,400 Hz in steps of 12.5 Hz, default 1,000 Hz.

## Lesson Plan

### Learning Objective

The learner will calculate the nearest FFT bin for 4 tone frequencies and the center frequency of 2 bins, using a sample rate of 12,800 Hz and an FFT size of 512, with at least 5 of 6 answers correct.

**Bloom's Taxonomy level:** Apply (calculate)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

frequency bin, bin width, sample rate, FFT size, Nyquist limit (all defined in this chapter above the block, and in Chapter 3 for sample rate and Nyquist limit).

### Activities

1. **Exploration (5 min):** Set the tone to 1,000 Hz, then 440 Hz, then 437.5 Hz. Compare where the tone sits in each case.
2. **Guided practice (5 min):** For challenge 3 (262 Hz), compute 262 / 25 on paper and decide which neighbor is nearer before submitting.
3. **Assessment (5 min):** Complete all six challenges. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) The bin number equals the frequency in hertz. (2) The bin width depends on the loudness of the tone. (3) A tone between two bins is lost.

### Discussion Questions

1. Is a tone between two bins lost?
2. Does a louder tone change the bin width?
3. Why is there no bin 256 in the useful range?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 9</summary>

```text
Type: microsim
**sim-id:** fft-bin-calculator<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the nearest FFT bin for 4 tone frequencies and the center frequency of 2 bins, using a sample rate of 12,800 Hz and an FFT size of 512, with at least 5 of 6 answers correct.

**Prerequisites:** frequency bin, bin width, sample rate, FFT size, Nyquist limit (all defined in this chapter above the block, and in Chapter 3 for sample rate and Nyquist limit).

**Evidence of Mastery:** For each of the 6 challenges the learner types a whole number (a bin number for challenges 1 to 4, a frequency in hertz for challenges 5 and 6) and submits. An answer is correct when it equals the Answer column in Content exactly. Mastery is 5 of 6 correct on the first attempt. Moving the exploration slider is exploration, not evidence.

**Misconceptions:** (1) The bin number equals the frequency in hertz. (2) The bin width depends on the loudness of the tone. (3) A tone between two bins is lost.

**Instructional Rationale:** Apply-level calculation needs repeated practice with a check. The learner commits a number before the result is shown, and the exploration slider first makes the two formulas visible on a tone the learner controls.

**Content:**

The model has a sample rate of 12,800 Hz, an FFT size of 512 samples, a bin width of 25 Hz, and 256 useful bins numbered 0 to 255. The formulas shown on screen are: bin = frequency / 25, and bin center = bin number x 25. The nearest bin is the bin whose center is closest to the tone.

| # | Question shown | Answer | Why (shown as feedback) |
|---|---|---|---|
| 1 | Nearest bin for a 1,000 Hz tone | 40 | 1,000 / 25 = 40.0, exactly on a bin center. |
| 2 | Nearest bin for a 440 Hz tone | 18 | 440 / 25 = 17.6, which is closer to 18 than to 17. |
| 3 | Nearest bin for a 262 Hz tone | 10 | 262 / 25 = 10.48, which is closer to 10 than to 11. |
| 4 | Nearest bin for a 3,300 Hz tone | 132 | 3,300 / 25 = 132.0, exactly on a bin center. |
| 5 | Center frequency of bin 100, in Hz | 2500 | 100 x 25 = 2,500 Hz. |
| 6 | Center frequency of bin 255, in Hz | 6375 | 255 x 25 = 6,375 Hz, the top bin; the Nyquist limit of 6,400 Hz would be bin 256. |

For exploration the learner moves a tone-frequency slider from 0 to 6,400 Hz in steps of 12.5 Hz, default 1,000 Hz. The sim shows the tone on a row of bins with the two formulas filled in, the bin number as a decimal, the nearest bin, and the difference in hertz between the tone and the nearest bin center.

**Provenance:** The sample rate, FFT size, and bin width are the values in `src/kits/study-buddy-base/config.py` (`MIC_SAMPLE_RATE`, `FFT_SIZE`). The answers are computed from the formulas in Rules, and they match the table in the chapter section "Frequency Bins and Bin Width".

**Rules:** Bin = frequency x 512 / 12,800. The nearest bin is the bin number rounded to the nearest whole number; a tone exactly halfway between two bins is shown as a tie and is not used in any challenge. Bin center = bin number x 12,800 / 512. Slider values from 0 to 6,400 Hz; at 6,400 Hz the bin is 256, which is outside the 256 useful bins, and the sim says so.

**Learner Activity:**

1. The learner moves the slider and watches the decimal bin number and the nearest bin change.
2. The learner notices that a tone at 1,000 Hz lands exactly on bin 40, while 440 Hz lands between bins 17 and 18.
3. The learner starts the 6 challenges. Challenge 1 is shown.
4. The learner types a whole number and submits.
5. The sim shows the correct answer with the Why text, and a running score.

**Feedback:** 6 challenges, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The slider is at 1,000 Hz, showing bin 40.0 and an exact match, with the question "Which bin does this tone land in?"

**Chapter Anchors:** The chapter states that the bin width is 25 Hz, that there are 256 useful bins (0 to 255, the top bin being 6,375 Hz), that 1,000 Hz is bin 40.0, that 440 Hz is bin 17.6, and that 262 Hz is bin 10.48.
```

</details>

## References

1. [Discrete Fourier transform](https://en.wikipedia.org/wiki/Discrete_Fourier_transform) - Wikipedia - What each bin of the transform measures.
2. [Fast Fourier transform](https://en.wikipedia.org/wiki/Fast_Fourier_transform) - Wikipedia - The algorithm the kit runs on every audio frame.
3. [Nyquist frequency](https://en.wikipedia.org/wiki/Nyquist_frequency) - Wikipedia - Why the top useful frequency is half the sample rate.

## Related Resources

- [Chapter 9: Signal Processing and the FFT](../../chapters/09-signal-processing-fft/index.md)
