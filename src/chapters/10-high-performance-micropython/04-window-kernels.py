# Chapter 10, Test 04: One loop, four speeds
# Windows 512 sixteen-bit samples with a Q15 Hann window, out[i] = (x[i] * w[i]) >> 15,
# in plain Python on lists, plain Python on array('h'), in @micropython.viper,
# and in @micropython.asm_thumb. First it checks that all four give EXACTLY the
# same 512 answers, then it times them. Also times the smallest loop of all
# (the sum of 512 numbers) in the same four ways, and shows the viper "ptr16
# reads are unsigned" gotcha. Needs only the Pico.
#
# PASS: "all four methods agree" and a table of times. WRITE DOWN: the four
# window times, and cycles per sample if the DWT counter works. They are rows
# of the chapter's results table.
#
# If the asm file is rejected ("invalid micropython decorator" or an assembler
# syntax error), the script says so, skips the assembly rows, and carries on:
# tell the chapter author which line. The viper versions do not depend on it.

NAME = "04-window-kernels.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
from array import array

import micropython

import bench
import kernels

try:
    import kernels_asm
except Exception as error:          # the Pico's assembler rejected a line
    kernels_asm = None
    print("kernels_asm.py did not load:", error)

N = 512
FRAME_US = 40000
bench.enable_dwt()
print("DWT cycle counter: {}".format("yes" if bench.HAS_DWT else "no"))

# A 1 kHz tone at about 25% of full scale as signed 16-bit samples, and the Hann window in Q15
x_list = [int(8000 * math.sin(2 * math.pi * 1000 * i / 12800)) - 100 for i in range(N)]
w_list = [int(32767 * (0.5 - 0.5 * math.cos(2 * math.pi * i / N))) for i in range(N)]
x = array("h", x_list)
w = array("h", w_list)
expected = [(x_list[i] * w_list[i]) >> 15 for i in range(N)]

out_list = [0] * N
out_array = array("h", [0] * N)
out_viper = array("h", [0] * N)
out_asm = array("h", [0] * N)

kernels.window_py(x_list, w_list, out_list, N)
kernels.window_py(x, w, out_array, N)
kernels.window_viper(x, w, out_viper, N)
if kernels_asm:
    kernels_asm.window_asm(x, w, out_asm, N)

agree = (out_list == expected and list(out_array) == expected
         and list(out_viper) == expected and (kernels_asm is None or list(out_asm) == expected))
print()
print("all {} methods agree on all {} samples: {}".format(4 if kernels_asm else 3, N, agree))

print()
print("Windowing 512 samples")
rows = []
jobs = [("window, Python, plain lists", kernels.window_py, (x_list, w_list, out_list, N)),
        ("window, Python, array('h')", kernels.window_py, (x, w, out_array, N)),
        ("window, @viper", kernels.window_viper, (x, w, out_viper, N))]
if kernels_asm:
    jobs.append(("window, @asm_thumb", kernels_asm.window_asm, (x, w, out_asm, N)))
for label, func, args in jobs:
    us, cyc = bench.bench(label, func, args, repeat=5, budget_us=FRAME_US)
    rows.append((label, us, cyc))
base = rows[0][1]
print()
print("{:<30} {:>10} {:>10} {:>16}".format("method", "ms", "speed-up", "cycles / sample"))
for label, us, cyc in rows:
    per_sample = "{:.0f}".format(cyc / N) if bench.HAS_DWT else "{:.0f} (from us)".format(us * 150 / N)
    print("{:<30} {:>10.3f} {:>9.1f}x {:>16}".format(label, us / 1000, base / us if us else 0, per_sample))

print()
print("The smallest loop: add up 512 sixteen-bit numbers")
jobs = [("sum, Python, array('h')", kernels.sum16_py, (x, N)),
        ("sum, @viper", kernels.sum16_viper, (x, N))]
if kernels_asm:
    jobs.append(("sum, @asm_thumb", kernels_asm.sum16_asm, (x, N)))
for label, func, args in jobs:
    bench.bench(label, func, args, repeat=5, budget_us=FRAME_US)
total = sum(x_list)
sums_agree = kernels.sum16_py(x, N) == total == kernels.sum16_viper(x, N)
if kernels_asm:
    sums_agree = sums_agree and kernels_asm.sum16_asm(x, N) == total
print("the sums agree: {}".format(sums_agree))

print()
print("The viper gotcha: ptr16 reads are unsigned")
minus_one = array("h", [-1])
print("  array('h') holds -1; Python reads it as {}; the viper sum (which fixes the sign) gives {}".format(
    minus_one[0], kernels.sum16_viper(minus_one, 1)))


@micropython.viper
def raw_read(a: ptr16) -> int:
    return int(a[0])


print("  the same value read through a bare ptr16 is {}".format(raw_read(minus_one)))

print()
print("PASS" if agree else "CHECK: the four methods disagree. The first difference is below.")
if not agree:
    for name, got in (("list", out_list), ("array", out_array), ("viper", out_viper), ("asm", out_asm)):
        if name == "asm" and kernels_asm is None:
            continue
        for i in range(N):
            if got[i] != expected[i]:
                print("  {} first differs at sample {}: got {}, expected {}".format(name, i, got[i], expected[i]))
                break
