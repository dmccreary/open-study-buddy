# Chapter 14, Test 02: Retry with exponential backoff and jitter (arithmetic)
# Prints the waiting time before each retry, the worst-case time a request can
# take, and a simulation of 30 classroom devices that all lose the server at
# the same instant and retry. Without jitter they all knock at the same moment
# every round; with jitter they spread out. Runs on your COMPUTER or the Pico;
# no network.
#
# PASS: the ceilings are 500, 1000, 2000, 4000, 8000, 8000 ms, the worst case
# for 4 attempts is 35.5 s, and the last line says PASS. The simulated peak
# numbers differ from run to run (they are random); jitter's peak should be
# far below 30.

NAME = "02-backoff-table.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import random

import backoff

BASE, CAP, ATTEMPTS, TIMEOUT_S = 500, 8000, 4, 8
DEVICES = 30
BUCKET_MS = 100

ok = True
print()
print("{:>7} {:>13} {:>12} {:>12}".format("retry", "ceiling ms", "average ms", "total so far"))
total = 0
for attempt in range(6):
    top = backoff.ceiling_ms(attempt, BASE, CAP)
    total += top
    print("{:>7} {:>13,} {:>12,.0f} {:>12,}".format(attempt + 1, top, top / 2, total))
ok = ok and [backoff.ceiling_ms(a, BASE, CAP) for a in range(6)] == [500, 1000, 2000, 4000, 8000, 8000]

waits = sum(backoff.ceiling_ms(a, BASE, CAP) for a in range(ATTEMPTS - 1))
worst = ATTEMPTS * TIMEOUT_S * 1000 + waits
print()
print("{} attempts, each failing after the {} s socket timeout, plus the waits:".format(ATTEMPTS, TIMEOUT_S))
print("  worst case = {} x {:,} ms + {:,} ms of waiting = {:,} ms ({:.1f} s)".format(
    ATTEMPTS, TIMEOUT_S * 1000, waits, worst, worst / 1000))
ok = ok and worst == 35500

random.seed(7)
print()
print("{} devices lose the server together; retry 1 happens within {} ms.".format(
    DEVICES, backoff.ceiling_ms(0, BASE, CAP)))
for label, jitter in (("no jitter  ", False), ("full jitter", True)):
    buckets = {}
    for _ in range(DEVICES):
        t = backoff.delay_ms(0, BASE, CAP, jitter) // BUCKET_MS
        buckets[t] = buckets.get(t, 0) + 1
    print("  {}: busiest {} ms window gets {:>2} of {} requests".format(
        label, BUCKET_MS, max(buckets.values()), DEVICES))
    if not jitter:
        ok = ok and max(buckets.values()) == DEVICES
print("  expected with jitter: {} devices / {} windows = {:.0f} per window".format(
    DEVICES, backoff.ceiling_ms(0, BASE, CAP) // BUCKET_MS,
    DEVICES / (backoff.ceiling_ms(0, BASE, CAP) // BUCKET_MS)))

print()
print("PASS" if ok else "CHECK: a number differs from the chapter")

# Try This
#   1. Change CAP to 2000. How does the worst case change, and why would a
#      school choose a longer cap?
#   2. Set DEVICES to 300. How many requests land in the busiest window?
