---
title: "Agent Data Flow Step-Through"
description: "The learner will explain which of three parts (terminal, network, server) performs each of the eight steps that carry a spoken question to a spoken answer, by predicting the owner of steps 2 to 8 with at least 6 of 7 correct."
status: scaffold
library: p5.js
bloom_level: Understand
---

# Agent Data Flow Step-Through



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md).

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

## Related Resources

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md)
