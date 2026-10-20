---
title: "Microphone Calibration and Push-to-Talk"
description: "How to measure a room's noise floor and a voice's speech level, turn them into level gates and a saved calibration, check for clipping, and record an utterance on a button press with voice activity detection finding where it starts and ends."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 12:59:05"
version: 1.11
---

# Microphone Calibration and Push-to-Talk

## Summary

This chapter prepares the microphone for reliable use. Students measure the noise floor and speech level, compute signal-to-noise ratio, and set level gates. They then record an utterance on a button press and use voice activity detection to find utterance boundaries, completing the default push-to-talk mode.

## Concepts Covered

This chapter covers the following 14 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Push-to-Talk | 69 |
| Recording an Utterance | 34 |
| Noise Floor | 73 |
| Speech Level | 72 |
| Signal-to-Noise Ratio | 6 |
| Speech Floor Gate | 65 |
| Level Gate | 64 |
| Microphone Calibration | 3 |
| Mic Distance Effect | 2 |
| Clipping Detection | 1 |
| Utterance Boundaries | 29 |
| Calibration Config Value | 1 |
| Room Acoustics | 1 |
| Voice Activity Detection | 28 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 3: Sound and Digital Audio Basics](../03-sound-and-digital-audio/index.md)
- [Chapter 4: The Pico Kit Hardware and Wiring](../04-pico-kit-hardware/index.md)
- [Chapter 8: I2S Audio: Recording and Playing Sound](../08-i2s-audio/index.md)
- [Chapter 9: Signal Processing and the FFT](../09-signal-processing-fft/index.md)

---

## A Microphone That Knows Its Room

In Chapter 8 you read 40 ms frames from the microphone and turned each one into a loudness in "bits". A loudness number is only useful when you know what it is being compared with. Is 15 bits loud? In one room it is a shout, and in another it is the hum of a fan. This chapter teaches the device to measure its own room and voice, then use those two measurements to decide when someone is talking and to record what they say.

!!! mascot-welcome "Teach the Ears Their Room"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter you will hold a button, ask a question, and watch your Study Buddy trim the recording to just your words. Let's listen closely! Every room sounds a little different, so the first job is to measure this one.

Chapter 9 explains RMS loudness and decibels in depth. This chapter keeps the simpler "bits" meter from Chapters 3 and 8 and the 40 ms frame (512 samples at 12,800 samples per second), so everything here runs in the same loop you already have.

## Push-to-Talk: The Default Way to Listen

**Push-to-talk** means the microphone is open only while a person holds a button. The student presses MODE, talks, and lets go. Nothing is listening before the press or after the release. This is the default listening mode of Open Study Buddy, and it is the mode the rest of the book assumes unless a chapter says otherwise. [Chapter 12](../12-wake-word-detection/index.md) builds an always-on alternative, and [Chapter 17](../17-privacy-responsible-listening/index.md) explains why that alternative needs approval first.

Push-to-talk is the right default for three reasons. It is private, because the student decides when the microphone is open. It is simple, because a button press is an unmistakable signal and the device never has to guess whether a sound was meant for it. And it solves the self-hearing problem from Chapter 8 by design, because the microphone is closed before the speaker plays the answer.

In Chapter 7 the state machine moves from CLOCK to LISTENING when MODE is pressed. If MODE is released after at least 0.2 seconds (`MIN_MS` = 200), it moves to THINKING, and a shorter tap goes back to CLOCK. This chapter fills in what happens inside LISTENING.

| Question | Push-to-talk (this chapter) | Always-on (Chapter 12) |
|----------|-----------------------------|------------------------|
| When is the microphone open? | Only while MODE is held | All the time while the mode is on |
| What starts a recording? | A button press | The device hears "Hey Pico" |
| Can the device start a recording by mistake? | Only by a bump of the button, and the 0.2 s rule rejects most bumps | Yes, a sound that scores above the threshold (a false accept) |
| What does the school have to approve? | Nothing beyond the normal kit rules | A written approval first (Chapter 17) |

*Worked example.* This timeline uses illustrative times, not a measurement. The student presses MODE at \( t = 0 \). The recorder opens the microphone and throws away 3 frames while the microphone settles, which is \( 3 \times 40 = 120 \) ms. Frames are stored from \( t = 120 \) ms. The student speaks from 0.5 s to 2.1 s and lets go at 2.4 s, and the recorder notices on the next frame. The recording holds about \( 2.4 - 0.12 = 2.28 \) s, which is 57 frames of 1,024 bytes, or 58,368 bytes. The microphone closes the moment recording stops, the state becomes THINKING, and only then may the speaker play. While the microphone is open, the onboard LED is on, so a listening device never listens silently.

## Measuring the Room: The Noise Floor

Silence is not zero. Even in an empty, quiet room the microphone reports a small, constantly changing number, because the microphone's own electronics make a little noise and the room has air movement, distant traffic, and the hum of the building. The **noise floor** is how loud that background is, in bits, when nobody is talking. Everything the device does with speech is measured against it.

The kit has already measured two quiet rooms. The kit's test 06 found about 12.5 bits, and the Chapter 8 self-hearing test read 13.1 bits before the tone. Those are measurements on the test board, in two different sessions, so treat them as the neighborhood to expect and not as a promise for your room. At 13.1 bits, the loudness is \( 2^{13.1} \approx 8{,}780 \) out of a full scale of \( 2^{23} = 8{,}388{,}608 \), which is \( 6.02 \times (23 - 13.1) = 59.6 \) dB below the loudest sound the microphone can report.

To measure the floor, the device listens to a quiet room for a while and keeps every frame's loudness. A frame is 40 ms, so 100 frames is 4 seconds. The readings are not all equal, because the noise wanders from frame to frame, and Chapter 8 observed that room noise can push a single frame about 1 bit high. So the question is which single number to keep. Here are the choices, applied to ten quiet frames (illustrative numbers, with one frame bumped by a passing noise).

| Choice | Value for the ten frames | Problem |
|--------|--------------------------|---------|
| Lowest frame | 12.80 | Unusually quiet; most frames are louder, so a gate set from it would open on ordinary noise |
| Mean | 13.16 | One bump pulled it up, and the answer changes if the bump happens to fall in the window |
| **Median** | **13.00** | Half the frames are above and half below; one bump cannot move it |
| 95th percentile | 13.97 | Almost every quiet frame is below it, which makes it a good "ceiling" |
| Highest frame | 14.60 | Set entirely by the single bump |

The ten frames were 12.9, 13.0, 13.1, 12.8, 13.0, 14.6, 13.1, 12.9, 13.0, and 13.2 bits. The book uses two numbers from the same recording. The **noise floor** is the **median** (the middle value when the readings are sorted), because it describes a typical quiet frame and shrugs off bumps. The **noise ceiling** is the **95th percentile**, the level that 95 of every 100 quiet frames stay below, because later steps need to know how high ordinary noise reaches. The `percentile()` function in `levels.py` finds both by sorting the readings and interpolating between neighbors.

```python
def percentile(values, p):
    ordered = sorted(values)
    k = (len(ordered) - 1) * p / 100      # a position between two readings
    low = int(k)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (k - low)
```

The function sorts the readings, converts the percentile `p` (0 to 100) into a position `k` in the sorted list, and blends the two readings on either side of that position. Test `02-noise-floor.py` collects 100 frames after discarding the first 8 (the microphone's start-up, as in kit test 06) and prints the lowest, median, mean, 90th, 95th, and highest readings, one line per second, plus the DC offset. It stays quiet for you. Run it in your room, write down the floor and ceiling, and then run it again while someone claps once. The highest reading jumps by several bits while the median barely moves, and that is the reason for the choice.

!!! mascot-thinking "Pick the Number That Ignores Bumps"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A percentile is a way to ask "what do most frames do?" instead of "what did the strangest frame do?" Median for the typical level, 95th percentile for how high ordinary noise reaches, and a single door slam cannot fool either one.

## Measuring the Voice: The Speech Level

The **speech level** is how loud the student's voice is, in bits, at the distance they normally speak from. It depends on who is talking, how loudly, and how far from the microphone, so you must state the distance with the number. A level with no distance is like a speed with no unit.

To measure it, ask the speaker to say the wake-style phrase, for example "Hey Pico, what is due tomorrow?", over and over for 4 seconds (100 frames). Speech is not steady: there are pauses between words and soft consonants, so many frames are quieter than the vowels. The book takes the **90th percentile** of the speech frames as the speech level. That is the level the louder syllables reach, and it ignores the pauses (which pull a mean down) and ignores the single loudest frame (which could be a cough or a bump).

Here are ten speech frames, again with illustrative numbers: 13.1, 15.8, 17.2, 17.9, 16.5, 17.4, 14.2, 17.0, 17.6, and 13.2 bits.

| Statistic | Value | What it says |
|-----------|-------|--------------|
| Mean | 15.99 | Dragged down by the two pauses at about 13.1 |
| Median | 16.75 | A typical frame, but half the phrase is pauses and consonants |
| **90th percentile** | **17.63** | The level of the louder syllables: the **speech level** |
| Highest | 17.90 | One frame; could be a pop |

A useful comparison comes from Chapter 8: a 1 kHz tone from the speaker, sitting beside the microphone at the kit's default volume, read 17.0 bits against a 13.1-bit floor. That is a measurement of a loud nearby tone, not of a voice, but it shows that a source close to the microphone can sit about 4 bits above a quiet room. Whether a student's voice at 30 cm lands higher or lower is something only the next script can tell you.

`03-speech-level.py` measures 3 seconds of quiet for the floor and then 4 seconds of speech, with the distance written in a constant at the top of the file. It prints the speech level and the signal-to-noise ratio, and it reports the biggest sample so you can see whether anything clipped. Measure the distance with a ruler, type it in, and write down the distance next to every result.

!!! mascot-tip "Always Write the Distance Down"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Tape a ruler mark to your desk at the distance you will normally speak from, such as 30 cm. Then your calibration and your later use are the same, and your results are comparable from one day to the next.

## Signal-to-Noise Ratio

The **signal-to-noise ratio** (SNR) compares the speech to the noise: how far the voice stands above the room. Because the "bits" scale is logarithmic, the comparison is a subtraction.

\[ \text{SNR}_{\text{bits}} = L_{\text{speech}} - L_{\text{floor}} \]

One bit is a doubling of the amplitude. A doubling changes the level by \( 20 \log_{10}(2) = 6.0206 \) dB, so \( b \) bits is \( 6.02\,b \) dB. The first script, `01-bits-and-db.py`, verifies this with synthetic frames: a frame built to be twice as big reads exactly 1.000 bit higher.

| Bits above the floor | Times bigger (amplitude) | Decibels |
|----------------------|--------------------------|----------|
| 1 | 2 | 6.02 |
| 2 | 4 | 12.04 |
| 4 | 16 | 24.08 |
| 8 | 256 | 48.16 |

One caution. The bits scale measures the average distance from the middle, not the RMS (root-mean-square) value used in textbook decibels. For the same RMS, a sine wave reads about 0.99 dB higher than random noise on the bits scale (the script prints this: the mean-distance-to-RMS ratio is 0.90 for a sine and about 0.80 for noise). So read SNR in bits as a good guide that can be off by about 1 dB, which is fine for setting gates and not good enough for lab-grade measurements.

*Worked example.* With a floor of 13.0 bits and a speech level of 17.0 bits, the SNR is \( 17.0 - 13.0 = 4.0 \) bits, which is \( 4.0 \times 6.02 = 24.1 \) dB, a voice 16 times larger than the noise. The kit's test 06 already used a rule of this kind: it called a frame "speech" when it was more than 2.0 bits (12 dB) above the floor. This chapter keeps 2.0 bits as the minimum acceptable SNR, `MIN_SNR_BITS`, and calibration complains if the voice does not clear it.

## Two Gates: Speech Floor and Level

With the floor and the speech level in hand, the device can draw a line between them. The line has two parts that are easy to mix up, so the book names them separately.

The **speech floor gate** is a loudness, in bits, below which a frame is treated as "not speech". It is a single number placed between the noise and the voice. The calibration puts it 40 percent of the way up from the floor \( F \) to the speech level \( S \), and never closer than 1 bit above the noise ceiling \( C \):

\[ T_{\text{open}} = \max\bigl(F + 0.4\,(S - F),\; C + 1.0\bigr) \]

Forty percent is a starting choice, low enough to catch soft word beginnings and high enough that ordinary noise stays below it; it is a tunable constant (`GATE_FRACTION`), and the measurement exercises ask you to test it. The `max` with \( C + 1.0 \) protects a quiet voice: if the voice is only a little above the noise, the gate is still held clear of the noise.

The **level gate** is the switch that applies that number to each frame as it arrives. It is open while the sound is loud enough to be speech. If it used a single threshold, a level that hovers near the line would make the gate flutter open and closed, frame after frame, so the level gate uses **hysteresis**: it opens when a frame reaches the open level \( T_{\text{open}} \), and it closes only when a frame falls below a lower close level \( T_{\text{close}} \). The gap between them is the hysteresis, 0.5 bit by default (about 3 dB), but never more than half the distance from the ceiling to the open level.

*Worked example.* Take a floor of 13.0 bits, a ceiling of 13.5, and a speech level of 17.0 (illustrative). Then \( F + 0.4(S - F) = 13.0 + 0.4 \times 4.0 = 14.6 \) and \( C + 1.0 = 14.5 \), so the larger is \( T_{\text{open}} = 14.6 \). The hysteresis is the smaller of 0.5 and \( (14.6 - 13.5)/2 = 0.55 \), so 0.5, which makes \( T_{\text{close}} = 14.1 \). The same arithmetic is in `make_calibration()`, and the gate itself is only a few lines.

```python
class LevelGate:
    def __init__(self, open_at, close_at):
        self.open_at = open_at       # open when a frame reaches this many bits
        self.close_at = close_at     # close when a frame falls below this
        self.is_open = False

    def update(self, bits):
        if self.is_open:
            if bits < self.close_at:
                self.is_open = False
        elif bits >= self.open_at:
            self.is_open = True
        return self.is_open
```

`update()` takes one frame's loudness and returns whether the gate is open. Notice the two comparisons: `>=` to open, `<` to close, so a frame exactly at the open level opens the gate and a frame exactly at the close level keeps it open.

Here is a 20-frame trace that wobbles around an open level of 15.0 bits, from the self-test `09-calibration-selftest.py` (synthetic values). A `#` means the gate is open.

| Frame | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |
|-------|---|---|---|---|---|---|---|---|---|---|----|----|----|----|----|----|----|----|----|----|
| Bits | 14.8 | 15.1 | 14.9 | 15.2 | 14.7 | 15.0 | 14.9 | 15.3 | 14.6 | 15.1 | 15.4 | 15.6 | 15.2 | 14.9 | 15.1 | 14.8 | 14.2 | 13.4 | 13.2 | 13.5 |
| Single threshold at 15.0 | . | # | . | # | . | # | . | # | . | # | # | # | # | . | # | . | . | . | . | . |
| Gate (open 15.0, close 14.5) | . | # | # | # | # | # | # | # | # | # | # | # | # | # | # | # | . | . | . | . |

The single threshold flips 12 times. The gate flips twice, once to open at frame 1 and once to close at frame 16, when the level finally drops below 14.5. That is the whole point of hysteresis. `05-gate-meter.py` shows the same thing live: it draws the level bar with marks for the floor, the open level, and the close level, prints "OPEN" or "closed" under it, and after 30 seconds prints how many times the gate flipped against how many times a single threshold would have. Write both counts down. Hysteresis does not remove isolated spikes that rise above the open level and fall right back to the floor, and a trace in the explorer below shows exactly that, which is the job of the frame counts in voice activity detection later in this chapter.

#### Diagram: Level Gate Hysteresis Explorer

<details markdown="1">
<summary>Level Gate Hysteresis Explorer</summary>
Type: microsim
**sim-id:** level-gate-hysteresis-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate how many times a single-threshold gate and a hysteresis gate change state on 3 loudness traces, matching the correct counts in 5 of 6 answers.

**Prerequisites:** loudness in bits, frame, speech floor gate, level gate, hysteresis (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 3 challenge traces, the learner types two whole numbers before the sim reveals them: the number of state changes of the single-threshold gate, and the number of state changes of the hysteresis gate. A state change is any frame whose open/closed state differs from the frame before it (the state before frame 0 counts as closed). An answer is correct when it equals the value in the Content table. Mastery is 5 of 6 answers correct on the first attempt. Moving the threshold controls in exploration is exploration, not evidence.

**Misconceptions:** (1) Hysteresis makes a gate less sensitive to speech. (2) Hysteresis removes every false opening. (3) The gate closes at the same level that it opens at.

**Instructional Rationale:** Apply-level calculation needs a procedure the learner can run and check, so the learner traces the two gates frame by frame in their head, commits two counts, and only then sees the sim's trace. Challenge 3 is built so that hysteresis does not help, which exposes misconception 2.

**Content:**

The sim shows one loudness trace of 20 frames at a time, as a line of bits against frame number, with the open level and the close level drawn as two horizontal lines. Loudness values are in bits. All 3 traces are synthetic and the sim labels them "synthetic".

| Frame | Trace A | Trace B | Trace C |
|-------|---------|---------|---------|
| 0 | 14.8 | 13.0 | 13.0 |
| 1 | 15.1 | 13.1 | 13.4 |
| 2 | 14.9 | 15.6 | 14.2 |
| 3 | 15.2 | 16.8 | 13.6 |
| 4 | 14.7 | 17.2 | 14.9 |
| 5 | 15.0 | 14.8 | 13.2 |
| 6 | 14.9 | 16.9 | 15.1 |
| 7 | 15.3 | 17.4 | 13.3 |
| 8 | 14.6 | 15.2 | 14.7 |
| 9 | 15.1 | 14.6 | 13.1 |
| 10 | 15.4 | 16.5 | 14.4 |
| 11 | 15.6 | 17.0 | 13.2 |
| 12 | 15.2 | 16.2 | 14.8 |
| 13 | 14.9 | 14.4 | 13.0 |
| 14 | 15.1 | 13.2 | 13.3 |
| 15 | 14.8 | 13.0 | 13.1 |
| 16 | 14.2 | 13.1 | 13.0 |
| 17 | 13.4 | 12.9 | 13.2 |
| 18 | 13.2 | 13.0 | 13.1 |
| 19 | 13.5 | 13.1 | 13.0 |

| # | Trace | Open level | Close level | Single-threshold changes | Hysteresis changes | Why (shown as feedback) |
|---|-------|------------|-------------|--------------------------|--------------------|-------------------------|
| 1 | A | 15.0 | 14.5 | 12 | 2 | The level crosses 15.0 twelve times, but it never falls below 14.5 until frame 16, so the gate opens at frame 1 and closes at frame 16. |
| 2 | B | 15.0 | 14.5 | 6 | 2 | Dips to 14.8 and 14.6 inside the phrase flip the single threshold, but they stay above 14.5. The gate opens at frame 2 and closes at frame 13, when 14.4 is below 14.5. |
| 3 | C | 14.5 | 14.0 | 8 | 8 | Each spike (14.9, 15.1, 14.7, 14.8) rises over 14.5 and then falls to 13.6 or lower, below the close level, so both gates open and close four times. Hysteresis helps only with wobble near the line. |

**Provenance:** Trace A is the wobble trace in `09-calibration-selftest.py` and the chapter table above. Traces B and C are synthetic, written for this sim. The change counts were computed with `levels.LevelGate` in `src/chapters/11-mic-calibration-push-to-talk/levels.py`.

**Rules:** The single-threshold gate is open when bits >= open level. The hysteresis gate starts closed, opens when bits >= open level, and closes when bits < close level. Exploration range for the open level: 13.0 to 18.0 bits, step 0.1, default 15.0. For the close level: 12.0 to 18.0 bits, step 0.1, default 14.5, and never above the open level. A change in the open level moves the close level down if needed to keep close <= open. The 3 challenge settings in the table override the controls.

**Learner Activity:**

1. The learner chooses a trace and moves the open and close levels. The sim shades the frames where each gate is open and shows both change counts. The learner should notice that raising the close level toward the open level makes the hysteresis gate behave like the single threshold.
2. The learner starts the 3 challenges. For challenge 1 the sim shows trace A and the two levels but hides both gates.
3. The learner types the two counts and submits.
4. The sim shades both gates, shows the counts, and shows the Why text.
5. After challenge 3, the sim shows the score and the learner should notice that a spike that falls all the way back to the floor flips both gates.

**Feedback:** 3 challenges, fixed order, one attempt each, 2 answers per challenge, 6 answers in all. Correct: "Correct: <Why>". Incorrect: "Not quite. The counts are <single> and <hysteresis>: <Why>". The counts are revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** Trace A is shown with the open level at 15.0 and the close level at 14.5, both gates shaded, and the question "Which gate flutters?"

**Chapter Anchors:** The chapter states that the single threshold flips 12 times and the gate flips twice on trace A (open at frame 1, close at frame 16), that the gate opens with `>=` and closes with `<`, and that hysteresis does not remove spikes that fall back to the floor.
</details>

## Microphone Calibration

**Microphone calibration** is the guided procedure that measures the floor and the speech level once, in the room and at the distance where the device will be used, and turns them into the numbers the rest of the program needs. The kit does this in `04-calibrate.py`. MODE starts it, the screen asks the student to be quiet for 4 seconds, then to say the phrase for 4 seconds, and then shows the result.

The procedure has a decision at the end that matters: the program checks the result before offering to save it. `make_calibration()` returns the values and a list of problems.

| Problem flag | Meaning | Advice shown |
|--------------|---------|--------------|
| `clipping` | A speech frame had samples at the rail (see the next section) | Move back or speak softer |
| `room_not_quiet` | Noise ceiling is more than 1.5 bits above the floor | Something made noise in the quiet step; try again |
| `snr_low` | Speech is less than 2.0 bits above the floor | Move closer or quiet the room |
| `too_few_frames` | Fewer than 20 frames in a step | Run the procedure again |

If any flag is raised the device does not offer to save. When the list is empty, UP saves and DOWN measures again. A calibration run on synthetic frames (`09-calibration-selftest.py`, a 13.0-bit quiet room and 17.0-bit speech, with a little random wobble) produced the following, and on your device the numbers will be your own.

| Value | Synthetic result |
|-------|------------------|
| Noise floor (median) | 12.97 bits |
| Noise ceiling (95th percentile) | 13.20 bits |
| Speech level (90th percentile) | 17.43 bits |
| SNR | 4.46 bits, 26.9 dB |
| Speech floor gate (opens) | 14.75 bits |
| Level gate close | 14.25 bits |

### Calibration Config Values

The numbers the calibration produces are **calibration config values**: settings that belong to this particular device, room, and voice, and that other programs read instead of re-measuring. Chapter 2 introduced the config file pattern, where every hardware fact lives in one module. Calibration values follow the same idea with one difference, which is why they do not go into `config.py`: they are measured, they change when the room does, and `upload-chapter.sh` copies the kit's `config.py` onto the Pico every time you upload, which would overwrite them. So the values live in their own small file, `calibration.json`, which no upload script touches.

| Key | Meaning |
|-----|---------|
| `noise_floor` | Median of the quiet readings, in bits |
| `noise_ceiling` | 95th percentile of the quiet readings, in bits |
| `speech_level` | 90th percentile of the speech readings, in bits |
| `speech_floor` | The level gate's open level, in bits |
| `gate_close` | The level gate's close level, in bits |
| `record_shift` | Right-shift applied to 24-bit samples when they are stored as 16-bit (0 to 8) |
| `distance_cm` | The distance the calibration was made at |

The file is a few lines of JSON. These values are the worked example's illustrative numbers, written as the file would hold them; the device writes your measured ones.

```json
{"version": 1, "noise_floor": 13.0, "noise_ceiling": 13.5, "speech_level": 17.0,
 "speech_floor": 14.6, "gate_close": 14.1, "record_shift": 5, "distance_cm": 30}
```

The `record_shift` value is the one that is not about loudness for the eye. It controls how a 24-bit sample is squeezed into 16 bits for storage. A shift of 8 keeps the whole 24-bit range, and a smaller shift makes the stored sound louder. `record_shift_for()` picks the smallest shift that keeps the biggest speech sample at or below half the 16-bit range (16,384), leaving headroom: a speech peak of 300,000 gives a shift of 5, because \( 300{,}000 \gg 5 = 9{,}375 \).

If the file is missing or damaged, `calibration.load()` returns a set of defaults built from the kit's own findings (floor 13.0, a speech floor 2.0 bits above it as in test 06, and a shift of 5, which gives the same +18 dB of gain as kit test 07), and the programs say they are using guesses.

!!! mascot-warning "Save Once, Never in a Loop"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Flash memory wears out if it is rewritten thousands of times, and a write cut off by a power loss can damage the file. `calibration.save()` is called only when the student presses UP, and it writes a temporary file first and swaps it in afterwards, so the old file stays whole until the new one is complete.

## Clipping Detection

**Clipping detection** notices when the microphone's samples reach the largest value the 24-bit range can hold, so the tops of the waves are flattened (Chapter 3 introduced audio clipping). A clipped recording is distorted, and no later processing can undo it. The largest 24-bit magnitude is \( 2^{23} = 8{,}388{,}608 \). The code calls a sample clipped when it is at least 95 percent of that, 7,969,177 (`CLIP_LEVEL`), and a frame clipped when it has at least 2 such samples (`CLIP_MIN_SAMPLES`), because one stray sample is not a flattened wave.

*Worked example.* At the quiet floor of 13.1 bits there are \( 23 - 13.1 = 9.9 \) bits of headroom, which is 59.6 dB, so ordinary speech has a lot of room before it reaches the rail. A very loud sound close to the microphone is what clips. `frame_stats()` checks the frame's highest and lowest samples first, which costs almost nothing, and counts clipped samples only if one of them is over the limit. The synthetic shouted frame in the self-test (a 200 Hz sine whose peaks reach 12,000,000, past the rail) reports 272 clipped samples. The calibration refuses to save when any speech frame is clipped, because the fix is physical: move back from the microphone or speak more softly, and run it again.

Clipping can also happen later, when the 24-bit sample is squeezed into 16 bits. The recorder reports `limited` when a stored sample hit the 16-bit limit, which means the `record_shift` is too small for the loudness, and calibration is what chooses it.

## The Microphone Distance Effect

The **microphone distance effect** is that the farther the speaker is from the microphone, the quieter the voice is relative to the room. A simple model, the inverse-distance rule, says amplitude falls in proportion to \( 1/d \). Each doubling of the distance halves the amplitude, which is 1 bit or 6.02 dB:

\[ L(d) = L(d_0) - \log_2\!\left(\frac{d}{d_0}\right) \]

This is a model, not a law of the room. It describes a small source in open space, and a real room adds echoes and background noise, so the measured drop can be different. The noise floor, however, does not depend on the talker's distance, so every bit lost by the voice is a bit lost from the SNR.

*Worked example (illustrative numbers).* Suppose a voice reads 18.0 bits at 10 cm against a 13.0-bit floor, an SNR of 5.0 bits. At 20 cm the model gives 17.0 bits (SNR 4.0), at 40 cm 16.0 bits (3.0), and at 80 cm 15.0 bits (2.0), which has reached the 2.0-bit minimum. So in this made-up room the voice stops being usable at about 80 cm. Going from 10 cm to 30 cm costs \( \log_2(3) = 1.58 \) bits, or 9.5 dB. `06-distance-test.py` measures your own voice at three distances (10, 20, and 40 cm by default), prints the model's prediction from the first row beside each measurement, and shows how far the room departs from the model. This is the habit to build: use a model to predict, then measure to see how wrong it is.

## Room Acoustics

**Room acoustics** is how the room itself shapes the sound the microphone hears. Hard, bare surfaces (windows, tile, a whiteboard, a desk) reflect sound, and the reflections arrive a moment after the direct voice, which adds echo and blurs the speech. Soft surfaces (carpet, curtains, bookshelves) absorb it. Steady noises such as a ventilation fan, a projector, or a refrigerator raise the noise floor, which lowers the SNR for exactly the same voice. A busy classroom can raise it much more.

The calibration captures the room as it is, which is both its strength and its limit. It measures the floor with the fan running and the voice at the distance you used, but it cannot know that the fan will stop, that the class will arrive, or that the device will be moved to a different desk. So recalibrate when the room, the position of the device, or the time of day changes much. The honest way to learn what your room does is to run `02-noise-floor.py` in two places (a hard room and a softer one, with and without the fan) and compare. Those are measurements for you to make, not numbers this chapter claims.

## Recording an Utterance

An **utterance** is one thing the student says, from the first word to the last. **Recording an utterance** means storing its samples in memory so they can be played back or sent to the agent. Push-to-talk makes the recording simple: store frames while the button is held.

The recording goes into a buffer that is allocated once, as the first thing the program does, because Chapter 2 showed that a big block is hard to find after the heap has been cut into pieces. The size comes from arithmetic. The microphone delivers 32-bit words, 51,200 bytes per second, but speech does not need 24 bits for transcription, so the recorder stores 16-bit samples, 25,600 bytes per second, half as much.

| Format | Bytes per second | 6 seconds |
|--------|------------------|-----------|
| 32-bit words as read (kit test 07 stores these) | 51,200 | 307,200 |
| **16-bit samples (this chapter)** | **25,600** | **153,600** |

\[ 12{,}800 \;\tfrac{\text{samples}}{\text{s}} \times 2 \;\tfrac{\text{bytes}}{\text{sample}} \times 6 \text{ s} = 153{,}600 \text{ bytes} = 150 \text{ frames of } 1{,}024 \text{ bytes} \]

That is the same number of bytes as kit test 07's 3-second buffer of 32-bit words, which was allocated successfully on the test board, so this buffer is known to fit in a program of that size. Your own free heap is something to look at, not assume: `07-ptt-record.py` prints `gc.mem_free()` right after the buffer is made. Six seconds is generous for a question like "What is due tomorrow?"; the buffer can be larger if the free heap allows, because the arithmetic is the same.

Before the loop, a plain-language tour of what the recorder does with each frame. `readinto` waits for the next 40 ms of sound. `frame_stats` unpacks the 512 words once, finds the loudness, DC offset, peak, and clipped count, and (when given a buffer and offset) also writes the frame as 16-bit samples with the DC offset removed and the `record_shift` applied. The loop stops on release, a full buffer, or a VAD signal.

```python
mic = config.init_microphone()
try:
    for _ in range(SKIP_FRAMES):              # the microphone's first moments
        mic.readinto(frame)
    while n < MAX_FRAMES:
        mic.readinto(frame)                   # waits for the next 40 ms of sound
        bits, dc, dev_peak, clipped = levels.frame_stats(
            frame, rec, n * FRAME16_BYTES, shift)
        n += 1
        if button.update() == "release":
            break
finally:
    mic.deinit()                              # always: the speaker may play next
```

`rec` is the pre-allocated buffer, `n * FRAME16_BYTES` is where this frame's 1,024 bytes go, and the `finally` closes the microphone even if something raises, as Chapter 2 taught. The full version in `recorder.py` also counts clipped frames, times the work, and runs the VAD.

Everything inside the loop has to fit in the frame budget from Chapter 8: 40 ms. Chapter 8 measured the plain-Python loudness calculation at about 10 ms per frame on the test board. The conversion adds work in the same loop, and drawing adds more, so `recorder.record()` times each frame and counts overruns (frames that took more than 40 ms). The added cost has not been measured on the kit, so treat the following as a prediction: it should be some milliseconds on top of the 10 ms. `07-ptt-record.py` prints the average and maximum work time, and the number that matters is the maximum.

The display is where a frame budget is easiest to lose. A full 360 by 360 redraw is \( 360 \times 360 \times 2 = 259{,}200 \) bytes, which is 86.4 ms at 24 MHz even in the best case (Chapter 5), more than two frames, so a recorder that redraws the screen each frame loses audio. The level bar uses region updates (Chapter 6): `ui.LevelBar` remembers how many columns are filled and draws only the columns that changed.

| Update | Bytes | Wire time at 24 MHz |
|--------|-------|---------------------|
| Whole 360 x 360 screen | 259,200 | 86.4 ms |
| Whole 200 x 22 bar | 8,800 | 2.93 ms |
| Bar growing by 10 columns | 440 | 0.15 ms |

The bar redraws fully only when its color changes, for example when the gate opens. The "REC" word and the time display are text regions padded to a fixed width, so each new value covers the old one.

!!! mascot-warning "Close the Microphone Before You Speak"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Playing the recording while the microphone is open is the self-hearing problem from Chapter 8. `record()` closes the microphone in its `finally` block, and only afterwards does `07-ptt-record.py` open the speaker. If you add playback of your own, keep that order.

## Utterance Boundaries and Voice Activity Detection

The student holds the button for a little longer than they speak. They press, take a breath, speak, and release a moment late. **Utterance boundaries** are the frames where the speech starts and ends inside the recording. Finding them lets the device keep only the speech, which means shorter uploads and a transcription service that does not have to skip over silence.

**Voice activity detection** (VAD) is the rule that finds those boundaries, frame by frame. This book's VAD is the simplest one that works, built from the level gate you already have: the gate decides whether a frame is loud, and two counters turn a stream of loud and quiet frames into a start and an end.

- **Start:** speech starts after `START_FRAMES` = 3 loud frames in a row (120 ms). A single loud frame, such as a click, is not speech.
- **End:** speech ends after `END_FRAMES` = 15 quiet frames in a row (600 ms). A pause between words is shorter than that, so it does not end the phrase.
- **Pre-roll:** keep `PRE_ROLL_FRAMES` = 4 frames (160 ms) before the first loud frame, because a soft first sound can sit below the gate.
- **Hang-over:** keep `HANG_OVER_FRAMES` = 5 frames (200 ms) after the last loud frame, for a soft last sound.

These four numbers are design choices with reasons, not measured optima. Three frames are enough to reject a click and short enough to lose little speech; 600 ms is longer than a typical pause between words; the pre-roll covers a soft first sound that sat below the gate, and the hang-over does the same for a soft last sound. The measurement exercise below asks you to test them with your own voice.

The VAD is a small state machine with four states. The states and transitions are the following.

| State | Meaning | A loud frame | A quiet frame |
|-------|---------|--------------|---------------|
| SILENCE | The gate is closed; nothing is happening | Go to STARTING (loud count 1) | Stay |
| STARTING | Counting loud frames in a row | Count one more; at 3 go to SPEECH and signal **start** | Go back to SILENCE (count reset) |
| SPEECH | An utterance is under way | Stay | Go to ENDING (quiet count 1) |
| ENDING | Counting quiet frames in a row | Go back to SPEECH (count reset) | Count one more; at 15 go to SILENCE and signal **end** |

The "loud" and "quiet" decisions come from the level gate, so its hysteresis already stops the gate from fluttering near the threshold. Two things are worth noticing. The start is signaled 2 frames after the first loud frame, because the third loud frame has to arrive; the code remembers the index of the first loud frame (`start_index`) and reports that. And the end is signaled 15 frames after the last loud frame, because the 15th quiet frame in a row has to arrive; the code reports the index of the last loud frame (`end_index`), not the frame at which it was sure.

*Worked example (synthetic frames from `09-calibration-selftest.py`).* The recording is 20 quiet frames, then 30 speech frames, then 50 quiet frames. The VAD signals "start" at frame 22 and reports `start_index` 20. It signals "end" at frame 64 (15 quiet frames after frame 49) and reports `end_index` 49. The boundaries add 4 frames of pre-roll and 5 of hang-over, so the device keeps frames 16 through 54, which is 39 frames or 1,560 ms of the 100-frame (4,000 ms) recording. In the same test, a one-frame click never starts speech, and two words separated by a 6-frame (240 ms) pause give one utterance, not two.

Because push-to-talk records from the button press, the pre-roll is free: the frames before the start are already in the buffer, and the device keeps them by choosing a different first frame. A hands-free recorder with no button would need a small ring buffer of the last few frames to do the same, which is one of the reasons always-on listening is a bigger project.

!!! mascot-encourage "A State Machine Is Just Counting"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Four states and two counters can look like a lot at first. You already built a state machine for the device's modes in Chapter 7, and this one only counts frames, so step through the table above with a pencil and it will settle.

Use the boundary finder to check your reading of the rules.

#### Diagram: VAD Boundary Finder

<details markdown="1">
<summary>VAD Boundary Finder</summary>
Type: microsim
**sim-id:** vad-boundary-finder<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** execute<br/>
**Learning Objective:** The learner will execute the voice activity detection rules on 5 loudness traces to find each trace's first and last speech frame, matching both frames in at least 4 of 5 traces.

**Prerequisites:** loudness in bits, frame, level gate, hysteresis, voice activity detection, start frames, end frames, state machine (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 5 traces, the learner types the start frame (the index of the first loud frame of the run that started the speech) and the end frame (the index of the last loud frame of the speech), or "none" when the VAD finds no speech, before the sim reveals them. A trace is correct when both entries equal the Start and End columns in Content. Mastery is 4 of 5 traces correct on the first attempt. Stepping through the example trace in exploration is exploration, not evidence.

**Misconceptions:** (1) Speech starts at the frame where the VAD signals "start". (2) Any loud frame starts speech. (3) Any quiet frame ends speech. (4) A trace that is still loud at its last frame has no end.

**Instructional Rationale:** Apply-level execution needs the learner to run the rules on data and get a checkable answer, so the learner counts runs of loud and quiet frames before the sim steps the state machine. The five traces each break one misconception.

**Content:**

The sim uses these fixed rules: the gate opens at 15.0 bits (bits >= 15.0) and closes below 14.5 bits (bits < 14.5); START_FRAMES is 3; END_FRAMES is 15; pre-roll is 4 frames; hang-over is 5 frames. Each trace is written as runs of "count at level", in order. Frames are numbered from 0. All 5 traces are synthetic, and the sim labels them "synthetic".

| # | Trace (frames at bits) | Total frames | Start | End | Kept frames (first to last) | Why (shown as feedback) |
|---|------------------------|--------------|-------|-----|-----------------------------|-------------------------|
| 1 | 5 at 13.0, 8 at 17.0, 6 at 13.0, 8 at 17.0, 20 at 13.0 | 47 | 5 | 26 | 1 to 31 | The 6 quiet frames in the middle are fewer than 15, so the two words are one utterance. The last loud frame is 26 (5 + 8 + 6 + 8 - 1), and the first is 5. |
| 2 | 10 at 13.0, 1 at 18.0, 30 at 13.0 | 41 | none | none | none | One loud frame is fewer than 3 in a row, so the click never starts speech. |
| 3 | 6 at 13.0, 2 at 17.0, 1 at 13.0, 2 at 17.0, 1 at 13.0, 2 at 17.0, 30 at 13.0 | 44 | none | none | none | Each loud run is 2 frames and a quiet frame resets the count, so the count never reaches 3. |
| 4 | 8 at 13.0, 40 at 17.0 | 48 | 8 | 47 | 4 to 47 | The speech is still going when the trace ends, so the end is the last loud frame, 47. The kept range stops at the last frame of the recording. |
| 5 | 3 at 13.0, 10 at 17.0, 14 at 13.0, 10 at 17.0, 25 at 13.0 | 62 | 3 | 36 | 0 to 41 | A pause of 14 frames is one short of 15, so it does not end the speech. The pre-roll would start at frame -1, so it stops at frame 0. |

The kept frames are computed as: first kept frame = max(0, start - 4); last kept frame = min(total - 1, end + 5).

The state machine has 4 states, SILENCE, STARTING, SPEECH, and ENDING, with the transitions given in the chapter table; the sim draws it and highlights the current state in the stepping mode. For each frame stepped, the sim shows the frame's bits, whether the gate is open, the loud count, the quiet count, and the state.

**Provenance:** The rules are those in `src/chapters/11-mic-calibration-push-to-talk/vad.py` and `levels.py`. The Start, End, and Kept columns were computed by running `vad.VAD` and `vad.boundaries` on the traces. The traces are synthetic.

**Rules:** Loud means the hysteresis gate is open after processing the frame. Start = the index of the first frame of the run of loud frames that reaches 3 in a row. End = the index of the last frame at which the gate was open, taken when 15 quiet frames in a row have been counted, or at the end of the trace if the speech is still going. A quiet frame while counting loud frames resets the loud count to 0. A loud frame while counting quiet frames resets the quiet count to 0. Exploration controls: START_FRAMES 1 to 6, step 1, default 3, unit frames; END_FRAMES 5 to 30, step 1, default 15, unit frames. The challenge answers use the defaults.

**Learner Activity:**

1. The learner steps through trace 1 one frame at a time and watches the state, the counts, and the gate. The learner should notice that the start is signaled 2 frames after the speech began and the end 15 frames after it finished.
2. The learner starts the 5 traces. Trace 1 is shown as a plot of bits against frame number with the gate levels drawn, and the state machine is hidden.
3. The learner types the start and end frames, or "none", and submits.
4. The sim steps through the trace, shows the state machine, the kept range, and the Why text.
5. After trace 5, the sim shows the score. The learner should notice that traces 1 and 5 differ only in whether the pause is under or over 15 frames in the rule.

**Feedback:** 5 traces, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. Start <start>, end <end>: <Why>". The answers are revealed right after each submission, and a running score "n of 5" is shown.

**Starting State:** Trace 1 is shown stopped at frame 0 with the question "Where does the speech start and where does it end?"

**Chapter Anchors:** The chapter states that START_FRAMES is 3 (120 ms), END_FRAMES is 15 (600 ms), the pre-roll is 4 frames, and the hang-over is 5 frames; that the start is signaled 2 frames after the first loud frame; that the end is reported at the last loud frame; and that a click and a 240 ms pause do not break an utterance.
</details>

Simple energy-based voice activity detection has limits that are worth knowing. It cannot tell speech from any other sound of the same loudness, so a fan, music, or a classmate across the room can open the gate. A very quiet or whispered voice may never reach the speech floor. These are the reasons the book treats the VAD as a trimming tool for a recording the student chose to make, and why Chapter 12 does not rely on loudness alone to recognize the wake word.

`08-vad-record.py` runs the VAD on every frame while MODE is held, prints a picture of the recording with the start (S), end (E), and kept range marked, and plays back only the kept part. With `AUTO_STOP = True` it also stops recording by itself when the speech ends.

## What Has and Has Not Been Measured

The code in this chapter has been run off the device, on a computer, against a stand-in for the Pico's pins, timer, and microphone, and its logic is checked by `09-calibration-selftest.py`. It has not yet been run on the Pico. Everything in the chapter that is described as synthetic or illustrative comes from the self-test or from stated arithmetic. The numbers that only the kit can give you are these, and each has a script waiting for it.

| Question | Script | Status |
|----------|--------|--------|
| Your room's noise floor and ceiling | `02-noise-floor.py` | Expected near 12.5 to 13.1 bits (two earlier kit measurements); not yet measured for this chapter |
| Your voice's speech level and SNR at 30 cm | `03-speech-level.py` | Not yet measured |
| How well the 1 bit per doubling model fits | `06-distance-test.py` | Not yet measured |
| The calibration file from a real run | `04-calibrate.py` | Not yet run on the device |
| Hysteresis versus single-threshold flips on real speech | `05-gate-meter.py` | Not yet measured |
| Work time per frame while recording, and free heap | `07-ptt-record.py` | Not yet measured; Chapter 8's 10 ms is for loudness alone |
| Whether 3, 15, 4, and 5 frames suit real speech | `08-vad-record.py` | Chosen by reasoning; not yet tested |

## Putting It All Together

You can now describe push-to-talk from the first press to the final trimmed recording. The device measures its room (noise floor) and your voice (speech level) at a stated distance, takes their difference as the signal-to-noise ratio, and places a speech floor gate between them. A level gate with hysteresis applies it to every 40 ms frame. The result is saved once as calibration config values. When MODE is pressed, the recorder opens the microphone, stores 16-bit frames in a buffer allocated at startup, shows a level bar by redrawing only what changed, and closes the microphone when the button is released. Voice activity detection finds the speech inside the recording, and the pre-roll and hang-over decide how much to keep.

Key takeaways:

- Push-to-talk is the default: the microphone is open only while MODE is held, and it closes before the speaker plays.
- The noise floor is the median of quiet-room readings, and the noise ceiling is their 95th percentile; the speech level is the 90th percentile of speech readings, always stated with its distance.
- SNR is a subtraction in bits, and 1 bit is 6.02 dB (to within about 1 dB on this mean-distance scale).
- The speech floor gate is a level between the noise and the voice; the level gate applies it with hysteresis (open at the higher level, close below the lower) so it does not flutter.
- Clipping means samples at the rail; calibration refuses to save a clipped run, and the fix is distance or a softer voice.
- Calibration values live in `calibration.json`, written once on a button press and read by every program.
- A 6-second 16-bit recording buffer is 153,600 bytes, allocated first; the loop must finish each frame within 40 ms, so the display is updated by region.
- VAD starts after 3 loud frames, ends after 15 quiet frames, and keeps 4 frames before and 5 after.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "A calibration with a noise floor of 13.0 bits and a speech level of 14.5 bits is rejected. Why, and what should you try? Click to expand"
    The SNR is \( 14.5 - 13.0 = 1.5 \) bits, which is below the minimum of 2.0 bits (`snr_low`). The voice does not stand far enough above the noise for a gate to separate them. Move closer to the microphone (each halving of the distance gains about 1 bit under the inverse-distance model), speak a little louder, or reduce the room noise, and calibrate again.

??? question "The VAD finds speech starting at frame 40 and ending at frame 90 of a 150-frame recording. Which frames does it keep, and why not exactly 40 to 90? Click to expand"
    It keeps frames 36 to 95. The first kept frame is \( 40 - 4 = 36 \) (4 frames of pre-roll) and the last is \( 90 + 5 = 95 \) (5 frames of hang-over). The extra frames keep soft sounds at the start and end of the phrase that were below the gate.

!!! mascot-celebration "A Microphone That Knows Its Room"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned how to measure a noise floor and a speech level, turn them into a signal-to-noise ratio and a level gate, save the result, and record and trim an utterance with push-to-talk. These are the foundations the wake-word detector in the next chapter stands on.

In [Chapter 12](../12-wake-word-detection/index.md) we turn these frames into features and score them against an enrolled "Hey Pico" template.
