#!/usr/bin/env python3
"""Chapter 13: check the buddy server without a Pico.

Runs on your COMPUTER:  python3 test_server.py

It starts buddy_server.py's handler on a spare port, sends it the requests the
Pico will send (and some bad ones), and checks the status codes and the reply
shape. To test a server that is already running instead, pass its address:

    python3 test_server.py 192.168.1.50 8080

PASS: every line says ok, and the last line says PASS.
"""

import http.client
import json
import sys
import threading

import buddy_server

REPLY_FIELDS = {"speak", "show", "next_mode"}
problems = []


def check(label, condition, detail=""):
    print("{:<4} {}{}".format("ok" if condition else "FAIL", label,
                              "  " + detail if detail else ""))
    if not condition:
        problems.append(label)


def call(host, port, method, path, body=None, headers=None):
    conn = http.client.HTTPConnection(host, port, timeout=5)
    try:
        conn.request(method, path, body=body, headers=headers or {})
        r = conn.getresponse()
        return r.status, r.read()
    finally:
        conn.close()


def run(host, port):
    status, body = call(host, port, "GET", "/v1/health")
    check("GET /v1/health is 200", status == 200, body.decode())

    good = json.dumps({"device": "desk-07", "kind": "question",
                       "text": "when is my next test"})
    status, body = call(host, port, "POST", "/v1/ask", good,
                        {"Content-Type": "application/json"})
    reply = json.loads(body)
    check("POST /v1/ask is 200", status == 200)
    check("reply has exactly speak, show, next_mode", set(reply) == REPLY_FIELDS)
    check("Chapter 1 answer", reply["speak"] == "Your next test is Biology on Friday.",
          reply["speak"])
    check("show fits the display", len(reply["show"]) <= 30, reply["show"])
    print("     body was {} bytes, reply was {} bytes".format(len(good), len(body)))

    status, body = call(host, port, "POST", "/v1/ask", json.dumps(
        {"device": "desk-07", "kind": "question", "text": "What is due this week?"}))
    check("due question", json.loads(body)["speak"] == "Lab report is due on Thursday.")

    status, body = call(host, port, "POST", "/v1/ask", json.dumps(
        {"device": "desk-07", "kind": "question", "text": "Do I have anything big this week?"}))
    check("unknown question gets the apology",
          json.loads(body)["speak"].startswith("Sorry"))

    status, body = call(host, port, "POST", "/v1/ask", "{'device': 'desk-07'}")
    check("single quotes are not JSON: 400", status == 400, body.decode())

    status, body = call(host, port, "POST", "/v1/ask", json.dumps(
        {"device": "desk-07", "text": "hi"}))
    check("missing field: 400", status == 400, body.decode())

    status, body = call(host, port, "POST", "/v1/ask", json.dumps(
        {"device": "desk-07", "kind": "shout", "text": "hi"}))
    check("unknown kind: 400", status == 400, body.decode())

    status, body = call(host, port, "POST", "/v1/ask", "x" * 5000)
    check("oversize body: 413", status == 413, body.decode())

    status, body = call(host, port, "GET", "/v1/ask")
    check("GET on /v1/ask: 405", status == 405)
    status, body = call(host, port, "POST", "/v1/nothing", "{}")
    check("unknown path: 404", status == 404)


if len(sys.argv) == 3:
    run(sys.argv[1], int(sys.argv[2]))
else:
    buddy_server.Handler.events = buddy_server.load_events()
    server = buddy_server.ThreadingHTTPServer(("127.0.0.1", 0), buddy_server.Handler)
    buddy_server.Handler.log_message = lambda *a: None
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        run("127.0.0.1", server.server_address[1])
    finally:
        server.shutdown()
        server.server_close()

print()
print("PASS: the server follows the contract." if not problems
      else "CHECK: {} problem(s): {}".format(len(problems), ", ".join(problems)))
