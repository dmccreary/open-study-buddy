# bench.py -- timing helpers for Chapter 10: a benchmark harness, the DWT cycle
# counter, and a small profiler.
#
# Two clocks:
#   time.ticks_us()   microseconds. Always works. One tick is 150 CPU cycles at
#                     150 MHz, so it cannot time anything shorter than about a
#                     millisecond to better than a few percent without repeating.
#   DWT cycle counter a 32-bit counter in the Cortex-M33 that adds 1 on every CPU
#                     clock cycle. It is a register at 0xE0001004, switched on
#                     through DEMCR (0xE000EDFC, bit 24) and DWT_CTRL (0xE0001000,
#                     bit 0). enable_dwt() tries it and returns False if the
#                     counter is missing or does not count. UNVERIFIED on the
#                     RP2350 as of writing this chapter: run 01-cycle-counter.py.
#                     The 32-bit counter wraps after 2**32 cycles = 28.6 s at 150
#                     MHz, so always subtract with `& 0xFFFFFFFF`.
#
# Every number printed by bench() is the BEST of `repeat` runs, with a
# gc.collect() before each run. The best run is the one least disturbed by
# interrupts and garbage collection; it measures the code, not the noise. Use
# the spread of several runs (see spread()) to judge timing verification.

import gc
import time
from machine import mem32

DEMCR = 0xE000EDFC
DWT_CTRL = 0xE0001000
DWT_CYCCNT = 0xE0001004
TRCENA = 1 << 24
CYCCNTENA = 1 << 0
NOCYCCNT = 1 << 25

HAS_DWT = False


def enable_dwt():
    """Switch on the DWT cycle counter. Returns True if it is counting."""
    global HAS_DWT
    mem32[DEMCR] = mem32[DEMCR] | TRCENA              # allow the DWT/trace block
    if mem32[DWT_CTRL] & NOCYCCNT:                    # this core has no cycle counter
        HAS_DWT = False
        return False
    mem32[DWT_CYCCNT] = 0
    mem32[DWT_CTRL] = mem32[DWT_CTRL] | CYCCNTENA     # start counting
    first = mem32[DWT_CYCCNT]
    for _ in range(50):
        pass
    HAS_DWT = mem32[DWT_CYCCNT] != first
    return HAS_DWT


def cycles():
    """The raw 32-bit cycle count (0 if there is no counter)."""
    return mem32[DWT_CYCCNT] if HAS_DWT else 0


def bench(label, func, args=(), repeat=5, budget_us=40000, quiet=False):
    """Time func(*args). Returns (best_us, best_cycles); cycles is 0 without DWT.

    Prints one line, and a RESULT line you can paste into the chapter's table:
    RESULT|label|best_us|best_cycles"""
    best_us = None
    best_cyc = 0
    for _ in range(repeat):
        gc.collect()
        c0 = cycles()
        t0 = time.ticks_us()
        func(*args)
        t1 = time.ticks_us()
        c1 = cycles()
        us = time.ticks_diff(t1, t0)
        if best_us is None or us < best_us:
            best_us = us
            best_cyc = (c1 - c0) & 0xFFFFFFFF
    if not quiet:
        cyc_text = "{:>11,} cycles".format(best_cyc) if HAS_DWT else "      (no DWT)"
        print("{:<34} {:>10.3f} ms {} {:>6.1f}% of a frame".format(
            label, best_us / 1000, cyc_text, 100 * best_us / budget_us))
        print("RESULT|{}|{}|{}".format(label, best_us, best_cyc))
    return best_us, best_cyc


def spread(func, args=(), repeat=20):
    """Run func(*args) `repeat` times and return (min_us, mean_us, max_us).
    The gap between min and max is how much you can trust a single run
    (timing verification)."""
    low = None
    high = 0
    total = 0
    for _ in range(repeat):
        t0 = time.ticks_us()
        func(*args)
        us = time.ticks_diff(time.ticks_us(), t0)
        total += us
        high = max(high, us)
        low = us if low is None else min(low, us)
    return low, total // repeat, high


class Profiler:
    """Adds up the time spent in named sections of a loop.

        prof = Profiler()
        ...
        prof.lap("read")      # time since the previous lap goes to "read"
        prof.lap("fft")
        prof.report(passes)   # milliseconds per pass for each section

    The dictionary gets one entry per section name the first time it is used;
    after that a lap allocates nothing but a small integer."""

    def __init__(self):
        self.totals = {}
        self.order = []
        self.last = time.ticks_us()

    def restart(self):
        self.last = time.ticks_us()

    def lap(self, name):
        now = time.ticks_us()
        if name not in self.totals:
            self.totals[name] = 0
            self.order.append(name)
        self.totals[name] += time.ticks_diff(now, self.last)
        self.last = time.ticks_us()

    def report(self, passes, budget_us=40000):
        total = 0
        for name in self.order:
            total += self.totals[name]
        print("{:<12} {:>9} {:>9}".format("section", "ms/pass", "share"))
        for name in self.order:
            each = self.totals[name] / passes
            print("{:<12} {:>9.2f} {:>8.0f}%".format(
                name, each / 1000, 100 * self.totals[name] / total if total else 0))
        print("{:<12} {:>9.2f}  (frame budget {:.0f} ms)".format(
            "total", total / passes / 1000, budget_us / 1000))
