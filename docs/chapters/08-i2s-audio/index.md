---
title: "I2S Audio: Recording and Playing Sound"
description: "How the I2S bus carries sound in and out of the Pico: bit clock, word select, and serial data; machine.I2S for receiving and transmitting; audio buffers and frames; tones and stored audio; the self-hearing problem; and the frame time budget."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 11:11:35"
version: 1.11
---

# I2S Audio: Recording and Playing Sound

## Summary

This chapter brings sound in and out of the device. Students learn the three I2S signals, configure machine.I2S for receive and transmit, and move samples through audio buffers and frames. They then play tones and stored audio, handle the self-hearing problem, and keep every frame inside its time budget.

## Concepts Covered

This chapter covers the following 19 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| I2S Bus | 346 |
| Amplifier Shutdown Pin | 4 |
| Bit Clock | 1 |
| Word Select | 2 |
| Serial Data Line | 1 |
| machine.I2S Class | 339 |
| Mono and Stereo | 2 |
| I2S Receive | 317 |
| I2S Transmit | 21 |
| Left-Right Channel | 1 |
| Audio Buffer | 240 |
| Tone Generation | 4 |
| Stored Audio Playback | 10 |
| Self-Hearing Problem | 6 |
| Ring Buffer | 4 |
| Audio Frame | 198 |
| Sine Table | 1 |
| Mute and Resume | 3 |
| Frame Time Budget | 7 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 3: Sound and Digital Audio Basics](../03-sound-and-digital-audio/index.md)
- [Chapter 4: The Pico Kit Hardware and Wiring](../04-pico-kit-hardware/index.md)

---

## The Ears and the Voice Get Wired In

You have met the microphone and the amplifier as parts on a breadboard, and you ran tests 05, 06, and 07 to prove they work. This chapter explains *how* they work together with the Pico, and how to write the code yourself. By the end you will read live sound into memory, play a tone you generated, and play a recording, all without losing a single sample.

!!! mascot-welcome "Let the Sound Flow"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    In this chapter you will record your own voice into memory and play it back through the speaker, and you will learn the timing rule that keeps the sound from stuttering. Let's listen closely! Audio code is mostly about keeping a steady stream flowing.

## The I2S Bus

**I2S** (Inter-IC Sound, pronounced "eye-two-ess") is a bus designed to carry digital audio between chips. It uses three signal wires, and every I2S part in the kit uses the same three. In this book the Pico is always the one that generates the clocks, and the microphone and amplifier follow along.

### The Bit Clock

The **bit clock** is a steady pulse that ticks once for every bit of audio data. On each tick, one bit moves across the data wire. Microphone boards label it SCK (serial clock) and amplifier boards label it BCLK (bit clock). In MicroPython's `I2S` class it is the `sck` pin.

### The Word Select Line

The **word select** line marks the beginning of each sample and tells which channel it belongs to. It flips between low and high, once for each sample slot. A low level means the left channel's word is on the wire, and a high level means the right channel's. Boards label it WS or LRC (left/right clock). In MicroPython it is the `ws` pin.

### The Serial Data Line

The **serial data line** carries the audio bits themselves, one per bit-clock tick, most significant bit first. The microphone drives it toward the Pico (SD), and the Pico drives it toward the amplifier (DIN). In MicroPython it is the `sd` pin.

| Signal | Job | Microphone pin | Amplifier pin |
|--------|-----|----------------|---------------|
| Bit clock (`sck`) | One tick per bit | SCK, GP10 | BCLK, GP20 |
| Word select (`ws`) | Marks each word and its channel | WS, GP11 | LRC, GP21 |
| Serial data (`sd`) | The audio bits | SD, GP12 (to the Pico) | DIN, GP19 (from the Pico) |

A standard I2S frame carries two slots, left and right, so the bit clock ticks \( \text{rate} \times \text{bits per slot} \times 2 \) times a second. For the kit's microphone (12,800 samples per second, 32 bits per slot) that is \( 12{,}800 \times 32 \times 2 = 819{,}200 \) ticks per second, and for the speaker test (16,000 samples per second, 16 bits) it is 512,000.

Here is the rule you met in Chapter 4, now with its reason. MicroPython's I2S on the Pico drives the clock and word-select lines with one hardware program that needs them on *adjacent pins*, so `ws` must be the pin number right after `sck`. The microphone's SCK is GP10 and WS is GP11, and the amplifier's BCLK is GP20 and LRC is GP21.

!!! mascot-warning "ws Must Be sck Plus One"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If you swap or move these two wires, `I2S()` raises an error such as `invalid ws (must be sck+1)`. Do not "fix" it by editing the pin numbers in `config.py` to match swapped wires. Move the wires back to the pins in the pin assignment table.

Before you read the next activity, one detail: real I2S shifts the data by one clock tick after the word select flips, and the hardware handles that for you. The activity uses a simplified version, with 8-bit words, so the bits are easy to read.

#### Diagram: I2S Signal Reader


<iframe src="../../sims/i2s-signal-reader/main.html" width="100%" height="542px" scrolling="no"></iframe>
[Run I2S Signal Reader Fullscreen](../../sims/i2s-signal-reader/main.html)

<details markdown="1">
<summary>I2S Signal Reader</summary>
Type: microsim
**sim-id:** i2s-signal-reader<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** interpret<br/>
**Learning Objective:** The learner will interpret simplified I2S waveforms by reading the value of the left-channel sample from the serial data line in 6 waveforms, with at least 5 of 6 correct.

**Prerequisites:** I2S, bit clock, word select, serial data line, most significant bit first, signed 8-bit numbers (all defined in this chapter above the block, and in Chapter 3 for bit depth).

**Evidence of Mastery:** For each of the 6 waveforms the learner enters the signed decimal value of the left-channel word. An answer is correct when it equals the Left value column in Content. Mastery is 5 of 6 correct on the first attempt. Stepping through the example waveform in exploration is exploration, not evidence.

**Misconceptions:** (1) The word select line carries audio. (2) The least significant bit is sent first. (3) Both channels are always sent in the same word.

**Instructional Rationale:** Understand-level interpretation requires the learner to apply the roles of the three wires to a concrete waveform. Reading the bits in the order they arrive, and noticing that the word-select level says which channel they belong to, ties each wire to its role.

**Content:**

The simplified waveform has three traces: the bit clock, the word select, and the serial data. Each word has 8 bits. While word select is low, the 8 bits on the data line are the left-channel word; while word select is high, the next 8 bits are the right-channel word. A bit is sampled at each rising edge of the bit clock. Bits are sent most significant bit first, and the value is a signed 8-bit number (two's complement: the first bit is the sign, and values with a first bit of 1 are negative, from -128 to -1).

| # | Left word bits (first to last) | Left value | Why (shown as feedback) |
|---|---|---|---|
| 1 | 00000000 | 0 | All bits are zero, so the value is 0. |
| 2 | 01111111 | 127 | The sign bit is 0 and all other bits are 1: 64+32+16+8+4+2+1 = 127. |
| 3 | 10000000 | -128 | The sign bit is 1 and the rest are 0, the most negative value. |
| 4 | 11111111 | -1 | All ones in two's complement is -1. |
| 5 | 00101101 | 45 | 32 + 8 + 4 + 1 = 45. |
| 6 | 11010011 | -45 | The sign bit is 1. Flipping all bits gives 00101100, adding 1 gives 00101101 = 45, so the value is -45. |

The right-channel word for each waveform is 00000000 (silent) and is shown so the learner can see the word select line change.

**Provenance:** The word length of 8 bits is a simplification for teaching and the values are illustrative. The sim labels both "illustrative." The roles of the three wires come from the chapter sections above.

**Rules:** The left word is the 8 bits sampled while word select is low. The value is the signed 8-bit number: the bits read as an unsigned number n from 0 to 255, minus 256 if n is 128 or more.

**Learner Activity:**

1. The learner explores an example waveform: steps forward one bit-clock tick at a time and watches which wire changes and which bit is collected.
2. The learner starts the 6 waveforms. Waveform 1 shows the three traces.
3. The learner enters the left-channel value and submits.
4. The sim highlights the 8 bits in the left word, then shows the correct value and the Why text.
5. After waveform 6, the sim shows the score. The learner should notice that waveforms 5 and 6 give 45 and -45, values with the same size and opposite signs.

**Feedback:** 6 waveforms, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The left value is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The example waveform is shown stopped at the start, with the question "Which wire says whose sample this is?"

**Chapter Anchors:** The chapter states that the three wires are the bit clock, the word select, and the serial data line, that word select low means the left channel, and that the most significant bit is sent first.
</details>

## Channels: Mono and Stereo, Left and Right

A **channel** is one stream of samples. **Stereo** has two channels, left and right, interleaved so that the samples arrive as left, right, left, right. **Mono** has one channel. Voice assistants use mono because one microphone and one speaker are enough and mono halves the data.

The **left-right channel** idea is built into the word select line: when it is low the word belongs to the left channel, and when it is high it belongs to the right. A microphone such as the INMP441 has a pin, L/R, that chooses which slot it answers in. Tied to GND it answers in the left slot, and tied to 3V3 it answers in the right slot. The kit ties it to GND. If you move that wire, a program that expects the left slot may read silence or noise, so keep it where the pin assignment table puts it.

In MicroPython the choice is the `format` argument: `I2S.MONO` for one stream of samples, `I2S.STEREO` for two. The kit uses `I2S.MONO` for both the microphone and the speaker.

| Term | Meaning | Kit setting |
|------|---------|-------------|
| Mono | One stream of samples | `format=I2S.MONO` for both parts |
| Stereo | Two interleaved streams | Not used |
| Left channel | Word when word select is low | Microphone answers here (L/R on GND) |
| Right channel | Word when word select is high | Not used |

## The machine.I2S Class

The **machine.I2S class** is MicroPython's way to run an I2S bus. You create one object per bus, and the object has the methods you need for audio.

| Argument | Meaning | Microphone (receive) | Speaker (transmit) |
|----------|---------|---------------------|--------------------|
| id | Which I2S block (0 or 1) | 1 | 0 |
| `sck` | Bit clock pin | GP10 | GP20 |
| `ws` | Word select pin | GP11 | GP21 |
| `sd` | Serial data pin | GP12 | GP19 |
| `mode` | Direction | `I2S.RX` | `I2S.TX` |
| `bits` | Bits per sample | 32 | 16 |
| `format` | Channel layout | `I2S.MONO` | `I2S.MONO` |
| `rate` | Samples per second | 12,800 | 16,000 (test 05) or 12,800 (test 07) |
| `ibuf` | Internal buffer size in bytes | 40,000 | 8,192 |

The two I2S blocks are independent. The microphone is on block 1 and the speaker is on block 0, so they can run at the same time without fighting each other. Three methods do the work: `readinto(buf)` fills a buffer with samples from the microphone, `write(buf)` sends a buffer of samples to the amplifier, and `deinit()` shuts the bus down and releases its pins. By default `readinto` and `write` *block*, which means they wait until the work is done, and that waiting is what keeps your loop in step with the audio.

Remember the Chapter 2 rule for hardware: always call `deinit()`, in a `finally` block. The kit hides the setup of the microphone behind `config.init_microphone()`, shown here in full so you can see all the arguments in use.

```python
mic = I2S(1, sck=Pin(10), ws=Pin(11), sd=Pin(12),
          mode=I2S.RX, bits=32, format=I2S.MONO,
          rate=12800, ibuf=40000)
```

!!! mascot-encourage "Eight Arguments Is a Lot"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    A constructor with eight arguments looks scary, but the table above is the whole story: the pins come from the pin assignment table, and the rest describe the audio format. You have already run these exact lines in tests 05 and 06, so the hard part is done.

## Receiving Sound

**I2S receive** is the direction from the microphone to the Pico. After you create the I2S object in `RX` mode, the hardware fills an internal buffer with samples in the background, and your program collects them with `readinto`.

The INMP441 sends 24-bit samples inside 32-bit words, with the real audio in the top 24 bits. That is why the kit sets `bits=32` and shifts every sample right by `MIC_SAMPLE_SHIFT`, which is 8. The samples also carry a small offset added by the microphone, called the DC offset, which the code subtracts. It is not a fixed number. On the test board the average of single 40 ms frames wandered between about -5,400 and +9,100 from one second to the next, while test 07's 1.5 second recording averaged about 15,000. So measure the offset over the frame or recording you are processing, and do not assume a value. The loudness code from test 06 shows all of this in one function.

```python
def loudness_bits(buf):
    samples = [s >> config.MIC_SAMPLE_SHIFT
               for s in struct.unpack(FRAME_FORMAT, buf)]
    middle = sum(samples) // FRAME_SAMPLES
    average = sum(abs(s - middle) for s in samples) // FRAME_SAMPLES
    return math.log(average + 1) / LOG2
```

The function unpacks 512 four-byte numbers with `struct`, shifts each right by 8 to get the 24-bit value, finds the average (the DC offset, or "middle"), and then computes the average distance from the middle. The log base 2 turns that into the "bits" scale from Chapter 3.

*Worked example.* One second of microphone audio at 12,800 samples per second and 4 bytes per sample is \( 12{,}800 \times 4 = 51{,}200 \) bytes, so the microphone delivers 51.2 KB every second. A `readinto` call with a 2,048-byte buffer takes 40 ms, because the buffer holds 512 samples. In a loop, each `readinto` call returns exactly when the next 40 ms of sound has arrived.

Two practical notes come from the kit's tests. The microphone needs a moment to settle after it starts, so test 06 throws away the first 8 frames and test 07 throws away the first 100 ms. And the first reading of a new frame must be handled before the next one is due, which is the subject of the frame time budget below.

## Audio Buffers and Frames

An **audio buffer** is a block of memory that holds samples. In MicroPython it is a `bytearray` that you create once and reuse, as Chapter 2 described.

| Buffer | Size | Holds | Where it is used |
|--------|------|-------|------------------|
| Frame buffer (`buf`) | 2,048 bytes | 512 samples, 40 ms | Test 06 |
| Read chunk | 1,024 bytes | 256 samples, 20 ms | Test 07 recording loop |
| Recording buffer (`raw`) | 153,600 bytes | 3 seconds | Test 07 |
| Microphone internal buffer (`ibuf`) | 40,000 bytes | about 0.4 s measured (0.78 s if every byte held microphone data) | The I2S driver |
| Speaker internal buffer (`ibuf`) | 8,192 bytes | 256 ms at 16 kHz | The I2S driver |

An **audio frame** is the fixed-size slice of audio your program processes in one pass of its loop. Using frames keeps the work regular: read a frame, analyze it, update the screen, repeat. The kit's frame is 512 samples, and at 12,800 samples per second that is exactly

\[ \frac{512}{12{,}800} = 0.04 \text{ s} = 40 \text{ ms}, \qquad 512 \times 4 = 2{,}048 \text{ bytes.} \]

The frame length is a trade-off. A longer frame gives the FFT finer frequency detail (Chapter 9) but responds more slowly. A shorter frame responds faster but gives coarser detail and makes the loop run more often. At 40 ms the loop runs 25 times a second.

| Frame samples | Duration at 12,800 Hz | Bytes (32-bit) | Loop passes per second |
|---------------|----------------------|----------------|------------------------|
| 256 | 20 ms | 1,024 | 50 |
| 512 | 40 ms | 2,048 | 25 |
| 1,024 | 80 ms | 4,096 | 12.5 |

## The Ring Buffer

Between the hardware and your program sits a **ring buffer**, a block of memory treated as a circle. Samples are written at a *head* position that advances after each write and wraps from the end back to the start. Your program reads from the oldest unread position. The I2S driver's internal buffer (`ibuf`) is one of these. It lets the hardware keep recording while your program is busy for a moment, within the buffer's size.

The class below shows the idea in plain MicroPython. It overwrites the oldest data when it is full, so a writer that is never read cannot stall.

```python
class Ring:
    def __init__(self, size):
        self.buf = bytearray(size)
        self.size = size
        self.head = 0          # next place to write
        self.count = 0         # bytes waiting to be read

    def put(self, data):
        for b in data:
            self.buf[self.head] = b
            self.head = (self.head + 1) % self.size
            if self.count < self.size:
                self.count += 1

    def get(self, n):
        n = min(n, self.count)
        start = (self.head - self.count) % self.size
        out = bytes(self.buf[(start + i) % self.size] for i in range(n))
        self.count -= n
        return out
```

The `%` operator makes the position wrap. Here is a ring of 8 bytes in action.

| Step | Action | Contents oldest to newest | Head | Count |
|------|--------|--------------------------|------|-------|
| 1 | Put "ABCDEF" | A B C D E F | 6 | 6 |
| 2 | Get 2 | C D E F | 6 | 4 |
| 3 | Put "GHIJK" | D E F G H I J K (C lost) | 3 | 8 |

At step 3 the ring holds only 8 bytes, so adding 5 more to the 4 waiting forces the oldest byte, C, to be dropped. If your program falls behind the microphone by more than the ring holds, this is what happens to the sound: the ring has no room left and audio is lost. The loop must therefore keep up, which leads to the next idea.

!!! mascot-thinking "A Ring Is a Promise"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A ring buffer lets the hardware and your code run at their own paces, but only for a while. It does not make a slow program fast. It gives a slow program a bounded amount of grace, and then sound is lost.

## The Frame Time Budget

The **frame time budget** is the time you have to finish one pass of the loop before the next frame is ready. At 40 ms per frame, everything the loop does for one frame (read, analyze, draw, decide) must fit in 40 ms. If one pass takes longer, the microphone is still filling the ring while your code is busy, and the backlog grows.

Measure it. The `ticks_us` function gives microseconds, which suits a budget this small.

```python
frame_us = config.FFT_SIZE * 1_000_000 // config.MIC_SAMPLE_RATE   # 40000
start = time.ticks_us()
# ... read, process, draw ...
used = time.ticks_diff(time.ticks_us(), start)
if used > frame_us:
    print("overrun by", used - frame_us, "us")
```

`FFT_SIZE` is 512 in `config.py`, the same number as the frame, so `frame_us` is 40,000 microseconds. Printing `used` against it after each pass tells you how much room is left.

On the test board (`src/chapters/08-i2s-audio/02-mic-frame-reader.py`), the plain-Python loudness calculation from test 06 used about 10 ms of every 40 ms frame, so `readinto` waited about 30 ms. The loop kept up at 25 frames per second, with about 30 ms to spare.

Since `readinto` blocks until a frame arrives, a loop that takes less than 40 ms simply waits for the rest of the frame, and it stays in step. A loop that takes more than 40 ms never waits, and the backlog grows by the excess every pass.

*Worked example.* The ring was created with `ibuf=40000`, which would hold \( 40{,}000 / 2{,}048 \approx 19.5 \) frames if every byte held microphone data. Measurement says it holds about half that. `03-ring-latency.py` plays a click once a second and prints how long after the click the program read it. At 50 ms per pass, that delay grew by roughly 10 ms per pass, as the backlog model predicts, and then stopped growing at about 460 ms. Two of the 14 clicks were lost. So the usable depth is about 0.4 s, or 9.8 frames. One explanation, not yet confirmed, is that in MONO mode the driver stores both I2S slots for every sample, 8 bytes instead of 4, which gives \( 40{,}000 / 8 / 12{,}800 \approx 0.39 \) s. The rest of this chapter uses the measured depth of 9.77 frames.

Suppose each pass takes 50 ms because of a slow display update. Each pass, the microphone produces \( 50/40 = 1.25 \) frames but the loop consumes only 1, so the backlog grows by 0.25 frames per pass. It passes 9.77 frames after 40 passes, which is \( 40 \times 50 = 2.0 \) seconds. After that, audio is lost. If the pass took 130 ms, about the measured time of a full-screen redraw from Chapter 5, the backlog would grow by 2.25 frames per pass and overflow in only 5 passes, about 0.65 seconds.

| Time per pass | Keeps up? | Backlog growth per pass | First sample lost after |
|---------------|-----------|------------------------|-------------------------|
| 30 ms | Yes, waits 10 ms | none | never |
| 40 ms | Yes, no spare time | none | never |
| 50 ms | No | 0.25 frames | about 2.0 s |
| 130 ms (full redraw) | No | 2.25 frames | about 0.65 s |

Use the budget explorer to check your arithmetic.

#### Diagram: Audio Frame Time Budget Explorer


<iframe src="../../sims/audio-frame-budget-explorer/main.html" width="100%" height="552px" scrolling="no"></iframe>
[Run Audio Frame Time Budget Explorer Fullscreen](../../sims/audio-frame-budget-explorer/main.html)

<details markdown="1">
<summary>Audio Frame Time Budget Explorer</summary>
Type: microsim
**sim-id:** audio-frame-budget-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** examine<br/>
**Learning Objective:** The learner will examine 6 loop timings against the 40 ms frame budget to decide whether each keeps up with the microphone and, for those that do not, calculate the time until the first audio is lost, to within 0.1 s.

**Prerequisites:** audio frame, ring buffer, frame time budget, backlog (all defined in the sections above this block). The model is stated in the Rules field and shown on screen.

**Evidence of Mastery:** For each of the 6 timings the learner types the seconds until the first sample is lost, or "never". An answer is correct when it equals "never" where the Answer column says never, or is within 0.1 s of the number in the Answer column. Mastery is 5 of 6 correct on the first attempt. Changing the exploration slider and watching the backlog is exploration, not evidence.

**Misconceptions:** (1) A loop that takes slightly longer than the frame is fine because the buffer is big. (2) A loop that is faster than the frame wastes audio. (3) The ring holds all the audio forever.

**Instructional Rationale:** Analyze-level examination requires the learner to relate parts of the system (the producer, the ring, the consumer) and reason about how a small rate difference accumulates. Using the same formula on six timings lets the learner see which one is the borderline case and why.

**Content:**

The model: one audio frame is 2,048 bytes and arrives every 40 ms. The ring holds 9.765625 frames (the depth measured in `03-ring-latency.py`, equal to 40,000 bytes at 8 bytes per sample time: 5,000 sample times, or 0.390625 s). Each pass of the loop takes P milliseconds of work and then reads one frame. If the loop is faster than 40 ms, it waits for the frame.

| # | Time per pass P (ms) | Answer | Why (shown as feedback) |
|---|---|---|---|
| 1 | 30 | never | The loop is faster than 40 ms, so it waits for each frame and the backlog stays at zero. |
| 2 | 40 | never | The loop exactly matches the audio rate, so there is no growth. |
| 3 | 45 | 3.56 | Growth 0.125 frames per pass, so it passes 9.77 frames on pass 79, and 79 x 45 ms = 3.56 s. |
| 4 | 50 | 2.0 | Growth 0.25 frames per pass, so it passes 9.77 on pass 40, and 40 x 50 ms = 2.0 s. |
| 5 | 60 | 1.2 | Growth 0.5 frames per pass, so it passes 9.77 on pass 20, and 20 x 60 ms = 1.2 s. |
| 6 | 130 | 0.65 | Growth 2.25 frames per pass, so it passes 9.77 on pass 5, and 5 x 130 ms = 0.65 s. |

For exploration the learner sets P from 10 to 100 ms in steps of 0.1 ms, default 40.0 ms. The sim shows the backlog in frames growing against the capacity of 9.765625 frames.

**Provenance:** The frame size and ring size are the values in `src/kits/study-buddy-base/config.py` (`FFT_SIZE`, `MIC_SAMPLE_RATE`, `MIC_BUFFER_BYTES`). The ring depth of 9.765625 frames comes from a measurement on the test board at 50 ms per pass (the delay stopped growing near 460 ms), and its cause is not confirmed. The model is a simplification, and the sim labels it "model, based on one board's measurement." The 130 ms value is the measured full-screen update time from Chapter 5.

**Rules:** Let T be the larger of P and 40 ms. The backlog after n passes is n x (T / 40 - 1) frames. The first sample is lost at the first whole number n for which the backlog is greater than 9.765625, and the time is n x T. If T equals 40, nothing is ever lost. Times are shown in seconds to two decimal places.

**Learner Activity:**

1. The learner moves the slider and watches the backlog line rise or stay flat against the capacity line.
2. The learner starts the 6 timings. Timing 1 is shown.
3. The learner types the seconds until the first loss, or "never," and submits.
4. The sim draws the backlog line for that timing and shows the Why text.
5. After timing 6, the sim shows the score. The learner should notice that a loop only 5 ms too slow still loses audio within 3.6 seconds.

**Feedback:** 6 timings, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The slider is at 40.0 ms with the backlog flat at zero, and the question "How long can this loop run before audio is lost?"

**Chapter Anchors:** The chapter states that a frame is 512 samples, 2,048 bytes, and 40 ms; that the microphone ring was created with 40,000 bytes but measured about 9.8 frames (0.4 s) deep; and that a 50 ms pass loses audio after about 2.0 s while a 130 ms pass loses it after about 0.65 s.
</details>

## Transmitting Sound

**I2S transmit** is the direction from the Pico to the amplifier. You create the I2S object in `TX` mode and call `write` with a buffer of 16-bit samples. The call waits until the samples are copied into the internal buffer, which is what keeps the playback in step.

There is one trap, and test 05 shows how to avoid it. `write` returns as soon as the *last bytes are in the buffer*, which is up to one buffer-length before they have finished playing. If you call `deinit()` immediately, the end of the sound is cut off. Test 05 therefore writes a short tail of silence and sleeps for the buffer's duration.

```python
audio.write(silence(100))
time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)
```

The buffer holds `IBUF` bytes, each sample is 2 bytes, and the rate is `RATE` samples per second, so `IBUF * 1000 // (RATE * 2)` is the buffer's length in milliseconds (256 ms for the 8,192 bytes at 16 kHz). Adding 50 ms gives margin.

!!! mascot-tip "Let the Buffer Drain Before You Stop"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    If the last note of a sound is missing, you called `deinit()` too soon. Write a little silence and wait for the buffer's duration first, as test 05 does. You can compute the wait: `ibuf` bytes divided by bytes per second.

### Tone Generation

**Tone generation** means computing the samples of a sine wave at a chosen frequency. For each sample number \( i \) at sample rate \( R \), the value is

\[ s_i = A \sin\left(2\pi f \frac{i}{R}\right) \]

where \( f \) is the frequency in hertz and \( A \) is the amplitude. Test 05 does this with `math.sin` for every sample and a 10 ms fade-in and fade-out so that the tone starts and stops without a click.

*Worked example.* A 440 Hz note lasting 800 ms at 16,000 samples per second has \( 16{,}000 \times 0.8 = 12{,}800 \) samples, which is 25,600 bytes. At volume 40 (the kit default) the peaks are about 13,107.

### The Sine Table

Calling `math.sin` for every sample is slow. A **sine table** avoids it: calculate one cycle of the sine wave once, store it in an array, and then look up values by position. To make a tone of frequency \( f \), step through the table at a rate of \( f \times N / R \) positions per sample, where \( N \) is the table length.

```python
import math
import array

N = 256
SINE = array.array("h", [int(32767 * math.sin(2 * math.pi * i / N))
                         for i in range(N)])

def tone(freq, ms, rate=16000, volume=40):
    count = rate * ms // 1000
    out = array.array("h", [0] * count)
    step = freq * N / rate
    phase = 0.0
    for i in range(count):
        out[i] = SINE[int(phase) % N] * volume // 100
        phase += step
    return out
```

The table is made once at startup: 256 entries of 2 bytes, 512 bytes in all. The function then fills an `array` of 16-bit values by indexing the table; `phase` is the current position, `step` is how far to move on each sample, and `% N` wraps back to the start of the table. The result can be passed straight to `audio.write()`. For a 440 Hz tone at 16,000 samples per second, `step` is \( 440 \times 256 / 16000 = 7.04 \) positions per sample.

The table method trades a little accuracy for speed. Truncating the position to a whole number adds a faint roughness, which is fine for a beep. Chapter 10 shows how to make this loop faster still.

### Stored Audio Playback

**Stored audio playback** plays samples that were recorded earlier and saved in a file in flash. The file holds raw 16-bit mono samples at a known rate. The player reads it in small chunks and writes each chunk to the amplifier, so only one small buffer is ever in memory.

```python
def play_file(audio, path, chunk=1024):
    buf = bytearray(chunk)
    view = memoryview(buf)
    with open(path, "rb") as f:
        while True:
            n = f.readinto(buf)
            if not n:
                break
            audio.write(view[:n])
```

`readinto` fills `buf` from the file and returns the number of bytes read, `view[:n]` selects just those bytes without copying them (Chapter 2), and `write` waits until the chunk has been accepted. The loop ends when the file runs out. The I2S rate must match the rate the file was recorded at. A recording made at 12,800 Hz played at 16,000 Hz comes out faster and higher, like a chipmunk. If the file is a WAV file from Chapter 3, call `f.seek(44)` before the loop to skip the 44-byte header.

*Worked example.* One second of 16-bit mono audio at 16,000 Hz takes 32,000 bytes. The Pico's flash also holds MicroPython itself, so you have room for tens of seconds of it, enough for a small library of spoken phrases such as "Test tomorrow."

## Speaking Without Hearing Yourself

### The Self-Hearing Problem

The **self-hearing problem** is that the microphone picks up the speaker. When the Study Buddy speaks an answer, its own voice travels through the air to the microphone a few centimeters away, and the device hears itself. Worse, a program that listens for the wake word "Hey Pico" can be triggered by its own reply, and a program that records questions can record its own answers and answer them again.

The simplest solution, and the one the kit uses, is to never listen while speaking. Test 07 works this way: it records, closes the microphone with `mic.deinit()`, and only then opens the speaker. Strategies, from simplest to hardest:

| Strategy | How it works | Cost |
|----------|--------------|------|
| Push-to-talk | The microphone is only open while a button is held | None; this is what the kit does |
| Half-duplex | Close the microphone (or ignore its frames) while playing | A little code |
| A quiet tail | Keep ignoring the microphone for about 120 ms after the last sound leaves the speaker (measured; see below) | Slight delay |
| Echo cancellation | Subtract the known speaker signal from the microphone signal | Far beyond a Pico; out of scope |

The "quiet tail" matters because sound lingers: the speaker keeps playing whatever is still queued in its buffer, and the room carries the sound a little longer.

*Measured result.* `src/chapters/08-i2s-audio/06-self-hearing.py` plays a 1 kHz tone through the speaker while reading the microphone one 40 ms frame at a time. On the test board, with the speaker beside the microphone and the volume at 40 (the kit default):

| Moment | Microphone loudness | Compared with the room |
|--------|--------------------|------------------------|
| Before the tone | 13.1 bits (the noise floor) | 1 times |
| During the tone | 17.0 bits, steady | 3.9 bits louder, about 15 times |
| First frame after the last tone write | 16.3 bits | 3.2 bits louder |
| Second and third frames after | 13.7 and 13.6 bits | within 0.6 bits of the floor |
| Fourth frame after, onward | at the floor | 0 |

So the device hears itself clearly: the speaker is about 15 times louder to the microphone than the quiet room. And it goes quiet fast. In this test the writes to the speaker were paced one frame at a time, so very little sound was queued, and the microphone was back near the floor within about 2 frames, roughly 80 to 120 ms. If your program queues more audio in the speaker's buffer (up to 320 ms for the kit's 8,192-byte buffer at 12,800 Hz), add that time to the tail. Room noise can make a single frame read 1 bit high, so judge the tail by a run of three quiet frames, not by one.

### Mute and Resume

**Mute and resume** is stopping the sound and starting it again cleanly. A software mute stops writing samples, or writes zeros, and the amplifier plays silence. To avoid a click, fade the volume down over about 10 ms before stopping, and fade up when resuming, as test 05 does at the start and end of every note.

### The Amplifier Shutdown Pin

The MAX98357A breakout also has a **shutdown pin** (labeled SD). Pulling it to ground switches the amplifier off completely, which removes the faint hiss some amplifiers make even when playing silence and saves power. On most breakout boards a resistor holds the amplifier on when the pin is not connected, and the tested kit leaves it unconnected (check your board's documentation). If you want a hardware mute, wire the SD pin to an unused pin such as GP22 and drive it low to mute and high to resume.

```python
shutdown = Pin(22, Pin.OUT, value=0)    # mute: amplifier off
shutdown = Pin(22, Pin.IN)              # resume: let the board's resistor turn it on
```

The first line makes the pin an output driven low, which shuts the amplifier down. The second line turns the pin back into an input, so the board's own resistor decides the state, as it does when nothing is wired. Give the amplifier a few milliseconds to wake before sending audio. This is an optional extension, and nothing else in the book depends on it.

## Putting It All Together

You can now describe the audio path from end to end. The microphone drives the serial data line in step with the Pico's bit clock and word select, and the I2S hardware collects the bits into a ring buffer. Your loop reads one 40 ms frame at a time with `readinto`, and must finish its work before the next frame arrives. The amplifier is fed by `write`, and you let its buffer drain before stopping. While the speaker plays, the microphone stays closed.

Key takeaways:

- I2S uses three wires: bit clock (one tick per bit), word select (marks each word and its channel), and serial data; `ws` must be the pin after `sck`.
- Mono is one stream; stereo is two interleaved; the INMP441's L/R pin on GND selects the left slot.
- `machine.I2S` has `readinto`, `write`, and `deinit`, and blocking is what paces your loop.
- The INMP441's 24-bit samples arrive in 32-bit words, so shift right by 8 and subtract the DC offset.
- A frame of 512 samples at 12,800 Hz is 2,048 bytes and 40 ms; the whole pass has a 40 ms budget.
- A ring buffer gives bounded grace: the microphone's ring held about 0.4 s of audio when measured, so at 50 ms per pass it overflows in about 2 s.
- Drain the speaker's buffer before `deinit()`; use a sine table for fast tones; play stored audio in chunks.
- Never listen while speaking: use push-to-talk or close the microphone during playback.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "A recording you made at 12,800 Hz plays back higher and faster. What is the likely cause? Click to expand"
    The playback I2S object was created with a different sample rate (for example 16,000 Hz). The rate used to play must equal the rate used to record. Both come from `MIC_SAMPLE_RATE` in `config.py` in test 07.

??? question "Your loop does a 60 ms update every frame. About how long until the microphone ring starts losing audio? Click to expand"
    About 1.2 seconds. The loop falls behind by 0.5 frames per pass, the ring holds about 9.8 frames, so it overflows on pass 20, and \( 20 \times 60 \text{ ms} = 1.2 \) s.

!!! mascot-celebration "Sound In, Sound Out"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned the three I2S wires, how `machine.I2S` receives and transmits, how a 40 ms frame and a ring buffer keep the stream flowing, and why the device must not listen while it speaks. You now have everything you need to run the microphone and speaker on your own.

In Chapter 9 we turn these frames of samples into a spectrum with the FFT.
