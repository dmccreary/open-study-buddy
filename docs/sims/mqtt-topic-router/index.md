---
title: "MQTT Topic Router"
description: "The learner will apply the \"+\" and \"#\" wildcard rules to decide which of 7 subscription filters select each of 8 topics, with at least 7 of the 8 selections exactly right."
status: scaffold
library: p5.js
bloom_level: Apply
---

# MQTT Topic Router



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 15: MQTT and Push Alerts](../../chapters/15-mqtt-push-alerts/index.md).

```text
Type: microsim
**sim-id:** mqtt-topic-router<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** apply<br/>
**Learning Objective:** The learner will apply the "+" and "#" wildcard rules to decide which of 7 subscription filters select each of 8 topics, with at least 7 of the 8 selections exactly right.

**Prerequisites:** topic, topic level, subscription filter, "+" wildcard, "#" wildcard, topics beginning with "$" (all defined in the section "Topics and How to Name Them" above this block).

**Evidence of Mastery:** For each of the 8 topics, in the fixed order of the Content table, the learner marks which of the filters S1 to S7 select it, then submits. A selection is correct when the marked set equals the Answer column exactly (a missing filter or an extra filter makes it wrong). Mastery is 7 of 8 correct on the first submission of each topic. Typing topics of the learner's own into the exploration box is exploration, not evidence.

**Misconceptions:** (1) "+" matches any number of levels. (2) "school/crhs/#" does not select "school/crhs". (3) "#" selects every topic, including those starting with "$".

**Instructional Rationale:** Applying a rule needs practice on cases that the rule treats differently. Each topic is built to separate two filters that look alike, and the learner commits a set of marks before the answer is shown, so a wrong rule shows up as a wrong set.

**Content:**

The 7 subscription filters, always shown:

| Id | Filter |
|----|--------|
| S1 | school/crhs/alert |
| S2 | school/crhs/class/214/alert |
| S3 | school/crhs/class/+/alert |
| S4 | school/crhs/device/+/status |
| S5 | school/crhs/# |
| S6 | school/+/alert |
| S7 | # |

The 8 topics, in order, with the filters that select each and the reason shown as feedback:

| # | Topic | Answer (filters that select it) | Why (shown as feedback) |
|---|-------|--------------------------------|-------------------------|
| 1 | school/crhs/alert | S1, S5, S6, S7 | S1 is the exact name. S5 and S7 take everything below their prefix. S6's "+" is the one level "crhs". S3 needs a "class" level that is not there. |
| 2 | school/crhs/class/214/alert | S2, S3, S5, S7 | S2 is exact and S3's "+" is the one level "214". S6 fails because "+" can match only one level, and three levels sit between "school" and "alert". |
| 3 | school/crhs/class/lab-130/alert | S3, S5, S7 | S3's "+" matches "lab-130". S2 names room 214 only. |
| 4 | school/crhs/device/desk-07/status | S4, S5, S7 | S4's "+" matches "desk-07". S3 fails on "device" versus "class". |
| 5 | school/crhs/device/desk-07/telemetry | S5, S7 | S4 needs the last level to be "status". Only the "#" filters take it. |
| 6 | school/trhs/alert | S6, S7 | S6's "+" matches "trhs". S1 and S5 name "crhs". |
| 7 | school/crhs | S5, S7 | "#" matches its parent level too, so "school/crhs/#" selects "school/crhs". |
| 8 | $SYS/broker/uptime | none | A filter that starts with a wildcard does not select a topic that starts with "$". |

**Provenance:** The scheme and the 7 filters come from the chapter section "Topics and How to Name Them" and from `src/chapters/15-mqtt-push-alerts/01-topic-matcher.py`, whose answers were written by hand and agree with the MQTT 3.1.1 specification's rules and with the paho-mqtt matcher.

**Rules:** Split a filter and a topic at "/" into levels. A filter level equal to "+" matches exactly one topic level, of any text, including empty text. A filter level equal to "#" is valid only as the last level and matches the topic's remaining levels, including none. Any other filter level must equal the topic level exactly, with case mattering. Without "#", the filter and the topic must have the same number of levels. A topic whose first level starts with "$" is not selected by a filter whose first level is "+" or "#".

**Learner Activity:**

1. The learner reads the 7 filters, then types one topic of their own into the exploration box. The sim lists which filters select it and highlights the levels that matched, so the learner can try "school/crhs" or "$SYS/x" freely.
2. The learner starts the 8 topics. Topic 1 is shown with the 7 filters unmarked.
3. The learner marks the filters that they think select the topic and submits.
4. The sim shows the correct set, the levels each filter matched, and the Why text. The learner moves to the next topic.
5. After topic 8, the sim shows the score. The learner should notice that topics 5 and 7 are the two that most often cost a point.

**Feedback:** 8 topics, fixed order, one submission each. Correct: "Correct: <Why>". Incorrect: "Not quite. The filters that select it are <answer>: <Why>", naming each filter that was wrongly marked or missed. The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** The 7 filters are shown with the exploration box empty and the question "Which subscribers would receive a message on this topic?"

**Chapter Anchors:** The chapter's table of 8 topics against filters S1 to S7 has the same answers. The chapter states that "school/crhs/#" selects "school/crhs", that "#" does not select "$SYS/broker/uptime", and that "+" matches exactly one level.
```

## Related Resources

- [Chapter 15: MQTT and Push Alerts](../../chapters/15-mqtt-push-alerts/index.md)
