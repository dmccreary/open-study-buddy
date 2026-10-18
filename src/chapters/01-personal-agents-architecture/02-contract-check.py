# Chapter 1, Test 02: Check the request-reply contract
# Runs on your COMPUTER (python3 02-contract-check.py). It reads request.json
# and reply.json from this folder and checks that they have exactly the fields
# the chapter's contract promises. The terminal can only work with a server
# whose replies look like this, no matter what brain is behind it.
#
# PASS: both files have the fields shown, and the last line says PASS.

import json
import os

NAME = "02-contract-check.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

HERE = os.path.dirname(os.path.abspath(__file__))
REQUEST_FIELDS = {"device", "kind", "text"}
REPLY_FIELDS = {"speak", "show", "next_mode"}
MODES = {"clock", "listening", "thinking", "speaking", "settings"}


def load(name):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


request = load("request.json")
reply = load("reply.json")
problems = []

if set(request) != REQUEST_FIELDS:
    problems.append("request fields are {}, expected {}".format(
        sorted(request), sorted(REQUEST_FIELDS)))
if set(reply) != REPLY_FIELDS:
    problems.append("reply fields are {}, expected {}".format(
        sorted(reply), sorted(REPLY_FIELDS)))
if reply.get("next_mode") not in MODES:
    problems.append("next_mode {!r} is not one of {}".format(
        reply.get("next_mode"), sorted(MODES)))

print("request:", request)
print("reply  :", reply)
print()
if problems:
    for p in problems:
        print("PROBLEM:", p)
else:
    print("PASS: both messages match the contract.")
