---
title: "High-Performance MicroPython"
description: "How to make MicroPython fast enough for the 40 ms audio frame: measuring with ticks_us and the DWT cycle counter, avoiding allocation, typed arrays, Q15 fixed-point math, @micropython.viper, inline assembly, a viper FFT, the second core, and the trade-offs of each speed-up."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 13:15:12"
version: 1.11
---

# High-Performance MicroPython

## Summary

This chapter shows how to make MicroPython fast enough for real-time audio. Students compare pure Python with viper and inline assembly, use typed arrays and pre-allocated buffers, and measure with the cycle counter. They finish able to benchmark code against the frame budget and explain the trade-offs of each speedup.

## Concepts Covered

This chapter covers the following 20 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Typed Arrays | 4 |
| Array Passed By Address | 1 |
| Avoiding Allocation | 3 |
| Cycle Counter | 17 |
| Floating Point Cost | 2 |
| DWT Timer | 16 |
| Fixed-Point Math | 1 |
| Pure Python FFT | 6 |
| Timing Verification | 8 |
| Viper Code | 4 |
| Pre-Allocated Buffers | 1 |
| Benchmarking | 7 |
| Table Precomputation | 1 |
| Inline Assembly | 3 |
| Profiling | 1 |
| Assembly FFT | 2 |
| Frame Overrun | 4 |
| Real-Time Constraint | 2 |
| Dual Core Use | 1 |
| Performance Trade-Offs | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 4: The Pico Kit Hardware and Wiring](../04-pico-kit-hardware/index.md)
- [Chapter 8: I2S Audio: Recording and Playing Sound](../08-i2s-audio/index.md)
- [Chapter 9: Signal Processing and the FFT](../09-signal-processing-fft/index.md)

---

## The 40 ms Promise

Chapter 9 ended with an uncomfortable fact: the whole spectrum pipeline is written in plain Python, and the FFT inside it does 2,304 butterflies in every 40 ms frame. This chapter is about keeping the promise from Chapter 8, that every pass of the loop finishes before the next frame arrives. It teaches a method more than a bag of tricks: *measure, find the biggest cost, fix that, measure again*.

!!! mascot-welcome "Make It Fit in 40 Milliseconds"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    In this chapter you will time your own code down to single CPU cycles and learn the tricks that can make a slow loop dramatically faster. Let's listen closely! You will also learn when *not* to use them.

**An honest note before we start.** I could not run any of this chapter's benchmarks on the real kit while writing it. Everything that follows is either arithmetic you can check, a fact I verified in the MicroPython source or documentation, a result I computed by running the same integer code on a computer, or a clearly labelled *estimate*. Every speed that only the Pico can reveal is a blank in the results table near the end, with a script that fills it in. The code was checked in real MicroPython on a computer and against a software model of the Pico's rules, and `src/chapters/10-high-performance-micropython/README.md` lists exactly what was and was not checked.

## The Real-Time Constraint and the Frame Overrun

A **real-time constraint** is a deadline that a result must meet to be useful. A spectrum that arrives 200 ms late is not a slow answer; it is a wrong one, because the sound it describes has already gone. For the Study Buddy the deadline comes from the microphone: a new 512-sample frame arrives every 40 ms whether or not your code is ready for it.

Chapter 8 introduced the budget. In cycles it looks like this, at the Pico 2's 150 MHz clock:

\[ 0.040 \text{ s} \times 150{,}000{,}000 \text{ cycles/s} = 6{,}000{,}000 \text{ cycles per frame}, \qquad \frac{6{,}000{,}000}{512} \approx 11{,}719 \text{ cycles per sample.} \]

A **frame overrun** is a pass of the loop whose work takes longer than one frame. While your code is busy the microphone keeps filling its ring buffer, so the next `readinto()` returns at once with an old frame, and the backlog grows. Chapter 8 measured the ring's depth at about 9.8 frames; once the backlog passes that, audio is lost. A loop can therefore be in one of three states, and a program that counts them is much easier to trust than one that only prints an average.

| State | How the loop sees it | What it means |
|-------|----------------------|---------------|
| On time | `readinto()` waited more than a few milliseconds | The frame was not ready yet; there is spare time |
| Behind | `readinto()` returned in under 4 ms | The frame was already waiting; the loop has no spare time |
| Overrun | The work in this pass was longer than 40 ms | The backlog grew by this pass; audio will be lost if it keeps happening |

`06-frame-loop-budget.py` counts all three for a real microphone loop, and it holds back 10 ms of the budget for the screen update, because Chapter 6 measured 8.5 ms for the spectrum region. So the working limit for the audio work is 30 ms.

!!! mascot-thinking "A Deadline Is Not a Speed"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A fast loop is not the same as a loop that meets its deadline. Notice that the average does not matter: one pass in a hundred that takes 90 ms is enough to lose audio. Real-time code is judged by its *worst* pass.

## Measure First: Benchmarking

**Benchmarking** is timing a piece of code in a way you can repeat and trust. A single timing is not trustworthy, because interrupts and garbage collection add random delays. The recipe in `bench.py` is short:

1. Call `gc.collect()` first, so a collection does not strike in the middle of the timing.
2. Run the code several times.
3. Report the *best* time, which is the run that was disturbed least and so measures the code itself.
4. Separately, look at the spread of times to see how much a single run can vary.

```python
def bench(label, func, args=(), repeat=5, budget_us=40000):
    best_us = None
    for _ in range(repeat):
        gc.collect()
        t0 = time.ticks_us()
        func(*args)
        us = time.ticks_diff(time.ticks_us(), t0)
        if best_us is None or us < best_us:
            best_us = us
    print(label, best_us / 1000, "ms", 100 * best_us / budget_us, "% of a frame")
```

The real function also reads the cycle counter, described next, and prints a `RESULT|...` line you can paste into a table. `time.ticks_us()` counts microseconds, and one microsecond is 150 CPU cycles, so it cannot resolve anything shorter than a few hundred cycles. Time a loop of 512 samples or more, never a single statement.

!!! mascot-tip "Best of Five"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    When a timing jumps around, run the code five times and keep the smallest number. The smallest is the run with the least interference, so it is the closest to what the code itself costs. For a deadline, though, also look at the largest.

## The Cycle Counter and the DWT Timer

A **cycle counter** is a hardware register that adds one on every tick of the CPU clock. At 150 MHz one cycle is 6.67 ns, so a counter gives timings 150 times finer than `ticks_us()` and, better, in the unit that the instruction manuals use. The ARM Cortex-M33 processor in the Pico 2 has such a counter inside a block called the **DWT** (Data Watchpoint and Trace). The **DWT timer** is that cycle counter. It sits at fixed addresses and MicroPython reaches it through `machine.mem32`, which reads and writes any 32-bit address:

| Register | Address | What to do |
|----------|---------|------------|
| DEMCR | 0xE000EDFC | Set bit 24 (TRCENA) to switch the DWT block on |
| DWT_CTRL | 0xE0001000 | Set bit 0 (CYCCNTENA) to start counting; bit 25 (NOCYCCNT) set means there is no counter |
| DWT_CYCCNT | 0xE0001004 | The count itself, 32 bits |

```python
mem32[DEMCR] = mem32[DEMCR] | (1 << 24)          # allow the DWT block
if mem32[DWT_CTRL] & (1 << 25):                  # NOCYCCNT: this core has no counter
    ...                                          # fall back to ticks_us()
mem32[DWT_CYCCNT] = 0
mem32[DWT_CTRL] = mem32[DWT_CTRL] | 1            # start counting
cycles = mem32[DWT_CYCCNT]                       # read it
```

**This is unverified on the RP2350.** The three registers are standard for Cortex-M cores, and I could not confirm that this chip implements the counter or that MicroPython may touch it. `01-cycle-counter.py` finds out. It tries the sequence, checks that the counter changes, and compares its rate with `ticks_us()`: a working counter gives about 150 cycles per microsecond. If it reports no counter, nothing else in the chapter breaks, because `bench.py` falls back to microseconds and you convert at 150 cycles per microsecond.

Two details matter either way. The counter is 32 bits, so it wraps after \( 2^{32}/150{,}000{,}000 = 28.6 \) seconds, and you must always subtract with `(end - start) & 0xFFFFFFFF`. And the value is often a number above \( 2^{30} \), which MicroPython cannot hold in a small integer, so a read can allocate a little; `01` measures what one read costs so you can subtract it. A third item: `time.ticks_cpu()` sounds like a cycle counter, but in the current MicroPython source for this port it returns the microsecond timer, which `01` checks on your build.

## Profiling and Timing Verification

**Profiling** is finding out *where* the time goes inside a loop, so you speed up the part that matters. A **profiler** at this scale is a few lines: stamp the clock after each section and add the difference to that section's total. The `Profiler` class in `bench.py` does it:

```python
prof = Profiler()
while running:
    mic.readinto(frame);        prof.lap("wait")
    dsp.load_frame(...);        prof.lap("load")
    dsp.fft(re, im, tables);    prof.lap("fft")
    ...
prof.report(passes)             # milliseconds per pass, and each section's share
```

Profile before you optimize. In Chapter 9's pipeline the FFT does 2,304 butterflies while the magnitude and band steps do a few hundred operations each, so the arithmetic predicts that the FFT dominates, and the profile should confirm it. If it did not, there would be no point rewriting the FFT.

**Timing verification** is proving that the finished loop meets its deadline, by measuring many real passes and checking the worst one. It is different from benchmarking. Benchmarking asks "how fast can this code go?" and reports the best run. Timing verification asks "can this ever be late?" and reports the worst. `06-frame-loop-budget.py` runs the live loop for 8 seconds in each of two modes (pure Python and viper) and prints a verdict from three numbers: the mean, the 95th percentile, and the maximum of the work per pass, plus the overrun count. The verdict is a pass only if there were no overruns and the worst pass is within 30 ms.

Two traps make the average misleading. A garbage collection pause strikes only now and then, so it raises the maximum without moving the mean. And the loop must be tested under realistic load: with sound arriving (a quiet room may take a different path through your code than speech) and with the display redrawing. A timing result from an idle bench does not verify a loop that also draws.

## The Baseline: Pure Python FFT

The **pure Python FFT** is `dsp.fft()` from Chapter 9: lists or `array('f')` buffers, floating-point arithmetic, and every line interpreted. It is correct and readable, and it is the baseline every faster version here is compared with. Count its work first.

*Worked example.* A 512-point FFT does \( 256 \times 9 = 2{,}304 \) butterflies, and the body of each butterfly in `dsp.fft` is 10 Python statements (two index calculations, two twiddle lookups, two lines for the twiddle product, four for the sum and difference). That is \( 2{,}304 \times 10 = 23{,}040 \) statements per FFT. If the FFT may use 10 ms, which is a quarter of the frame, each butterfly may take \( 10 \text{ ms} / 2{,}304 = 4.34 \) microseconds, about 651 cycles, and each statement only about 65 cycles. A statement such as `tr = re[b]*c + im[b]*s` does two array reads, two multiplications and an addition, and each float result is a new heap object (next sections). Fitting that in 65 cycles looks very unlikely for an interpreter.

The table turns the question around: for each cost per butterfly, how long does the whole FFT take?

| Cycles per butterfly | Microseconds per butterfly | FFT of 512 points | Share of the 40 ms frame |
|---------------------|----------------------------|-------------------|--------------------------|
| 100 | 0.67 | 1.5 ms | 4% |
| 300 | 2.0 | 4.6 ms | 12% |
| 651 | 4.3 | 10.0 ms | 25% |
| 1,000 | 6.7 | 15.4 ms | 38% |
| 2,604 | 17.4 | 40.0 ms | 100% |
| 5,000 | 33.3 | 76.8 ms | 192% |
| 10,000 | 66.7 | 153.6 ms | 384% |

Every row is arithmetic: cycles \( \times 2{,}304 / 150{,}000 \) gives milliseconds. `02-fft-pure-python-bench.py` prints microseconds per butterfly, so multiply by 150 to find your row. Chapter 9 guessed 100 to 300 ms for the FFT; in this table that is 6,500 to 19,500 cycles per butterfly, which is a guess, not a measurement. **The real number is a blank in the results table below until someone runs the script on the kit.**

## Why Python Costs So Much Here

Four facts explain where the time of pure Python goes, and each points at a fix.

### Floating Point Cost

The RP2350's ARM cores include a single-precision floating-point unit, so a hardware add or multiply of two floats is cheap. The **floating point cost** you pay in MicroPython is elsewhere. In the MicroPython source for this port, floats are 32-bit single precision (`MICROPY_FLOAT_IMPL_FLOAT`), and every float *result* is a new object on the heap (the port uses the default object layout, in which a float is not packed into the value itself). So `y = y * 1.0001` runs the interpreter's float multiply and then allocates a small object, and the old object becomes garbage. Whether the C code uses the FPU instructions or software routines I did not verify. Either way, the allocation and the interpreter around the operation cost more than the multiply.

Integers are cheaper: a whole number that fits in 31 bits is stored inside the value, with no allocation. `03-allocation-and-floats.py` times 2,000 multiply-adds on integers and on floats so you can see the ratio on your board. The conclusion that matters is the design rule: *keep the hot loop on whole numbers where you can.*

### Typed Arrays

A **typed array** from the `array` module stores numbers of one kind packed into memory, with no object per element.

| Typecode | Element | Bytes each | Range |
|----------|---------|-----------|-------|
| `'b'` / `'B'` | signed / unsigned byte | 1 | -128..127 / 0..255 |
| `'h'` / `'H'` | signed / unsigned 16-bit | 2 | -32768..32767 / 0..65535 |
| `'i'` / `'I'` | signed / unsigned 32-bit | 4 | about +-2.1 billion / 0..4.29 billion |
| `'f'` | single-precision float | 4 | about 7 decimal digits |

*Worked example.* 512 numbers cost these amounts on the Pico, by arithmetic (a list slot is a 4-byte pointer; a float object occupies one 16-byte heap block):

| Container | Bytes for 512 numbers | How |
|-----------|----------------------|-----|
| list of floats | about 10,240 | \( 512 \times (4 + 16) \) |
| `array('f')` | 2,048 | \( 512 \times 4 \) |
| list of small integers | about 2,048 | \( 512 \times 4 \) |
| `array('h')` | 1,024 | \( 512 \times 2 \) |

`03` measures the same containers on the board, so you can compare. A typed array has a second benefit: the garbage collector does not need to look inside it, because it holds no pointers. And a third, which matters most for this chapter: a typed array is a block of memory with a fixed layout, so code that works at the machine level can address its elements directly.

### Array Passed By Address

When you pass an array to a function written in viper or assembly, MicroPython does not copy it. It passes the *address* of the first element, and the function reads and writes your memory in place, exactly as `readinto()` fills a buffer you own. This is **array passed by address**, and it is what makes the fast code fast: `window_viper(x, w, out, n)` takes three arrays and a count and touches no objects at all. It also removes the safety net. The function knows no length except the `n` you give it, so an `n` that is too large overwrites memory beyond the array.

### Avoiding Allocation and Pre-Allocated Buffers

Every allocation uses heap, and heap eventually needs a collection. The MicroPython documentation warns that a collection can take several milliseconds, which is a good fraction of a 40 ms frame. The rule for a real-time loop is therefore **avoiding allocation** inside it, and the habit that makes it possible is **pre-allocated buffers**: create every array, table, and buffer once, before the loop, and reuse it on every pass (the Chapter 2 rule, now with a cost attached). Chapter 9's scripts already follow it for `re`, `im`, `mag`, and the tables.

Which statements allocate? The list is not obvious, so `03` tests twelve of them with the garbage collector switched off and reports the bytes used. The first column of the next table is what MicroPython's object model predicts; running `03` on the kit confirms or corrects it.

| Statement (run 200 times) | Predicted to allocate? | Why |
|--------------------------|------------------------|-----|
| `x = x + 1` | no | A small integer lives inside the value |
| `y = y * 1.0001` | yes | The float result is a new object |
| `arr_f[3] = arr_f[3] * 1.0001` | yes | Reading makes a float, multiplying makes another |
| `arr_h[3] = (arr_h[3] * 3) >> 1` | no | Whole numbers in a typed array stay small integers |
| `buf[0:8]` | yes | A slice of a `bytearray` is a copy |
| `view[0:8]` | yes | A memoryview slice is a new (small) object |
| `[0] * 16` | yes | A new list |
| `struct.unpack("<4i", words)` | yes | A new tuple |
| `struct.pack_into("<i", words, 0, 7)` | no | Writes into memory you already own |
| `"%d" % 12345` | yes | A new string |
| `big + 1` where `big` is above \( 2^{30} \) | yes | Too big for a small integer on a 32-bit chip |
| `buf[5] = 77` | no | Stores into an existing byte |

Run the allocation quiz to test your own predictions before you look at the table.

#### Diagram: Allocation Classifier


<iframe src="../../sims/allocation-classifier/main.html" width="100%" height="482px" scrolling="no"></iframe>
[Run Allocation Classifier Fullscreen](../../sims/allocation-classifier/main.html)

<details markdown="1">
<summary>Allocation Classifier</summary>
Type: microsim
**sim-id:** allocation-classifier<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** distinguish<br/>
**Learning Objective:** The learner will distinguish 12 MicroPython statements that allocate heap memory from those that do not, with at least 10 of 12 correct.

**Prerequisites:** heap, garbage collection, small integer, float object, typed array, pre-allocated buffer, memoryview (defined in Chapter 2 and in this chapter above the block).

**Evidence of Mastery:** For each of the 12 statements the learner chooses "Allocates" or "Does not allocate" and submits before the answer is shown. A choice is correct when it matches the Answer column in Content. Mastery is 10 of 12 correct on the first attempt. Reading the Why text after an answer is feedback, not evidence.

**Misconceptions:** (1) Any arithmetic is free. (2) A slice never copies. (3) Floats are stored inside the value, like small integers. (4) Writing into an array allocates.

**Instructional Rationale:** Analyze-level distinction asks the learner to separate cases by a hidden property, whether a new object is created, using the object model rather than memorized examples. Committing before the answer is shown makes the learner apply the model, and the Why text names the object that is created, which is what the learner needs for the next unfamiliar statement.

**Content:**

The 12 statements are shown one at a time in this order, each with its answer. The answers are what MicroPython's object model predicts for the Pico's 32-bit chip; `03-allocation-and-floats.py` measures them on the board.

| # | Statement | Answer | Why (shown as feedback) |
|---|---|---|---|
| 1 | `x = x + 1` (x is a small whole number) | Does not allocate | A small integer lives inside the value itself. |
| 2 | `y = y * 1.0001` (y is a float) | Allocates | The float result is a new heap object. |
| 3 | `arr_f[3] = arr_f[3] * 1.0001` (arr_f is array('f')) | Allocates | Reading an element makes a float object, and so does the product. |
| 4 | `arr_h[3] = (arr_h[3] * 3) >> 1` (arr_h is array('h')) | Does not allocate | Every value is a small integer. |
| 5 | `part = buf[0:8]` (buf is a bytearray) | Allocates | A slice of a bytearray is a new bytearray. |
| 6 | `part = view[0:8]` (view is a memoryview) | Allocates | A memoryview slice is a new, small memoryview object, though it copies no data. |
| 7 | `t = [0] * 16` | Allocates | A new list is created. |
| 8 | `t = struct.unpack("<4i", words)` | Allocates | A new tuple holds the four results. |
| 9 | `struct.pack_into("<i", words, 0, 7)` | Does not allocate | It writes into memory the program already owns. |
| 10 | `s = "%d" % 12345` | Allocates | A new string is built. |
| 11 | `z = big + 1` (big is 2**30) | Allocates | 2**30 does not fit a 31-bit small integer on a 32-bit chip, so the value is a big-integer object. |
| 12 | `buf[5] = 77` | Does not allocate | It stores into a byte of an existing bytearray. |

**Provenance:** The answers are predictions from the MicroPython object model on a 32-bit port with the default object layout (source: `ports/rp2/mpconfigport.h`, which sets single-precision floats and does not override the object representation). They are labelled "expected" in the sim until `03-allocation-and-floats.py` has been run on the kit. Statement 11 depends on a 31-bit small integer and is not true on a 64-bit computer; the sim says so.

**Rules:** A statement allocates when it creates a new object that is not a small integer. A small integer is a whole number from -2**30 to 2**30 - 1. Storing into an existing buffer never allocates.

**Learner Activity:**

1. The learner reads statement 1 and chooses Allocates or Does not allocate.
2. The sim shows the answer and the Why text, and a running score.
3. The learner continues through statement 12.
4. After statement 12, the sim lists the statements the learner got wrong. The learner should notice that the safe statements either work on small integers or write into an existing buffer.

**Feedback:** 12 statements, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. <Answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 12" is shown.

**Starting State:** Statement 1 is shown with the question "Does this line create a new object?"

**Chapter Anchors:** The chapter states that floats allocate, small integers do not, a bytearray slice copies, a memoryview slice makes a small object, `struct.pack_into` writes in place, and that the predictions are confirmed on the kit by `03-allocation-and-floats.py`.
</details>

### Table Precomputation

**Table precomputation** is the rule that anything which does not change between frames is computed once, before the loop, and stored. You have used it twice already: the sine table in Chapter 8 and `make_tables()` in Chapter 9, which fills the Hann window, the twiddle factors, and the bit-reversal table at start-up. The saving is easy to count. Without the twiddle tables, every butterfly would compute a cosine and a sine: \( 2{,}304 \times 2 = 4{,}608 \) trigonometric calls per frame, or \( 4{,}608 \times 25 = 115{,}200 \) per second. With the tables the loop calls none, and the one-time cost is 512 sine and cosine calls, paid at boot. The price is memory, which is small here: 256 cosines and 256 sines in `array('f')` are 2,048 bytes.

### Fixed-Point Math

**Fixed-point math** avoids floats by storing a fraction as a whole number with an agreed scale. In **Q15** format a number between -1 and 1 is stored as an integer from -32768 to 32767, with the value equal to the integer divided by 32768. So 16384 means 0.5 and -16384 means -0.5. To multiply two Q15 numbers, multiply the integers and shift right by 15 to remove the extra scale:

\[ (a \times b) \gg 15 \]

*Worked example.* \( 0.5 \times 0.5 \): \( 16384 \times 16384 = 268{,}435{,}456 \), and \( 268{,}435{,}456 \gg 15 = 8192 \), which is 0.25. `08-q15-fixed-point.py` runs six cases on your computer:

| a (Q15) | b (Q15) | \( (a \times b) \gg 15 \) | Meaning |
|---------|---------|---------------------------|---------|
| 16384 | 16384 | 8192 | 0.5 x 0.5 = 0.25 |
| 32767 | 32767 | 32766 | the largest value squared is just under 1.0 |
| -16384 | 16384 | -8192 | -0.5 x 0.5 = -0.25 |
| 3 | 3 | 0 | tiny numbers vanish: \( 9 \gg 15 = 0 \) |
| -3 | 3 | -1 | a negative result rounds toward minus infinity |
| -32768 | -32768 | 32768 | (-1.0) x (-1.0) = +1.0, which does not fit in 16 bits |

Two hazards follow. A result can fall outside the range (the last row), and the intermediate product must fit in the 32-bit register that holds it: two products near \( 32768^2 \) add up to \( 2^{31} \), one more than a signed 32-bit register can hold. The fixed-point FFT later in this chapter avoids both with a scale-down at every stage.

#### Diagram: Q15 Calculator


<iframe src="../../sims/q15-calculator/main.html" width="100%" height="532px" scrolling="no"></iframe>
[Run Q15 Calculator Fullscreen](../../sims/q15-calculator/main.html)

<details markdown="1">
<summary>Q15 Calculator</summary>
Type: microsim
**sim-id:** q15-calculator<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the Q15 product (a x b) >> 15 of 6 pairs of Q15 integers, and state whether the result fits in 16 bits, with at least 5 of 6 correct.

**Prerequisites:** fixed-point math, Q15 format, arithmetic shift right (all defined in this chapter above the block).

**Evidence of Mastery:** For each of the 6 pairs the learner types the whole-number result and submits. A result is correct when it equals the Answer column in Content. For pair 6 the learner must also choose "Fits in 16 bits" or "Does not fit", and the pair counts as correct only when both are right. Mastery is 5 of 6 correct on the first attempt. Using the exploration calculator is exploration, not evidence.

**Misconceptions:** (1) The product of two Q15 numbers is already Q15. (2) A shift right always rounds toward zero. (3) Q15 can hold exactly 1.0.

**Instructional Rationale:** Apply-level calculation needs practice on cases that differ in kind: a normal product, a vanishing product, a negative rounding case, and an overflow. Committing a number before the result is shown makes the learner carry out the shift, not recognize it.

**Content:**

The sim shows the formula result = (a x b) >> 15, where >> is an arithmetic shift right that keeps the sign and rounds toward minus infinity. A 16-bit signed Q15 number fits when it is from -32768 to 32767.

| # | a | b | Answer | Fits in 16 bits? | Why (shown as feedback) |
|---|---|---|---|---|---|
| 1 | 16384 | 16384 | 8192 | yes | 16384 x 16384 = 268,435,456, and 268,435,456 >> 15 = 8192. |
| 2 | 32767 | 32767 | 32766 | yes | 32767 x 32767 = 1,073,676,289, and >> 15 gives 32766. |
| 3 | -16384 | 16384 | -8192 | yes | The product -268,435,456 >> 15 is -8192. |
| 4 | 3 | 3 | 0 | yes | 3 x 3 = 9, and 9 >> 15 is 0: the result is smaller than one Q15 step. |
| 5 | -3 | 3 | -1 | yes | -9 >> 15 rounds toward minus infinity, giving -1, not 0. |
| 6 | -32768 | -32768 | 32768 | no | The product is +1,073,741,824, and >> 15 gives 32768, one more than the largest 16-bit value. |

For exploration the learner enters any two Q15 integers from -32768 to 32767 (step 1, default 16384 and 16384) and sees the full product, the shifted result, the real values (integer / 32768) and whether the result fits.

**Provenance:** The six pairs are the rows of the table in the chapter section "Fixed-Point Math", produced by `src/chapters/10-high-performance-micropython/08-q15-fixed-point.py`.

**Rules:** result = floor(a x b / 32768). real value = integer / 32768. A result fits in 16 bits when -32768 <= result <= 32767. Inputs: min -32768, max 32767, step 1, unit none (Q15 integer).

**Learner Activity:**

1. The learner enters pairs in the exploration calculator and watches the full product and the shifted result.
2. The learner tries 32767 x 32767 and -32768 x -32768 and notices that one fits and the other does not.
3. The learner starts the 6 pairs. Pair 1 is shown.
4. The learner types the result (and, for pair 6, the fit choice) and submits.
5. The sim shows the correct answer and the Why text.

**Feedback:** 6 pairs, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The exploration calculator shows 16384 x 16384 = 8192 with the real values 0.5 x 0.5 = 0.25, and the question "What do you get when you multiply two Q15 numbers?"

**Chapter Anchors:** The chapter states that 16384 stands for 0.5, that 16384 x 16384 >> 15 is 8192, that 3 x 3 >> 15 is 0, and that -32768 x -32768 >> 15 is 32768, which does not fit in 16 bits.
</details>

## Viper: Machine Code from Python

**Viper code** is Python that MicroPython compiles to real machine instructions for the processor, instead of interpreting it. You mark a function with `@micropython.viper` and add type hints to its arguments. Inside, integers are plain 32-bit machine words in registers (they wrap around instead of growing), array arguments become pointers into your memory, and nothing is allocated. Three pointer types read arrays of different widths: `ptr8` for bytes, `ptr16` for 16-bit elements, and `ptr32` for 32-bit elements, indexed like lists with no bounds checking.

Here is the windowing loop from Chapter 9 in its viper form (`kernels.py`). It multiplies each signed 16-bit sample by a Q15 window value:

```python
@micropython.viper
def window_viper(x: ptr16, w: ptr16, out: ptr16, n: int):
    i = 0
    while i < n:
        s = int(x[i])
        if s >= 32768:            # ptr16 reads are unsigned: sign-extend by hand
            s -= 65536
        out[i] = (s * int(w[i])) >> 15
        i += 1
```

The type hints turn the three arrays into pointers and `n` into a machine integer. The loop body is the same arithmetic as the Python version `out[i] = (x[i] * w[i]) >> 15`. The lines about 32768 are the first trap.

!!! mascot-warning "ptr16 Reads Are Unsigned"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A `ptr16` read zero-extends, so a stored -1 comes back as 65535. If your samples are signed, subtract 65536 when the value is 32768 or more, as `window_viper` does. `04-window-kernels.py` prints the raw read so you can see it, and it also checks all four versions give identical answers.

Viper has more rules, from the MicroPython documentation. There are no default argument values. Floating-point works but is not optimized, so keep floats out. Slices are not supported on pointers. And casting one viper value to another viper type costs nothing at run time, but casting a Python object can be slow, so do the casts at the top of the function and not inside a hot loop. Integer division (`//`) calls a helper function; this chapter's code uses shifts inside loops instead.

I checked the two viper functions in `kernels.py` in real MicroPython running on a computer (an x86-64 build of the current source), and they produce exactly the same outputs as the plain Python versions over 512 random samples. That checks the code and the `ptr16` rule. It says nothing about speed on the Pico.

## The Viper Q15 FFT

A fixed-point FFT is the Chapter 9 algorithm with whole numbers. `fft_viper.py` holds it: the same bit-reversal reorder, the same nine stages of butterflies, the same in-place updates, but `re` and `im` are `array('i')`, the twiddle factors are Q15 integers (cosine and sine times 32768), and the functions are viper. After each butterfly both outputs are **halved**, so a number never grows beyond what it started with. That is how fixed-point FFTs avoid overflow: the 512-point transform's outputs are \( 1/512 \) of the true values, because nine halvings multiply to \( 1/512 \).

```python
tr = (rb * c + ib * s + 16384) >> 15       # twiddle times the second number, Q15
ti = (ib * c - rb * s + 16384) >> 15
re[b] = (ra - tr + 1) >> 1                  # difference, halved
im[b] = (ia - ti + 1) >> 1
re[a] = (ra + tr + 1) >> 1                  # sum, halved
im[a] = (ia + ti + 1) >> 1
```

The added 16384 and 1 round the result to the nearest integer rather than always down.

*Worked example.* One butterfly at 45 degrees, where \( c = s = 23{,}170 \) (0.7071 in Q15). Let the first number be \( 4000 + 0j \) and the second \( 3000 + 1000j \):

| Step | Calculation | Result |
|------|-------------|--------|
| tr | \( (3000 \times 23170 + 1000 \times 23170 + 16384) \gg 15 \) | 2828 |
| ti | \( (1000 \times 23170 - 3000 \times 23170 + 16384) \gg 15 \) | -1414 |
| new second number | \( ((4000 - 2828 + 1) \gg 1,\; (0 + 1414 + 1) \gg 1) \) | 586 + 707j |
| new first number | \( ((4000 + 2828 + 1) \gg 1,\; (0 - 1414 + 1) \gg 1) \) | 3414 - 707j |

The exact answer for the twiddle product is \( (3000 + 1000j)(0.7071 - 0.7071j) = 2828.4 - 1414.2j \), so `tr` and `ti` agree to the nearest integer, and the halved outputs are half of \( 4000 \pm 2828.4 \) and so on.

### How accurate is it?

Precision is the price of whole numbers. The input is cut from 24 bits to 16 (`shift=16` in `load_frame_q15`), and every stage rounds. I measured the effect without the Pico: integer arithmetic gives the same answers on any machine as long as nothing overflows, so I ran the same functions on a computer inside a model that checks every addition and multiplication against 32-bit limits (none overflowed), and compared with the floating-point pipeline on synthetic frames: 48 frames of a single tone (six amplitudes from about -62 to -12 dBFS, four frequencies, two noise seeds) with random noise of about -63 dBFS added.

| Question | Result of the computer model |
|----------|-----------------------------|
| Largest difference in a band louder than -50 dBFS | 0.20 dB (mean 0.03 dB over 48 bands) |
| Largest difference in a band louder than -60 dBFS | 0.54 dB (30 bands) |
| Peak bin the same as the float FFT | 42 of 42 test tones |
| Rounding-noise floor of the Q15 path, in the bands away from a clean test tone (`shift` 16) | about -65 to -75 dBFS |
| Same, with `shift` 14 (four times the input gain) | about -77 to -90 dBFS |
| Same, with `shift` 12 (sixteen times the gain) | about -91 to -99 dBFS |

Read the table as a trade. Where the sound is loud the viper FFT agrees with the float one to within about half a decibel. Where it is quiet, near the room's own noise, rounding in the Q15 path dominates, so the quietest bands read up to roughly 17 dB too high in my noise-only test. Raising the gain (a smaller `shift`) lowers that floor by 6 dB per factor of two, but a loud sound then clips, because `load_frame_q15` clamps at \( \pm 32767 \): at `shift` 12 any peak louder than about -24 dBFS saturates. For a display of speech and tones the default is fine; for a calibration of the noise floor (Chapter 11) use the float path or a lower `shift`.

`05-fft-viper-bench.py` does the same comparison on the Pico, with the real time per stage, and also checks that `fft_q15` allocates zero bytes. The speed is not known yet.

## Inline Assembly

**Inline assembly** lets you write machine instructions directly inside a Python file with `@micropython.asm_thumb`. It is the last stop on the road down. Each line is one ARM Thumb instruction, and you decide which register holds what. The function receives up to four arguments in registers `r0`, `r1`, `r2`, `r3`, and whatever is in `r0` when the function ends is the return value. You may use `r0` to `r7`. Arrays arrive as the address of their first element.

The smallest useful loop adds up an array of signed 16-bit numbers. Read it line by line, since there are only eight instructions:

```python
@micropython.asm_thumb
def sum16_asm(r0, r1):            # r0 = address of the array, r1 = count (must be > 0)
    mov(r2, 0)                    # r2 = running total
    label(LOOP)
    ldrh(r3, [r0, 0])             # r3 = next number, zero-extended from 16 bits
    lsl(r3, r3, 16)
    asr(r3, r3, 16)               # sign-extend it to 32 bits
    add(r2, r2, r3)               # total = total + number
    add(r0, r0, 2)                # move to the next 16-bit element
    sub(r1, r1, 1)                # one fewer left
    cmp(r1, 0)
    bgt(LOOP)                     # branch back while the count is greater than 0
    mov(r0, r2)                   # the value in r0 is returned
```

| Instruction | What it does |
|-------------|--------------|
| `ldrh(r3, [r0, 0])` | Load 16 bits from the address in `r0` plus 0 into `r3` |
| `lsl`, `asr` by 16 | Shift left then arithmetic shift right: copies bit 15 into the upper 16 bits (sign extension) |
| `add`, `sub` | Add or subtract; `r0` moves by 2 bytes because each element is 2 bytes |
| `cmp`, `bgt` | Compare the count with 0, and branch back to `LOOP` if it is greater |
| `label(LOOP)` | A name for the position, used by the branch |

The windowing loop is the same idea with a multiply: two loads, a sign extension, `mul(r4, r5)`, an arithmetic shift by 15, a store with `strh`, and three pointer increments. Counting from the source in `kernels_asm.py`, `window_asm` runs 13 instructions per sample and `sum16_asm` 8 per element; I got those by stepping through the code in an emulator written for this chapter, which also confirmed that all three versions of the sum and the window give the same answers. That emulator checks the *logic*; it does not check the real assembler's encoding rules.

!!! mascot-encourage "Assembly Looks Scarier Than It Is"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    A page of mnemonics is hard to take in at first glance, and most people feel that way. Read one instruction at a time, as the table above does, and remember that every line only moves, adds, or compares numbers you have already met.

There are three cautions. The assembler has no safety: a count of 0 still runs the loop once, and a bad address corrupts memory, so pass a count above 0 and no larger than the array. Not every instruction exists on every Pico. The MicroPython source enables the wider ARMv7-M instructions (`sdiv`, `udiv`, `movw`, `clz`, and others) when the firmware is built for a Thumb-2 core, which the RP2350's Cortex-M33 is; the older RP2040 lacks them. The loops in this chapter use only the basic instructions that both have, so they do not depend on it. And `asm_thumb` is ARM-only: it works while the Pico 2 runs on its ARM cores (the default), but if you flash firmware for the chip's RISC-V cores it is not available, because that build has a different assembler.

**Speed estimate, not measured.** Counting 13 instructions in the windowing loop, two of which are loads and one a taken branch, a rough guess for the Cortex-M33 is 15 to 25 cycles per sample. For 512 samples that is 7,700 to 12,800 cycles, or 51 to 85 microseconds. That comes from instruction counts and typical cycle costs, not from a measurement. `04-window-kernels.py` measures all four versions on the board, and its numbers replace this paragraph.

## The Assembly FFT

An **assembly FFT** puts the butterfly loop into inline assembly. It is the fastest way to run an FFT on this board without leaving MicroPython, and it is a *stretch exercise* here: I have not written or run one, and I will not pretend to. What I can give you is the design, so you know what is involved.

| Part | Where it lives | Why |
|------|----------------|-----|
| Bit-reversal reorder | viper (`fft_q15`) | It runs once per frame and touches 512 entries |
| The 9 stages and the loop over groups | Python or viper | There are only 9 stages; but stage 1 has 256 groups, so a Python call per group means 511 calls in total, which is too many |
| The butterflies inside a stage | assembly | 2,304 per frame; this is where the time is |
| Twiddle factors | Q15 arrays read by address | Already computed |

The assembly function can take only four arguments, so it must be given a small array of parameters (the stage size, the twiddle stride, and the three array addresses) as one of them. Each butterfly needs about six loads, four multiplies, six additions, four shifts, four stores and some pointer arithmetic: roughly 35 to 45 instructions, with `r0` to `r7` only for all of the values. *If* a butterfly took 60 cycles, the FFT would take \( 2{,}304 \times 60 = 138{,}240 \) cycles, or 0.92 ms. That is a paper estimate from my own instruction count, not a measurement; treat it as the target to beat when you try the exercise.

Before you attempt it, ask whether you need it. If the viper FFT already meets the deadline with room to spare, the assembly version buys speed you cannot use and costs readability, so the next sections give you the means to decide.

## Using the Second Core

**Dual core use** means running a second piece of code at the same time on the Pico's other processor core. MicroPython starts one with `_thread.start_new_thread(function, args)`; on the Pico there are only two threads, one per core, and the new one runs on core 1. In the MicroPython source for this port there is no global interpreter lock, so the two cores run MicroPython code truly in parallel.

The temptation is to read the microphone on core 0 and run the FFT on core 1. It can work, but it comes with hazards, which is why this book keeps the audio work on one core (Chapter 4 said so):

| Hazard | Why | Safe habit |
|--------|-----|-----------|
| Shared heap | Both cores allocate from one heap with one garbage collector protected by a lock; a collection started by one core can make the other wait | Allocate nothing on core 1: pre-allocate everything, use viper |
| Hardware ownership | Starting or stopping I2S, the display's SPI, or a pin from two cores at once is unsafe, and I did not verify how the I2S driver's interrupts behave when its owner is core 1 | Do all `I2S`, `SPI`, and `Pin` work on core 0; let core 1 touch only pure data |
| Data races | A buffer being rewritten by one core while the other reads it gives garbage | Use two buffers and a flag that only one core writes |
| Pauses | Flash writes typically pause the other core (the port sets up a lockout for this) | Keep file writes out of the real-time loop |
| Latency | Doing the FFT on frame \( k \) while frame \( k+1 \) is read means the display is one frame (40 ms) behind | Accept it, or avoid the second core |

`07-dual-core.py` measures the safe version of the idea. It runs a worker that touches no hardware, first alone and then beside core 0's counting loop, and reports how much each side slows the other. Pairs A and B are the solo baselines; C uses the allocation-free viper FFT, and D uses the pure-Python float FFT that allocates. My *expectation*, not a measurement: in C the two sides should run at nearly their solo speeds, and in D at least one should be slower because of the shared garbage collector. The script fills in those four ratios.

## Choosing: Performance Trade-Offs

Each speed-up buys time and charges something else. **Performance trade-offs** are the choice of what to pay.

| Approach | Speed | Readability | Portability | Accuracy | Memory | Risk |
|----------|-------|-------------|-------------|----------|--------|------|
| Plain Python on lists | slowest | best | any MicroPython | float precision | most | none |
| Python on `array` | slow | good | any MicroPython | float precision | less | none |
| Fixed-point in Python | slow | fair | any MicroPython | limited by bits | less | overflow |
| Viper | much faster (to be measured) | fair | Pico and other supported ports | integer only, limited by bits | least | no bounds checking, unsigned `ptr16` |
| Inline assembly | fastest (to be measured) | poor | ARM Thumb only | integer only | least | crashes, silent corruption |
| Second core | up to 2 cores of work | poor | dual-core ports only | unchanged | shared heap | races, GC stalls |

The rule that comes out of the table is to use the *simplest* approach that keeps the **worst** pass inside the budget (less the display reserve). Start with plain Python and measure. If the profile shows one loop dominating, move only that loop to viper. Move to assembly or a second core only when viper still does not fit. Stop at the first row that passes timing verification: speed past the deadline is not worth any cost.

#### Diagram: Speed-Up Chooser


<iframe src="../../sims/speedup-chooser/main.html" width="100%" height="557px" scrolling="no"></iframe>
[Run Speed-Up Chooser Fullscreen](../../sims/speedup-chooser/main.html)

<details markdown="1">
<summary>Speed-Up Chooser</summary>
Type: microsim
**sim-id:** speedup-chooser<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Evaluate<br/>
**Bloom Verb:** recommend<br/>
**Learning Objective:** The learner will recommend, for 6 scenarios, the simplest implementation whose worst-case pass time fits within the frame budget minus the display reserve, or state that none fits, with at least 5 of 6 correct.

**Prerequisites:** frame budget, display reserve, worst-case pass time, viper code, inline assembly, performance trade-offs (all defined in this chapter above the block).

**Evidence of Mastery:** For each scenario the learner chooses one of "Plain Python", "Viper", "Assembly", or "None fits" and submits. A choice is correct when it matches the Answer column in Content. Mastery is 5 of 6 correct on the first attempt. Changing the numbers in the exploration panel is exploration, not evidence.

**Misconceptions:** (1) The fastest implementation is always the best choice. (2) An implementation that fits on average fits the deadline. (3) Assembly is always needed for real-time audio.

**Instructional Rationale:** Evaluate-level recommendation requires the learner to apply a stated criterion to evidence and justify the choice. The scenarios put a boundary case (an implementation that fits by exactly zero margin), a case where the simplest option already fits, and a case where nothing fits, so the learner cannot recommend by habit.

**Content:**

The numbers in this activity are **illustrative** and are not measurements of the kit. Each scenario gives the frame budget, the display reserve, and the worst-case pass time of three implementations, all in milliseconds. The complexity order from simplest to hardest is Plain Python, Viper, Assembly. The fitting limit is the budget minus the reserve; an implementation fits when its worst-case time is less than or equal to the limit.

| # | Budget (ms) | Reserve (ms) | Limit (ms) | Plain Python | Viper | Assembly | Answer | Why (shown as feedback) |
|---|---|---|---|---|---|---|---|---|
| 1 | 40 | 10 | 30 | 120 | 6 | 4 | Viper | Plain Python is over the limit; viper and assembly both fit, and viper is the simpler. |
| 2 | 40 | 10 | 30 | 18 | 5 | 3 | Plain Python | Plain Python already fits, so any faster option costs readability for nothing. |
| 3 | 40 | 10 | 30 | 90 | 34 | 12 | Assembly | Viper at 34 ms is over the 30 ms limit; assembly at 12 ms fits. |
| 4 | 40 | 10 | 30 | 200 | 80 | 45 | None fits | Even assembly at 45 ms is over the limit, so the work itself must be reduced. |
| 5 | 20 | 5 | 15 | 60 | 14 | 7 | Viper | Viper at 14 ms is within the 15 ms limit, so assembly is not needed. |
| 6 | 40 | 10 | 30 | 31 | 12 | 9 | Viper | Plain Python at 31 ms is just over the limit of 30 ms; viper at 12 ms fits. |

For exploration the learner sets the budget (10 to 80 ms, step 5, default 40), the reserve (0 to 20 ms, step 5, default 10), and the three times (1 to 300 ms, step 1, defaults 90, 20, 10), and the sim shows which options fit.

**Provenance:** The scenario numbers are illustrative and invented for this activity. The 40 ms budget and 10 ms reserve are the values used in the chapter section "The Real-Time Constraint and the Frame Overrun". The sim labels all times "illustrative, not measured."

**Rules:** limit = budget - reserve. An option fits when its time <= limit. The answer is the first option that fits in the order Plain Python, Viper, Assembly; if none fits the answer is None fits. Budget: min 10, max 80, step 5, default 40, unit ms. Reserve: min 0, max 20, step 5, default 10, unit ms. Times: min 1, max 300, step 1, unit ms.

**Learner Activity:**

1. The learner changes the numbers in the exploration panel and watches which options fit.
2. The learner notices that raising the reserve can make a fitting option stop fitting.
3. The learner starts the 6 scenarios. Scenario 1 is shown.
4. The learner chooses a recommendation and submits.
5. The sim shows the limit, which options fit, the correct answer, and the Why text.

**Feedback:** 6 scenarios, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The exploration panel shows scenario 1's numbers with the limit of 30 ms and the three options marked fits or does not fit, and the question "Which is the simplest option that fits?"

**Chapter Anchors:** The chapter states that the audio work gets 30 ms of the 40 ms frame after a 10 ms display reserve, that the simplest approach that passes timing verification on the worst pass is the right one, and that the numbers in this activity are illustrative.
</details>

## The Results Table

This is the table the chapter is waiting for. **Its measured columns are blank on purpose.** I could not run the scripts on the kit, and I would rather leave a gap than print a number that was not measured. Run the scripts, copy the `RESULT|` lines they print, and fill in the columns. The "predicted" column holds only arithmetic or labelled estimates.

| Row | Code | Script | Predicted (arithmetic or estimate) | Measured ms | Measured cycles | Share of 40 ms |
|-----|------|--------|-----------------------------------|-------------|------------------|----------------|
| 1 | `dsp.fft`, plain lists, 512 points | 02 | at 2,604 cycles per butterfly it fills the frame; the real figure is unknown | to be measured | to be measured | to be measured |
| 2 | `dsp.fft`, `array('f')` | 02 | same | to be measured | to be measured | to be measured |
| 3 | Whole pure-Python pipeline (load, FFT, magnitudes, bands) | 02 | dominated by the FFT | to be measured | to be measured | to be measured |
| 4 | Window 512 samples, Python on lists | 04 | no prediction | to be measured | to be measured | to be measured |
| 5 | Window 512 samples, Python on `array('h')` | 04 | no prediction | to be measured | to be measured | to be measured |
| 6 | Window 512 samples, `@viper` | 04 | between rows 5 and 7 | to be measured | to be measured | to be measured |
| 7 | Window 512 samples, `@asm_thumb` | 04 | estimate 51 to 85 us (7,700 to 12,800 cycles) | to be measured | to be measured | to be measured |
| 8 | `fft_q15` viper FFT, 512 points | 05 | no prediction | to be measured | to be measured | to be measured |
| 9 | Whole viper pipeline | 05 | no prediction | to be measured | to be measured | to be measured |
| 10 | Assembly FFT (stretch exercise) | none | paper estimate about 0.92 ms if 60 cycles per butterfly | not written | not written | not written |
| 11 | Live loop, pure Python: worst pass, overruns | 06 | expected to fail | to be measured | to be measured | to be measured |
| 12 | Live loop, viper: worst pass, overruns | 06 | the aim is a pass | to be measured | to be measured | to be measured |
| 13 | Second core: ratios A to D | 07 | C near 100%, D slower (expectation) | to be measured | | |

When rows 1 to 12 are filled in, the chapter's story can be checked: whether the plain-Python FFT really overruns the frame, how much of the speed-up viper delivers, and whether the viper pipeline passes timing verification with the display reserve. If a row surprises you, the surprise is the useful result: report it.

## Putting It All Together

Real-time audio on the Pico is a budget problem. You have 6,000,000 cycles per 40 ms frame and a pipeline whose FFT alone is 2,304 butterflies. You measure with `ticks_us` or the DWT cycle counter, using the best of several runs; you profile to find the loop that matters; and you verify the finished loop by its worst pass, not its average. Then you spend effort in order of cost: remove allocation and floats from the hot loop, use typed arrays and pre-allocated buffers, precompute the tables, move the one dominant loop into viper with fixed-point arithmetic, and only if that is still not enough consider assembly or the second core.

Key takeaways:

- A real-time constraint is a deadline: 40 ms and 6,000,000 cycles per frame; a frame overrun is a pass that takes longer than one frame, and the backlog it creates eventually loses audio.
- Measure first with the best of several runs; the DWT cycle counter (DEMCR bit 24, DWT_CTRL bit 0, CYCCNT at 0xE0001004) is unverified on the RP2350, and `01-cycle-counter.py` checks it; `ticks_cpu()` is microseconds on this port.
- Profile to find where time goes, and verify timing by the worst pass with a reserve for the display.
- A float result is a heap object; a small integer is not. Typed arrays store numbers packed, pre-allocated buffers avoid garbage, and precomputed tables turn thousands of trigonometric calls per second into lookups.
- Q15 fixed-point stores a fraction as an integer over 32768; multiply, then shift right by 15; watch for overflow, and halve at each FFT stage.
- Viper compiles a typed function to machine code, passes arrays by address, has unsigned `ptr16` reads and no bounds checking.
- Inline assembly gives you instructions and registers (`r0` to `r3` arguments, `r0` returned) at the price of safety and portability; an assembly FFT is a stretch exercise.
- A second core runs truly in parallel but shares one heap; keep all I2S, SPI, and pin work on core 0.
- Use the simplest approach that keeps the worst pass inside the budget; the results table is yours to fill in.

Test yourself with these questions, and click each one to reveal its answer.

??? question "A loop averages 25 ms per pass but once in a while takes 55 ms. Does it meet a 40 ms deadline? Click to expand"
    No. The average does not matter for a deadline; the 55 ms pass is an overrun, and the backlog it adds eventually loses audio. Find out what causes the long pass (often a garbage collection), and verify timing by the worst pass.

??? question "A viper function reads a signed 16-bit sample with `ptr16` and gets 65535. What is the value, and how do you fix the code? Click to expand"
    The stored value is -1: `ptr16` reads are unsigned, so -1 comes back as 65535. Subtract 65536 when the value is 32768 or more, as `window_viper` does.

??? question "You have a 512-point FFT with 2,304 butterflies and want it to use at most 10 ms. How many cycles may one butterfly take at 150 MHz? Click to expand"
    10 ms is 1,500,000 cycles. Divided by 2,304 butterflies that is about 651 cycles per butterfly, or 4.3 microseconds.

!!! mascot-celebration "Faster, and Proven"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned to benchmark and profile against the 40 ms frame budget, remove allocation, use typed arrays and Q15 fixed-point math, write a viper function, read inline assembly, and choose a speed-up by its trade-offs. Fill in the results table and you will know, with numbers, which version of your pipeline keeps up.

In the next chapter we calibrate the microphone and build push-to-talk.
