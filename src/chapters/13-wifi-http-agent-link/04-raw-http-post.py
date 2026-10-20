# Chapter 13, Test 04: Read an HTTP POST as plain text
# Builds the request the Pico sends to the buddy server, prints it with every
# line ending made visible, checks that Content-Length equals the real number
# of body bytes, then reads a canned server reply with the same code the Pico
# uses. Runs on your COMPUTER or on the Pico; it sends nothing over the network.
#
# PASS: the request is made of the parts the chapter names, Content-Length
# says 73 and the body really is 73 bytes, the canned reply parses to status
# 200, and the last line says PASS.

NAME = "04-raw-http-post.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import json

import buddy_config
import rawhttp

request = {"device": buddy_config.DEVICE_ID, "kind": "question",
           "text": "when is my next test"}
raw = rawhttp.build_post(buddy_config.BUDDY_HOST, buddy_config.BUDDY_PORT,
                         "/v1/ask", request)

head, _, body = raw.partition(b"\r\n\r\n")
print()
print("The request, {} bytes in all (\\r\\n shown as <CRLF>):".format(len(raw)))
print()
for line in head.decode().split("\r\n"):
    print("  " + line + "<CRLF>")
print("  <CRLF>              <- the blank line: headers end here")
print("  " + body.decode())
print()

declared = int([l for l in head.decode().split("\r\n")
                if l.lower().startswith("content-length")][0].split(":")[1])
print("request line : {}".format(head.decode().split("\r\n")[0]))
print("header lines : {}".format(len(head.decode().split("\r\n")) - 1))
print("body bytes   : {}   Content-Length says: {}".format(len(body), declared))
ok = declared == len(body)


class FakeSocket:
    """Hands out a canned reply in small pieces, the way a network does."""

    def __init__(self, data):
        self.data = data

    def recv(self, n):
        piece, self.data = self.data[:min(n, 40)], self.data[min(n, 40):]
        return piece


reply_body = json.dumps({"speak": "Your next test is Biology on Friday.",
                         "show": "Biology test: Friday", "next_mode": "clock"})
canned = ("HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n"
          "Content-Length: {}\r\n\r\n{}").format(len(reply_body), reply_body).encode()
status, headers, body = rawhttp.read_response(FakeSocket(canned))
print()
print("canned reply : status {}, {} headers, body {} bytes".format(
    status, len(headers), len(body)))
print("parsed       :", json.loads(body)["show"])
ok = ok and status == 200 and json.loads(body)["next_mode"] == "clock"

print()
print("PASS" if ok else "CHECK: Content-Length or the reply parser is wrong")

# Try This
#   1. Change the text and run again. Content-Length changes with it. What
#      goes wrong if a hand-written request says 60 but sends 73 bytes?
#   2. Change "HTTP/1.0" to "HTTP/1.1" in rawhttp.py. What would the server
#      then be allowed to do with the connection after replying?
