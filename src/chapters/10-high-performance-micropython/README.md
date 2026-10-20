# Chapter 10 code: High-Performance MicroPython

Chapter: `docs/chapters/10-high-performance-micropython/index.md`

```bash
cd src/chapters
./upload-chapter.sh 10 01-cycle-counter.py
```

Everything here runs on the Pico 2 W. These files are **Pico-only** unless the
table says otherwise: `@micropython.viper` and `@micropython.asm_thumb` do not
exist on a computer's CPython. The numbers are for YOU to fill in: the chapter's
results table has "to be measured" in every measured column.

Modules the numbered files import (uploaded with them):

| Module | What it is |
|--------|-----------|
| `dsp.py` | The Chapter 9 library, an IDENTICAL copy (if you change one, change both) |
| `bench.py` | `bench()`, `spread()`, the DWT cycle counter helpers, and the `Profiler` |
| `kernels.py` | The windowing loop in Python and viper, and the sum loop in the same two ways |
| `kernels_asm.py` | The same two loops in inline assembly, in their own file so a line the assembler rejects cannot break the rest |
| `fft_viper.py` | The Q15 fixed-point FFT, `load_frame_q15`, `power_q15`, `band_sums` |

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-cycle-counter.py` | Pico only | "cycle counter is counting" and about 150 cycles per microsecond; or "no cycle counter" (also a valid answer) |
| `02-fft-pure-python-bench.py` | Pico only | Peak bin 40; a table of the pure-Python FFT times; pipeline total vs the 40 ms frame |
| `03-allocation-and-floats.py` | Pico only | "expected" and "measured" columns agree for all 12 statements |
| `04-window-kernels.py` | Pico only | "all four methods agree", then times for Python, viper and assembly |
| `05-fft-viper-bench.py` | Pico only | Both pipelines find bin 40; band error < 1 dB in loud bands; viper FFT allocates 0 bytes |
| `06-frame-loop-budget.py` | Microphone | A VERDICT for each mode; pure Python is expected to FAIL, viper to PASS |
| `07-dual-core.py` | Pico only | Four results A to D, no error |
| `08-q15-fixed-point.py` | none (also runs on a computer) | Six rows match the chapter; PASS |

Start with `01`, then `02`. `08` can be run any time on your computer:

```bash
cd src/chapters/10-high-performance-micropython
python3 08-q15-fixed-point.py
```

## The most important tests for the book

Chapter 10 is about speed, and every speed in it is a blank until you run these.
The scripts print `RESULT|...` lines you can paste into the chapter's results
table. Please record:

- From `01`: whether the DWT cycle counter exists and counts on the RP2350 (the
  chapter calls its register sequence "unverified"), the measured cycles per
  microsecond, the cost of one `bench.cycles()` read, and whether
  `time.ticks_cpu()` advances like `ticks_us()` (the MicroPython source says it does).
- From `02`: the time of one `dsp.fft` (512 points, `array('f')` and plain
  lists), the microseconds per butterfly (multiply by 150 for cycles), and the
  pipeline total. The chapter only says "unknown"; Chapter 9 guessed 100 to 300 ms.
- From `03`: whether every "expected" matches "measured", especially the
  `integer above 2**30` row (it is only true on a 32-bit chip), plus the float
  versus integer time and the list versus `array` times and memory.
- From `04`: the four window times and cycles per sample. The chapter estimates
  15 to 25 cycles per sample (51 to 85 us per frame) for the assembly version,
  from instruction counts only. If the assembly is rejected by the Pico's
  assembler, note the exact error and line.
- From `05`: the time of `fft_q15`, the whole viper pipeline, the band error,
  and the allocation (expected 0 bytes).
- From `06`: both VERDICT lines, the worst pass, and the overrun counts. This is
  the test that decides whether the viper pipeline keeps up.
- From `07`: the four ratios. The chapter expects C near 100% and D slower.

## What has and has not been checked

Checked off the device:

- **In real MicroPython** (the unix port built from the current source, an x86-64
  Intel Mac, so 64-bit integers and double-precision floats): `dsp.py` and the Chapter 9
  scripts run and print the same numbers; `kernels.py`'s viper functions compile
  and give bit-exact results against the Python versions over random samples;
  `fft_viper.py` compiles; `03` and `08` run. The unix port zero-extends a `ptr32`
  read where the Pico's 32-bit registers sign-extend it, so the fixed-point FFT
  could not be checked for values there.
- **In a software model** (CPython with a stand-in for `micropython.viper` that
  re-parses each function and checks every `+`, `-`, `*` and `<<` against signed
  32-bit limits, with the Pico's `ptr16` (unsigned) and `ptr32` (signed) rules):
  `fft_q15`, `load_frame_q15`, `power_q15` and `band_sums` gave no overflow, agreed
  with the floating-point pipeline (see the accuracy table in the chapter), and
  `window_viper` and `sum16_viper` were exact. The accuracy table in the chapter
  comes from this model, which is valid because integer arithmetic is deterministic.
- **An assembly emulator** (a small interpreter for the Thumb instructions
  the book uses): `window_asm` and `sum16_asm` give exactly the same answers as
  Python on random data and edge values. It confirmed 13 and 8 instructions per
  iteration. It does NOT check that the real assembler accepts each line.
- **Fake `machine`, `gc9b72`, and microphone** for `06` and `07`: they run to the
  end, print their reports, and the frame-skip logic of Chapter 9 behaves.
- The register facts in the chapter (RP2350 float implementation, `ticks_cpu`,
  thread model, which assembler opcodes the ARM build enables) were read from
  the MicroPython source and documentation, not from the board.

Not checked, and the reason this folder exists:

- Any speed on the Pico: the cycle counter's existence, the pure-Python FFT time,
  viper and assembly speed-ups, garbage-collection pauses, dual-core slowdowns.
- Whether `machine.mem32` reads and writes of `0xE000EDFC`, `0xE0001000` and
  `0xE0001004` are accepted on the RP2350 (worst case: the board resets; nothing
  else is touched).
- Whether the real assembler accepts `window_asm`'s exact text (it uses only basic
  instructions that exist on every Pico).
- Whether a second thread behaves as the chapter expects on your firmware version.
