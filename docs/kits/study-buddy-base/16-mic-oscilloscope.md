---
title: "Lab 16: A Microphone Oscilloscope"
description: "Draw the sound the INMP441 microphone hears as a wave across the round display, 25 times a second, and learn DC offset, gain, and triggering."
---

# Lab 16: A Microphone Oscilloscope

!!! mascot-welcome "See Your Own Voice"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Engineers use a machine called an oscilloscope to see electrical signals as moving waves. In this lab your Study Buddy becomes one, and you get to watch your own humming, whistling, and "ahhh" become a picture. Let's listen closely, and look too!

| | |
|---|---|
| **Program** | `16-mic-oscilloscope.py` |
| **Parts needed** | The microphone, the display, and the buttons |
| **Time** | 25 minutes |
| **Makes sound?** | No |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* What a **microphone sample** is
* What a **DC offset** is and how to remove it
* How **gain** (zoom) scales a wave to fit the screen
* How a **trigger** makes a steady note hold still

## The Big Idea

The INMP441 microphone measures the air pressure on its tiny membrane **12,800 times a second**
and sends each measurement as a number. If you plot those numbers left to right, you see the
**sound wave itself**. Three ideas make the picture useful.

### 1. DC offset

Silence is **not** zero. This microphone adds a constant (around 15,000) to everything it
sends. If you drew the raw numbers, even a quiet room would sit far from the middle of the
screen. Subtracting the **average** of each frame puts silence back on the middle line.

### 2. Gain

Speech is small numbers next to the full 24-bit range. To see it, the picture is scaled up. **UP**
and **DOWN** zoom in and out, doubling or halving the **gain**.

### 3. Trigger

Each frame starts at a **random point** in the wave, so a steady hum would jump around from
frame to frame and look like a blur. A **trigger** waits for the wave to cross the middle line
**going up**, and starts drawing there. So every frame of a steady note begins at the same
place in its cycle, and the picture **holds still**. **MODE** turns the trigger on and off, so
you can compare.

!!! mascot-thinking "Why the Trigger Works"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A steady note is the same shape repeating, so if every drawing starts at the same point of that shape, every drawing looks identical, like a flip-book where each page shows the same moment. Without the trigger, each page starts at a different moment and the picture shimmers.

## Walking Through the Code

### The settings

```python
RATE = config.MIC_SAMPLE_RATE           # 12800 samples a second
FRAME = 512                             # 40 ms
SHOWN = 256                             # samples drawn: 20 ms of sound
PLOT_X, PLOT_W = 52, 256                # one sample per pixel
PLOT_MID, PLOT_HALF = 180, 80
```

Each frame reads 512 samples (40 ms), but the screen shows only 256 of them: **one sample per
pixel**, which is 20 ms of sound. The grid has vertical lines every 64 pixels, and 64 samples is 64 / 12,800 = **5 ms**. So each square is 5 ms wide.

### A small buffer on purpose

```python
mic = I2S(config.MIC_I2S_ID, ..., mode=I2S.RX, bits=32, format=I2S.MONO,
          rate=RATE, ibuf=4096)
```

`ibuf=4096` holds only 80 ms of sound, much smaller than the big buffer in
`config.init_microphone()`. Drawing is slower than the sound arrives. A big buffer would let the
picture fall further and further **behind** what you are doing, like a delayed video call. A
small buffer can only hold the last 80 ms, so what you see is what you just did.

### Samples, offset, and peak

```python
mic.readinto(buf)
samples = [s >> config.MIC_SAMPLE_SHIFT
           for s in struct.unpack("<%di" % FRAME, buf)]
offset = sum(samples) // FRAME              # the DC offset
peak = max(abs(s - offset) for s in samples)
```

As in Lab 06, the shift by 8 recovers the real 24-bit audio. `offset` is the average of the
frame, the DC offset. `peak` is the biggest distance from the middle, which is shown in
yellow on the screen. Quiet room: a small peak. Loud sound: a big one.

### The trigger

```python
start = 0
if trigger:
    for i in range(1, FRAME - SHOWN):
        if samples[i - 1] < offset <= samples[i]:
            start = i
            break
```

The loop looks for the first place where the previous sample was **below** the middle line
(`offset`) and this one is **at or above** it. That is an **upward crossing**. The drawing then starts
at `start` instead of 0. It stops looking early enough (`FRAME - SHOWN`) that there are always
256 samples left to draw.

### Drawing the wave

```python
value = (samples[start + x] - offset) * scale // 65536
y = PLOT_MID - max(-PLOT_HALF, min(PLOT_HALF - 1, value))
```

For each pixel column `x`, the sample minus the offset is scaled by `zoom * PLOT_HALF`, and then divided by
65,536 to bring a 24-bit number down to screen size. The clamp keeps the trace inside the plot box. The `PLOT_MID - ...`
flips it, because on screen `y` grows downward, as in Labs 04 and 09.

Each column is drawn as a **vertical line** from the previous point to this one, so the wave
stays joined up even where it is steep:

```python
display.vline(PLOT_X + x, top, max(previous_old, old[x]) - top + 1, config.BLACK)   # erase the old
display.vline(PLOT_X + x, top, max(previous_new, y) - top + 1, TRACE)               # draw the new
```

The list `old` remembers the `y` of every column from the last frame so the old trace can be
erased, the "erase the old hand" trick from Lab 09. Every 8 frames, the grid is redrawn to
repair the lines that erasing cut.

### Updating the text

The `offset` and `peak` numbers, and the zoom and trigger status, are redrawn only every 5th frame. That
keeps the text from slowing down the wave.

## Run It

Open `16-mic-oscilloscope.py` and press Run. Hum, whistle, say "ahhh", and clap.

## What PASS Looks Like

* A **flat line** in the middle when it is quiet
* A wave that **grows** when you make a sound
* A steady hum or whistle **holds still** while the trigger is on, and drifts across the
  screen when it is off
* The `offset` number stays around 15,000, and `peak` changes with how loud you are

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| Flat line, `peak` stays 0 | Microphone wiring | Check [Lab 02](02-probe.md), section 8 |
| The wave is clipped (flat on top) | Zoom too high | Press DOWN to halve the gain |
| The wave is too tiny to see | Zoom too low | Press UP to double the gain |
| The picture shimmers | Trigger is off | Press MODE to turn it on |
| The picture lags behind your sound | Buffer too big | Keep `ibuf=4096` |

## Try This

1. **Measure a whistle.** Whistle as steady a note as you can and count the waves in one 5 ms
   square. 5 waves in 5 ms is 1,000 waves a second: 1,000 Hz. What pitch is your whistle?
2. **Lose the offset.** Remove `- offset` from the `value` line. Where does the trace go?
3. **"sss" versus "ooo".** Say "sss" and then "ooo". Which one looks like a smooth wave and
   which looks like noise? Which is easier for a computer to recognize?
4. **Draw the middle.** Add a bright line at `PLOT_MID` so you can see where zero is.

??? tip "Hint for number 1"
    The frequency is *waves per square* divided by *seconds per square*. If you count 3 waves
    in one 5 ms square, it is 3 / 0.005 = 600 Hz. A typical whistle lands between about 500
    and 3,000 Hz.

??? tip "Hint for number 3"
    "ooo" is a voiced, repeating sound, so it makes a clear wave with a pitch. "sss" is hiss, a
    random-looking noise with no pattern. Computers find patterns in the voiced sounds much more
    easily, which is why Lab 17 works with a whistle.

## Check Your Understanding

1. What is the DC offset, and how does the program remove it?
2. Why does a steady hum look steadier with the trigger on?
3. How wide, in milliseconds, is each grid square?
4. Why does this program use a smaller `ibuf` than `config.init_microphone()`?

??? question "Answers"
    1. A constant the microphone adds to every sample. The program subtracts the frame's average.
    2. The trigger starts every frame at the same point in the wave's cycle, so each
       drawing looks the same.
    3. 64 samples / 12,800 samples per second = 5 ms.
    4. A small buffer only holds 80 ms of sound, so what you draw is never much older than
       that. A big buffer could hold nearly a second, and the picture would lag behind you.

## Where Next

You can see sound. [Lab 17](17-whistle-tuner.md) goes one step further and measures how high a
whistle is, in hertz, as a musical note.

*Related in this book:* the [I2S Signal Reader](../../sims/i2s-signal-reader/index.md) MicroSim
and [Chapter 8: I2S Audio](../../chapters/08-i2s-audio/index.md).
