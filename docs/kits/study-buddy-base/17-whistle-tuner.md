---
title: "Lab 17: A Whistle Tuner"
description: "Measure the pitch of a whistle by counting upward zero crossings, then turn the frequency into a note name and a needle that shows whether you are sharp or flat."
---

# Lab 17: A Whistle Tuner

!!! mascot-welcome "Is That Note in Tune?"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Whistle a note and your Study Buddy will tell you its frequency, its musical name, and whether you are a little sharp or a little flat. You are about to build a tuner like the ones guitar players use. Let's listen closely, and try to hold that note steady!

| | |
|---|---|
| **Program** | `17-whistle-tuner.py` |
| **Parts needed** | The microphone and the display |
| **Time** | 30 minutes |
| **Makes sound?** | No (but *you* will!) |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* How to measure **frequency** by counting **zero crossings**
* What **hysteresis** is, and why noise makes it necessary
* What a **noise gate** does
* How a frequency becomes a **note name** and **cents**, using a logarithm

## The Big Idea

### Frequency from crossings

A steady note is a wave that crosses the middle line **going upward once every cycle**. If you
count the upward crossings in a frame and time how far apart the first and last are, you can
work out the frequency:

```
frequency = (crossings - 1) * RATE / (samples from first crossing to last)
```

Why `crossings - 1`? Three crossings mark only **two** full cycles: the gaps *between* crossings are
the cycles. For example, if a 1,000 Hz whistle is sampled at 12,800 samples per second, one cycle
is 12.8 samples. Over 80 cycles, the first and last crossings are about 80 x 12.8 = 1,024 samples
apart, and `(81 - 1) * 12800 / 1024` is close to 1,000.

### Two tricks that make it work on real sound

**Hysteresis.** Near the middle line, noise wiggles the signal back and forth across it,
making false crossings. So a crossing only counts once the signal has gone properly **low**
(below `-LEVEL`) and **then** properly **high** (above `+LEVEL`). `LEVEL` is 30 percent of the
frame's peak. Think of a light switch that needs a firm push, not a tickle.

**A noise gate.** A quiet room has no pitch at all, so frames that are not clearly **louder than
the room** are ignored, instead of shown as nonsense numbers. For the first second, the program
measures the room's **noise floor**, as in Lab 06. A frame must be **4 times louder** (`GATE = 4`)
to count.

!!! mascot-thinking "Hysteresis Is a Door with a Latch"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A door that swings open at the slightest breeze would bang all night, so doors have latches that only let go when you push properly. The `armed` flag in this lab works the same way: it will not count a crossing until the signal has first gone clearly low.

### From frequency to note

Music divides each **octave** (a doubling of frequency) into **12 steps**, so each step is
a factor of 2<sup>1/12</sup> (about 1.0595) higher than the one before. The reference is **A4 =
440 Hz**, and A4 is note number 69. So

```
note number = 69 + 12 * log2(frequency / 440)
```

The **whole part** is the nearest note. The leftover, times 100, is how many **cents** sharp (+)
or flat (-) you are. **100 cents make one note.** For example:

| Whistle | Note number | Nearest note | Cents |
|---------|-------------|--------------|-------|
| 440 Hz | 69.00 | A4 | 0 |
| 880 Hz | 81.00 | A5 | 0 |
| 1,000 Hz | 83.21 | B5 | +21 (sharp) |

## Walking Through the Code

### Taking a frame

```python
def read_frame():
    mic.readinto(buf)
    return [s >> config.MIC_SAMPLE_SHIFT
            for s in struct.unpack("<%di" % FRAME, buf)]
```

A frame here is **1,024 samples**, which is 80 ms. That is long enough to hold many cycles of a
whistle, so the counting is accurate.

### The pitch function

```python
def pitch(samples, floor):
    offset = sum(samples) // len(samples)
    if loudness(samples, offset) < floor * GATE:
        return None, 0                     # too quiet: the noise gate
    peak = max(abs(s - offset) for s in samples)
    level = int(peak * HYSTERESIS)
    low = offset - level
    high = offset + level
    armed = False
    first = last = None
    crossings = 0
    for i in range(len(samples)):
        s = samples[i]
        if s < low:
            armed = True
        elif s > high and armed:           # low, then high: one upward crossing
            armed = False
            crossings += 1
            if first is None:
                first = i
            last = i
    if crossings < 3:
        return None, peak
    return (crossings - 1) * RATE / (last - first), peak
```

The function returns **`None`** when it cannot tell the pitch: when the frame is too quiet, or when it found fewer than 3
crossings. Read the loop slowly:

1. If the sample drops **below `low`**, the detector is **armed**.
2. If it then rises **above `high`** *and* is armed, that is a real upward crossing. Count it and
   disarm.
3. Remember the **first** and **last** crossing positions.

Small wiggles between `low` and `high` do **nothing**. That is the hysteresis.

### From frequency to note

```python
def note_of(frequency):
    number = 69 + 12 * math.log(frequency / 440) / math.log(2)
    nearest = round(number)
    cents = round((number - nearest) * 100)
    name = NOTE_NAMES[nearest % 12] + str(nearest // 12 - 1)
    return name, cents
```

Python's `math.log` is the natural log, so dividing by `math.log(2)` gives log base 2. The note
**name** comes from the position in the 12-name list (`nearest % 12`), and the **octave**
number from `nearest // 12 - 1`. Note number 69: 69 % 12 = 9, which is `"A"`, and
69 // 12 - 1 = 4, so it is **A4**.

### The needle

```python
x = CX + cents * (BAR_W // 2) // 50
color = config.GREEN if abs(cents) <= 5 else (
    config.YELLOW if abs(cents) <= 20 else config.RED)
display.fill_rect(x - 3, BAR_Y, 7, BAR_H, color)
```

The bar is 240 pixels wide, with the middle at 0 cents and the edges at -50 and +50. The marker
moves 2.4 pixels for each cent. It is **green** within 5 cents of the note, **yellow** within
20, and **red** beyond that.

### Only redraw when something changes

When the room goes quiet, `pitch()` returns `None`, and the screen shows `--`. The `shown`
variable remembers whether the screen is already showing `--`, so it is only redrawn once. The
send-only-what-changed idea from Lab 10 appears again.

## Run It

Open `17-whistle-tuner.py` and press Run. When the screen says **quiet please...**, stay silent
for one second. Then whistle a steady note.

!!! mascot-tip "Whistle Like a Pro"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    A whistle is almost a pure sine wave, which is exactly what this method likes, so purse your lips and blow gently and steadily. Humming "ooo" works too, but a voice has many waves at once and the reading will jump around.

## What PASS Looks Like

* The big number shows a steady frequency in hertz, usually between **500 and 3,000 Hz** for a
  whistle.
* Below it, a note name such as **B5** in cyan.
* The needle moves **left** when you whistle flat, and **right** when you whistle sharp, and turns
  green when you are in tune.
* When you stop, the screen returns to `--`.
* The shell prints each reading, for example `1000.3 Hz  B5  +21 cents  (peak ...)`.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| Always `--` | Gate too strict, or the mic is not working | Whistle louder; check [Lab 06](06-listen-meter.md); lower `GATE` to 3 |
| The reading jumps all over | Noise causing false crossings | Raise `HYSTERESIS` to 0.4 |
| It shows a wrong note when you hum | A voice has many waves at once | Use a whistle; the FFT in Chapter 9 handles voices |
| The room was noisy at start-up | Floor too high | Stop and run it again, quietly |

## Try This

1. **Hold it steady.** Whistle the same note and watch the cents. How steady can you hold it?
   Professional singers stay within about 10 cents.
2. **No hysteresis.** Set `HYSTERESIS` to `0`. Whistle softly. What happens to the reading,
   and why?
3. **Compare with a phone.** Play a note from a phone tuner app next to the microphone (try A4,
   440 Hz). How close does this tuner get?
4. **Play a tune.** Whistle a scale (C, D, E, F, G). Do the note names step upward as you
   expect?
5. **Octave jump.** Whistle a note and then the same note an octave higher. By what factor does
   the frequency change?

??? tip "Hint for number 2"
    With no hysteresis, `low` and `high` both equal the middle line, so *any* wiggle of noise
    across it counts as a crossing. A soft whistle is close to the noise level, so the program
    counts far too many crossings and reports a frequency that is too high.

## Check Your Understanding

1. Why does the formula use `crossings - 1`?
2. What problem does hysteresis solve?
3. What note number is 880 Hz? What is its name?
4. If your whistle measures 450 Hz, are you sharp or flat compared to A4?

??? question "Answers"
    1. `n` crossings mark only `n - 1` complete cycles between them.
    2. Noise near the middle line can cross it many times, causing false crossings. Hysteresis
       requires the signal to go clearly low and then clearly high.
    3. 69 + 12 x log2(2) = 81, which is A5.
    4. Sharp. 450 Hz is above 440 Hz, by about 39 cents.

!!! mascot-celebration "You Built a Tuner"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You counted zero crossings with hysteresis, gated out the room's noise, and turned a frequency into a note name and cents using a logarithm. That is real signal processing, running on a board the size of your thumb.

## Where Next

The tuner works well for whistles but struggles with voices. Chapter 9 of this book shows how the
**FFT** solves that. First, [Lab 18](18-network-layers.md) turns outward: how your Study Buddy
reaches the internet.

*Related in this book:* [Chapter 9: Signal Processing and the FFT](../../chapters/09-signal-processing-fft/index.md)
