---
title: "Study Buddy Architecture Explorer"
description: "The learner will identify the job of each of the five kit parts and of the buddy server by matching six described jobs to the correct part, with at least 5 of 6 correct."
status: built
library: vis-network
bloom_level: Remember
image: /sims/study-buddy-architecture-explorer/study-buddy-architecture-explorer.png
og:image: /sims/study-buddy-architecture-explorer/study-buddy-architecture-explorer.png
twitter:image: /sims/study-buddy-architecture-explorer/study-buddy-architecture-explorer.png
social:
   cards: false
---

# Study Buddy Architecture Explorer

<iframe src="main.html" width="100%" height="622px" scrolling="no"></iframe>

[Run the Study Buddy Architecture Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/study-buddy-architecture-explorer/main.html" width="100%" height="622px" scrolling="no"></iframe>
```

## Description

The Open Study Buddy device on your desk is an **agent terminal**: it gives the
agent ears, a voice, and a face, but not its brain. The brain is the
**buddy server**, which runs on a school computer and is not part of the desk
device. This MicroSim shows the five kit parts of the terminal and the buddy
server as a network diagram in two groups, "Agent terminal (the desk device)"
and "School network".

In **Explore** mode, hover over or click a part to read its job. Clicking a part
also highlights every connection to it and lists what travels along each one.
Notice that four parts connect only to the Pico, and only the Pico connects to
the buddy server, over Wi-Fi.

In **Quiz** mode, the sim shows one job description at a time and you click the
part that does that job. The correct part turns green, a wrong click turns
orange, and the feedback repeats the part's job.

## How to Use

1. Start in **Explore**. Hover over a part to read its job, then click it to see its
   connections.
2. Answer the **Check yourself** question: which part must the Pico talk to over
   Wi-Fi? Press **Show answer** to check.
3. Press **Quiz**. Read the job description and click the matching part in the
   diagram. Each question gets one attempt.
4. Press **Next question** after each answer. After question 6, press
   **See results** to see your score and any missed parts.
5. Press **Restart quiz** to try again, or **Explore** to go back to exploring.

Mastery is 5 of 6 correct on the first attempt. Quiz mode hides the job text on
hover, so the quiz measures what you remember.

When the page is opened full screen, you can also drag and zoom the diagram.
Inside the textbook page, use the navigation buttons at the bottom of the diagram.

## Lesson Plan

### Learning Objective

Students will identify the job of each of the five kit parts and of the buddy
server by matching six described jobs to the correct part, with at least 5 of 6
correct (Bloom's Taxonomy: Remember, verb *identify*).

### Prerequisites

Students should have read the chapter section
[The Open Study Buddy Device](../../chapters/01-personal-agents-architecture/index.md#the-open-study-buddy-device),
including the table of five kit parts.

### Activities

1. **Explore (5 minutes).** Students click each of the six parts and read its job and
   connections.
2. **Check yourself (1 minute).** Students answer the Wi-Fi question before pressing
   **Show answer**.
3. **Quiz (4 minutes).** Students complete the six-question quiz without switching back
   to Explore.
4. **Trace a request (5 minutes).** Starting at the microphone, students name every part
   a spoken question passes through until the answer comes out of the speaker.

### Discussion Questions

1. Why does the speaker need an amplifier? What would happen if the Pico tried to
   drive the speaker directly?
2. The buddy server is not part of the desk device. What are two benefits of putting
   the brain on a separate computer?
3. Which single part would you replace to upgrade the agent's brain? Which parts
   would stay the same?

### Common Misconceptions Addressed

- *The speaker and the amplifier are the same thing.* The node is named "MAX98357A
  amplifier and speaker" because the amplifier turns digital audio numbers into sound
  that the speaker plays.
- *The buddy server is part of the desk device.* It sits in the separate "School
  network" group.
- *The Pico sends sound straight to the display.* The Pico sends text and pictures to
  the display and audio numbers to the speaker.

### Assessment

A student who scores 5 or 6 on the quiz has met the objective. For students below 5,
the results screen lists each missed part with its job text for review.

## References

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md)
- [Raspberry Pi Pico series](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) documentation from Raspberry Pi
- [I²S](https://en.wikipedia.org/wiki/I%C2%B2S) on Wikipedia
- [vis-network documentation](https://visjs.github.io/vis-network/docs/network/)

## Specification

The specification below is extracted from
[Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md).

<details markdown="1">
<summary>Show the full specification</summary>

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

</details>
