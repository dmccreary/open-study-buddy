---
title: "Heap Fragmentation Explorer"
description: "The learner will explain why a memory request can fail when enough total memory is free, by predicting the outcome of 6 allocation requests on a fragmented 16-cell heap and choosing the reason."
status: built
library: p5.js
bloom_level: Understand
image: /sims/heap-fragmentation-explorer/heap-fragmentation-explorer.png
og:image: /sims/heap-fragmentation-explorer/heap-fragmentation-explorer.png
twitter:image: /sims/heap-fragmentation-explorer/heap-fragmentation-explorer.png
social:
   cards: false
---

# Heap Fragmentation Explorer

<iframe src="main.html" width="100%" height="517px" scrolling="no"></iframe>

[Run the Heap Fragmentation Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

Place the following line in your website to include this MicroSim in your course:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/heap-fragmentation-explorer/main.html" width="100%" height="517px" scrolling="no"></iframe>
```

## Description

This MicroSim shows an illustrative MicroPython heap as a row of 16 cells.
Objects A to H sit one cell apart, and B, D, F and H are garbage that has not
been collected yet. You predict whether six memory requests succeed or raise
`MemoryError`, and for each failure you choose the reason: there are not
enough free cells in total, or no single gap is big enough.

Every result is computed from the heap picture with the same rule MicroPython's
allocator follows: a request for *n* cells needs *n* free cells **in a row**,
and it takes the first such run from cell 1. The stats line under the heap
shows the free total and the longest free run, so you can see that the two
numbers are not the same thing.

The key idea: MicroPython's garbage collector frees dead objects but never
moves the live ones. Collecting garbage raises the free total from 8 to 12
cells, yet the longest gap only grows from 1 to 3.

## How to Use

1. Read request 1 and the heap state it uses (X or Y).
2. Press **Succeeds** or **MemoryError**. If you choose MemoryError, pick the
   reason: **Not enough free cells in total** or **No single gap is big enough**.
3. The sim tries the allocation. A successful request is shown in orange as a
   trial allocation, which is released before the next request. A failure
   outlines the heap in red.
4. After request 3, press **Collect garbage** to free B, D, F and H and move
   on to state Y for requests 4 to 6.
5. After request 6, press **Finish**, then **Restart** to empty the heap.
   Try **Buffer first, then A to H**, press **Restart** again, and try
   **A to H spaced first, then buffer**.

Each request allows one answer, and the running score is shown as "n of 6".
Mastery is 5 of 6 correct.

## Lesson Plan

### Learning Objective

Students will explain why a memory request can fail when enough total memory
is free, by predicting the outcome of 6 allocation requests on a fragmented
16-cell heap and choosing the reason.

### Warm-Up (3 minutes)

Ask: "If a parking lot has 8 empty spaces scattered around, can a bus that
needs 8 spaces in a row park there?" Collect answers, then connect the parking
lot to the heap.

### Guided Exploration (10 minutes)

1. Students work through all six requests, committing to a prediction and a
   reason before each reveal.
2. Pause after request 3 and ask: "8 cells are free and you asked for 8. Why
   did it fail?"
3. After collecting garbage, have students write down the free total and the
   longest run before and after. Ask why the objects A, C, E and G did not
   slide together.

### Allocation-Order Experiment (5 minutes)

Students restart the heap and run both allocation orders. Ask them to state a
rule for their own MicroPython programs. The expected answer: allocate the
biggest buffers first, at the start of the program.

### Discussion Questions

1. Request 6 fails for a different reason than requests 2, 3 and 5. What is
   the difference?
2. Why does garbage collection not fix fragmentation on MicroPython?
3. Restarting the device clears fragmentation. Why is allocating big buffers
   first a better fix than restarting?

### Assessment

The sim records 6 first-attempt answers. Mastery is 5 of 6 correct. Pressing
Collect garbage and Restart is exploration, not evidence.

## References

1. [Fragmentation (computing)](https://en.wikipedia.org/wiki/Fragmentation_(computing)) -
   Wikipedia overview of external fragmentation, the kind shown in this sim.
2. [Garbage collection (computer science)](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science)) -
   Wikipedia article on how collectors find and free unreachable objects.
3. [MicroPython on microcontrollers: Heap fragmentation](https://docs.micropython.org/en/latest/reference/constrained.html) -
   official MicroPython guidance on fragmentation and allocating large buffers early.

## Related Resources

- [Chapter 2: MicroPython Review for Embedded Systems](../../chapters/02-micropython-review/index.md)

??? note "Original specification"

    Type: microsim
    **sim-id:** heap-fragmentation-explorer<br/>
    **Library:** p5.js<br/>
    **Status:** Specified<br/>
    **Bloom Level:** Understand<br/>
    **Bloom Verb:** explain<br/>
    **Learning Objective:** The learner will explain why a memory request can fail when enough total memory is free, by predicting the outcome of 6 allocation requests on a fragmented 16-cell heap and choosing the reason.

    **Prerequisites:** heap, garbage collection, heap fragmentation, MemoryError (all defined in the section "Memory: The Resource That Runs Out" above this block).

    **Evidence of Mastery:** For each of the 6 requests, the learner predicts "succeeds" or "MemoryError." For a request predicted to fail, the learner also picks the reason from two choices: "not enough free cells in total" or "no single gap is big enough." A request is correct when the prediction matches the Result column and, for failures, the reason matches the Correct reason column. Mastery is 5 of 6 correct on the first attempt. Pressing the collect and restart controls to watch the heap change is exploration, not evidence.

    **Misconceptions:** (1) If the total free memory is large enough, the request succeeds. (2) Garbage collection pushes the remaining objects together. (3) Restarting is the only way to get a big buffer.

    **Instructional Rationale:** An Understand-level explanation needs the learner to connect a failure to its cause. Predicting the outcome and then naming the reason separates "not enough memory" from "no single gap big enough," which is the misconception that makes fragmentation confusing.

    **Content:**

    The heap is a row of 16 cells numbered 1 to 16. Each cell is either free or used. A request for n cells succeeds when some run of n or more consecutive free cells exists, and takes the first such run starting from cell 1.

    State X (the starting heap): cells 1, 3, 5, 7, 9, 11, 13, 15 hold the objects A, B, C, D, E, F, G, H (one cell each). Cells 2, 4, 6, 8, 10, 12, 14, 16 are free. That is 8 free cells in total, and the longest run of free cells is 1.

    State Y (after "Collect garbage" from state X): the objects B, D, F, and H are garbage and are freed. Objects A, C, E, and G stay where they are. Free cells are 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16. That is 12 free cells, and the longest run is 3.

    | # | Heap state | Request (cells) | Result | Correct reason | Why (shown as feedback) |
    |---|---|---|---|---|---|
    | 1 | X | 1 | succeeds | none asked | Any free cell is a gap of at least 1. |
    | 2 | X | 2 | MemoryError | no single gap is big enough | 8 cells are free in total, but every gap is 1 cell wide. |
    | 3 | X | 8 | MemoryError | no single gap is big enough | 8 cells are free in total, which equals the request, but they are not together. |
    | 4 | Y | 3 | succeeds | none asked | Cells 2 to 4 form a run of 3. |
    | 5 | Y | 4 | MemoryError | no single gap is big enough | 12 cells are free, but the longest run is 3. |
    | 6 | Y | 13 | MemoryError | not enough free cells in total | Only 12 cells are free in total. |

    After the six requests, the learner can restart the heap (all 16 cells free) and allocate in the order "one 8-cell buffer, then the eight 1-cell objects A to H." Everything fits. In the opposite order (A to H spaced one cell apart first), the 8-cell buffer fails.

    **Provenance:** The heap size and objects are illustrative, and the sim labels them "illustrative." The statement that MicroPython's collector frees objects but does not move them comes from the chapter section "Heap Fragmentation."

    **Rules:** A request for n cells succeeds when the heap has a run of at least n consecutive free cells, and it takes the lowest-numbered such run. "Collect garbage" frees only the cells of objects marked as garbage and never moves any other object. "Restart" frees all 16 cells.

    **Learner Activity:**

    1. The learner sees state X and reads request 1, then predicts the outcome and, if the prediction is a failure, picks a reason.
    2. The sim attempts the allocation on the heap picture and shows the result and the Why text.
    3. After request 3, the learner presses "Collect garbage" to reach state Y and continues with requests 4 to 6.
    4. After request 6, the learner presses "Restart," then allocates the 8-cell buffer first and the eight objects second, and tries the opposite order.
    5. The learner should notice that collecting garbage increased the free total from 8 to 12 but only grew the longest gap from 1 to 3.

    **Feedback:** 6 requests, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. <Why>". The result is revealed right after each answer, and a running score "n of 6" is shown.

    **Starting State:** State X is shown with request 1 and the question "Will this request succeed?"

    **Chapter Anchors:** The chapter states that the collector frees garbage but does not move remaining objects, and that the practical fix is to allocate the biggest buffers first.
