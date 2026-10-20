# Chapter 18 code: Testing, Integration, and Capstone Projects

Chapter: `docs/chapters/18-testing-integration-capstones/index.md`

```bash
cd src/chapters
./upload-chapter.sh 18 selftest.py
```

Files in `tools/` run on your computer and are not uploaded. The modules
(`log.py`, `checks.py`, `overrun.py`, `scheduler.py`, `detectors.py`,
`listen.py`) are imported by the numbered files; the upload script puts every
top-level `.py` file on the Pico, and `mpremote run` then finds them.

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `log.py` | none (a module; runs on a computer too) | Levels, a RAM ring of the last N lines, an optional flash file with a size cap |
| `01-log-demo.py` | none (computer or Pico) | Ring holds the last 10 lines; flash files stay under the cap; only WARN and ERROR in flash; PASS |
| `02-display-probe.py` | Display | Three solid colors, then rings; you answer UP; prints the SPI rate you really got and three fill times |
| `03-mic-probe.py` | Microphone | Verdict PASS, spread above 0, loudness jumps several bits when you clap |
| `04-speaker-probe.py` | Amplifier + speaker; microphone optional | You hear the beep; the microphone line says it heard the tone 2.0+ bits above the room |
| `05-button-probe.py` | Buttons | PASS, with a small number of bounce edges per button |
| `06-wifi-probe.py` | Pico | Your 2.4 GHz school network is listed; PASS (or joined, with a `secrets.py`) |
| `07-wiring-check.py` | none (config.py on the Pico) | The wire list matches your kit; pin plan PASS |
| `selftest.py` | Whatever is wired | One line per subsystem and a summary on the display; no FAIL |
| `08-scheduler-demo.py` | none (timing model) | Tables for the scenario you set (`normal`, `stall`, `bug`, `sliced`) |
| `09-detectors-test.py` | none (computer or Pico) | Every line ok, then PASS (synthetic sound; checks logic only) |
| `10-clap-detector.py` | Display + microphone | Calibrates, then counts claps; double clap toggles a light |
| `11-noise-monitor.py` | Display + microphone | QUIET / TALKING / LOUD with a bar; "Level only. No audio saved." |
| `12-study-timer.py` | Display + buttons + speaker | Focus and break countdown; a beep at 0:00 |
| `13-homework-reminder.py` | Display + buttons (speaker optional) | Shows TEST/DUE items and how soon; beeps once per new alert |
| `tools/wiring_table.py` | computer | Prints (or `--markdown`) the wire list from `config.py` |
| `tools/diagnose.py` | computer | Asks yes/no questions and names a likely cause, test, and fix |
| `tools/trim_events.py` | computer | Cuts the Cedar Ridge `events.json` to the 50 TEST/DUE events (4,197 bytes) |
| `user-test-sheet.md` | none | A printable observation sheet and consent script |

## The most important tests for the book

Please record, so the chapter can replace estimates with measurements:

- `selftest.py`: the "ms" at the end of each line (how long each check takes) and
  whether the speaker's microphone loopback passes at `MIN_RISE_BITS` = 2.0.
- `02-display-probe.py`: the three fill times (Chapter 5 recorded 129 ms).
- `03-mic-probe.py`: the spread, DC offset, loudness, and the jump when you clap.
- `08-scheduler-demo.py` costs are inputs, not measurements. Replace the two
  ASSUMED costs (`buttons` 0.5 ms and `network` 2.0 ms) with your own timings.
- `10-clap-detector.py`: how far from the microphone a clap still counts.
- `11-noise-monitor.py`: the floor, and the smoothed level in your classroom
  during silent work, group work, and a loud moment.
- `12-study-timer.py`: stopwatch against a 5-minute focus period.
- `user-test-sheet.md`: run it with three classmates on one project.

## What has been checked, and what has not

- Every file compiles. `01`, `09`, and everything in `tools/` run on a computer.
  The scripts that touch hardware were run to completion (or until stopped)
  against a fake Pico layer with a virtual clock, fake pins, a fake I2S that
  blocks like the real one, and synthetic sound. This catches typos and logic
  errors. It also checked the failure paths: a flat-line microphone, a
  microphone WS wire on GP13, and missing font files.
- `09` uses synthetic frames (a fixed random seed). It shows how the logic
  behaves, not how a real clap, voice, or fan looks to your microphone.
- Every number printed in the chapter from `08` and `09` is the output of this
  code. The scheduler costs are inputs from Chapters 5, 6, and 8 plus two assumed
  values; the results are a model.
- Nothing here has run on the Pico yet. Unmeasured: the time each self-test check
  takes, whether the loopback threshold of 2.0 bits works with your speaker and
  microphone, the real clap and noise levels in a classroom, and how long
  `shapes.ring()` takes for the self-test pattern.
