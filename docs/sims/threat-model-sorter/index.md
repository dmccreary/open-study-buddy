---
title: "Threat Model Sorter"
description: "The learner will prioritize 10 classroom threats into the correct fix order using each threat's likelihood, impact, and effort to fix, with at least 8 of 10 threats in the correct position."
status: built
library: p5.js
bloom_level: Evaluate
image: /sims/threat-model-sorter/threat-model-sorter.png
og:image: /sims/threat-model-sorter/threat-model-sorter.png
twitter:image: /sims/threat-model-sorter/threat-model-sorter.png
social:
   cards: false
quality_score: 95
---

# Threat Model Sorter

<iframe src="main.html" width="100%" height="622px" scrolling="no"></iframe>

[Run the Threat Model Sorter MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/threat-model-sorter/main.html" width="100%" height="622px" scrolling="no"></iframe>
```

## Description

A threat model lists what could go wrong and decides what to fix first. Here each classroom threat has a likelihood and an impact from 1 to 3, and the risk score is their product. Threats are fixed from the highest score down; equal scores put the cheaper fix first, and a final tie goes to the lower threat number, so the order is unique.

The ten threats are shown in a scrambled order with their ratings. You select a row and move it up or down until the list runs from first to fix to last, then submit once; the sim reveals each threat's score and correct position and explains any misplaced threat. A small example lets you try a likelihood and an impact first. The ratings are reasoned judgments for a classroom, not statistics.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Selected menu, or click a row**: Choose the threat to move.
- **Move up / Move down**: Move the selected threat one place.
- **Submit order**: Submit the whole order once.
- **Start over**: Return to the scrambled order.
- **Example likelihood and impact sliders**: Try a risk score on an example threat.

## Lesson Plan

### Learning Objective

The learner will prioritize 10 classroom threats into the correct fix order using each threat's likelihood, impact, and effort to fix, with at least 8 of 10 threats in the correct position.

**Bloom's Taxonomy level:** Evaluate (prioritize)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

threat model, asset, actor, attack surface, likelihood, impact, risk score, effort to fix (all defined in the section "The Threat Model" above this block).

### Activities

1. **Exploration (5 min):** Use the example sliders to list every possible risk score from 1 to 9.
2. **Guided practice (5 min):** Before arranging, compute every threat's score and group the six threats that tie at 6.
3. **Assessment (5 min):** Submit one order. Mastery is 8 of 10 threats in the correct position.

### Common Misconceptions Addressed

(1) The most technical-sounding threat is always the most important. (2) Likelihood alone decides priority. (3) Equal scores mean the order does not matter. (4) A threat caused by our own bug is not a real threat.

### Discussion Questions

1. Is the most technical-sounding threat always the most important?
2. Why does effort decide the order of the six threats that tie at 6?
3. Is a threat caused by our own bug a real threat?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 17</summary>

```text
Type: microsim
**sim-id:** threat-model-sorter<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Evaluate<br/>
**Bloom Verb:** prioritize<br/>
**Learning Objective:** The learner will prioritize 10 classroom threats into the correct fix order using each threat's likelihood, impact, and effort to fix, with at least 8 of 10 threats in the correct position.

**Prerequisites:** threat model, asset, actor, attack surface, likelihood, impact, risk score, effort to fix (all defined in the section "The Threat Model" above this block).

**Evidence of Mastery:** The learner arranges all 10 threats in order and submits once. A threat is in the correct position when its position equals the Fix position column in Content. Mastery is 8 of 10 in the correct position. Changing the likelihood and impact of the example threat in exploration is not evidence.

**Misconceptions:** (1) The most technical-sounding threat is always the most important. (2) Likelihood alone decides priority. (3) Equal scores mean the order does not matter. (4) A threat caused by our own bug is not a real threat.

**Instructional Rationale:** Prioritizing at the Evaluate level means choosing an order against stated criteria and defending it. Giving the learner the three ratings and one tie-break rule makes the criteria explicit, so the activity checks judgment applied to criteria rather than memory of the table.

**Content:**

The rule: the risk score is likelihood times impact. Threats are ordered by risk score from highest to lowest. Among threats with equal scores, the lower effort comes first. Among threats with equal score and equal effort, the lower threat number comes first.

The 10 threats, shown in this scrambled order, with their ratings (likelihood and impact from 1 to 3, effort from 1 easy to 3 hard):

| Threat | Description | Likelihood | Impact | Effort | Score | Fix position | Why (shown as feedback) |
|---|---|---|---|---|---|---|---|
| T7 | Always-on listening turned on without approval | 1 | 3 | 1 | 3 | 9 | Score 3, effort 1, and its number is lower than T10's, so it comes ninth. |
| T2 | Eavesdropping on an unencrypted HTTP link | 2 | 3 | 2 | 6 | 5 | Score 6 with effort 2: after the three effort-1 threats and T1, before T9. |
| T10 | Someone else's voice triggers the device | 3 | 1 | 1 | 3 | 10 | Score 3 ties with T7 and effort ties too, so the higher number goes last. |
| T4 | secrets.py committed to git | 2 | 3 | 1 | 6 | 2 | Score 6 with effort 1; its number is higher than T3's. |
| T9 | A cloud vendor keeps recordings | 2 | 3 | 3 | 6 | 6 | Score 6 with the highest effort, so it is last of the score-6 group. |
| T1 | Microphone left open with no indicator | 2 | 3 | 2 | 6 | 4 | Score 6 with effort 2: after the effort-1 threats, before T2. |
| T6 | Server logs keep audio or transcripts | 3 | 2 | 1 | 6 | 3 | Score 6 with effort 1; its number is higher than T4's. |
| T5 | Prompt injection in a calendar title | 2 | 2 | 2 | 4 | 7 | Score 4 is below every score-6 threat; effort 2 and number 5 put it before T8. |
| T3 | Exposed MQTT broker | 2 | 3 | 1 | 6 | 1 | Score 6 with effort 1 and the lowest number among them, so it is first. |
| T8 | Lost or stolen device | 2 | 2 | 2 | 4 | 8 | Score 4 and effort 2 tie with T5, so the higher number goes after it. |

**Provenance:** The ratings are the judgments in `src/chapters/17-privacy-responsible-listening/tools/threat_model.py` and the chapter table "The Threat Model". The sim labels them "reasoned judgments for a classroom, not statistics."

**Rules:** Score = likelihood x impact, from 1 to 9. Order by score descending, then effort ascending, then threat number ascending. The correct order is therefore unique. The sim counts how many threats are in the position given in the Fix position column.

**Learner Activity:**

1. The learner explores one example threat and changes its likelihood and impact between 1 and 3; the score updates at once.
2. The learner is shown the 10 threats in the scrambled order and the ordering rule.
3. The learner arranges them from first to fix to last to fix and submits.
4. The sim reveals the correct order, marks each threat as correctly or wrongly placed, and shows the Why text for each wrongly placed threat.
5. The sim shows the score "n of 10". The learner should notice that six threats tie at 6, so effort decided their order.

**Feedback:** One submission of 10 placements. Correct placement: the threat is marked correct. Wrong placement: "Not quite. <Threat> belongs in position <n>: <Why>". The correct order is revealed after the submission, and the score is shown.

**Starting State:** The 10 threats are shown in the scrambled order with their ratings visible and the question "Which threat should you fix first, and why?"

**Chapter Anchors:** The chapter states that the ratings are judgments, that six of the ten threats tie at a score of 6, that effort breaks ties, and that the first three to fix are T3, T4, and T6.
```

</details>

## References

1. [Threat model](https://en.wikipedia.org/wiki/Threat_model) - Wikipedia - Listing assets, actors and attack surfaces.
2. [Risk matrix](https://en.wikipedia.org/wiki/Risk_matrix) - Wikipedia - Likelihood times impact.
3. [Prompt injection](https://en.wikipedia.org/wiki/Prompt_injection) - Wikipedia - One of the ten threats, explained.

## Related Resources

- [Chapter 17: Privacy, Safety, and Responsible Listening](../../chapters/17-privacy-responsible-listening/index.md)
