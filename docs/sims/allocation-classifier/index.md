---
title: "Allocation Classifier"
description: "Sort 12 MicroPython statements by whether they allocate heap memory, from small integers to buffer writes and string joins."
status: built
library: p5.js
bloom_level: Analyze
image: /sims/allocation-classifier/allocation-classifier.png
og:image: /sims/allocation-classifier/allocation-classifier.png
twitter:image: /sims/allocation-classifier/allocation-classifier.png
social:
   cards: false
quality_score: 95
---

# Allocation Classifier

<iframe src="main.html" width="100%" height="482px" scrolling="no"></iframe>

[Run the Allocation Classifier MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/allocation-classifier/main.html" width="100%" height="482px" scrolling="no"></iframe>
```

## Description

In MicroPython, a statement allocates heap memory when it creates a new object that is not a small integer. Small integers (from -2**30 to 2**30 - 1 on the Pico's 32-bit port) live inside the value itself, and storing into an existing buffer never allocates. Everything else (floats, slices, lists, tuples, strings, big integers) creates garbage that the collector must clean up later.

This MicroSim shows twelve statements, one at a time. You choose Allocates or Does not allocate; the sim then shows either the new object appearing on the heap or the existing value or buffer that was written, with the reason. After statement 12 it lists the statements you got wrong. The answers are predictions from the MicroPython object model for the Pico's 32-bit port, labeled "expected" until `03-allocation-and-floats.py` has been run on the kit.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Allocates / Does not allocate**: Choose your answer. One attempt per statement.
- **Next statement / See results**: Move on after the feedback.
- **Start over**: Return to statement 1 with a fresh score.

## Lesson Plan

### Learning Objective

The learner will distinguish 12 MicroPython statements that allocate heap memory from those that do not, with at least 10 of 12 correct.

**Bloom's Taxonomy level:** Analyze (distinguish)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

heap, garbage collection, small integer, float object, typed array, pre-allocated buffer, memoryview (defined in Chapter 2 and in this chapter above the block).

### Activities

1. **Exploration (5 min):** Read the rule at the top of this page, then predict statements 1 and 2 aloud before choosing.
2. **Guided practice (5 min):** After each wrong answer, name the object that was created (or the buffer that was written) before moving on.
3. **Assessment (5 min):** Complete all twelve statements. Mastery is 10 of 12 correct on the first attempt.

### Common Misconceptions Addressed

(1) Any arithmetic is free. (2) A slice never copies. (3) Floats are stored inside the value, like small integers. (4) Writing into an array allocates.

### Discussion Questions

1. What do all the statements that do not allocate have in common?
2. A memoryview slice copies no data. Why does it still allocate?
3. Why would statement 11 give a different answer on a 64-bit computer?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 10</summary>

```text
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
```

</details>

## References

1. [Maximising MicroPython speed](https://docs.micropython.org/en/latest/reference/speed_python.html) - MicroPython documentation - Avoiding allocation in fast code.
2. [MicroPython on microcontrollers](https://docs.micropython.org/en/latest/reference/constrained.html) - MicroPython documentation - The heap, garbage collection and pre-allocated buffers.
3. [Garbage collection (computer science)](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science)) - Wikipedia - Why freeing objects costs time.

## Related Resources

- [Chapter 10: High-Performance MicroPython](../../chapters/10-high-performance-micropython/index.md)
