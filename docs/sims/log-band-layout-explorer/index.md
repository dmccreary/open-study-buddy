---
title: "Log Band Layout Explorer"
description: "The learner will use the 16-band log-spaced layout from 100 Hz to 6,400 Hz to find the band that contains 3 tones and the number of bins in 3 bands, with at least 5 of 6 correct."
status: built
library: p5.js
bloom_level: Apply
image: /sims/log-band-layout-explorer/log-band-layout-explorer.png
og:image: /sims/log-band-layout-explorer/log-band-layout-explorer.png
twitter:image: /sims/log-band-layout-explorer/log-band-layout-explorer.png
social:
   cards: false
quality_score: 95
---

# Log Band Layout Explorer

<iframe src="main.html" width="100%" height="562px" scrolling="no"></iframe>

[Run the Log Band Layout Explorer MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/log-band-layout-explorer/main.html" width="100%" height="562px" scrolling="no"></iframe>
```

## Description

The display groups the 256 FFT bins into a few bands. Because the ear judges pitch by ratio, the bands are log-spaced: each band's top edge is a fixed multiple of its bottom edge. For 16 bands from 100 Hz to 6,400 Hz that ratio is 64^(1/16) = 1.2968. The edges are rounded to whole bins, and a band narrower than one bin is stretched to one bin.

The strip shows every band along the bin axis, and the table lists each band's bins, bin count and edges in hertz. In explore mode you change the number of bands (4 to 32) and the lowest frequency (50 to 400 Hz). In the quiz, which always uses the default 16-band layout, you find the band that holds three tones and the number of bins in three bands. The layout reproduces `dsp.log_band_edges(16, 100, 6400, 12800, 512)`.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 6 challenges / Back to explore**: Switch between exploring and the quiz.
- **Answer box and Submit**: Type a whole number. One attempt per challenge.
- **Next challenge / See score**: Move on after the feedback.
- **Bands and Lowest sliders**: Explore only: 4 to 32 bands in steps of 4; lowest frequency 50 to 400 Hz in steps of 50.

## Lesson Plan

### Learning Objective

The learner will use the 16-band log-spaced layout from 100 Hz to 6,400 Hz to find the band that contains 3 tones and the number of bins in 3 bands, with at least 5 of 6 correct.

**Bloom's Taxonomy level:** Apply (use)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

frequency bin, bin width, band energy, log-spaced bands (all defined in this chapter above the block).

### Activities

1. **Exploration (5 min):** Set 32 bands and 50 Hz, then 8 bands and 400 Hz. Count how many bands hold only one bin in each layout.
2. **Guided practice (5 min):** For challenge 2 (440 Hz), find the nearest bin first, then look it up in the table.
3. **Assessment (5 min):** Complete all six challenges. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) Every band has the same number of bins. (2) Equal-width bands and log-spaced bands put 1,000 Hz in the same band. (3) The highest band is the narrowest.

### Discussion Questions

1. Why does every band have a different number of bins?
2. Would equal-width bands put 1,000 Hz in the same band number as log bands?
3. Why do the bands start at 100 Hz instead of 0 Hz?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 9</summary>

```text
Type: microsim
**sim-id:** log-band-layout-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** use<br/>
**Learning Objective:** The learner will use the 16-band log-spaced layout from 100 Hz to 6,400 Hz to find the band that contains 3 tones and the number of bins in 3 bands, with at least 5 of 6 correct.

**Prerequisites:** frequency bin, bin width, band energy, log-spaced bands (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 6 challenges the learner types a whole number (a band number for challenges 1 to 3, a bin count for challenges 4 to 6) and submits. An answer is correct when it equals the Answer column in Content. Mastery is 5 of 6 correct on the first attempt. Changing the number of bands or the lowest frequency in exploration is exploration, not evidence.

**Misconceptions:** (1) Every band has the same number of bins. (2) Equal-width bands and log-spaced bands put 1,000 Hz in the same band. (3) The highest band is the narrowest.

**Instructional Rationale:** Apply-level use of a layout requires reading a table of edges and mapping a frequency through bins to a band. Changing the number of bands during exploration shows how the layout depends on the ratio between neighboring edges, before the learner uses the fixed 16-band layout for the challenges.

**Content:**

The fixed layout for the challenges is the 16-band table in the chapter section "Band Energy and Log-Spaced Bands", with bin width 25 Hz. A tone belongs to the band that contains its nearest bin.

| # | Question shown | Answer | Why (shown as feedback) |
|---|---|---|---|
| 1 | Which band contains a 1,000 Hz tone? | 8 | 1,000 / 25 = bin 40, and band 8 holds bins 32 to 40. |
| 2 | Which band contains a 440 Hz tone? | 5 | 440 / 25 = 17.6, nearest bin 18, and band 5 holds bins 15 to 18. |
| 3 | Which band contains a 3,000 Hz tone? | 13 | 3,000 / 25 = bin 120, and band 13 holds bins 117 to 151. |
| 4 | How many bins are in band 10? | 16 | Band 10 holds bins 54 to 69, which is 69 - 54 + 1 = 16. |
| 5 | How many bins are in band 15? | 59 | Band 15 holds bins 197 to 255, which is 59. |
| 6 | How many bins are in band 0? | 1 | Band 0 holds only bin 4, because the band between 100 and 129.7 Hz is narrower than one 25 Hz bin and is stretched to one bin. |

For exploration the learner changes the number of bands and the lowest frequency, and the sim shows the edge in hertz, the bins, and the bin count of every band.

**Provenance:** The 16-band layout and its bin ranges are printed by `src/chapters/09-signal-processing-fft/03-bin-calculator.py`, which calls `dsp.log_band_edges(16, 100, 6400, 12800, 512)`. The chapter section reproduces the same table.

**Rules:** Edge i is round(f_low x r^i x 512 / 12,800) with r = (6,400 / f_low)^(1 / bands); halves round to the nearest even whole number. If an edge is not greater than the previous edge, it is set to the previous edge plus 1. Band i holds bins edge[i] to edge[i+1] - 1. Number of bands: min 4, max 32, step 4, default 16. Lowest frequency: min 50, max 400, step 50, default 100, unit Hz. The highest frequency is always 6,400 Hz.

**Learner Activity:**

1. The learner changes the number of bands and the lowest frequency and watches the edges and bin counts update.
2. The learner notices that the lowest bands always shrink to one bin.
3. The learner starts the 6 challenges with the default layout. Challenge 1 is shown.
4. The learner types a whole number and submits.
5. The sim highlights the band or the bins involved and shows the Why text.

**Feedback:** 6 challenges, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The default 16-band layout is shown, with the question "Which band holds this tone?"

**Chapter Anchors:** The chapter states that the 16 bands run from 100 Hz to 6,400 Hz with a ratio of 1.2968 per band, that band 8 holds bins 32 to 40, that band 10 holds 16 bins, and that band 15 holds 59 bins.
```

</details>

## References

1. [Octave band](https://en.wikipedia.org/wiki/Octave_band) - Wikipedia - Log-spaced frequency bands used in acoustics.
2. [Logarithmic scale](https://en.wikipedia.org/wiki/Logarithmic_scale) - Wikipedia - Why equal ratios look like equal steps.
3. [Spectrum analyzer](https://en.wikipedia.org/wiki/Spectrum_analyzer) - Wikipedia - Band displays like the one on the Study Buddy screen.

## Related Resources

- [Chapter 9: Signal Processing and the FFT](../../chapters/09-signal-processing-fft/index.md)
