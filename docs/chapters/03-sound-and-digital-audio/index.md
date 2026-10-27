---
title: "Sound and Digital Audio Basics"
description: "How a sound wave becomes numbers: frequency, amplitude, sampling, sample rate, bit depth, the Nyquist limit, aliasing, clipping, WAV files, and the time and frequency domains."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 10:56:47"
version: 1.11
---

# Sound and Digital Audio Basics

## Summary

This chapter turns sound into numbers. Students learn what a sound wave is, how frequency and amplitude describe it, and how sampling, sample rate, and bit depth capture it digitally. It also introduces the Nyquist limit, aliasing, and the time and frequency domains, so every later audio and FFT chapter has its vocabulary in place.

## Concepts Covered

This chapter covers the following 13 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Sound Wave | 2282 |
| Frequency | 311 |
| Amplitude | 512 |
| Sampling | 1108 |
| Sample Rate | 210 |
| Bit Depth | 351 |
| WAV File Format | 11 |
| Time Domain | 96 |
| Nyquist Limit | 2 |
| Analog to Digital Conversion | 347 |
| Audio Clipping | 3 |
| Frequency Domain | 94 |
| Aliasing | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)

---

## Sound Is Something You Can Count

Your Open Study Buddy has to hear a question, and a microcontroller cannot hear anything. It can only work with numbers. So before we wire a microphone or play a note, we need to understand how a sound turns into numbers and how those numbers turn back into a sound. That is the whole subject of this chapter, and every audio chapter after it depends on it.

!!! mascot-welcome "Numbers That Sound Like Something"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter you will be able to look at a microphone setting like "12,800 samples per second, 24 bits" and know exactly what it keeps and what it throws away. That skill is what lets your buddy hear a question without drowning in data. Let's listen closely!

## The Sound Wave

A **sound wave** is a pattern of pressure changes that travels through the air. When you speak, your vocal cords vibrate, pushing air molecules together and then pulling them apart. That squeeze-and-stretch pattern spreads outward at about 343 meters per second in room-temperature air. When it reaches a microphone, the pressure pushes a tiny membrane back and forth. When a speaker plays sound, a cone moves back and forth and makes the same kind of pressure pattern in the air.

The key point is that sound is a *change over time*. A single pressure reading tells you nothing, but a long series of readings tells you everything. We draw this series as a wavy line, with time running left to right and pressure going up and down.

*Worked example.* A tuning fork that vibrates 440 times each second makes a sound wave that repeats every \( 1/440 \approx 0.00227 \) seconds, or 2.27 milliseconds. Because sound travels at 343 meters per second, one repeat of the pattern stretches over \( 343 / 440 \approx 0.78 \) meters in the air. A pressure sensor right next to the fork sees the pattern pass by 440 times per second.

Two numbers describe almost everything about a simple sound: how fast the pattern repeats, and how big the pressure swings are. We name them next.

| Where the wave is | What moves | Turns into |
|-------------------|------------|------------|
| In the air | Air molecules pushed and pulled | Pressure changes |
| At the microphone | A thin membrane | A tiny electrical signal |
| At the speaker | A cone driven by the amplifier | Pressure changes again |

## Frequency

**Frequency** is how many times per second a wave repeats. It is measured in **hertz** (Hz), where 1 Hz is one repeat per second. The time for one repeat is the **period**, and the two are opposites:

\[ T = \frac{1}{f} \]

Here \( f \) is the frequency in hertz and \( T \) is the period in seconds. Higher frequency means a shorter period, and your ear hears higher frequency as a higher pitch.

Doubling the frequency raises the pitch by one *octave*. The notes in the kit's speaker test (test 05) show this: A4 is 440 Hz, and the A one octave higher is 880 Hz.

| Sound | Approximate frequency | Period |
|-------|----------------------|--------|
| Lowest note a person can hear | 20 Hz | 50 ms |
| Low speaking voice (fundamental) | about 100 Hz | 10 ms |
| Middle C (C4), the first note in test 05 | 262 Hz | 3.82 ms |
| A4, the beep in test 05 | 440 Hz | 2.27 ms |
| Highest note in test 05 (C5) | 523 Hz | 1.91 ms |
| A high "s" sound in speech | 4,000 Hz and above | 0.25 ms |
| Highest note a young person can hear | 20,000 Hz | 0.05 ms |

Human speech is not one frequency. A voice has a base pitch, and on top of it are many higher frequencies that give each vowel and consonant its character. Most of what makes speech understandable lies below about 4,000 Hz, which is the reason old telephones got away with such a small range.

*Worked example.* How many dots will we need to draw one cycle of the 440 Hz beep if we measure 16,000 times per second? One cycle lasts 2.27 ms, and 16,000 measurements per second means one every 0.0625 ms, so one cycle gets \( 16000 / 440 \approx 36.4 \) measurements. At the microphone's 12,800 per second the same note gets \( 12800 / 440 \approx 29.1 \). We will use this idea in the next sections.

## Amplitude

**Amplitude** is how big the pressure swing is. A loud sound swings far from the resting level, and a quiet sound swings only a little. In a picture of the wave, amplitude is the height. The **peak amplitude** is the largest distance from the middle, and for digital audio it is the largest number.

Two sounds can have the same frequency and different amplitudes: a whisper and a shout of the same note. They look alike except for height.

Our ears do not hear amplitude as a straight line. Doubling the amplitude does not sound twice as loud; it adds a fixed step. Engineers measure that step in **decibels** (dB), and each doubling of amplitude adds about 6 dB:

\[ \text{change in dB} = 20 \log_{10}\left(\frac{A_2}{A_1}\right), \qquad \text{so doubling is } 20 \log_{10}(2) \approx 6.02 \text{ dB} \]

The kit uses the same idea in a simpler form. Test 06 finds the average distance of the samples from the middle and takes the log base 2 of it, and the result is a number it calls "bits." One bit more means the sound is twice as big, which is about 6 dB. The meter in that test runs from 9 bits to 21 bits, a span of 12 bits, which is about 72 dB. Its "I hear you" rule says speech is any frame 2.0 bits above the room's noise floor, which means \( 2^{2} = 4 \) times larger than the room.

| Amplitude relative to the room | Bits above the floor | Decibels |
|-------------------------------|----------------------|----------|
| Same as the room | 0 | 0 dB |
| 2 times | 1 | about 6 dB |
| 4 times (test 06's "heard" level) | 2 | about 12 dB |
| 8 times | 3 | about 18 dB |
| 1,024 times | 10 | about 60 dB |

!!! mascot-thinking "Measure in Doublings"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Why do the kit's meters count in doublings instead of raw numbers? A whisper and a shout can differ by a factor of a thousand, and a straight bar would show the whisper as nothing. A log scale gives both of them room on the same screen, and it matches how your ears work.

## From Air to Numbers: Analog to Digital Conversion

A sound wave is **analog**: the pressure can take any value at any instant, with infinite detail. A computer stores **digital** data: a list of whole numbers. **Analog-to-digital conversion** (ADC) is the process that changes the first into the second. It has two separate steps that every digital audio system performs.

1. **Sampling** measures the wave at regular moments in time.
2. **Quantization** rounds each measurement to the nearest value a fixed number of bits can store.

The Open Study Buddy does this in the microphone itself. The INMP441 is a MEMS microphone with its own converter built in. It senses the pressure, converts it to numbers, and sends the numbers to the Pico on the I2S wires. The Pico never sees an analog voltage from the microphone. (The RP2350 chip has its own 12-bit ADC for analog pins, but this kit does not use it for sound.) We follow the whole path in the table.

| Stage | Where it happens | What the signal is |
|-------|------------------|--------------------|
| 1. Pressure wave | The air in the room | Analog |
| 2. Membrane and amplifier | Inside the INMP441 | Analog voltage |
| 3. Sampling and quantizing | Inside the INMP441 | Numbers, 24 bits each |
| 4. I2S transfer | Three wires to the Pico | Digital stream |
| 5. Your code | MicroPython on the Pico | A buffer of integers |

Placing the converter in the microphone is a big help to builders. A converter right next to the membrane picks up less electrical noise than a long analog wire into the Pico would.

## Sampling

**Sampling** means measuring the wave at equal time steps and keeping only those measurements. Imagine taking a photograph of the wave's height 12,800 times each second. You do not keep the wave between the photographs. You keep a list of heights.

Each measurement is called a **sample**. A one-second recording at the kit's microphone setting is a list of 12,800 samples. A single frame in test 06 is 512 samples, which is exactly \( 512 / 12800 = 0.04 \) seconds, or 40 ms, of sound.

*Worked example.* A 1,000 Hz tone has a period of 1 ms. Sampled at 8,000 times per second, a sample is taken every 0.125 ms, so each cycle is described by 8 samples. Plotting those 8 dots per cycle, you can see the wave clearly. Now sample the same tone only 1,500 times per second. Each cycle gets 1.5 samples, which is not enough to draw the up and down of the wave. Something is lost, and we investigate what in the sections on the Nyquist limit and aliasing.

!!! mascot-tip "Count the Dots per Cycle"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    A fast sanity check for any audio setting is to divide the sample rate by the frequency you care about. If you get fewer than 2 samples per cycle, that frequency cannot be captured, no matter how good the microphone is.

## Sample Rate

The **sample rate** is the number of samples taken each second, measured in hertz. Higher rates capture more detail, and they also create more data, which a microcontroller must store and process.

| Use | Sample rate | Bytes per second (16-bit mono) |
|-----|-------------|-------------------------------|
| Old telephone | 8,000 Hz | 16,000 |
| Kit microphone (`MIC_SAMPLE_RATE`) | 12,800 Hz | 25,600 (51,200 stored as 32-bit samples) |
| Kit speaker tests (`RATE` in test 05) | 16,000 Hz | 32,000 |
| Music CD | 44,100 Hz | 88,200 |
| Video soundtrack | 48,000 Hz | 96,000 |

The kit uses 12,800 Hz because it is plenty for speech and keeps the later signal-processing work cheap. With 512-sample frames, 12,800 Hz makes each frame exactly 40 ms long, and it gives the FFT in Chapter 9 bins that are 25 Hz apart.

The right sample rate is a trade-off. Too low and you lose the high-frequency detail that makes the letters "s" and "f" clear. Too high and the Pico runs out of time or memory. The next two sections explain the limit that a rate sets, and an explorer after them lets you test it.


## The Nyquist Limit

The **Nyquist limit** is the highest frequency a given sample rate can capture, and it is exactly half the sample rate. To draw the up and down of a wave you need at least two samples in every cycle, one near the top and one near the bottom.

\[ f_{\text{Nyquist}} = \frac{f_s}{2} \]

Here \( f_s \) is the sample rate. The kit's 12,800 Hz microphone can capture frequencies up to 6,400 Hz, and the 16,000 Hz speaker tests can reproduce up to 8,000 Hz. Anything above the limit is not captured correctly, which brings us to the problem it causes.

## Aliasing

**Aliasing** is what happens to a frequency above the Nyquist limit: it does not vanish, it turns into a false lower frequency. The sampled dots land at positions that also fit a slower wave, and the slower wave is what the computer sees. It works like a movie in which a wagon wheel seems to spin backwards because the camera takes too few pictures per second.

A tone at frequency \( f \) between \( f_s/2 \) and \( f_s \) shows up at \( f_s - f \). With the microphone at 12,800 Hz, a 7,000 Hz whistle appears as a 5,800 Hz tone. Once the samples are stored there is no way to tell the false tone from a real one.

The defense is to keep high frequencies out before sampling. Most audio systems use a filter, or they sample at a rate far above what they need. The INMP441 has a built-in digital filter that follows the sample rate and removes most frequencies above the Nyquist limit, so outside sounds alias very little with this microphone. The rule still matters for sound your own code makes, as the warning below shows.

!!! mascot-warning "Pick Your Rate on Purpose"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If a tone you generate in code sounds lower than you asked for, check its frequency against half of `RATE`. Anything above that limit folds down, so ask for a frequency below it or raise the sample rate.

Now test the folding rule yourself.

#### Diagram: Sampling Explorer

<iframe src="../../sims/sampling-explorer/main.html" width="100%" height="547px" scrolling="no"></iframe>

<details markdown="1">
<summary>Sampling Explorer</summary>
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
</details>

## Bit Depth

Sampling decides *when* to measure. **Bit depth** decides *how precisely*. It is the number of bits used to store each sample, and it fixes how many different values a sample can have. With \( n \) bits there are \( 2^n \) possible values:

\[ \text{levels} = 2^{n} \]

| Bit depth | Number of levels | Where it appears |
|-----------|-----------------|------------------|
| 8 bits | 256 | Simple, low-quality audio |
| 12 bits | 4,096 | The Pico's own ADC (not used for sound here) |
| 16 bits | 65,536 | The speaker samples in test 05 and CD audio |
| 24 bits | 16,777,216 | The real audio inside each INMP441 sample |
| 32 bits | 4,294,967,296 | The word the INMP441 sends, with 24 audio bits inside |

Rounding a measurement to the nearest level introduces a small error called **quantization error**. More bits mean smaller steps, so smaller errors. Each extra bit doubles the number of levels and adds about 6 dB of range between the loudest sound and the quietest detail, so 16 bits gives about 96 dB and 24 bits about 144 dB.

*Worked example.* A signed 16-bit sample holds whole numbers from -32,768 to 32,767. A sample of 0 is the resting level. A loud peak is near 32,767. In test 05 the amplitude of a tone is `32767 * volume / 100`, so a volume of 40 produces peaks of about 13,107, which is 40 percent of full scale.

The INMP441 reports 24 bits of audio inside a 32-bit word. This is why the kit's code shifts each microphone sample right by 8 (`MIC_SAMPLE_SHIFT = 8`): the 24 real bits sit in the top of the 32-bit number, and shifting by 8 puts them where Python expects. The next activity lets you see what the number of levels does to a wave.

#### Diagram: Bit Depth Quantizer

<iframe src="../../sims/bit-depth-quantizer/main.html" width="100%" height="502px" scrolling="no"></iframe>

<details markdown="1">
<summary>Bit Depth Quantizer</summary>
Type: microsim
**sim-id:** bit-depth-quantizer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the number of levels available at a given bit depth, and the smallest bit depth that provides a required number of levels, for 5 challenge questions, with all 5 correct within two attempts each.

**Prerequisites:** bit depth, levels, quantization error, powers of two (all defined in the section "Bit Depth" above this block).

**Evidence of Mastery:** For each of the 5 challenge questions the learner types a number. An answer is correct when it equals the Answer column in Content exactly. Mastery is 5 of 5 correct, with up to two attempts per question. Moving the bit-depth control and watching the staircase is exploration, not evidence.

**Misconceptions:** (1) Each extra bit adds a fixed number of levels instead of doubling them. (2) A higher bit depth makes the sound's pitch more accurate. (3) 8 bits is half as good as 16 bits.

**Instructional Rationale:** Apply-level calculation of 2 to the power n needs repeated practice with a check. Seeing the staircase get finer as the number of levels doubles gives the learner a mental picture to check the arithmetic against.

**Content:**

The sim draws one cycle of a sine wave and the staircase of its quantized version. The learner chooses the bit depth for exploration: minimum 1, maximum 16, step 1, unit bits, default 4. The sim shows the number of levels for the chosen bit depth after the learner changes it.

Challenge questions, in this order:

| # | Question | Answer | Why (shown as feedback) |
|---|---|---|---|
| 1 | How many levels does 3-bit audio have? | 8 | 2 x 2 x 2 = 8. |
| 2 | How many levels does 8-bit audio have? | 256 | 2 to the power 8 is 256. |
| 3 | How many levels does the Pico's 12-bit ADC have? | 4096 | 2 to the power 12 is 4,096. |
| 4 | How many levels does 16-bit audio have? | 65536 | 2 to the power 16 is 65,536. |
| 5 | What is the smallest bit depth with at least 1,000 levels? | 10 | 2 to the power 9 is 512, which is too few, and 2 to the power 10 is 1,024. |

**Provenance:** The levels follow from the formula levels = 2 to the power n given in the chapter. The 12-bit figure is the RP2350 ADC resolution mentioned in the chapter.

**Rules:** levels = 2 to the power n. The quantized value of a sample x between -1.0 and +1.0 is the nearest of the evenly spaced levels between -1.0 and +1.0, with spacing 2 / (levels - 1). A sample exactly halfway between two levels rounds up. Answers are whole numbers typed without commas.

**Learner Activity:**

1. The learner moves the bit-depth control from 1 to 16 and watches the staircase get finer and the level count double each step.
2. The learner starts the challenges and types an answer to question 1.
3. The sim says whether the answer is correct. After a wrong first answer, the learner may try once more.
4. After a second wrong answer, the sim shows the answer and the Why text, and the question counts as missed.
5. After question 5, the sim shows the score. The learner should notice that adding one bit always doubles the number of levels.

**Feedback:** 5 questions, fixed order, two attempts each. Correct: "Correct: <Why>". First incorrect: "Not quite. Think about doubling for each bit. Try again." Second incorrect: "The answer is <answer>: <Why>". A running score "n of 5" is shown.

**Starting State:** The sine wave and its 4-bit staircase are shown with the text "16 levels" and the question "What happens to the staircase as you add bits?"

**Chapter Anchors:** The chapter states that n bits give 2 to the power n levels, that 16 bits give 65,536 levels, and that each extra bit adds about 6 dB.
</details>

## Audio Clipping

**Audio clipping** happens when a signal tries to go beyond the biggest number the storage can hold. The peaks are cut off flat, and the cut-off peaks sound like a harsh crackle. Clipping can happen at the microphone when the sound is too loud, or in your code when you multiply samples to make them louder.

In test 07 the playback code multiplies the recorded samples by `PLAYBACK_GAIN` and then limits them with `max(-32768, min(32767, ...))`. That limit is the clipping step: a value above 32,767 is replaced by 32,767.

*Worked example.* A sample of 6,000 played with a gain of 2 becomes 12,000, which is fine. With a gain of 8 it becomes 48,000, which is more than 32,767, so it is clipped to 32,767. If every peak of a sine wave is clipped this way, the top of the wave becomes a flat line, and your ear hears the crackle that the test warns about when `PLAYBACK_GAIN` is too high.

The fix is the same as for any clipping problem: reduce the gain or move the source farther away, so that the peaks stay inside the range.

## The WAV File Format

A **WAV file** is the simplest common way to store sound on a computer. It is a small header followed by the raw samples, with no compression. The header, which is 44 bytes in its standard form, tells a program how to read the samples: how many channels, how many samples per second, and how many bits per sample.

| Header field | Size | Value for the kit's recording |
|--------------|------|-------------------------------|
| `RIFF` marker | 4 bytes | the text "RIFF" |
| File size minus 8 | 4 bytes | data length + 36 |
| `WAVE` marker | 4 bytes | the text "WAVE" |
| `fmt ` marker and its size | 8 bytes | "fmt " and 16 |
| Format code | 2 bytes | 1 (plain uncompressed samples) |
| Channels | 2 bytes | 1 (mono) |
| Sample rate | 4 bytes | 12,800 |
| Bytes per second | 4 bytes | 25,600 |
| Bytes per sample frame | 2 bytes | 2 |
| Bits per sample | 2 bytes | 16 |
| `data` marker and length | 8 bytes | "data" and the number of sample bytes |

The code below builds that header with the `struct` module from Chapter 2. The format string packs each field in the order of the table, using `<` for little-endian, `4s` for four text bytes, `I` for a 4-byte unsigned number, and `H` for a 2-byte unsigned number.

```python
import struct

def wav_header(data_bytes, rate=12800, bits=16, channels=1):
    byte_rate = rate * channels * bits // 8
    block = channels * bits // 8
    return struct.pack("<4sI4s4sIHHIIHH4sI",
                       b"RIFF", 36 + data_bytes, b"WAVE",
                       b"fmt ", 16, 1, channels, rate, byte_rate, block, bits,
                       b"data", data_bytes)
```

*Worked example.* Test 07 recorded 1.50 seconds, which is 19,200 samples at 12,800 Hz. Converted to 16-bit samples, that is 38,400 bytes of sound data. The file would be 44 + 38,400 = 38,444 bytes, and `wav_header(38400)` produces exactly the 44 bytes in front. Open the saved file on a computer and any audio player will play it.

## Two Views of the Same Sound

### The Time Domain

The **time domain** is the view we have used so far: the sound drawn as height versus time. It is what a microphone records and what a speaker plays. A time-domain picture is good at showing *when* things happen: a clap is a sudden spike, speech rises and falls in bursts, and silence is a flat line near the middle.

### The Frequency Domain

The **frequency domain** shows the same sound as how much of each frequency it contains. The horizontal axis is frequency in hertz, and the height of each bar is the amount at that frequency. A single steady 440 Hz beep is one tall bar at 440 Hz. A voice is a cluster of bars: a low base pitch and a family of higher ones.

The two views contain exactly the same information, drawn from different angles. The time domain shows *when*, and the frequency domain shows *what pitches*. Chapter 9 teaches the algorithm, the FFT, that converts from one to the other quickly on the Pico.

| Sound | Time domain looks like | Frequency domain looks like |
|-------|-----------------------|-----------------------------|
| Silence | Flat line near the middle | Very small bars everywhere |
| A steady beep | Smooth repeating wave | One tall bar |
| Two notes at once | A wave that wobbles in shape | Two tall bars |
| A clap | One tall, sharp spike | Low bars spread across many frequencies |
| A vowel in speech | Repeating pattern with a wobble | A base bar plus a family of higher bars |
| Steady hiss | Rough, random-looking wave | Bars of similar height across many frequencies |

!!! mascot-encourage "Two Pictures, One Sound"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Seeing a sound as bars instead of a wiggly line feels odd at first, and that is normal. You already read maps and graphs; this is one more way to look at the same data. Try the viewer below and change one control at a time.

#### Diagram: Time and Frequency Domain Viewer

<iframe src="../../sims/time-and-frequency-domain-viewer/main.html" width="100%" height="577px" scrolling="no"></iframe>

<details markdown="1">
<summary>Time and Frequency Domain Viewer</summary>
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
</details>

## Putting It All Together

You can now follow a sound all the way into the Pico. Air pressure moves the membrane in the microphone. The microphone's converter measures it at the sample rate and rounds each measurement to the bit depth. The numbers arrive at the Pico as a stream, and your code can look at them in the time domain or, after Chapter 9, in the frequency domain.

Key takeaways:

- A sound wave is a pattern of pressure changes over time, described mainly by its frequency (pitch) and amplitude (size).
- Analog-to-digital conversion is sampling plus quantization, and the INMP441 does it inside the microphone.
- The sample rate sets the highest frequency you can capture: the Nyquist limit, which is half the sample rate. For the kit's 12,800 Hz rate it is 6,400 Hz.
- A frequency above the limit does not vanish; it aliases as a false lower tone, so a 7,000 Hz tone sampled at 12,800 Hz appears at 5,800 Hz.
- Bit depth sets how many levels a sample can hold: \( 2^n \) levels for \( n \) bits.
- Clipping flattens peaks that exceed the range and sounds like crackle.
- A WAV file is a 44-byte header plus raw samples.
- The time domain shows when, and the frequency domain shows which pitches.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "A tone at 5,000 Hz is sampled at 8,000 Hz. What frequency appears in the samples? Click to expand"
    3,000 Hz. The Nyquist limit is 4,000 Hz, and 5,000 Hz is above it, so the tone folds to 8,000 - 5,000 = 3,000 Hz.

??? question "Why does a 16-bit sample hold 65,536 values, and what is the smallest and largest signed value? Click to expand"
    Each of the 16 bits doubles the choices, so there are \( 2^{16} = 65{,}536 \) values. As a signed number the smallest is -32,768 and the largest is 32,767.

!!! mascot-celebration "Sound, Now in Numbers"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned how frequency and amplitude describe a wave, how sample rate and bit depth turn it into numbers, and why 12,800 Hz caps the kit's hearing at 6,400 Hz. Every audio chapter ahead builds on these ideas.

In Chapter 4 we meet the five hardware parts that make, capture, and play these sounds.
