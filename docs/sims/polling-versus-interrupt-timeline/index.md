---
title: "Polling Versus Interrupt Timeline"
description: "The learner will compare a polling loop with an interrupt by predicting, for 6 button presses, whether a loop that checks the pin every P milliseconds sees the press, and observing that an interrupt sees all 6."
status: built
library: p5.js
bloom_level: Understand
image: /sims/polling-versus-interrupt-timeline/polling-versus-interrupt-timeline.png
og:image: /sims/polling-versus-interrupt-timeline/polling-versus-interrupt-timeline.png
twitter:image: /sims/polling-versus-interrupt-timeline/polling-versus-interrupt-timeline.png
social:
   cards: false
---

# Polling Versus Interrupt Timeline

<iframe src="main.html" width="100%" height="482px" scrolling="no"></iframe>

[Run the Polling Versus Interrupt Timeline MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

Place the following line in your website to include this MicroSim in your course:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/polling-versus-interrupt-timeline/main.html" width="100%" height="482px" scrolling="no"></iframe>
```

## Description

A button press pulls the pin from 1 to 0 for a short time. A polling loop only
looks at the pin every *P* milliseconds, so it sees the press only when one of
its checks lands inside the press. An interrupt is different: the hardware
notices the falling edge the moment it happens and runs the interrupt service
routine (ISR) right away.

This MicroSim draws a 0 to 220 ms timeline with an illustrative press and the
polling check times. For six cases you predict whether the polling loop sees
the press. The checks that land inside the press are computed from the rule
start &le; *k*&middot;*P* &lt; end and drawn in green after you answer. After
the six predictions, the **Interrupt** display shows every press caught at its
falling edge.

## How to Use

1. Read case 1: the polling interval *P* and the press start and end times.
   The blue ticks on the axis show when the loop checks the pin.
2. Press **Seen** or **Missed**.
3. The sim shows what each check read from the pin, lists the checks inside
   the press, and explains the result.
4. Press **Next case** and continue through case 6. The running score is
   shown as "n of 6"; mastery is 5 of 6.
5. After case 6, set **Display** to **Interrupt** and use **Previous case**
   and **Next case** to step through all six presses again.

## Lesson Plan

### Learning Objective

Students will compare a polling loop with an interrupt by predicting, for 6
button presses, whether a loop that checks the pin every *P* milliseconds sees
the press, and observing that an interrupt sees all 6.

### Warm-Up (3 minutes)

Ask: "If you check your phone every 20 minutes, can you miss a message that
appears and disappears in 5 minutes?" Connect the phone check to a polling
loop.

### Guided Exploration (10 minutes)

1. Students predict all six cases before each reveal.
2. Compare cases 2 and 3: same *P*, same press length, different results.
   Ask: "What changed?"
3. Compare cases 4 and 5. Ask students to state when a press is guaranteed to
   be seen by polling (when it lasts longer than *P*).
4. Switch to Interrupt display and step through all six cases.

### Discussion Questions

1. Does a shorter *P* guarantee that every press is seen? What does it cost?
2. Why should an ISR only set a flag and return, instead of doing the work?
3. Does using an interrupt make the main loop run faster? Explain.

### Assessment

The sim records 6 first-attempt predictions. Mastery is 5 of 6 correct.
Switching to interrupt mode is exploration, not evidence.

## References

1. [Polling (computer science)](https://en.wikipedia.org/wiki/Polling_(computer_science)) -
   Wikipedia overview of checking a device's state in a loop.
2. [Interrupt](https://en.wikipedia.org/wiki/Interrupt) -
   Wikipedia article on hardware interrupts and interrupt handlers.
3. [MicroPython: Writing interrupt handlers](https://docs.micropython.org/en/latest/reference/isr_rules.html) -
   official rules for keeping MicroPython ISRs short and safe.

## Related Resources

- [Chapter 2: MicroPython Review for Embedded Systems](../../chapters/02-micropython-review/index.md)

??? note "Original specification"

    Type: microsim
    **sim-id:** polling-versus-interrupt-timeline<br/>
    **Library:** p5.js<br/>
    **Status:** Specified<br/>
    **Bloom Level:** Understand<br/>
    **Bloom Verb:** compare<br/>
    **Learning Objective:** The learner will compare a polling loop with an interrupt by predicting, for 6 button presses, whether a loop that checks the pin every P milliseconds sees the press, and observing that an interrupt sees all 6.

    **Prerequisites:** polling, interrupt, interrupt service routine, falling edge (all defined in the section "Interrupts and Interrupt Service Routines" above this block).

    **Evidence of Mastery:** For each of the 6 cases, the learner commits to "seen" or "missed" for the polling loop before the result is shown. A prediction is correct when it matches the Polling result column in Content. Mastery is 5 of 6 correct. Switching to interrupt mode and watching is exploration, not evidence.

    **Misconceptions:** (1) A faster loop always catches every press. (2) A very short press is always missed. (3) An interrupt makes the main loop run faster.

    **Instructional Rationale:** An Understand-level comparison needs the learner to infer an outcome from a rule rather than watch it. Predicting before the result forces the learner to apply the rule "a poll sees the press only if a check lands inside it," and the interrupt mode then shows why that rule does not apply to hardware edges.

    **Content:**

    A timeline runs from 0 ms to 220 ms. Polling checks happen at 0 ms and then every P ms. A press is a time interval [start, end) during which the pin reads 0. The polling loop sees a press when at least one check time t satisfies start <= t < end.

    | # | P (ms) | Press start (ms) | Press end (ms) | Press length (ms) | Check times inside the press | Polling result | Why (shown as feedback) |
    |---|---|---|---|---|---|---|---|
    | 1 | 5 | 12 | 22 | 10 | 15, 20 | seen | Two checks land inside the press. |
    | 2 | 20 | 12 | 22 | 10 | 20 | seen | The check at 20 ms lands inside the press, by luck. |
    | 3 | 20 | 22 | 32 | 10 | none (checks at 20 and 40) | missed | The press starts just after one check and ends before the next. |
    | 4 | 100 | 30 | 80 | 50 | none (checks at 0 and 100) | missed | A 50 ms press fits entirely between two checks 100 ms apart. |
    | 5 | 100 | 90 | 210 | 120 | 100, 200 | seen | A press longer than P always contains a check. |
    | 6 | 50 | 55 | 95 | 40 | none (checks at 50 and 100) | missed | A press shorter than P can fall between two checks. |

    In interrupt mode every case is seen at its press start, because the hardware notices the falling edge.

    **Provenance:** The numbers are illustrative and the sim labels them "illustrative." The rule that a polling loop misses a press that fits between two checks comes from the chapter section "Interrupts and Interrupt Service Routines."

    **Rules:** Checks occur at 0, P, 2P, and so on up to 220 ms. A press is seen by polling when start <= kP < end for some integer k >= 0. In interrupt mode a press is seen at its start time for every case. A press longer than P is always seen by polling.

    **Learner Activity:**

    1. The learner reads case 1 (P and the press interval) and chooses "seen" or "missed."
    2. The sim draws the check times and the press, then shows the result and the Why text.
    3. The learner continues through case 6, then sees the score.
    4. The learner switches the display to interrupt mode and steps through the six cases again, noticing that every press is marked at its start time.

    **Feedback:** 6 cases, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The polling loop <seen or missed> this press: <Why>". The result is revealed after each answer, and a running score "n of 6" is shown.

    **Starting State:** Case 1 is shown with the checks marked on the timeline and the question "Will the polling loop see this press?"

    **Chapter Anchors:** The chapter states that polling can miss a press that starts and ends between two checks, that an interrupt cannot miss it, and that an ISR should only set a flag.
