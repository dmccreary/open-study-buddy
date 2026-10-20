#!/usr/bin/env python3
"""Check agent.toml and the calendar it points at (Chapter 16).

    python3 check_config.py [path/to/agent.toml]

Prints every problem in plain English and exits 1 if any are errors.
"""
import os
import sys

import agent_config
from load_calendar import load_calendar


def main(argv):
    path = argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.toml")
    cfg = agent_config.load(path)
    errors, warnings = agent_config.check(cfg)
    print("Checking %s" % path)
    if not errors:
        try:
            cal, status = load_calendar(cfg)
        except Exception as error:               # a clear message beats a traceback in a classroom
            errors.append("could not load the calendar: %s" % error)
        else:
            print("Calendar: %s, %d events (%s)" % (cal.source, len(cal.events), status))
            cats = {}
            for e in cal.events:
                cats[e.category] = cats.get(e.category, 0) + 1
            print("  " + ", ".join("%s %d" % (k, v) for k, v in sorted(cats.items())))
            warnings += ["calendar: " + w for w in cal.warnings]
            names = {c["name"] for c in cfg["courses"]}
            used = {e.course for e in cal.events if e.course}
            for missing in sorted(names - used):
                warnings.append("course %r appears in no event title" % missing)
            for unknown in sorted(
                    {e.title for e in cal.events if e.category in ("test", "due") and not e.course}):
                warnings.append("no course matched in %r" % unknown)
    for line in errors:
        print("ERROR  :", line)
    for line in warnings:
        print("warning:", line)
    print("%d error(s), %d warning(s)" % (len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
