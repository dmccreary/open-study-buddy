# Study Buddy base kit

A Raspberry Pi Pico 2 W with a 2.1" round GC9B72 display, three buttons, a
MAX98357A amplifier with a speaker, and an INMP441 microphone. The tests are
small and numbered so students can wire one part, run its test, and then add
the next part.

## Wiring

| Part | Pico pins |
|---|---|
| Display (SCL, SDA, RST, DC, CS, BL) | GP2, GP3, GP4, GP5, GP6, GP7 (SPI0), plus 3V3 and GND |
| Buttons MODE, UP, DOWN | GP16, GP17, GP18, each with its other leg to GND |
| Microphone SCK, WS, SD | GP13, GP14, GP15 (I2S block 1) |
| Microphone L/R, VDD, GND | GND (left channel), 3V3, GND |
| Amplifier BCLK, LRC, DIN | GP9, GP10, GP11 (I2S block 0) |
| Amplifier GAIN | GP12 |
| Amplifier VIN, GND | 5 V (VBUS) or 3V3, and GND |

**The I2S pin rule:** MicroPython's I2S on the Pico needs the word-select pin
(LRC or WS) on the pin right after the clock pin (BCLK or SCK). Test 02 checks
it for both the speaker and the microphone.

**Microphone wiring gotchas:** the microphone's SCK and WS wires are easy to
swap, and so are SCK and SD. A swapped mic starts without any error and sends
nothing but zeros, so test 02 reports "flat line" and test 06's meter never
moves. If you see that, check, in this order: SCK on GP13, WS on GP14, SD on
GP15; VDD on 3V3 (not 5 V); GND and L/R both on GND. Do not "fix" it by
editing the pins in `config.py` to match swapped wires: SCK on GP15 would need
WS on GP16, which is the MODE button, and `I2S()` raises
`invalid ws (must be sck+1)`.

All the pin numbers are in `config.py`.

## Setup

1. Put MicroPython `RPI_PICO2_W` on the Pico.
2. Quit Thonny, then upload everything:

   ```bash
   ./upload-code.sh
   ```

   If it finds the wrong serial port, name it:
   `PORT=/dev/cu.usbmodem14301 ./upload-code.sh`.

   This uploads every `.py` file in the folder, so it replaces `config.py`
   and any test files already on the Pico. A Pico that used to run another
   kit (a smart clock, say) keeps its old `main.py`, which will run at power-up
   and may not work with the new `config.py`. Run the tests from Thonny or
   `mpremote run`, or delete that `main.py`.
3. `secrets.py` (WiFi name and password) is optional for these tests, and is
   not in the repository because it is listed in `.gitignore`. To make one,
   write `wifi_ssid = "..."` and `wifi_pass = "..."`, or copy it from another
   Pico with `mpremote fs cp :secrets.py secrets.py`. `upload-code.sh` sends
   it to the Pico if it is present.

## Tests

Each test needs only the parts named in its row. Add a part, run its test.

| Test | File | Parts needed | PASS looks like |
|---|---|---|---|
| 01 | `01-blink-onboard-led.py` | Pico | The LED blinks. |
| 02 | `02-probe.py` | Pico (checks the rest as they are added) | No warnings for the parts you have wired. |
| 03 | `03-buttons.py` | Buttons | Each press and release prints in the shell, then "PASS". |
| 04 | `04-hello-world.py` | Display | "Hello World!" inside a cyan ring. |
| 05 | `05-speaker-tones.py` | Amplifier, speaker | You hear a beep, a scale, and three volumes. |
| 06 | `06-listen-meter.py` | Display, microphone | "Say 'Hey Pico'" with a meter that moves when you talk. |
| 07 | `07-record-playback.py` | Button, microphone, speaker, display | Hold MODE and talk; let go and hear it back. |

Tests 01 to 05 each use one part. Test 06 combines the display with the
microphone, and test 07 combines everything.

### Running a test

Open the file in Thonny and press Run, or from a terminal:

```bash
mpremote run 02-probe.py
```

Tests 01, 03, 06, and 07 run until you stop them (Stop in Thonny, or Ctrl-C).
Tests 05 and 07 make sound; run 02, 03, 04, and 06 first if you are somewhere
quiet. Test 02 never makes a sound.

### What has been checked on hardware

Run on a Pico 2 W with everything wired as above:

| Test | Result |
|---|---|
| 01 | PASS. The LED blinks. |
| 02 | No warnings. Its pin rules also caught a real mis-wiring (see the microphone gotchas above). |
| 03 | PASS. All three buttons reported presses and releases. |
| 04 | PASS. "Hello World!" is drawn inside the ring. |
| 05 | PASS. The beep, the scale, and the three volumes were all heard, and the sound quality was good. |
| 06 | PASS. Calibrates a noise floor of about 12.5 bits in a quiet room, and the meter responds to speech. |
| 07 | PASS. A 1.50 s recording (19,200 samples) played back; the microphone's DC offset measured about 15,000. |

All seven tests pass on this kit.

## Demo 20: the showcase

`20-demo-template.py` shows off everything the kit can do. To run it at
power-up, make it the Pico's `main.py`:

```bash
mpremote cp 20-demo-template.py :main.py
```

It starts in **mode 0, the showcase**: the welcome screen (`welcome.py`,
"Study Buddy Kit" and the parts in the kit), then one screen for each demo,
changing every six seconds. UP or MODE skips ahead, DOWN goes back.

**Hold any button for one second** to try the demo on the screen. Inside a
demo, **hold MODE for one second** to go back to the showcase.

| # | Module | Demo | Buttons |
|---|---|---|---|
| 1 | `demo_clock.py` | Clock and weather forecast (needs `secrets.py`) | -- |
| 2 | `demo_alarm.py` | Alarm clock, set for one minute from now | MODE set, UP on/off, DOWN test |
| 3 | `demo_timer.py` | Countdown timer with presets | UP start/pause, DOWN preset/reset, MODE set |
| 4 | `demo_stopwatch.py` | Stopwatch with laps | UP or MODE start/stop, DOWN lap/reset |
| 5 | `demo_school.py` | School mascot and this week's events | UP/DOWN page |
| 6 | `demo_tones.py` | Sine, square, triangle, sawtooth, octaves, a tune | UP all again, DOWN tune |
| 7 | `demo_listen.py` | Sound meter (VU arc with peak hold) | UP/DOWN recalibrate |
| 8 | `demo_record.py` | Record 3 seconds, play it back | UP or MODE record, DOWN replay |
| 9 | `demo_quote.py` | Quote of the day (20 quotes) | UP/DOWN another |
| 10 | `demo_spanish.py` | Hear a Spanish word, pick its meaning | UP/DOWN pick, MODE choose |
| 11 | `demo_vocab.py` | Vocabulary flash cards | MODE flip, UP/DOWN next/previous |

A running timer, or an alarm that is on, keeps going after you leave its
demo. When it is due, the demo comes back on screen to ring.

Supporting files:

- `demo_kit.py`: text that word-wraps to fit the round glass, and a faster
  `Speaker` (tones from a wave table, WAV files, a looping alarm).
- `demo_icons.py`: the showcase pictures, drawn from shapes, so no image files.
- `wifi_time.py`, `forecast.py`, `lib/watchparts.py`: copied unchanged from
  the sw-gc9b72 kit in clocks-and-watches.
- `spanish/*.wav`: the 16 spoken words for the Spanish quiz (16-bit mono,
  16000 Hz, about 25 KB each). `tools/make-spanish-audio.sh` makes them
  again on a Mac with its built-in Spanish voice, for example after adding a
  word to `WORDS` in `demo_spanish.py`.
- `secrets-template.py`: copy it to `secrets.py` and fill in your WiFi.

Each demo is loaded only while it is on screen, then unloaded, so they never
all sit in RAM together. If a demo crashes, the error is printed and shown on
the screen, and the showcase carries on.
