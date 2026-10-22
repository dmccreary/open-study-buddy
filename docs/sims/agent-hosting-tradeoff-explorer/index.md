---
title: "Agent Hosting Trade-Off Explorer"
description: "The learner will recommend one of three hosting options (cloud agent, self-hosted agent, school-hosted agent) for each of four scenarios and identify the deciding factor, with at least 3 of 4 scenarios fully correct."
status: built
library: p5.js
bloom_level: Evaluate
image: /sims/agent-hosting-tradeoff-explorer/agent-hosting-tradeoff-explorer.png
og:image: /sims/agent-hosting-tradeoff-explorer/agent-hosting-tradeoff-explorer.png
twitter:image: /sims/agent-hosting-tradeoff-explorer/agent-hosting-tradeoff-explorer.png
social:
   cards: false
---

# Agent Hosting Trade-Off Explorer

<iframe src="main.html" width="100%" height="667px" scrolling="no"></iframe>

[Run the Agent Hosting Trade-Off Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/agent-hosting-tradeoff-explorer/main.html" width="100%" height="667px" scrolling="no"></iframe>
```

## Description

An agent has to run on a computer somewhere, and where it runs decides who
controls it, what it costs, and who can see your data. The chapter compares
three options, a **cloud agent**, a **self-hosted agent**, and a
**school-hosted agent**, using four questions. This MicroSim asks you to use
that comparison to make recommendations.

You read four illustrative scenarios, such as a coding club that wants to read
and change its agent's code, or a family that wants audio to stay on the home
network. For each one you first recommend a hosting option and then name the
deciding factor, A to D:

- **A.** Who runs the computer?
- **B.** Who decides what data it can touch?
- **C.** What is the typical cost pattern?
- **D.** Who keeps it running?

The comparison table stays on screen but is not highlighted until you have made
both choices. Then the decisive cell is highlighted in gold and the reason is
shown. At the end, the table shows a numbered badge in the decisive cell for each
scenario.

## How to Use

1. Read the scenario on the card.
2. In the first row of buttons, press **Cloud agent**, **Self-hosted agent**, or
   **School-hosted agent**.
3. In the second row, press **A**, **B**, **C**, or **D** for the deciding factor.
   The factor buttons unlock after you choose an option. Each choice gets one attempt.
4. Read the highlighted table cell and the feedback, then press **Next scenario**.
5. After scenario 4, press **See results** to see your score and the decisive cells.
   Press **Restart** to try again.

A scenario counts as fully correct only when both the option and the factor are
correct. Mastery is 3 of 4 scenarios fully correct.

## Lesson Plan

### Learning Objective

Students will recommend one of three hosting options (cloud agent, self-hosted
agent, school-hosted agent) for each of four scenarios and identify the deciding
factor, with at least 3 of 4 scenarios fully correct (Bloom's Taxonomy: Evaluate,
verb *recommend*).

### Prerequisites

Students should have read the chapter section
[Where an Agent Lives](../../chapters/01-personal-agents-architecture/index.md#where-an-agent-lives),
including the table "Comparing the Three Hosting Options".

### Activities

1. **Recommend and justify (8 minutes).** Students complete the four scenarios
   individually.
2. **Defend a choice (7 minutes).** In pairs, students pick the scenario they found
   hardest and argue for a different option. Their partner names the factor that
   rules it out.
3. **Write a scenario (5 minutes).** Each student writes a fifth scenario where
   cost (factor C) is the deciding factor, then swaps with a partner.

### Discussion Questions

1. Scenarios 3 and 4 have the same deciding factor but different options. What
   changes between them?
2. Is a cloud agent ever the right choice? What would have to be true about the
   questions you ask it?
3. A school-hosted agent is a self-hosted agent run by a school. What does a
   student gain and give up when the school runs it?

### Common Misconceptions Addressed

- *A cloud agent is always the best choice because it is easiest.* Scenarios 2 to 4
  favor other options.
- *Self-hosting is only for experts.* Scenario 4 is a family.
- *Hosting only affects cost, not who sees the data.* Factor B decides two of the
  four scenarios.

### Assessment

A student with 3 or 4 scenarios fully correct has met the objective. For students
who chose the right option but the wrong factor, ask them to point to the table
cell that makes the difference.

## References

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md)
- [Cloud computing](https://en.wikipedia.org/wiki/Cloud_computing) on Wikipedia
- [Self-hosting (network)](https://en.wikipedia.org/wiki/Self-hosting_(network)) on Wikipedia

## Specification

The specification below is extracted from
[Chapter 1: Personal Agents and the Open Study Buddy Architecture](../../chapters/01-personal-agents-architecture/index.md).

<details markdown="1">
<summary>Show the full specification</summary>

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

</details>
