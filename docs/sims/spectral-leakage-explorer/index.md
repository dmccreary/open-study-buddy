---
title: "Spectral Leakage Explorer"
description: "Compare a tone's spectrum with no window and with the Hann window to see how windowing trades leakage for a wider peak."
status: built
library: p5.js
bloom_level: Analyze
image: /sims/spectral-leakage-explorer/spectral-leakage-explorer.png
og:image: /sims/spectral-leakage-explorer/spectral-leakage-explorer.png
twitter:image: /sims/spectral-leakage-explorer/spectral-leakage-explorer.png
social:
   cards: false
quality_score: 95
---

# Spectral Leakage Explorer

<iframe src="main.html" width="100%" height="552px" scrolling="no"></iframe>

[Run the Spectral Leakage Explorer MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/spectral-leakage-explorer/main.html" width="100%" height="552px" scrolling="no"></iframe>
```

## Description

When a tone does not complete a whole number of cycles in the 512-sample frame, its energy leaks into neighboring bins. Multiplying the samples by the Hann window, w[i] = 0.5 - 0.5 cos(2 pi i / 512), tames the leakage but always spreads a peak over about three bins.

The chart shows bins 30 to 50 as a percentage of the loudest bin, with a dashed line at 10%. The sim counts every bin from 0 to 255 at or above that line. In explore mode you move a tone of amplitude 1,000 between 900 and 1,100 Hz and switch the window. In the quiz you predict, for six tones, which window gives fewer bins above 10%, then see both spectra side by side. The sim computes a real 512-point DFT and reproduces the counts printed by `04-leakage-hann.py`.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 6 tones / Back to explore**: Switch between exploring and the quiz.
- **Prediction menu and Submit**: Choose No window, Hann window or The same. One attempt per tone.
- **Next tone / See score**: Move on after the feedback.
- **Window menu and Tone slider**: Explore only: pick the window; move the tone from 900 to 1,100 Hz in steps of 6.25 Hz.

## Lesson Plan

### Learning Objective

The learner will compare the spectra of 6 test tones taken with no window and with the Hann window, and choose for each the window that gives the narrower peak, with at least 5 of 6 correct.

**Bloom's Taxonomy level:** Analyze (compare)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

frequency bin, spectral leakage, windowing, Hann window, magnitude spectrum (all defined in this chapter above the block).

### Activities

1. **Exploration (5 min):** Count the dark bars at 1,000 Hz and 1,012.5 Hz with each window. Write the four counts in a table.
2. **Guided practice (5 min):** For tones 1 and 2, decide whether the tone sits on a bin center before predicting.
3. **Assessment (5 min):** Complete all six tones. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) A window always makes the peak narrower. (2) Leakage only happens to loud tones. (3) A tone exactly on a bin leaks.

### Discussion Questions

1. Does a window always make the peak narrower? When does it not?
2. Where does a tone have to sit for the worst leakage without a window?
3. Does a quieter tone leak less? Why does the percentage scale answer this?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 9</summary>

```text
Type: microsim
**sim-id:** spectral-leakage-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** compare<br/>
**Learning Objective:** The learner will compare the spectra of 6 test tones taken with no window and with the Hann window, and choose for each the window that gives the narrower peak, with at least 5 of 6 correct.

**Prerequisites:** frequency bin, spectral leakage, windowing, Hann window, magnitude spectrum (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 6 tones the learner sees the tone's frequency and its bin number, predicts which window ("No window", "Hann window", or "The same") gives fewer bins with at least 10% of the loudest bin's magnitude, and submits before the two spectra are drawn. A choice is correct when it matches the Answer column in Content. Mastery is 5 of 6 correct on the first attempt. Moving the exploration slider is exploration, not evidence.

**Misconceptions:** (1) A window always makes the peak narrower. (2) Leakage only happens to loud tones. (3) A tone exactly on a bin leaks.

**Instructional Rationale:** Analyze-level comparison requires the learner to relate where a tone sits relative to the bins to how a window changes the picture. Predicting before the spectra are drawn forces a decision based on that relationship. The six tones include two on-bin cases where the window does not help, which exposes the first misconception.

**Content:**

The model is a sine wave of amplitude 1,000 sampled at 12,800 Hz for 512 samples. The "no window" spectrum is the magnitude of the 512-point DFT of the samples. The "Hann window" spectrum is the same after multiplying the samples by w[i] = 0.5 - 0.5 cos(2 pi i / 512). The sim counts bins 0 to 255 whose magnitude is at least 10% of the largest magnitude in that spectrum.

| # | Tone (Hz) | Bin | Bins at least 10%, no window | Bins at least 10%, Hann | Answer | Why (shown as feedback) |
|---|---|---|---|---|---|---|
| 1 | 1,000 | 40.00 | 1 | 3 | No window | The tone is exactly on a bin, so there is no leakage to remove, and the window adds a three-bin peak. |
| 2 | 1,006.25 | 40.25 | 5 | 3 | Hann window | The tone is a quarter bin off center, so the plain spectrum leaks into 5 bins and Hann holds it to 3. |
| 3 | 1,012.5 | 40.50 | 10 | 4 | Hann window | Halfway between bins is the worst case without a window: 10 bins. |
| 4 | 1,018.75 | 40.75 | 5 | 3 | Hann window | A quarter bin off center on the other side, the mirror image of tone 2. |
| 5 | 1,037.5 | 41.50 | 10 | 4 | Hann window | Another halfway case, between bins 41 and 42. |
| 6 | 1,050 | 42.00 | 1 | 3 | No window | Exactly on bin 42, so the window can only widen the peak. |

For exploration the learner moves a tone slider from 900 Hz to 1,100 Hz in steps of 6.25 Hz (default 1,000 Hz) and chooses the window, and the sim draws the magnitude of bins 30 to 50 for the chosen window.

**Provenance:** The counts in the table are produced by `src/chapters/09-signal-processing-fft/04-leakage-hann.py` and a variant of it using the same code and the same FFT, for the tones 1,000, 1,006.25, 1,012.5, 1,018.75, 1,037.5, and 1,050 Hz. The sim computes the spectra with the same formulas and must reproduce the table.

**Rules:** Count bins k from 0 to 255 with magnitude >= 0.1 x the largest magnitude. The "Answer" is the window with the smaller count; if the counts are equal the answer is "The same" (no challenge has equal counts). Slider: min 900, max 1,100, step 6.25, default 1,000, unit Hz.

**Learner Activity:**

1. The learner moves the slider with each window and watches the peak and the skirt of small bins around it.
2. The learner notices that on bin centers (1,000 Hz and 1,050 Hz) the plain spectrum has a single spike.
3. The learner starts the 6 tones. Tone 1 is shown with its bin number.
4. The learner chooses a window and submits.
5. The sim draws both spectra, highlights the bins counted, and shows the Why text.

**Feedback:** 6 tones, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. <Why>". The two spectra and the counts are revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The slider is at 1,000 Hz with the plain spectrum drawn as one spike and the question "Which window makes this peak narrower?"

**Chapter Anchors:** The chapter states that a tone on a bin center has 1 loud bin with no window and 3 with Hann, that 1,006.25 Hz gives 5 and 3, and that 1,012.5 Hz gives 10 and 4.
```

</details>

## References

1. [Spectral leakage](https://en.wikipedia.org/wiki/Spectral_leakage) - Wikipedia - Why off-bin tones spread across many bins.
2. [Hann function](https://en.wikipedia.org/wiki/Hann_function) - Wikipedia - The window formula used by the kit.
3. [Window function](https://en.wikipedia.org/wiki/Window_function) - Wikipedia - How windows trade peak width for leakage.

## Related Resources

- [Chapter 9: Signal Processing and the FFT](../../chapters/09-signal-processing-fft/index.md)
