# Chapter 2, Test 05: bytearray, struct, and memoryview
# Runs on the Pico or on your computer. It reproduces the chapter's examples:
# the two bytes 0x34 0x12 read as the number 4660, 32-bit microphone samples
# unpacked with struct, and a memoryview slice that copies nothing.
#
# PASS: the last line says PASS.

NAME = "05-bytes-struct-memoryview.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import struct

ok = True

# 1. Two bytes, little-endian
raw = bytearray(8)
raw[0] = 0x34
raw[1] = 0x12
(value,) = struct.unpack("<h", raw[:2])
print("bytes 34 12 as '<h' ->", value, "(expect 4660, which is 0x1234)")
ok = ok and value == 4660

# 2. Four-byte samples, like the microphone's
samples = [1, -1, 100000, -100000]
packed = struct.pack("<4i", *samples)
print("4 samples pack to", len(packed), "bytes (expect 16)")
ok = ok and len(packed) == 16 and list(struct.unpack("<4i", packed)) == samples

# 3. 512 samples are 2,048 bytes, like one audio frame in test 06
frame = bytearray(512 * 4)
unpacked = struct.unpack("<512i", frame)
print("one frame:", len(frame), "bytes ->", len(unpacked), "samples")
ok = ok and len(frame) == 2048 and len(unpacked) == 512

# 4. memoryview slices point at the same memory
buffer = bytearray(b"abcdefgh")
view = memoryview(buffer)
piece = view[2:5]
piece[0] = ord("X")                     # writes into `buffer`
print("buffer after writing through the view:", bytes(buffer), "(expect b'abXdefgh')")
ok = ok and bytes(buffer) == b"abXdefgh"

# 5. A slice of a bytearray is a copy; a slice of a memoryview is not
copy = buffer[2:5]
copy[0] = ord("Z")
print("buffer after writing to a copy      :", bytes(buffer), "(unchanged)")
ok = ok and bytes(buffer) == b"abXdefgh"

try:
    import gc
    gc.collect()
    before = gc.mem_free()
    big = bytearray(20000)
    gc.collect()
    mid = gc.mem_free()
    for _ in range(50):
        part = memoryview(big)[100:1100]    # no copy
    after_views = gc.mem_free()
    for _ in range(50):
        part = big[100:1100]                # copies 1000 bytes each time
    after_copies = gc.mem_free()
    print("free heap: start {:,}, after big {:,}, after 50 views {:,}, after 50 copies {:,}".format(
        before, mid, after_views, after_copies))
except AttributeError:
    print("(gc.mem_free is not available on this Python; skip the heap check)")

print()
print("PASS" if ok else "FAIL: one of the checks above did not match")
