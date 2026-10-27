---
title: "QoS Handshake Stepper"
description: "Step through MQTT QoS 0, 1 and 2 handshakes with lost packets and count how many copies of an alert the broker processes."
status: built
library: p5.js
bloom_level: Understand
image: /sims/mqtt-qos-handshake-stepper/mqtt-qos-handshake-stepper.png
og:image: /sims/mqtt-qos-handshake-stepper/mqtt-qos-handshake-stepper.png
twitter:image: /sims/mqtt-qos-handshake-stepper/mqtt-qos-handshake-stepper.png
social:
   cards: false
quality_score: 95
---

# QoS Handshake Stepper

<iframe src="main.html" width="100%" height="552px" scrolling="no"></iframe>

[Run the QoS Handshake Stepper MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/mqtt-qos-handshake-stepper/main.html" width="100%" height="552px" scrolling="no"></iframe>
```

## Description

MQTT offers three delivery promises. QoS 0 sends a PUBLISH once and never repeats it. QoS 1 repeats the PUBLISH until a PUBACK comes back, so the broker may process a repeat. QoS 2 uses a four-packet handshake (PUBLISH, PUBREC, PUBREL, PUBCOMP) so the broker processes each packet number exactly once.

The sequence diagram shows one hop from the publisher to the broker. Each step draws one packet; a lost packet is crossed out, and a counter shows how many copies of the alert the broker has processed. In explore mode you step through the no-loss case of each QoS level. In the quiz you predict the number of copies for six scenarios, then step through the packets. The scenarios are illustrative and the model does not reproduce timing.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Start the 6 scenarios / Back to explore**: Switch between exploring and the quiz.
- **Copies processed menu and Submit**: Choose 0, 1 or 2. One attempt per scenario.
- **Next scenario / See score**: Move on after the feedback.
- **QoS menu, Step, Back to start**: Choose the QoS level (explore only) and step through the packets.

## Lesson Plan

### Learning Objective

The learner will infer, for 6 scenarios of a publisher sending one alert to a broker, how many copies of the alert the broker processes, with at least 5 of the 6 inferences right.

**Bloom's Taxonomy level:** Understand (infer)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

publisher, broker, QoS 0, QoS 1, QoS 2, PUBLISH, PUBACK, PUBREC, PUBREL, PUBCOMP, duplicate (all defined in the section "Delivery Promises" above this block).

### Activities

1. **Exploration (5 min):** Step through QoS 0, 1 and 2 with nothing lost and count the packets each needs.
2. **Guided practice (5 min):** Before scenario 5, say which side is waiting for which packet when the PUBACK is lost.
3. **Assessment (5 min):** Complete all six scenarios. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) QoS 0 retries until the message gets through. (2) QoS 1 guarantees exactly one copy. (3) A lost acknowledgement means the message was lost. (4) QoS 2 never sends a packet twice.

### Discussion Questions

1. Does QoS 1 guarantee exactly one copy?
2. Does a lost acknowledgement mean the message was lost?
3. Why do alerts carry an id?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 15</summary>

```text
Type: microsim
**sim-id:** mqtt-qos-handshake-stepper<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** infer<br/>
**Learning Objective:** The learner will infer, for 6 scenarios of a publisher sending one alert to a broker, how many copies of the alert the broker processes, with at least 5 of the 6 inferences right.

**Prerequisites:** publisher, broker, QoS 0, QoS 1, QoS 2, PUBLISH, PUBACK, PUBREC, PUBREL, PUBCOMP, duplicate (all defined in the section "Delivery Promises" above this block).

**Evidence of Mastery:** For each scenario the learner chooses 0, 1, or 2 as the number of copies the broker processes, before the packets are stepped through. A choice is correct when it equals the Answer column. Mastery is 5 of 6 correct on the first choice for each scenario. Stepping through the packets after the answer, and the exploration mode, are not evidence.

**Misconceptions:** (1) QoS 0 retries until the message gets through. (2) QoS 1 guarantees exactly one copy. (3) A lost acknowledgement means the message was lost. (4) QoS 2 never sends a packet twice.

**Instructional Rationale:** Inference at the Understand level requires the learner to reason from the packet sequence to the outcome rather than recall a definition. Committing to a count first, and then stepping through the packets, shows where the extra or missing copy comes from.

**Content:**

The sim shows one hop only, from the publisher to the broker, drawn as two lanes with packets moving between them. The packet sequences when nothing is lost:

| QoS | Packets in order | Who sends each |
|-----|------------------|----------------|
| 0 | PUBLISH | publisher |
| 1 | PUBLISH, PUBACK | publisher, broker |
| 2 | PUBLISH, PUBREC, PUBREL, PUBCOMP | publisher, broker, publisher, broker |

The 6 scenarios, in order. "Lost" means that packet never arrives and the sender never learns why.

| # | Scenario | Answer (copies processed) | Why (shown as feedback) |
|---|----------|---------------------------|-------------------------|
| 1 | QoS 0. Nothing is lost. | 1 | The one PUBLISH arrives and is processed once. |
| 2 | QoS 0. The PUBLISH is lost. | 0 | QoS 0 has no acknowledgement and no repeat, so the alert is gone. |
| 3 | QoS 1. Nothing is lost. | 1 | The PUBLISH arrives, is processed once, and the PUBACK ends the exchange. |
| 4 | QoS 1. The PUBLISH is lost. | 1 | No PUBACK comes back, so the publisher sends the PUBLISH again with the duplicate flag set. That second one arrives and is processed once. |
| 5 | QoS 1. The PUBLISH arrives but the PUBACK is lost. | 2 | The broker already processed the alert, but the publisher sees no PUBACK and sends it again, so the broker processes it a second time. This is why alerts carry an id. |
| 6 | QoS 2. The PUBREC is lost. | 1 | The publisher repeats the PUBLISH, the broker recognizes the packet number and does not process it again, and the handshake continues to PUBCOMP. |

**Provenance:** The packet sequences and the behavior of each QoS level come from the MQTT 3.1.1 specification and the chapter section "QoS Levels". The scenarios are illustrative, and the sim labels them "illustrative". The sim is a model of one hop and does not reproduce timing.

**Rules:** The publisher resends an unacknowledged PUBLISH (QoS 1) or PUBLISH and PUBREL (QoS 2) after a loss, with the duplicate flag set, until the acknowledgement arrives. The broker processes every QoS 1 PUBLISH it receives, including repeats. For QoS 2 the broker processes a packet number once, however many times the PUBLISH arrives. QoS 0 is never resent. In a scenario, exactly one packet is lost, once; the resend then arrives.

**Learner Activity:**

1. The learner opens the exploration mode, chooses QoS 0, 1, or 2, and steps through the packets of the no-loss case one at a time. The sim names each packet and who sent it.
2. The learner starts the 6 scenarios. Scenario 1 is shown with the packet lanes empty.
3. The learner chooses 0, 1, or 2 as the number of copies processed and submits.
4. The sim steps through the scenario's packets, marks the lost one, and shows the Why text.
5. After scenario 6, the sim shows the score. The learner should notice that only one scenario gives more than one copy and that it is the one where the acknowledgement, not the message, was lost.

**Feedback:** 6 scenarios, fixed order, one choice each. Correct: "Correct: <Why>". Incorrect: "Not quite. The broker processes <answer> copy or copies: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The exploration mode is shown with QoS 1 selected and no packets sent, with the question "What will the broker do if an acknowledgement goes missing?"

**Chapter Anchors:** The chapter states that QoS 0 is at most once, QoS 1 is at least once and may deliver a repeat, QoS 2 is exactly once with a four-packet handshake, that `umqtt.simple` supports QoS 0 and 1 only, and that alerts carry an id so repeats can be ignored.
```

</details>

## References

1. [MQTT](https://en.wikipedia.org/wiki/MQTT) - Wikipedia - The publish/subscribe protocol and its QoS levels.
2. [MQTT Version 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html) - OASIS standard - The packet flows for QoS 0, 1 and 2.
3. [umqtt.simple](https://github.com/micropython/micropython-lib/tree/master/micropython/umqtt.simple) - micropython-lib - The MicroPython MQTT client (QoS 0 and 1).

## Related Resources

- [Chapter 15: MQTT and Push Alerts](../../chapters/15-mqtt-push-alerts/index.md)
