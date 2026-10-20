# Chapter 10, Test 03: Which statements allocate memory?
# Runs 12 small statements 200 times each with the garbage collector switched
# off and reports how many bytes of heap each one used per run. A statement that
# allocates makes garbage, and garbage means a collection pause some time later.
# Then it times the same arithmetic on integers and on floats, and on plain
# lists versus array('h') and array('f'). Needs only the Pico.
#
# PASS: the "expected" column (written from how MicroPython stores objects)
# matches the "measured" column for every row. If a row disagrees, tell the
# chapter author: it changes the allocation quiz in the chapter.
#
# EXPECTED but not yet confirmed on the Pico: floats allocate on this build
# (a float is a small heap object), small integers do not, big integers do.
# (If you run this file on a 64-bit computer instead, the "integer above 2**30"
# row says "no": there the small-integer range is far bigger. That is fine.)

NAME = "03-allocation-and-floats.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import struct
import time
from array import array

import bench

REPEAT = 200
buf = bytearray(64)
view = memoryview(buf)
arr_h = array("h", [1] * 64)
arr_f = array("f", [1.0] * 64)
words = bytearray(16)


def case_int_add():
    x = 1
    for _ in range(REPEAT):
        x = x + 1


def case_float_mul():
    y = 1.5
    for _ in range(REPEAT):
        y = y * 1.0001


def case_array_float():
    for _ in range(REPEAT):
        arr_f[3] = arr_f[3] * 1.0001          # reads a float, makes one, stores it


def case_array_int():
    for _ in range(REPEAT):
        arr_h[3] = (arr_h[3] * 3) >> 1         # all small integers


def case_slice_copy():
    for _ in range(REPEAT):
        part = buf[0:8]                       # a new bytearray of 8 bytes


def case_view_slice():
    for _ in range(REPEAT):
        part = view[0:8]                      # a new (tiny) memoryview object


def case_new_list():
    for _ in range(REPEAT):
        t = [0] * 16


def case_unpack():
    for _ in range(REPEAT):
        t = struct.unpack("<4i", words)       # a new tuple of 4 integers


def case_unpack_into():
    for _ in range(REPEAT):
        struct.pack_into("<i", words, 0, 7)   # writes into memory we already own


def case_format():
    for _ in range(REPEAT):
        s = "%d" % 12345                      # a new string


def case_big_int():
    big = 1 << 30                             # does not fit a 31-bit small integer
    for _ in range(REPEAT):
        z = big + 1


def case_assign_element():
    for _ in range(REPEAT):
        buf[5] = 77


CASES = (
    ("int + 1", case_int_add, False),
    ("float * float", case_float_mul, True),
    ("array('f') element times a float", case_array_float, True),
    ("array('h') element, integer math", case_array_int, False),
    ("bytearray slice buf[0:8]", case_slice_copy, True),
    ("memoryview slice view[0:8]", case_view_slice, True),
    ("[0] * 16", case_new_list, True),
    ("struct.unpack('<4i', ...)", case_unpack, True),
    ("struct.pack_into('<i', ...)", case_unpack_into, False),
    ("'%d' % number", case_format, True),
    ("integer above 2**30", case_big_int, True),
    ("buf[5] = 77", case_assign_element, False),
)

print()
print("{:<36} {:>9} {:>14} {:>9}".format("statement (x200)", "expected", "bytes per run", "measured"))
agree = True
for label, func, expected in CASES:
    gc.collect()
    gc.disable()
    before = gc.mem_alloc()
    func()
    after = gc.mem_alloc()
    gc.enable()
    used = after - before
    measured = used > 64          # the loop itself may take a few bytes; real garbage is much more
    agree = agree and (measured == expected)
    print("{:<36} {:>9} {:>14.1f} {:>9}".format(
        label, "yes" if expected else "no", used / REPEAT, "yes" if measured else "no"))
gc.collect()

# Floating point cost: the same loop on integers and on floats
print()
print("Floating point cost: 2000 multiply-adds")


def loop_int():
    a = 3
    total = 0
    for i in range(2000):
        total = total + a * i


def loop_float():
    a = 3.0
    total = 0.0
    for i in range(2000):
        total = total + a * i


bench.bench("2000 x (a * i + total), integers", loop_int, repeat=5, budget_us=40000)
bench.bench("2000 x (a * i + total), floats", loop_float, repeat=5, budget_us=40000)

# Typed arrays versus lists
print()
print("Lists versus typed arrays: sum of 512 numbers")
n = 512
list_int = [i & 1023 for i in range(n)]
array_int = array("h", list_int)
list_float = [float(v) for v in list_int]
array_float = array("f", list_float)


def sum_of(seq):
    total = 0
    for i in range(n):
        total += seq[i]
    return total


for label, seq in (("list of ints", list_int), ("array('h')", array_int),
                   ("list of floats", list_float), ("array('f')", array_float)):
    bench.bench("sum of 512, " + label, sum_of, (seq,), repeat=5, budget_us=40000)

print()
print("memory used by 512 numbers:")
for label, build in (("list of ints", lambda: [i & 1023 for i in range(n)]),
                     ("list of floats", lambda: [float(i & 1023) for i in range(n)]),
                     ("array('h')", lambda: array("h", [0] * n)),
                     ("array('f')", lambda: array("f", [0.0] * n))):
    gc.collect()
    before = gc.mem_alloc()
    keep = build()
    gc.collect()                       # frees the temporary list used to build the array
    after = gc.mem_alloc()
    print("  {:<16} {:>6} bytes".format(label, after - before))
    del keep
gc.collect()

print()
print("PASS" if agree else "CHECK: a row disagrees with the expected column. Tell the chapter author.")
