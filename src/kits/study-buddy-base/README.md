# Study Buddy base kit

A Raspberry Pi Pico 2 W with a 2.1" round GC9B72 display, three buttons, a
MAX98357A amplifier with a speaker, and an INMP441 microphone. The tests are
small and numbered so students can wire one part, run its test, and then add
the next part.

## Wiring

| Part | Pico pins |
|---|---|
| Display (SCL, SDA, RST, DC, CS, BL) | GP2, GP3, GP4, GP5, GP6, GP7 (SPI0), plus 3V3 and GND |
| Buttons MODE, UP, DOWN | GP13, GP14, GP15, each with its other leg to GND |
| Microphone SCK, WS, SD | GP10, GP11, GP12 (I2S block 1) |
| Microphone L/R, VDD, GND | GND (left channel), 3V3, GND |
| Amplifier BCLK, LRC, DIN | GP20, GP21, GP19 (I2S block 0) |
| Amplifier GAIN | GP18 |
| Amplifier VIN, GND | 5 V (VBUS) or 3V3, and GND |

**The I2S pin rule:** MicroPython's I2S on the Pico needs the word-select pin
(LRC or WS) on the pin right after the clock pin (BCLK or SCK). Test 02 checks
it for both the speaker and the microphone.

**Microphone wiring gotchas:** the microphone's SCK and WS wires are easy to
swap, and so are SCK and SD. A swapped mic starts without any error and sends
nothing but zeros, so test 02 reports "flat line" and test 06's meter never
moves. If you see that, check, in this order: SCK on GP10, WS on GP11, SD on
GP12; VDD on 3V3 (not 5 V); GND and L/R both on GND. Do not "fix" it by
editing the pins in `config.py` to match swapped wires: SCK on GP12 would need
WS on GP13, which is the MODE button, and `I2S()` raises
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
| 02 | No warnings. Its pin rules also caught a real mis-wiring (see the microphone gotchas above). |
| 03 | PASS. All three buttons reported presses and releases. |
| 05 | PASS. The beep, the scale, and the three volumes were all heard, and the sound quality was good. |
| 06 | Calibrates a noise floor of about 12.5 bits in a quiet room. Its response to speech has not been recorded here. |
| 07 | PASS. A 1.50 s recording (19,200 samples) played back; the microphone's DC offset measured about 15,000. |

Test 04 (the display) has not been recorded here. Test 01 has not been
recorded either.
