---
title: "Sampling Explorer"
description: "The learner will calculate the frequency a sampled tone appears to have, given its true frequency and the sample rate, for 6 challenge tones, with at least 5 of 6 correct."
status: built
library: p5.js
bloom_level: Apply
image: /sims/sampling-explorer/sampling-explorer.png
og:image: /sims/sampling-explorer/sampling-explorer.png
twitter:image: /sims/sampling-explorer/sampling-explorer.png
social:
   cards: false
---

# Sampling Explorer

<iframe src="main.html" width="100%" height="517px" scrolling="no"></iframe>

[Run the Sampling Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

Place the following line in your website to include this MicroSim in your course:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/sampling-explorer/main.html" width="100%" height="517px" scrolling="no"></iframe>
```

## Description

A microphone input is measured at a fixed sample rate. This MicroSim draws a
true sine tone in gray, the sample dots in red, and the wave the dots suggest
in blue. When the tone is below the Nyquist limit (half the sample rate) the
blue wave matches the true tone. When the tone is above the limit, the dots
trace a lower, false tone: the true frequency folds back to
sample rate - true frequency.

The blue wave is not drawn by hand. For a tone *f* above the limit, every
sample of sin(2&pi;*f* *t*) equals a sample of -sin(2&pi;(*fs* - *f*) *t*), so
the sim draws that phase-inverted wave and it passes exactly through every dot.
At exactly half the sample rate every sample lands on zero, and the sim says
the samples cannot show the tone reliably.

The 12,800 Hz rate is the kit's `MIC_SAMPLE_RATE`, and 16,000 Hz is the test 05
speaker rate. The other tones and rates are illustrative.

## How to Use

1. Move the **True frequency** slider (100 to 9,000 Hz) and pick a **Sample
   rate**. Watch the dots and the blue wave they suggest. The true frequency
   always stays below the sample rate: picking a lower rate lowers the
   frequency if needed.
2. Press **Start challenges**. Each challenge shows a tone and a sample rate.
3. Type the apparent frequency in hertz and press **Submit** or Enter. The
   sim then shows the samples, the Nyquist limit and the correct answer.
4. Press **Next challenge**, and after challenge 6 press **Show score**.

Each challenge allows one answer, and an answer within 1 Hz counts as
correct. Mastery is 5 of 6.

## Lesson Plan

### Learning Objective

Students will calculate the frequency a sampled tone appears to have, given its
true frequency and the sample rate.

### Warm-Up (3 minutes)

Show a video clip of a car wheel that seems to spin backward. Ask why a camera
taking pictures at a fixed rate could make a wheel look slow or reversed.

### Guided Exploration (8 minutes)

1. At 12,800 Hz, students move the tone from 1,000 Hz up past 6,400 Hz and
   watch the blue wave slow down instead of speed up.
2. Students set the tone to 7,000 Hz and confirm the chapter's example: it
   appears at 5,800 Hz.
3. Students change the sample rate to 16,000 Hz and note that the same tone is
   now captured correctly.

### Challenge (7 minutes)

Students complete the six challenges. Ask them to write the folding
calculation for each answer before they submit.

### Discussion Questions

1. Does a tone above the Nyquist limit disappear, get quieter, or turn into
   something else?
2. Why would a recording device filter out high frequencies before sampling?
3. Is a higher sample rate always better? When does it stop helping?

### Assessment

The sim records 6 first-attempt answers. Mastery is 5 of 6 correct within
1 Hz. Moving the controls is exploration, not evidence.

## References

1. [Nyquist-Shannon sampling theorem](https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem) -
   Wikipedia article on the sample rate needed to capture a signal.
2. [Aliasing](https://en.wikipedia.org/wiki/Aliasing) -
   Wikipedia article on how high frequencies fold into false low ones.
3. [Nyquist frequency](https://en.wikipedia.org/wiki/Nyquist_frequency) -
   Wikipedia article on the half-sample-rate limit.

## Related Resources

- [Chapter 3: Sound and Digital Audio](../../chapters/03-sound-and-digital-audio/index.md)

??? note "Original specification"

    Type: microsim
    **sim-id:** sampling-explorer<br/>
    **Library:** p5.js<br/>
    **Status:** Specified<br/>
    **Template:** https://github.com/dmccreary/token-efficiency/tree/main/docs/sims/sampling-parameter-explorer<br/>
    **Bloom Level:** Apply<br/>
    **Bloom Verb:** calculate<br/>
    **Learning Objective:** The learner will calculate the frequency a sampled tone appears to have, given its true frequency and the sample rate, for 6 challenge tones, with at least 5 of 6 correct.

    **Prerequisites:** sampling, sample rate, frequency, Nyquist limit, aliasing (all defined in the sections above this block).

    **Evidence of Mastery:** For each of the 6 challenge tones the learner types the apparent frequency in hertz before the sim shows it. An answer is correct when it is within 1 Hz of the Apparent frequency column in Content. Mastery is 5 of 6 correct. Changing the tone and the sample rate and watching the dots is exploration, not evidence.

    **Misconceptions:** (1) A tone above half the sample rate disappears. (2) A tone above half the sample rate is recorded at its true frequency but quietly. (3) A higher sample rate always sounds better regardless of the sound's frequency.

    **Instructional Rationale:** Apply-level calculation needs the learner to use the folding rule on new numbers. Committing a number first, and then seeing the sampled dots form a wave of a different frequency, shows that the lost tone reappears as a false one.

    **Content:**

    The sim shows one true sine wave, its sample dots, and the wave the dots suggest. The folding rule used for the apparent frequency is given in the Rules field.

    Challenge tones, in this order:

    | # | True frequency (Hz) | Sample rate (Hz) | Nyquist limit (Hz) | Apparent frequency (Hz) | Why (shown as feedback) |
    |---|---|---|---|---|---|
    | 1 | 1,000 | 12,800 | 6,400 | 1,000 | 1,000 is below 6,400, so it is captured correctly. |
    | 2 | 6,000 | 12,800 | 6,400 | 6,000 | 6,000 is just below the limit, so it is captured correctly. |
    | 3 | 7,000 | 12,800 | 6,400 | 5,800 | 7,000 is above 6,400, so it folds to 12,800 - 7,000 = 5,800. |
    | 4 | 9,000 | 12,800 | 6,400 | 3,800 | 9,000 is above 6,400, so it folds to 12,800 - 9,000 = 3,800. |
    | 5 | 3,000 | 4,000 | 2,000 | 1,000 | 3,000 is above 2,000, so it folds to 4,000 - 3,000 = 1,000. |
    | 6 | 5,000 | 8,000 | 4,000 | 3,000 | 5,000 is above 4,000, so it folds to 8,000 - 5,000 = 3,000. |

    Exploration controls: true frequency from 100 to 9,000 Hz in steps of 100 Hz, default 1,000 Hz; sample rate chosen from 4,000, 8,000, 12,800 and 16,000 Hz, default 12,800 Hz.

    **Provenance:** The 12,800 Hz and 16,000 Hz rates are the kit's `MIC_SAMPLE_RATE` and test 05 `RATE`. The other tones and rates are illustrative, and the sim labels them "illustrative."

    **Rules:** The Nyquist limit is the sample rate divided by 2. For a true frequency f and sample rate fs, if f <= fs / 2 the apparent frequency equals f. If fs / 2 < f <= fs, the apparent frequency is fs - f. The challenges use only frequencies that satisfy one of those two cases (no frequency equals exactly fs / 2 or fs). In exploration, the true frequency is limited to values below the sample rate: if the learner picks a sample rate that is not above the current frequency, the frequency is lowered to the largest allowed value below the rate. When f equals fs / 2 exactly, the sim shows the message "at the Nyquist limit: the samples cannot show this tone reliably" instead of an apparent frequency.

    **Learner Activity:**

    1. The learner explores: changes the true frequency and the sample rate and watches the dots and the wave they suggest.
    2. The learner starts the challenges. Challenge 1 shows a true frequency and a sample rate.
    3. The learner types the apparent frequency in hertz and submits.
    4. The sim shows the dots and the suggested wave for that tone, with the correct answer and the Why text.
    5. After challenge 6, the sim shows the score. The learner should notice that tones 3 to 6 reappeared at lower frequencies, never at higher ones.

    **Feedback:** 6 challenges, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The apparent frequency is <answer> Hz: <Why>". The correct answer is revealed immediately after each submission, and a running score "n of 6" is shown.

    **Starting State:** The explorer is shown at 1,000 Hz and 12,800 Hz with the question "What wave do these dots suggest?"

    **Chapter Anchors:** The chapter states the kit microphone rate is 12,800 Hz with a Nyquist limit of 6,400 Hz, and that a 7,000 Hz tone sampled at 12,800 Hz appears at 5,800 Hz.
