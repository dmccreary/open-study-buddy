---
title: "Chatbot or Agent Sorter"
description: "The learner will distinguish chatbot behaviors from personal-agent behaviors by classifying 10 described behaviors, with at least 8 of 10 correct on the first attempt."
status: built
library: p5.js
bloom_level: Analyze
image: /sims/chatbot-or-agent-sorter/chatbot-or-agent-sorter.png
og:image: /sims/chatbot-or-agent-sorter/chatbot-or-agent-sorter.png
twitter:image: /sims/chatbot-or-agent-sorter/chatbot-or-agent-sorter.png
social:
   cards: false
---

# Chatbot or Agent Sorter

<iframe src="main.html" width="100%" height="564px" scrolling="no"></iframe>

[Run the Chatbot or Agent Sorter MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/chatbot-or-agent-sorter/main.html" width="100%" height="564px" scrolling="no"></iframe>
```

## Description

A chatbot answers one message at a time. A personal agent uses tools, works in
several steps, acts without being asked at that moment, and comes back for a
decision before it changes something that affects you. This MicroSim turns that
definition into ten quick decisions.

Each card describes one illustrative behavior, such as "Tells a joke when asked"
or "Sends an alert to the student's desk device when a test is one day away."
You sort it into **Chatbot behavior** or **Agent behavior**. The sim tells you
right away whether you were right and gives a one-sentence reason that names
the trait involved. Each answered behavior becomes a numbered chip in its
correct bin: green when you sorted it correctly, orange when you missed it.

After the tenth behavior, a summary shows your score and lists every behavior
you missed, with its correct bin and the reason.

## How to Use

1. Read the behavior on the card.
2. Press **Chatbot behavior** or **Agent behavior**. Each behavior gets one attempt.
3. Read the feedback, then press **Next**. **Next** stays disabled until you choose a bin.
4. After behavior 10, press **See results** to see your score and the behaviors you missed.
5. Press **Restart** to practice the same ten behaviors in a new random order.

The first run uses a fixed order and is the only run that counts toward mastery.
Mastery is 8 of 10 correct.

## Lesson Plan

### Learning Objective

Students will distinguish chatbot behaviors from personal-agent behaviors by
classifying 10 described behaviors, with at least 8 of 10 correct on the first
attempt (Bloom's Taxonomy: Analyze, verb *distinguish*).

### Prerequisites

Students should have read the chapter section
[What Is a Personal Agent?](../../chapters/01-personal-agents-architecture/index.md#what-is-a-personal-agent),
which defines personal agent, chatbot, tool, and multi-step work.

### Activities

1. **Warm-up (2 minutes).** Ask students to name one app that "talks" to them.
   Is it a chatbot or an agent? Record their guesses without correcting them.
2. **First run (5 minutes).** Students complete the sorter individually. The first
   run is their evidence of mastery, so they should not restart before finishing.
3. **Rule check (5 minutes).** For each missed behavior, students write which of
   the four agent signs it shows or lacks: uses a tool to act, works in more than
   one step, acts without being prompted at that moment, or asks for approval
   before acting.
4. **Practice run (3 minutes).** Students press **Restart** and sort the shuffled
   behaviors again.

### Discussion Questions

1. Behaviors 3 and 4 both involve talking. Why is one a chatbot behavior and the
   other an agent behavior?
2. Many agents contain a chatbot-style language model inside. Does that make every
   agent a chatbot? Use the chapter's test: does it only reply, or does it act?
3. Which of the agent behaviors would you want your Study Buddy to ask permission
   for first? Why?

### Common Misconceptions Addressed

- *Any program that talks is an agent.* Behaviors 1, 7, and 10 talk but take no action.
- *A chatbot that sounds smart is an agent.* Rewriting or summarizing pasted text is
  still one request and one reply.
- *An agent must be a robot or a physical device.* Behavior 6 is software acting on a
  schedule.

### Assessment

A student who scores 8 or more on the first run has met the objective. For students
below 8, review the missed-behavior list together and ask them to explain each
reason in their own words before a practice run.

## References

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md)
- [Software agent](https://en.wikipedia.org/wiki/Software_agent) on Wikipedia
- [Chatbot](https://en.wikipedia.org/wiki/Chatbot) on Wikipedia

## Specification

The specification below is extracted from
[Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md).

<details markdown="1">
<summary>Show the full specification</summary>

```text
Type: microsim
**sim-id:** chatbot-or-agent-sorter<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/conversational-ai/tree/main/docs/sims/chat-interface-anatomy<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** distinguish<br/>
**Learning Objective:** The learner will distinguish chatbot behaviors from personal-agent behaviors by classifying 10 described behaviors, with at least 8 of 10 correct on the first attempt.

**Prerequisites:** personal agent, chatbot, tool, multi-step work (all defined in the section "What Is a Personal Agent?" above this block).

**Evidence of Mastery:** For each of the 10 behaviors, the learner commits to one of two bins, "Chatbot behavior" or "Agent behavior". A classification is correct when it matches the Correct bin column in Content. Mastery is 8 of 10 correct. Reading a behavior without committing is not evidence.

**Misconceptions:** (1) Any program that talks is an agent. (2) A chatbot that sounds smart is an agent. (3) An agent must be a robot or a physical device.

**Instructional Rationale:** Analyze-level distinguishing requires the learner to apply the three traits to new cases rather than recite them. A forced two-way choice on concrete behaviors makes the learner decide which trait is present, and the one-sentence reason after each answer names the trait.

**Content:**

The learner sees the behaviors one at a time in this fixed order:

| # | Behavior shown to the learner | Correct bin | Why (shown as feedback) |
|---|---|---|---|
| 1 | Answers one typed question, then waits for the next message. | Chatbot behavior | It replies to a single message and takes no further action. |
| 2 | Reads the school calendar, finds a test, and adds a reminder for the night before. | Agent behavior | It uses a tool and acts in several steps without being asked for each one. |
| 3 | Explains what a "TEST:" event is when asked, with no access to any calendar. | Chatbot behavior | It gives information only and takes no action for the person. |
| 4 | Asks "Should I move your study session to 6 pm?" before changing the schedule. | Agent behavior | It comes back for a decision before an action that affects the person. |
| 5 | Rewrites a paragraph that the student pastes in. | Chatbot behavior | One request produces one reply, and the work ends there. |
| 6 | Checks every morning for new due dates and announces them. | Agent behavior | It acts on its own over time on the person's behalf. |
| 7 | Tells a joke when asked. | Chatbot behavior | It produces a reply only. |
| 8 | Sends an alert to the student's desk device when a test is one day away. | Agent behavior | It takes an action through a tool, without being asked at that moment. |
| 9 | Remembers that the student prefers 7 pm reminders and schedules the next reminder for 7 pm. | Agent behavior | It uses what it remembers to take an action on the person's behalf. |
| 10 | Summarizes a news article that the student pastes in. | Chatbot behavior | One request produces one reply, and no action follows. |

**Provenance:** Illustrative behaviors written for this sim from the chapter section "What Is a Personal Agent?". The sim labels them "illustrative".

**Rules:** A behavior belongs in "Agent behavior" when it includes at least one of these: it uses a tool to take an action, it works in more than one step, it acts without being prompted at that moment, or it asks for approval before an action. Otherwise it belongs in "Chatbot behavior". The score is the count of correct classifications, from 0 to 10.

**Learner Activity:**

1. The learner reads behavior 1 and chooses a bin.
2. The sim shows whether the choice was correct and the reason from the Why column, then the learner continues to the next behavior.
3. After behavior 10, the sim shows the score and lists each missed behavior with its reason.
4. The learner can restart with the same 10 behaviors in a new random order. Only the first run counts as evidence.

**Feedback:** Ten items, fixed order on the first run, one attempt per item. Correct: "Correct: <Why>". Incorrect: "Not quite: <Why>". The correct bin is revealed immediately after each answer. A running score "n of 10" is shown after every answer.

**Starting State:** Behavior 1 is shown with the two bins and the question "Is this a chatbot behavior or an agent behavior?"

**Chapter Anchors:** A chatbot answers one message at a time. An agent uses tools, works in several steps, and comes back when it needs a decision.
```

</details>
