# Chapter 14 code: Streaming Speech, Security, and Network Resilience

Chapter: `docs/chapters/14-streaming-security-resilience/index.md`

Chapter 14's server replaces Chapter 13's. It needs Python 3.10+ and, for the
WebSocket part only, `pip install websockets` (tested with websockets 16).

```bash
# 1. On your computer: make a token and start the servers (two terminals)
python3 -c "import secrets; print(secrets.token_urlsafe(24))"      # copy the output
cd src/chapters/14-streaming-security-resilience/server
export BUDDY_TOKENS="paste-the-token-here"
python3 buddy_server.py --debug            # HTTP :8080  (--debug adds /v1/slow and /v1/flaky)
python3 ws_server.py                       # WebSocket :8081  (second terminal, same BUDDY_TOKENS)

# 2. Edit buddy_config.py: BUDDY_HOST = the address the server printed.
#    Add the SAME token to the kit's secrets.py:   buddy_token = "paste-the-token-here"

# 3. Upload and run
cd src/chapters
./upload-chapter.sh 14 04-upload-voice.py
```

Check both servers with no Pico at all: `python3 server/test_client.py` (starts
its own servers on spare ports and a random token, and ends with PASS).

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-chunk-arithmetic.py` | none (also runs on a computer; on the Pico it reports which recordings fit) | 5 s is 128,000 bytes; 2,048-byte chunks make 63; PASS |
| `02-backoff-table.py` | none (also runs on a computer) | Ceilings 500 to 8,000 ms; worst case 35.5 s; jitter's busiest window far below 30; PASS |
| `03-record-utterance.py` | Microphone + display + MODE | Bytes match the time held; **worst conversion under 20,000 us**; PASS |
| `04-upload-voice.py` | Whole kit + HTTP server | Status walks recording, uploading, speaking; beeps play; timings print; MODE interrupts |
| `05-timeouts-and-failures.py` | Wi-Fi + server with `--debug` | Six cases end as the "expected" column says; PASS |
| `06-retry-fallback.py` | Display + MODE + UP + Wi-Fi + server with `--debug` | Retries show `retry 1/3`...; with the server stopped, MODE ends in OFFLINE with the cached answer |
| `07-tls-probe.py` | Wi-Fi + HTTPS server + `ca.der` on the Pico | Cases 1 to 3 ok; the wrong certificate is refused; the heap and time columns are yours to record |
| `08-websocket-stream.py` | Whole kit + WebSocket server | Streams while you talk, plays the answer, MODE interrupts it |
| `buddy_config.py`, `wifi_link.py`, `backoff.py`, `buddy_http.py`, `buddy_client.py`, `utterance.py`, `screen.py`, `offline.py`, `wsclient.py` | helper modules | |
| `server/` | your computer | `test_client.py` ends with PASS |

## Server files (stay on your computer)

| File | What it is |
|------|------------|
| `server/buddy_server.py` | HTTP/HTTPS server: `/v1/health`, `/v1/ask`, `/v1/events`, `/v1/voice`, `/v1/speech/<id>`; token login; `--tls CERT KEY`; `--debug` |
| `server/ws_server.py` | WebSocket server, `/v1/stream` on port 8081; same token; `--tls CERT KEY` |
| `server/brain.py` | the rule-based `decide()` and `make_reply()` (swap this for a smarter brain) |
| `server/stt.py`, `server/tts.py` | speech-to-text and text-to-speech hooks. The default **stub** backends do not recognize or speak anything; the places to add a real service are marked, and keys come from `STT_API_KEY` / `TTS_API_KEY` in the **server's** environment |
| `server/make-cert.sh` | `./make-cert.sh <server ip or name>` makes `server.pem`, `server.key`, `ca.der` for the HTTPS lab |
| `server/test_client.py` | tests everything above with no Pico |

The server never writes a recording to disk, and does not log what was said
unless you start it with `--log-text`.

## The most important tests for the book

- `03-record-utterance.py`: **worst conversion time per 20 ms read**. If it is
  over 20,000 us, the chapter's live 16-bit recording does not work and the
  chapter must say to record 32-bit and convert afterwards.
- `04-upload-voice.py`: **upload+server ms** for a 1 s and a 5 s recording and
  **first audio ms**. The chapter's latency table is arithmetic and estimates
  until these exist.
- `07-tls-probe.py`: **connect time and heap used** for cases 2 and 3, whether
  case 3 verifies at all with an IP address in the certificate, and whether the
  wrong-certificate case is refused.
- `08-websocket-stream.py`: does `wsclient.py` connect and stream from the
  Pico (it has only been run from a computer); the **slowest frame** time.
- `05-timeouts-and-failures.py`: the milliseconds for each failure on your network.

## What has been checked, and what has not

- `server/test_client.py` ran green (all checks ok): logins, token rotation,
  3 s upload, speech download, volume, 411 for chunked, 413 for oversize,
  slow and flaky endpoints, WebSocket handshake, streaming, barge-in, 1009 on
  too much audio, and the same over HTTPS and WSS with a throw-away certificate.
- Pico scripts `01` to `08` ran to completion on a computer against a fake
  `machine` / `network` / `time` layer with real sockets talking to the real
  servers (including TLS, the certificate check, a deliberately wrong
  certificate, an unreachable address, and the WebSocket barge-in). This
  catches typos and logic errors.
- Nothing here has run on the Pico yet. Not checked on the device: all timings
  and heap numbers, the I2S conversion speed, TLS on MicroPython's `ssl`
  (including certificates with an IP address in subjectAltName and the date
  check), `wsclient.py`'s big-integer masking trick, and `str.format` `{:,}`.
- Speech-to-text and text-to-speech are stubs. No account, key, or real
  recognition was used.
