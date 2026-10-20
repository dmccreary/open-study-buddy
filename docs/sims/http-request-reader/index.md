---
title: "HTTP Request Reader"
description: "The learner will interpret the parts of an HTTP POST request and its reply by answering 8 questions about the request text, with at least 7 of 8 correct."
status: scaffold
library: p5.js
bloom_level: Understand
---

# HTTP Request Reader



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../../chapters/13-wifi-http-agent-link/index.md).

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

## Related Resources

- [Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../../chapters/13-wifi-http-agent-link/index.md)
