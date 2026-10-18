# Chapter 8, Test 07: The Ring buffer class
# The plain-MicroPython ring buffer from the chapter, with the chapter's
# 8-byte example replayed step by step. Runs on the Pico or on your computer
# (python3 07-ring-class.py). Needs no hardware.
#
# PASS: the three steps match the chapter's table and the last line says PASS.

NAME = "07-ring-class.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))


class Ring:
    def __init__(self, size):
        self.buf = bytearray(size)
        self.size = size
        self.head = 0          # next place to write
        self.count = 0         # bytes waiting to be read

    def put(self, data):
        for b in data:
            self.buf[self.head] = b
            self.head = (self.head + 1) % self.size
            if self.count < self.size:
                self.count += 1

    def get(self, n):
        n = min(n, self.count)
        start = (self.head - self.count) % self.size
        out = bytes(self.buf[(start + i) % self.size] for i in range(n))
        self.count -= n
        return out

    def contents(self):
        """Oldest to newest, without removing anything."""
        start = (self.head - self.count) % self.size
        return bytes(self.buf[(start + i) % self.size] for i in range(self.count))


ring = Ring(8)
ok = True


def show(step, action):
    print("{} {:<14} contents {:<10} head {} count {}".format(
        step, action, ring.contents().decode(), ring.head, ring.count))


ring.put(b"ABCDEF")
show(1, 'put "ABCDEF"')
ok = ok and ring.contents() == b"ABCDEF" and ring.head == 6 and ring.count == 6

got = ring.get(2)
show(2, "get 2 -> " + got.decode())
ok = ok and got == b"AB" and ring.contents() == b"CDEF" and ring.count == 4

ring.put(b"GHIJK")
show(3, 'put "GHIJK"')
ok = ok and ring.contents() == b"DEFGHIJK" and ring.head == 3 and ring.count == 8
print("(C was lost: the ring only holds 8 bytes.)")

print()
print("PASS" if ok else "FAIL")
