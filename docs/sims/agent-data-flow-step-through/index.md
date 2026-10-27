---
title: "Agent Data Flow Step-Through"
description: "Step through the eight hops a spoken question takes to become a spoken answer, and predict whether the terminal, network or server does each one."
status: built
library: p5.js
bloom_level: Understand
image: /sims/agent-data-flow-step-through/agent-data-flow-step-through.png
og:image: /sims/agent-data-flow-step-through/agent-data-flow-step-through.png
twitter:image: /sims/agent-data-flow-step-through/agent-data-flow-step-through.png
social:
   cards: false
---

# Agent Data Flow Step-Through

<iframe src="main.html" width="100%" height="582px" scrolling="no"></iframe>

[Run the Agent Data Flow Step-Through MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/agent-data-flow-step-through/main.html" width="100%" height="582px" scrolling="no"></iframe>
```

## Description

When you ask your Study Buddy "When is my next test?", the answer takes eight
steps to reach you, and three different parts do the work: the **terminal** on
your desk, the **network** (Wi-Fi) between the computers, and the **buddy server**
on a school computer. This MicroSim walks through those eight steps one at a time.

Before each of steps 2 to 8 is revealed, you predict which part performs it. The
sim then shows the owner, a one-line description of the step, and the concrete
data at that step, such as the sample sound values (illustrative), the request
fields `device = desk-07` and `kind = question`, the text "when is my next test",
and the reply "Your next test is Biology on Friday." Each revealed step becomes a
numbered chip under the part that performed it, so by the end the steps are
grouped by owner. There is no animation: each step waits for you.

## How to Use

1. Read the previous step and the next job on the card.
2. Predict the part that performs it: press **Terminal**, **Network**, or **Server**.
   Each step gets one prediction.
3. Read the owner, the description, the data, and the feedback. Then press **Next**.
   **Next** stays disabled until you make a prediction.
4. After step 8, press **See summary** to see your score and the steps grouped by owner.
5. Press **Restart** to start again from step 1.

Mastery is 6 of 7 predictions correct. The running score is shown at the top right.

## Lesson Plan

### Learning Objective

Students will explain which of three parts (terminal, network, server) performs
each of the eight steps that carry a spoken question to a spoken answer, by
predicting the owner of steps 2 to 8 with at least 6 of 7 correct (Bloom's
Taxonomy: Understand, verb *explain*).

### Prerequisites

Students should have read the chapter section
[How the Terminal and Server Talk](../../chapters/01-personal-agents-architecture/index.md#how-the-terminal-and-server-talk),
which defines the agent terminal, the buddy server, the request-reply contract,
speech-to-text, and text-to-speech.

### Activities

1. **Predict before you look (8 minutes).** Students step through all eight steps
   individually, committing to a prediction each time.
2. **Explain the pattern (5 minutes).** Using the summary screen, students write one
   sentence explaining why the server owns steps 4, 5, and 6. The word "memory"
   should appear in a good answer.
3. **Trace a new question (5 minutes).** Students write the data at each of the eight
   steps for a different question, such as "When is my lab report due?"

### Discussion Questions

1. The network carries the request in step 3 but never reads it. Why is it useful
   that the Wi-Fi link does not need to understand the question?
2. Which steps would change if the school replaced the brain in step 5 with a
   smarter one? Which steps would stay exactly the same?
3. If your buddy stays silent, which step would you test first, and why?

### Common Misconceptions Addressed

- *The Pico decides the answer.* Step 5 is owned by the server.
- *The microphone sends sound straight to the speaker.* Six steps separate them.
- *The Wi-Fi link understands the question.* Steps 3 and 7 only carry data.

### Assessment

A student who predicts 6 or more of the 7 owners correctly has met the objective.
Ask students below 6 to explain, for each missed step, which part has the needed
memory or hardware.

## References

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md)
- [Speech recognition](https://en.wikipedia.org/wiki/Speech_recognition) on Wikipedia
- [Speech synthesis](https://en.wikipedia.org/wiki/Speech_synthesis) on Wikipedia
- [Client-server model](https://en.wikipedia.org/wiki/Client%E2%80%93server_model) on Wikipedia

## Specification

The specification below is extracted from
[Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md).

<details markdown="1">
<summary>Show the full specification</summary>

```text
Type: microsim
**sim-id:** agent-data-flow-step-through<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/conversational-ai/tree/main/docs/sims/response-generation-architecture<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** explain<br/>
**Learning Objective:** The learner will explain which of three parts (terminal, network, server) performs each of the eight steps that carry a spoken question to a spoken answer, by predicting the owner of steps 2 to 8 with at least 6 of 7 correct.

**Prerequisites:** agent terminal, buddy server, request-reply contract, speech-to-text, text-to-speech (all defined in the section "How the Terminal and Server Talk" above this block).

**Evidence of Mastery:** Before each of steps 2 to 8 is revealed, the learner commits to the part that performs it: Terminal, Network, or Server. A prediction is correct when it matches the Owner column in Content. Mastery is 6 of 7 correct. Pressing Next without predicting is not allowed.

**Misconceptions:** (1) The Pico decides the answer. (2) The microphone sends sound straight to the speaker. (3) The Wi-Fi link understands the question.

**Instructional Rationale:** Understand-level explanation needs the learner to trace the process with concrete data. Step-through with prediction before reveal makes the learner reason about which part has the memory and the job, and the concrete values shown at each step prevent a vague answer. There is no animation, because animation would hide the data at each step.

**Content:**

The scenario is the question "When is my next test?" The learner sees these eight steps in order, with the data shown at each step:

| Step | What happens | Data shown | Owner | Why the owner (shown as feedback) |
|---|---|---|---|---|
| 1 | The student speaks | The spoken words "When is my next test?" | Student | Shown to start the scenario, and not predicted. |
| 2 | The microphone captures sound as digital numbers | Illustrative sample values: 12, -40, 85, 130, 60, -25 | Terminal | The microphone is wired to the Pico, so the terminal captures the sound. |
| 3 | The request travels to the server | The request fields: device = desk-07, kind = question, plus the sound numbers | Network | The Wi-Fi link only carries the request. It does not read or change it. |
| 4 | The server converts speech to text | The text "when is my next test" | Server | Speech-to-text needs more memory than the Pico has, so the server does it. |
| 5 | The brain decides the reply | Event found: "TEST: Biology, Friday". Reply text: "Your next test is Biology on Friday." | Server | The calendar and the decision logic live on the server. |
| 6 | The server converts the reply to speech and packages it | The reply fields: speak = the sentence as audio, show = "Biology test: Friday" | Server | Text-to-speech also needs more memory than the Pico has. |
| 7 | The reply travels back to the terminal | The same reply fields moving from the server to desk-07 | Network | The Wi-Fi link only carries the reply. |
| 8 | The terminal shows and plays the reply | The display shows "Biology test: Friday". The speaker says "Your next test is Biology on Friday." | Terminal | The display and speaker are wired to the Pico, so the terminal outputs the reply. |

**Provenance:** An illustrative scenario written for this sim from the chapter section "How the Terminal and Server Talk". The sample values are illustrative and the sim labels them "illustrative".

**Rules:** There are eight steps and three owners. The prediction applies to steps 2 to 8, which is 7 predictions. A prediction is correct when it equals the Owner of that step. The score is the number of correct predictions, from 0 to 7. The correct owner is always revealed after the prediction, and the data for that step is then shown.

**Learner Activity:**

1. Step 1 is shown. The learner sees the spoken question.
2. For step 2 the learner chooses Terminal, Network, or Server.
3. The sim reveals the correct owner, the step description, and the data shown for that step, with the reason if the prediction was wrong.
4. The learner presses Next and repeats for steps 3 to 8.
5. After step 8, the sim shows a summary that groups the eight steps by owner and shows the score.

**Feedback:** Seven predictions, fixed order, one attempt each. Correct: "Correct: <Owner>. <Why the owner>". Incorrect: "Not quite. The <Owner> does this step. <Why the owner>". The owner is revealed immediately after each prediction. A running score "n of 7" is shown.

**Starting State:** Step 1 is shown with the spoken question, the terminal and the server shown as separate parts, and the question "Which part performs step 2?"

**Chapter Anchors:** There are eight steps. Step 1 is the student's, two steps happen on the terminal (2 and 8), three happen on the server (4, 5, 6), and two happen on the network (3 and 7). The example question is "When is my next test?" and the example reply is "Your next test is Biology on Friday."
```

</details>
