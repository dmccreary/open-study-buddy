#!/usr/bin/env python3
"""Ask the school agent a question from the command line (Chapter 16).

    python3 ask.py "when is my next test" --now 2026-10-19T09:00
    python3 ask.py --briefing --now 2026-10-19T07:30

--now is the school's local time (the demo date for Cedar Ridge is
2026-10-19). Without it, the real current time is used.
"""
import argparse
import json
import os
import sys
from datetime import datetime

import agent_config
import compose
from load_calendar import load_calendar

HERE = os.path.dirname(os.path.abspath(__file__))


def local_now(cal, text=None):
    if text:
        return datetime.fromisoformat(text).replace(tzinfo=cal.tz)
    return datetime.now(cal.tz)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("question", nargs="?", default="")
    p.add_argument("--config", default=os.path.join(HERE, "agent.toml"))
    p.add_argument("--now")
    p.add_argument("--briefing", action="store_true")
    args = p.parse_args(argv)
    cfg = agent_config.load(args.config)
    cal, _ = load_calendar(cfg)
    now = local_now(cal, args.now)
    if args.briefing:
        result = compose.daily_briefing(cal, now, cfg)
        if result is None:
            print("No briefing: %s is not a school day." % now.date())
            return 0
        print(json.dumps({"speak": result["speak"], "show": result["show"]}, indent=2))
        return 0
    if not args.question:
        p.error("give a question, or use --briefing")
    print(json.dumps(compose.answer(args.question, cal, now, cfg), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
