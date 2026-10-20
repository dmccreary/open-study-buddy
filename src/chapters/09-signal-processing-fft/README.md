# Chapter 9 code: Signal Processing and the FFT

Chapter: `docs/chapters/09-signal-processing-fft/index.md`

```bash
cd src/chapters
./upload-chapter.sh 09 05-mic-spectrum-text.py
```

`dsp.py` is the chapter's library (FFT, Hann window, RMS, decibels, bands, peak
frequency). The upload script copies it with the numbered files. Chapter 10 keeps
an identical copy of it; if you change one, change both.

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-dft-by-hand.py` | none (also runs on a computer) | `X = [0, -2j, 0, +2j]`; two tones show energy only in bins 2 and 5; PASS |
| `02-fft-vs-dft.py` | none (also runs on a computer) | fft and naive DFT agree to < 0.0001; 512-point row shows 262,144 vs 2,304; PASS |
| `03-bin-calculator.py` | none (also runs on a computer) | Bin width 25 Hz, 256 bins, 1,000 Hz = bin 40.0, 16 bands cover bins 4 to 255; PASS |
| `04-leakage-hann.py` | none (also runs on a computer) | 1,000 Hz: 1 loud bin plain, 3 with Hann; 1,012.5 Hz: 10 plain, 4 with Hann; 440 Hz refines to 439.7 Hz; PASS |
| `05-mic-spectrum-text.py` | Microphone | Peak column follows a whistle within about 25 Hz; one band digit rises |
| `06-volume-meter.py` | Display + microphone | Bar rises with sound; dBFS number near -55 to -60 in a quiet room; zero frames over budget |
| `07-spectrum-display.py` | Display + microphone | A whistle raises one bar; a rising whistle moves it right; peak Hz follows the note |

Run `01` to `04` first on your computer. They need no hardware and they produce
every number the chapter prints in its tables:

```bash
cd src/chapters/09-signal-processing-fft
python3 04-leakage-hann.py
```

## The most important tests for the book

`05` and `07` show how slow the pure-Python pipeline is, which is the problem
Chapter 10 solves. Please record:

- From `05` and `07`: the **work ms** per analyzed frame (the chapter only says
  "I expect 100 to 300 ms, a guess, not a measurement") and how many frames were
  skipped. If it is under 40 ms, the chapter's story about overruns needs to change.
- From `05`: the dBFS reading and the band digits in a quiet room, and with a
  whistle or a phone tone. The chapter's -58 dBFS quiet-room figure is modelled
  from Chapter 8's 13.1 bits, and the scale ends (-90 to -30 dBFS for the bars,
  -70 to -20 dBFS for the volume meter) are starting guesses.
- From `06`: the work ms per frame (expected to be small, since it does no FFT).
- Whether `PEAK_GATE_DBFS` (-50) hides the peak in a quiet room and shows it for a
  whistle. Adjust it if not.

## What has and has not been checked

Checked off the device with plain CPython, using a fake `machine`, `gc9b72`, and
microphone (a synthetic 1 kHz tone plus noise and a DC offset) that run the
scripts at their real code paths:

- `dsp.fft` against `dsp.naive_dft` on 64 random numbers (agreement about 3e-7).
- All the numbers printed in the chapter's tables: the bin and band tables, the
  leakage counts, the 440 Hz peak refinement, the dBFS values, and the band
  energy example.
- `05`, `06`, and `07` run to completion against the fake microphone and display:
  no exceptions, every `fill_rect` and `text` call is inside the 360 x 360 square
  and inside the visible circle, and `latest_frame()` skips the expected number of
  frames when the analysis is made artificially slow (150 ms).

Not checked: anything on the real board. The speed of `dsp.fft` on the Pico, the
dBFS levels of a real room, whether `array('f')` and `struct.unpack_from` behave
exactly as on CPython in your MicroPython build, and how the picture looks on the
glass. The script comments say where each of these is expected to matter.
