# Chapter 12 code: Wake-Word Detection

Chapter: `docs/chapters/12-wake-word-detection/index.md`

```bash
cd src/chapters
./upload-chapter.sh 12 05-enroll.py
```

Before you start: run Chapter 11's `04-calibrate.py` (the level gate reads `calibration.json`).
The default listening mode of the Study Buddy is **push-to-talk**. These files keep it that way:
`09-live-detector.py` listens only while MODE is held unless `ALWAYS_ON_APPROVED` is set, and
always-on listening needs approval first (Chapter 17).

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-detector-math-test.py` | none (also runs on a computer) | Mean subtraction, length 1, self score 1.0000, running sums match the textbook steps; PASS |
| `02-band-table.py` | none (also runs on a computer) | 16 bands over bins 4 to 255, 25 frames = 1.00 s, a memory table that adds up |
| `03-feature-timing.py` | Pico only | Per-step milliseconds for one frame; says whether it fits in 40 ms |
| `04-feature-image.py` | Display + button + microphone | A heat map of "Hey Pico" that looks the same each time |
| `05-enroll.py` | Display + buttons + microphone | Five accepted utterances; consistency numbers; UP saves `wake_template.bin` |
| `06-self-test.py` | Pico (+ microphone, optional) | Self score 1.0000; shifted scores fall off; noise scores low; timing verdict |
| `07-score-trace.py` | Display + button + microphone | Best score for "Hey Pico" clearly above other phrases; CSV of the trace |
| `08-threshold-sweep.py` | Display + button + microphone | Table of false rejects and false accepts at 0.50 to 0.95 |
| `09-live-detector.py` | Display + button + microphone + speaker | Beep on "Hey Pico"; 0 overruns (needs a fast transform) |

Helper modules (uploaded with the tests, imported by them):

| Module | What it holds |
|--------|---------------|
| `features.py` | `Extractor`: 512 samples to 16 log band energies; the plain-Python reference FFT and the hook for a fast one; `band_edges()`, `dct()` |
| `detector.py` | mean subtraction, normalization, `Window` (rolling window with running sums), `Detector`, `build_template()`, template file save and load |
| `wake.py` | helpers that score or enroll from a recording |
| `levels.py`, `vad.py`, `calibration.py`, `recorder.py`, `ui.py`, `synth.py`, `buttons.py` | unchanged copies of Chapter 11's modules (and Chapter 7's `buttons.py`), so this folder uploads on its own. If you edit one, copy it to the other folder too. |

Tools that run on your computer (not uploaded):

| File | What it does |
|------|--------------|
| `tools/threshold-sweep.py` | Reads the `RESULT,...` lines that `08` prints and prints false rejects and false accepts by threshold, per speaker and pace |
| `tools/pipeline-synthetic-test.py` | The REAL detector code on SYNTHETIC speech-like audio: enroll, score, sweep thresholds, change speaker and pace. Needs `numpy` and `scipy`. About half a minute. |

Run the no-hardware checks first, on your computer:

```bash
cd src/chapters/12-wake-word-detection
python3 01-detector-math-test.py
python3 02-band-table.py
python3 tools/pipeline-synthetic-test.py
```

## The plain-Python FFT is too slow for the live loop

`features.Extractor` uses a plain-Python FFT as a readable reference. Expect it to be far
over the 40 ms frame budget (the chapter works out why). So:

- `05`, `07` and `08` work with it: they record first and compute features afterwards.
- `09` needs a fast transform: write `fast(re, im, power)` (Chapter 10) and pass it as
  `features.Extractor(spectrum_fn=fast)` in `09` and `06`. Until then `09` reports its overruns.

## The most important tests for the book

The chapter gives **no real accuracy numbers**, because none exist yet. These runs make them.
Please record:

- From `03`: milliseconds per step, with the reference transform and again with Chapter 10's.
- From `05`: the five consistency numbers for your "Hey Pico".
- From `06`: the shifted-window scores (how fussy the alignment is) and the room-noise score.
- From `07`: best score for "Hey Pico" (5 tries) and for 5 other phrases, a cough, a clap.
- From `08`: the false-reject and false-accept table, for different speakers, a faster pace,
  a slower pace, and a noisy room. Save the RESULT lines and use `tools/threshold-sweep.py`.
- Using `09` with approval: false accepts per hour over a long, ordinary session
  (this needs always-on approval and a fast transform; do not skip Chapter 17).

## What has been checked, and what has not

- Every file compiles. `01` and `02` pass on a computer. `tools/pipeline-synthetic-test.py`
  runs and its numbers are reproducible (fixed seeds); they are for SYNTHETIC audio.
- `03` to `09` were run, as far as their logic goes, on a computer against a fake Pico layer
  (pins, buttons on a script, an I2S microphone playing synthetic audio, a recording display,
  a virtual clock). That caught typos and logic errors, showed an enrollment writing and reading
  `wake_template.bin`, a score trace finding the phrase, and the live loop firing, beeping with
  the microphone closed, and resetting. The virtual clock charges no time for Python work, so it
  says nothing about milliseconds.
- The plain-Python FFT was checked against numpy's on a computer. The fast-transform hook was
  exercised with numpy's FFT.
- Nothing here has run on the Pico yet. Timings, real "Hey Pico" scores, false-accept and
  false-reject rates, and the effect of a different speaker or pace are the open questions this
  folder exists to answer.
