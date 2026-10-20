---
title: "Signal Processing and the FFT"
description: "How to turn a 40 ms frame of microphone samples into loudness and pitch information: RMS and decibels, the Fourier transform, the DFT and FFT, bins, windowing, magnitude spectra, log-spaced bands, and live volume meter and spectrum displays on the round screen."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 12:59:57"
version: 1.11
---

# Signal Processing and the FFT

## Summary

This chapter turns raw samples into information about frequency. Students learn the Fourier transform, the DFT, and the FFT, then see how bins, windowing, and magnitude spectra describe a sound. They apply the results to loudness, band energies, volume meters, and a spectrum display on the round screen.

## Concepts Covered

This chapter covers the following 24 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Fourier Transform | 93 |
| Discrete Fourier Transform | 92 |
| FFT | 91 |
| Frequency Bin | 67 |
| Windowing | 3 |
| Twiddle Factors | 4 |
| Bit-Reversal Table | 3 |
| In-Place Transform | 1 |
| Real-Valued Input | 1 |
| Magnitude Spectrum | 64 |
| Hann Window | 1 |
| Spectral Leakage | 1 |
| FFT Size | 3 |
| Spectrogram | 1 |
| Log Magnitude | 31 |
| Band Energy | 29 |
| RMS Loudness | 157 |
| DC Offset Removal | 1 |
| Bin Width | 2 |
| Log-Spaced Bands | 28 |
| Decibels | 8 |
| Spectrum Display | 1 |
| Volume Meter | 2 |
| Peak Frequency Detection | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 3: Sound and Digital Audio Basics](../03-sound-and-digital-audio/index.md)
- [Chapter 6: Drawing Directly to Display Regions](../06-display-regions-and-drawing/index.md)
- [Chapter 8: I2S Audio: Recording and Playing Sound](../08-i2s-audio/index.md)

---

## One Frame, Two Questions

At the end of Chapter 8 you had a loop that reads one 40 ms frame at a time: 512 numbers, 2,048 bytes, 25 times a second. A list of 512 numbers can answer two questions, and they need different tools. *How loud is it?* needs only a little arithmetic on the samples. *Which pitches are in it?* needs a transform that turns the 512 samples into a picture of frequency. This chapter answers the first question, then the second, and then draws both answers on the round screen.

!!! mascot-welcome "Turn Sound into a Picture"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter your Study Buddy will show a live volume meter and a spectrum of dancing bars, and it will be able to tell you which note you are whistling. Let's listen closely! You will also see why one clever algorithm makes all of it possible on a tiny chip.

Everything in this chapter is in one small library, `src/chapters/09-signal-processing-fft/dsp.py`, and seven numbered scripts beside it. The library is plain MicroPython, so most of it also runs on your computer, which is the quickest way to check your understanding. Anything about how *fast* it runs on the Pico is saved for Chapter 10.

## Cleaning the Frame: DC Offset Removal

The microphone's samples do not swing evenly around zero. They carry a small constant shift called the **DC offset** (DC stands for direct current, meaning a value that does not oscillate). Chapter 8 measured it on the test board: it wandered between about -5,400 and +9,100 from one frame to the next, and the 1.5 second recording in test 07 averaged about 15,000. A constant shift is not sound, but it would add a false "loudness" and a false spike at the lowest frequency, so the first step of every analysis is **DC offset removal**: find the frame's average and subtract it from every sample.

```python
total = 0
for i in range(n):
    total += raw[i] >> shift          # shift is 8: 32-bit word to 24-bit value
dc = total // n                       # the frame's average
x = (raw[i] >> shift) - dc            # a DC-free sample
```

*Worked example.* Suppose a four-sample frame reads 3, 5, 4, 8. The average is \( (3+5+4+8)/4 = 5 \), so the DC-free samples are -2, 0, -1, 3. Their average is now 0, as it must be. Measure the offset over the frame you are processing and never assume a fixed number, because the offset moves.

## RMS Loudness

Loudness should depend on how far the samples swing, not on which way they swing. **RMS loudness** does this. RMS stands for root mean square, and the name is the recipe, read right to left: square each DC-free sample, take the mean of the squares, then take the square root.

\[ \text{RMS} = \sqrt{\frac{1}{N}\sum_{i=0}^{N-1}\left(x_i - \bar{x}\right)^2} \]

Here \( x_i \) are the samples, \( \bar{x} \) is their average (the DC offset), and \( N \) is 512. Squaring makes every term positive and gives big swings more weight than small ones. The square root at the end puts the answer back in the same units as the samples. Chapter 8's loudness function used the *average distance* from the middle instead. Both rise and fall together, but RMS is the standard measure and the one that connects to power and decibels, so this chapter uses it.

*Worked example.* Take the DC-free frame -2, 0, -1, 3 from above. The squares are 4, 0, 1, 9, which sum to 14. The mean is \( 14/4 = 3.5 \) and the root is \( \sqrt{3.5} \approx 1.87 \). For a pure sine wave of amplitude \( A \), the RMS is always \( A/\sqrt{2} \approx 0.707\,A \), while the average distance is \( 2A/\pi \approx 0.637\,A \). A sine of amplitude 1,000 therefore has an RMS of 707.1.

| Signal | Peak | Average distance | RMS | RMS / peak |
|--------|------|------------------|-----|------------|
| Sine wave of amplitude 1,000 | 1,000 | 636.6 | 707.1 | 0.707 |
| Square wave of amplitude 1,000 | 1,000 | 1,000 | 1,000 | 1.000 |
| Constant 1,000 after DC removal | 0 | 0 | 0 | not defined |

The last row is the point of the previous section: a constant has no loudness. In `dsp.py`, `load_frame()` computes the DC offset and then the RMS in one pass over the frame and returns both. If you only need loudness, `frame_rms()` skips the window and the FFT entirely and is the cheaper call.

## Decibels

Chapter 3 introduced the **decibel** (dB) as the unit that matches how ears hear: each doubling of amplitude adds about 6 dB. Decibels always compare two amplitudes, so you must choose a reference. For an amplitude (a sample, an RMS, or an FFT magnitude) the formula is

\[ \text{level in dB} = 20 \log_{10}\left(\frac{A}{A_{\text{ref}}}\right) \]

and for an energy or power, which is an amplitude squared, it is \( 10 \log_{10}(E/E_{\text{ref}}) \). The two formulas agree because \( 20 \log_{10}(A) = 10 \log_{10}(A^2) \). The most useful reference for a microphone is full scale, giving **dBFS**: decibels relative to the largest sample the converter can deliver. Our samples are 24-bit signed values, so full scale is \( 2^{23} = 8{,}388{,}608 \). A reading is then

\[ \text{dBFS} = 20 \log_{10}\left(\frac{\text{RMS}}{2^{23}}\right), \]

which is always negative, and a full-scale sine (RMS 0.707 of full scale) reads -3.0 dBFS. In code, `dsp.to_db(rms, 1 << 23)` does it, and it clamps the answer at -120 dB so a silent frame cannot take the log of zero.

*Worked example.* The test tone used to check the display scripts has amplitude 200,000, so its RMS is \( 200{,}000/\sqrt{2} = 141{,}421 \), and \( 20\log_{10}(141{,}421/8{,}388{,}608) = -35.5 \) dBFS. Chapter 8's quiet room read 13.1 bits, a mean distance of about \( 2^{13.1} - 1 \approx 8{,}780 \). Random noise has an RMS about 1.25 times its average distance, so the room is roughly 11,000 RMS, or about -58 dBFS. That is a *modelled* estimate from Chapter 8's measurement, not a new measurement. Chapter 8's self-hearing tone, at 17.0 bits, comes out near -35 dBFS by the same arithmetic.

| Amplitude relative to full scale | Decibels (dBFS) | Same amplitude in bits (\( \log_2 \) of the amplitude) |
|---|---|---|
| 1 (the largest sample) | 0 | about 23 bits |
| 0.5 | -6.0 | about 22 bits |
| 0.1 | -20.0 | about 19.7 bits |
| 0.01 | -40.0 | about 16.4 bits |
| 0.001 | -60.0 | about 13.0 bits |

Every row follows from \( 20\log_{10} \), and the bits column follows from \( 1 \text{ bit} \approx 6.02 \text{ dB} \).

!!! mascot-tip "Decibels Turn Multiplying into Adding"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    To sanity-check a dB value, remember that every 6 dB is a doubling and every 20 dB is a factor of 10. If your meter says -40 dBFS, the signal is 100 times smaller than full scale, so you know the number is plausible before you look at the screen.

## The Volume Meter

A **volume meter** draws the current RMS level as a bar. It is the simplest useful display on the device, and it needs no FFT. `06-volume-meter.py` converts each frame's RMS to dBFS, maps -70 to -20 dBFS onto a 200-pixel bar, and shows the number as text. The ends of the scale are chosen for the modelled room (about -58 dBFS) and the loud tone (about -35 dBFS) above; change `METER_MIN_DBFS` and `METER_MAX_DBFS` to suit your room.

The bar uses the Chapter 6 dirty-region idea. When the level rises, only the new slice is painted. When it falls, only the slice that vanished is erased.

```python
def draw_bar(width):
    old = shown_width
    if width > old:
        display.fill_rect(METER_X + old, METER_Y, width - old, METER_HEIGHT, color)
    else:
        display.fill_rect(METER_X + width, METER_Y, old - width, METER_HEIGHT, TRACK)
```

The real script also repaints the whole bar when the color zone changes, so the colors stay right. The number is redrawn only when its text changes, and it is padded with `.center(10)` so a shorter value covers the longer one (the Chapter 6 text-padding rule). Redrawing the whole 200 by 26 bar would send \( 200 \times 26 \times 2 = 10{,}400 \) bytes, at least 3.5 ms at 24 MHz; a typical slice sends a few hundred. Chapter 8's budget leaves room for either, because the meter's only other work is the cheap RMS pass.

## From Loudness to Pitch: The Fourier Transform

RMS tells you how much, never which pitches. Think of a chord played on a piano. Your ear hears three notes at once, but a microphone records one wiggling line that is the *sum* of three sine waves. The **Fourier transform** is the mathematical tool that takes the wiggling line and recovers the recipe: which sine waves, at which frequencies, in what amounts. It is named for Joseph Fourier, who showed that any reasonable repeating signal can be built by adding sine waves.

This is the time domain and frequency domain from Chapter 3, made precise. The time-domain view lists the amplitude at each moment. The frequency-domain view lists the amount at each frequency. They hold the same information, and the Fourier transform converts one into the other.

The pure form of the transform works on continuous signals that last forever, so a computer cannot compute it directly. A microcontroller has 512 samples, and the three names in this chapter describe the step-down from the ideal to the practical.

| Name | Input | Output | Used here? |
|------|-------|--------|------------|
| Fourier transform | A continuous signal, over all time | A continuous function of frequency | No; it is the idea |
| Discrete Fourier transform (DFT) | N samples | N numbers, one per frequency bin | Yes; it is the definition |
| Fast Fourier transform (FFT) | N samples (N a power of 2) | The same N numbers as the DFT | Yes; it is the algorithm |

!!! mascot-thinking "A Recipe for Sound"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Think of the transform as running a recipe backwards: the signal is the finished dish, and the spectrum lists the ingredients and how much of each. Notice that nothing is lost, because the same sound can be rebuilt from its ingredients.

*Worked example.* Build a 16-sample frame by adding a sine wave that fits 2 whole cycles into the frame to half of a sine wave that fits 5 whole cycles. The transform of this frame has energy in exactly two places, the 2-cycle slot and the 5-cycle slot, in the ratio 2 to 1. `01-dft-by-hand.py` computes it and prints magnitudes of 8.0 at slot 2 and 4.0 at slot 5, with zero everywhere else. (The numbers are \( N/2 = 8 \) times the amplitudes 1 and 0.5; the next section explains why.) The slots are called bins.

## The Discrete Fourier Transform

The **discrete Fourier transform** (DFT) computes the frequency recipe for exactly \( N \) samples. It produces \( N \) numbers, \( X[0] \) to \( X[N-1] \), one for each probe frequency. The probe for number \( k \) is a sine and a cosine that complete exactly \( k \) cycles in the frame. To measure how much of probe \( k \) is in the signal, multiply the signal by the probe sample by sample and add everything up. If the signal contains that frequency, the products are mostly positive and the sum is big. If it does not, the positive and negative products cancel and the sum is near zero.

\[ X[k] = \sum_{t=0}^{N-1} x[t]\left(\cos\frac{2\pi k t}{N} \;-\; j\,\sin\frac{2\pi k t}{N}\right) \]

The letter \( j \) is the imaginary unit, \( j^2 = -1 \). It simply lets one number carry two parts: the real part is the sum of the sample-times-cosine products, and the imaginary part is the negative of the sum of the sample-times-sine products. Each \( X[k] \) is therefore a pair, \( (\text{re}, \text{im}) \), and the code stores them in two arrays. Why both? A tone's cosine probe and sine probe tell you where in its cycle the wave starts (its phase); together their size tells you how much of the frequency is present. You will take the size and ignore the phase.

*Worked example.* Let \( N = 4 \) and \( x = [0, 1, 0, -1] \), one cycle of a sine wave. For \( k = 1 \) the probe angles \( 2\pi t/4 \) are 0, 90, 180 and 270 degrees. Only \( x[1] = 1 \) and \( x[3] = -1 \) are nonzero.

| Term | Sample | Angle | Cosine | Sine | Contribution to re | Contribution to im |
|------|--------|-------|--------|------|-------------------|--------------------|
| t = 1 | 1 | 90 degrees | 0 | 1 | 1 x 0 = 0 | -(1 x 1) = -1 |
| t = 3 | -1 | 270 degrees | 0 | -1 | -1 x 0 = 0 | -(-1 x -1) = -1 |
| Sum \( X[1] \) | | | | | 0 | -2 |

So \( X[1] = -2j \), with magnitude 2. The same arithmetic gives \( X[0] = 0 \), \( X[2] = 0 \) and \( X[3] = +2j \). The magnitudes are 0, 2, 0, 2: the energy appears at bin 1 and again, mirrored, at bin 3. That mirror is a general fact, and the "Real-Valued Input" section explains it.

The cost is the catch. Each of \( N \) outputs sums \( N \) products, so the DFT does \( N^2 \) multiply-adds. For \( N = 512 \) that is \( 512 \times 512 = 262{,}144 \) of them in every 40 ms frame. `naive_dft()` in `dsp.py` is this definition, written out in a few lines. It is slow on purpose and exists to check the fast version.

!!! mascot-encourage "Complex Numbers Are Just Pairs"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    If \( j \) and "imaginary" sound intimidating, that is normal, because the word is unfortunate. In the code there is nothing imaginary: each result is two ordinary numbers, `re[k]` and `im[k]`. Run `01-dft-by-hand.py` and follow the four-number example term by term, and it will click.

## The FFT: Same Answer, a Hundred Times Less Work

The **FFT** (fast Fourier transform) is an algorithm that computes exactly the same \( N \) numbers as the DFT with far less arithmetic. The derivation is outside this course, but the shape of the result is easy to see. The FFT splits the job into \( \log_2 N \) stages. In each stage it combines pairs of numbers with a small operation called a **butterfly**, and each stage needs \( N/2 \) butterflies. The total is \( (N/2)\log_2 N \) butterflies instead of \( N^2 \) multiply-adds.

*Worked example.* For \( N = 512 \), \( \log_2 512 = 9 \), so the FFT does \( 256 \times 9 = 2{,}304 \) butterflies, against 262,144 for the DFT, a ratio of 113.8. `02-fft-vs-dft.py` prints the whole table:

| N | DFT: \( N^2 \) | FFT: \( (N/2)\log_2 N \) | Ratio |
|---|----------------|------------------------|-------|
| 8 | 64 | 12 | 5.3 |
| 64 | 4,096 | 192 | 21.3 |
| 256 | 65,536 | 1,024 | 64.0 |
| 512 | 262,144 | 2,304 | 113.8 |
| 1,024 | 1,048,576 | 5,120 | 204.8 |

A butterfly is not the same size as a DFT term (a butterfly takes four multiplications and six additions), so read the last column as "about a hundred times less work". The saving grows with \( N \): doubling the frame quadruples the DFT's work but only a little more than doubles the FFT's. This is what makes real-time spectra possible on a microcontroller at all.

!!! mascot-thinking "Faster, Not Rougher"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    The FFT is not an approximation of the DFT. It gives the same numbers, to rounding, by reusing partial results instead of recomputing them, like adding a column of figures once and reusing the subtotals.

Before the code, three terms. Each butterfly multiplies one of its two numbers by a *twiddle factor*; the pairs are found by first *reordering* the samples with a *bit-reversal table*; and all of it happens *in place*. The next three subsections define them.

### Twiddle Factors

A **twiddle factor** is the constant that a butterfly multiplies by. It is a point on a circle, \( W_N^k = \cos(2\pi k/N) - j\sin(2\pi k/N) \), the same cosine and sine probes the DFT used. There are only \( N/2 \) different ones, because the rest repeat or are negatives of these. For \( N = 512 \) that is 256 pairs of numbers. Computing a sine takes far longer than looking one up, so `make_tables()` computes the cosines and sines once, at start-up, into two arrays of 256 entries (1,024 bytes each as 4-byte floats), and the FFT only reads them.

| k | Angle \( 2\pi k/8 \) | Cosine | Sine |
|---|----------------------|--------|------|
| 0 | 0 degrees | 1.0000 | 0.0000 |
| 1 | 45 degrees | 0.7071 | 0.7071 |
| 2 | 90 degrees | 0.0000 | 1.0000 |
| 3 | 135 degrees | -0.7071 | 0.7071 |

The table shows the four distinct factors for an 8-point FFT; \( W_8^4 \) to \( W_8^7 \) are the negatives of these. In the code, the sign of the sine is applied inside the butterfly: `tr = re[b]*c + im[b]*s` and `ti = im[b]*c - re[b]*s`.

### The Bit-Reversal Table

The butterflies work most easily when the inputs are in a scrambled order: the sample that belongs at position \( i \) is moved to the position whose binary number is \( i \) written backwards. A **bit-reversal table** stores that new position for every index, so the reorder is a lookup, and `make_tables()` builds it once.

| Index | Binary | Reversed | New position |
|-------|--------|----------|--------------|
| 0 | 000 | 000 | 0 |
| 1 | 001 | 100 | 4 |
| 2 | 010 | 010 | 2 |
| 3 | 011 | 110 | 6 |
| 4 | 100 | 001 | 1 |
| 5 | 101 | 101 | 5 |
| 6 | 110 | 011 | 3 |
| 7 | 111 | 111 | 7 |

Index 1 and 4 swap, and 3 and 6 swap, while 0, 2, 5, and 7 stay where they are. The code swaps only when `rev[i] > i`, so every pair swaps exactly once and nothing is swapped back. For \( N = 512 \) the table has 512 entries of 2 bytes, 1,024 bytes in all.

### In Place, and for Real Input

The FFT is an **in-place transform**: each butterfly reads two numbers and writes its two results back into the same two slots, so the output overwrites the input and no second buffer is needed. The whole transform for 512 points lives in two arrays of 512 4-byte floats, 4,096 bytes together. The price is that the original samples are gone afterward; keep a copy if you need them. In Chapter 10 this matters for a different reason: an in-place algorithm allocates no memory while it runs.

The microphone samples are **real-valued input**: ordinary numbers with no imaginary part. The FFT is built for complex input, so you load the samples into the `re` array and fill the `im` array with zeros. For real input, the output has a pattern, which you saw in the four-number example: \( X[N-k] \) is the mirror image of \( X[k] \) (its complex conjugate), so the second half of the output repeats the first half. Only bins 0 to \( N/2 \) carry new information. That is why the kit uses 256 of the 512 outputs. (Clever programs use the redundancy to transform two real frames with one complex FFT; this book does not.)

```python
def fft(re, im, tables):
    rev, cos_t, sin_t = tables
    n = len(re)
    for i in range(n):                          # step 1: bit-reversal reorder
        j = rev[i]
        if j > i:
            re[i], re[j] = re[j], re[i]
            im[i], im[j] = im[j], im[i]
    half = 1
    while half < n:                             # step 2: log2(n) stages
        stride = n // (2 * half)                # twiddle step for this stage
        for start in range(0, n, 2 * half):
            for k in range(half):
                a = start + k
                b = a + half
                c = cos_t[k * stride]
                s = sin_t[k * stride]
                tr = re[b] * c + im[b] * s      # twiddle times the second number
                ti = im[b] * c - re[b] * s
                re[b] = re[a] - tr              # the butterfly: difference ...
                im[b] = im[a] - ti
                re[a] += tr                     # ... and sum, written in place
                im[a] += ti
        half *= 2
```

Read it in two steps. Step 1 is the bit-reversal reorder. Step 2 has three nested loops: the `while` loop is the stage (`half` doubles from 1 to 256, giving 9 stages), the `for start` loop walks across the groups, and the `for k` loop does the butterflies inside a group. For the 8-point example the stages pair the following positions:

| Stage | Distance (`half`) | Pairs combined | Twiddle indices used (`k * stride`) |
|-------|-------------------|----------------|-------------------------------------|
| 1 | 1 | (0,1) (2,3) (4,5) (6,7) | 0 |
| 2 | 2 | (0,2) (1,3) (4,6) (5,7) | 0, 2 |
| 3 | 4 | (0,4) (1,5) (2,6) (3,7) | 0, 1, 2, 3 |

That is 4 butterflies per stage and 3 stages, 12 in all, matching \( (8/2)\log_2 8 = 12 \). `02-fft-vs-dft.py` checks this code against `naive_dft()` on 64 random numbers, and on the machine used to write this chapter the two agreed to within a few parts in ten million.

!!! mascot-warning "Size Must Be a Power of Two"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    The bit-reversal trick only works when N is a power of 2, so `make_tables(500)` raises a `ValueError`. If you want a different frame length, pick 128, 256, 512, or 1024, and remember the frame must still be read from the microphone in that many samples.

## Frequency Bins and Bin Width

Each of the \( N/2 \) useful outputs is a **frequency bin**: a slot that collects the energy of every sound close to one particular frequency. Bin \( k \) is centered on \( k \) cycles per frame. A frame lasts \( N/R \) seconds, where \( R \) is the sample rate, so \( k \) cycles per frame is \( k \cdot R/N \) cycles per second:

\[ f_k = k\,\frac{R}{N}, \qquad \text{bin width } \Delta f = \frac{R}{N}. \]

The **bin width** is the gap between neighboring bins. For the kit, \( R = 12{,}800 \) Hz and \( N = 512 \), so the bin width is \( 12{,}800/512 = 25 \) Hz. Bin 0 is 0 Hz (the DC slot), bin 1 is 25 Hz, bin 40 is 1,000 Hz, and bin 255 is 6,375 Hz. Bin 256 would be exactly 6,400 Hz, the Nyquist limit from Chapter 3, which is the top of what 12,800 samples per second can represent. The code uses bins 0 to 255.

To go the other way, a tone of frequency \( f \) lands at \( k = f \cdot N/R = f/25 \), a number that is usually not whole. `03-bin-calculator.py` prints the kit's arithmetic:

| Tone | Bin \( f/25 \) | Nearest bin | Nearest bin's center | Tone minus center |
|------|---------------|-------------|----------------------|-------------------|
| 100 Hz | 4.00 | 4 | 100 Hz | 0 Hz |
| 262 Hz (middle C) | 10.48 | 10 | 250 Hz | +12 Hz |
| 440 Hz (concert A) | 17.60 | 18 | 450 Hz | -10 Hz |
| 1,000 Hz | 40.00 | 40 | 1,000 Hz | 0 Hz |
| 1,012.5 Hz | 40.50 | 41 | 1,025 Hz | -12.5 Hz |
| 6,375 Hz | 255.00 | 255 | 6,375 Hz | 0 Hz |

The bin width is the finest pitch distinction the frame can make: two tones closer together than about one bin width, 25 Hz, merge into one lump. The worst-case error when you read a pitch off the nearest bin is half a bin, 12.5 Hz. Both numbers come straight from \( R/N \). Use the explorer below to practice the arithmetic.

#### Diagram: FFT Bin Calculator


<iframe src="../../sims/fft-bin-calculator/main.html" width="100%" height="532px" scrolling="no"></iframe>
[Run FFT Bin Calculator Fullscreen](../../sims/fft-bin-calculator/main.html)

<details markdown="1">
<summary>FFT Bin Calculator</summary>
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
</details>

## The Magnitude Spectrum

Each \( X[k] \) is a pair \( (\text{re}, \text{im}) \). The **magnitude spectrum** keeps only how big each pair is, by the Pythagorean theorem:

\[ |X[k]| = \sqrt{\text{re}[k]^2 + \text{im}[k]^2}. \]

Plotted against frequency, the magnitudes show which pitches are present and how strongly. The phase, the angle of the pair, says where in its cycle each wave starts, and for loudness displays you throw it away. `dsp.magnitudes()` is a loop over bins 0 to 255.

```python
def magnitudes(re, im, out):
    for k in range(len(out)):
        out[k] = math.sqrt(re[k] * re[k] + im[k] * im[k])
```

The magnitudes are not in the same units as the samples. The DFT *adds up* \( N \) products, so a steady sine of amplitude \( A \) that sits exactly on a bin produces a magnitude of \( A \cdot N/2 \) at that bin. The Fourier worked example near the start of this chapter hinted at this number (8.0 for amplitude 1 in a 16-sample frame), and it is easy to check at full size.

*Worked example.* A 1,000 Hz sine of amplitude 1,000 sampled at 12,800 Hz fits exactly 40 cycles in 512 samples. The FFT gives a magnitude of \( 1{,}000 \times 512/2 = 256{,}000 \) at bin 40 and zero (to within rounding) at every other bin. A tone half as loud would give 128,000. Reading a spectrum is therefore a two-axis job:

| Axis | Reads as | Units |
|------|----------|-------|
| Bin number | Pitch: \( k \times 25 \) Hz | hertz |
| Magnitude | Amplitude: divide by \( N/2 = 256 \) to get the tone's amplitude | same as the samples, times 256 |
| Phase (discarded) | Where the wave starts in its cycle | not used here |

Notice that the spectrum answers a different question from RMS. RMS is a single number for the whole frame. The magnitude spectrum is 256 numbers, one per 25 Hz, and its sum of squares is tied to the RMS, because the same energy is just counted by pitch instead of by moment.

!!! mascot-thinking "One Number Versus 256"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    RMS squeezes the whole frame into one loudness number. The spectrum spreads the same energy across 256 pitches. Notice that nothing is added: the FFT only re-sorts what the frame already contains.

## Windowing, the Hann Window, and Spectral Leakage

The test tone above was chosen to fit a whole number of cycles in the frame. Real sounds do not. The FFT quietly assumes that the frame repeats forever, like a loop of tape. If the frame ends part-way through a wave, the end does not join the beginning, and the repeated signal has a jump at every seam. That jump is not part of the sound, but the transform dutifully reports it, as a smear of energy across many bins. This smear is **spectral leakage**.

Take a 1,012.5 Hz tone, which is bin 40.5, exactly between bins 40 and 41. With no special treatment, `04-leakage-hann.py` shows the leakage: bin 40 has 163,903 and bin 41 has 162,059, but there are also 10 bins in total with at least 10% of the peak, and the bin 20 away from the peak is still only 33.5 dB below it.

The fix is **windowing**: multiply the frame by a smooth curve that fades the samples to zero at both ends before taking the FFT. With the ends at zero, the repeated copies join without a jump. The standard curve is the **Hann window**, a gentle hill:

\[ w[i] = 0.5 - 0.5\cos\left(\frac{2\pi i}{N}\right), \qquad i = 0 \ldots N-1. \]

It is 0 at the first sample, rises to 1 in the middle (sample 256), and falls back toward 0. `dsp.hann_table()` computes the 512 values once; `load_frame()` multiplies each DC-free sample by its window value as it loads. Windowing costs one multiplication per sample and makes the leakage dramatically smaller, but it has two prices: the peak is half as tall (the window's average height is 0.5), and a tone on a bin center now covers three bins instead of one.

| Tone | Where | Window | Bins at least 10% of the peak | 20 bins from the peak |
|------|-------|--------|-------------------------------|-----------------------|
| 1,000 Hz | bin 40.0 | none | 1 | below -100 dB (rounding only) |
| 1,000 Hz | bin 40.0 | Hann | 3 | below -100 dB (rounding only) |
| 1,006.25 Hz | bin 40.25 | none | 5 | -37.0 dB |
| 1,006.25 Hz | bin 40.25 | Hann | 3 | -90.3 dB |
| 1,012.5 Hz | bin 40.5 | none | 10 | -33.5 dB |
| 1,012.5 Hz | bin 40.5 | Hann | 4 | -87.3 dB |

All six rows come from running `04-leakage-hann.py` on a test tone of amplitude 1,000, no microphone needed. Read the table as a trade: if you know your tone sits on a bin, no window is sharper (1 loud bin, not 3). For real sounds, whose frequencies are anywhere, the Hann window gives a far cleaner picture, about 54 dB less leakage at 20 bins out in the last pair of rows. That is why the display scripts always use it. The 0.5 gain only changes the vertical scale, and `dsp.dbfs_reference()` includes it.

!!! mascot-warning "Unwindowed Frames Look Messy"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If your spectrum has a wide skirt around every note, you probably forgot the window. Check that `load_frame()` received the Hann table, not `None`, and that the table is built with the same N as the FFT.

Try the explorer to see leakage change as you slide a tone across a bin.

#### Diagram: Spectral Leakage Explorer


<iframe src="../../sims/spectral-leakage-explorer/main.html" width="100%" height="552px" scrolling="no"></iframe>
[Run Spectral Leakage Explorer Fullscreen](../../sims/spectral-leakage-explorer/main.html)

<details markdown="1">
<summary>Spectral Leakage Explorer</summary>
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
</details>

## Choosing the FFT Size

The **FFT size** is the number of samples \( N \) in one transform. It sets everything at once. The frame lasts \( N/R \) seconds, the bin width is \( R/N \), and there are \( N/2 \) useful bins. Because bin width times frame length is always 1 (the product of \( R/N \) and \( N/R \)), you cannot improve one without worsening the other: a longer frame resolves finer pitches but reacts more slowly.

| FFT size | Frame length | Bin width | Useful bins | Butterflies |
|----------|--------------|-----------|-------------|-------------|
| 128 | 10 ms | 100 Hz | 64 | 448 |
| 256 | 20 ms | 50 Hz | 128 | 1,024 |
| 512 | 40 ms | 25 Hz | 256 | 2,304 |
| 1,024 | 80 ms | 12.5 Hz | 512 | 5,120 |

The kit uses 512, which is `config.FFT_SIZE`: 25 Hz is fine enough to separate neighboring musical notes above roughly 400 Hz, 40 ms is quick enough for a display that updates 25 times a second, and Chapter 8 already organized the microphone loop around frames of exactly that length.

## Peak Frequency Detection

**Peak frequency detection** answers the question "what note is that?" Find the bin with the largest magnitude and report its frequency. For a pure whistle this works well.

```python
best = first_bin                      # start above bin 0 to skip the DC end
for k in range(first_bin, len(mag) - 1):
    if mag[k] > mag[best]:
        best = k
frequency = best * rate / n
```

The answer can only be a multiple of the bin width, so the error can be up to 12.5 Hz. A 440 Hz tone lands at bin 17.6, the loudest bin is 18, and the reported frequency is 450 Hz, 10 Hz too high. A cheap refinement fits a parabola through the log-magnitudes of the peak bin and its two neighbors and takes the top of the parabola. `dsp.peak_frequency(refine=True)` does it, and `04-leakage-hann.py` shows it recovering 439.7 Hz for the 440 Hz test tone, an error of -0.3 Hz.

Two cautions. In a quiet room the loudest bin is just noise, so the scripts report a peak only when the RMS is above a gate (`PEAK_GATE_DBFS`, set to -50 dBFS, a guess to tune for your room). And speech has many peaks at once (a voice is a stack of harmonics), so the loudest bin is a poor description of a voice. Later chapters therefore use the whole spectrum, not one peak.

## Log Magnitude

Magnitudes cover a huge range. The test tone above peaks at 256,000, a quiet room's bins may be near 1,000, and a full-scale sine would reach about \( 1.07 \times 10^9 \). A bar drawn in proportion to magnitude would be invisible for everything except the loudest sounds, and it would not match how the ear hears. The **log magnitude** is the magnitude converted to decibels, \( 20\log_{10}(|X[k]|/|X|_{\text{ref}}) \), so equal ratios become equal steps.

The reference that makes the scale meaningful is the peak that a full-scale sine would give with the Hann window: \( 2^{23} \times 512/2 \times 0.5 = 1{,}073{,}741{,}824 \). `dsp.dbfs_reference()` returns it, and it is 180.6 dB on its own scale. With this reference a bin's level reads in dBFS, where 0 means a full-scale tone exactly on that bin.

*Worked example.* The Hann-windowed 1,000 Hz tone of amplitude 1,000 has a peak magnitude of 128,000 at bin 40. Its level is \( 20\log_{10}(128{,}000/1{,}073{,}741{,}824) = -78.5 \) dBFS. A tone half as loud sits 6 dB lower, at -84.5 dBFS, and a tone ten times quieter sits 20 dB lower. Equal ratios line up as equal distances, which is what a bar chart needs.

## Band Energy and Log-Spaced Bands

A spectrum of 256 bars does not fit on a round screen as bars you can read, and most of the bars carry nothing you care about. The fix is to group neighboring bins into a few **bands** and add up their energy. The **band energy** is the sum of the squared magnitudes of the bins in the band:

\[ E_{\text{band}} = \sum_{k \,\in\, \text{band}} |X[k]|^2. \]

Squaring gives energy, so the decibel form is \( 10\log_{10}(E/E_{\text{ref}}) \), with \( E_{\text{ref}} \) the square of the reference magnitude above.

The next question is where the band edges go. Equal-width bands would give 16 bands of 16 bins (400 Hz) each. The ear does not hear that way: it judges pitch by ratio, so the step from 100 Hz to 200 Hz sounds the same as the step from 1,000 Hz to 2,000 Hz, even though the first is a 100 Hz change and the second a 1,000 Hz one. **Log-spaced bands** follow the ear. Each band's top edge is a fixed multiple of its bottom edge. For 16 bands from 100 Hz to 6,400 Hz, the total ratio is 64, so each band's edges differ by the factor \( 64^{1/16} = 1.2968 \). `dsp.log_band_edges()` computes the edges, rounds them to bins, and stretches any band narrower than one bin to one bin. `03-bin-calculator.py` prints the result:

| Band | Bins | Frequencies (Hz) | Bins in band |
|------|------|------------------|--------------|
| 0 | 4 | 100 to 125 | 1 |
| 1 | 5 to 6 | 125 to 175 | 2 |
| 2 | 7 to 8 | 175 to 225 | 2 |
| 3 | 9 to 10 | 225 to 275 | 2 |
| 4 | 11 to 14 | 275 to 375 | 4 |
| 5 | 15 to 18 | 375 to 475 | 4 |
| 6 | 19 to 24 | 475 to 625 | 6 |
| 7 | 25 to 31 | 625 to 800 | 7 |
| 8 | 32 to 40 | 800 to 1,025 | 9 |
| 9 | 41 to 53 | 1,025 to 1,350 | 13 |
| 10 | 54 to 69 | 1,350 to 1,750 | 16 |
| 11 | 70 to 90 | 1,750 to 2,275 | 21 |
| 12 | 91 to 116 | 2,275 to 2,925 | 26 |
| 13 | 117 to 151 | 2,925 to 3,800 | 35 |
| 14 | 152 to 196 | 3,800 to 4,925 | 45 |
| 15 | 197 to 255 | 4,925 to 6,400 | 59 |

The rounding is visible at the bottom: bands 0 to 3 are all one or two bins wide, because a 25 Hz bin is a large share of a 25 to 50 Hz band. The bands start at 100 Hz, not 0, because the lowest bins hold the DC residue and rumble.

*Worked example.* The 1,000 Hz Hann-windowed test tone of amplitude 1,000 has magnitudes 64,000, 128,000 and 64,000 at bins 39, 40 and 41. Bins 39 and 40 are in band 8 and bin 41 is in band 9. Band 8's energy is \( 64{,}000^2 + 128{,}000^2 = 2.048 \times 10^{10} \) and band 9's is \( 64{,}000^2 = 4.096 \times 10^{9} \). Band 8 is five times stronger, \( 10\log_{10} 5 = 7.0 \) dB. In dBFS, band 8 reads \( 10\log_{10}\left(2.048\times10^{10} / (1.0737\times10^{9})^2\right) = -77.5 \) dBFS: a little higher than the -78.5 dBFS peak because the band also holds a neighbor bin.

#### Diagram: Log Band Layout Explorer


<iframe src="../../sims/log-band-layout-explorer/main.html" width="100%" height="562px" scrolling="no"></iframe>
[Run Log Band Layout Explorer Fullscreen](../../sims/log-band-layout-explorer/main.html)

<details markdown="1">
<summary>Log Band Layout Explorer</summary>
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
</details>

## The Spectrogram

One spectrum describes one 40 ms frame. A **spectrogram** stacks the spectra of consecutive frames into a picture: time runs along one axis, frequency along the other, and the level at each point is shown as brightness or color. A steady whistle makes a horizontal line, a rising whistle makes a diagonal, and a clap makes a vertical stripe. At 25 frames per second, a 32-row spectrogram of the 16 bands covers 1.28 seconds and fits in \( 32 \times 16 = 512 \) bytes.

Because this display has no frame buffer, a scrolling picture cannot slide the old rows down. The trick is the one from Chapter 8's ring buffer: write each new row in the next row position and wrap around to the top, so every frame draws only one row. A row of 16 cells that are 12 pixels wide and 6 high is \( 16 \times 12 \times 6 \times 2 = 2{,}304 \) bytes, at least 0.8 ms at 24 MHz. Building this is an extension exercise, not one of the seven scripts.

## The Spectrum Display

The **spectrum display** is the live bar chart that this chapter has been building toward. `07-spectrum-display.py` does the whole job for every frame: load and window, FFT, magnitudes, band energies, convert each band to decibels, and move each bar to its new height. The bars use the Chapter 6 dirty-region rule: a bar that grows gets a slice of color added on top, and a bar that shrinks gets a slice of black painted over its top.

| Part | Value |
|------|-------|
| Bars | 16, each 12 pixels wide with a 3 pixel gap |
| Bar area | 237 pixels wide, up to 120 pixels high, baseline at y = 250 |
| Full redraw of the bar area | \( 237 \times 120 \times 2 = 56{,}880 \) bytes, at least 19.0 ms at 24 MHz |
| Level scale | -90 dBFS (empty bar) to -30 dBFS (full 120-pixel bar), so 2 pixels per decibel; the ends are a starting guess to tune for your room |
| Labels | 100, 800, and 6.4k under the bars; the peak frequency below |

```python
def draw_bar(i, height):
    old = shown[i]
    if height == old:
        return
    x = BARS_X + i * (BAR_WIDTH + BAR_GAP)
    if height > old:
        display.fill_rect(x, BASELINE - height, BAR_WIDTH, height - old, colors[i])
    else:
        display.fill_rect(x, BASELINE - old, BAR_WIDTH, old - height, BLACK)
    shown[i] = height
```

The whole bar area stays inside the visible circle (the corner at the bottom-left of the bars, at x = 61, y = 250, is 119 pixels from the center along one axis and 70 along the other, a distance of 138 pixels, well inside the 168-pixel safe radius from `config.py`). For each frame, `shown[i]` remembers what is on the glass, so only the difference travels over the SPI wire.

## The Whole Pipeline, and What It Costs

Everything in this chapter is one chain, and each stage's cost class is easy to count.

| Stage | Function in `dsp.py` | Work per 512-sample frame |
|-------|----------------------|--------------------------|
| Read the frame | `readinto()` | waits for the microphone (up to 40 ms) |
| DC removal, RMS, Hann window | `load_frame()` | 3 passes over 512 samples |
| FFT | `fft()` | 2,304 butterflies |
| Magnitudes | `magnitudes()` | 256 square roots |
| Band energies | `band_energies()` | 256 multiply-adds |
| Decibels and bar heights | `to_db()`, `scale()` | 16 logarithms |
| Redraw changed bars | `fill_rect()` | only the changed slices |

Chapter 8's budget says that all of this must finish within 40 ms. The FFT dominates, and **this chapter's FFT is plain Python, which is slow**. I expect it to take several frame times: a rough guess from similar boards is somewhere between 100 and 300 ms for the 2,304 butterflies, which would be 3 to 8 frames. That is a guess, not a measurement. The scripts print the real value, in the "work ms" column of `05-mic-spectrum-text.py` and the summary line of `07-spectrum-display.py`, and Chapter 10 measures it carefully and then makes it faster. Until then, the scripts use `dsp.latest_frame()` to skip the frames that pile up while the FFT runs, so the display shows the present, a few times a second, instead of a delayed past. The last column of `05` counts the skipped frames.

The files for this chapter:

| File | Parts needed | What it shows |
|------|--------------|---------------|
| `01-dft-by-hand.py` | none | The four-number DFT term by term, then two tones |
| `02-fft-vs-dft.py` | none | FFT equals DFT; operation counts |
| `03-bin-calculator.py` | none | Bin width, bins for tones, the 16 band edges |
| `04-leakage-hann.py` | none | Leakage with and without Hann; peak frequency refinement |
| `05-mic-spectrum-text.py` | Microphone | RMS, dBFS, peak frequency, and band digits as text |
| `06-volume-meter.py` | Display + microphone | RMS volume meter with changed-slice redraw |
| `07-spectrum-display.py` | Display + microphone | 16-band live spectrum on the round screen |

Upload and run them as described in `src/chapters/README.md`; the folder's own `README.md` says what PASS looks like for each.

## Putting It All Together

A frame of 512 samples is a 40 ms sound. Remove its average, and the leftover swing is its loudness, which you can measure in RMS and show in decibels as a volume meter. To learn which pitches it contains, window it with Hann, and transform it with the FFT, a fast way to get the DFT's 512 numbers, of which 256 are useful, each a bin of 25 Hz. Take their magnitudes, group them into log-spaced bands, convert to decibels, and draw only the bars that moved.

Key takeaways:

- RMS loudness is the square root of the mean of the squared, DC-free samples; remove the frame's own average first, because the microphone's offset drifts.
- Decibels compare amplitudes with \( 20\log_{10} \) (or energies with \( 10\log_{10} \)); relative to full scale (\( 2^{23} \)) they are negative, and every 6 dB is a doubling.
- The Fourier transform recovers the sine-wave recipe of a signal; the DFT does it for N samples in \( N^2 \) steps; the FFT does it in \( (N/2)\log_2 N \), which is 2,304 butterflies instead of 262,144 for N = 512.
- Twiddle factors and the bit-reversal table are computed once; the FFT then runs in place, in two 512-entry arrays.
- Bin \( k \) is at \( k \times 25 \) Hz; the bin width is \( R/N = 25 \) Hz; the useful bins are 0 to 255 because real input mirrors.
- A tone not on a bin center leaks; the Hann window cuts the leakage by tens of decibels at the price of half the peak and a three-bin-wide peak.
- The magnitude spectrum is \( \sqrt{\text{re}^2 + \text{im}^2} \); an on-bin sine of amplitude A peaks at \( A \cdot N/2 \) (halved by Hann).
- Show decibels, not raw magnitudes, and group the 256 bins into log-spaced bands whose edges grow by a constant ratio.
- Draw by changed slice, and measure the pure-Python pipeline before you trust it to fit in 40 ms.

Test yourself with these questions, and click each one to reveal its answer.

??? question "A tone of 3,000 Hz is played at 12,800 samples per second with a 512-point FFT. Which bin has the most energy, and which log band is it in? Click to expand"
    \( 3{,}000/25 = 120 \), so bin 120, which is exactly on a bin center. Band 13 holds bins 117 to 151, so the tone is in band 13.

??? question "You move the sample rate to 25,600 Hz but keep N = 512. What happens to the bin width and the frame length? Click to expand"
    The bin width doubles to \( 25{,}600/512 = 50 \) Hz and the frame length halves to 20 ms. Product of the two stays 1, so a shorter frame always means coarser bins.

??? question "Why does a spectrum from a frame that is not windowed show a wide skirt around a pure tone? Click to expand"
    The FFT treats the frame as if it repeats forever. A tone that does not fit a whole number of cycles leaves a jump where the end meets the start, and the jump spreads energy into many bins. A window that fades the ends to zero removes the jump.

!!! mascot-celebration "From Samples to a Spectrum"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned how RMS and decibels measure loudness, how the DFT and the FFT turn 512 samples into 256 bins of 25 Hz, and how windowing, magnitudes, and log-spaced bands become a live spectrum on the round screen. The spectrum is yours to draw, and the next step is making it fast.

In Chapter 10 we measure how long this pure-Python pipeline really takes on the Pico, and then make it fast enough for the 40 ms budget.
