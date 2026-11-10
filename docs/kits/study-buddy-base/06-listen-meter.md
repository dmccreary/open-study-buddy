---
title: "Lab 06: Listen with the Microphone"
description: "Read the INMP441 microphone, measure how loud the room is as a number of bits, calibrate a noise floor, and show a moving level meter on the round display."
---

# Lab 06: Listen with the Microphone

!!! mascot-welcome "Your Buddy Learns to Listen"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Now your Study Buddy hears you, at least well enough to tell when you speak up. This lab is the first time sound travels from the air into your Pico and onto the screen. Let's listen closely!

| | |
|---|---|
| **Program** | `06-listen-meter.py` |
| **Parts needed** | The display and the INMP441 microphone |
| **Time** | 15 minutes |
| **Makes sound?** | No |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* How the microphone's samples reach the Pico over I2S
* How to measure loudness from a block of samples
* Why a **noise floor** needs to be measured instead of guessed
* Why loudness is shown on a **logarithmic** scale (in "bits")

## Wiring

| Microphone pin | Pico pin | What it does |
|----------------|----------|--------------|
| SCK | GP13 | Serial clock from the Pico |
| WS | GP14 | Word select |
| SD | GP15 | Serial data, microphone to Pico |
| L/R | GND | Chooses the left channel |
| VDD | **3V3** | Power. **Never 5 V.** |
| GND | GND | Ground |

Plus the display wiring from [Lab 04](04-hello-world.md).

!!! mascot-warning "Three Wires Everyone Swaps"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A swapped microphone starts without any error and sends only zeros, so the meter never moves. If that happens, check in this order: SCK on GP13, WS on GP14, SD on GP15, then VDD on 3V3, and finally GND and L/R both on GND.

## The Big Idea

The microphone measures air pressure **12,800 times a second** and sends each measurement to
the Pico as a number. To turn a stream of numbers into "how loud is it?", the program does three
things:

1. **Collect a frame.** A frame is 512 samples, which is 512 / 12,800 = **40 milliseconds**
   of sound.
2. **Find the average distance from the middle.** Quiet sound stays close to the middle value;
   loud sound swings far from it.
3. **Take log base 2.** This turns the huge range of loudness into a small number of "bits",
   which is how ears hear it too: every doubling of loudness sounds like one equal step.

The result is a loudness number, in bits, roughly between 9 (a quiet room) and 21 (shouting
right at the microphone).

!!! mascot-thinking "Why Logarithms?"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A whisper and a shout can differ by a factor of a thousand in raw numbers, so a straight meter would show the whisper as nothing. Taking the log base 2 asks "how many times did the loudness double?", and that spreads quiet and loud sounds across the whole meter.

## Walking Through the Code

### Turning a frame into loudness

```python
def loudness_bits(buf):
    samples = [s >> config.MIC_SAMPLE_SHIFT
               for s in struct.unpack(FRAME_FORMAT, buf)]
    middle = sum(samples) // FRAME_SAMPLES        # the microphone's DC offset
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2
```

This one small function does a lot:

* **`struct.unpack("<512i", buf)`** converts 2,048 raw bytes into 512 whole numbers. Each is a
  32-bit signed integer (`i`).
* **`s >> 8`** shifts each number right by 8 bits. The INMP441 sends 24 bits of real audio
  tucked into the top of a 32-bit word, so dropping the bottom 8 bits recovers the real value.
* **`middle`** is the average of all the samples. The microphone adds a constant (the **DC
  offset**) to everything it sends, so silence is not zero. Subtracting `middle` puts
  silence back at zero. You will see the offset with your own eyes in [Lab 16](16-mic-oscilloscope.md).
* **`abs(s - middle)`** is each sample's distance from the middle. The program averages them.
* **`math.log(average + 1) / LOG2`** is log base 2. The `+ 1` is there because the log of 0 does
  not exist, and a perfectly quiet frame could average 0.

### Learning the room's noise floor

```python
for _ in range(8):                     # skip the microphone's start-up
    mic.readinto(buf)
total = 0
for _ in range(CALIBRATE_FRAMES):
    mic.readinto(buf)
    total += loudness_bits(buf)
floor = total / CALIBRATE_FRAMES
```

No room is perfectly silent. A classroom has a hum, and a bedroom has a fan. For the first
second the program listens and averages 25 frames to learn how loud **this** room is when
nothing is happening. That is the **noise floor**. Then "loud" means *louder than the floor by
2 bits* (`SPEECH_ABOVE_FLOOR = 2.0`), which is four times the loudness, and it works equally
well in a quiet library or a noisy kitchen.

The first 8 reads are thrown away because a microphone's first moments are not real sound:
they are start-up clicks.

### Drawing the meter

```python
width = int(METER_WIDTH * meter_fraction(bits))
if abs(width - drawn_width) >= 2:
    ...
    display.fill_rect(METER_X, METER_Y, width, METER_HEIGHT, color)
    display.fill_rect(METER_X + width, METER_Y,
                      METER_WIDTH - width, METER_HEIGHT, TRACK)
    drawn_width = width
```

`meter_fraction()` turns the loudness in bits into a number from 0.0 to 1.0, where 9 bits is
the bottom of the meter and 21 bits is the top. Then the width is that fraction of 200 pixels.
The meter is drawn in two pieces: a colored bar for the loud part, and a dark "track" for the
rest, so there is no need to erase it first. The color is green below half, yellow up to 80%,
and red above that.

Notice `abs(width - drawn_width) >= 2`. The program only redraws the meter when the bar would
change by at least 2 pixels. Sending fewer pixels to the screen makes the program faster.
You will study this idea in [Lab 10](10-flicker-free-text.md).

### Updating the text only when it changes

```python
is_loud = bits > floor + SPEECH_ABOVE_FLOOR
if is_loud != heard:
    heard = is_loud
    ...
```

The status line only changes when `is_loud` flips between `True` and `False`, so the screen
does not flicker with the same words over and over.

## Run It

Open `06-listen-meter.py` and press Run. When it says **Quiet please...**, stay silent for one
second. When it says **Listening...**, talk, clap, or tap near the microphone.

## What PASS Looks Like

* The screen shows **Say 'Hey Pico'** and an empty meter.
* After the one-second calibration, the shell prints the noise floor. About 12 bits is typical for
  a quiet room.
* The meter bounces when you talk, and sits low when the room is quiet.
* **I hear you!** appears in green when you speak up, and goes back to **Listening...** when you
  stop.
* The shell prints a line with a row of `#` characters every 200 ms, a simple text meter.

This is **not** wake-word detection yet. It only measures loudness. A later chapter of the
book builds the real thing.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| The meter never moves | Mic wires swapped or loose | Run [Lab 02](02-probe.md); section 8 checks the microphone |
| The meter is stuck at full | Very loud room, or the SD wire is picking up noise | Move somewhere quieter; reseat the SD wire |
| "I hear you!" appears all the time | Calibration happened while it was noisy | Stop and run again; stay quiet for the first second |
| The screen stays blank | The display is not working | Go back to [Lab 04](04-hello-world.md) |

## Try This

1. **Sensitivity.** Make `SPEECH_ABOVE_FLOOR` 1.0, then 3.0. How does "I hear you!" change?
   Which setting would a noisy classroom need?
2. **A clap.** Clap once. Does the meter jump and fall back? Then whistle a steady note. What
   does the meter do?
3. **A steady tone.** Play a steady tone from a phone next to the microphone. Does the meter hold
   still, or wobble like it does for speech?
4. **Peak hold.** The program already tracks `peak`. Show the highest loudness it has heard as a
   thin white line on the meter.

??? tip "Hint for number 4"
    Convert `peak` to a pixel position with `meter_fraction(peak)` and the same width. Draw
    a thin `fill_rect` 2 pixels wide there. Remember to draw the colored bar *first* so the
    white line is on top.

## Check Your Understanding

1. A frame is 512 samples at 12,800 samples per second. How long is it?
2. Why does the program subtract `middle` from every sample?
3. If the noise floor is 12 bits, how loud (in bits) must a sound be to count as "I hear you"?
   How many times louder is that than the floor?

??? question "Answers"
    1. 512 / 12,800 = 0.04 seconds, which is 40 milliseconds.
    2. The microphone has a DC offset, a constant added to every sample. Subtracting the
       average puts silence at zero.
    3. Above 14 bits. Two bits is two doublings, so it is 4 times louder.

## Where Next

You can now make sound and hear sound. [Lab 07](07-record-playback.md) puts them together:
record your voice and play it back.

*Review in the course:* [the I2S microphone lab](https://dmccreary.github.io/learning-micropython/hands-on-labs/18-sound-music-audio/13-i2s-microphone/)
