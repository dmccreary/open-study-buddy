---
title: "Lab 15: Envelopes"
description: "Play the same four notes with four different loudness shapes (pluck, organ, swell, bell) and learn how an envelope, not the pitch, makes an instrument sound like itself."
---

# Lab 15: Envelopes

!!! mascot-welcome "Same Notes, Different Instruments"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    A guitar and a pipe organ can play the very same note and still sound nothing alike. This lab plays the same four notes four times, and the only thing that changes is the *shape* of how loud each note is. Let's listen closely!

| | |
|---|---|
| **Program** | `15-sound-envelopes.py` |
| **Parts needed** | The speaker, the display, and the buttons |
| **Time** | 25 minutes |
| **Makes sound?** | **Yes** |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* What an **envelope** is
* How to **multiply** a wave by an envelope to shape it
* The four parts of an envelope: **attack, decay, sustain, release**
* How to build a **lookup table** to avoid slow math

## The Big Idea

An **envelope** is how loud a note is at each moment, from 0 (silent) to 1 (full). To give a
plain wave the shape of an envelope, **multiply every sample by the envelope's value at that
moment**:

```
sample = wave(t) * envelope(t)
```

When the envelope is 1, the note is at full volume. When it is 0.5, the note is half as loud.
When it is 0, you hear nothing. The notes (the pitch) never change. Only the shape does.

| Envelope | Shape | Sounds like |
|----------|-------|-------------|
| **PLUCK** | Instant start, then dies away fast | A guitar string |
| **ORGAN** | Quick start, holds steady, quick stop | Air through a pipe |
| **SWELL** | Fades in slowly, then stops | A bowed violin |
| **BELL** | Instant start, rings for a long time | A struck bell |

Musicians describe an envelope in four parts, often called **ADSR**:

| Part | Meaning |
|------|---------|
| **A**ttack | How fast the note gets loud when it starts |
| **D**ecay | How fast it drops after the first burst |
| **S**ustain | The level it holds while the key is down |
| **R**elease | How fast it fades after the key is let go |

The **pluck** is almost all decay. The **organ** is almost all sustain.

!!! mascot-thinking "Your Ear Listens to the Shape"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    The brain recognizes an instrument mostly by the first fraction of a second of each note and by how the note fades. If you cut the start off a piano note, many people cannot say what instrument it was.

## Walking Through the Code

### An envelope is a small function

```python
def pluck(t):
    return math.exp(-t / 90)

def organ(t):
    return min(1.0, t / 15, (NOTE_MS - t) / 30)

def swell(t):
    return min(t / (NOTE_MS * 0.8), 1.0, (NOTE_MS - t) / 20)

def bell(t):
    return math.exp(-t / 400) * min(1.0, t / 2 + 0.01)
```

Each function takes `t`, the number of **milliseconds since the note started**, and returns how
loud it should be.

* **`pluck`** uses `math.exp(-t / 90)`, an **exponential decay**. At t = 0 it is 1, and it falls
  to about 37 percent of its value every 90 ms (the `90` is the *time constant*). It dies away
  smoothly, like a real string.
* **`organ`** uses `min()` of three straight lines: a **ramp up** over 15 ms (`t / 15`), a flat
  **1.0** in the middle, and a **ramp down** over the last 30 ms (`(NOTE_MS - t) / 30`). Whichever is
  smallest wins. That makes a trapezoid.
* **`swell`** is the same idea, but the ramp up takes 80 percent of the note.
* **`bell`** multiplies a slow exponential decay (`-t / 400`) by a very fast ramp up (2 ms),
  so it starts instantly and rings on.

### A lookup table

```python
def table(shape):
    return [max(0.0, min(1.0, shape(t))) for t in range(NOTE_MS)]
```

Calling `math.exp` for each of 16,000 samples a second would be slow. Instead, the program
works the envelope out **once per millisecond** into a list of 500 numbers (for a 500 ms note).
Each sample then **looks up** its millisecond:

```python
level = levels[i * 1000 // RATE]
```

Sample number `i` happens at `i * 1000 / RATE` milliseconds, so that is the position in the
list. `max(0.0, min(1.0, ...))` is the clamp trick from [Lab 07](07-record-playback.md),
keeping every value between 0 and 1.

!!! mascot-tip "Precompute What Never Changes"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    If you will use the same expensive answer thousands of times, work it out once, put it in a list, and look it up. This trade of memory for speed shows up all over embedded programming.

### Making a note

```python
def note(freq, levels):
    count = RATE * NOTE_MS // 1000
    peak = 32767 * VOLUME / 100
    step = 2 * math.pi * freq / RATE
    buf = bytearray(count * 2)
    for i in range(count):
        level = levels[i * 1000 // RATE]
        struct.pack_into("<h", buf, i * 2, int(peak * level * math.sin(step * i)))
    return buf
```

This is the sine wave from Lab 05, with one extra factor: `level`. The variable `step` is
computed once, outside the loop, to save a multiply per sample.

### Four notes, back to back

```python
NOTES = (523, 659, 784, 1047)         # C5 E5 G5 C6: a C major arpeggio
notes = [note(freq, levels) for freq in NOTES]
for buf in notes:
    audio.write(buf)
```

The four notes (C, E, G, and C an octave higher) make a **C major arpeggio**. The program builds all
four first, then plays them, so there is no gap while the Pico calculates.

### The plot

The envelope is also **drawn** as a curve in the plot box, with a time axis along the bottom (0 to
500 ms) and a loudness axis along the left. You can *see* the shape you are hearing.

## Run It

Open `15-sound-envelopes.py` and press Run. It plays PLUCK first. Press **UP** or **DOWN** to
change the envelope, and **MODE** to hear it again.

## What PASS Looks Like

Four very different sounds from the same four notes, each with its envelope drawn as a curve:

* **PLUCK**: a quick spike that decays smoothly
* **ORGAN**: a flat-topped trapezoid
* **SWELL**: a slow ramp up
* **BELL**: a sharp spike with a long, slow tail

## If Something Goes Wrong

| What you hear or see | Likely cause | Fix |
|----------------------|--------------|-----|
| No sound | Speaker wiring | Run [Lab 05](05-speaker-tones.md) |
| Notes sound gapped or choppy | Not enough memory, or notes made while playing | The program builds all four notes first; do not change that |
| `MemoryError` | `NOTE_MS` too large | Keep each note near 500 ms |
| A click at the end of the BELL | The tail cuts off | Add a short fade, as in Lab 05 |

## Try This

1. **Faster and slower.** Make PLUCK die faster (change `90` to `30`), then slower (to `300`). At
   what point does it stop sounding plucked?
2. **Your own envelope.** Write a "tremolo" that wobbles: `0.6 + 0.4 * math.sin(t / 20)`. Add it
   to `ENVELOPES`.
3. **A real bell.** Give BELL two waves at once, the note and a quieter one at 2.76 times its
   frequency, the way a real bell rings. Does it sound more like a bell?
4. **ADSR.** Write an envelope with all four parts: it ramps to 1 in 10 ms, falls to 0.6 over
   100 ms, holds at 0.6, then fades over the last 80 ms.

??? tip "Hint for number 3"
    In `note()`, change the sample line to add a second sine:
    `wave = math.sin(step * i) + 0.5 * math.sin(2.76 * step * i)`. The result can be up to 1.5, so
    divide by 1.5 to keep it from clipping. Real bells ring at frequencies that are *not* whole-number
    multiples of the main note, and that gives them their clang.

??? tip "Hint for number 4"
    Use `if` and `elif` on `t`:

    ```python
    def adsr(t):
        if t < 10:
            return t / 10
        if t < 110:
            return 1 - 0.4 * (t - 10) / 100
        if t > NOTE_MS - 80:
            return 0.6 * (NOTE_MS - t) / 80
        return 0.6
    ```

## Check Your Understanding

1. What does an envelope multiply?
2. Which envelope has almost all **decay** and almost no **sustain**?
3. Why does the program precompute the envelope into a list?
4. If an envelope's value is 0.25 at some moment, how loud is the sample compared with the
   plain wave?

??? question "Answers"
    1. Every sample of the wave.
    2. The PLUCK.
    3. Working out `math.exp` for 16,000 samples a second is too slow, so it computes 500 values
       once and looks them up.
    4. One quarter of the volume.

## Where Next

You have made sound. [Lab 16](16-mic-oscilloscope.md) turns the kit around and *draws* the sound
the microphone hears.

*Review in the course:* [Sound, Music, and Audio](https://dmccreary.github.io/learning-micropython/chapters/18-sound-music-audio/)
