---
title: FAQ Quality Report
description: Quality metrics for the Open Study Buddy FAQ, including Bloom's Taxonomy distribution, answer quality, concept coverage, and recommendations.
---

# FAQ Quality Report

Generated: 2026-10-27

This report scores the [Open Study Buddy FAQ](../faq.md). The statistics come from parsing `docs/faq.md` and matching it against the 326 concepts in `learning-graph.json`. The structured export is `faq-chatbot-training.json` in this folder.

## Overall Statistics

- **Total Questions:** 90
- **Overall Quality Score:** 88/100
- **Content Completeness Score:** 100/100
- **Concept Coverage:** 70.6% (230/326 concepts)

### Content Completeness Inputs

| Input | Finding | Points |
|-------|---------|--------|
| Course description | Complete, with Bloom's outcomes at all six levels (quality score 99) | 25/25 |
| Learning graph | 326 concepts, 531 dependencies, valid DAG with 0 cycles | 25/25 |
| Glossary | 326 terms | 15/15 |
| Chapter content | About 148,500 words across 18 chapters | 20/20 |
| Concept coverage in chapters | Every chapter lists its concepts in a "Concepts Covered" table | 15/15 |

## Category Breakdown

| Category | Questions | Avg words | Bloom's levels present | With examples |
|----------|-----------|-----------|------------------------|---------------|
| Getting Started | 12 | 160 | Remember 7, Understand 5 | 3 |
| Core Concepts | 24 | 176 | Remember 4, Understand 11, Apply 4, Analyze 5 | 15 |
| Technical Details | 23 | 177 | Remember 5, Understand 10, Apply 6, Analyze 1, Evaluate 1 | 11 |
| Common Challenges | 12 | 184 | Understand 3, Apply 4, Analyze 5 | 2 |
| Best Practices | 11 | 185 | Apply 5, Analyze 2, Evaluate 4 | 3 |
| Advanced Topics | 8 | 197 | Analyze 2, Evaluate 3, Create 3 | 1 |

Difficulty rises from category to category, as intended. Getting Started is all Remember and Understand, and Advanced Topics is all Analyze, Evaluate, and Create.

## Bloom's Taxonomy Distribution

| Level | Actual | Target | Deviation |
|-------|--------|--------|-----------|
| Remember | 18% (16) | 20% | -2% ✓ |
| Understand | 32% (29) | 30% | +2% ✓ |
| Apply | 21% (19) | 25% | -4% ✓ |
| Analyze | 17% (15) | 15% | +2% ✓ |
| Evaluate | 9% (8) | 7% | +2% ✓ |
| Create | 3% (3) | 3% | 0% ✓ |

The total absolute deviation is 12%, and every level is within ±5%.

Bloom's Score: 20/25

## Answer Quality Analysis

- **Examples:** 35/90 (39%). Target: 40%+. This is 1 point short. An answer counts when it contains a code block, a table, a worked calculation, or an explicit "for example."
- **Links:** 90/90 (100%). Target: 60%+ ✓
- **Average length:** 178 words (range 127–229). Target: 100–300 ✓
- **Complete answers:** 90/90 (100%) ✓
- **Anchor links:** 0 ✓
- **Broken links:** 0. Every link target exists on disk. ✓

Answer Quality Score: 23/25 (examples 5/7, links 7/7, length 6/6, completeness 5/5)

### Accuracy Checks

Answers were checked against the chapter text rather than the glossary examples. Numbers such as the pin assignments, the 12,800 Hz sample rate, the 40 ms frame, the 25 Hz bin width, the 129 ms full-screen fill, the QoS assignments, and the seven-step always-on approval process come from the chapters. The FAQ also keeps the chapters' honesty about unmeasured values. It does not quote speed-ups from Chapter 10's blank results table, and it labels the wake-word synthetic test as "not accuracy claims." It describes TLS on the Pico, mDNS name lookup, and the Home Assistant integration as untested or unconfirmed.

!!! warning "Glossary inconsistency found"
    Several glossary examples assume a 16,000 Hz microphone rate, but the chapters use 12,800 Hz. The affected entries are **Aliasing**, **Audio Frame** (32 ms), **Bin Width** (31.25 Hz), **Frame Time Budget** (32 ms), **Nyquist Limit** (8,000 Hz), and **Timing Verification** (32 ms). The **Audio Buffer** entry (1,024 samples) also disagrees with the chapters' 512-sample frame. The FAQ follows the chapters. To match them, these glossary entries should give 12,800 Hz, a 40 ms frame, 25 Hz bins, and a 6,400 Hz Nyquist limit.

## Concept Coverage

**Covered:** 230 of 326 concepts (70.6%). Coverage counts a concept when its label appears in a question or answer. Concepts explained in other words are counted as gaps, so true coverage is somewhat higher.

**Not covered:** 96 concepts. 5 are high priority (CIS ≥ 10), 14 medium (CIS 4–9), and 77 low (CIS < 4). The full ranked list is in the [FAQ Coverage Gaps](faq-coverage-gaps.md) report.

The top five uncovered concepts by Concept Impact Score:

1. RP2350 Microcontroller (CIS 27)
2. Flash File System (CIS 17)
3. Event Parsing (CIS 12)
4. mip Package Manager (CIS 11)
5. WAV File Format (CIS 11)

Coverage Score: 25/30

## Organization Quality

- Logical categorization: ✓ Six standard categories, in learning order
- Progressive difficulty: ✓ Bloom's levels rise from Getting Started to Advanced Topics
- No duplicates: ✓ No identical questions, and each near-duplicate topic was merged into one answer
- Clear questions: ✓ Every question is specific and searchable, and uses glossary terminology

Organization Score: 20/20

## Overall Quality Score: 88/100

- Coverage: 25/30
- Bloom's Distribution: 20/25
- Answer Quality: 23/25
- Organization: 20/20

## Recommendations

### High Priority

1. Fix the six 16,000 Hz glossary examples listed above so the glossary agrees with the chapters and with this FAQ.
2. Add one question that covers the RP2350 microcontroller, the flash file system, and the mip package manager. These are hardware and tooling basics with high CIS.

### Medium Priority

1. Add a worked example to one more answer to pass the 40% example target. The Common Challenges answers are the best candidates, because a short REPL session would show each diagnosis.
2. Weave the medium-priority gap concepts into existing answers. Add the "Hey Pico" phrase to the wake-word answer, the requests library to the Wi-Fi answer, and chunked audio upload to the data-flow answer.
3. Add three or four Apply-level questions to bring Apply from 21% up to the 25% target.

### Low Priority

1. Revisit the low-priority gaps after the chapter quizzes exist, using quiz misses to choose which ones students actually need.
2. Regenerate `faq-chatbot-training.json` whenever `docs/faq.md` changes, so the RAG export stays in sync.

## Suggested Additional Questions

1. "What is the RP2350 chip, and what do its two cores and 520 KB of SRAM mean for my code?" (Technical Details)
2. "How do I save files and settings on the Pico's flash file system?" (Technical Details)
3. "How do I install libraries like umqtt with mip?" (Getting Started)
4. "How does the server turn an ICS event into a structured event?" (Technical Details)
5. "How is a recording stored as a WAV file?" (Technical Details)
6. "How do I use the requests library to send a question to the buddy server?" (Best Practices)
7. "What is a probe program and how is it different from a self-test?" (Common Challenges)
8. "What tools can the agent call, and who decides?" (Core Concepts)
9. "How do I draw a clock face on a round display?" (Best Practices)
10. "When should the device stream audio over a WebSocket instead of uploading it?" (Advanced Topics)
