# Chapter 18, Test 01: The logger, with a size cap you can watch
# Writes 200 lines through log.py with a deliberately tiny flash cap (400 bytes)
# and shows what each of the three places (serial, RAM ring, flash file) kept.
# Needs only the Pico. It also runs on a computer: python3 01-log-demo.py
#
# PASS: the ring holds exactly the last 10 lines; the flash file never grows
# past the cap (log-demo.txt plus log-demo.txt.1 stay under 2 x 400 bytes);
# only WARN and ERROR lines reached flash; the last line says PASS.
# The demo files are deleted at the end.

NAME = "01-log-demo.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import os
from log import Log, DEBUG, INFO, WARN, ERROR

PATH = "log-demo.txt"
CAP = 400


def size(path):
    try:
        return os.stat(path)[6]
    except OSError:
        return 0


for p in (PATH, PATH + ".1"):
    try:
        os.remove(p)
    except OSError:
        pass

log = Log(level=ERROR, ring=10, path=PATH, max_bytes=CAP, echo=False)
worst = 0
for i in range(200):
    if i % 10 == 0:
        log.warn("overrun %d: %d us", i, 41000 + i)
    elif i % 15 == 0:
        log.error("failure %d", i)
    else:
        log.info("frame %d ok", i)
    worst = max(worst, size(PATH), size(PATH + ".1"))

print("lines logged      :", log.total)
print("by level          :", {("DBG", "INF", "WRN", "ERR")[(k // 10) - 1]: v
                              for k, v in sorted(log.counts.items())})
print("ring holds        :", len(log.lines()), "lines (oldest first):")
for line in log.lines()[:3]:
    print("   ", line)
print("   ...")
print("flash file bytes  :", size(PATH), "and .1:", size(PATH + ".1"),
      "(cap", CAP, "each)")
print("largest file seen :", worst)

with open(PATH) as f:
    levels = {line.split()[1] for line in f}
print("levels in flash   :", sorted(levels))

ok = (len(log.lines()) == 10 and worst <= CAP and levels <= {"WRN", "ERR"}
      and log.file_errors == 0)
for p in (PATH, PATH + ".1"):
    try:
        os.remove(p)
    except OSError:
        pass
print("PASS" if ok else "FAIL")
