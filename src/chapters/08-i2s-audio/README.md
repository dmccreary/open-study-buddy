# Chapter 8 code: I2S Audio: Recording and Playing Sound

Chapter: `docs/chapters/08-i2s-audio/index.md`

```bash
cd src/chapters
./upload-chapter.sh 08 01-i2s-pin-rule.py
```

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-i2s-pin-rule.py` | Pico only | As-wired pairs start; swapped or non-adjacent pairs raise an error |
| `02-mic-frame-reader.py` | Microphone | About 25.0 frames per second; note the "work ms" number |
| `03-ring-latency.py` | Microphone + speaker, close together | Delay stays small at `LOOP_MS` 40; grows at 50 and levels off |
| `04-sine-table-tone.py` | Speaker | Table version is faster; both beeps sound the same |
| `05-play-file.py` | Speaker | `.raw` and `.wav` sound the same; half rate is an octave lower |
| `06-self-hearing.py` | Microphone + speaker | Tone is clearly louder than the floor; prints a quiet-tail time |
| `07-ring-class.py` | none (also runs on a computer) | Matches the chapter's table, PASS |
| `08-amp-shutdown.py` | **Optional**: SD wired to GP22 | Tone, silence, tone, silence, tone |

## The most important tests for the book

`02` and `03` check the model Chapters 9 to 12 depend on: the 40 ms frame
budget. Please record:

- From `02`: the **work ms** of the plain-Python loudness calculation.
- From `03`: for `LOOP_MS` of 30, 40, 50, 60 and 86, how the delay grows and
  where it stops. The chapter predicts +200 ms per second at 50 ms, leveling off
  near 780 ms after about 3.95 s. If the board does something else (for example
  the delay never grows because the driver drops new data), tell me and I will
  correct the chapter and the "Audio Frame Time Budget Explorer" specification.
- From `06`: the quiet tail in milliseconds.

## Optional measurement

If you have a logic analyzer or oscilloscope, probe the microphone's SCK
(GP10) while `02` runs. The chapter says the bit clock should be about
12,800 x 32 x 2 = 819,200 Hz. If you measure half that, the I2S bus is only
clocking one channel's slot in MONO mode and the chapter's formula needs a note.
