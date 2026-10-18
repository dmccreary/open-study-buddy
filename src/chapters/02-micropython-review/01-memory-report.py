# Chapter 2, Test 01: Memory report
# Prints how much heap and flash this Pico has, then tries the allocations the
# chapter does the arithmetic for: a 3-second recording (test 07 of the kit)
# and a 5-second one. Needs only the Pico.
#
# PASS: the report prints, "3 s recording" says it fits, and the free heap is
# close to what you expect. Write down your numbers: later chapters compare
# against them.
#
# The chapter's arithmetic: 12,800 samples/s x 4 bytes x 3 s = 153,600 bytes.

NAME = "01-memory-report.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import os

RATE = 12800
BYTES_PER_SAMPLE = 4

gc.collect()
free = gc.mem_free()
used = gc.mem_alloc()
print()
print("heap free     : {:,} bytes ({:.1f} KB)".format(free, free / 1024))
print("heap in use   : {:,} bytes ({:.1f} KB)".format(used, used / 1024))
print("heap total    : {:,} bytes".format(free + used))

stats = os.statvfs("/")
print("flash free    : {:,} bytes ({:.2f} MB)".format(
    stats[0] * stats[3], stats[0] * stats[3] / 1048576))
print("files on flash:", os.listdir())

print()
for seconds in (3, 5):
    needed = seconds * RATE * BYTES_PER_SAMPLE
    gc.collect()
    try:
        block = bytearray(needed)
        print("{} s recording: fits   ({:,} bytes needed, {:,} free after)".format(
            seconds, needed, gc.mem_free()))
        del block
    except MemoryError:
        print("{} s recording: does NOT fit ({:,} bytes needed)".format(
            seconds, needed))
    gc.collect()

# Find the largest single block by halving the step.
low, high = 0, gc.mem_free()
while high - low > 256:
    middle = (low + high) // 2
    gc.collect()
    try:
        block = bytearray(middle)
        del block
        low = middle
    except MemoryError:
        high = middle
gc.collect()
print()
print("largest single block you can allocate right now: about {:,} bytes".format(low))
print("(free heap is {:,}; the gap is what fragmentation and overhead cost)".format(
    gc.mem_free()))

# Try This
#   1. Import the display (import config; d = config.init_display()) and run
#      this again. How much heap did the display and fonts use?
#   2. Make a list of 1000 small bytearrays, delete half of them, then run the
#      "largest block" search again.
