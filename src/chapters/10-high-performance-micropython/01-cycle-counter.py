# Chapter 10, Test 01: Does the DWT cycle counter work on this board?
# Tries to switch on the Cortex-M33's cycle counter (the "DWT timer"), checks
# that it counts, and calibrates it against time.ticks_us(). Then it measures
# how many cycles one reading of the counter costs, and shows what
# time.ticks_cpu() really is on this build. Needs only the Pico.
#
# UNVERIFIED: this approach (DEMCR bit 24, DWT_CTRL bit 0, CYCCNT at
# 0xE0001004) is standard for Cortex-M cores, but nobody has yet confirmed
# that it works from MicroPython on the RP2350. This is the file that finds out.
#
# PASS (counter works): "cycle counter is counting" and a "cycles per
# microsecond" within about 1% of the CPU frequency in MHz (150).
# ALSO FINE: "no cycle counter on this board". Then every later file still
# works, it times in microseconds, and you can convert with 150 cycles per us.
# Write down which one you got: it is the answer the chapter is waiting for.

NAME = "01-cycle-counter.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import machine
import time

import bench

mhz = machine.freq() / 1_000_000
print()
print("CPU frequency: {:.0f} MHz  ->  {:.2f} ns per cycle, {:.0f} cycles per microsecond".format(
    mhz, 1000 / mhz, mhz))

ok = bench.enable_dwt()
print()
print("DEMCR  = 0x{:08X}".format(bench.mem32[bench.DEMCR]))
print("DWT_CTRL = 0x{:08X}   (bit 25 set means NO cycle counter)".format(bench.mem32[bench.DWT_CTRL]))

if ok:
    print("cycle counter is counting.")
    # Calibrate: count cycles across 20 ms, 5 times.
    print()
    print("{:>4} {:>12} {:>10} {:>14}".format("run", "cycles", "us", "cycles per us"))
    ratios = []
    for run in range(5):
        c0 = bench.cycles()
        t0 = time.ticks_us()
        time.sleep_ms(20)
        c1 = bench.cycles()
        t1 = time.ticks_us()
        cyc = (c1 - c0) & 0xFFFFFFFF
        us = time.ticks_diff(t1, t0)
        ratios.append(cyc / us)
        print("{:>4} {:>12,} {:>10,} {:>14.2f}".format(run, cyc, us, cyc / us))
    average = sum(ratios) / len(ratios)
    print("average {:.2f} cycles per microsecond (CPU says {:.0f})".format(average, mhz))

    # What does one reading cost?
    reads = 1000
    c0 = bench.cycles()
    for _ in range(reads):
        bench.cycles()
    cost = ((bench.cycles() - c0) & 0xFFFFFFFF) / reads
    print()
    print("one call of bench.cycles() costs about {:.0f} cycles ({:.2f} us)".format(cost, cost / mhz))
    print("(that includes the call itself; subtract it from very short measurements)")
    verdict = abs(average - mhz) / mhz < 0.02
else:
    print("no cycle counter on this board (or it did not count).")
    print("Use microseconds: 1 us = {:.0f} cycles at this clock.".format(mhz))
    verdict = None

# What is ticks_cpu()?
print()
a = time.ticks_cpu()
time.sleep_ms(10)
b = time.ticks_cpu()
a2 = time.ticks_us()
time.sleep_ms(10)
b2 = time.ticks_us()
print("ticks_cpu() advanced {} in about 10 ms; ticks_us() advanced {}".format(
    time.ticks_diff(b, a), time.ticks_diff(b2, a2)))
print("If the two are about equal, ticks_cpu() on this build counts microseconds, not cycles.")

print()
if verdict:
    print("PASS: the DWT cycle counter works; use bench.cycles() for cycle counts.")
elif verdict is None:
    print("No DWT: time in microseconds. Tell the chapter author (TODO list).")
else:
    print("CHECK: the counter counts, but not at the CPU frequency. Is machine.freq() what you expect?")
