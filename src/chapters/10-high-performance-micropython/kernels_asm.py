# kernels_asm.py -- the same two loops in inline assembly (Chapter 10)
#
#   window_asm   out[i] = (x[i] * w[i]) >> 15 for signed 16-bit x and Q15 window w
#   sum16_asm    the sum of n signed 16-bit numbers
#
# They are in their own file so that a line the Pico's assembler rejects only
# breaks this file. They use only basic Thumb instructions (mov add sub cmp lsl
# asr mul ldrh strh bgt), which exist on every Pico, so they need none of the
# wider RP2350-only opcodes. Rules for @micropython.asm_thumb: up to four
# arguments, named r0..r3; what is in r0 at the end is the return value; r0..r7
# are free to use; an array argument arrives as the address of its first element.
#
# Both loops run once even for n = 0 and do no bounds checking: pass n > 0 and
# n <= len(array).
#
# UNVERIFIED on the real assembler. The logic was checked with an emulator on a
# computer (same answers as Python, 13 and 8 instructions per element); whether
# the Pico accepts every line is what 04-window-kernels.py finds out.

import micropython


@micropython.asm_thumb
def window_asm(r0, r1, r2, r3):   # r0 = x, r1 = w, r2 = out, r3 = n (n > 0)
    label(LOOP)
    ldrh(r4, [r0, 0])             # r4 = x[i], zero-extended to 32 bits
    lsl(r4, r4, 16)               # shift it to the top ...
    asr(r4, r4, 16)               # ... and back with the sign: r4 = signed x[i]
    ldrh(r5, [r1, 0])             # r5 = w[i] (0 .. 32767, no sign problem)
    mul(r4, r5)                   # r4 = r4 * r5  (fits in 32 bits: |r4*r5| < 2**30)
    asr(r4, r4, 15)               # back to the sample scale
    strh(r4, [r2, 0])             # out[i] = low 16 bits
    add(r0, r0, 2)                # three pointers move on by 2 bytes
    add(r1, r1, 2)
    add(r2, r2, 2)
    sub(r3, r3, 1)                # one fewer left
    cmp(r3, 0)
    bgt(LOOP)                     # while n > 0


@micropython.asm_thumb
def sum16_asm(r0, r1):            # r0 = pointer to int16 array, r1 = n (n > 0)
    mov(r2, 0)                    # r2 = running total
    label(LOOP)
    ldrh(r3, [r0, 0])             # r3 = next sample, zero-extended
    lsl(r3, r3, 16)
    asr(r3, r3, 16)               # sign-extend to 32 bits
    add(r2, r2, r3)               # total += sample
    add(r0, r0, 2)                # next sample
    sub(r1, r1, 1)                # one fewer left
    cmp(r1, 0)
    bgt(LOOP)
    mov(r0, r2)                   # the value in r0 is what the function returns
