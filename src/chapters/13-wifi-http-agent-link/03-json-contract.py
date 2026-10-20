# Chapter 13, Test 03: JSON and the request-reply contract
# Turns the Chapter 1 request and reply into JSON text with json.dumps, reads
# them back with json.loads, checks the field names, counts the BYTES (the
# number HTTP's Content-Length needs), and shows what happens to JSON that
# is not valid. Runs on your COMPUTER or on the Pico; needs no network.
#
# PASS: the request is 73 bytes and the reply is 103 bytes, the bad JSON raises
# an error instead of being accepted, and the last line says PASS.

NAME = "03-json-contract.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import json

REQUEST_FIELDS = {"device", "kind", "text"}
REPLY_FIELDS = {"speak", "show", "next_mode"}
MODES = {"clock", "listening", "thinking", "speaking", "settings"}

request = {"device": "desk-07", "kind": "question", "text": "when is my next test"}
reply = {"speak": "Your next test is Biology on Friday.",
         "show": "Biology test: Friday", "next_mode": "clock"}

ok = True


def report(label, text):
    # Content-Length counts bytes, so encode first. For plain English text the
    # byte count equals len(text), but a name with an accent does not.
    n = len(text.encode("utf-8"))
    print("{:<8} {:>3} bytes  {}".format(label, n, text))
    return n


print()
request_text = json.dumps(request)
reply_text = json.dumps(reply)
n_request = report("request", request_text)
n_reply = report("reply", reply_text)
ok = ok and n_request == 73 and n_reply == 103

print()
back = json.loads(request_text)
print("round trip keeps the data :", back == request)
print("request has the contract's fields:", set(back) == REQUEST_FIELDS)
print("reply has the contract's fields  :", set(json.loads(reply_text)) == REPLY_FIELDS)
print("reply mode is a known mode       :", reply["next_mode"] in MODES)
ok = ok and back == request and set(back) == REQUEST_FIELDS

print()
print("An accent changes bytes but not characters:")
report("accent", json.dumps({"text": "café"}))

print()
bad = ("{'device': 'desk-07'}",                       # single quotes
       '{"device": "desk-07",}',                      # trailing comma
       '{"device": "desk-07"',                        # missing brace
       "")                                            # nothing at all
for text in bad:
    try:
        json.loads(text)
        print("accepted (BAD):", repr(text))
        ok = False
    except (ValueError, TypeError):
        print("rejected      :", repr(text))

print()
print("PASS" if ok else "CHECK: a number differs from the chapter")

# Try This
#   1. Change the text to "when is my next test?" (add a question mark). How
#      many bytes does the request become? The Content-Length must follow.
#   2. Add a fourth field to the request. Which side must change before it
#      is accepted? (Hint: run server/test_server.py's bad-field case.)
