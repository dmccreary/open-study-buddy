#!/usr/bin/env python3
"""Chapter 17: check that a Privacy and Consent Plan is complete.

    python3 check_plan.py privacy-and-consent-plan-cedar-ridge-example.md

It reads lines of the form  - **Field name:** value  and reports:
  - fields that are missing, empty, or still contain a <placeholder> or TODO
  - rule violations, for example always-on listening without the approvals

A passing check means the plan is COMPLETE and CONSISTENT. It does not mean the
plan is good, or that your school will approve it. Humans decide that.
"""
import re
import sys

REQUIRED = [
    "School and class", "Plan owner", "Date prepared", "Review date", "Purpose",
    "Who is near the microphone", "Listening mode", "Why this mode is needed",
    "Hardware mute and indicator", "Data collected", "Audio stored",
    "Transcripts stored", "Retention days", "Where processing happens",
    "Outside services that receive data", "Who can read transcripts or logs",
    "Deletion process", "Agent permissions", "Secrets handling", "Network",
    "Incident contact", "Parent notice and opt-out", "Policies consulted",
    "School approval", "Parent consent record", "Always-on approval",
]

FIELD = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")


def read_fields(text):
    fields = {}
    for line in text.splitlines():
        m = FIELD.match(line.strip())
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields


def check(fields):
    problems = []
    for name in REQUIRED:
        value = fields.get(name)
        if value is None:
            problems.append("missing field: " + name)
        elif value == "" or "TODO" in value or re.search(r"<[^>]+>", value):
            problems.append("not filled in: " + name)
    if problems:
        return problems

    mode = fields["Listening mode"].lower()
    always_on = "always" in mode or "wake" in mode
    if not always_on and "push" not in mode:
        problems.append("Listening mode must say push-to-talk or wake word (always-on)")
    if always_on:
        for name in ("School approval", "Parent consent record", "Always-on approval"):
            v = fields[name].lower()
            if v.startswith("not") or v in ("none", "n/a"):
                problems.append("always-on listening needs: " + name)
    if not re.fullmatch(r"\d+", fields["Retention days"]):
        problems.append("Retention days must be a whole number (use 0 for nothing kept)")
    else:
        days = int(fields["Retention days"])
        stored = [fields["Audio stored"].lower(), fields["Transcripts stored"].lower()]
        if days == 0 and any(s.startswith("yes") for s in stored):
            problems.append("something is stored but Retention days is 0")
        if days > 0 and all(s.startswith("no") for s in stored):
            problems.append("Retention days is above 0 but nothing is stored")
    if "web" in fields["Agent permissions"].lower() and "no web" not in fields["Agent permissions"].lower():
        problems.append("Agent permissions mentions web access: justify it or remove it")
    return problems


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        fields = read_fields(f.read())
    problems = check(fields)
    for p in problems:
        print("PROBLEM", p)
    print("PASS ({} fields)".format(len(REQUIRED)) if not problems
          else "NEEDS WORK: {} problem(s)".format(len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
