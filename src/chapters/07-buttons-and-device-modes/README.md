# Chapter 7 code: Buttons, State Machines, and Device Modes

Chapter: `docs/chapters/07-buttons-and-device-modes/index.md`

```bash
cd src/chapters
./upload-chapter.sh 07 01-button-events.py
```

`buttons.py` (the debounced `Button` class) and `device.py` (the five-mode
state machine) are modules the tests import. The upload script copies them
with the tests.

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-button-events.py` | Three buttons | Tap: press, release ~100 ms. Hold: press, long, release |
| `02-bounce-capture.py` | MODE button | Raw traces print; summary says whether 30 ms is enough |
| `03-device-modes.py` | Display + buttons | Every transition matches the chapter's table |
| `04-state-machine-selftest.py` | none (also runs on a computer) | Every row "ok", PASS |
| `05-nonblocking-deadline.py` | Pico (MODE optional) | Blocking: 3 passes; non-blocking: thousands |
| `06-volume-beep.py` | Display + buttons + speaker | Beep gets louder with the number; stops at 0 and 100 |

Run `04` first: it needs no hardware and checks the logic. On your computer:

```bash
cd src/chapters/07-buttons-and-device-modes
python3 04-state-machine-selftest.py
```

**Record these:** the worst settle time from `02` (the chapter assumes bounce
is well under 30 ms), and the passes-per-second from `05`.

If you capture traces with `02`, paste the "5 ms" line into a new trace in the
debounce activity to see how your own switch behaves.
