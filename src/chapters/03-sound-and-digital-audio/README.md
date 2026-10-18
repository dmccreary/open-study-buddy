# Chapter 3 code: Sound and Digital Audio Basics

Chapter: `docs/chapters/03-sound-and-digital-audio/index.md`

```bash
cd src/chapters
./upload-chapter.sh 03 01-alias-tone.py
```

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-alias-tone.py` | Amplifier + speaker | 9,000 Hz sounds lower than 7,000 Hz (aliasing) |
| `02-wav-header.py` | none (also runs on a computer) | 44-byte header, 25,644-byte file, PASS |
| `03-clipping-demo.py` | Speaker optional | Gain 2 and 4 clip 0 samples; gain 8 and 24 clip many |
| `04-bit-depth-quantizer.py` | none (also runs on a computer) | Levels double, worst error halves, PASS |
| `05-mic-loudness-db.py` | Microphone | Floor about 12 to 13 bits; +1 bit is about +6 dB |

Measurements worth recording: the noise floor from `05` (the README says
12.5 bits), and whether your ear agrees with `01` that 9,000 Hz folds to 3,800 Hz.
