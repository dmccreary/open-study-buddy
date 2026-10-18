# Chapter 5 code: Display Basics: Pixels, Color, and Frame Size

Chapter: `docs/chapters/05-display-basics/index.md`

```bash
cd src/chapters
./upload-chapter.sh 05 01-fill-timing.py
```

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-fill-timing.py` | Display | Measured full-screen time >= 86.4 ms at 24 MHz; 20 MHz request gives 12 MHz |
| `02-rgb565-colors.py` | Display | Seven color bands; every value "ok", PASS |
| `03-clock-face-marks.py` | Display | Round clock face with hands at 10:10; five "ok" |
| `04-color-themes.py` | Display | Screen alternates dark and light |
| `05-frame-size-calc.py` | none (also runs on a computer) | 259,200 bytes; 86.4 ms; PASS |

**Record this number:** the measured full-screen fill time at 24 MHz from `01`.
The chapter says "at least 86 ms"; the real figure tells you how much overhead
MicroPython adds on top of the wire time.
