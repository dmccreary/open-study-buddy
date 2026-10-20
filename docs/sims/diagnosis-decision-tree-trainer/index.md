---
title: "Diagnosis Decision Tree Trainer"
description: "The learner will differentiate the likely cause of each of 6 reported kit failures from three other causes in the same decision tree, choosing the correct cause for at least 5 of 6 cases."
status: scaffold
library: p5.js
bloom_level: Analyze
---

# Diagnosis Decision Tree Trainer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 18: Testing, Integration, and Capstone Projects](../../chapters/18-testing-integration-capstones/index.md).

```text
Type: microsim
**sim-id:** diagnosis-decision-tree-trainer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** differentiate<br/>
**Learning Objective:** The learner will differentiate the likely cause of each of 6 reported kit failures from three other causes in the same decision tree, choosing the correct cause for at least 5 of 6 cases.

**Prerequisites:** flat line, backlight, sample rate, frame overrun, wire swap (all defined in the sections of this chapter above this block and in Chapters 4 and 8); the three diagnosis tables in this chapter, whose rows are named M1 to M6, A1 to A7, and D1 to D8.

**Evidence of Mastery:** For each of the 6 cases the learner reads the reported symptoms and chooses one of 4 candidate causes before the decision tree is shown. A choice is correct when it equals the Correct row in Content. Mastery is 5 of 6 correct on the first attempt. Walking the tree by answering its questions in exploration is not evidence.

**Misconceptions:** (1) Any failure of the microphone means the microphone is broken. (2) A program that runs without an error has no wiring fault. (3) A dark screen is always a software bug. (4) The answer to a distorted sound is always to lower the volume.

**Instructional Rationale:** Differentiating at the Analyze level means telling apart causes that produce similar symptoms. Asking the learner to commit to a cause from four candidates, and only then showing the tree that leads to it, makes the learner use the symptom details that separate the candidates.

**Content:**

The sim has three trees, one per symptom: silent microphone (rows M1 to M6), distorted audio (rows A1 to A7), and blank display (rows D1 to D8). A tree is a list of rows. Each row asks a yes-or-no question; yes ends the walk at that row's cause, and no goes to the next row of the same tree. The last row of each tree (M6, A7, D8) has no question and is reached when every earlier answer is no. The rows, with their questions, causes, quick tests, and fixes, are the rows of the three tables in the chapter section "Diagnosing the Three Classic Failures". The questions, in order:

| Row | Question |
|---|---|
| M1 | An error at start, and it says "must be sck+1"? |
| M2 | An error at start, with another message? |
| M3 | No error, but the spread is 0, a flat line? |
| M4 | The loudness barely changes when you talk next to it? |
| M5 | The meter is pinned at the top? |
| A1 | Is the speaker silent, not distorted? |
| A2 | Does it crackle only when loud? |
| A3 | Is the pitch wrong? |
| A4 | Does it stutter or have gaps? |
| A5 | Is the start clicky, or the end cut off? |
| A6 | Is there hiss or buzz even when nothing plays? |
| D1 | Is the screen completely dark, with no light? |
| D2 | Did the program stop with an error before drawing? |
| D3 | Is it lit but only black or random noise? |
| D4 | Is the picture speckled or torn? |
| D5 | Is part of what you drew missing? |
| D6 | Is the picture rotated or mirrored? |
| D7 | Are old letters left over, or is the picture sheared or striped? |

The 6 cases, in this order. Each case lists the 3 other candidate causes, which are rows of the same tree.

| # | Reported symptoms | Correct row | Three other candidates (rows) |
|---|---|---|---|
| 1 | "The microphone test stops at once with: invalid ws (must be sck+1)." | M1 | M3, M4, M5 |
| 2 | "No error. The probe says every sample is 12345 and the spread is 0." | M3 | M1, M4, M6 |
| 3 | "The screen is completely dark. The program runs and prints no errors." | D1 | D2, D3, D4 |
| 4 | "The screen is lit and shows the right picture, but it is speckled, on long wires." | D4 | D3, D5, D7 |
| 5 | "A recording I made plays back higher and faster than I spoke." | A3 | A2, A4, A6 |
| 6 | "The sound stutters. The overrun counter reports many passes longer than 40 ms." | A4 | A1, A3, A5 |

**Provenance:** The causes and tests come from the kit README, the headers of kit tests 05 and 07, `config.py`, and Chapters 2 to 8, as cited in the `source` field of `src/chapters/18-testing-integration-capstones/tools/diagnose.py`. The six cases are illustrative, and the sim labels them "illustrative".

**Rules:** Each case has exactly one correct row. A tree question is answered only yes or no. The candidate order is shuffled for each learner, with a fixed seed per case.

**Learner Activity:**

1. The learner explores one tree: picks a symptom, answers its questions, and reads the cause, test, and fix at the end.
2. The learner starts the 6 cases. Case 1 shows its symptoms and the four candidate causes.
3. The learner chooses a cause and submits.
4. The sim shows the correct cause, then walks the tree for that case, highlighting the questions answered and the cause reached, with the quick test and the fix.
5. After case 6, the sim shows the score. The learner should notice that the cheap early questions rule out whole branches.

**Feedback:** 6 cases, fixed order, one attempt each. Correct: "Correct: <cause text>". Incorrect: "Not quite. The likely cause is <correct cause text>: look at <the symptom detail that separates it from the chosen cause>". The correct cause is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The three symptom names are shown with the question "Which one are you diagnosing?" and no tree open.

**Chapter Anchors:** The chapter names three failures (silent microphone, distorted audio, blank display); states that the microphone tree has rows M1 to M6, the audio tree A1 to A7, and the display tree D1 to D8; that a swapped microphone starts with no error and sends zeros; that the sck+1 rule applies to the microphone and the amplifier; and that BAUDRATE 12,000,000 is the fix for speckle.
```

## Related Resources

- [Chapter 18: Testing, Integration, and Capstone Projects](../../chapters/18-testing-integration-capstones/index.md)
