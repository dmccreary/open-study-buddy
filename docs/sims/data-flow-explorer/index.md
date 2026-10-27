---
title: "Data Flow Explorer"
description: "Follow a spoken question through eight hops and toggle encryption and server location to see which observers can read the data at each hop."
status: built
library: p5.js
bloom_level: Analyze
image: /sims/data-flow-explorer/data-flow-explorer.png
og:image: /sims/data-flow-explorer/data-flow-explorer.png
twitter:image: /sims/data-flow-explorer/data-flow-explorer.png
social:
   cards: false
quality_score: 95
---

# Data Flow Explorer

<iframe src="main.html" width="100%" height="612px" scrolling="no"></iframe>

[Run the Data Flow Explorer MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/data-flow-explorer/main.html" width="100%" height="612px" scrolling="no"></iframe>
```

## Description

A spoken question travels through eight hops, from the microphone to the device status the broker keeps. At each hop someone can see the data, and two design choices change who: turning network encryption off exposes the network hops to anyone on the Wi-Fi, and moving speech-to-text, the agent and text-to-speech to an outside vendor gives that vendor the question and the reply.

The eight hops are drawn with badges for the observers who can see each one. Clicking a hop shows its row of the chapter table "Tracing One Question": what travels, who can see it, where it is stored and for how long. In explore mode you flip the two settings. In the quiz you count hops for six what-if questions. The visibility matrix is a teaching model, not a measurement of any school.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 6 questions / Back to explore**: Switch between exploring and the quiz.
- **Hops box and Submit**: Type a whole number from 0 to 8. One attempt per question.
- **Next question / See score**: Move on after the feedback.
- **Network encryption on, Services at an outside vendor**: Explore only: the two settings.
- **Show hop menu, or click a hop**: Read that hop's row of the table.

## Lesson Plan

### Learning Objective

The learner will examine the 8 hops of a spoken question under two settings (network encryption on or off, services on the school server or at an outside vendor) and count how many hops each observer can see, answering 6 what-if questions with at least 5 of 6 correct.

**Bloom's Taxonomy level:** Analyze (examine)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

hop, observer, network encryption, school server, outside vendor, broker (all defined in the sections above this block; the broker is defined in Chapter 15 and named in the hop table).

### Activities

1. **Exploration (5 min):** Click hops 1, 2 and 7 and read who can see each, then turn encryption off and look again.
2. **Guided practice (5 min):** For question 6, apply both settings and write the observers of each hop before counting.
3. **Assessment (5 min):** Answer all six questions. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) Only the person who owns the device can see what they say. (2) If the data stays on the Wi-Fi it is private. (3) Moving the services to a vendor changes nothing about who sees the audio. (4) Only the audio is sensitive, not the text.

### Discussion Questions

1. Is data that stays on the Wi-Fi private?
2. What does moving the services to a vendor change about who sees the audio?
3. Is only the audio sensitive, or the text too?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 17</summary>

```text
Type: microsim
**sim-id:** data-flow-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** examine<br/>
**Learning Objective:** The learner will examine the 8 hops of a spoken question under two settings (network encryption on or off, services on the school server or at an outside vendor) and count how many hops each observer can see, answering 6 what-if questions with at least 5 of 6 correct.

**Prerequisites:** hop, observer, network encryption, school server, outside vendor, broker (all defined in the sections above this block; the broker is defined in Chapter 15 and named in the hop table).

**Evidence of Mastery:** For each of the 6 what-if questions the learner types a whole number before the answer is revealed. An answer is correct when it equals the Answer column in Content. Mastery is 5 of 6 correct on the first attempt. Clicking hops and flipping the two settings in exploration is not evidence.

**Misconceptions:** (1) Only the person who owns the device can see what they say. (2) If the data stays on the Wi-Fi it is private. (3) Moving the services to a vendor changes nothing about who sees the audio. (4) Only the audio is sensitive, not the text.

**Instructional Rationale:** Analyze-level examination asks the learner to relate parts of a system to who can reach them. Counting observers across hops under changed settings forces the learner to apply the visibility rules rather than recall one setting's answer, and the what-if questions make the effect of each setting concrete.

**Content:**

The sim shows the 8 hops in order: 1 Microphone to Pico; 2 Pico to server; 3 Speech-to-text; 4 The agent or language model; 5 Text-to-speech; 6 Server to Pico; 7 MQTT alerts; 8 Device status. Clicking a hop shows its row from the table "Tracing One Question" (what travels, who can see it, stored where, kept how long).

There are five observers: Pico, School server admin, Outside vendor, Anyone on the Wi-Fi, and Broker admin and subscribers. The two settings are Network encryption (On by default, or Off) and Services (School server by default, or Outside vendor).

Who can see each hop under the default settings (encryption on, school server):

| Hop | Pico | School server admin | Outside vendor | Anyone on the Wi-Fi | Broker admin and subscribers |
|---|---|---|---|---|---|
| 1 | yes | no | no | no | no |
| 2 | yes | yes | no | no | no |
| 3 | no | yes | no | no | no |
| 4 | no | yes | no | no | no |
| 5 | no | yes | no | no | no |
| 6 | yes | yes | no | no | no |
| 7 | yes | no | no | no | yes |
| 8 | yes | no | no | no | yes |

Changing Network encryption to Off adds "Anyone on the Wi-Fi" to hops 2, 6, 7, and 8. Changing Services to Outside vendor adds "Outside vendor" to hops 3, 4, and 5. Nothing else changes.

The 6 questions, in this order:

| # | Question | Answer | Why (shown as feedback) |
|---|---|---|---|
| 1 | With the default settings, how many hops can anyone on the Wi-Fi read? | 0 | Encryption is on, so the Wi-Fi observer is added to no hop. |
| 2 | With encryption off, how many hops can anyone on the Wi-Fi read? | 4 | Turning encryption off adds that observer to hops 2, 6, 7, and 8. |
| 3 | With services at an outside vendor, how many hops can the outside vendor see? | 3 | The vendor is added to hops 3, 4, and 5: speech-to-text, the agent, and text-to-speech. |
| 4 | With the default settings, how many hops can the school server admin see? | 5 | The admin sees hops 2, 3, 4, 5, and 6, because the server handles all of them. |
| 5 | With the default settings, how many hops can only the Pico see? | 1 | Only hop 1 has the Pico as its single observer. Hops 7 and 8 also reach the broker. |
| 6 | With encryption off and services at an outside vendor, how many hops can at least three different observers see? | 4 | Hops 2, 6, 7, and 8 each have the Pico, one more observer, and the Wi-Fi observer. Hops 3, 4, and 5 have two observers. |

**Provenance:** The hops, observers, and kept times come from the chapter table "Tracing One Question" and from `src/chapters/17-privacy-responsible-listening/tools/data_flow.py`. The visibility matrix is a teaching model written for this sim: the sim labels it "model, not a measurement of any real school."

**Rules:** The answer to each question is the number of hops whose visibility row contains the stated observer (or the stated number of observers) after the two settings are applied. Answers are whole numbers from 0 to 8.

**Learner Activity:**

1. The learner clicks each hop to read what travels, who can see it, and how long it is kept.
2. The learner flips Network encryption and Services and watches which observers appear on which hops.
3. The learner starts the 6 questions. Question 1 is shown with the settings it assumes already applied.
4. The learner types a number and submits.
5. The sim shows the answer, highlights the hops that were counted, and shows the Why text.
6. After question 6, the sim shows the score. The learner should notice that one setting change adds the same observer to several hops at once.

**Feedback:** 6 questions, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The 8 hops are shown in default settings with the question "Who can see hop 2?"

**Chapter Anchors:** The chapter states there are 8 hops; that the hop table is a recommended design and not a measurement; that hop 1 is seen by the Pico only; that turning off encryption exposes the network hops (2 and 6 for questions and replies, 7 and 8 for MQTT); and that an outside vendor sees the speech-to-text, agent, and text-to-speech hops.
```

</details>

## References

1. [Data minimization](https://en.wikipedia.org/wiki/Data_minimization) - Wikipedia - Collecting and keeping less.
2. [Transport Layer Security](https://en.wikipedia.org/wiki/Transport_Layer_Security) - Wikipedia - What network encryption protects.
3. [Family Educational Rights and Privacy Act](https://en.wikipedia.org/wiki/Family_Educational_Rights_and_Privacy_Act) - Wikipedia - US student-privacy law that applies to school data.

## Related Resources

- [Chapter 17: Privacy, Safety, and Responsible Listening](../../chapters/17-privacy-responsible-listening/index.md)
