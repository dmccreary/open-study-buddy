---
title: "Chunk-Size and Heap Explorer"
description: "The learner will examine 8 upload designs to decide whether each fits in a given free heap and, for those that fit, how many sends it needs, with at least 7 of 8 correct."
status: scaffold
library: p5.js
bloom_level: Analyze
---

# Chunk-Size and Heap Explorer



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 14: Streaming Speech, Security, and Network Resilience](../../chapters/14-streaming-security-resilience/index.md).

```text
Type: microsim
**sim-id:** chunk-heap-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** examine<br/>
**Learning Objective:** The learner will examine 8 upload designs to decide whether each fits in a given free heap and, for those that fit, how many sends it needs, with at least 7 of 8 correct.

**Prerequisites:** 16-bit and 32-bit recording sizes, memoryview slice, chunk, free heap, contiguous block (all defined in this chapter above this block and in Chapter 2).

**Evidence of Mastery:** For each of the 8 cases the learner chooses "fits" or "does not fit", and for a case that fits, types the number of sends. A case is correct when the choice matches the Fits column and, for fitting cases, the number matches the Sends column exactly. Mastery is 7 of 8 correct on the first attempt. Moving the explorer's sliders is exploration, not evidence.

**Misconceptions:** (1) Sending in chunks makes the recording itself smaller. (2) Joining the header and body is harmless because the recording is already in memory. (3) A bigger free heap total always means a big block is available. (4) Streaming needs the whole recording in memory.

**Instructional Rationale:** Analyze-level examination requires the learner to break a design into the blocks it needs and compare them with what is available. Using the same rule on eight designs lets the learner see which designs move the memory problem, rather than remove it.

**Content:**

Four designs are described. In each, S is the length in seconds, R16 is the 16-bit recording size \( S \times 25{,}600 \) bytes, and R32 is the 32-bit size \( S \times 51{,}200 \) bytes.

| Design | Description | Largest memory it needs |
|---|---|---|
| A | Record 16-bit. Join the header and the body into one bytes object, then send it once. | Two blocks of R16 at the same time: \( 2 \times R16 \) in all, the largest single block R16 |
| B | Record 16-bit. Send the header, then send the recording in slices of a chunk size K bytes. | R16 for the recording, plus a small K-byte staging area: \( R16 + K \) in all, the largest single block R16 |
| C | Record 32-bit, convert in place after release, send the first half in slices of K bytes. | R32 for the buffer, plus K: \( R32 + K \) in all, the largest single block R32 |
| D | Stream each 1,024-byte frame as it is converted and keep nothing. | One 1,024-byte staging frame, at any length of speech |

The rule: a case fits when the total memory the design needs is no more than the free heap F minus a reserve of 40,000 bytes, which stands for the code, display, and network buffers. The number of sends is the length divided by the chunk size, rounded up (for design D, the frames of 1,024 bytes).

| # | Design | S (s) | K (bytes) | F (bytes) | Fits | Sends | Why (shown as feedback) |
|---|---|---|---|---|---|---|---|
| 1 | B | 3 | 2,048 | 180,000 | fits | 38 | R16 is 76,800; plus 2,048 is 78,848, under 140,000. 76,800 / 2,048 is 37.5, rounded up to 38. |
| 2 | B | 5 | 2,048 | 180,000 | fits | 63 | R16 is 128,000; plus 2,048 is 130,048, under 140,000. 128,000 / 2,048 is 62.5, rounded up to 63. |
| 3 | A | 5 | not used | 180,000 | does not fit | none | The join needs 128,000 + 128,000 = 256,000, over 140,000. |
| 4 | C | 5 | 2,048 | 180,000 | does not fit | none | R32 is 256,000, over 140,000 by itself. |
| 5 | C | 3 | 2,048 | 260,000 | fits | 38 | R32 is 153,600; plus 2,048 is 155,648, under 220,000. The first half to send is 76,800 bytes: 38 sends. |
| 6 | B | 10 | 2,048 | 260,000 | does not fit | none | R16 is 256,000, over 220,000. |
| 7 | D | 10 | 1,024 | 100,000 | fits | 250 | One 1,024-byte frame needs no recording. 10 s is 256,000 bytes: 256,000 / 1,024 is 250 frames. |
| 8 | B | 5 | 8,192 | 180,000 | fits | 16 | R16 is 128,000; plus 8,192 is 136,192, under 140,000. 128,000 / 8,192 is 15.6, rounded up to 16. |

For exploration the learner sets S from 1 to 10 s in steps of 1 s (default 5), K from 512 to 8,192 bytes in the five sizes of the chapter's table (default 2,048), and F from 100,000 to 260,000 bytes in steps of 10,000 (default 180,000), and sees each design's memory need drawn against the free heap with the reserve.

**Provenance:** The recording sizes follow from the kit's 12,800 samples per second, with 4 bytes per sample for 32-bit words and 2 for 16-bit samples (`config.MIC_SAMPLE_RATE`). The reserve of 40,000 bytes and the free heap values are illustrative, and the sim labels them "illustrative." The learner's own free heap comes from Chapter 2's memory report.

**Rules:** Total need and largest block follow the Largest memory column. A case fits when the total need is at most \( F - 40{,}000 \). Sends are \( \lceil \text{bytes to send} / K \rceil \), where the bytes to send are R16 for designs A and B, R16 (the converted half) for design C, and \( S \times 25{,}600 \) split into 1,024-byte frames for design D. A design that does not fit has no send count.

**Learner Activity:**

1. The learner moves the three sliders and watches each design's bar against the free heap line.
2. The learner starts the 8 cases. Case 1 is shown.
3. The learner chooses fits or does not fit and, if it fits, types the number of sends.
4. The sim draws the case's memory need against the free heap and shows the Why text.
5. After case 8, the sim shows the score. The learner should notice that designs A and C fail at 5 s where design B fits, and that design D fits at any length.

**Feedback:** 8 cases, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. It <fits or does not fit><, with N sends if it fits>: <Why>". The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** Design B at 5 s, 2,048 bytes, and 180,000 free is drawn, with the question "Does this fit in the free heap, and how many sends does it need?"

**Chapter Anchors:** The chapter states that a 5 s recording is 128,000 bytes in 16-bit and 256,000 in 32-bit, that joining the head and body needs a second block as large as the recording, that 2,048-byte chunks make 63 sends for 5 s, and that a WebSocket frame header is 8 bytes.
```

## Related Resources

- [Chapter 14: Streaming Speech, Security, and Network Resilience](../../chapters/14-streaming-security-resilience/index.md)
