# FAQ Generator Session Log

- **Date:** 2026-10-27
- **Skill:** faq-generator v1.0
- **Model:** Claude Opus 5.5

## Inputs Read

- `CONTENT-GENERATION-GUIDE.md`, for the mascot rules and the formatting and anti-padding rules
- `docs/course-description.md` (quality score 99)
- `docs/learning-graph/learning-graph.json`: 326 concepts, 531 edges, CIS values. The DAG is valid per `quality-metrics.md`.
- `docs/glossary.md`: 326 terms
- All 18 chapter `index.md` files. I read section headings for every chapter and section text for the sections that hold facts (pins, frame sizes, the contract, MQTT, privacy, wake word, the time budget).
- No existing `docs/faq.md` existed, so there was nothing to merge.

## Content Completeness Score: 100/100

The course description scored 25, the learning graph 25, the glossary 15, chapter word count 20 (about 148,500 words), and chapter concept tables 15.

## Outputs

| File | Contents |
|------|----------|
| `docs/faq.md` | 90 questions in 6 categories, plus 1 `mascot-welcome` admonition |
| `docs/learning-graph/faq-chatbot-training.json` | RAG export with Bloom level, difficulty, concepts, keywords, source links, and word count for each question |
| `docs/learning-graph/faq-quality-report.md` | Overall score 88/100 |
| `docs/learning-graph/faq-coverage-gaps.md` | 96 uncovered concepts, ranked by CIS |
| `mkdocs.yml` | Added `FAQ: faq.md` after Glossary, and the two reports under Learning Graph |

## Key Metrics

- Questions: 90 (Getting Started 12, Core 24, Technical 23, Challenges 12, Best Practices 11, Advanced 8)
- Bloom's levels: Remember 18%, Understand 32%, Apply 21%, Analyze 17%, Evaluate 9%, Create 3%
- Examples: 39% (target 40%). Links: 100%. Average answer: 178 words.
- Concept coverage: 70.6% (230/326), by exact label match
- Anchor links: 0. Broken links: 0. Duplicate questions: 0.

## Validation

- `mkdocs build --strict` built cleanly. The only notices were three pre-existing pages that are not in nav (`img/cover-image-prompt.md` and two teachers-guide image descriptions), which this session did not touch.
- `validate-chapter-mascots.py docs/faq.md` found no violations.
- `faq-chatbot-training.json` parses as valid JSON.

## Issues Found

- **Glossary and chapter mismatch.** The glossary examples for Aliasing, Audio Frame, Bin Width, Frame Time Budget, Nyquist Limit, and Timing Verification assume a 16,000 Hz microphone, and Audio Buffer assumes a 1,024-sample buffer. The chapters use 12,800 Hz, a 512-sample/40 ms frame, and 25 Hz bins. The FAQ follows the chapters, and the glossary was not changed.
- **Unconfirmed claims.** Some book claims are explicitly unconfirmed: mDNS on the Pico, TLS details, and Home Assistant integration. The FAQ repeats those caveats rather than presenting the claims as fact.

## Process Note

The JSON export and the statistics were produced by a one-off parsing script in the session scratchpad, which is not committed. Bloom levels were assigned per question by hand, in FAQ order. Difficulty was derived from category and Bloom level. Concepts were found by matching learning-graph labels against question and answer text.
