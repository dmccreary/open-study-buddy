---
title: "Lab 05: Speaker Tones"
description: "Play a beep, a musical scale, and three volume levels through the MAX98357A amplifier and speaker, building every sound from a list of numbers and sending it over I2S."
---

# Lab 05: Speaker Tones

!!! mascot-welcome "Give Your Buddy a Voice"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Today your Study Buddy learns to make sound, starting with a plain beep and ending with a scale you can sing along to. The Pico cannot hear whether this works, so you are the test equipment. Let's listen closely!

| | |
|---|---|
| **Program** | `05-speaker-tones.py` |
| **Parts needed** | The MAX98357A amplifier and the speaker |
| **Time** | 15 minutes |
| **Makes sound?** | **Yes.** Keep the speaker a little away from your ear. |
| **How to stop** | The program ends by itself after about 6 seconds |

## What You Will Learn

* How the Pico turns a **list of numbers** into sound
* What **I2S** is and which pins carry it
* How to build a sine wave with `math.sin`
* Why a short **fade** at each end of a note stops it from clicking
* What a **decibel** step is, and why doubling the numbers does not sound twice as loud

## Wiring

| Amplifier pin | Pico pin | What it does |
|---------------|----------|--------------|
| BCLK | GP9 | The "bit clock": one tick for every bit of audio |
| LRC | GP10 | The "left/right clock": says which channel a sample belongs to |
| DIN | GP11 | The audio data itself |
| GAIN | GP12 | Chooses how loud the amplifier makes the signal |
| VIN | 5 V (VBUS) or 3V3 | Power |
| GND | GND | Ground |

Connect the speaker to the amplifier's two output terminals (+ and -).

!!! mascot-warning "The I2S Pin Rule"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    MicroPython's I2S on the Pico needs LRC on the pin **right after** BCLK, which is why this kit uses GP9 and GP10. If you swap them, `I2S()` raises an error, and the fix is to put LRC back on the next pin up from BCLK.

## The Big Idea

A speaker makes sound by moving a cone in and out. The Pico cannot move the cone smoothly. It
sends a **list of numbers**, and each number says where the cone should be at one instant.
Played fast enough, the numbers make a smooth wave. Each number is called a **sample**.

This lab sends **16,000 samples every second** (the *sample rate*). Each sample is a 16-bit
number from -32768 to 32767. Positive pushes the cone out, negative pulls it in, and zero is
the middle. The shape of the list decides the sound, and the *speed* of the wiggle decides the
pitch:

| Frequency | Musical meaning |
|-----------|-----------------|
| 220 Hz | A3 |
| 440 Hz | A4, the "tuning A" |
| 880 Hz | A5, one octave above |

Every time the frequency **doubles**, the note goes up one **octave**.

### What is I2S?

**I2S** (Inter-IC Sound) is a way for chips to send digital audio over three wires. It is like
SPI, but made for sound:

| I2S wire | Job |
|----------|-----|
| Bit clock (BCLK) | Ticks once for every bit |
| Word select (LRC) | Flips between left and right channel |
| Data (DIN) | The bits of each sample |

The amplifier receives the samples, converts them into a smooth voltage, and boosts that
voltage enough to drive the speaker. You do not need a DAC or any resistors.

## Walking Through the Code

### Making a note

```python
def make_tone(freq, ms, volume=config.VOLUME):
    count = RATE * ms // 1000
    amplitude = 32767 * volume / 100
    out = bytearray(count * 2)
    for i in range(count):
        fade = min(1.0, i / FADE, (count - i) / FADE)
        value = int(amplitude * fade * math.sin(2 * math.pi * freq * i / RATE))
        struct.pack_into("<h", out, i * 2, value)
    return out
```

Take it one line at a time:

* `count = RATE * ms // 1000` is how many samples a note of `ms` milliseconds needs. For an
  800 ms beep: 16000 x 800 / 1000 = **12,800 samples**.
* `amplitude` is the biggest value the wave will reach. At 100% volume it is 32767. The kit's
  `VOLUME` setting is 40, so the amplitude is about 13,000.
* `bytearray(count * 2)` makes room for the samples. Each sample is **2 bytes** (16 bits).
* `math.sin(2 * math.pi * freq * i / RATE)` is the heart of it. For sample number `i`, the time
  is `i / RATE` seconds. A wave of `freq` cycles per second has traveled `freq * time` cycles
  by then, and a full cycle is `2 * pi` radians. The sine of that angle is a number between -1
  and 1.
* `fade` smoothly goes from 0 up to 1 over the first 10 ms and back to 0 over the last 10 ms.
  Without it, a note that starts or stops in the middle of a wave makes the cone jump, and you
  hear a **click**.
* `struct.pack_into("<h", out, i * 2, value)` writes the number into the array as a 16-bit
  signed integer (`h`), least significant byte first (`<`).

!!! mascot-thinking "A Sound Is Just a List"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    There is no "sound" object anywhere in this program, only a list of numbers made by a formula. Change the formula and you change the sound, which is why every later audio lab in this kit is a new way of filling a list.

### Starting I2S

```python
config.set_gain()
audio = I2S(config.I2S_SPEAKER_ID,
            sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
            sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
            format=I2S.MONO, rate=RATE, ibuf=IBUF)
```

* `set_gain()` sets the amplifier's loudness (9 dB by default).
* `mode=I2S.TX` means "transmit" (the Pico sends sound out).
* `bits=16` and `format=I2S.MONO` say each sample is 16 bits and there is one channel.
* `ibuf=8192` is the size of a buffer that holds up to 8192 bytes, which is **256 ms** of
  sound at this sample rate. The Pico fills the buffer, and I2S empties it at exactly the right
  speed.

### Playing the sound

```python
audio.write(make_tone(440, 800))
audio.write(silence(300))
```

`audio.write()` hands the samples to the buffer. When the buffer is full, `write` waits until
there is room. The program ends with a short sleep and `audio.deinit()`, so the last bytes
finish playing before the speaker is released.

### Part 2: the scale

The scale is eight notes, C4 up to C5. The program **builds every note first**, and then plays
them. If it built each note right before playing it, the speaker would run out of numbers while
the Pico was busy calculating, and you would hear gaps.

| Note | C4 | D4 | E4 | F4 | G4 | A4 | B4 | C5 |
|------|----|----|----|----|----|----|----|----|
| Hz | 262 | 294 | 330 | 349 | 392 | 440 | 494 | 523 |

Notice that C5 (523 Hz) is almost exactly double C4 (262 Hz): an octave.

### Part 3: three volumes

```python
for percent in (10, 30, 100):
    level = config.VOLUME * percent // 100
    audio.write(make_tone(440, 400, level) + silence(125))
```

The program plays the same note at 10%, 30%, and 100% of `VOLUME`. Each step is about
**10 decibels** louder, which is the step your ears hear as "twice as loud". Doubling the
numbers (25%, 50%, 100%) is only 6 dB per step, and on a small speaker that sounds almost the
same.

## Run It

Open `05-speaker-tones.py` in Thonny and press Run. Keep the speaker at arm's length: a speaker
an inch from your ear is much louder than you expect.

## What PASS Looks Like

You hear three things in order:

1. A steady beep (A4, 440 Hz)
2. A rising scale of eight notes
3. Three beeps that get louder each time

The shell prints each note name and frequency as it plays, and ends with
`Done. Did you hear all three parts?`

## If Something Goes Wrong

| What you hear or see | Likely cause | Fix |
|----------------------|--------------|-----|
| Silence | Amplifier power or speaker wires | Check VIN, GND, and the speaker + and - terminals |
| Silence, but no error | Signal wires | Check BCLK (GP9), LRC (GP10), DIN (GP11) |
| `ValueError` from `I2S()` | LRC is not right after BCLK | Check the pins in `config.py` |
| Buzzing or crackling at full volume | The speaker is running out of room to move | Lower `VOLUME` in `config.py` |
| A quiet hiss | Normal at low volume | Ignore it; it is the amplifier |

## Try This

1. **Octaves.** Change `440` in part 1 to `220`, then to `880`. What happens to the pitch each
   time you double the frequency?
2. **Your own song.** Write a list of `(name, frequency)` pairs and play them the way part 2
   does. "Twinkle, Twinkle, Little Star" starts C C G G A A G.
3. **More gain.** Change `GAIN_DB` from `9` to `12` in `config.py`, upload it, and run again.
   How much louder is it? Start with a low `VOLUME`.
4. **A siren.** Play 600 Hz for 300 ms, then 900 Hz for 300 ms, and repeat. How does it sound?

??? tip "Hint for number 2"
    Use a dictionary to look up frequencies by name: `{"C": 262, "D": 294, "E": 330, "F": 349,
    "G": 392, "A": 440}`. Then a song is a string like `"CCGGAAG"`, and you loop over the
    letters. Dictionaries are in the
    [Collections](https://dmccreary.github.io/learning-micropython/chapters/02-control-flow-functions/)
    chapter of the course.

## Check Your Understanding

1. How many samples are in a 250 ms note at a 16,000 Hz sample rate?
2. Why does each note start and end with a 10 ms fade?
3. What is the frequency of the note one octave above 330 Hz?

??? question "Answers"
    1. 16000 x 250 / 1000 = 4,000 samples.
    2. To keep the cone from jumping at the start and end of the note, which would make a click.
    3. 660 Hz. An octave up doubles the frequency.

## Where Next

You can now hear what you build. [Lab 06](06-listen-meter.md) goes the other direction: the
Pico *listens*.

*Review in the course:* [Sound, Music, and Audio](https://dmccreary.github.io/learning-micropython/chapters/18-sound-music-audio/),
including the [play a scale lab](https://dmccreary.github.io/learning-micropython/hands-on-labs/18-sound-music-audio/04-play-scale/)
and the [I2S standard lab](https://dmccreary.github.io/learning-micropython/hands-on-labs/18-sound-music-audio/08-i2s-standard/).
