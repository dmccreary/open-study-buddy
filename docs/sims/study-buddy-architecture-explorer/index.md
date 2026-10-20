---
title: "Study Buddy Architecture Explorer"
description: "The learner will identify the job of each of the five kit parts and of the buddy server by matching six described jobs to the correct part, with at least 5 of 6 correct."
status: scaffold
library: vis-network
bloom_level: Remember
---

# Study Buddy Architecture Explorer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md).

```text
Type: graph-model
**sim-id:** study-buddy-architecture-explorer<br/>
**Library:** vis-network<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/bioinformatics/tree/main/docs/sims/profile-hmm-architecture<br/>
**Bloom Level:** Remember<br/>
**Bloom Verb:** identify<br/>
**Learning Objective:** The learner will identify the job of each of the five kit parts and of the buddy server by matching six described jobs to the correct part, with at least 5 of 6 correct.

**Prerequisites:** Open Study Buddy device, agent terminal, buddy server, and the five kit parts (all defined in the section "The Open Study Buddy Device" above this block).

**Evidence of Mastery:** In quiz mode the sim shows one job description and the learner clicks the part that does that job. A click is correct when it matches the Correct part column in Content. Mastery is 5 of 6 correct on the first attempt. Hovering and clicking in explore mode is exploration, not evidence.

**Misconceptions:** (1) The speaker and the amplifier are the same thing. (2) The buddy server is part of the desk device. (3) The Pico sends sound straight to the display.

**Instructional Rationale:** Remember-level identification needs retrieval, so the learner first explores each part and then retrieves the matching part from a job description. Showing the connections reveals which parts talk to the Pico and which talk across the network, which is the structure the chapter describes.

**Content:**

Six nodes, in two groups. The group "Agent terminal (the desk device)" contains five nodes, and the group "School network" contains one node. Each node shows this text when hovered or clicked:

| Node | Group | Job text revealed |
|---|---|---|
| Raspberry Pi Pico 2 W | Agent terminal | Runs the terminal program, reads the microphone and buttons, drives the display and speaker, and talks to the buddy server over Wi-Fi. |
| Round color display | Agent terminal | Shows the clock, the agent's words, and status as a 360 by 360 pixel round picture. |
| INMP441 microphone | Agent terminal | Turns sound into digital numbers that the Pico can read. |
| MAX98357A amplifier and speaker | Agent terminal | Turns digital audio numbers into sound that the student hears. |
| Mode, Up, and Down buttons | Agent terminal | Let the student change modes, move through menus, and adjust values by hand. |
| Buddy server | School network | Receives requests, decides on a reply, and sends it back. It runs on a school computer and is not part of the desk device. |

Five edges. The meaning of each edge is shown when either of its two nodes is selected:

| From | To | Meaning |
|---|---|---|
| INMP441 microphone | Raspberry Pi Pico 2 W | Sends digital sound numbers to the Pico. |
| Mode, Up, and Down buttons | Raspberry Pi Pico 2 W | Send button presses to the Pico. |
| Raspberry Pi Pico 2 W | Round color display | Sends text and pictures to show. |
| Raspberry Pi Pico 2 W | MAX98357A amplifier and speaker | Sends digital audio numbers to play. |
| Raspberry Pi Pico 2 W | Buddy server | Sends requests and receives replies over Wi-Fi on the school network. |

Quiz questions, in this fixed order:

| # | Job description shown | Correct part |
|---|---|---|
| 1 | Turns sound into digital numbers. | INMP441 microphone |
| 2 | Turns digital audio numbers into sound the student hears. | MAX98357A amplifier and speaker |
| 3 | Shows the clock and the agent's words as a round picture. | Round color display |
| 4 | Runs the terminal program and connects to Wi-Fi. | Raspberry Pi Pico 2 W |
| 5 | Lets the student change modes and adjust values by hand. | Mode, Up, and Down buttons |
| 6 | Decides on a reply and sends it back, from a school computer. | Buddy server |

**Provenance:** From the chapter section "The Open Study Buddy Device" and the table of five kit parts there. The sim labels the quiz wording "written for this sim".

**Rules:** A quiz answer is correct when the clicked node equals the Correct part. The score is the number of correct answers, from 0 to 6. Selecting a node in explore mode highlights that node and every edge connected to it.

**Learner Activity:**

1. In explore mode, the learner hovers or clicks each of the six nodes to read its job text.
2. The learner selects a node and sees its connected edges and their meanings.
3. The learner answers the question: "Which part must the Pico talk to over Wi-Fi?" (answer: the buddy server).
4. The learner switches to quiz mode and clicks the matching part for each of the six job descriptions.
5. After question 6 the sim shows the score and lists each missed part with its job text.

**Feedback:** Six questions, fixed order, one attempt per question. Correct: "Correct: <job text>". Incorrect: "Not quite. The part that does this is <correct part>: <job text>". The correct part is revealed immediately after each answer, and a running score "n of 6" is shown.

**Starting State:** All six nodes and five edges are visible with no node selected, in explore mode, with the instruction "Click a part to learn its job."

**Chapter Anchors:** The device has five groups of parts. The buddy server is not part of the desk device. The terminal talks to the buddy server over Wi-Fi on the school network.
```

## Related Resources

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md)
