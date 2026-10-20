---
title: "HTTP Request Reader"
description: "The learner will interpret the parts of an HTTP POST request and its reply by answering 8 questions about the request text, with at least 7 of 8 correct."
status: built
library: p5.js
bloom_level: Understand
image: /sims/http-request-reader/http-request-reader.png
og:image: /sims/http-request-reader/http-request-reader.png
twitter:image: /sims/http-request-reader/http-request-reader.png
social:
   cards: false
quality_score: 95
---

# HTTP Request Reader

<iframe src="main.html" width="100%" height="522px" scrolling="no"></iframe>

[Run the HTTP Request Reader MicroSim Fullscreen](main.html){ .md-button .md-button--primary }

## Embed This MicroSim

Place the following line in your website to include this MicroSim:

```html
<iframe src="https://dmccreary.github.io/open-study-buddy/sims/http-request-reader/main.html" width="100%" height="522px" scrolling="no"></iframe>
```

## Description

When the Pico asks the buddy server a question, it sends a short HTTP POST: a request line, four headers, a blank line, and a 73-byte JSON body, 194 bytes in all. Each part has one job, and getting a single number wrong, such as Content-Length, changes what the server does.

The request is shown as seven numbered lines; hovering over a line names it. Eight questions ask what a line does or what happens when a value is wrong, and two show the server's reply. You answer each with A, B or C, and the lines involved are highlighted with the reason. The request is the one printed by `04-raw-http-post.py`.

## How to Use

The MicroSim opens in its starting state and nothing moves until you act.

- **Answer A, B, C**: Choose an answer. One attempt per question.
- **Next question / See score**: Move on after the feedback.
- **Start over**: Return to question 1 with a fresh score.
- **Hover over a line**: Read what the line is called (exploration, not scored).

## Lesson Plan

### Learning Objective

The learner will interpret the parts of an HTTP POST request and its reply by answering 8 questions about the request text, with at least 7 of 8 correct.

**Bloom's Taxonomy level:** Understand (interpret)

### Audience and Duration

High school students (grades 9-12) building the Open Study Buddy; about 15 minutes.

### Prerequisites

HTTP protocol, request line, header, blank line, body, Content-Length, status code, HTTP POST (all defined in this chapter above this block).

### Activities

1. **Exploration (5 min):** Hover over all seven lines before question 1 and say aloud what each one does.
2. **Guided practice (5 min):** Before questions 4 and 5, count the body's 73 bytes against each wrong Content-Length.
3. **Assessment (5 min):** Answer all eight questions. Mastery is 7 of 8 correct on the first attempt.

### Common Misconceptions Addressed

(1) The blank line is optional decoration. (2) A wrong Content-Length is harmless. (3) A 4xx status means the server is broken. (4) The body can be longer than Content-Length says.

### Discussion Questions

1. Why must the blank line be there?
2. Why does a too-small Content-Length fail fast while a too-large one hangs?
3. Whose mistake is a 4xx status, and whose a 5xx?

### Assessment

The quiz inside the MicroSim is the evidence of mastery: each item is scored on the first attempt only, the correct answer and its reason are shown after every submission, and the final screen reports the score against the mastery threshold.

## Specification

<details markdown="1">
<summary>Full specification from Chapter 13</summary>

```text
Type: microsim
**sim-id:** http-request-reader<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** interpret<br/>
**Learning Objective:** The learner will interpret the parts of an HTTP POST request and its reply by answering 8 questions about the request text, with at least 7 of 8 correct.

**Prerequisites:** HTTP protocol, request line, header, blank line, body, Content-Length, status code, HTTP POST (all defined in this chapter above this block).

**Evidence of Mastery:** For each of the 8 questions the learner chooses one of three answers. An answer is correct when it matches the Correct answer column in Content. Mastery is 7 of 8 correct on the first attempt. Hovering over a line of the request to read its label is exploration, not evidence.

**Misconceptions:** (1) The blank line is optional decoration. (2) A wrong Content-Length is harmless. (3) A 4xx status means the server is broken. (4) The body can be longer than Content-Length says.

**Instructional Rationale:** Understand-level interpretation requires the learner to explain what a part of the message means in a concrete example, not to name it. Choosing the effect of a changed or wrong value makes the learner use the meaning of each part.

**Content:**

The request shown on screen, with its lines numbered:

| Line | Text |
|---|---|
| L1 | `POST /v1/ask HTTP/1.0` |
| L2 | `Host: 192.168.1.50:8080` |
| L3 | `Content-Type: application/json` |
| L4 | `Content-Length: 73` |
| L5 | `Connection: close` |
| L6 | (blank line) |
| L7 | `{"device": "desk-07", "kind": "question", "text": "when is my next test"}` |

The 8 questions, each with three choices:

| # | Question | Choices | Correct answer | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | Which line says what the client wants done, and where? | L1, L2, L7 | L1 | The request line holds the method (POST), the path (/v1/ask) and the HTTP version. |
| 2 | Which line tells the server how many bytes of body to read? | L3, L4, L5 | L4 | Content-Length counts the body's bytes. |
| 3 | What does the blank line L6 do? | It ends the headers, so the body starts after it; it is optional; it separates two requests | It ends the headers, so the body starts after it | Without it the server would keep reading header lines. |
| 4 | Content-Length says 60 but the body is 73 bytes. What does the buddy server do? | Reads 60 bytes and answers 400 because the JSON is cut off; reads all 73 and answers 200; waits for 13 more bytes | Reads 60 bytes and answers 400 because the JSON is cut off | The server trusts the header, so it stops at 60 and the JSON is incomplete. |
| 5 | Content-Length says 90 but the body is 73 bytes. What happens? | The server answers 200; the server answers 400; the server waits for 17 more bytes, and the Pico's timeout ends it | The server waits for 17 more bytes, and the Pico's timeout ends it | The server is still reading and the Pico is waiting for the reply, so neither moves. |
| 6 | Which line tells the server the body is JSON? | L2, L3, L5 | L3 | Content-Type names the format of the body. |
| 7 | The reply starts with HTTP/1.0 400 Bad Request. Whose mistake is it? | The client's request was wrong; the server is broken; the Wi-Fi dropped | The client's request was wrong | A first digit of 4 means the client made the mistake; 5 means the server did. |
| 8 | The reply has Content-Length: 103. How many body bytes should the Pico read? | 73, 103, as many as arrive until a timeout | 103 | The reply's Content-Length counts the reply's body, and the Pico stops there. |

**Provenance:** The request is the one printed by `src/chapters/13-wifi-http-agent-link/04-raw-http-post.py` with the default `buddy_config.py`. The reply length 103 is the length of the Chapter 1 reply as JSON. The server behaviors in questions 4 and 5 are those of `server/buddy_server.py`.

**Rules:** Question order is fixed and the choices of each question are shown in the order in the table. Each question has one attempt. The score is the number of correct answers.

**Learner Activity:**

1. The learner hovers over each of the lines L1 to L7 to read what it is called.
2. The learner starts the 8 questions. Question 1 is shown.
3. The learner picks an answer and submits.
4. The sim shows the correct answer and the Why text, and highlights the lines involved in the request.
5. After question 8, the sim shows the score. The learner should notice that questions 4 and 5 differ only in whether the header number is smaller or larger than the real body.

**Feedback:** 8 questions, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** The request is shown with numbered lines and nothing selected, with the question "Which line says what the client wants done, and where?"

**Chapter Anchors:** The chapter states that the request is 194 bytes in all, 121 of head and 73 of body; that the reply is 103 bytes of body; that a Content-Length smaller than the body gives a 400 and a larger one makes the server wait; and that a first status digit of 4 means the client's mistake.
```

</details>

## References

1. [HTTP](https://en.wikipedia.org/wiki/HTTP) - Wikipedia - Requests, headers and replies.
2. [List of HTTP status codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) - Wikipedia - What 200, 400 and 500 mean.
3. [POST (HTTP)](https://en.wikipedia.org/wiki/POST_(HTTP)) - Wikipedia - Sending a body to the server.

## Related Resources

- [Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../../chapters/13-wifi-http-agent-link/index.md)
