#!/usr/bin/env python3
"""Chapter 14: the buddy server with a login, voice, and optional HTTPS.

Runs on your COMPUTER (or a school Raspberry Pi), never on the Pico. Standard
library only for this file; the WebSocket server (ws_server.py) needs
`pip install websockets`.

    export BUDDY_TOKENS="pick-a-long-random-string"
    python3 buddy_server.py                          # HTTP on 0.0.0.0:8080
    python3 buddy_server.py --tls server.pem server.key --port 8443   # HTTPS
    python3 buddy_server.py --no-auth                # lab only: no login at all

Every endpoint except /v1/health needs the header  X-Buddy-Token: <token>.
BUDDY_TOKENS may list several tokens separated by commas, so you can ROTATE:
add the new token, update the Pico, then remove the old one.

    GET  /v1/health           open; {"ok": true}
    POST /v1/ask              the Chapter 13 contract, JSON in, JSON out
    GET  /v1/events           the school events, for the Pico's offline cache
    POST /v1/voice            a recording: 16-bit mono PCM, Content-Length required,
                              header X-Audio-Rate. Replies with the contract plus
                              "heard" (the transcript) and "audio" (where to GET the speech)
    GET  /v1/speech/<id>?volume=40   the spoken reply as raw 16-bit mono PCM at the
                              device's rate (12,800 Hz), Content-Length known
    GET  /v1/slow?ms=3000     (--debug) answers after a delay: practice for timeouts
    GET  /v1/flaky?fail=2     (--debug) fails with 503 twice, then succeeds: practice for retries

The recording is held in memory only while it is being transcribed. It is never
written to disk.
"""

import argparse
import hmac
import json
import os
import secrets as pysecrets
import socket
import ssl
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import brain
import stt
import tts

NAME = "buddy_server.py (chapter 14)"
VERSION = "1.0"

DEVICE_RATE = 12800                 # samples per second the Pico's speaker is set up for
MAX_AUDIO_BYTES = 10 * DEVICE_RATE * 2     # 10 seconds of 16-bit mono = 256,000 bytes
MAX_JSON_BYTES = 2048
SPEECH_TTL_S = 60
SPEECH_MAX_ITEMS = 20
SPEECH_CHUNK = 2048

TOKENS = []                         # filled in main()
OPEN_PATHS = {"/v1/health"}
DEBUG = False
LOG_TEXT = False                    # transcripts are personal data: off unless asked for
EVENTS = []
SPEECH = {}                         # id -> (expires_at, pcm_bytes_at_full_scale)
LOCK = threading.Lock()
FLAKY = {"count": 0}


def token_ok(supplied):
    """Compare in constant time, against every accepted token."""
    ok = False
    for token in TOKENS:
        ok |= hmac.compare_digest(supplied.encode(), token.encode())
    return ok


def remember_speech(pcm):
    with LOCK:
        now = time.time()
        for key in [k for k, (exp, _) in SPEECH.items() if exp < now]:
            del SPEECH[key]
        while len(SPEECH) >= SPEECH_MAX_ITEMS:
            del SPEECH[min(SPEECH, key=lambda k: SPEECH[k][0])]
        speech_id = pysecrets.token_hex(4)
        SPEECH[speech_id] = (now + SPEECH_TTL_S, pcm)
        return speech_id


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    # -- helpers --------------------------------------------------------
    def reply(self, status, body, content_type, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, payload):
        self.reply(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def authorized(self, path):
        if path in OPEN_PATHS or not TOKENS:
            return True
        supplied = self.headers.get("X-Buddy-Token", "")
        if token_ok(supplied):
            return True
        self.log_message("%s", "REFUSED: missing or wrong token for " + path)
        self.send_json(401, {"error": "missing or wrong X-Buddy-Token"})
        return False

    def read_body(self, limit):
        """The body bytes, or None after sending an error. Content-Length must be
        present: this server does not accept Transfer-Encoding: chunked."""
        if "chunked" in self.headers.get("Transfer-Encoding", "").lower():
            self.send_json(411, {"error": "chunked bodies are not accepted; send Content-Length"})
            return None
        length = self.headers.get("Content-Length")
        if length is None or not length.isdigit():
            self.send_json(411, {"error": "Content-Length is required"})
            return None
        length = int(length)
        if length > limit:
            self.send_json(413, {"error": "body is larger than {} bytes".format(limit)})
            return None
        data = bytearray()
        while len(data) < length:
            piece = self.rfile.read(min(65536, length - len(data)))
            if not piece:
                self.send_json(400, {"error": "body ended after {} of {} bytes".format(len(data), length)})
                return None
            data += piece
        return bytes(data)

    # -- GET ------------------------------------------------------------
    def do_GET(self):
        url = urlparse(self.path)
        path, query = url.path, parse_qs(url.query)
        if not self.authorized(path):
            return
        if path == "/v1/health":
            self.send_json(200, {"ok": True, "server": "buddy", "version": VERSION,
                                 "auth": bool(TOKENS)})
        elif path == "/v1/events":
            self.send_json(200, EVENTS)
        elif path.startswith("/v1/speech/"):
            self.send_speech(path[len("/v1/speech/"):], query)
        elif path == "/v1/slow" and DEBUG:
            ms = max(0, min(30000, int(query.get("ms", ["1000"])[0])))
            time.sleep(ms / 1000)
            self.send_json(200, {"ok": True, "waited_ms": ms})
        elif path == "/v1/flaky" and DEBUG:
            fail = int(query.get("fail", ["2"])[0])
            with LOCK:
                if FLAKY["count"] < fail:
                    FLAKY["count"] += 1
                    n = FLAKY["count"]
                    self.send_json(503, {"error": "try again (failure {} of {})".format(n, fail)})
                    return
                FLAKY["count"] = 0
            self.send_json(200, {"ok": True})
        elif path in ("/v1/ask", "/v1/voice"):
            self.send_json(405, {"error": "use POST for " + path})
        else:
            self.send_json(404, {"error": "no such endpoint"})

    def send_speech(self, speech_id, query):
        with LOCK:
            item = SPEECH.get(speech_id)
        if item is None or item[0] < time.time():
            self.send_json(404, {"error": "no such speech (it may have expired)"})
            return
        volume = int(query.get("volume", ["40"])[0])
        pcm = tts.apply_volume(item[1], volume)
        self.reply(200, pcm, "audio/L16;rate={};channels=1".format(DEVICE_RATE),
                   {"X-Audio-Rate": str(DEVICE_RATE)})

    # -- POST -----------------------------------------------------------
    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/v1/ask", "/v1/voice"):
            self.send_json(404, {"error": "no such endpoint"})
            return
        if not self.authorized(path):
            return
        if path == "/v1/ask":
            self.post_ask()
        else:
            self.post_voice()

    def post_ask(self):
        raw = self.read_body(MAX_JSON_BYTES)
        if raw is None:
            return
        try:
            data = json.loads(raw.decode("utf-8"))
            ok = (isinstance(data, dict) and set(data) == {"device", "kind", "text"}
                  and all(isinstance(v, str) for v in data.values())
                  and data["kind"] == "question" and 0 < len(data["device"]) <= 32
                  and len(data["text"]) <= 200)
        except (UnicodeDecodeError, ValueError):
            ok = False
        if not ok:
            self.send_json(400, {"error": "body does not match the request contract"})
            return
        reply = brain.make_reply(data["text"], EVENTS)
        self.log_message("%s", "ask from {}{}".format(
            data["device"], ": {!r}".format(data["text"]) if LOG_TEXT else ""))
        self.send_json(200, reply)

    def post_voice(self):
        try:
            rate = int(self.headers.get("X-Audio-Rate", ""))
        except ValueError:
            rate = 0
        if rate != DEVICE_RATE:
            self.send_json(400, {"error": "X-Audio-Rate must be {}".format(DEVICE_RATE)})
            return
        pcm = self.read_body(MAX_AUDIO_BYTES)
        if pcm is None:
            return
        if len(pcm) % 2:
            self.send_json(400, {"error": "16-bit audio must have an even number of bytes"})
            return
        device = self.headers.get("X-Buddy-Device", "?")[:32]
        reply = voice_reply(pcm, rate)
        self.log_message("%s", "voice from {}: {} bytes ({:.2f} s){}".format(
            device, len(pcm), len(pcm) / 2 / rate,
            " heard {!r}".format(reply["heard"]) if LOG_TEXT else ""))
        self.send_json(200, reply)


def answer_audio(pcm, rate):
    """Shared by the HTTP and WebSocket servers: audio in, (contract reply with
    "heard", spoken answer as PCM) out. This is where the swappable pieces plug in:
    stt.transcribe -> brain.make_reply -> tts.synthesize."""
    heard = stt.transcribe(pcm, rate)
    reply = {"heard": heard, **brain.make_reply(heard, EVENTS)}
    return reply, tts.synthesize(reply["speak"], DEVICE_RATE)


def voice_reply(pcm, rate):
    reply, speech = answer_audio(pcm, rate)
    reply["audio"] = "/v1/speech/" + remember_speech(speech)
    return reply


def lan_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def configure_tokens(no_auth):
    global TOKENS
    if no_auth:
        TOKENS = []
        print("WARNING: --no-auth. Anyone who can reach this port can use it.")
        return
    TOKENS = [t.strip() for t in os.environ.get("BUDDY_TOKENS", "").split(",") if t.strip()]
    if not TOKENS:
        sys.exit("Set BUDDY_TOKENS (one or more tokens, comma separated), or use --no-auth for a lab demo.\n"
                 "A good token:  python3 -c \"import secrets; print(secrets.token_urlsafe(24))\"")
    if any(len(t) < 16 for t in TOKENS):
        print("WARNING: a token shorter than 16 characters is easy to guess.")


def main():
    global DEBUG, EVENTS, LOG_TEXT
    parser = argparse.ArgumentParser(description="Open Study Buddy server, chapter 14")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--no-auth", action="store_true")
    parser.add_argument("--debug", action="store_true", help="enable /v1/slow and /v1/flaky")
    parser.add_argument("--log-text", action="store_true",
                        help="print what students said and asked (personal data: lab use only)")
    parser.add_argument("--tls", nargs=2, metavar=("CERT.pem", "KEY.pem"),
                        help="serve HTTPS with this certificate and key")
    args = parser.parse_args()

    configure_tokens(args.no_auth)
    DEBUG = args.debug
    LOG_TEXT = args.log_text
    EVENTS = brain.load_events()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    scheme = "http"
    if args.tls:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(*args.tls)
        server.socket = context.wrap_socket(server.socket, server_side=True,
                                            do_handshake_on_connect=False)
        scheme = "https"
    print("{} v{}".format(NAME, VERSION))
    print("{} on {}:{}  (auth {}, debug endpoints {})".format(
        scheme, args.host, args.port, "OFF" if not TOKENS else "on", "on" if DEBUG else "off"))
    print("BUDDY_HOST = \"{}\"".format(lan_address()))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
