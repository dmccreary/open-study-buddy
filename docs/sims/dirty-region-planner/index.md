---
title: "Dirty Region Planner"
description: "The learner will apply the dirty-region rule to 6 device events by selecting exactly the regions that must be redrawn for each, with at least 5 of 6 correct on the first attempt."
status: built
library: p5.js
bloom_level: Apply
image: /sims/dirty-region-planner/dirty-region-planner.png
og:image: /sims/dirty-region-planner/dirty-region-planner.png
twitter:image: /sims/dirty-region-planner/dirty-region-planner.png
social:
   cards: false
quality_score: 95
---

# Dirty Region Planner

<iframe src="main.html" width="100%" height="552px" scrolling="no"></iframe>

[Run the Dirty Region Planner MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/dirty-region-planner/main.html" width="100%" height="552px" scrolling="no"></iframe>
```

## Description

The Study Buddy's round 360 x 360 display is split into five regions: status bar, time, mascot, spectrum and agent message. Redrawing the whole screen sends 259,200 bytes; redrawing all five regions sends 50,752. The dirty-region rule says a region is redrawn only when the content shown in it changes.

This MicroSim gives you six device events, one at a time. For each event you tick the regions that must be redrawn (none is allowed) and submit. The sim then colors each region (green: needed and chosen, orange: needed but missed, red: chosen but not needed), shows the bytes the correct choice sends, and compares that with a full frame. The region positions and byte sizes come from the chapter table "Region Layout"; the six events are illustrative.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Redraw checkboxes**: Tick each region whose content changes for the event shown. Leave all unticked if nothing changes.
- **Submit**: Check your selection. One attempt per event.
- **Next event / See score**: Move to the next event, or see the score after event 6.
- **Start over**: Return to event 1 with a fresh score.

## Lesson Plan

### Learning Objective

The learner will apply the dirty-region rule to 6 device events by selecting exactly the regions that must be redrawn for each, with at least 5 of 6 correct on the first attempt.

**Bloom's Taxonomy level:** Apply (apply)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

dirty region, region layout, direct region write (all defined in the sections above this block, including the five regions in the table "Region Layout").

### Activities

1. **Exploration (5 min):** Before submitting event 1, read the five region sizes on the display and the full-frame marker on the bytes bar.
2. **Guided practice (5 min):** Work through events 1 to 3 aloud with a partner: for each, name what changes on the screen and which region it lives in.
3. **Assessment (5 min):** Complete all six events. Mastery is 5 of 6 correct on the first attempt.

### Common Misconceptions Addressed

(1) Any event requires a full-screen redraw. (2) A region should be redrawn on every frame whether or not its content changed. (3) Changing the mascot's pose does not require redrawing the mascot region.

### Discussion Questions

1. Which event sent no bytes at all, and why is that still a correct "redraw"?
2. Event 5 is the most expensive. What fraction of a full frame does it cost?
3. Why is redrawing every region on every frame a waste even though it is 4.6 times cheaper than a full frame?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 6</summary>

```text
Type: microsim
**sim-id:** dirty-region-planner<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** apply<br/>
**Learning Objective:** The learner will apply the dirty-region rule to 6 device events by selecting exactly the regions that must be redrawn for each, with at least 5 of 6 correct on the first attempt.

**Prerequisites:** dirty region, region layout, direct region write (all defined in the sections above this block, including the five regions in the table "Region Layout").

**Evidence of Mastery:** For each of the 6 events the learner selects zero or more of the five regions. A selection is correct when the set of selected regions equals the Dirty regions column in Content. Mastery is 5 of 6 correct on the first attempt. Viewing the region sizes before answering is allowed and is not scored.

**Misconceptions:** (1) Any event requires a full-screen redraw. (2) A region should be redrawn on every frame whether or not its content changed. (3) Changing the mascot's pose does not require redrawing the mascot region.

**Instructional Rationale:** Apply-level use of a rule requires the learner to carry it out on new cases. Deciding the set of dirty regions for each event, and then seeing the byte cost of the choice next to the cost of a full frame, ties the rule to the bandwidth reason for it.

**Content:**

The sim shows the five regions of the table "Region Layout" with their byte sizes: Status bar 4,800; Time 6,400; Mascot 8,192; Spectrum 16,000; Agent message 15,360. A full frame is 259,200 bytes.

Events, in this order:

| # | Event shown to the learner | Dirty regions | Bytes sent | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | A new audio frame arrives and the spectrum values are different from the last frame. | Spectrum | 16,000 | Only the spectrum content changed. |
| 2 | The clock minute changes from 12:34 to 12:35. | Time | 6,400 | Only the clock digits changed. |
| 3 | The Pico connects to Wi-Fi and the status icon changes. | Status bar | 4,800 | The icon lives in the status bar. |
| 4 | The student presses Mode and the device enters Listening mode, which changes the mascot's pose and the status text. | Status bar, Mascot | 12,992 | Both the pose and the status text changed. |
| 5 | The agent replies "Test on Friday" and the mascot switches to a speaking pose. | Agent message, Mascot | 23,552 | The words and the pose changed. |
| 6 | A silent room produces an audio frame whose spectrum values equal the last frame. | none | 0 | Nothing changed, so nothing is sent. |

**Provenance:** The regions and bytes come from the chapter table "Region Layout." The events are illustrative, and the sim labels them "illustrative."

**Rules:** A region is dirty when the content shown in it would be different after the event. The bytes sent are the sum of the sizes of the dirty regions. The full frame is 259,200 bytes. The saving shown is 259,200 minus the bytes sent.

**Learner Activity:**

1. The learner reads event 1 and selects the regions that must be redrawn (none is allowed).
2. The learner submits.
3. The sim shows the correct set, the bytes sent, how that compares to 259,200, and the Why text.
4. The learner continues through event 6, then sees the score.
5. The learner should notice that event 6 sends nothing and that event 5 is the most expensive at 23,552 bytes, still far less than a full frame.

**Feedback:** 6 events, fixed order, one attempt each. Correct: "Correct: <Why> (<bytes> bytes, <percent of full frame>%)". Incorrect: "Not quite. The dirty regions are <set>: <Why>". The correct set is revealed after each submission, and a running score "n of 6" is shown.

**Starting State:** The five regions are shown unselected with their sizes, and event 1 is shown with the question "Which regions must be redrawn?"

**Chapter Anchors:** The chapter states that the five regions are the status bar, time, mascot, spectrum, and agent message; that redrawing all five costs 50,752 bytes (16.9 ms of wire time, 28.1 ms measured); and that a full frame is 259,200 bytes.
```

</details>

## References

1. [Framebuffer](https://en.wikipedia.org/wiki/Framebuffer) - Wikipedia - What a frame of pixels is and why rewriting it costs bandwidth.
2. [High color (RGB565)](https://en.wikipedia.org/wiki/High_color) - Wikipedia - The 2-bytes-per-pixel format behind every byte count in this sim.
3. [Serial Peripheral Interface](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface) - Wikipedia - The bus that carries each region write to the display.
4. [framebuf: frame buffer manipulation](https://docs.micropython.org/en/latest/library/framebuf.html) - MicroPython documentation - Drawing into a small buffer before writing one region.

## Related Resources

- [Chapter 6: Drawing Directly to Display Regions](../../chapters/06-display-regions-and-drawing/index.md)
