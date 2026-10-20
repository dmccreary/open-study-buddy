#!/usr/bin/env python3
"""Chapter 18: make a small events.json for the Pico.

The Cedar Ridge calendar has 92 events (27 KB). The homework reminder only
needs TEST: and DUE: items, with an id, title, and date. This keeps those and
writes a file about 4 KB big, which fits easily in the Pico's memory.

    python3 trim_events.py ../../../../docs/schools/cedar-ridge-high-school/events.json events.json
    mpremote fs cp events.json :events.json
"""
import json
import sys

if len(sys.argv) != 3:
    print(__doc__)
    sys.exit(2)

with open(sys.argv[1]) as f:
    data = json.load(f)
keep = [{"id": e["id"], "title": e["title"], "date": e["date"]}
        for e in data["events"] if e["title"].startswith(("TEST:", "DUE:"))]
with open(sys.argv[2], "w") as f:
    json.dump(keep, f, separators=(",", ":"))
print("kept {} of {} events".format(len(keep), len(data["events"])))
