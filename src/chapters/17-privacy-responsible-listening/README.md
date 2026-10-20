# Chapter 17 code: Privacy, Safety, and Responsible Listening

Chapter: `docs/chapters/17-privacy-responsible-listening/index.md`

```bash
cd src/chapters
./upload-chapter.sh 17 02-indicator-demo.py
```

This chapter is mostly about decisions, so most of its files run on your
computer. Files in `tools/` never go to the Pico. The Privacy and Consent Plan
template and its Cedar Ridge example are ordinary Markdown files for a teacher
or parent to read. **None of this is legal advice.** Read your own school's
policies and ask your school's privacy officer.

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `listening_indicator.py` | none (a module; runs on a computer too) | Imported by the files below; defines `Listener`, `LedIndicator`, `StatusBarIndicator` |
| `01-mute-switch.py` | Pico; optional: slide switch on GP9, microphone | Switch off: pin reads 1, microphone opens. Switch on: pin reads 0, "MIC OFF" |
| `02-indicator-demo.py` | Display, MODE button, microphone; optional GP9 switch | LED and status bar change the instant MODE is pressed and released |
| `03-indicator-test.py` | none (computer or Pico) | Six scenarios ok, both broken listeners CAUGHT, no direct mic opens, PASS |
| `04-wipe-buffers.py` | none (computer or Pico) | Buffer nonzero before, all zero after, PASS; on the Pico note "wipe ms" |
| `tools/data_flow.py` | computer | The eight hops with who sees, where stored, how long; audio-volume arithmetic |
| `tools/threat_model.py` | computer | Ten threats sorted by likelihood x impact, with effort to fix |
| `tools/injection_demo.py` | computer | Naive agent RUNS `send_message`; guarded agent BLOCKS it |
| `tools/retention_sweep.py` | computer | Dry run lists old files; `--delete` removes only those |
| `tools/check_secrets.py` | computer, inside the git repo | PASS, or a file and line number (never the secret itself) |
| `tools/check_plan.py` | computer | PASS on the Cedar Ridge example; NEEDS WORK on the blank template |
| `privacy-and-consent-plan-template.md` | none | A worksheet with 26 fields |
| `privacy-and-consent-plan-cedar-ridge-example.md` | none | The same worksheet filled in for the synthetic school |

## Wiring the optional mute switch

GP9 is not used by anything in `config.py`. For a **software-visible** mute,
wire a switch between GP9 and GND. For a **true hardware** mute, use a two-pole
slide switch: one pole in the microphone's VDD wire (3V3 to VDD), the other
pole from GP9 to GND, so the program can show the state. Check with a
multimeter that the microphone's VDD pin reads about 0 V with the switch on.

## The most important tests for the book

- From `01` with a **true VDD switch**: write down the `spread` the microphone
  reports while its power is cut. The chapter makes no claim about it.
- From `02`: press and release MODE 20 times and watch for any moment when the
  LED and the status bar disagree with whether you are holding the button.
- From `04`: the "wipe ms" for the 150 KB buffer.
- With a network monitor (for example Wireshark) on a push-to-talk device:
  confirm no audio leaves the Pico before you press MODE. See the chapter's
  always-on approval checklist.

## What has been checked, and what has not

- Every file compiles. `03`, `04`, and all the `tools/` run on a computer.
  The mutation check was done: deleting the `deinit()` call from `stop()` makes
  `03` print FAIL. `01` and `02` run to completion against a fake Pico layer
  (virtual clock, fake pins and I2S) with a scripted mute switch and MODE
  button; that checks the logic, not the wiring.
- Nothing here has run on the Pico yet. Unmeasured: what the INMP441 sends when
  its power is cut, how long `wipe()` takes, how long the status bar redraw
  takes, and whether a fixed-size 120 x 20 bar is easy to see from across a room.
