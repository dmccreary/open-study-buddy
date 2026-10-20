#!/usr/bin/env python3
"""Chapter 13: the smallest useful buddy server.

Runs on your COMPUTER (or a school Raspberry Pi), never on the Pico. It uses
only Python's standard library, so there is nothing to install.

    python3 buddy_server.py                 # listens on 0.0.0.0:8080
    python3 buddy_server.py --port 9000     # another port

It implements the Chapter 1 request-reply contract with the rule-based
decide() from Chapter 1. The brain is one function, so Chapters 14 and 16 can
swap it for something smarter without touching the Pico.

    GET  /v1/health   -> {"ok": true, "server": "buddy", "version": "1.0"}
    POST /v1/ask      -> request  {"device": "...", "kind": "question", "text": "..."}
                         reply    {"speak": "...", "show": "...", "next_mode": "clock"}

Anything wrong with a request gets a JSON error body {"error": "..."} and a
4xx status, so a student can see exactly what the server did not like.

PLAIN HTTP, NO LOGIN. That is acceptable only on a trusted classroom network
(Chapter 13). Chapter 14 adds a token and HTTPS.
"""

import argparse
import json
import os
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

NAME = "buddy_server.py"
VERSION = "1.0"

HERE = os.path.dirname(os.path.abspath(__file__))
REQUEST_FIELDS = {"device", "kind", "text"}
KINDS = {"question"}
MODES = {"clock", "listening", "thinking", "speaking", "settings"}
MAX_BODY = 2048          # a real request is about 75 bytes; refuse anything bigger
MAX_TEXT = 200
MAX_SHOW = 30            # the message region on the round display fits 30 characters


# ----------------------------------------------------------------------
# The brain: Chapter 1's rule-based decide(), made safe for a missing event
# ----------------------------------------------------------------------

def load_events(path=None):
    """Events are a list of {"title": ..., "day": ...}. Chapter 16 replaces
    this file with a real school calendar."""
    path = path or os.path.join(HERE, "events.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def next_event_with_prefix(events, prefix):
    """The first event whose title starts with prefix, prefix removed."""
    for event in events:
        if event["title"].startswith(prefix):
            return {"title": event["title"][len(prefix):].strip(),
                    "day": event["day"]}
    return None


def decide(text, events):
    """Return (speak, show) for a question."""
    words = text.lower()
    if "test" in words:
        event = next_event_with_prefix(events, "TEST:")
        if event is None:
            return "I do not see a test coming up.", "No tests coming up"
        return ("Your next test is {} on {}.".format(event["title"], event["day"]),
                "{} test: {}".format(event["title"], event["day"]))
    if "due" in words:
        event = next_event_with_prefix(events, "DUE:")
        if event is None:
            return "Nothing is due soon.", "Nothing due soon"
        return ("{} is due on {}.".format(event["title"], event["day"]),
                "{} due: {}".format(event["title"], event["day"]))
    return ("Sorry, I only know about tests and due dates.",
            "I only know tests, due")


def make_reply(text, events):
    speak, show = decide(text, events)
    return {"speak": speak, "show": show[:MAX_SHOW], "next_mode": "clock"}


def check_request(data):
    """Return an error string, or None when the request fits the contract."""
    if not isinstance(data, dict):
        return "request must be a JSON object"
    if set(data) != REQUEST_FIELDS:
        return "request fields must be exactly {}".format(sorted(REQUEST_FIELDS))
    for name in REQUEST_FIELDS:
        if not isinstance(data[name], str):
            return "field '{}' must be a string".format(name)
    if data["kind"] not in KINDS:
        return "kind must be one of {}".format(sorted(KINDS))
    if not data["device"] or len(data["device"]) > 32:
        return "device must be 1 to 32 characters"
    if len(data["text"]) > MAX_TEXT:
        return "text is longer than {} characters".format(MAX_TEXT)
    return None


# ----------------------------------------------------------------------
# The HTTP part
# ----------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    # HTTP/1.0 closes the connection after every reply. That is what the
    # Pico's requests library expects (it sends "Connection: close").
    protocol_version = "HTTP/1.0"
    events = []

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/v1/health":
            self.send_json(200, {"ok": True, "server": "buddy", "version": VERSION})
        elif self.path == "/v1/ask":
            self.send_json(405, {"error": "use POST for /v1/ask"})
        else:
            self.send_json(404, {"error": "no such endpoint"})

    def do_POST(self):
        if self.path != "/v1/ask":
            self.send_json(404, {"error": "no such endpoint"})
            return
        length_text = self.headers.get("Content-Length")
        if length_text is None or not length_text.isdigit():
            self.send_json(411, {"error": "Content-Length is required"})
            return
        length = int(length_text)
        if length > MAX_BODY:
            self.send_json(413, {"error": "body is larger than {} bytes".format(MAX_BODY)})
            return
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            self.send_json(400, {"error": "body is not valid JSON"})
            return
        problem = check_request(data)
        if problem:
            self.send_json(400, {"error": problem})
            return
        reply = make_reply(data["text"], self.events)
        self.log_message("%s", "ask from {}: {!r} -> {!r}".format(
            data["device"], data["text"], reply["show"]))
        self.send_json(200, reply)


def lan_address():
    """The address other computers on your network would use to reach this
    one. (Connecting a UDP socket sends nothing; it only picks a route.)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--events", default=None, help="path to an events JSON file")
    args = parser.parse_args()

    Handler.events = load_events(args.events)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print("{} v{}".format(NAME, VERSION))
    print("listening on {}:{}".format(args.host, args.port))
    print("put this in buddy_config.py on the Pico:  BUDDY_HOST = \"{}\"".format(lan_address()))
    print("(plain HTTP, no login: trusted classroom network only)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
