#!/usr/bin/env python3
"""Chapter 18: print the wire list for the kit from config.py, on your computer.

    python3 wiring_table.py                          (uses the kit's config.py)
    python3 wiring_table.py path/to/config.py
    python3 wiring_table.py --markdown               (a table you can paste or print)

It READS config.py as text (it never runs it, so it needs no Pico modules),
pulls out the pin numbers, and uses the same function the Pico-side check uses
(checks.wiring_table), so the printed sheet cannot disagree with the program.
Tape the printout next to the kit and tick each wire as you check it.
"""
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import checks                                       # noqa: E402

DEFAULT = os.path.join(HERE, "..", "..", "..", "kits", "study-buddy-base", "config.py")


def read_config(path):
    values = {}
    with open(path) as f:
        for line in f:
            m = re.match(r"^([A-Z][A-Z0-9_]*)\s*=\s*(\d+)\s*(#.*)?$", line.strip())
            if m:
                values[m.group(1)] = int(m.group(2))
    return types.SimpleNamespace(**values)


def main(argv):
    markdown = "--markdown" in argv
    paths = [a for a in argv[1:] if not a.startswith("--")]
    config = read_config(paths[0] if paths else DEFAULT)
    rows = checks.wiring_table(config)
    if markdown:
        print("| Part | Part pin | Pico pin | Header pin |")
        print("|------|----------|----------|------------|")
        for part, pin, pico, physical in rows:
            print("| {} | {} | {} | {} |".format(part, pin, pico, physical))
    else:
        print("{:<12} {:<12} {:<12} {}".format("part", "part pin", "Pico pin", "header pin"))
        for part, pin, pico, physical in rows:
            print("{:<12} {:<12} {:<12} {}".format(part, pin, pico, physical))
    verdict, detail = checks.check_pin_plan(config)
    print()
    print("Pin plan: {} - {}".format(verdict, detail))
    return 0 if verdict == checks.PASS else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
