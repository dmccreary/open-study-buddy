#!/usr/bin/env python3
"""A minimal buddy server for the calendar brain (Chapter 16).

    python3 buddy_server_min.py --port 8080 --now 2026-10-19T09:00

POST /v1/ask    JSON {"device": "desk-07", "kind": "question", "text": "when is my next test"}
                -> JSON {"speak": ..., "show": ..., "next_mode": ...}   (Chapter 1's contract)
GET  /v1/health -> {"ok": true}

This follows the conventions of Chapters 13 and 14: the /v1/ paths, the three
request fields and three reply fields, and a token in the header
    X-Buddy-Token: <token>
taken from the BUDDY_TOKENS environment variable (several tokens separated by
commas, so you can rotate). With no token set, anyone on the network may ask:
fine on a trusted classroom LAN, not beyond it. It does only /v1/ask and
/v1/health. To get voice, WebSocket and the offline events list as well, keep
Chapter 14's server and drop in calendar_brain.py in place of its brain.py
(see that file). By default this server listens on 127.0.0.1 only; pass
--host 0.0.0.0 to serve the LAN.
"""
import argparse
import hmac
import json
import os
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import agent_config
import compose
from load_calendar import load_calendar

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_BODY = 2048          # same limit as Chapter 13


def make_handler(cfg, fixed_now, tokens):
    class Handler(BaseHTTPRequestHandler):
        server_version = "BuddyMin/1.0"

        def log_message(self, fmt, *args):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

        def _send(self, code, body):
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/v1/health":
                self._send(200, {"ok": True})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/v1/ask":
                return self._send(404, {"error": "not found"})
            if tokens:
                given = self.headers.get("X-Buddy-Token", "").encode()
                ok = False
                for token in tokens:                      # compare against every accepted token
                    ok |= hmac.compare_digest(given, token.encode())
                if not ok:
                    return self._send(401, {"error": "bad or missing token"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_BODY:
                    return self._send(413, {"error": "body must be 1 to %d bytes" % MAX_BODY})
                request = json.loads(self.rfile.read(length))
                text = request["text"]
                if not isinstance(text, str) or len(text) > 200:
                    raise ValueError("text")
            except (ValueError, KeyError, TypeError):
                return self._send(400, {"error": "send JSON with a 'text' field of at most 200 characters"})
            cal, _ = load_calendar(cfg)
            now = fixed_now.replace(tzinfo=cal.tz) if fixed_now else datetime.now(cal.tz)
            self._send(200, compose.answer(text, cal, now, cfg))

    return Handler


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--config", default=os.path.join(HERE, "agent.toml"))
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--now", help="pretend it is this school-local time (for demos)")
    args = p.parse_args(argv)
    cfg = agent_config.load(args.config)
    fixed = datetime.fromisoformat(args.now) if args.now else None
    tokens = [t.strip() for t in os.environ.get("BUDDY_TOKENS", "").split(",") if t.strip()]
    server = ThreadingHTTPServer((args.host, args.port), make_handler(cfg, fixed, tokens))
    print("listening on http://%s:%d  (token %s)" % (args.host, args.port, "required" if tokens else "not required"))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
