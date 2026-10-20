---
title: "Agent Hosting Trade-Off Explorer"
description: "The learner will recommend one of three hosting options (cloud agent, self-hosted agent, school-hosted agent) for each of four scenarios and identify the deciding factor, with at least 3 of 4 scenarios fully correct."
status: scaffold
library: p5.js
bloom_level: Evaluate
---

# Agent Hosting Trade-Off Explorer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md).

```text
Type: microsim
**sim-id:** agent-hosting-tradeoff-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Evaluate<br/>
**Bloom Verb:** recommend<br/>
**Learning Objective:** The learner will recommend one of three hosting options (cloud agent, self-hosted agent, school-hosted agent) for each of four scenarios and identify the deciding factor, with at least 3 of 4 scenarios fully correct.

**Prerequisites:** cloud agent, self-hosted agent, school-hosted agent, and the four comparison questions (all defined in the section "Where an Agent Lives" above this block).

**Evidence of Mastery:** For each scenario, the learner first commits to a hosting option and then commits to the deciding factor from four choices. A scenario is fully correct when both choices match the Correct columns in Content. Mastery is 3 of 4 scenarios fully correct. Reading the comparison table is exploration, not evidence.

**Misconceptions:** (1) A cloud agent is always the best choice because it is easiest. (2) Self-hosting is only for experts. (3) Hosting only affects cost, not who sees the data.

**Instructional Rationale:** Evaluate-level recommending requires the learner to weigh criteria against a situation. Choosing the option and then naming the one factor that decides it makes the learner justify the choice, and committing before the table is highlighted prevents simply reading the answer off.

**Content:**

The learner sees the four comparison questions as the factors, labeled A to D:

| Factor | Question |
|---|---|
| A | Who runs the computer? |
| B | Who decides what data it can touch? |
| C | What is the typical cost pattern? |
| D | Who keeps it running? |

The three options and their answers to the four factors are exactly the values in the chapter table "Comparing the Three Hosting Options". The learner sees four scenarios in this fixed order:

| # | Scenario shown to the learner | Correct option | Correct factor | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | A student wants an agent today, with no setup, and the questions contain nothing private. | Cloud agent | D | The vendor keeps it running, so the student has nothing to maintain. |
| 2 | A coding club wants to learn how agents work by reading and changing the agent's code. | Self-hosted agent | A | The club runs the computer, so it can open and change the software. |
| 3 | A school wants every classroom device to announce the school calendar, with the school deciding what is kept. | School-hosted agent | B | One school server serves every device, and the school decides what data it touches. |
| 4 | A family wants an assistant whose audio never leaves their home network. | Self-hosted agent | B | The family decides what data the agent touches, and nothing goes to a vendor. |

**Provenance:** The options and factors come from the chapter section "Where an Agent Lives". The four scenarios are illustrative, written for this sim, and the sim labels them "illustrative".

**Rules:** An option answer is correct when it equals the Correct option for that scenario. A factor answer is correct when it equals the Correct factor. A scenario is fully correct only when both are correct. The score is the number of fully correct scenarios, from 0 to 4.

**Learner Activity:**

1. The learner reads scenario 1 and chooses one of the three options.
2. The learner chooses the deciding factor, A to D.
3. The sim then highlights the matching cells of the comparison table and shows the Why text.
4. The learner continues through scenarios 2 to 4 in the same way.
5. After scenario 4 the sim shows the score and the cells of the comparison table that were decisive in each scenario.

**Feedback:** Four scenarios, fixed order, one attempt for the option and one for the factor. Correct: "Correct: <Why>". Incorrect option: "Not quite: <Why>". Incorrect factor with a correct option: "Right option. The deciding factor is <factor letter and question>: <Why>". The correct answers are revealed after both choices are made. A running count "Scenarios fully correct: n of 4" is shown.

**Starting State:** The comparison table is visible without highlights, scenario 1 is shown, and the question on screen is "Which option would you recommend?"

**Chapter Anchors:** The chapter table "Comparing the Three Hosting Options" has four questions and three options with the exact values used in the Content. The chapter states that a cloud agent is run by a vendor, and that a school-hosted agent is a self-hosted agent run by a school.
```

## Related Resources

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md)
