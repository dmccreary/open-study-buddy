---
title: "Time and Frequency Domain Viewer"
description: "The learner will interpret a frequency-domain bar chart by choosing, for 6 challenge sounds, the time-domain waveform that has the same frequencies and amplitudes, with at least 5 of 6 correct."
status: built
library: p5.js
bloom_level: Understand
image: /sims/time-and-frequency-domain-viewer/time-and-frequency-domain-viewer.png
og:image: /sims/time-and-frequency-domain-viewer/time-and-frequency-domain-viewer.png
twitter:image: /sims/time-and-frequency-domain-viewer/time-and-frequency-domain-viewer.png
social:
   cards: false
---

# Time and Frequency Domain Viewer

<iframe src="main.html" width="100%" height="577px" scrolling="no"></iframe>

[Run the Time and Frequency Domain Viewer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

Place the following line in your website to include this MicroSim in your course:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/time-and-frequency-domain-viewer/main.html" width="100%" height="577px" scrolling="no"></iframe>
```

## Description

The same sound can be drawn two ways. The **time domain** plot shows the
waveform: how the signal changes over a 20 ms window. The **frequency domain**
bar chart shows the ingredients: one bar for each sine component, placed at its
frequency, with height equal to its amplitude.

This MicroSim builds a sound from two sine components that you control and
draws both views together. The bars are measured, not copied: the sim runs a
discrete Fourier transform (DFT) on the 20 ms waveform. Every frequency used is
a multiple of 50 Hz, so each component lands exactly on a DFT bin and the
measured height equals the component amplitude. If you set both components to
the same frequency they add together into one taller bar, just as they would in
a real spectrum.

## How to Use

1. Move **Freq 1**, **Amp 1**, **Freq 2** and **Amp 2**. Watch both views
   change at the same time.
2. Set one amplitude to 0 and notice that its bar disappears.
3. Press **Start challenges**. Each challenge shows a spectrum and three
   waveforms, A, B and C, drawn on the same vertical scale.
4. Press **A**, **B** or **C**. The sim marks the matching waveform in green,
   marks a wrong pick in red, and explains the answer.
5. Press **Next challenge**, and after challenge 6 press **Show score**.

Each challenge allows one pick. Mastery is 5 of 6 correct on the first attempt.

## Lesson Plan

### Learning Objective

Students will interpret a frequency-domain bar chart by choosing, for 6
challenge sounds, the time-domain waveform that has the same frequencies and
amplitudes.

### Warm-Up (3 minutes)

Play a single steady beep, then two notes at once. Ask: "How would you draw
each sound as a list of ingredients?"

### Guided Exploration (8 minutes)

1. Students set Amp 2 to 0 and move Freq 1. Ask: "What happens to the bar,
   and what happens to the waveform?"
2. Students change Amp 1 only. Ask the same question.
3. Students set both components to 200 Hz and explain why there is only one
   bar, at height 1.5.

### Challenge (7 minutes)

Students complete the six challenges. After each wrong pick, ask them to name
which property (position or height) they misread.

### Discussion Questions

1. Do taller bars mean higher pitches? What does bar height mean?
2. Are the two views showing different sounds?
3. A sound with two tones shows two bars. Why does its waveform look like one
   wiggly line instead of two separate waves?

### Assessment

The sim records 6 first-attempt picks. Mastery is 5 of 6 correct. Using the
sliders is exploration, not evidence.

## References

1. [Frequency domain](https://en.wikipedia.org/wiki/Frequency_domain) -
   Wikipedia article comparing time-domain and frequency-domain views.
2. [Discrete Fourier transform](https://en.wikipedia.org/wiki/Discrete_Fourier_transform) -
   Wikipedia article on the calculation used to measure the bars.
3. [Spectrum analyzer](https://en.wikipedia.org/wiki/Spectrum_analyzer) -
   Wikipedia article on instruments that display a frequency-domain view.

## Related Resources

- [Chapter 3: Sound and Digital Audio](../../chapters/03-sound-and-digital-audio/index.md)

??? note "Original specification"

    Type: microsim
    **sim-id:** time-and-frequency-domain-viewer<br/>
    **Library:** p5.js<br/>
    **Status:** Specified<br/>
    **Template:** https://github.com/dmccreary/spectrum-analyzer/tree/main/docs/sims/waveform-types<br/>
    **Bloom Level:** Understand<br/>
    **Bloom Verb:** interpret<br/>
    **Learning Objective:** The learner will interpret a frequency-domain bar chart by choosing, for 6 challenge sounds, the time-domain waveform that has the same frequencies and amplitudes, with at least 5 of 6 correct.

    **Prerequisites:** time domain, frequency domain, frequency, amplitude (all defined in this chapter above this block).

    **Evidence of Mastery:** For each of the 6 challenges the learner is shown a frequency-domain bar chart and picks one of three time-domain waveforms. A pick is correct when it matches the Correct choice column in Content. Mastery is 5 of 6 correct on the first attempt. Using the sliders in exploration is not evidence.

    **Misconceptions:** (1) Taller bars mean higher pitches. (2) The two views show different sounds. (3) A sound with two tones must show two separate waves in the time view.

    **Instructional Rationale:** Interpreting a spectrum requires connecting bar position to pitch and bar height to amplitude. Choosing among waveforms that differ in exactly one of those properties makes the learner decide which property each bar encodes.

    **Content:**

    Each sound is the sum of sine components, written (frequency in Hz, amplitude on a scale of 0 to 1). The sim draws the bars for the spectrum and the waveform for the time-domain choices from these lists.

    | # | Spectrum shown (components) | Choice A | Choice B | Choice C | Correct choice | Why (shown as feedback) |
    |---|---|---|---|---|---|---|
    | 1 | (200, 1.0) | (200, 1.0) | (400, 1.0) | (200, 0.5) | A | The bar is at 200 Hz and full height. |
    | 2 | (400, 1.0) | (200, 1.0) | (400, 1.0) | (400, 0.5) | B | The bar position gives the frequency: 400 Hz. |
    | 3 | (200, 0.5) | (200, 1.0) | (400, 0.5) | (200, 0.5) | C | The bar height gives the amplitude: half. |
    | 4 | (200, 1.0) and (600, 0.5) | (200, 1.0) | (200, 1.0) and (600, 0.5) | (600, 1.0) and (200, 0.5) | B | Two bars mean two components, with the heights shown. |
    | 5 | (300, 0.75) and (900, 0.75) | (300, 0.75) and (900, 0.75) | (300, 0.75) | (900, 0.75) and (300, 0.25) | A | Both bars are the same height, at 300 and 900 Hz. |
    | 6 | (100, 1.0), (300, 0.5) and (500, 0.25) | (100, 1.0), (300, 0.25) and (500, 0.5) | (100, 0.25), (300, 0.5) and (500, 1.0) | (100, 1.0), (300, 0.5) and (500, 0.25) | C | The bars fall in height from left to right: 1.0, 0.5, 0.25. |

    Exploration controls: two components, each with frequency from 100 to 1,000 Hz in steps of 50 Hz (defaults 200 Hz and 600 Hz) and amplitude from 0 to 1 in steps of 0.25 (defaults 1.0 and 0.5). Both views update together as the learner changes them.

    **Provenance:** All components are illustrative, and the sim labels them "illustrative."

    **Rules:** A time-domain waveform is the sum of its components, each a sine wave of its frequency and amplitude, plotted over a 20 ms window. The spectrum has one bar per component, placed at its frequency, with height proportional to its amplitude. A component with amplitude 0 has no bar.

    **Learner Activity:**

    1. The learner explores: changes the frequency and amplitude of each component and sees both views change at the same time.
    2. The learner starts the challenges. Challenge 1 shows a spectrum and three waveforms.
    3. The learner picks one waveform.
    4. The sim shows whether the pick is correct, marks the matching waveform, and shows the Why text.
    5. After challenge 6, the sim shows the score. The learner should notice that bar position is frequency and bar height is amplitude.

    **Feedback:** 6 challenges, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. <Why>". The correct choice is revealed right after each pick, and a running score "n of 6" is shown.

    **Starting State:** The two views are shown with the default components and the question "Which bars belong to which part of the wave?"

    **Chapter Anchors:** The chapter states that bar position is frequency and bar height is amount, that a steady beep is one bar, and that two notes at once are two bars.
