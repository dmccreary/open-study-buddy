# Chapter code for Open Study Buddy

Runnable code for each chapter, so you can test what the book says on the real
kit. One folder per chapter, named like the chapter folder in `docs/chapters/`.
Each folder has its own `README.md` with a table of files, the parts each needs,
and what PASS looks like.

## Before you start

1. Wire and test the kit with the tests in `../kits/study-buddy-base/` (01 to 07).
   These chapter files reuse that kit's `config.py`, display driver, and fonts, so
   the pin numbers only live in one place.
2. Install `mpremote` (`pip install mpremote`) and quit Thonny: only one program
   can use the Pico's serial port at a time.

## Upload and run

```bash
cd src/chapters
./upload-chapter.sh 05                      # kit files + chapter 5 files
./upload-chapter.sh 05 01-fill-timing.py    # ...and run one file
./upload-chapter.sh 05 --no-kit             # chapter files only (kit already there)
```

You can also run a file straight from your computer without saving it on the
Pico, after the upload has put the helper modules there:

```bash
mpremote run 05-display-basics/01-fill-timing.py
```

Files in a `tools/` folder run on your computer and are not uploaded.

## What is in each chapter

| Chapter | Folder | Files | Hardware |
|---------|--------|-------|----------|
| 1 | `01-personal-agents-architecture` | rule-based `decide()`, request/reply JSON check | none (computer) |
| 2 | `02-micropython-review` | memory report, pull-up, timer, interrupt, struct, try/finally mic, heap fragmentation | Pico, button, mic |
| 3 | `03-sound-and-digital-audio` | aliasing tone, WAV header, clipping, bit depth, mic loudness in dB | speaker, mic |
| 4 | `04-pico-kit-hardware` | SPI byte count, pin table, floating pin, visible area, Wi-Fi scan | display, Pico |
| 5 | `05-display-basics` | full-fill timing, RGB565, clock face, themes, frame size table | display |
| 6 | `06-display-regions-and-drawing` | pixel vs fill vs blit, window order, dirty meter, text padding, sprite, animation, region layout, image loader | display |
| 7 | `07-buttons-and-device-modes` | `buttons.py`, `device.py`, button events, bounce capture, device modes, self-test, non-blocking, volume beep | buttons, display, speaker |
| 8 | `08-i2s-audio` | I2S pin rule, mic frame reader, ring latency, sine table, play file, self-hearing, ring class, amp shutdown | mic, speaker |

## Suggested order for a first pass

Run the no-hardware checks first, then the hardware ones:

1. On your computer: Chapter 1 (both files), `03/02`, `03/04`, `05/05`,
   `06/09`, `07/04`, `08/07`.
2. Pico only: `02/01`, `02/05`, `02/07`, `04/02`, `04/05`, `08/01`.
3. Display: Chapters 4 (`01`, `04`), 5, and 6.
4. Buttons: Chapter 7.
5. Audio: Chapter 3 (`01`, `03`, `05`), Chapter 8.

## Numbers to write down

The chapters make claims that these files measure. The most useful ones:

| File | What to record |
|------|----------------|
| `02/01-memory-report.py` | Free heap; whether a 3 s and a 5 s recording fit |
| `05/01-fill-timing.py` | Measured full-screen fill time at 24 MHz (chapter: at least 86.4 ms) |
| `06/07-region-layout.py` | Time to redraw all five regions (chapter best case: 16.9 ms) |
| `07/02-bounce-capture.py` | Worst contact-bounce settle time on your buttons |
| `08/02-mic-frame-reader.py` | "work ms" of the plain-Python loudness calculation |
| `08/03-ring-latency.py` | How the microphone delay grows at `LOOP_MS` = 30, 40, 50, 60, 86 |
| `08/06-self-hearing.py` | The quiet tail, in milliseconds |

If a result differs from what the chapter says, the chapter needs to change, not
your hardware. Bring the numbers back and the text, tables, and MicroSim
specifications can be corrected.

## What has been checked, and what has not

- Every file compiles, and every file runs to completion (or until you stop it)
  on a computer against a fake Pico layer that supplies pins, SPI, I2S, and
  timing. This catches typos and logic errors.
- The display byte counts in `04/01` and `06/01` were checked against the real
  `gc9b72.py` driver: one `pixel()` is 13 bytes and a 100 x 30 `fill_rect()` is
  6,011 bytes.
- Nothing here has run on the Pico yet. Timings, microphone behavior, and sound
  quality are the open questions this folder exists to answer.
