---
title: "Lab 07: Hold to Record, Release to Play Back"
description: "Hold the MODE button to record your voice into memory, then let go to hear it played back, using every part of the kit at once: button, microphone, speaker, and display."
---

# Lab 07: Hold to Record, Release to Play Back

!!! mascot-welcome "Your First Voice Recorder"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Hold a button, say something, let go, and hear your own voice come out of a gadget that you wired yourself. This is the first lab that uses every part in the kit at the same time. Let's listen closely!

| | |
|---|---|
| **Program** | `07-record-playback.py` |
| **Parts needed** | MODE button, microphone, amplifier and speaker, display |
| **Time** | 20 minutes |
| **Makes sound?** | **Yes**, it plays your voice back |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## Before You Start

If this lab fails, one of the earlier tests will tell you which part is broken, so run
Labs 03, 04, 05, and 06 first. That is the whole reason those tests exist.

## What You Will Learn

* How to **record** into a big block of memory, and why you convert it *later*
* What a **memoryview** is, and why it avoids making copies
* How to convert 32-bit samples to 16-bit samples **in place**
* What the microphone's **DC offset** is, and how to remove it
* Why the recording and playback **sample rates must match**

## The Big Idea

Recording is easy to describe: copy the microphone's numbers into memory while the button is
down. Playback is the reverse: send the numbers to the speaker. Two problems make it harder
than it sounds, and both are the lessons of this lab.

**Problem 1: Python is too slow to do math on every sample while recording.** The microphone
sends 12,800 samples a second, and the Pico must grab each one right away. So the program does
**no math** while recording. It just stores the raw bytes. The math happens *after* you let go.

**Problem 2: the microphone and the speaker speak different "sizes".** The microphone sends
32-bit samples (with 24 real bits inside). The amplifier wants 16-bit samples. The program
converts the whole recording after the button is released.

!!! mascot-thinking "Do the Slow Work Later"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    When a job has a deadline you cannot miss, such as catching every microphone sample, do only the bare minimum during the deadline and finish the rest afterward. Professional audio programs use the same trick.

## Walking Through the Code

### One big buffer

```python
MAX_SECONDS = 3
raw = bytearray(MAX_SECONDS * RATE * 4)    # 3 s of 32-bit samples, 150 KB
view = memoryview(raw)
```

The buffer holds 3 seconds x 12,800 samples x 4 bytes = **153,600 bytes**. That is a big piece
of the Pico's memory, which is why [Lab 02](02-probe.md) checked whether it would fit.

A **memoryview** is a window onto the same bytes. When you slice a `bytearray`, Python makes a
*copy*. When you slice a `memoryview`, it does not. Slicing without copying is important when
every byte counts.

### Recording while the button is held

```python
while position < len(raw) and button.value() == 0:
    got = mic.readinto(view[position:position + CHUNK])
    if skip > 0:                   # throw away the start-up sound
        skip -= got
        continue
    position += got
    width = BAR_WIDTH * position // len(raw)
    if width > drawn:              # grow the red bar
        display.fill_rect(BAR_X + drawn, BAR_Y, width - drawn, 14, config.RED)
        drawn = width
```

Read the loop condition aloud: "*keep going while there is still room in the buffer, and
MODE is held down.*" Each pass reads one chunk of 1,024 bytes (256 samples, 20 ms) straight
into the next open part of the buffer. The first 100 ms are skipped, because a microphone's
first moments are start-up clicks and not real sound.

While it records, a **red bar** grows across the screen so you can see how much of the three
seconds you have used. Notice that the bar only draws the *new* part (`width - drawn`), the same
"send only what changed" trick from [Lab 10](10-flicker-free-text.md).

The `try ... finally` around the loop makes sure `mic.deinit()` always runs. That releases the
microphone's I2S block so it can be used again for the next recording.

### Converting in place

```python
def convert(count):
    # Pass 1: find the DC offset
    total = 0
    for start in range(0, count, BLOCK):
        n = min(BLOCK, count - start)
        total += sum(s >> SHIFT for s in
                     struct.unpack_from("<%di" % n, raw, start * 4))
    offset = total // count

    # Pass 2: remove it, apply the gain, write 16-bit samples
    for start in range(0, count, BLOCK):
        n = min(BLOCK, count - start)
        samples = struct.unpack_from("<%di" % n, raw, start * 4)
        louder = [max(-32768, min(32767, ((s >> SHIFT) - offset) * PLAYBACK_GAIN >> 8))
                  for s in samples]
        struct.pack_into("<%dh" % n, raw, start * 2, *louder)
    return offset
```

This function is the most advanced code in the book so far, so take it slowly.

**Pass 1** adds up every sample (256 at a time, called a *block*) and divides by the count to
find the average. That average is the **DC offset**, the constant the microphone adds to
everything. It measured about 15,000 on this kit.

**Pass 2** goes through the samples again. For each one it:

1. Shifts right by 8 to recover the real 24-bit value (`s >> SHIFT`)
2. Subtracts the offset, so silence becomes zero
3. Multiplies by `PLAYBACK_GAIN` (8) to make it louder, and shifts right by 8 to squeeze it
   into 16 bits
4. **Clamps** it with `max(-32768, min(32767, ...))` so it can never go outside the 16-bit
   range, because an out-of-range value would wrap around and make a loud crackle

!!! mascot-tip "The Clamp Trick"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    To force a number `x` into a range, write `max(low, min(high, x))`. Remember it as "cap the top with `min`, lift the bottom with `max`", and use it any time a calculation might overshoot.

Why "in place"? Each 16-bit result takes **half** the space of its 32-bit original. So the
output for block `start` is written at byte `start * 2`, always behind the place where the next
input is read at byte `start * 4`. The output never overwrites a sample that has not been read
yet. That means the program does not need a second 150 KB buffer, and a Pico has little
memory to spare.

### Playing back

```python
audio = I2S(config.I2S_SPEAKER_ID, ..., mode=I2S.TX, bits=16,
            format=I2S.MONO, rate=RATE, ibuf=IBUF)
audio.write(view[:count * 2])
```

The speaker is started with `rate=RATE`, the **same** 12,800 Hz the microphone used. This is
important. If you recorded at one speed and played back at another, your voice would sound like
a chipmunk or a monster.

## Run It

Open `07-record-playback.py`, press Run, then **hold MODE** and say something. Let go to hear it.

## What PASS Looks Like

1. The screen says **Hold MODE**.
2. While you hold the button, the screen says **RECORDING** and a red bar grows. The onboard
   LED is lit.
3. When you let go, the screen says **Playing** and you hear your voice.
4. The shell prints something like `Recorded 1.50 s (19200 samples)` and the offset it found.
5. It goes back to **Hold MODE** so you can do it again.

A tap shorter than 0.2 seconds shows **Too short**, because it is a bump and not a recording.

## If Something Goes Wrong

| What you hear or see | Likely cause | Fix |
|----------------------|--------------|-----|
| Playback is silent | The recording was too quiet | Talk closer to the microphone, or raise `PLAYBACK_GAIN` |
| Playback crackles | The recording is too loud | Lower `PLAYBACK_GAIN` or `VOLUME` |
| Your voice sounds like a chipmunk or a monster | The two sample rates do not match | Both come from `MIC_SAMPLE_RATE` in `config.py` |
| `MemoryError` | The 3-second buffer does not fit | Run [Lab 02](02-probe.md); lower `MAX_SECONDS` |
| "Too short" every time | You are tapping, not holding | Hold the button the whole time you talk |

## Try This

1. **Gain experiment.** Change `PLAYBACK_GAIN` to 2, then to 24. Where does it get too quiet, or
   too crackly? What is happening to the numbers when it crackles?
2. **Longer recordings.** Change `MAX_SECONDS` to 5. Does the buffer still fit in RAM? Run
   Lab 02 to see how much memory is left.
3. **Half speed.** In `play()`, change `rate=RATE` to `rate=RATE // 2`. Is your voice higher or
   lower? Why?
4. **Double speed.** Try `rate=RATE * 2`. What changes about how long it takes?

??? tip "Hint for number 3"
    Playing the same samples more slowly stretches every wave, so each wave takes longer. Longer waves are lower in pitch, which makes your voice deep and slow. Playing faster does the reverse and gives a chipmunk. The recording is exactly the same numbers either way.

## Check Your Understanding

1. Why does the program do no math on the samples while it is recording?
2. How many bytes would a 2-second recording use?
3. What does `max(-32768, min(32767, x))` do?
4. What would you hear if you played the recording back at 25,600 Hz instead of 12,800 Hz?

??? question "Answers"
    1. Python is too slow to convert samples and still keep up with 12,800 samples a second.
       The program stores the raw bytes now and does the math after the button is released.
    2. 2 x 12,800 x 4 = 102,400 bytes.
    3. It forces `x` into the range of a 16-bit sample, so it can never overflow.
    4. Your voice would play twice as fast, one octave higher, and take half as long.

!!! mascot-celebration "A Real Voice Recorder"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just recorded sound into memory with a `memoryview`, removed a DC offset, converted 32-bit samples to 16-bit in place, and played them back, all on a board with less memory than a single photo. Every part in your kit now works.

## Where Next

You have finished the **Does it work?** labs. Labs 08 to 18 start from scratch and explain *how*
each part works, one idea per lab. [Lab 08](08-color-mixing.md) begins with the most colorful
idea of all.

*Review in the course:* [the audio chapter](https://dmccreary.github.io/learning-micropython/chapters/18-sound-music-audio/)
