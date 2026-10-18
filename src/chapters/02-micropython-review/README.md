# Chapter 2 code: MicroPython Review for Embedded Systems

Chapter: `docs/chapters/02-micropython-review/index.md`

Upload the kit and this chapter, then run one file at a time (quit Thonny first):

```bash
cd src/chapters
./upload-chapter.sh 02 01-memory-report.py
```

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-memory-report.py` | Pico | Report prints; the 3 s recording fits |
| `02-pull-up-button.py` | MODE button | 1 idle, 0 pressed |
| `03-timer-blink.py` | Pico | LED blinks while the main loop keeps counting |
| `04-button-interrupt.py` | MODE button | Raw edges >= interrupt >= polling |
| `05-bytes-struct-memoryview.py` | none (also runs on a computer) | Last line says PASS |
| `06-try-finally-mic.py` | Microphone | Frames print; Ctrl-C releases the mic; reruns cleanly |
| `07-heap-fragmentation.py` | Pico | Big request fails at step 3, succeeds at step 5 |

Write down the numbers from test 01 and the totals from test 04 with different
`POLL_MS` values; the chapter's tables use them.
