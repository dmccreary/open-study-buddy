# Chapter 2, Test 07: Make the heap fragmented
# Allocates a lot of small blocks, frees every other one, and then asks for one
# big block. The total free memory is large, but no single gap is. Then it
# frees everything and asks again. This is the chapter's "Heap Fragmentation
# Explorer" done for real. Needs only the Pico.
#
# PASS: step 3 reports MemoryError even though plenty of heap is free in
# total, and step 5 succeeds. (If step 3 succeeds on your board, the allocator
# found a big gap; try raising FILL to 0.95.)

NAME = "07-heap-fragmentation.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc

SMALL = 512          # bytes per small block
FILL = 0.90          # fraction of the free heap to fill with small blocks
BIG_FRACTION = 0.30  # the big request, as a fraction of the starting free heap

gc.collect()
start_free = gc.mem_free()
count = int(start_free * FILL) // (SMALL + 32)     # 32 bytes of rough overhead per block
print("1. start: {:,} bytes free".format(start_free))

blocks = []
try:
    for _ in range(count):
        blocks.append(bytearray(SMALL))
except MemoryError:
    print("   (ran out of heap after {} blocks; carrying on)".format(len(blocks)))
count = len(blocks)
gc.collect()
print("2. after {} small blocks: {:,} bytes free".format(count, gc.mem_free()))

for i in range(0, count, 2):
    blocks[i] = None                  # free every other block
gc.collect()
free_total = gc.mem_free()
want = int(start_free * BIG_FRACTION)
print("3. freed every other block: {:,} bytes free in total.".format(free_total))
print("   asking for ONE block of {:,} bytes ...".format(want))
try:
    big = bytearray(want)
    print("   it fit (no fragmentation problem on this run)")
    del big
except MemoryError:
    print("   MemoryError! Free memory is split into gaps of about {} bytes.".format(SMALL))

blocks = None
gc.collect()
print("4. freed everything: {:,} bytes free".format(gc.mem_free()))
try:
    big = bytearray(want)
    print("5. the same request now succeeds: {:,} bytes".format(len(big)))
    del big
except MemoryError:
    print("5. still failing: something else is using the heap")

# Try This
#   1. Change SMALL to 64. Does the big request still fail?
#   2. Allocate the big block FIRST, then the small ones. Does everything fit?
