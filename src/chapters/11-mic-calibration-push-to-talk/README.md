# Chapter 11 code: Microphone Calibration and Push-to-Talk

Chapter: `docs/chapters/11-mic-calibration-push-to-talk/index.md`

```bash
cd src/chapters
./upload-chapter.sh 11 02-noise-floor.py
```

Run `04-calibrate.py` once first: the later tests read the `calibration.json` it saves
(they fall back to documented defaults and say so if it is missing).

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-bits-and-db.py` | none (also runs on a computer) | 1 bit is 6.02 dB; a doubled frame reads +1.00 bit; PASS |
| `02-noise-floor.py` | Microphone | Table of floor statistics; floor near 12.5 to 13.1 bits; spread under 1.5 bits |
| `03-speech-level.py` | Microphone | Speech level, SNR in bits and dB, "no clipping" (set `DISTANCE_CM`) |
| `04-calibrate.py` | Display + buttons + microphone | Result screen; UP saves `calibration.json`; it reads back the same |
| `05-gate-meter.py` | Display + microphone | Gate opens when you talk; summary compares gate flips with single-threshold flips |
| `06-distance-test.py` | Microphone | Table of level against distance beside the 1-bit-per-doubling model |
| `07-ptt-record.py` | Display + buttons + microphone + speaker | REC only while MODE is held; playback; "overruns 0" |
| `08-vad-record.py` | Display + buttons + microphone + speaker | Picture with S, E and the kept range; playback is trimmed |
| `09-calibration-selftest.py` | none (also runs on a computer) | Every row "ok", PASS |

Helper modules (uploaded with the tests, imported by them, not run on their own):

| Module | What it holds |
|--------|---------------|
| `levels.py` | `frame_stats()`, `percentile()`, `make_calibration()`, `LevelGate` (pure Python) |
| `vad.py` | the `VAD` state machine and `boundaries()` (pure Python) |
| `calibration.py` | `load()`, `save()`, `DEFAULTS` for `calibration.json` |
| `recorder.py` | `new_buffer()` and `record()`: push-to-talk into a pre-allocated buffer |
| `ui.py` | `put()` text and `LevelBar` (draws only the columns that changed) |
| `synth.py` | seeded synthetic frames for the checks (not a microphone) |
| `buttons.py` | a copy of Chapter 7's debounced `Button` |

`tools/raw-to-wav.py` runs on your computer: after `07` saves `utterance.raw`
(press UP after the playback), `mpremote fs cp :utterance.raw .` and
`python3 tools/raw-to-wav.py utterance.raw utterance.wav` lets you listen on the computer.

Run the no-hardware checks first, on your computer:

```bash
cd src/chapters/11-mic-calibration-push-to-talk
python3 01-bits-and-db.py
python3 09-calibration-selftest.py
```

`levels.py`, `vad.py` and `calibration.py` are also copied, unchanged, into
`12-wake-word-detection/`, so each chapter folder uploads on its own. If you edit one,
copy it to the other folder too.

## The most important tests for the book

The chapter's numbers for the room, the voice, and the timing are waiting for these runs.
Please record:

- From `02`: the noise **floor**, **ceiling** and **spread**, in two rooms or with and
  without a fan. Expected near 12.5 to 13.1 bits (two earlier kit measurements);
  not yet measured for this chapter.
- From `03`: speech level and SNR at 30 cm, and whether anything clipped.
- From `06`: the measured level at 10, 20 and 40 cm beside the model's prediction.
- From `04`: the saved `calibration.json` (all values), especially `speech_floor` and
  `record_shift`.
- From `05`: the gate's flips against the single threshold's flips on your own speech.
- From `07`: **work ms avg and max** per frame (the limit is 40 ms) and the free heap line.
  Chapter 8 measured 10 ms for the loudness calculation alone; the 16-bit conversion
  adds an amount that has not been measured.
- From `08`: kept versus recorded length for a phrase, and what whispering, coughing and
  a fan do to the start and end. Tune `START_FRAMES`, `END_FRAMES`, pre-roll and
  hang-over in `vad.py` if your voice needs it.

## What has been checked, and what has not

- Every file compiles. `01` and `09` pass on a computer (CPython 3), and their numbers are
  the synthetic ones quoted in the chapter.
- `02` to `08` were each run, as far as their logic goes, on a computer against a fake Pico
  layer (pins, buttons on a script, I2S microphone with a synthetic waveform, a recording
  display, timing from a virtual clock). That caught typos and logic errors, and showed
  `calibration.json` being written and read back, the VAD finding the start and end of a
  synthetic phrase, `AUTO_STOP` working, and the 6-second buffer filling and stopping.
- The fake layer's virtual clock does not charge time for Python work, so it says nothing about
  the work ms per frame.
- Nothing here has run on the Pico yet. Real noise floors, speech levels, distance effects,
  work times, and VAD behavior on a real voice are the open questions this folder exists to
  answer.
