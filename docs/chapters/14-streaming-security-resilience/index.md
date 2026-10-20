---
title: "Streaming Speech, Security, and Network Resilience"
description: "How the Pico sends recorded speech to the buddy server in memory-safe chunks, uses speech-to-text and text-to-speech services, streams audio over a WebSocket, adds authentication tokens and HTTPS, and survives network failure with timeouts, retries with backoff, and an offline fallback."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 13:12:59"
version: 1.11
---

# Streaming Speech, Security, and Network Resilience

## Summary

This chapter makes the agent link work for real speech. Students upload recorded audio in memory-safe chunks, use speech-to-text and text-to-speech services, and stream audio over a WebSocket. They also add authentication tokens and HTTPS, and handle timeouts, retries, and offline fallback when the network fails.

## Concepts Covered

This chapter covers the following 15 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| WebSocket | 3 |
| Authentication Token | 6 |
| TLS Encryption | 5 |
| Text-to-Speech Service | 7 |
| HTTPS | 4 |
| Chunked Audio Upload | 4 |
| Streaming Audio | 2 |
| Certificate Handling | 1 |
| Network Failure Handling | 7 |
| Audio Chunk Size | 1 |
| Speech-to-Text Service | 2 |
| Barge-In Interruption | 1 |
| Retry and Backoff | 1 |
| Timeouts | 1 |
| Offline Fallback | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../01-personal-agents-architecture/index.md)
- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 7: Buttons, State Machines, and Device Modes](../07-buttons-and-device-modes/index.md)
- [Chapter 8: I2S Audio: Recording and Playing Sound](../08-i2s-audio/index.md)
- [Chapter 11: Microphone Calibration and Push-to-Talk](../11-mic-calibration-push-to-talk/index.md)
- [Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../13-wifi-http-agent-link/index.md)

---

## From One Question to Real Speech

Chapter 13 sent a typed question and got a typed answer. A real device has to send a *recording* of someone talking, get back *speech*, keep working when the Wi-Fi hiccups, and keep strangers out. Each of those has a catch on a board with 520 KB of RAM, and this chapter is about the catches.

!!! mascot-welcome "Let's Make It Talk"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    In this chapter you will hold a button, say a sentence, and hear the buddy server's answer come back through your own speaker, with a login, a plan for bad networks, and a way to interrupt. Let's listen closely! The trick is sending sound in pieces small enough for a tiny memory.

Chapter 1's data flow had eight steps, and Chapter 13 handled them with typed text. Step 1 is still the student speaking. Here is what steps 2 to 8 become.

| Step | What happens | Where | Section |
|------|--------------|-------|---------|
| 2 | The microphone's samples are made smaller (16-bit) and kept | Pico | Recording an Utterance for the Network |
| 3 | The recording travels to the server in chunks, with a token | Network | Chunked Audio Upload; Authentication Tokens |
| 4 | The server turns speech into words | Server | Speech-to-Text and Text-to-Speech |
| 5 | The brain decides on a reply (Chapter 13's `decide()`) | Server | (unchanged) |
| 6 | The server turns the reply into speech | Server | Speech-to-Text and Text-to-Speech |
| 7 | The speech comes back in pieces | Network | Playing the Answer |
| 8 | The Pico plays it, and the listener may interrupt | Pico | Interrupting: Barge-In |


## Recording an Utterance for the Network

Chapter 11 builds the full push-to-talk recorder with a noise floor and voice-activity detection. This chapter needs only a small one, `utterance.py`, so that it stands on its own: hold MODE, record, release.

The microphone delivers 32-bit words, 4 bytes per sample (Chapter 8). A speech service does not need 24 bits of precision, and the Pico cannot afford them. Converting each sample to 16 bits as it arrives halves the memory.

| Length | 32-bit words | 16-bit samples | Share of the chip's 520 KB (532,480 bytes), 16-bit |
|--------|--------------|----------------|-------------------------------------|
| 3 s | \( 3 \times 12{,}800 \times 4 = 153{,}600 \) bytes | 76,800 bytes | 14.4 % |
| 5 s | 256,000 bytes | 128,000 bytes | 24.0 % |
| 10 s | 512,000 bytes | 256,000 bytes | 48.1 % |

The 3 s row in 32-bit is Chapter 2's 29 percent figure. Five seconds in 32-bit words (256,000 bytes) is almost half the chip and almost certainly fails, as Chapter 2 warned. So `utterance.record()` converts each 20 ms read (1,024 bytes, 256 samples) into 512 bytes of 16-bit audio as it goes.

```python
def convert(raw, out, pos):
    shifted = [v >> SHIFT for v in struct.unpack(_UNPACK, raw)]   # 32-bit word -> 24-bit sample
    mean = sum(shifted) // READ_SAMPLES                           # this chunk's DC offset
    struct.pack_into(_PACK, out, pos,
                     *[max(-32768, min(32767, ((x - mean) * GAIN) >> 8)) for x in shifted])
```

Each step has a reason from earlier chapters. The right shift by `MIC_SAMPLE_SHIFT` recovers the 24-bit value, subtracting the chunk's mean removes the microphone's wandering DC offset (Chapter 8 measured it moving between frames), and the multiply by `GAIN` of 8 followed by `>> 8` is the same 18 dB boost the kit's test 07 uses to bring speech up to a playable level. The `max/min` clips instead of wrapping around, which would sound like a crack (Chapter 3).

The conversion has to finish inside the 20 ms between reads, or the microphone's ring buffer starts to fill (Chapter 8's frame budget). Chapter 8 measured about 10 ms for a similar loop over 512 samples, so there is reason to expect this one to fit, but no one has measured *this* code on the kit. `03-record-utterance.py` prints the worst conversion time against the 20,000 microsecond budget, and if it is over, the fix is the kit's test 07 method: record 32-bit words, convert after you let go, and limit the utterance to 3 s. Allocate the recording buffer first, before the heap fragments, with `utterance.make_buffer()`.

## Chunked Audio Upload

**Chunked audio upload** means sending the recording to the server in pieces instead of in one write. Here is the reason. The obvious way to send a POST is to join the header and the body into one `bytes` object and call `send` once.

```python
request = head + body          # NEVER with a recording: this copies it
sock.send(request)
```

Joining makes a *new* object as big as both. A 5 s recording is 128,000 bytes, so the join needs another 128,000 contiguous bytes while the recording still exists: 256,000 bytes in two blocks. Chapter 2's fragmentation rule says a block that size is hard to find. The fix costs nothing. Send the header first, then send the recording itself in slices of a `memoryview`, which points into the existing buffer without copying it.

```python
sock.write(head)
view = memoryview(pcm)[:nbytes]
sent = 0
while sent < len(view):
    piece = view[sent:sent + chunk]
    sock.write(piece)
    sent += len(piece)
```

`buddy_http.request()` does this, with a deadline check before every piece. Slicing a memoryview is free, so the only memory the upload needs beyond the recording is a few small objects. The server still sees one ordinary POST whose `Content-Length` was known up front.

There is a second way to send a body of unknown length, called `Transfer-Encoding: chunked`, in which each piece is preceded by its size in hexadecimal. The `requests` library will do it for you when `data=` is a generator. The book does not use it, for three reasons. The Pico knows the total as soon as the button is released. Many simple servers do not accept chunked request bodies (ours answers 411, Length Required). And a request that fails halfway is simpler to reason about when the length is fixed.

*Worked example.* A 5 s utterance is 128,000 bytes. With 2,048-byte chunks that is \( \lceil 128{,}000 / 2{,}048 \rceil = 63 \) calls to `write`. Each chunk is \( 2{,}048 / 25{,}600 = 0.08 \) s, 80 ms, of audio. No more than 2,048 bytes is ever in flight beyond the recording itself.

### Audio Chunk Size

The **audio chunk size** is how many bytes go in each write. It is a trade-off among four things, and `01-chunk-arithmetic.py` prints all of them.

| Chunk (bytes) | Chunks for 5 s | Audio per chunk | Typical TCP segments | WebSocket extra bytes | Extra as % |
|---------------|----------------|-----------------|----------------------|-----------------------|------------|
| 512 | 250 | 20 ms | 1 | 8 | 1.56 % |
| 1,024 | 125 | 40 ms | 1 | 8 | 0.78 % |
| 2,048 | 63 | 80 ms | 2 | 8 | 0.39 % |
| 4,096 | 32 | 160 ms | 3 | 8 | 0.20 % |
| 8,192 | 16 | 320 ms | 6 | 8 | 0.10 % |

The "segments" column assumes a TCP segment carries up to 1,460 bytes, the usual size on an Ethernet-style network; the real value on your network may differ. The "extra bytes" column is a WebSocket client frame's 8-byte header (2 for the opcode and length, 2 more when the length is 126 or over, and 4 for the mask), which the WebSocket section explains. Small chunks cost more calls and a little more overhead, and large chunks cost latency (the first sound cannot leave until the chunk is full) and cost more to lose when one fails.

The book's defaults come from two numbers already in this book. For the HTTP upload, `UPLOAD_CHUNK_BYTES = 2048` (80 ms, two audio reads): large enough that the overhead is a rounding error, small enough that a stalled network is noticed within one deadline check. For streaming over a WebSocket, `STREAM_CHUNK_BYTES = 1024`, which is 512 samples, exactly Chapter 8's 40 ms frame, so each frame the loop produces is one message. Neither value was tuned on the kit.

#### Diagram: Chunk-Size and Heap Explorer

<details markdown="1">
<summary>Chunk-Size and Heap Explorer</summary>
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
</details>

!!! mascot-thinking "Chunks Move the Problem, Not the Data"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Sending in pieces does not make the recording smaller. It stops you from making a *second* copy, and only streaming (never keeping the whole recording) removes the big block entirely. Ask "how many copies of the data exist at once?" of every design.

## Speech-to-Text and Text-to-Speech

The Pico does not understand speech and cannot make it. Both jobs belong to the buddy server, which has the memory and the processing power. In `server/buddy_server.py` the whole voice path is three function calls, and each one is a swappable piece.

```python
heard = stt.transcribe(pcm, rate)                      # speech-to-text
reply = brain.make_reply(heard, EVENTS)                # the brain: Chapter 13's decide()
speech = tts.synthesize(reply["speak"], DEVICE_RATE)   # text-to-speech
```

### The Speech-to-Text Service

A **speech-to-text service** turns a recording into written words. Servers get it in one of two ways: a program running on the server's own computer, or a company's web service. The server's `stt.py` has two backends, chosen with the `BUDDY_STT` environment variable.

| Backend | What it does | Needs |
|---------|--------------|-------|
| `stub` (default) | Checks that the recording is not silent (an RMS loudness test), then returns a fixed phrase. **It does not recognize speech.** | Nothing |
| `service` | The place, clearly marked in the file, where you write the call to a real service | A provider your school approved, and an API key in the server's `STT_API_KEY` environment variable |

The stub exists so every other part of the pipeline can be tested with no account and no internet. With the stub, whatever you say, the answer is about "when is my next test", and a silent recording gives "Sorry, I did not catch that." Most services want a WAV file rather than raw samples, so `stt.pcm_to_wav()` adds the 44-byte header from Chapter 3. Keys live only in the server's environment. They are never in a file you share and never on the Pico.

A cloud service means the student's voice leaves the classroom. Chapter 17 asks the questions to answer before you do that, and the stub keeps this chapter from needing an answer.

### The Text-to-Speech Service

A **text-to-speech service** does the opposite: it turns the reply's `speak` sentence into audio. The same pattern applies: `tts.py` has a `stub` backend (one beep per word, rising in pitch, so you can hear that audio arrived and how long a sentence is) and a marked place for a `service` backend with its key in `TTS_API_KEY`.

The catch is the *format*. The Pico's speaker is set up for 16-bit mono at 12,800 samples per second, the same settings as the kit's test 07. A real service usually returns something else, so the server must convert before it sends.

| A service may return | The Pico can play it? | What the server must do |
|----------------------|-----------------------|-------------------------|
| 16-bit mono PCM at 12,800 Hz | Yes | Nothing |
| 16-bit mono PCM at another rate (22,050, 24,000) | Only at the wrong speed | Resample to 12,800 Hz with `tts.to_device_pcm()` |
| Stereo PCM | No | Mix to mono first |
| WAV | After the 44-byte header is removed | Strip the header, then as above |
| MP3 or Opus | No: the Pico cannot decode them | Decode on the server |

Resampling by linear interpolation is enough for speech, and going down to 12,800 Hz discards everything above 6,400 Hz (Chapter 3's Nyquist limit), which the speaker could not reproduce anyway. A common surprise is a sentence that plays too fast and too high: that is the wrong rate, the same chipmunk effect as Chapter 8. The server also applies the device's volume (`GET /v1/speech/<id>?volume=40` scales the samples), so the Pico does no per-sample work. At volume 40 the peak is \( 0.4 \times 32{,}767 \approx 13{,}107 \), the same figure as Chapter 8's tone.

*Worked example.* A sentence that takes 2.5 s to say is \( 2.5 \times 12{,}800 \times 2 = 64{,}000 \) bytes of speech. The Pico never holds all of it. The next section shows why.

### Playing the Answer

**Streaming audio** means playing sound while it is still arriving, instead of waiting for all of it. The server sends the speech with a `Content-Length` and `X-Audio-Rate: 12800`, and `buddy_http.request()` reads the body into one reusable 2,048-byte buffer and hands each filled buffer to a function, which writes it to the speaker.

```python
def sink(view):
    speaker.write(view)         # blocks until the chunk is in the speaker's buffer

buddy_client.speech(path, config.VOLUME, sink, chunk_buf)
```

The speaker's `write` blocks until its 8,192-byte buffer has room (Chapter 8), and the socket read blocks until the next chunk arrives, so the two pace each other. The network is the producer, the I2S buffer is the consumer, and one 2,048-byte buffer sits in the middle. This is the ring-buffer idea of Chapter 8 again, with the Wi-Fi link in place of the microphone. At the natural end of the sound the code lets the speaker's buffer drain before `deinit()`, and it closes the microphone for the whole time the speaker is open, which is Chapter 8's rule against the self-hearing problem. The speech request is deliberately *not* retried: a retry would start the sentence again after part of it had played.

## Interrupting: Barge-In

**Barge-in interruption** is the listener cutting off the device while it is speaking. People do it all the time: the answer starts, they know what it will say, and they say "stop" or ask something else. A good device lets them.

Voice barge-in would need the microphone open while the speaker plays, and Chapter 8 explained why that fails: the microphone hears the speaker, about 15 times louder than a quiet room in the kit's test. Telling the device's voice from the listener's would need echo cancellation, which Chapter 8 called out of scope for a Pico. So in this book barge-in is a **button press**: the device checks MODE between chunks, and if it is down, it stops.

| What interrupts | Works on the kit? | Why |
|-----------------|-------------------|-----|
| Pressing MODE | Yes | A button is not affected by sound |
| Saying "stop" | No | The microphone is closed while speaking, and hearing over the speaker needs echo cancellation |
| A new wake word | Not in this book | Same problem as saying "stop" |

Stopping takes three steps in `04-upload-voice.py`: raise an exception from the playback function (which also closes the socket, so the rest of the speech is not downloaded), call `speaker.finish(drain=False)` so `deinit()` discards what is queued, and wait out the quiet tail (120 ms, from Chapter 8's measurement) before the microphone is opened again. Skipping the drain matters. The speaker's buffer holds up to \( 8{,}192 / (12{,}800 \times 2) = 0.32 \) s of sound, and left to drain it would keep talking for a third of a second after the press. Because the loop checks the button once per 2,048-byte chunk (80 ms of audio), the expected stop time is one chunk plus the discarded buffer, about 80 ms. That is an estimate from arithmetic; no one has measured it on the kit.

On a WebSocket the same press also sends `{"event": "cancel"}`, so the *server* stops sending speech too.

## Authentication Tokens

Chapter 13's server answers anyone who can reach it. An **authentication token** is a secret string that the device presents with every request, so the server can tell the school's devices from everyone else. In this book it travels in an HTTP header, `X-Buddy-Token`, and it lives in `secrets.py` on the Pico next to the Wi-Fi password.

```python
# secrets.py on the Pico  (never committed)
buddy_token = "a-long-random-string"
```

```python
headers = {"X-Buddy-Token": TOKEN, "X-Buddy-Device": cfg.DEVICE_ID}
```

On the server, `BUDDY_TOKENS` holds one or more accepted tokens, and every endpoint except `/v1/health` refuses a request with a missing or wrong one by answering **401** and doing nothing else. The check compares in constant time (`hmac.compare_digest`), so the time it takes does not reveal how many leading characters were right. The Pico treats 401 as *not worth retrying*: the same token will fail the same way, so the status region says "bad token" and stops.

!!! mascot-tip "Make a Token That Cannot Be Guessed"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Run `python3 -c "import secrets; print(secrets.token_urlsafe(24))"` on your computer. It makes 24 random bytes, which is \( 24 \times 8 = 192 \) bits of randomness, written as 32 characters. A word from a dictionary is far easier to guess.

Tokens should be **rotated**, replaced from time to time and whenever one might have leaked. The server's list makes rotation painless, because the old and new tokens work together for a while.

| Step | Server's `BUDDY_TOKENS` | Pico's `buddy_token` | Result |
|------|-------------------------|----------------------|--------|
| 1 | `old` | `old` | Working |
| 2 | `new,old` | `old` | Still working: both accepted |
| 3 | `new,old` | `new` | Pico updated |
| 4 | `new` | `new` | Old token no longer works |

Two warnings go with tokens. First, keep the token out of the URL: web addresses are written to logs, browser histories, and error messages, while headers are not. Second, a token over plain HTTP is visible to anyone who can capture the network traffic, exactly like the question itself. It keeps strangers from *using* the server, but it does not hide anything from someone listening on the same Wi-Fi, which is what the next section addresses.

!!! mascot-warning "A Token in Git Is a Token Given Away"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If `buddy_token` ends up in a file you commit, anyone who can read the repository holds the key. It belongs in `secrets.py`, which is listed in `.gitignore`. If it ever gets out, rotate it as in the table above at once.

## Encrypting the Link: TLS, HTTPS, and Certificates

**TLS encryption** (Transport Layer Security) scrambles everything on a connection so that anyone capturing the traffic sees only noise, and it lets the client confirm which server it reached. **HTTPS** is ordinary HTTP carried inside a TLS connection, and by convention uses a different port; the book's server uses 8443 for HTTPS and 8080 for plain HTTP. Setting up TLS adds a *handshake* to the start of every connection, in which the two sides agree on keys and the server proves its identity with a certificate.

The Pico can do this. MicroPython's `ssl` module wraps a connected socket, and `buddy_http.open_socket(..., tls=True)` is four lines of it.

```python
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.verify_mode = ssl.CERT_REQUIRED               # check the certificate
ctx.load_verify_locations(cadata=ca_bytes)        # ...against this one
sock = ctx.wrap_socket(sock, server_hostname=host)
```

TLS costs memory and time. From MicroPython's TLS configuration (the `master` source we read), the library keeps a 16,384-byte input record buffer and a 4,096-byte output record buffer for each connection: \( 16{,}384 + 4{,}096 = 20{,}480 \) bytes, before anything is spent on the handshake itself and on parsing the certificate. On top of a 5 s recording of 128,000 bytes that is already \( 128{,}000 + 20{,}480 = 148{,}480 \) bytes. The handshake time and the rest of the heap use are not known for this kit, and `07-tls-probe.py` measures both so that you can replace this estimate. The same configuration lists TLS 1.2 and earlier, and no TLS 1.3, so a server must be willing to speak 1.2 (the book's server sets 1.2 as its minimum and negotiates upward with other clients).

### Certificate Handling

**Certificate handling** is how the client decides whether to believe the server's certificate. Encryption alone is not enough. Without checking, a program on the same network could pretend to be the buddy server, accept the encrypted connection, and read everything. There are three choices.

| Option | How | Protects against an eavesdropper | Protects against an impostor | Cost to set up |
|--------|-----|----------------------------------|------------------------------|----------------|
| Verify against a CA | Trust the certificate authority that signed the server's certificate | Yes | Yes | A certificate from a CA, and a name for the server |
| Pin the server's certificate | Keep the server's own certificate on the Pico and accept only that | Yes | Yes | Copy a ~400-byte file when the certificate is renewed |
| Skip verification (`CERT_NONE`) | Do not check | Yes | **No** | None |

On the mbedTLS-based builds, MicroPython's documentation says plainly that `CERT_NONE` and `CERT_OPTIONAL` do not validate any certificate, and only `CERT_REQUIRED` does. Verifying also needs two things from the Pico: the correct date and time, because a certificate has a validity period (set the clock with NTP, or from your computer with `mpremote rtc --set`), and `server_hostname`, the name or address the certificate was issued for.

`server/make-cert.sh <address>` makes a certificate for the lab: an EC key, valid 365 days, with the server's address in the subject alternative name, plus `ca.der`, the same certificate in DER form. You copy `ca.der` (about 400 bytes) to the Pico and the Pico trusts that one certificate: pinning. Test 07 connects with no checking, then with `ca.der`, then with a deliberately damaged copy, which must be refused.

!!! mascot-warning "CERT_NONE Is a Lock Without a Door Check"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Skipping verification makes the connection *look* secure while anyone on the network can be the server. It is acceptable only for a lab demo that measures cost, as test 07's case 2 does. Note that the standard `requests` library on the Pico does this for every `https://` address, so do not use it for HTTPS and assume you are safe.

### What the Book Recommends, and What Is Untested

For a classroom, keep the plain-HTTP-plus-token setup of this chapter on a trusted network, and add TLS when the traffic leaves it. The most practical way is to leave the Pico and the buddy server as they are and put a *reverse proxy* (a web server such as Caddy or nginx on the same computer) in front. It holds a real certificate and passes requests to the buddy server on the same machine, so the Pico's side of the problem is just "trust this CA". Pinning a single certificate, as the lab does, is a good second choice for one fixed server. Skipping verification is for measuring only.

These parts of the TLS story are the least certain in the book, and are untested on the kit:

- Whether `CERT_REQUIRED` accepts a certificate that names the server by **IP address** (the lab certificate does), or whether a `.local` or DNS name is needed.
- Whether the Pico's date check passes without NTP, and what error you see when it does not.
- The real memory and time cost of the handshake: `07-tls-probe.py` measures it, and the 20,480 bytes above is only the buffer floor.
- The behavior of `ssl` on your firmware version; the notes here come from the current MicroPython documentation and source.

If HTTPS will not work on your Pico, the fallback is to stay on plain HTTP with the token, on a network the school controls. That is a decision to make knowingly, not a failure.

!!! mascot-encourage "TLS Is Fiddly for Everyone"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Certificates, dates, hostnames, and memory all have to line up, so a first HTTPS attempt that fails is normal, even for professionals. You already know how to isolate a problem: run test 07's three cases in order, and the first one that fails tells you whether it is the network, the encryption, or the certificate check.

## When the Network Fails

Wi-Fi in a school building drops, the server restarts, a router reboots, and a student walks out of range. A device that assumes the network always works will freeze, crash, or silently say nothing. **Network failure handling** is deciding in advance what the device does in each case, and showing the student what is happening. It has four tools that build on each other: time limits, a classification of what went wrong, patient retries, and a fallback.

### Timeouts

A **timeout** is a time limit on waiting. Without one, a socket call waits for ever when the other side goes quiet, and the whole device freezes with it, which a student sees as a dead gadget. Every network wait in this chapter has a limit.

| Limit | Value | What it covers |
|-------|-------|----------------|
| `REQUEST_TIMEOUT_S` | 8 s | Each single wait: connecting, each `write`, each `read`. Set with `sock.settimeout()` |
| `TOTAL_TIMEOUT_S` | 20 s | The whole request, checked between every chunk, so a server that trickles a byte at a time cannot hold the device |
| `CONNECT_TIMEOUT_MS` | 15,000 ms | Joining Wi-Fi |

Both layers are needed. `settimeout` limits one wait, but a server that sends one byte every 7 seconds would pass every single-wait limit for ever. The total deadline catches that. One gap remains: looking up a *name* with `getaddrinfo` has its own waiting that `settimeout` does not control, which is another reason the book uses IP addresses.

How long should the limit be? It has to be longer than the slowest normal case. The server's speech-to-text and text-to-speech both run inside the wait for the reply, so with a real service that wait can be seconds. The upload time depends on a network speed no one has measured for your classroom, so here is the arithmetic for three assumed speeds.

| Assumed upload speed | Time to upload 128,000 bytes (5 s) |
|----------------------|-------------------------------------|
| 10,000 bytes/s (very poor) | 12.8 s |
| 50,000 bytes/s | 2.6 s |
| 200,000 bytes/s | 0.64 s |

These speeds are assumptions, not measurements. The point is the first row: on a bad link the upload alone would pass 8 s, which is why `TOTAL_TIMEOUT_S` is 20 and the per-wait limit counts each piece separately. `05-timeouts-and-failures.py` makes requests that go wrong on purpose and prints how long each took to fail.

### Failure Kinds

Not every failure deserves a retry, so `buddy_http` turns each one into a `NetError` with a **kind** and a flag for whether trying again could help.

| Kind | What it means | Retry? | The status region says |
|------|---------------|--------|------------------------|
| `timeout` | Nothing answered in time | Yes | `retry 1/3` |
| `dns` | A server name could not be looked up | Yes | `retry 1/3` |
| `refused` | Nothing is listening at that address and port (server not running) | Yes | `retry 1/3` |
| `unreachable` | No route to that address | Yes | `retry 1/3` |
| `reset` | The connection was cut | Yes | `retry 1/3` |
| `busy` | The server answered 408, 429, or 5xx | Yes | `retry 1/3` |
| `auth` | The server answered 401 or 403: bad token | **No** | `bad token` |
| `bad-request` | Another 4xx: the request itself is wrong (400, 411, 413) | **No** | `error` |
| `bad-reply` | The reply was not HTTP or was too big | **No** | `error` |
| `tls` | The handshake or certificate check failed | **No** | `error` |

A wrong token will be just as wrong in a second, and a malformed request will be too, so retrying them only wastes time and hammers the server. A timeout or a refused connection may be gone in a moment.

One more thing is easy to miss. A server that refuses an upload early, with a 413 or a 401, may close the connection while the Pico is still sending. The Pico's next write then fails with a reset, and the reason sits unread in the socket. `buddy_http.request()` reads the reply once a send fails, so the device shows "bad token" rather than a mysterious reset. Only requests that are safe to repeat should be retried: asking a question changes nothing on the server, so `/v1/ask` and `/v1/voice` are safe. The speech download is not retried, as discussed earlier.

### Retry and Backoff

**Retry and backoff** means trying again after a wait that grows. The simplest rule, retrying immediately, is the worst: if the server is overloaded or restarting, a hundred devices hammering it every few milliseconds keep it down. **Exponential backoff** doubles the wait each time, from a base and up to a cap, and **jitter** randomizes it. `backoff.py` implements full jitter.

\[ \text{ceiling}_k = \min\bigl(\text{cap},\ \text{base} \times 2^{k}\bigr), \qquad \text{wait}_k = \text{a random number from 0 to ceiling}_k \]

With the book's base of 500 ms and cap of 8,000 ms, where \( k = 0 \) is the wait after the first failure:

| Retry | Ceiling (ms) | Average wait (ms) | Longest total waiting so far (ms) |
|-------|--------------|-------------------|-----------------------------------|
| 1 | 500 | 250 | 500 |
| 2 | 1,000 | 500 | 1,500 |
| 3 | 2,000 | 1,000 | 3,500 |
| 4 | 4,000 | 2,000 | 7,500 |
| 5 | 8,000 | 4,000 | 15,500 |
| 6 | 8,000 | 4,000 | 23,500 |

The longest a request can take is every attempt timing out plus every wait at its ceiling. With 4 attempts and an 8 s socket timeout that is \( 4 \times 8{,}000 + (500 + 1{,}000 + 2{,}000) = 35{,}500 \) ms, 35.5 seconds. That is a long time to stare at a device, which is why the display shows each retry. Choosing the number of attempts and the timeouts is a design decision about how long a student will wait, and the table is the tool for making it.

*Worked example.* Thirty desk devices lose the server for a few seconds when it restarts. With no jitter, all thirty retry at exactly 500 ms, then all thirty at 1,000 ms later, so the server receives 30 requests in the same instant, every round. With full jitter, the first retry of each device is a random time between 0 and 500 ms. Cut those 500 ms into five 100 ms windows, and the expected load is \( 30 / 5 = 6 \) requests per window instead of 30. The actual number in any run is random, and `02-backoff-table.py` simulates it.

!!! mascot-thinking "Randomness Is the Cure for Stampedes"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Doubling the wait spaces retries *out in time*, and jitter keeps many devices from choosing the *same* moment. Neither idea helps alone: doubling without jitter keeps the herd in step, and jitter without doubling never gives a struggling server room to breathe.

#### Diagram: Retry and Backoff Timeline Explorer

<details markdown="1">
<summary>Retry and Backoff Timeline Explorer</summary>
Type: microsim
**sim-id:** retry-backoff-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the longest time a request can take under 8 retry settings, to within 0.05 s, with at least 7 of 8 correct.

**Prerequisites:** timeout, retry, exponential backoff, ceiling, attempt (all defined in this chapter above this block).

**Evidence of Mastery:** For each of the 8 settings the learner types the worst-case total time in seconds. An answer is correct when it is within 0.05 s of the number in the Answer column. Mastery is 7 of 8 correct on the first attempt. Dragging the explorer's controls and watching the timeline is exploration, not evidence.

**Misconceptions:** (1) The wait doubles for ever. (2) The last attempt is followed by a wait. (3) Jitter makes the worst case longer. (4) The waits are the only time a retry costs.

**Instructional Rationale:** Apply-level calculation requires the learner to carry out the worst-case formula on new numbers. Seeing the same attempts laid out on a timeline, with the waits and the timeouts as separate segments, shows what each term in the formula stands for and why the last attempt has no wait after it.

**Content:**

The model: a request makes up to N attempts. Every attempt fails by timing out after T seconds. After each failed attempt except the last, the device waits. The wait after failed attempt k (k = 0 for the first) has a ceiling of \( \min(\text{cap}, \text{base} \times 2^k) \). The worst case is every attempt timing out and every wait taking its full ceiling, so the worst-case total is \( N \times T + \sum_{k=0}^{N-2} \min(\text{cap}, \text{base} \times 2^k) \). With jitter, each actual wait is a random number from 0 up to its ceiling, and never above it.

| # | Base (ms) | Cap (ms) | Attempts N | Timeout T (s) | Answer (s) | Why (shown as feedback) |
|---|---|---|---|---|---|---|
| 1 | 500 | 8,000 | 4 | 8 | 35.5 | 4 x 8 = 32 s of timeouts, plus waits of 0.5 + 1 + 2 = 3.5 s. |
| 2 | 500 | 8,000 | 3 | 5 | 16.5 | 3 x 5 = 15 s, plus waits of 0.5 + 1 = 1.5 s. |
| 3 | 1,000 | 4,000 | 5 | 3 | 26 | 5 x 3 = 15 s, plus waits of 1 + 2 + 4 + 4 = 11 s: the fourth wait would be 8 s but is capped at 4 s. |
| 4 | 500 | 2,000 | 4 | 2 | 11.5 | 4 x 2 = 8 s, plus waits of 0.5 + 1 + 2 = 3.5 s. |
| 5 | 250 | 8,000 | 6 | 4 | 31.75 | 6 x 4 = 24 s, plus waits of 0.25 + 0.5 + 1 + 2 + 4 = 7.75 s. |
| 6 | 500 | 8,000 | 1 | 8 | 8 | One attempt has no retry and no wait. |
| 7 | 500 | 8,000 | 7 | 8 | 79.5 | 7 x 8 = 56 s, plus waits of 0.5 + 1 + 2 + 4 + 8 + 8 = 23.5 s (the sixth would be 16 s but is capped at 8 s). |
| 8 | 100 | 800 | 4 | 1 | 4.7 | 4 x 1 = 4 s, plus waits of 0.1 + 0.2 + 0.4 = 0.7 s. |

For exploration the learner sets the base from 100 to 1,000 ms in steps of 50 (default 500), the cap from 800 to 8,000 ms in steps of 200 (default 8,000), N from 1 to 7 in steps of 1 (default 4), and T from 1 to 8 s in steps of 1 (default 8), and sees the timeline of attempts and waits with the worst-case total. A switch shows one random jittered run beneath the worst case, labeled "one random run."

**Provenance:** The formula and the default values (500 ms, 8,000 ms, 4 attempts, 8 s) are the chapter's `backoff.py` and `buddy_config.py` settings, and the default row matches `02-backoff-table.py`, which prints 35.5 s. The other settings are illustrative, and the sim labels them "illustrative."

**Rules:** Ceiling of the wait after failed attempt k is \( \min(\text{cap}, \text{base} \times 2^k) \) in milliseconds. There is no wait after the last attempt. Worst-case total in seconds is \( N \times T + (\text{sum of the } N - 1 \text{ ceilings}) / 1000 \). A jittered wait is a whole number of milliseconds from 0 to its ceiling. For N = 1 there are no waits.

**Learner Activity:**

1. The learner drags the four controls and watches the timeline lengthen or shorten.
2. The learner turns on the "one random run" switch and sees that the jittered run is never longer than the worst case.
3. The learner starts the 8 settings. Setting 1 is shown.
4. The learner types the worst-case total in seconds and submits.
5. The sim draws that setting's timeline and shows the Why text.
6. After setting 8, the sim shows the score. The learner should notice that in settings 3 and 7 the cap makes later waits equal, and that setting 6 has no waits at all.

**Feedback:** 8 settings, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The worst case is <answer> s: <Why>". The answer is revealed right after each submission, and a running score "n of 8" is shown.

**Starting State:** The default setting (500 ms, 8,000 ms, 4 attempts, 8 s) is drawn as a timeline with the question "What is the longest this request can take?"

**Chapter Anchors:** The chapter states that with a base of 500 ms, a cap of 8,000 ms, 4 attempts and an 8 s timeout the longest a request can take is 35.5 s; that the ceilings of the first six retries are 500, 1,000, 2,000, 4,000, 8,000 and 8,000 ms; and that with full jitter each wait is a random number from 0 to its ceiling.
</details>

### Showing the Link's State

A device that is retrying looks, from outside, exactly like one that has crashed, unless it says so. The status region (15 characters) carries one short phrase per state, and the message region carries the detail. Redrawing only these two regions is cheap (Chapter 6), so it can happen while the retry waits.

| State | Status region | Meaning for the student |
|-------|---------------|-------------------------|
| Ready | `online` | The last request worked |
| Working | `asking...`, `uploading`, `speaking` | Wait a moment |
| Waiting to retry | `retry 2/3` | It is trying again by itself |
| Cannot reach the server | `no server`, `OFFLINE` | The cached answers are available |
| Wrong login | `bad token` | Ask the teacher; retrying will not help |
| Wi-Fi gone | `no Wi-Fi` | Check the network |

### Offline Fallback

An **offline fallback** is what the device does when every retry has failed. The Pico cannot turn speech into words by itself, so offline it cannot understand a spoken question at all. What it can do is answer a small set of fixed questions from a copy of the school events saved earlier. When the device starts, `06-retry-fallback.py` downloads the events with `GET /v1/events` and saves them to `events_cache.json`. When asking fails after the last retry, it runs the same rule-based `decide()` from Chapter 1 against the saved copy, and the status region says `OFFLINE` so the student knows the answer may be out of date.

```python
def save_events(events):
    text = json.dumps(events)
    try:
        with open(CACHE_FILE) as f:
            if f.read() == text:
                return False          # unchanged: do not rewrite the flash
    except OSError:
        pass
    with open(CACHE_FILE, "w") as f:
        f.write(text)
    return True
```

The function writes only when the events changed, because flash memory wears out after many writes. Offline mode is deliberately small: a few kilobytes of JSON and about thirty lines of code, answering "next test" and "what is due" only. It also gives a different message for a 401 (`bad token`) than for a lost network, because showing yesterday's schedule to cover for a wrong token would hide a problem someone must fix. Chapter 16 replaces the simple event list with a real school calendar, and the cache should then hold whatever that chapter's server returns.

## Streaming Over a WebSocket

A **WebSocket** is a connection that stays open after it is set up, over which either side can send small messages, called frames, at any time. An HTTP request is one question and one answer, and each one pays for a connection and a block of headers (121 bytes of head for Chapter 13's request). With a WebSocket the Pico can send each 40 ms of speech the moment it exists, so the server starts working while the student is still talking, and the server can send speech back and also hear "stop" on the same connection.

A WebSocket starts as an HTTP request that asks to be upgraded.

| Step | Who | What |
|------|-----|------|
| 1 | Pico | `GET /v1/stream` with `Upgrade: websocket`, `Connection: Upgrade`, a random `Sec-WebSocket-Key`, and our `X-Buddy-Token` header |
| 2 | Server | Checks the token; answers `101 Switching Protocols` and a `Sec-WebSocket-Accept` computed from the key |
| 3 | Pico | Checks the accept value (SHA-1 of the key plus a fixed string, in base64) |
| 4 | Both | Send frames: a 1-byte opcode, a length, and the payload |

Every frame the Pico sends must be *masked*: the four-byte random mask is XORed over the payload, a rule of the standard meant to protect proxies. MicroPython has a built-in `websocket` module, but it does not mask the frames it writes, and a correct server closes the connection when it sees an unmasked frame from a client. So `wsclient.py` does the handshake and framing itself, in about 100 lines. The masking is the only clever part.

```python
def _xor_mask(data, key):
    n = len(data)
    repeated = (key * (n // 4 + 1))[:n]
    return (int.from_bytes(data, "big") ^ int.from_bytes(repeated, "big")).to_bytes(n, "big")
```

A Python loop over 1,024 bytes would take a long time per frame; this version turns the whole frame into one big integer and lets the interpreter's C code do the XOR. The overhead of a frame is small: 2 header bytes, 2 more for the length when the payload is 126 bytes or longer, and 4 for the mask, which is \( 2 + 2 + 4 = 8 \) bytes on a 1,024-byte frame, or 0.78 percent.

The messages of the book's server are listed in the table. Text frames are JSON, and binary frames are raw 16-bit audio at 12,800 Hz.

| Direction | Frame | Meaning |
|-----------|-------|---------|
| Pico to server | text `{"event": "start", "rate": 12800, "volume": 40}` | An utterance begins |
| Pico to server | binary, 1,024 bytes | A chunk of speech, sent as it is recorded |
| Pico to server | text `{"event": "end"}` | The button was released |
| Server to Pico | text `{"type": "reply", "heard": ..., "speak": ..., "show": ..., "next_mode": ...}` | The contract reply |
| Server to Pico | binary, up to 1,024 bytes | The spoken answer |
| Server to Pico | text `{"type": "audio_end"}` | That was the last of it |
| Pico to server | text `{"event": "cancel"}` | Barge-in: stop speaking |
| Server to Pico | text `{"type": "cancelled"}` | Stopped |

In `08-websocket-stream.py` nothing larger than the one 1,024-byte staging frame is kept while recording, which is design D in the explorer above. The cost moves to the network: if sending one frame stalls for longer than the microphone's ring buffer can hold (about 0.4 s, Chapter 8), audio is lost, so the script prints the slowest frame it sent. The script opens a new connection for each utterance. A connection that is held open for minutes must also answer the server's pings (the `recv()` in `wsclient.py` does so, but only while it is being called), which a program waiting for a button would not do.

Streaming all the time needs permission. A button-driven stream, as in this chapter, sends audio only when a student chooses to talk. An always-on stream that listens for a wake word and then sends is a different matter: it needs school and parent approval, covered in Chapter 17. The code is the same; the responsibility is not.

## Putting It All Together

You can now follow one spoken question from the button to the speaker, and say what happens when something goes wrong. The recording is converted to 16 bits as it arrives, uploaded in 2,048-byte chunks with a token, answered by the server's speech-to-text, brain, and text-to-speech, and streamed back into the speaker, where MODE can interrupt it. Around all of that, every wait has a limit, failures are sorted by kind, retries back off with jitter, and the last resort is a cached answer marked `OFFLINE`.

Key takeaways:

- A 5 s utterance is 128,000 bytes as 16-bit audio (256,000 as 32-bit), so convert while recording and allocate the buffer first.
- Chunked audio upload sends the header, then slices of a memoryview, to avoid a second copy of the recording; the book uses a known `Content-Length`, not `Transfer-Encoding: chunked`.
- The audio chunk size trades call count and overhead against latency: 2,048 bytes (80 ms) for HTTP and 1,024 bytes (one 40 ms frame) for a WebSocket.
- Speech-to-text and text-to-speech are server-side services behind stubs with marked places for a real one; keys live in the server's environment, and the server converts audio to 16-bit mono at 12,800 Hz.
- Streaming audio plays each chunk as it arrives, so the Pico never holds the whole answer.
- Barge-in is a button press, because the microphone must stay closed while the speaker plays (Chapter 8); stop without draining, then wait out the quiet tail.
- An authentication token goes in an `X-Buddy-Token` header, lives in `secrets.py`, is compared in constant time, and is rotated by accepting old and new together; a 401 is never retried.
- TLS encrypts, and only certificate verification (CA or pinned) also checks who the server is; `CERT_NONE` is for lab demos, and TLS has a memory cost of at least the 20,480 bytes of record buffers.
- Every socket wait needs a timeout, plus a total deadline; classify failures and retry only the ones that may pass, with exponential backoff and jitter.
- The offline fallback answers a few fixed questions from cached events, because the Pico cannot recognize speech itself.
- A WebSocket keeps one connection open for frames in both directions; the Pico must mask its frames, so `wsclient.py` does it by hand.

Test yourself with these three questions, and click each one to reveal its answer.

??? question "A 5 s recording uploads fine in tests, but the same code fails with MemoryError when the request is built as head + body. Why? Click to expand"
    Joining the header and the body creates a second 128,000-byte block while the 128,000-byte recording still exists, which needs 256,000 bytes in two blocks. Send the header first, then send slices of a `memoryview` of the recording, so no second copy is made.

??? question "Thirty devices retry a failed request at exactly 500 ms, 1,000 ms, and 2,000 ms after the failure. What is wrong, and what is the fix? Click to expand"
    The doubling is right but the timing is identical on every device, so the server gets all thirty requests at once on each round. Add jitter: wait a random time from 0 to the ceiling, so the requests spread out (about 6 per 100 ms window on the first retry instead of 30).

??? question "The device shows `bad token` after the school rotated the server's token. Should it retry? What should it do? Click to expand"
    No. A 401 means the token itself is wrong, and the same token will fail the same way. The device stops, shows `bad token`, and waits for someone to put the new `buddy_token` in `secrets.py`. During a rotation the server accepts both tokens for a while, so this should not happen if the steps are followed in order.

!!! mascot-celebration "A Link That Holds Up"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just uploaded speech in memory-safe chunks, put a token on every request, weighed TLS and certificate checking, and built timeouts, backoff with jitter, and an offline fallback. That is a network link that keeps working when the network does not.

In Chapter 15 we add MQTT, so the school can push an alert to the device without waiting for a question.
