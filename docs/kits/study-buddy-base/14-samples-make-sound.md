---
title: "Lab 14: Samples Make Sound"
description: "See a sine wave as a row of dots, hear it at eight pitches, and discover samples per cycle, the Nyquist limit, and aliasing, where a note above half the sample rate sounds lower than expected."
---

# Lab 14: Samples Make Sound

!!! mascot-welcome "Sound You Can See"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Lab 05 made sound from a list of numbers. This time you will draw every one of those numbers as a dot and hear what happens when a note has too few dots to be drawn properly. One of the notes will sound *wrong* on purpose. Let's listen closely!

| | |
|---|---|
| **Program** | `14-samples-make-sound.py` |
| **Parts needed** | The speaker, the display, and the buttons |
| **Time** | 25 minutes |
| **Makes sound?** | **Yes**. Keep `VOLUME` low. |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* What a **sample** is, and what **sample rate** means
* How to calculate **samples per cycle** for any note
* What the **Nyquist limit** is
* What **aliasing** is, and why a high note can sound like a lower one

## The Big Idea

A speaker cone moves in and out smoothly, but the Pico can only send it a list of numbers, once
every 1/16,000th of a second. Each number is one **sample**: where the cone should be at that
instant. A note of frequency `f` repeats `f` times a second, so each cycle of the wave gets

```
samples per cycle = sample rate / frequency
```

At the kit's rate of 16,000 samples a second:

| Frequency | Samples per cycle | What the dots look like |
|-----------|-------------------|--------------------------|
| 110 Hz | 145.5 | A very smooth, slow curve |
| 440 Hz | 36.4 | A smooth wave |
| 1,760 Hz | 9.1 | A visible zig-zag |
| 3,520 Hz | 4.5 | A rough wave |
| 7,000 Hz | 2.3 | Almost a straight zig-zag |

The higher the note, the **fewer dots** draw each wave.

### The Nyquist limit

The least number of samples that can still describe a wave is **2 per cycle**: one up, one
down. That happens at **half the sample rate**, which is 8,000 Hz here. It is called the
**Nyquist limit**.

Go **above** it and the samples cannot tell your wave apart from a *lower* one. The note you
hear is the wrong note. This is **aliasing**. The last step in the program is 10,000 Hz, which is
above the limit, and its samples are exactly those of a **6,000 Hz wave** (16,000 - 10,000). So
it sounds **lower** than the 7,000 Hz step just before it.

!!! mascot-thinking "Same Dots, Two Waves"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Draw a dot on a graph every time a clock ticks, and many different waves pass through the very same dots, the way many roads pass through the same two towns. When two waves fit the same dots, the Pico plays the slower one, and that is why movie wagon wheels seem to spin backwards.

Many things in the real world use this rule. CD audio uses 44,100 samples a second so it can
reproduce notes up to 22,050 Hz, just above what people can hear. The Study Buddy's microphone
uses 12,800 samples a second, so it can hear up to 6,400 Hz, which is plenty for speech.

## Walking Through the Code

### One function makes every sample

```python
def sample(freq, i, volume=VOLUME):
    return int(32767 * volume / 100 * math.sin(2 * math.pi * freq * i / RATE))
```

This is the same formula as Lab 05. Sample number `i` happens at time `i / RATE` seconds, and
the sine of the angle gives the cone position. Both **drawing** and **playing** use this one
function, so the dots on the screen are *exactly* the numbers sent to the speaker.

### Drawing the dots

```python
def plot(freq):
    ...
    for i in range(PLOT_SAMPLES):
        x = PLOT_X + i * PLOT_W // PLOT_SAMPLES
        y = PLOT_MID - sample(freq, i, 100) * PLOT_HALF // 32767
        display.fill_rect(x, y - 1, DOT, DOT, config.CYAN)
```

The plot shows the **first 72 samples**, one dot each, spread across a 280-pixel box. A sample
of 32767 is the top of the box and -32767 is the bottom, so `* PLOT_HALF // 32767` scales the
number to 52 pixels either way. Because the box shows only 72 samples, a low note shows only part of one cycle,
and a high note shows many.

### Playing the note

```python
def play(freq):
    count = RATE * NOTE_MS // 1000
    fade = RATE // 100
    buf = bytearray(count * 2)
    for i in range(count):
        level = min(1.0, i / fade, (count - i) / fade)
        struct.pack_into("<h", buf, i * 2, int(sample(freq, i) * level))
    audio.write(buf)
```

The note is 600 ms long (9,600 samples). The **fade** is the 10 ms ramp from Lab 05 that stops
clicks at the start and end.

### The buttons

| Button | Does |
|--------|------|
| **UP** | Next, higher frequency |
| **DOWN** | Previous, lower frequency |
| **MODE** | Plays the same one again |

Each press is an edge (a `1` to `0` change, as in Lab 11), and calls `show(index)`, which updates the text,
draws the dots, and plays the note. The index is kept in range with `min` and `max`:

```python
index = min(len(FREQS) - 1, index + 1)     # stops at the last item
index = max(0, index - 1)                  # stops at the first
```

### Warning the listener

```python
if freq > RATE // 2:
    put("past Nyquist: heard as %d Hz" % (RATE - freq), 252, config.RED)
elif per_cycle < 4:
    put("close to Nyquist", 252, config.color565(255, 140, 0))
```

The screen shows **close to Nyquist** in orange when a note has fewer than 4 samples per cycle,
and **past Nyquist: heard as 6000 Hz** in red when it is over the limit.

## Run It

Open `14-samples-make-sound.py` and press Run. It starts with 440 Hz. Press UP to climb
through the notes, and watch the dots and listen to the pitch.

## What PASS Looks Like

* Each press plays a note and redraws the dots.
* **Low notes** are smooth curves of many dots. **High notes** are a few dots in a zig-zag.
* The screen shows the samples per cycle, such as `36.4 samples per cycle` for 440 Hz.
* **10000 Hz sounds *lower* than 7000 Hz**, and the screen says why.

## If Something Goes Wrong

| What you hear or see | Likely cause | Fix |
|----------------------|--------------|-----|
| No sound | Speaker wiring | Run [Lab 05](05-speaker-tones.md) first |
| The 10000 Hz note does not sound lower than 7000 Hz | You may have missed the change | Play 7000 Hz and then 10000 Hz again, and listen for the *drop* in pitch |
| Very high notes are hard to hear | Small speakers are weak at high pitch | Hold the speaker closer, with `VOLUME` still low |
| Dots do not move | Buttons not wired | Run [Lab 03](03-buttons.md) |

## Try This

1. **Slower sampling.** Change `RATE` to `8000` (the I2S rate follows it). Which notes are now
   above Nyquist? Does 440 Hz sound any different?
2. **Prove the alias.** Add `9000` to `FREQS`. It should sound exactly like 7,000 Hz. Print a
   few samples of each: how are the two lists related?
3. **A square wave.** Replace `math.sin` with a square wave:
   `1 if (freq * i / RATE) % 1 < 0.5 else -1`. How do the dots change? How does the sound
   change?
4. **Find your highest hearing.** Add 12,000, 14,000, and 15,000 to `FREQS`. What does each
   alias to? Which can you actually hear?

??? tip "Hint for number 2"
    9,000 Hz is above Nyquist, and 16,000 - 9,000 = 7,000. The samples of 9,000 Hz are the
    *negatives* of those of 7,000 Hz, the same wave flipped upside down. Your ear cannot tell
    a flipped wave from the original, so they sound the same.

??? tip "Hint for number 3"
    A square wave has only two values, so the dots sit in two rows: top and bottom. A square
    wave sounds buzzy and bright compared to the smooth sine, because it contains many extra
    high-pitched parts.

## Check Your Understanding

1. How many samples per cycle does a 1,000 Hz note have at 16,000 samples a second?
2. What is the Nyquist limit when the sample rate is 12,800 Hz?
3. A 9,000 Hz note is played with a 16,000 Hz sample rate. What pitch do you hear?

??? question "Answers"
    1. 16,000 / 1,000 = 16 samples per cycle.
    2. Half of 12,800, which is 6,400 Hz.
    3. 7,000 Hz (16,000 - 9,000), because 9,000 is above the Nyquist limit of 8,000.

## Where Next

You know what a sample is. [Lab 15](15-sound-envelopes.md) asks why a piano and an organ playing
the *same note* sound so different.

*Related in this book:* [Chapter 3: Sound and Digital Audio Basics](../../chapters/03-sound-and-digital-audio/index.md)
and the [Sampling Explorer](../../sims/sampling-explorer/index.md) MicroSim.
