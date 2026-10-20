# Chapter 10, Test 08: Fixed-point (Q15) arithmetic by hand
# Shows what Q15 numbers are, multiplies a few of them, and then checks all
# six challenges of the chapter's "Q15 calculator" activity. Runs on the Pico
# or on your computer (python3 08-q15-fixed-point.py). Needs no hardware.
#
# PASS: every row of the table matches the chapter and the last line says PASS.

NAME = "08-q15-fixed-point.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

ONE = 32768          # 1.0 in Q15 is 2**15


def to_q15(value):
    """Float to Q15, rounded, and clamped to the 16-bit range."""
    n = int(round(value * ONE))
    return max(-32768, min(32767, n))


def q15_mul(a, b):
    """Multiply two Q15 numbers: the full product is Q30, so shift right by 15."""
    return (a * b) >> 15


def to_float(q):
    return q / ONE


print()
print("Q15 in one table")
print("{:>10} {:>8} {:>26}".format("real value", "Q15", "back to a real value"))
for v in (0.5, 0.25, -0.5, 0.1, 0.999, 1.0, -1.0):
    q = to_q15(v)
    print("{:>10} {:>8} {:>26.6f}".format(v, q, to_float(q)))
print("Smallest step: 1/32768 = {:.7f}.  Largest: {} = {:.5f}.  1.0 does not fit (it clamps).".format(
    1 / ONE, 32767, 32767 / ONE))

print()
print("The Q15 multiply: (a * b) >> 15")
CHALLENGES = (
    # (a, b, expected result of (a*b)>>15, why)
    (16384, 16384, 8192, "0.5 x 0.5 = 0.25"),
    (32767, 32767, 32766, "the largest value squared is just under 1.0"),
    (-16384, 16384, -8192, "-0.5 x 0.5 = -0.25"),
    (3, 3, 0, "tiny numbers vanish: 9 >> 15 is 0"),
    (-3, 3, -1, "a negative product rounds toward minus infinity: -9 >> 15 is -1"),
    (-32768, -32768, 32768, "-1.0 x -1.0 = +1.0, which no longer fits in 16 bits"),
)
ok = True
for a, b, expected, why in CHALLENGES:
    got = q15_mul(a, b)
    mark = "ok" if got == expected else "MISMATCH"
    ok = ok and got == expected
    print("  {:>7} x {:>7} -> {:>6}   {:<6} {}".format(a, b, got, mark, why))

print()
print("How big can a sum of two products get? (viper integers are 32 bits)")
worst = 32768 * 32768 + 32768 * 32768
print("  two products of 32768 x 32768 add to {:,}; a signed 32-bit register holds up to {:,}".format(
    worst, 2 ** 31 - 1))
print("  -> that worst case does NOT fit, which is why fft_viper.py keeps |re + j im| <= 32768 and halves")
print("     every stage: the real worst case is |z| x 32768 = {:,.0f}, which does fit.".format(
    32768 * 2 ** 0.5 * 32768))
ok = ok and worst > 2 ** 31 - 1 and 32768 * 2 ** 0.5 * 32768 < 2 ** 31 - 1

print()
print("PASS" if ok else "CHECK: a Q15 result does not match the chapter.")
