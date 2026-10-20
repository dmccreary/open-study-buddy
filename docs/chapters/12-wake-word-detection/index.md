---
title: "Wake-Word Detection"
description: "How a Pico can listen for a spoken phrase: log band features, a rolling window, mean subtraction, unit normalization, a dot-product score against an enrolled template, thresholds and cooldown, false accepts and false rejects, and the honest limits of template matching."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 13:13:04"
version: 1.11
---

# Wake-Word Detection

## Summary

This chapter builds an always-on wake-word detector from the tools of earlier chapters. Students extract features, normalize them, and score a rolling window against an enrolled template with a dot product. They tune thresholds, examine false accepts and false rejects, and learn the honest limits of template matching compared with trained models.

## Concepts Covered

This chapter covers the following 24 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Feature Extraction | 27 |
| Mean Subtraction | 15 |
| Rolling Window | 3 |
| MFCC Features | 2 |
| Unit Normalization | 14 |
| Dot Product Score | 13 |
| Wake Word | 27 |
| Hey Pico Phrase | 8 |
| Always-On Listening | 3 |
| Template Matching | 13 |
| Wake Confirmation Beep | 2 |
| Wake-Word Enrollment | 6 |
| Template Correlation | 12 |
| Wake Cooldown | 1 |
| Window Fill Percentage | 2 |
| Detection Threshold | 5 |
| Single-Speaker Limits | 2 |
| Detector Self-Test | 2 |
| False Accept | 2 |
| False Reject | 2 |
| Speaking Pace Sensitivity | 1 |
| Trained Keyword Spotting | 1 |
| Detector Math Test | 1 |
| Threshold Trade-Off | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../01-personal-agents-architecture/index.md)
- [Chapter 7: Buttons, State Machines, and Device Modes](../07-buttons-and-device-modes/index.md)
- [Chapter 8: I2S Audio: Recording and Playing Sound](../08-i2s-audio/index.md)
- [Chapter 9: Signal Processing and the FFT](../09-signal-processing-fft/index.md)
- [Chapter 10: High-Performance MicroPython](../10-high-performance-micropython/index.md)
- [Chapter 11: Microphone Calibration and Push-to-Talk](../11-mic-calibration-push-to-talk/index.md)

---

## Listening for a Name

Push-to-talk, from [Chapter 11](../11-mic-calibration-push-to-talk/index.md), asks the student to press a button before speaking. A **wake word** asks them to say a name instead: the device is listening for one particular phrase, and only when it hears it does it start paying attention. This chapter builds a small detector for the phrase "Hey Pico" from parts you already have, and then spends as much time on its limits as on its design.

!!! mascot-welcome "Teach the Ears One Phrase"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    In this chapter you will teach your Study Buddy what your own "Hey Pico" looks like and score every second of sound against it. Let's listen closely! You will also measure where the detector fails, because an honest detector is a useful one.

## The Wake Word and the "Hey Pico" Phrase

A wake word is the phrase that says "this is for you." The device's default is **"Hey Pico"**, the **Hey Pico phrase**. Two choices make it a good phrase for a template detector. It has several different sounds in a row (an "h" breath, a gliding "ay", a "p" burst, an "ee", a "k" burst, an "oh"), so its pattern over time is distinctive. And it takes about 0.7 to 0.9 seconds to say, which fits in the one-second window the detector uses. A very short word, such as "Pico" alone, gives the template less to match, and a long sentence would need a bigger window. [Chapter 16](../16-school-agent-calendar/index.md) comes back to choosing a different phrase for a school.

It helps to see the three jobs in the listening chain, because they are easy to confuse.

| Job | Question it answers | Built in |
|-----|---------------------|----------|
| Level gate and VAD | Is there sound loud enough to be speech? | [Chapter 11](../11-mic-calibration-push-to-talk/index.md) |
| Wake-word detector | Was that the phrase "Hey Pico"? | This chapter |
| Transcription | What words were said after it? | The agent, in [Chapter 13](../13-wifi-http-agent-link/index.md) and [Chapter 14](../14-streaming-security-resilience/index.md) |

The detector never understands words. It only asks whether the last second of sound has the same shape as the second you enrolled.

### Always-On Listening Needs Approval

**Always-on listening** means the microphone stays open all the time so the detector can hear the wake word without a button press. It is the way commercial smart speakers work, and it is an **advanced option** in this book. Push-to-talk stays the default. Before a device runs always-on, a parent, teacher, or school must approve it by the process in [Chapter 17](../17-privacy-responsible-listening/index.md), because an open microphone raises privacy questions that a button does not.

The test program `09-live-detector.py` is built around that rule. Its default listens only while MODE is held, which lets you try the detector without an open microphone. It has a flag, `ALWAYS_ON_APPROVED`, that is `False`. A flag in a file is not an approval, and the program keeps the LED on and "ALWAYS ON" on the screen whenever the microphone is open.

!!! mascot-warning "Approval Comes Before the Flag"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Do not set `ALWAYS_ON_APPROVED` to `True` because you are curious. Complete Chapter 17's approval first, and leave the LED and the on-screen label alone so everyone nearby can tell the microphone is open.

## Template Matching

**Template matching** is detection by comparison. You record the phrase once, keep a summary of it (the **template**), and later ask of any stretch of sound: how similar is this to the template? If the similarity is high enough, call it a match. It is the simplest detector there is: there is no training on thousands of speakers and no neural network, and the "learning" is storing your own voice.

The comparison needs two ingredients. A **summary** that keeps what makes "Hey Pico" recognizable and throws away what does not, such as how loud it was and how the room colored it. And a **similarity score** that is high when two summaries agree and low when they do not. The next sections build the summary (features, a rolling window, mean subtraction, normalization) and then the score (a dot product).

## Feature Extraction

**Feature extraction** turns one 40 ms frame of 512 samples into a short list of numbers that describe it, so the detector compares 16 numbers per frame instead of 512 samples. The features here come from the spectrum of the frame, which Chapter 9 explains in depth: an FFT gives 256 frequency bins of 25 Hz, and **log-spaced bands** group neighboring bins into 16 bands from 100 Hz to 6,400 Hz. A band is narrow where our ears are sensitive to small differences and wide where they are not.

| Band | Bins | Hz | Band | Bins | Hz |
|------|------|----|------|------|----|
| 0 | 4 | 100-125 | 8 | 32-40 | 800-1,025 |
| 1 | 5-6 | 125-175 | 9 | 41-53 | 1,025-1,350 |
| 2 | 7-8 | 175-225 | 10 | 54-69 | 1,350-1,750 |
| 3 | 9-10 | 225-275 | 11 | 70-90 | 1,750-2,275 |
| 4 | 11-14 | 275-375 | 12 | 91-116 | 2,275-2,925 |
| 5 | 15-18 | 375-475 | 13 | 117-151 | 2,925-3,800 |
| 6 | 19-24 | 475-625 | 14 | 152-196 | 3,800-4,925 |
| 7 | 25-31 | 625-800 | 15 | 197-255 | 4,925-6,400 |

The feature for a band is the natural logarithm of its energy, \( f_j = \ln\!\left(\sum_{k \in \text{band } j} |X_k|^2 + 1\right) - 20 \), where \( X_k \) is bin \( k \) of the windowed FFT. The logarithm matters for the same reason that "bits" worked for loudness: a sound twice as strong adds a fixed amount, instead of doubling the number. The "+1" avoids the log of zero, and subtracting 20 only keeps the numbers small (mean subtraction, below, removes any constant anyway). This is the `features.py` file; this table is the same layout as the spectrum display in Chapter 9, but the detector does not depend on Chapter 9's code, because enrollment and detection both use this file's table. `02-band-table.py` prints it.

*Worked example.* Two synthetic frames show what the features look like (made by `features.Extractor` on a computer; they are not microphone recordings). A pure 1,000 Hz tone lands in band 8 (800-1,025 Hz) and spills into band 9, and every other band is near the floor of the scale.

| Bands 0-7 | -20.0, -20.0, -16.0, -17.6, -20.0, -17.5, -13.8, -15.3 |
|-----------|-----------------------------------------------------------|
| **Bands 8-15** | **13.0, 11.3,** -12.3, -14.2, -15.0, -13.4, -13.8, -12.5 |

A frame of plain noise at 13.0 bits gives something quite different: 4.3, 4.5, 4.6, 4.1, 5.2, 5.2, 5.8, 5.3, 5.5, 5.7, 6.1, 6.8, 6.8, 7.1, 7.7, 7.8, a gentle climb from the low bands to the high bands. That climb has nothing to do with the sound. The upper bands are wider (band 15 holds 59 bins, band 0 holds 1), so they add up more bins even for white noise. It is a steady **tilt** built into the features, and it is exactly the kind of thing mean subtraction removes.

### MFCC Features, and What This Book Uses Instead

Speech systems usually use **MFCC features** (mel-frequency cepstral coefficients). They are computed in five steps: take the spectrum, group it into bands spaced on the mel scale (roughly linear below 1 kHz and logarithmic above), take the log of each band's energy, apply a **discrete cosine transform** (DCT) to those logs, and keep the first 12 or 13 coefficients. The DCT separates the broad shape of the spectrum from fine detail and compacts the information into fewer numbers.

This book stops after the log. The 16 log band energies are MFCC-like, not true MFCCs: the bands are log-spaced instead of mel-spaced and there is no DCT. The reason is cost, since the DCT adds \( 12 \times 16 = 192 \) multiplications per frame to a budget with little to spare, and the log bands give a template matcher most of what it needs. `features.dct()` is the bridge: apply it to the 16 values and you have MFCC-like coefficients. The test `01-detector-math-test.py` verifies one property worth knowing: adding the same number to all 16 band values changes only coefficient 0, which is why MFCC systems shrug off a change in overall gain. Swapping the log bands for DCT coefficients, and keeping everything else the same, is a good experiment.

### The Frame Budget

Every frame must be fully processed within the 40 ms frame budget of Chapter 8, and the FFT is the expensive step. A 512-point FFT is 2,304 butterflies (Chapter 9). If the whole 40 ms were spent on the transform, each butterfly would get \( 40{,}000 / 2{,}304 = 17.4 \) microseconds, and in reality the loudness calculation, the band sums, the window, the score, and the display need a share too (Chapter 8 measured about 10 ms for the loudness alone). The `Extractor` in `features.py` carries a plain-Python transform as a readable reference. It is expected to be several times over budget, and `03-feature-timing.py` prints the real number, step by step. [Chapter 10](../10-high-performance-micropython/index.md) shows how to make the transform fast. Whatever you build there plugs in as `Extractor(spectrum_fn=fast)`, where `fast(re, im, power)` reads the windowed samples from `re` and fills `power` with the squared magnitudes. Until it does, the programs here that must keep pace with the microphone report their overruns, and the programs that record first and score afterwards (`05`, `07` and `08`) work at any speed.

## The Rolling Window

A phrase is a pattern over time, so one frame's 16 numbers are not enough. The **rolling window** is the memory of the last \( K \) frames of features, kept as a ring: each new frame overwrites the oldest, and the window always holds the most recent second. With 25 frames of 40 ms, the window spans \( K = 25 \) frames \( = 1.00 \) s, which holds "Hey Pico" with a little room to spare. The window is a block of \( 25 \times 16 = 400 \) numbers, and as 4-byte floats that is \( 25 \times 16 \times 4 = 1{,}600 \) bytes.

| Memory item | Bytes |
|-------------|-------|
| Rolling window (25 frames x 16 floats) | 1,600 |
| Template (25 x 16 floats) | 1,600 |
| Running sums and flags | 153 |
| Extractor (FFT arrays, Hann window, tables) | 10,240 |
| **Total** | **13,593** |

(`02-band-table.py` prints this table, plus one extra 64-byte frame vector, and on the Pico it reports the heap actually used.) That is small next to the 150 KB recording buffer of Chapter 11.

The window is empty when the program starts and after any reset. The **window fill percentage** is how much of it holds real frames: \( 100 \times \text{frames stored} / K \). One frame is 4 percent, thirteen is 52 percent, twenty-four is 96 percent, and twenty-five is 100 percent. The detector does not score a window below 100 percent, because the mean subtraction and normalization that follow assume 25 real frames, and a half-empty window would be a strange, unrelated shape. After a reset the window needs 25 frames, one second, to fill again.

!!! mascot-warning "Don't Score a Half-Empty Window"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A window that is only 40 percent full holds frames of zeros, and normalizing those can produce high scores from nothing. `Window.score()` returns `None` until the fill percentage reaches 100, and the screen of the live detector shows the fill so you can see why it is quiet for the first second.

## Mean Subtraction

**Mean subtraction** removes whatever is constant in each band over the window. For each of the 16 bands, add up that band's value in all 25 frames, divide by 25 to get the band's average, and subtract the average from every frame's value of that band:

\[ \tilde{x}_{ij} = x_{ij} - \frac{1}{K} \sum_{i'=1}^{K} x_{i'j} \]

Here \( x_{ij} \) is the feature of frame \( i \) in band \( j \). What is left is how each band moves up and down over the second, with the steady part gone. The steady part is mostly not the phrase. It is the microphone's frequency response, the hum of the room, the tilt that wider bands add (the climb in the noise frame above), and the overall gain, which in the log domain is just a number added to every band. All of these are the same in every frame, so all of them vanish.

*Worked example.* Take a window of 3 frames and 2 bands, small enough to do by hand: frame 0 is (3, 9), frame 1 is (4, 8), frame 2 is (5, 7). Band 0 averages \( (3 + 4 + 5)/3 = 4 \) and band 1 averages \( (9 + 8 + 7)/3 = 8 \). After subtraction the window is (-1, 1), (0, 0), (1, -1): band 0 rises through the window while band 1 falls. Now give the microphone a different tone, say +6 in band 0 and -3 in band 1 in every frame: (9, 6), (10, 5), (11, 4). The averages are 10 and 5, and the result is the same (-1, 1), (0, 0), (1, -1). The colouring changed and the subtracted window did not. This is why the course description says mean subtraction is needed: without it, a different room or a different microphone would shift every feature and the template would stop matching.

!!! mascot-thinking "Subtract What Stays the Same"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Think of it as asking each band "how did you change?" instead of "how big were you?" A steady hum, a muffled microphone, and a louder voice all give the same answer: not at all.

## Unit Normalization

**Unit normalization** scales the whole mean-subtracted window so its length is 1. The length of the 400 numbers is the square root of the sum of their squares, and normalizing divides every number by it:

\[ \hat{x}_{ij} = \frac{\tilde{x}_{ij}}{\lVert \tilde{x} \rVert}, \qquad \lVert \tilde{x} \rVert = \sqrt{\sum_{i,j} \tilde{x}_{ij}^{\,2}} \]

This removes how big the ups and downs are. A person who speaks closer to the microphone has a larger contrast between speech and noise, so the swings in the features are bigger; normalizing makes a loud speaker and a soft one comparable.

*Worked example.* The subtracted window from above is (-1, 1), (0, 0), (1, -1). Its squares add to \( 1 + 1 + 0 + 0 + 1 + 1 = 4 \), so its length is 2. Dividing by 2 gives (-0.5, 0.5), (0, 0), (0.5, -0.5), whose length is \( \sqrt{0.25 \times 4} = 1 \). If the speaker had been twice as close, the swings would have been twice as big, (-2, 2), (0, 0), (2, -2), with length 4, and dividing by 4 gives the same (-0.5, 0.5), (0, 0), (0.5, -0.5). The same shape comes out at any strength. The test `01-detector-math-test.py` checks the property on a larger synthetic window: halving the depth of the pattern leaves the score at 1.000.

A window of pure silence has no swings at all and its length is zero, so there is nothing to divide by. The code returns a score of 0 in that case. The level gate of Chapter 11 keeps such windows from being scored in the first place.

## The Dot Product Score and Template Correlation

The **dot product** of two lists of numbers is the sum of the products of their matching entries. For two windows that have each been mean-subtracted and normalized to length 1, it measures how well their shapes agree, and it has a geometric meaning: it is the cosine of the angle between the two as 400-dimensional arrows. The **dot product score** is that number:

\[ s = \sum_{i,j} \hat{t}_{ij}\, \hat{x}_{ij} = \cos\theta \]

where \( \hat{t} \) is the template and \( \hat{x} \) is the live window. Arrows pointing the same way give \( s = 1 \), arrows at a right angle give 0, and opposite arrows give -1. Because both lists are zero-mean in every band, this score is also the correlation coefficient between the window and the template, which is why the detector's scoring is called **template correlation**.

The `Window` class in `detector.py` keeps a ring of 25 frames and a template of the same shape, and the score is one pass of 400 multiply-adds. Here is the toy window from the last two sections scored against a toy template. The template is (-0.5, 0.5), (0, 0), (0.5, -0.5). Four windows are scored in the explorer below; the values were checked with the `detector.py` functions.

| Window | Frames (band 0, band 1) | After subtraction | Length | Dot with template | Score |
|--------|------------------------|--------------------|--------|-------------------|-------|
| W1: the pattern in another room | (3, 9), (4, 8), (5, 7) | (-1, 1), (0, 0), (1, -1) | 2.00 | 2.00 | **1.00** |
| W2: the pattern, twice as strong | (2, 12), (4, 10), (6, 8) | (-2, 2), (0, 0), (2, -2) | 4.00 | 4.00 | **1.00** |
| W3: the pattern backwards in time | (5, 7), (4, 8), (3, 9) | (1, -1), (0, 0), (-1, 1) | 2.00 | -2.00 | **-1.00** |
| W4: something else | (3, 6), (4, 8), (6, 7) | (-1.33, -1), (-0.33, 1), (1.67, 0) | 2.58 | 1.00 | **0.39** |

W1 and W2 differ from the template in colouring and strength and still score 1.00. W3 has the right band values in the wrong order, and scores -1.00, so the score cares about the order in time. W4 is partly similar and scores 0.39. On a larger window (25 frames of 16 bands, synthetic, from the math test), the same story holds: the template's own window scores 1.000000; adding 3.0 to every feature, or a different steady offset to each band, still scores 1.000000; the pattern upside down scores -1.000000; and 200 random windows scored 0.0001 on average with a spread of 0.052, which matches the theory of \( 1/\sqrt{384} = 0.051 \) (the 400 numbers have 16 band means removed, leaving 384 free ones).

#### Diagram: Template Score Explorer

<details markdown="1">
<summary>Template Score Explorer</summary>
Type: microsim
**sim-id:** template-score-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the template score of 4 small windows by mean subtraction, unit normalization and a dot product, within 0.02 of the correct value in at least 3 of the 4.

**Prerequisites:** feature, window, mean subtraction, unit normalization, dot product score, template (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 4 challenge windows the learner types a score before the sim reveals it. A score is correct when it is within 0.02 of the Score column in Content. Mastery is 3 of 4 correct on the first attempt. Stepping through the worked window in exploration is exploration, not evidence.

**Misconceptions:** (1) A louder or stronger window scores higher. (2) A steady offset in a band changes the score. (3) A negative score means "no similarity" instead of "the opposite pattern". (4) The order of the frames does not matter.

**Instructional Rationale:** Apply-level calculation needs a procedure with a checkable answer. The windows are small enough (3 frames, 2 bands) to calculate by hand, and four challenges are chosen so that each breaks one of the misconceptions.

**Content:**

All windows have 3 frames and 2 bands. Each frame is written (band 0, band 1). The template is already mean-subtracted and length 1: (-0.5, 0.5), (0, 0), (0.5, -0.5). The sim labels all windows "synthetic".

The worked window, used in exploration: E = (10, 2), (10, 4), (10, 6). Band means 10 and 4. After subtraction: (0, -2), (0, 0), (0, 2). Length 2.83. Dot with the template -2.00. Score -0.71.

| # | Window | Band means | After subtraction | Length | Dot | Score | Why (shown as feedback) |
|---|--------|------------|--------------------|--------|-----|-------|-------------------------|
| 1 | W1: (3, 9), (4, 8), (5, 7) | 4, 8 | (-1, 1), (0, 0), (1, -1) | 2.00 | 2.00 | 1.00 | Subtracting the band means leaves exactly the template's shape, so the angle is 0. |
| 2 | W2: (2, 12), (4, 10), (6, 8) | 4, 10 | (-2, 2), (0, 0), (2, -2) | 4.00 | 4.00 | 1.00 | Twice the strength, same shape: normalizing divides by 4 and gives the template, so strength does not matter. |
| 3 | W3: (5, 7), (4, 8), (3, 9) | 4, 8 | (1, -1), (0, 0), (-1, 1) | 2.00 | -2.00 | -1.00 | The same band movements in the opposite order are the opposite pattern, so the score is -1. |
| 4 | W4: (3, 6), (4, 8), (6, 7) | 4.33, 7 | (-1.33, -1), (-0.33, 1), (1.67, 0) | 2.58 | 1.00 | 0.39 | Only partly the same shape: the dot product is 1.00 but the length is 2.58, so the score is 1.00 / 2.58. |

**Provenance:** Synthetic windows written for this sim; the arithmetic matches the chapter's toy-window sections and was checked with Python.

**Rules:** Band mean = sum of that band's values over the 3 frames, divided by 3. After subtraction = value - band mean. Length = square root of the sum of squares of the 6 subtracted numbers. Dot = sum over the 6 entries of subtracted value times template value. Score = dot divided by length, or 0 if the length is below 0.000001. Scores are shown to 2 decimals and compared with a tolerance of 0.02.

**Learner Activity:**

1. The learner steps through the worked window E in three stages: mean subtraction, normalization, dot product. At each stage the sim shows the numbers. The learner should notice that the band that never moves (band 0 of E) contributes nothing.
2. The learner starts the 4 challenges. Window W1 is shown with the template.
3. The learner types the score and submits.
4. The sim shows the three stages with their numbers and the Why text.
5. After challenge 4, the sim shows the score. The learner should notice that W1 and W2 differ in strength and colouring but score the same, and that W3 has the same numbers as W1 in a different order.

**Feedback:** 4 challenges, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The score is <score>: <Why>". The score is revealed right after each submission, and a running score "n of 4" is shown.

**Starting State:** The worked window E is shown before any stage, with the question "What does this window score against the template?"

**Chapter Anchors:** The chapter states that W1 and W2 score 1.00, W3 scores -1.00, W4 scores 0.39, and that the template is (-0.5, 0.5), (0, 0), (0.5, -0.5).
</details>

!!! mascot-encourage "Four Hundred Numbers Is Still Just One Idea"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    A window of 400 numbers can feel like a lot, but it is the same three steps you just did on six numbers: subtract the averages, scale to length 1, add up the products. If a step feels shaky, redo the toy window with a pencil and then check yourself against the table.

### Making the Score Cheap

The textbook steps build a mean-subtracted copy of the window and a normalized copy of that, and then multiply. That is clear, and it allocates new arrays every frame. The live loop avoids it with two facts. The template has zero mean in every band, so its dot product with the mean-subtracted window equals its dot product with the raw window; no subtracted copy is needed. And the length of the mean-subtracted window follows from running sums that the window keeps for each band: the sum \( S_j \) and the sum of squares \( Q_j \) of the 25 values, so that \( \lVert \tilde{x} \rVert^2 = \sum_j \left( Q_j - S_j^2 / K \right) \). The window updates the sums as each frame enters and leaves. `01-detector-math-test.py` checked the fast score against the textbook steps for 700 frames; the largest difference was \( 7 \times 10^{-7} \). The window also recomputes the sums from scratch every 250 frames (10 seconds) so rounding errors cannot build up over hours.

## Enrolling the Phrase

**Wake-word enrollment** is recording your own "Hey Pico" and turning it into the template. It builds one template from several windows, and `05-enroll.py` walks through the steps.

1. The student holds MODE and says "Hey Pico" five times, one recording each. The Chapter 11 recorder runs voice activity detection and finds the first loud frame of each.
2. The window for each utterance starts 3 frames before that first loud frame (`LEAD_FRAMES`), so every recording puts the same stretch of the phrase in the same rows. It spans 25 frames. A recording shorter than that is rejected, as is one that clipped or has no speech.
3. Each window gets its 25 frames of features, is mean-subtracted, and is made length 1.
4. The five are averaged and the average is made length 1 again, which gives the template.
5. Each utterance is scored against the finished template, and the console prints these as its **consistency**.
6. UP saves the template to `wake_template.bin`: 8 header bytes (a name, the window size, the band count, and a check of the band table) plus \( 25 \times 16 \times 4 = 1{,}600 \) bytes, 1,608 in all. Like the calibration, it is written only on that button press.

Averaging matters because any single utterance has quirks: a slightly longer "ay", a breath. The average keeps what the five share. The consistency numbers are a first look at how repeatable your phrase is. In a synthetic test on a computer (five synthetic utterances with a 4 percent random variation in pace), the consistencies were 0.847, 0.686, 0.879, 0.858 and 0.705. Real values for a person are for you to measure with `05-enroll.py`. The script flags anything under 0.5, a starting value, so you can redo an enrollment where one recording was odd.

!!! mascot-tip "Enroll the Way You Will Use It"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Enroll in the room, at the distance, and at the pace and volume you will really use. The template is a photograph of one voice in one place, and the closer the real use is to that photograph, the better it matches.

### Single-Speaker Limits

The template is built from one speaker, on one microphone, in one room, so it can recognize that speaker much better than anyone else. This is the **single-speaker limit**. Another person's "Hey Pico" has a different pitch and a different vocal-tract length, so the spectral bands move in different places. In the end-to-end synthetic test described below (`tools/pipeline-synthetic-test.py`, with clean synthetic vowels), a voice synthesized with a higher pitch and shorter vocal tract was rejected 100 percent of the time at a threshold of 0.70, and a lower voice 5 percent of the time. Those are synthetic voices; they do not say how the real kit treats real children and adults. The honest reading is that the detector may need to be enrolled for each person who will use it, and `08-threshold-sweep.py` lets you measure it with a classmate.

## Deciding: Threshold, Cooldown, and the Beep

Each frame produces a score, and the detector must decide when a score is high enough. The **detection threshold** is the score at or above which the detector fires. A threshold of 0.70 means the live window must have at least 0.70 correlation with the template. The value in `detector.py` is a starting point that is not yet validated on the kit; you set it from measurements with `08-threshold-sweep.py`. For scale, random windows spread by only 0.05, so scores of 0.3 and higher are far beyond chance. But real sounds that are not random, such as other words, score much higher than random ones, and where the threshold goes between those and "Hey Pico" is the subject of the trade-off section.

Three more rules make a decision from a score.

- **Window full.** Nothing is scored until the fill percentage reaches 100.
- **Speech present.** At least 8 of the 25 frames (320 ms) must have had the level gate from Chapter 11 open. Otherwise the window is background noise, and a normalized window of noise should not be allowed to correlate by accident. The `Detector` returns a score of `None` in that case.
- **Cooldown.** After a detection the detector ignores scores for 50 frames (2 seconds).

The **wake cooldown** is needed because the window slides one frame at a time. The score rises as the phrase enters the window, stays high for a few frames while the alignment is close, and falls again, so a single "Hey Pico" produces several consecutive scores above the threshold. The math test shows it: a stream with one phrase and one later blip gave 5 scores at or above 0.70 (four in a row for the phrase), and a 4-frame cooldown turned them into 2 detections, one for each. Note that the detector fires on the first frame at or above the threshold, and the peak may come a frame or two later.

The **wake confirmation beep** tells the student that the device heard them. The program closes the microphone, plays a short tone, and only then continues. This follows Chapter 8's self-hearing rule: the speaker's beep must never reach the open microphone and be scored. The beep is a sine at 880 Hz for 120 ms (Chapter 8's tone generation), with 10 ms fades and a low volume: \( 12{,}800 \times 0.12 \times 2 = 3{,}072 \) bytes. After the beep, the detector resets its window (fill back to 0 percent), so it needs a full second of new sound before it can score, and the cooldown runs during that second.

```python
def on_detection():
    text("Hey Pico!", config.GREEN, "score above {:.2f}".format(THRESHOLD))
    play_beep()                 # the microphone is CLOSED here
    det.reset()                 # window back to 0% full
    det.start_cooldown()        # and ignore the next 2 seconds
```

`play_beep()` writes the beep and a quiet tail to the speaker and waits for its buffer to drain, as in Chapter 8. The sequence for a detection looks like this:

| Step | What happens | Window fill |
|------|--------------|-------------|
| 1 | Score reaches the threshold; microphone closes | 100% |
| 2 | Beep plays, then silence while the buffer drains | (microphone closed) |
| 3 | `reset()` and `start_cooldown()`; microphone reopens | 0% |
| 4 | Frames arrive; the window refills | 4% per frame |
| 5 | Window full; cooldown over after 50 frames (2 s) | 100% |

So the earliest a second detection can happen is about 2 seconds after the first. The `update()` method that ties the rules together is short.

```python
def update(self, feats, bits):
    loud = self.gate.update(bits)
    self.window.push(feats, loud)
    score = None
    if self.window.is_full() and self.window.active_count >= self.min_active:
        score = self.window.score(self.template)
    fired = False
    if self.cooldown > 0:
        self.cooldown -= 1
    elif score is not None and score >= self.threshold:
        fired = True
        self.start_cooldown()
    return score, fired
```

`feats` is the frame's 16 features and `bits` is its loudness from Chapter 11's `frame_stats()`. The method pushes the frame into the window, scores only when the window is full and enough of it was loud, and fires when no cooldown is running and the score reaches the threshold.

## Testing the Detector

A detector should be able to prove it works before anyone trusts it. This chapter has two tests, one for the math and one for the device.

The **detector math test**, `01-detector-math-test.py`, checks the pure math on synthetic windows and needs no hardware. It checks that every band's mean is 0 after subtraction (the largest was \( 2 \times 10^{-8} \)); that the length after normalizing is 1; that a window scores 1.000000 against its own template; that the score ignores a steady offset and a change of depth; that random windows score near 0; that the running-sums score matches the textbook steps; that the fill percentage goes 0, 4, 20, 40, 80, 96, and 100 percent as expected; that the cooldown and the speech-present rule work; that the template file saves and loads in 1,608 bytes; and that the DCT changes only coefficient 0 when a constant is added. Its last line is PASS or FAIL.

The **detector self-test**, `06-self-test.py`, runs on the Pico against your enrolled template and checks things the math test cannot: that the template scores 1.0000 against itself, how fast the score falls when the window is shifted by 1, 2, or 3 frames (a measure of how fussy your template is), that random windows and a second of your room's noise score low, and, last, the **time per frame**. It adds up the cost of the features, the window update, and the score and compares the total with the 40 ms budget. That last line is the link to Chapter 8's frame overrun: a detector that is right but too slow loses audio, and the self-test says so.

On a computer, the fake-microphone run of the shift test, on a synthetic smooth pattern, gave 0.891, 0.617, and 0.292 for shifts of 1, 2, and 3 frames. Real speech features change faster, so expect your template to be at least as fussy.

## False Accepts, False Rejects, and the Trade-Off

A detector can be wrong in two ways. A **false accept** is a detection when the wake word was not said: the device wakes up for a cough, a similar-sounding phrase, or a classmate's chatter. A **false reject** is a miss: the student says "Hey Pico" and nothing happens. They are measured differently. A false-reject rate is a fraction of the attempts you made on purpose: say it 20 times and count the misses. A false-accept rate needs a lot of audio that is not the wake word, and it is naturally counted per hour.

*Worked example (illustrative arithmetic).* Suppose a classroom produces 300 speech-like segments an hour that the level gate opens for (an assumption for the example, not a measurement), and that 1 percent of non-wake segments score above the threshold. That is \( 300 \times 0.01 = 3 \) false accepts an hour, which is a distracting device in a lesson. At 0.1 percent it would be 0.3 an hour. The numbers show why a detector that looks accurate per attempt can be annoying per hour.

The **threshold trade-off** is that moving the detection threshold changes the two errors in opposite directions. Raise it and the device ignores more imposters (fewer false accepts) but misses more of the real ones (more false rejects). Lower it and the reverse happens. Neither direction is free, and no setting is best for everyone. The table uses synthetic score distributions: 1,000 "Hey Pico" scores drawn near 0.80 and 1,000 other-sound scores drawn near 0.35, from the fixed-seed generator in `01-detector-math-test.py` (the shapes are invented to show the effect; real distributions are for `08` to find).

| Threshold | False rejects (of "Hey Pico") | False accepts (of other sounds) |
|-----------|-------------------------------|----------------------------------|
| 0.50 | 0.0% | 16.6% |
| 0.55 | 0.1% | 9.1% |
| 0.60 | 0.8% | 5.3% |
| 0.65 | 3.5% | 2.4% |
| 0.70 | 11.2% | 0.8% |
| 0.75 | 26.2% | 0.5% |
| 0.80 | 49.3% | 0.1% |
| 0.85 | 74.3% | 0.0% |
| 0.90 | 90.1% | 0.0% |

!!! mascot-thinking "There Is No Free Threshold"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    The two score distributions overlap, and the threshold only decides which error you accept more of. Lowering the false accepts always costs some false rejects, and the only way to improve both at once is a better detector, not a better number.

#### Diagram: Threshold Trade-Off Explorer

<details markdown="1">
<summary>Threshold Trade-Off Explorer</summary>
Type: microsim
**sim-id:** threshold-tradeoff-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Evaluate<br/>
**Bloom Verb:** judge<br/>
**Learning Objective:** The learner will judge which detection threshold, if any, meets stated limits on false rejects and false accepts in 4 scenarios, choosing the correct threshold or "none" in at least 3 of 4.

**Prerequisites:** detection threshold, score, false accept, false reject, threshold trade-off (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 4 scenarios the learner chooses one threshold from the table in Content, or "none", before the sim reveals the answer. A choice is correct when it equals the Answer column. Mastery is 3 of 4 correct on the first attempt. Moving the threshold control and watching the two error rates in exploration is exploration, not evidence.

**Misconceptions:** (1) A higher threshold is always safer. (2) There is always a threshold that satisfies both limits. (3) A false-accept rate per attempt is the same as per hour.

**Instructional Rationale:** Evaluate-level judgment means deciding against criteria, so each scenario states limits and the learner must test candidate thresholds against them. Scenario 3 has no valid answer, which makes the learner judge rather than pick the middle option.

**Content:**

The sim shows two score distributions as histograms: 1,000 scores for "Hey Pico" and 1,000 for other sounds, and a threshold line. All scores are synthetic and labelled "synthetic". For each threshold the sim shows the false-reject percentage (wake scores below the threshold) and the false-accept percentage (other scores at or above it).

| Threshold | False rejects | False accepts |
|-----------|---------------|---------------|
| 0.50 | 0.0% | 16.6% |
| 0.55 | 0.1% | 9.1% |
| 0.60 | 0.8% | 5.3% |
| 0.65 | 3.5% | 2.4% |
| 0.70 | 11.2% | 0.8% |
| 0.75 | 26.2% | 0.5% |
| 0.80 | 49.3% | 0.1% |
| 0.85 | 74.3% | 0.0% |
| 0.90 | 90.1% | 0.0% |

Scenarios, in this order. Among the thresholds that meet every limit, the answer is the one with the smallest sum of the two percentages; if no threshold meets every limit, the answer is "none".

| # | Scenario | Limits | Answer | Why (shown as feedback) |
|---|----------|--------|--------|--------------------------|
| 1 | A quiet bedroom where missing the phrase is annoying | False rejects at most 5% | 0.65 | 0.50 to 0.65 meet the limit; 0.65 has the fewest false accepts of them (2.4%). |
| 2 | A busy classroom where a false wake-up is disruptive | False accepts at most 1% | 0.70 | 0.70 and higher meet the limit; 0.70 has the fewest false rejects of them (11.2%). |
| 3 | A demo that must almost never miss and almost never wake by mistake | False rejects at most 10% and false accepts at most 1% | none | At 0.65 false accepts are 2.4% (too many) and at 0.70 false rejects are 11.2% (too many). No threshold meets both; the detector needs to be better, not retuned. |
| 4 | A shared class device with a patient user | False rejects at most 25% and false accepts at most 1% | 0.70 | 0.70 gives 11.2% and 0.8%. 0.75 has false rejects of 26.2%, which is over the limit. |

**Provenance:** The scores are synthetic: 1,000 "Hey Pico" scores drawn near mean 0.80 with standard deviation 0.08 (capped at 1.0) and 1,000 other scores near mean 0.35 with standard deviation 0.15, from the fixed-seed generator (seed 77) in `src/chapters/12-wake-word-detection/01-detector-math-test.py`. The percentages in the table are that script's output.

**Rules:** False reject = wake score < threshold. False accept = other score >= threshold. The threshold control has the range 0.50 to 0.90, step 0.05, default 0.70, unit score. Percentages are shown to 1 decimal. The scenario answer is chosen as stated in Content.

**Learner Activity:**

1. The learner moves the threshold and watches the two histograms' tails and the two percentages. The learner should notice that the two numbers move in opposite directions.
2. The learner starts the 4 scenarios. Scenario 1 is shown with its limits.
3. The learner chooses a threshold or "none" and submits.
4. The sim marks the threshold on the histograms, shows both percentages at the chosen value and at the answer, and shows the Why text.
5. After scenario 4, the sim shows the score. The learner should notice that scenario 3 cannot be solved by moving the threshold.

**Feedback:** 4 scenarios, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 4" is shown.

**Starting State:** The threshold is at 0.70 with both histograms visible and the question "How many of each error would you accept?"

**Chapter Anchors:** The chapter's trade-off table has the same 9 rows. It states that 0.70 gives 11.2% false rejects and 0.8% false accepts.
</details>

## The Honest Limits of Template Matching

A template matcher on a 12.8 kHz microphone is a modest detector, and this section says so plainly. It is a good way to learn how wake-word detection works, and with careful enrollment and a tuned threshold it can work for one person in one room. It should not be sold as a replacement for the products you know.

To see the shape of the limits, `tools/pipeline-synthetic-test.py` runs the real feature and detector code, on a computer, on synthetic speech-like audio from a vowel-formant synthesizer: a clean pattern of vowels and bursts, with fixed seeds. It enrolls five synthetic utterances and scores 80 more of the enrolled voice, 160 other clips (random phrases, near-misses of "Hey Pico", and noise), and clips at different paces and voices. The audio is synthetic and much cleaner than real speech, so these results are not accuracy claims. At a threshold of 0.70 the test rejected 7.5 percent of the enrolled voice's "Hey Pico" clips (6 of 80; 5 of those 6 were never scored at all, because too few of their frames opened the level gate) and accepted 18.1 percent of the other clips, because the made-up near-misses and random phrases share vowel shapes with the template. The real rates are what `08` measures.

### Speaking Pace Sensitivity

**Speaking pace sensitivity** is that the template matches only when the phrase is said at about the speed it was enrolled at. The window compares frame \( i \) of the live sound with frame \( i \) of the template, so if the student speaks 20 percent faster, the "p" burst that was in frame 13 arrives in frame 11, and every later part is early. Nothing stretches or squeezes the time axis to compensate. The synthetic pace sweep of the pipeline test shows the shape (enrolled voice, 40 clips per pace):

| Pace (time compared with enrollment) | Mean best score | Rejected at 0.70 |
|--------------------------------------|-----------------|------------------|
| 0.7 (faster) | 0.518 | 100% |
| 0.8 | 0.656 | 78% |
| 0.9 | 0.739 | 5% |
| 1.0 (as enrolled) | 0.787 | 5% |
| 1.1 | 0.689 | 22% |
| 1.2 (slower) | 0.559 | 100% |
| 1.3 | 0.429 | 100% |

The score falls off quickly on both sides, so a student who says it more slowly when tired or more quickly when rushed will be missed. A method that does stretch time is dynamic time warping, which aligns two sequences by finding the cheapest path through a table of frame-to-frame distances; it costs far more computation and is a good pointer for further reading, not something this book builds. A cheaper remedy is to enroll at more than one pace and keep more than one template.

### Trained Keyword Spotting

**Trained keyword spotting** is what commercial wake-word systems use instead. A small neural network is trained, on a computer, on thousands of recordings of many speakers saying the word and many hours of other sound, and then the trained weights are loaded onto the device. Such models learn what is common across speakers and paces and learn to reject confusable phrases, which is what a single enrolled template cannot do. They also take features like the MFCCs above as input. Building and training them is outside this book (the course description lists it as a topic not covered), but you now know what they are replacing: a template made from five of your own utterances.

The limits, summarized, are these.

- The template fits one speaker, microphone, and room; a new voice or a changed room may need re-enrolling.
- The window needs the phrase at about the enrolled pace.
- The detector knows no phonetics, so similar-sounding phrases can score high.
- The plain-Python transform cannot keep up with 40 ms frames; the live detector needs Chapter 10's work.
- Accuracy numbers are not claims until you have measured them.

!!! mascot-warning "Do Not Read Synthetic Numbers as Accuracy"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    The tables marked synthetic show how the math behaves and what shapes to expect, not how well your kit will hear "Hey Pico". Measure with `08-threshold-sweep.py`, at several thresholds, with several speakers and paces, before you claim a false-accept or false-reject rate.

## What Has and Has Not Been Measured

The code in this chapter ran, off the device, on a computer against a stand-in for the Pico's pins, microphone, and timer. The math is tested by `01-detector-math-test.py`, and the end-to-end pipeline by the synthetic test. Nothing here has run on the Pico yet. This table lists what you will have to measure.

| Question | Script | Status |
|----------|--------|--------|
| Milliseconds per frame for each feature step and the total | `03-feature-timing.py` and `06-self-test.py` | Not yet measured; the plain-Python FFT is expected to be over the 40 ms budget |
| How repeatable your "Hey Pico" is | `05-enroll.py` consistency | Not yet measured (the synthetic values are 0.686 to 0.879) |
| How fussy the alignment is for a real template | `06-self-test.py` shifted scores | Not yet measured |
| Scores for "Hey Pico" and for other phrases | `07-score-trace.py` | Not yet measured |
| False rejects and false accepts at several thresholds | `08-threshold-sweep.py` | Not yet measured; the chapter's tables are synthetic |
| Other speakers and other paces | `08-threshold-sweep.py` with `SPEAKER` and `PACE` set | Not yet measured; the tables above are synthetic |
| False accepts per hour in ordinary use | `09-live-detector.py`, with approval | Not yet measured; needs a fast transform and Chapter 17's approval |
| Detection latency | `09-live-detector.py` | Not yet measured |

## Putting It All Together

A frame of 512 samples becomes 16 log band energies. The last 25 frames form a rolling window, which is not scored until its fill reaches 100 percent. Mean subtraction removes each band's steady part, normalization removes the strength, and a dot product with the enrolled template gives a score from -1 to 1. If at least 8 frames of the window had speech, the score reaches the threshold, and no cooldown is running, the detector fires: the microphone closes, the confirmation beep plays, the window resets, and a 2-second cooldown starts. Enrollment builds the template from five of your own utterances. Push-to-talk stays the default listening mode, and always-on listening is an advanced option that needs approval.

Key takeaways:

- A wake word is a phrase the device listens for; "Hey Pico" is long enough and varied enough for a template detector.
- Feature extraction reduces a frame to 16 log band energies (MFCC-like, without the DCT); the plain-Python FFT is a reference that Chapter 10 replaces with a fast one.
- The rolling window holds 25 frames (1 second, 1,600 bytes); never score it before the fill percentage is 100.
- Mean subtraction removes steady colouring, unit normalization removes strength, and the dot product is the cosine of the angle between window and template.
- Enrollment averages five of your own utterances into `wake_template.bin`; the template fits one speaker, microphone, and room.
- The threshold, the speech-present rule, the cooldown, and the confirmation beep (microphone closed) turn scores into decisions.
- Raising the threshold trades false accepts for false rejects, and some requirements cannot be met by any threshold.
- Template matching is a modest detector: it is pace and speaker sensitive, and every accuracy number must be measured.
- Always-on listening needs approval (Chapter 17); push-to-talk (Chapter 11) is the default.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "The window is 60 percent full and the room is noisy. Why must the detector not score it, and what does the code return? Click to expand"
    A 60 percent full window has 15 real frames and 10 frames of zeros (or old data), so its band means and length do not describe a second of sound, and normalizing it can make a meaningless pattern look like a strong match. `Window.score()` returns `None` until the fill percentage is 100, and the detector also requires at least 8 frames with the level gate open before it scores.

??? question "You moved the kit to a room with a different hum and a cheaper microphone. Why can the score still work, and what might not? Click to expand"
    The hum and the microphone's frequency response add steady amounts to the band energies, and mean subtraction removes anything steady in a band, so the score is largely unchanged. What it cannot remove is noise that changes during the second, a much lower speech-to-noise ratio (the level gate may stay shut), or a different speaker. Recalibrate (Chapter 11) and measure again with `08-threshold-sweep.py`.

!!! mascot-celebration "A Detector You Can Explain"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just built and tested a wake-word detector from log band features, a rolling window, mean subtraction, unit normalization, and a dot-product score, and you know exactly where it is weak. Few people can say why their assistant wakes up; you can.

In [Chapter 13](../13-wifi-http-agent-link/index.md) we connect the device to the agent that answers the questions you ask it.
