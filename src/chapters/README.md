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
| 9 | `09-signal-processing-fft` | `dsp.py`, DFT by hand, FFT vs DFT, bin calculator, Hann leakage, mic spectrum, volume meter, spectrum display | mic, display |
| 10 | `10-high-performance-micropython` | benchmark harness, cycle counter, FFT benchmarks, allocation and floats, window kernels (list/array/viper/asm), Q15 viper FFT, frame-loop budget, dual core | mic, Pico |
| 11 | `11-mic-calibration-push-to-talk` | bits and dB, noise floor, speech level, calibration file, gate meter, distance test, push-to-talk record, VAD record, self-test | mic, buttons, display |
| 12 | `12-wake-word-detection` | detector math test, band table, feature timing, enrollment, self-test, score trace, threshold sweep, live detector | mic, speaker, buttons, display |
| 13 | `13-wifi-http-agent-link` | Wi-Fi connect, raw HTTP and `requests` POST, ask the buddy, mDNS check; `server/` buddy server | Pico W, computer |
| 14 | `14-streaming-security-resilience` | chunk arithmetic, recorder, voice upload, timeouts, retry and offline fallback, TLS probe, WebSocket; `server/` with token auth, STT/TTS hooks | mic, speaker, Pico W, computer |
| 15 | `15-mqtt-push-alerts` | topic matcher, MQTT hello, link listener, `check_msg` cost, alert audio loop, status heartbeat, echo round trip; `server/` Mosquitto config and tools | Pico W, broker |
| 16 | `16-school-agent-calendar` | school mascot and edition splash, briefing display; `server/` calendar pipeline (ICS and JSON), `agent.toml`, reminders | display, Pico W, computer |
| 17 | `17-privacy-responsible-listening` | hardware mute switch, listening indicator and its test, buffer wipe; `tools/` data-flow, threat model, injection demo, plan checker | mic, display, switch |
| 18 | `18-testing-integration-capstones` | `log.py`, probes, `selftest.py`, scheduler demo, detectors, clap detector, noise monitor, study timer, homework reminder | whole kit |

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
| `05/01-fill-timing.py` | Measured full-screen fill time at 24 MHz (chapter: 86.4 ms best case; test board 129 ms) |
| `06/07-region-layout.py` | Time to redraw all five regions (best case 16.9 ms; test board 28.1 ms) |
| `07/02-bounce-capture.py` | Worst contact-bounce settle time on your buttons |
| `08/02-mic-frame-reader.py` | "work ms" of the plain-Python loudness calculation |
| `08/03-ring-latency.py` | How the microphone delay grows at `LOOP_MS` = 30, 40, 50, 60, 130 (30 and 50 are done) |
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
