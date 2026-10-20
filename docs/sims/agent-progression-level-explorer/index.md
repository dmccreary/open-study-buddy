---
title: "Agent Progression Level Explorer"
description: "The learner will differentiate the three agent progression levels by placing 8 abilities at the lowest level where each first appears, with at least 7 of 8 correct."
status: scaffold
library: p5.js
bloom_level: Analyze
---

# Agent Progression Level Explorer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md).

```text
Type: microsim
**sim-id:** agent-progression-level-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/ai-strategy-for-education/tree/main/docs/sims/ai-agent-anatomy<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** differentiate<br/>
**Learning Objective:** The learner will differentiate the three agent progression levels by placing 8 abilities at the lowest level where each first appears, with at least 7 of 8 correct.

**Prerequisites:** rule-based agent, LLM-backed agent, agent tools, agent memory, agent approval rules, open-source agent framework, and the three levels (all defined in the section "The Swappable Brain" above this block).

**Evidence of Mastery:** For each of the 8 abilities, the learner commits to Level 1, Level 2, or Level 3. A placement is correct when it matches the Correct level column in Content. Mastery is 7 of 8 on the first attempt. Comparing the three replies in the second part is exploration, not evidence.

**Misconceptions:** (1) Only Level 3 can use tools. (2) A higher level needs a different terminal. (3) An LLM always gives a correct answer.

**Instructional Rationale:** Analyze-level differentiation requires the learner to tell which capability comes from which kind of brain. Placing each ability on the ladder after predicting, and then comparing the replies of all three levels to the same question, shows that the abilities differ while the request-reply contract stays the same.

**Content:**

The three levels are the values in the chapter table "Agent Progression Levels". The learner sees the abilities one at a time in this fixed order:

| # | Ability shown to the learner | Correct level | Why (shown as feedback) |
|---|---|---|---|
| 1 | Matches the question text against fixed rules a person wrote. | Level 1 | A rule-based server is made of exactly these rules. |
| 2 | Reads events from the school calendar using a tool. | Level 1 | Even the rule-based server calls tools when a rule says to. |
| 3 | Answers a question worded in a way no rule anticipated. | Level 2 | Interpreting free-form wording is what the LLM call adds. |
| 4 | Converts the student's speech to text and the reply back to speech. | Level 2 | Level 2 adds speech-to-text and text-to-speech. |
| 5 | Chooses for itself which tool to call for a new kind of request. | Level 2 | An LLM-backed agent can choose tools instead of following a rule. |
| 6 | Remembers a preferred reminder time between conversations using a ready-made memory feature. | Level 3 | A framework supplies memory so you do not build it yourself. |
| 7 | Asks for approval before a risky action using ready-made approval rules. | Level 3 | A framework supplies approval rules that apply before an action. |
| 8 | Runs a planning loop with tools, memory, and approvals supplied by a published toolkit. | Level 3 | That combination is what an open-source agent framework provides. |

After the eight placements, the learner compares replies. The question is "Do I have anything big coming up this week?" and the learner chooses a level to see its reply:

| Level | Reply shown |
|---|---|
| 1 | "Sorry, I only know about tests and due dates." |
| 2 | "You have a lab report due Thursday and a Biology test on Friday." |
| 3 | "You have a lab report due Thursday and a Biology test on Friday. I can set a reminder for Thursday at 7 pm. Should I?" |

For every level the sim also shows the same request and the same reply shape, with the fields `device`, `kind`, and `text` in the request and `speak`, `show`, and `next_mode` in the reply.

**Provenance:** The levels and the replies come from the chapter sections "Agent Progression Levels" and "The Swappable Brain". The calendar events are illustrative, and the sim labels them "illustrative".

**Rules:** A placement is correct when it equals the Correct level for that ability. The score is the number of correct placements, from 0 to 8. The request and reply fields are identical for all three levels. Only the reply text differs.

**Learner Activity:**

1. The learner reads ability 1 and chooses Level 1, 2, or 3.
2. The sim shows whether it was correct and the Why text, then the learner continues through ability 8.
3. After ability 8, the sim shows the score.
4. The learner chooses a level and reads its reply to the sample question, and does the same for the other two levels.
5. The learner should notice that the request and reply fields never change between levels.

**Feedback:** Eight abilities, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. This first appears at <correct level>: <Why>". The correct level is revealed immediately after each answer, and a running score "n of 8" is shown.

**Starting State:** Ability 1 is shown with the three levels, and the question "At which level does this ability first appear?"

**Chapter Anchors:** There are three levels. Level 1 is about 100 lines and uses no LLM. Level 2 adds speech-to-text, text-to-speech, and one LLM call. Level 3 is an optional open-source agent framework. The terminal and the request-reply contract do not change between levels.
```

## Related Resources

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md)
