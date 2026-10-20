---
title: "Testing, Integration, and Capstone Projects"
description: "How to find and fix problems on the Study Buddy and finish it: serial debugging and logging, probe programs, wiring verification, a self-test, diagnosing a silent microphone, distorted audio, or a blank display, a frame overrun counter, system integration inside a 40 ms frame, four capstone projects, and user testing."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 13:21:41"
version: 1.11
---

# Testing, Integration, and Capstone Projects

## Summary

This chapter combines every earlier feature into one finished device. Students use probes, self-tests, logging, and diagnostic checklists to find and fix wiring, audio, and display problems, and then integrate the clock, audio, DSP, and agent features. The chapter ends with capstone projects such as a clap detector, a classroom noise monitor, and a study timer buddy.

## Concepts Covered

This chapter covers the following 16 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Logging | 3 |
| Probe Programs | 6 |
| Serial Debugging | 1 |
| Self-Test Program | 5 |
| Wiring Verification | 4 |
| Diagnosing Silent Microphone | 1 |
| Diagnosing Distorted Audio | 1 |
| Diagnosing Blank Display | 1 |
| Frame Overrun Counter | 1 |
| System Integration | 7 |
| Capstone Project | 6 |
| Clap Detector | 1 |
| Classroom Noise Monitor | 1 |
| Study Timer Buddy | 1 |
| Homework Reminder Buddy | 1 |
| User Testing | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../01-personal-agents-architecture/index.md)
- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 3: Sound and Digital Audio Basics](../03-sound-and-digital-audio/index.md)
- [Chapter 4: The Pico Kit Hardware and Wiring](../04-pico-kit-hardware/index.md)
- [Chapter 5: Display Basics: Pixels, Color, and Frame Size](../05-display-basics/index.md)
- [Chapter 6: Drawing Directly to Display Regions](../06-display-regions-and-drawing/index.md)
- [Chapter 7: Buttons, State Machines, and Device Modes](../07-buttons-and-device-modes/index.md)
- [Chapter 8: I2S Audio: Recording and Playing Sound](../08-i2s-audio/index.md)
- [Chapter 9: Signal Processing and the FFT](../09-signal-processing-fft/index.md)
- [Chapter 10: High-Performance MicroPython](../10-high-performance-micropython/index.md)
- [Chapter 11: Microphone Calibration and Push-to-Talk](../11-mic-calibration-push-to-talk/index.md)
- [Chapter 13: Wi-Fi, HTTP, and Connecting to the Agent](../13-wifi-http-agent-link/index.md)
- [Chapter 14: Streaming Speech, Security, and Network Resilience](../14-streaming-security-resilience/index.md)
- [Chapter 16: Configuring the School Agent and Calendar](../16-school-agent-calendar/index.md)

---

## From Parts to a Working Device

You now have every piece of the Study Buddy: wired parts, a display that redraws only what changed, a button state machine, and a microphone and speaker on I2S, plus sound analysis, a wake word, and a link to the school agent. This chapter is about the skill that makes all of that survive real life, which is finding out what is wrong when something is. Then you put the pieces together and build something of your own.

!!! mascot-welcome "From Working Parts to a Working Device"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    In this chapter you will build the tools that find a bad wire in minutes, put every subsystem into one loop that keeps up with the microphone, and finish with a project that is yours. Let's listen closely! Every real device spends more time being debugged than being written.

## Seeing What the Device Is Doing

### Serial Debugging

**Serial debugging** means finding a problem by reading the text a program sends over the USB serial port. Everything `print()` writes travels to your computer, where Thonny's shell or `mpremote` shows it. It is the oldest and still the most useful debugging tool on a microcontroller, because it works even when the display does not.

Four rules keep it useful. First, only one program can use the Pico's serial port at a time, so quit Thonny before you run `mpremote` (Chapter 2). Second, print what you need to decide something: the value, its unit, and a label. Third, do not print on every 40 ms frame. Twenty-five lines a second floods the shell and slows the loop; print about once a second, as Chapter 8's `02-mic-frame-reader.py` does. Fourth, use the REPL to try one line at a time before you write it into a file.

| Task | Command | Notes |
|------|---------|-------|
| List the connected boards | `mpremote connect list` | If your Pico is missing, check the cable (some are charge-only) |
| Open the REPL | `mpremote repl` | Ctrl-C stops the program; Ctrl-D soft-reboots; the exit key is printed when it starts |
| Run a file without saving it | `mpremote run selftest.py` | The file stays on your computer |
| Run one line | `mpremote exec "import selftest; selftest.run()"` | For a file already on the Pico |
| Read a file from the Pico | `mpremote fs cat :log.txt` | Or copy it: `mpremote fs cp :log.txt .` |
| Restart the program | `mpremote soft-reset` | The upload script uses this too |

!!! mascot-warning "machine.reset() Ends Your Conversation"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    `machine.reset()` restarts the whole chip, so the USB connection drops, the last lines you printed may never arrive, and every pin and bus goes back to its start state. A program that resets itself on every error can trap you in a reset loop that never reaches the REPL. While developing, print the problem and stop; to get out of a loop, send Ctrl-C right after connecting, then run `mpremote fs rm main.py`.

### Logging

**Logging** is `print()` with discipline: each line has a time, a level, and a message, and the program decides where each line goes. `log.py` keeps three places, because each costs something different.

| Place | What goes there | Cost | Lost when |
|-------|-----------------|------|-----------|
| Serial (the shell) | Lines at or above `level` | Time to print | The shell is closed |
| RAM ring | Every line, in a ring of the last `ring` lines | A few hundred bytes | Power goes off |
| Flash file | WARN and ERROR only, with a size cap | Slow writes; flash wears (Chapter 2) | Never, until you delete it |

The four levels are DEBUG (details for a bug hunt), INFO (normal events), WARN (odd but recovered), and ERROR (something failed). The ring is the trick that matters most: after something strange, `log.dump()` shows what happened just before, even though you were not printing it. The flash file is capped. When a write would pass `max_bytes`, the file is renamed to `log.txt.1`, replacing the older copy, so the worst case is twice the cap.

```python
from log import Log, INFO, WARN

log = Log(level=INFO, ring=40, path="log.txt", max_bytes=8192)
log.info("mic opened at %d Hz", 12800)
log.warn("frame overrun: %d us", 52000)
log.dump()
```

The first line makes a logger that prints INFO and above, keeps the last 40 lines in RAM, and writes WARN and above to `log.txt`, never letting it pass 8,192 bytes. Each `%d` is filled in by the argument that follows it, in the old `%` formatting style. The last line prints the ring, oldest line first. `01-log-demo.py` writes 200 lines through a deliberately tiny 400-byte cap and checks that the ring holds exactly the last 10, that the file stays under the cap, and that only WARN and ERROR reached flash. It runs on a computer too, and it prints `PASS`.

One rule from Chapter 17 applies to every log: never log audio or the words people said. Log levels, counts, and codes.

## Probe Programs

### What a Probe Is

A **probe program** is a small program that tests one subsystem and prints evidence about it. A good probe does four things: it touches only the part it tests, it changes nothing that matters, it prints the measured numbers before the verdict, and it ends with one line that says `PASS`, `FAIL`, `ASK`, or `SKIP`. The kit's `02-probe.py` is a probe for the whole board. This chapter adds one per part, so you can ask a narrow question: not "is my kit broken?" but "does the microphone send changing numbers?"

The four verdicts say what the program actually knows. `PASS` means it measured the right thing. `FAIL` means it measured the wrong thing. `ASK` means it cannot tell and a person must look or listen. `SKIP` means the part is not wired. This matters because the display and the amplifier cannot report back to the Pico (the kit README says so), so a probe can draw a pattern but cannot know if you can see it.

| Probe | Part | What it measures | Honest limit |
|-------|------|------------------|--------------|
| `02-display-probe.py` | Display | SPI rate you really got, three timed fills, rings at the glass edge and `SAFE_RADIUS` | A person must say what they saw (ASK) |
| `03-mic-probe.py` | Microphone | Spread, DC offset, loudness in bits, samples at full scale, for 5 s | It cannot tell a swapped wire from no power |
| `04-speaker-probe.py` | Speaker (+ mic) | Plays a 1 kHz tone and listens with the microphone | A quiet room and a far microphone look the same as a dead speaker (ASK) |
| `05-button-probe.py` | Buttons | Idle reads, then each press with its bounce edges | A button that reads 1 may be unwired |
| `06-wifi-probe.py` | Wi-Fi radio | Networks seen, channel, signal; joins if `secrets.py` exists | A 5 GHz-only network never appears |
| `07-wiring-check.py` | All wires | The wire list from `config.py` and the pin-plan rules | It cannot see a wire |

*Worked example.* You run `03-mic-probe.py` and the verdict says `FAIL - flat line: every sample is 12345`. A flat line means the microphone started with no error but sent the same number every time. The probe lists what to check, in the kit README's order: SCK on GP10, WS on GP11, SD on GP12; VDD on 3V3; GND and L/R on GND; and the Chapter 17 mute switch. You find SD and SCK swapped, fix them, and the next run prints a `PASS` line. (The numbers in this example are made up to show the format.)

Every probe calls the same functions in `checks.py`, which is also what the self-test uses. One implementation means a bug is fixed once.

!!! mascot-thinking "A Probe Asks One Question"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Notice what makes a probe powerful: it removes everything but the part under suspicion. When the whole device fails, nothing is learned. When the microphone probe fails with every other part unplugged, you know where to look.

## Wiring Verification

**Wiring verification** is checking every wire against one reference, the pin assignment table from Chapter 4. Most "broken" kits are wiring mistakes, and most wiring mistakes are found by comparing, not by reasoning. The reference must be the same as what the program uses, or the table and the code can drift apart. So the wire list here is *computed* from `config.py`.

`tools/wiring_table.py` reads `config.py` as text, with no Pico modules, and prints the table below. The same function runs on the Pico as `07-wiring-check.py`. A change to a pin in `config.py` changes the printout.

| Part | Part pin | Pico pin | Header pin |
|------|----------|----------|------------|
| Display | SCL | GP2 | 4 |
| Display | SDA | GP3 | 5 |
| Display | RST | GP4 | 6 |
| Display | DC | GP5 | 7 |
| Display | CS | GP6 | 9 |
| Display | BL | GP7 | 10 |
| Microphone | SCK | GP10 | 14 |
| Microphone | WS | GP11 | 15 |
| Microphone | SD | GP12 | 16 |
| Button MODE | one leg | GP13 | 17 |
| Button UP | one leg | GP14 | 19 |
| Button DOWN | one leg | GP15 | 20 |
| Amplifier | DIN | GP19 | 25 |
| Amplifier | BCLK | GP20 | 26 |
| Amplifier | LRC | GP21 | 27 |
| Amplifier | GAIN | GP18 | 24 |

The power wires follow: display VCC and microphone VDD to 3V3 (header pin 36), amplifier VIN to VBUS or 3V3 (pin 40 or 36), and every GND, including the microphone's L/R and the buttons' other legs, to any GND pin. The tool prints these too. Sixteen signal wires are checked by the program; the power wires it cannot see, so you check those by eye.

The method is a ritual. Print the list, put a finger on one wire at a time, say its part and Pico pin out loud, and tick it. Do power and ground last, and check that the microphone's VDD goes to 3V3, not 5 V (Chapter 4). Then run `check_pin_plan`, which tests three rules the table cannot show by itself: each I2S word-select pin is the clock pin plus one, no GP number is used twice, and none of GP23, GP24, GP25, or GP29 (the wireless chip's) is used.

*Worked example.* The kit's `config.py` is edited so the microphone's WS is GP13, to match a wire placed there. The pin-plan check prints `FAIL - microphone word select GP13 must be GP11 (clock + 1); GP13 used by 'Microphone WS' and 'Button MODE one leg'`. It names the rule *and* the second victim, because GP13 is also the MODE button. The fix is the one the kit README gives: move the wire, and do not edit `config.py` to match the wrong wire.

## The Self-Test Program

A **self-test program** runs every check, prints a verdict per subsystem, and shows a summary on the display. `selftest.py` is built from the same `checks.py` functions as the probes. You run it after assembling, after every change, and, if you like, at power-up.

| Check | What it measures | What it cannot know |
|-------|------------------|---------------------|
| Files | `config.py`, the driver, both fonts are on the board | Whether they are the right versions |
| Memory | Free heap, and that a 3 s recording (153,600 bytes) fits | How fragmented the heap will be later |
| Flash | At least 64 KB of flash free | Wear |
| Pin plan | The three pin rules above | A wire in the wrong hole |
| Buttons | All three read 1 when untouched; optionally each press and its bounce | An unwired button reads 1 |
| Display | Draws a ring and text, then asks UP or DOWN | It cannot see the screen: ASK, then a person decides |
| Microphone | Not a flat line, no full-scale samples, loudness and DC offset | Whether the L/R wire is on the channel the program reads |
| Speaker | Plays a 1 kHz tone and checks the microphone hears it at least 2.0 bits above the room | Whether it sounds good |
| Wi-Fi | The radio sees networks; joins if `secrets.py` exists | Whether the school server is up |

The speaker check borrows Chapter 8's finding that the device hears itself. On the test board a 1 kHz tone at volume 40 read 3.9 bits above the quiet room (about 15 times louder), so the check asks for half of that, 2.0 bits. This is a number from one board. If your speaker is quieter, or the microphone is farther away, the check says `ASK` instead of `FAIL`, because "the microphone did not hear it" is not proof that nobody could.

*Worked example.* This is what the self-test prints when the microphone's WS wire is on GP13 (produced by running the real program against a fake Pico layer where the fault was simulated, so the timings are left out).

```
Files       PASS config.py, driver and both fonts are present
Memory      PASS heap 180,000 bytes free; a 3 s recording fits
Pin plan    FAIL microphone word select GP13 must be GP11 (clock + 1); GP13 used by 'Microphone WS' and 'Button MODE one leg'
Buttons     PASS all three read 1 (not pressed); an unconnected wire also reads 1
Display     PASS a person saw the ring and the text
Microphone  FAIL microphone failed to start: invalid ws (must be sck+1) (word select must be the pin after the clock: SCK GP10, WS GP11)
Speaker     PASS a person heard the beep
Wi-Fi       PASS radio sees 2 network(s); no secrets.py, so no connection tried

7 PASS  2 FAIL  0 ASK  0 SKIP
```

Two lines point at the same wire from two angles: the pin-plan rule, and the error that `I2S()` raised. When two checks agree, trust the diagnosis. The summary also appears on the round display, one row per check, with the word as well as a color, so a person who cannot tell red from green reads the same result. A row is `"{:<11}{:>5}"`, 16 characters at 8 pixels each, 128 pixels wide. The first row sits at y = 62, where the visible circle of radius 168 is \( 2\sqrt{168^2 - 118^2} \approx 239 \) pixels wide, so it fits with room to spare.

## Diagnosing the Three Classic Failures

A **diagnosis** goes from a symptom to a cause, asking the cheapest question first. Three failures account for most "it doesn't work" reports on this kit: a silent microphone, distorted audio, and a blank display. Each table below is a decision tree written flat. Start at the first row and ask its question. If the answer is yes, that row's cause is your likely cause: run its quick test, then apply the fix. If the answer is no, go to the next row. Every cause comes from the kit README, a test file's header, or an earlier chapter, and `tools/diagnose.py` asks the same questions at the terminal. A tree names the *likely* cause, so run the quick test before you change anything.

### Diagnosing a Silent Microphone

The symptom is a level meter that never moves, or a probe that reports a flat line.

| Row | Ask | Likely cause | Quick test | Fix |
|-----|-----|--------------|------------|-----|
| M1 | An error at start, and it says `must be sck+1`? | WS is not on the pin after SCK | Compare with the table: SCK GP10, WS GP11 | Move the wire back. Do not edit `config.py`: SCK on GP12 would need WS on GP13, the MODE button |
| M2 | An error at start, with another message? | A previous run left the I2S block open, or memory is short (likely) | Ctrl-D, run again, print `gc.mem_free()` | Close the microphone in a `finally` block |
| M3 | No error, but the spread is 0 (a flat line)? | Swapped SCK, WS, or SD wires; no power; or the mute switch is on | In order: SCK, WS, SD; VDD on 3V3, not 5 V; GND and L/R on GND; the mute switch | Re-seat the wires. A swapped microphone starts with no error and sends zeros |
| M4 | The loudness barely changes when you talk next to it? | L/R is on 3V3, so the microphone answers in the right slot while the program reads the left | Look at where L/R goes | Move L/R to GND |
| M5 | The meter is pinned at the top? | The 32-bit samples were not shifted right by 8, so values are 256 times too big; or the room or SD wire is noisy | Print a few samples before and after `>> config.MIC_SAMPLE_SHIFT` | Shift by `MIC_SAMPLE_SHIFT` and subtract the frame's DC offset |
| M6 | None of the above | The microphone works; the level you chose is the problem | Probe 03: does a clap jump several bits? | Calibrate the noise floor first; for quiet playback raise `PLAYBACK_GAIN` |

### Diagnosing Distorted Audio

The symptom is a sound that is wrong: silent, crackling, the wrong pitch, stuttering, clicking, or hissing.

| Row | Ask | Likely cause | Quick test | Fix |
|-----|-----|--------------|------------|-----|
| A1 | Is the speaker silent, not distorted? | No power or ground at the amplifier, or a signal wire is wrong | Probe 04; VIN and GND, then BCLK GP20, LRC GP21, DIN GP19 | Fix the wire. If `I2S()` raises an error, LRC must be right after BCLK |
| A2 | Does it crackle only when loud? | The samples clip: peaks are cut flat | Lower `VOLUME`; the crackle should go | Reduce `VOLUME` (test 05) or `PLAYBACK_GAIN` (test 07) |
| A3 | Is the pitch wrong, too high and fast or too low and slow? | The playback sample rate is not the recording rate | Print both rates | Use `MIC_SAMPLE_RATE` for both |
| A4 | Does it stutter or have gaps? | The loop takes longer than one 40 ms frame: a frame overrun | Wrap the microphone in `OverrunCounter`; read the summary | Redraw only changed regions, or slice big jobs |
| A5 | Is the start clicky, or the end cut off? | `deinit()` ran before the buffer drained; or a WAV header was played as sound | Listen with and without `f.seek(44)`; lengthen the tail | Write silence and wait the buffer's length; skip the 44-byte header; fade 10 ms |
| A6 | Is there hiss or buzz even when nothing plays? | Power or ground noise: loose grounds, long wires | Re-seat every GND; keep microphone and amplifier wires apart | Shorter wires and one solid ground rail |
| A7 | None of the above | No cause matched | Play the 05 tone and a 07 recording separately | Fix the path that distorts |

### Diagnosing a Blank Display

The symptom is a screen that shows nothing, or nothing right.

| Row | Ask | Likely cause | Quick test | Fix |
|-----|-----|--------------|------------|-----|
| D1 | Is the screen completely dark, with no light? | The backlight is off: BL not wired, VCC or GND missing, or `set_backlight(True)` never ran | Check BL to GP7, VCC to 3V3, GND | Wire BL to GP7 and call `config.set_backlight(True)` |
| D2 | Did the program stop with an error before drawing? | A kit file is missing: `config.py`, `lib/gc9b72.py`, or a font | Self-test "Files", or `02-probe.py` section 4 | Run `upload-chapter.sh` |
| D3 | Is it lit but only black or random noise? | A control wire is wrong: SCL GP2, SDA GP3, RST GP4, DC GP5, or CS GP6 | `07-wiring-check.py`; touch each wire | Fix the wire; the colors are in `config.py` |
| D4 | Is the picture speckled or torn? | The SPI speed is too fast for the wiring | Print the SPI object to see the rate you got | `BAUDRATE = 12_000_000` (nothing exists between 12 and 24 MHz) |
| D5 | Is part of what you drew missing? | It was drawn outside the visible circle: corners and edge are hidden | Chapter 4's `04-display-visible-area.py` | Stay inside `SAFE_RADIUS`, 168 pixels from the center |
| D6 | Is the picture rotated or mirrored? | The driver's `rotation` argument | Try 0, 1, 2, 3 in `config.init_display()` | Choose the one that matches |
| D7 | Are old letters left over, or is the picture sheared or striped? | Text was not padded to a fixed width, or a buffer is not width x height x 2 bytes | Print `len(buffer)` and compare | Pad with `.center(width)`; size buffers exactly |
| D8 | None of the above | A program from an earlier kit may be running as `main.py` | `mpremote fs ls` | `mpremote fs rm main.py` |

!!! mascot-tip "Cheapest Question First"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Order your own checks by cost, not by how interesting the cause is. "Is it completely dark?" takes one second and splits the display problem in two. Reading a datasheet to explain a speckle can wait until you have tried the 12 MHz setting.

The next activity checks that you can follow a symptom to a cause.

#### Diagram: Diagnosis Decision Tree Trainer


<iframe src="../../sims/diagnosis-decision-tree-trainer/main.html" width="100%" height="642px" scrolling="no"></iframe>
[Run Diagnosis Decision Tree Trainer Fullscreen](../../sims/diagnosis-decision-tree-trainer/main.html)

<details markdown="1">
<summary>Diagnosis Decision Tree Trainer</summary>
Type: microsim
**sim-id:** diagnosis-decision-tree-trainer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** differentiate<br/>
**Learning Objective:** The learner will differentiate the likely cause of each of 6 reported kit failures from three other causes in the same decision tree, choosing the correct cause for at least 5 of 6 cases.

**Prerequisites:** flat line, backlight, sample rate, frame overrun, wire swap (all defined in the sections of this chapter above this block and in Chapters 4 and 8); the three diagnosis tables in this chapter, whose rows are named M1 to M6, A1 to A7, and D1 to D8.

**Evidence of Mastery:** For each of the 6 cases the learner reads the reported symptoms and chooses one of 4 candidate causes before the decision tree is shown. A choice is correct when it equals the Correct row in Content. Mastery is 5 of 6 correct on the first attempt. Walking the tree by answering its questions in exploration is not evidence.

**Misconceptions:** (1) Any failure of the microphone means the microphone is broken. (2) A program that runs without an error has no wiring fault. (3) A dark screen is always a software bug. (4) The answer to a distorted sound is always to lower the volume.

**Instructional Rationale:** Differentiating at the Analyze level means telling apart causes that produce similar symptoms. Asking the learner to commit to a cause from four candidates, and only then showing the tree that leads to it, makes the learner use the symptom details that separate the candidates.

**Content:**

The sim has three trees, one per symptom: silent microphone (rows M1 to M6), distorted audio (rows A1 to A7), and blank display (rows D1 to D8). A tree is a list of rows. Each row asks a yes-or-no question; yes ends the walk at that row's cause, and no goes to the next row of the same tree. The last row of each tree (M6, A7, D8) has no question and is reached when every earlier answer is no. The rows, with their questions, causes, quick tests, and fixes, are the rows of the three tables in the chapter section "Diagnosing the Three Classic Failures". The questions, in order:

| Row | Question |
|---|---|
| M1 | An error at start, and it says "must be sck+1"? |
| M2 | An error at start, with another message? |
| M3 | No error, but the spread is 0, a flat line? |
| M4 | The loudness barely changes when you talk next to it? |
| M5 | The meter is pinned at the top? |
| A1 | Is the speaker silent, not distorted? |
| A2 | Does it crackle only when loud? |
| A3 | Is the pitch wrong? |
| A4 | Does it stutter or have gaps? |
| A5 | Is the start clicky, or the end cut off? |
| A6 | Is there hiss or buzz even when nothing plays? |
| D1 | Is the screen completely dark, with no light? |
| D2 | Did the program stop with an error before drawing? |
| D3 | Is it lit but only black or random noise? |
| D4 | Is the picture speckled or torn? |
| D5 | Is part of what you drew missing? |
| D6 | Is the picture rotated or mirrored? |
| D7 | Are old letters left over, or is the picture sheared or striped? |

The 6 cases, in this order. Each case lists the 3 other candidate causes, which are rows of the same tree.

| # | Reported symptoms | Correct row | Three other candidates (rows) |
|---|---|---|---|
| 1 | "The microphone test stops at once with: invalid ws (must be sck+1)." | M1 | M3, M4, M5 |
| 2 | "No error. The probe says every sample is 12345 and the spread is 0." | M3 | M1, M4, M6 |
| 3 | "The screen is completely dark. The program runs and prints no errors." | D1 | D2, D3, D4 |
| 4 | "The screen is lit and shows the right picture, but it is speckled, on long wires." | D4 | D3, D5, D7 |
| 5 | "A recording I made plays back higher and faster than I spoke." | A3 | A2, A4, A6 |
| 6 | "The sound stutters. The overrun counter reports many passes longer than 40 ms." | A4 | A1, A3, A5 |

**Provenance:** The causes and tests come from the kit README, the headers of kit tests 05 and 07, `config.py`, and Chapters 2 to 8, as cited in the `source` field of `src/chapters/18-testing-integration-capstones/tools/diagnose.py`. The six cases are illustrative, and the sim labels them "illustrative".

**Rules:** Each case has exactly one correct row. A tree question is answered only yes or no. The candidate order is shuffled for each learner, with a fixed seed per case.

**Learner Activity:**

1. The learner explores one tree: picks a symptom, answers its questions, and reads the cause, test, and fix at the end.
2. The learner starts the 6 cases. Case 1 shows its symptoms and the four candidate causes.
3. The learner chooses a cause and submits.
4. The sim shows the correct cause, then walks the tree for that case, highlighting the questions answered and the cause reached, with the quick test and the fix.
5. After case 6, the sim shows the score. The learner should notice that the cheap early questions rule out whole branches.

**Feedback:** 6 cases, fixed order, one attempt each. Correct: "Correct: <cause text>". Incorrect: "Not quite. The likely cause is <correct cause text>: look at <the symptom detail that separates it from the chosen cause>". The correct cause is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The three symptom names are shown with the question "Which one are you diagnosing?" and no tree open.

**Chapter Anchors:** The chapter names three failures (silent microphone, distorted audio, blank display); states that the microphone tree has rows M1 to M6, the audio tree A1 to A7, and the display tree D1 to D8; that a swapped microphone starts with no error and sends zeros; that the sck+1 rule applies to the microphone and the amplifier; and that BAUDRATE 12,000,000 is the fix for speckle.
</details>

## System Integration

### Putting the Subsystems in One Loop

**System integration** is making the parts you built separately work together without breaking each other. Each earlier chapter was tested alone, with the whole 40 ms frame to itself. In the finished device they share it. The integration question is never "does each part work?" but "does the sum of the parts fit in the time, memory, and attention available?"

Start with a map. The device has six subsystems, and a state machine (Chapter 7) decides which are active.

| Subsystem | Owns | Talks to | Built in |
|-----------|------|----------|----------|
| Input | Three buttons, microphone read | The state machine, audio | Chapters 7, 8 |
| Audio | I2S in and out, tones, playback | Input, DSP, the speaker | Chapters 3, 8 |
| DSP | Loudness, FFT, band energies, wake word | Audio, display | Chapters 9, 10, 12 |
| Display | Regions: status, time, mascot, spectrum, message | State machine, DSP | Chapters 5, 6 |
| Network | Wi-Fi, HTTP, MQTT `check_msg` | Agent, state machine | Chapters 13, 14, 15 |
| Agent | The buddy server and its calendar | Network only | Chapters 1, 16 |

The main loop of the finished device has one structure: wait for a frame, then run what is due.

```python
sched = Scheduler(frame_us=40000)
sched.add("audio", do_audio, 0, 12)          # period 0 = every pass; budget in ms
sched.add("buttons", do_buttons, 0, 1)
sched.add("spectrum", draw_spectrum, 0, 9)
sched.add("status", draw_status, 200, 4)     # every 200 ms
sched.add("network", poll_network, 200, 3)
while True:
    mic.readinto(buf)      # blocks until a frame is ready: this starts a pass
    sched.run_pass()       # run every task that is due and fits in what is left
```

`scheduler.py` is a **cooperative** scheduler: a task runs until it returns, and nothing can interrupt it. A task's *budget* is therefore a promise, not a limit. What the scheduler can do is run tasks in the order added (earlier means more important); skip a due task whose budget does not fit into the time left in this frame, for at most three passes so it cannot starve; time every run and count the ones that exceed their budget; and count passes that take longer than the frame. The period `0` means "every pass," for the work tied to each audio frame.

A note on buttons: if the loop blocks 40 ms in `readinto`, polled buttons are checked 25 times a second, and a tap shorter than 40 ms can be missed. Either read the microphone in 20 ms chunks as test 07 does, or use the button interrupt from Chapter 7.

### The Frame Overrun Counter

A **frame overrun** is a pass of the main loop that takes longer than one 40 ms frame (Chapter 8 introduced the budget, and Chapter 10 measures it closely). A **frame overrun counter** counts them. It works because `readinto()` blocks until the next frame is ready: the time between two returns of `readinto()` *is* the length of one pass. `overrun.py` wraps the microphone in an object with the same `readinto()` and `deinit()`, so you can drop it in without changing the loop.

```python
mic = OverrunCounter(config.init_microphone())
# ... use mic.readinto(buf) exactly as before ...
print(mic.summary())
```

```python
def _note(self, pass_us):
    if pass_us > self.frame_us + self.jitter_us:
        self.overruns += 1
    self.backlog = max(0.0, self.backlog + pass_us / self.frame_us - 1.0)
    if self.backlog > self.ring_frames:
        self.lost_est += self.backlog - self.ring_frames
        self.backlog = self.ring_frames
```

`_note` is called once per pass. A pass longer than the frame plus `jitter_us` (2 ms, the same timing noise allowance Chapter 8's test used) is an overrun. The backlog is Chapter 8's model: it grows by `pass / frame - 1` frames on a slow pass, shrinks on a fast one, and never goes below zero. When it passes the ring's depth, `ring_frames` (9.77, the depth Chapter 8 measured on one board), the excess is counted as estimated lost frames. Run the model on the passes from Chapter 8: at 50 ms per pass the first loss comes on pass 40, which is \( 40 \times 50 = 2.0 \) seconds, and at 130 ms it comes on pass 5, which is 0.65 seconds. Both match the chapter. The backlog and lost numbers are a model, so treat `overruns` and `worst_us` as measurements and the rest as an estimate. Chapter 10's `06-frame-loop-budget.py` measures the same thing in more detail (a 95th percentile and a display reserve); `OverrunCounter` is the small version you can leave in the finished device.

### The Time Budget in Numbers

The budget table uses numbers measured in earlier chapters wherever they exist. The others are assumptions, marked, which you replace with your own timings.

| Task | Cost per run | Runs | Source |
|------|--------------|------|--------|
| Read a frame and compute its loudness | 10.0 ms | every pass | Chapter 8, plain-Python loudness on the test board |
| Poll the three buttons | 0.5 ms | every pass | Assumed |
| Redraw the spectrum region | 8.5 ms | every pass | Chapter 6, measured |
| Redraw the status bar | 3.0 ms | every 200 ms | Chapter 6, measured |
| Redraw the time region | 3.8 ms | every 1,000 ms | Chapter 6, measured |
| Check for an MQTT message | 2.0 ms | every 200 ms | Assumed |
| One full-screen redraw | 129.4 ms | when it happens | Chapter 5, measured |

A typical pass costs \( 10.0 + 0.5 + 8.5 = 19.0 \) ms, which leaves \( 40 - 19.0 = 21.0 \) ms for the FFT, the wake word, and everything else (Chapter 10's results table is where the FFT's cost is filled in). The worst scheduled pass adds the three periodic tasks: \( 19.0 + 3.0 + 2.0 + 3.8 = 27.8 \) ms, leaving 12.2 ms. Compare two bad plans. Redrawing all five regions every frame costs 28.1 ms measured (Chapter 6), so with the loudness work the pass is \( 10.0 + 28.1 = 38.1 \) ms, only 1.9 ms from the edge. One full-screen redraw makes the pass \( 19.0 + 129.4 = 148.4 \) ms.

`08-scheduler-demo.py` runs these costs through the scheduler in four scenarios. The costs are *inputs to a model*, not measurements of the program, so the results show how the design behaves, not how fast your Pico is. On a computer with a fake clock the output below is what the demo printed for 250 frames (10 seconds).

| Scenario | What it does | Passes over 40 ms | Worst pass | Max backlog | Model-estimated lost |
|----------|--------------|-------------------|-----------|-------------|---------------------|
| normal | Only the tasks in the table | 0 | 27.8 ms | 0.00 frames | 0.00 frames |
| stall | One full redraw (129.4 ms) every 2 s | 5 | 148.4 ms | 2.71 frames | 0.00 frames |
| bug | A full redraw on every pass | 62 | 157.2 ms | 9.77 frames | 71.53 frames |
| sliced | The same redraw in 8 strips of 16.2 ms | 0 | 35.2 ms | 0.00 frames | 0.00 frames |

Read the table in order. The *stall* scenario overruns five times but loses nothing in the model: the pass is \( 148.4/40 - 1 = 2.71 \) frames behind, which is about 108 ms, and the ring holds about 9.8 frames (Chapter 8), so the following light passes catch up. A one-off stall costs *latency*, the delay before the device reacts, not audio. The *bug* scenario never catches up: the backlog sits at the ring's depth of 9.77 frames, and the model says 71.5 frames were lost. The *sliced* scenario does the same job without an overrun by doing \( 129.4/8 \approx 16.2 \) ms of it per pass: \( 10.0 + 0.5 + 8.5 + 16.2 = 35.2 \) ms. When status, network, and the slice would all land in one pass, they total 40.2 ms, so the scheduler defers the slice (its 17 ms budget does not fit in the 16 ms left) and the pass stays at 24.0 ms.

!!! mascot-thinking "A Stall Costs Time, a Treadmill Costs Sound"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Notice the difference between a slow pass and a slow loop. One slow pass makes the device late and then it recovers. A loop that is slow on average never recovers, and that is when audio is lost. Budget for the average, then check the worst case.

The activity below lets you build a pass and see whether it fits.

#### Diagram: Frame Budget Scheduler Timeline


<iframe src="../../sims/frame-budget-scheduler-timeline/main.html" width="100%" height="587px" scrolling="no"></iframe>
[Run Frame Budget Scheduler Timeline Fullscreen](../../sims/frame-budget-scheduler-timeline/main.html)

<details markdown="1">
<summary>Frame Budget Scheduler Timeline</summary>
Type: microsim
**sim-id:** frame-budget-scheduler-timeline<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** examine<br/>
**Learning Objective:** The learner will examine 6 loop passes against the 40 ms frame budget by calculating each pass's total time to within 0.1 ms and deciding whether it overruns, with at least 5 of 6 fully correct.

**Prerequisites:** frame, frame budget, task, task budget, cooperative scheduler, deferral, overrun (all defined in the sections above this block).

**Evidence of Mastery:** For each of the 6 passes the learner types the total milliseconds the pass takes and chooses "overruns" or "fits" before the answer is revealed. A pass is fully correct when the number is within 0.1 ms of the Total column in Content and the choice matches the Overrun column. Mastery is 5 of 6 fully correct. Switching tasks on and off in the free-build timeline in exploration is not evidence.

**Misconceptions:** (1) A task with a big budget only costs its budget. (2) The scheduler can interrupt a task that runs too long. (3) A pass that fits in 40 ms on average cannot overrun. (4) Turning the scheduler on always makes every task run.

**Instructional Rationale:** Examining a pass at the Analyze level means relating its parts to the whole. Summing task costs to a total and comparing it with the frame makes the learner relate each task to the shared budget, and the case where the scheduler defers a task shows how the parts interact.

**Content:**

The tasks, with their cost per run and budget in milliseconds, in the order the scheduler considers them (earlier is more important):

| Order | Task | Cost (ms) | Budget (ms) |
|---|---|---|---|
| 1 | audio | 10.0 | 12 |
| 2 | buttons | 0.5 | 1 |
| 3 | spectrum | 8.5 | 9 |
| 4 | status | 3.0 | 4 |
| 5 | network | 2.0 | 3 |
| 6 | time | 3.8 | 4 |
| 7 | redraw (full screen) | 129.4 | 140 |
| 8 | slice (one eighth of the redraw) | 16.2 | 17 |

The frame budget is 40 ms. The 6 passes, in this order:

| # | Scheduler | Tasks due in the pass | Total (ms) | Overrun | Why (shown as feedback) |
|---|---|---|---|---|---|
| 1 | off | audio, buttons, spectrum | 19.0 | fits | 10.0 + 0.5 + 8.5 = 19.0, which leaves 21.0 ms. |
| 2 | off | audio, buttons, spectrum, status, network, time | 27.8 | fits | 19.0 + 3.0 + 2.0 + 3.8 = 27.8, which leaves 12.2 ms. |
| 3 | off | audio, buttons, spectrum, redraw | 148.4 | overruns | 19.0 + 129.4 = 148.4, which is 108.4 ms over the frame. |
| 4 | off | audio, buttons, spectrum, status, network, slice | 40.2 | overruns | 19.0 + 3.0 + 2.0 + 16.2 = 40.2, which is 0.2 ms over. |
| 5 | on | audio, buttons, spectrum, status, network, slice | 24.0 | fits | After network the pass has used 24.0 ms, which leaves 16.0 ms. The slice's budget is 17 ms, which does not fit, so it is deferred. |
| 6 | off | audio, buttons, spectrum, slice | 35.2 | fits | 19.0 + 16.2 = 35.2, which leaves 4.8 ms. |

**Provenance:** The costs for audio, spectrum, status, and time are the measurements in Chapters 8 and 6, the redraw cost is the Chapter 5 measurement, and the slice cost is 129.4 divided by 8, rounded to 16.2. The buttons and network costs, and all the budgets, are assumed values from `08-scheduler-demo.py`. The sim labels the costs "model inputs, not a measurement of your program."

**Rules:** Total = sum of the costs of the tasks that run in the pass. A pass overruns when Total > 40.0. With the scheduler on, tasks are considered in the Order column; a task is deferred (not run) when its budget is greater than 40.0 minus the total so far. With the scheduler off, every due task runs. Answers are in milliseconds with one decimal place.

**Learner Activity:**

1. The learner switches the 8 tasks on and off in a free-build timeline and flips the scheduler on and off. The timeline shows each task as a block along the 40 ms frame, and a block past 40 ms is marked as an overrun.
2. The learner starts the 6 passes. Pass 1 shows the scheduler setting and the due tasks.
3. The learner types the total and chooses overruns or fits, then submits.
4. The sim reveals the total, draws the pass on the timeline, marks any deferred task, and shows the Why text.
5. After pass 6, the sim shows the score. The learner should notice that passes 4 and 5 hold the same tasks and differ only in the scheduler.

**Feedback:** 6 passes, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The total is <Total> ms and it <overruns or fits>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The timeline shows the three always-due tasks (audio, buttons, spectrum) with the scheduler off, and the question "How much of the 40 ms is left?"

**Chapter Anchors:** The chapter states the task costs in the table "The Time Budget in Numbers"; that a typical pass is 19.0 ms and the worst scheduled pass is 27.8 ms; that a full-screen redraw makes a pass 148.4 ms; that the slice is about 16.2 ms and a pass with status, network, and the slice would be 40.2 ms; and that the scheduler defers the slice, leaving 24.0 ms.
</details>

### Build Order and the Regression Checklist

The order you assemble the device in is part of the design, because each step gives the next a working base.

1. Pico alone: kit test 01 (the LED blinks) and test 02 (the board probe).
2. Buttons: test 03. Display: test 04. Speaker: test 05. Microphone with the display: test 06. Everything: test 07.
3. Add logging and the self-test (this chapter). From now on, run `selftest.py` after every change.
4. Add the audio loop with the `OverrunCounter`, then the display regions inside the scheduler.
5. Add DSP (Chapters 9 and 10), calibration and push-to-talk (Chapter 11), and the wake word (Chapter 12).
6. Add the network link (Chapters 13 and 14), MQTT alerts (Chapter 15), and the school agent (Chapter 16).
7. Add the privacy features of Chapter 17: the hardware mute, the listening indicator, and the plan.

A **regression** is something that used to work and no longer does, and it is the most common bug in a growing device: you add a feature and break an old one. The defense is to run the same short checklist after every change.

| After every change, check | How | Passes when |
|---------------------------|-----|-------------|
| The kit still checks out | `selftest.py` | No FAIL |
| The display still updates quickly | Watch a changing region; run `02-display-probe.py` if unsure | Fills time like before |
| The loop keeps up | Read the `OverrunCounter` summary after 60 s | 0 overruns, or only the ones you expect |
| Push-to-talk still works end to end | Hold MODE, ask a question, hear the reply | Reply plays, then the clock returns |
| The listening indicator is still true | `03-indicator-test.py` from Chapter 17 | PASS |
| Nothing new is stored | `mpremote fs ls` | No audio or transcript files |
| Secrets stay out of git | `check_secrets.py` | PASS |

## Capstone Projects

### Choosing and Scoping a Capstone

A **capstone project** is a device feature you design, build, test, and defend yourself, using what the book taught. It is the difference between following a recipe and cooking. Every capstone needs the same six things before you start, and a rubric (below) grades the same six.

1. A one-sentence purpose in plain words, and the one person it is for.
2. A list of requirements you can test, each a sentence that ends in "so that ..." or a number you measure.
3. Thresholds that come from a **calibration step the program runs** (Chapter 11's idea: measure the quiet room first), never from a number you guessed or copied.
4. A passing `selftest.py`, and an `OverrunCounter` summary you can show.
5. A privacy statement: what the device hears, what leaves it, what is kept, and who knows (Chapter 17).
6. A user test with at least three classmates (below).

The four starters in this chapter each work on the base kit, use only what the book has taught, and are small enough to finish in a few sessions. They are starting points: change the purpose and they become your own. The logic of each lives in `detectors.py`, which `09-detectors-test.py` exercises on **synthetic** sound and scripted buttons. Synthetic means made up by the test: it shows how the logic behaves, not how a real clap, voice, or fan looks to your microphone.

### Clap Detector

A **clap detector** notices a short, sharp sound. Speech and steady noise stay loud for many frames; a clap is loud for one or two frames and falls straight back. `ClapDetector` therefore watches the frame loudness in bits (the log scale from Chapter 3) and reports a clap when a run of one or two frames at least `jump` bits above the calibrated floor ends. The jump is `max(2.0, 4 x the spread of the quiet frames)`, so a noisier room needs a bigger jump. The 2.0 is the "heard" margin of kit test 06: 2 bits is 4 times the quiet room's average level.

Here is what 09 printed for the synthetic room, whose noise floor was built to be 12.5 bits like the test board's.

| Burst peak compared with the room's noise amplitude | Claps found out of 40 |
|-----------------------------------------------------|------------------------|
| 10 times | 0 |
| 20 times | 0 |
| 40 times | 1 |
| 80 times | 40 |
| 160 times | 40 |

Read the table as a sensitivity curve. The sharp edge between 40 and 80 times exists because an 8 ms burst is only a small part of a 40 ms frame's average, so it must be loud to move the frame by 2 bits. Your real threshold depends on your microphone and room, which is why the program calibrates. Two more results from the same test: 180 seconds of syllable-like sound made 0 false claps, and 180 seconds after a fan-like step to 4 times the noise made 0 false claps (the floor drifted up to it). But a single loud frame, such as a sharp "p" or "k", counted as a clap 40 times out of 40. That is a limit of the design, not a bug: it cannot separate a one-frame spike from a clap. `Try This` in the program suggests adding a crest-factor check.

| Requirement | Test |
|-------------|------|
| Learns the quiet room before listening | The shell prints the floor and jump after 2 s |
| Counts a clap near the microphone | 5 claps at 0.5 m count 5 |
| Ignores talking and steady noise | 30 s of talking and a fan count 0 |
| Two claps within 1 s toggle a light | The on-screen light switches |
| Reports what it cannot do | The README lists the one-frame-spike limit |

Extensions: record the distance at which claps stop counting at 0.5, 1, 2, and 4 m; add the crest-factor check; make a triple clap do something different.

### Classroom Noise Monitor

A **classroom noise monitor** shows how loud a room is as one of three words, QUIET, TALKING, or LOUD. `NoiseMonitor` smooths the loudness with a moving average (time constant 1 second by default, like the slow setting of a sound level meter), compares it with limits that are *bits above the room's own floor*, and changes the word only after the new band has held for 12 frames (0.5 s) so it does not flicker. The limits are 2.0 and 4.0 bits above the floor, which is 4 and 16 times the quiet level, or about 12 and 24 dB. These are **relative to your microphone and room**, not sound-pressure decibels, because the microphone is uncalibrated. The starting limits are values to tune with your class.

On the synthetic 60 seconds (20 s quiet, 20 s at 6 times the noise, 10 s at 25 times, 10 s quiet), the band was TALKING at the end of the second stretch (smoothed level +2.6 bits above the floor), LOUD at the end of the third (+4.7 bits), and QUIET again at the end. The monitor counted 30.6 s QUIET, 20.4 s TALKING, and 9.0 s LOUD, which add to 60: the smoothing and the 0.5 s dwell shift a little time between bands. A sound that flickered across the limit every 3 frames changed the band 0 times in 20 seconds.

!!! mascot-warning "Level Only: Say So, and Mean It"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A noise monitor is still a microphone in a classroom, so build it so it cannot keep sound: it is handed one number per frame, keeps three counters, and writes no file. Put "Level only. No audio saved." on the screen and tell the room first (Chapter 17).

| Requirement | Test |
|-------------|------|
| Level only | The code never stores samples or writes a file; `mpremote fs ls` shows none |
| Says so | The screen shows "Level only. No audio saved." |
| Calibrates | The floor is measured at start and shown |
| Stable | The word does not flicker when someone speaks at the limit |
| Summarizes | Seconds per band are printed each minute |

Extensions: let UP and DOWN change the limits and save them; show the last 10 minutes as a strip chart in one region; ask three classmates what "too loud" means for silent reading and for group work, and set two modes.

### Study Timer Buddy

A **study timer buddy** runs focus and break periods so a student can work in short blocks. `StudyTimer` is a state machine (Chapter 7) with three states, IDLE, FOCUS, and BREAK, plus a paused flag. MODE starts, pauses, or resumes; a long MODE press skips to the other phase; UP and DOWN change the focus length from 5 to 60 minutes while idle. The defaults of 25 minutes of focus and 5 of break, with a 15 minute break after every 4th focus, are common study-technique values, and they are settings you can change.

Time comes from a deadline, not from counting seconds in a loop (Chapter 7's non-blocking rule). The timer stores when the phase ends, and `remaining = end - now` is computed each pass with `time.ticks_diff`, so a slow pass cannot make the clock drift and the millisecond counter's wrap-around is handled. Pausing stores the remaining time; resuming sets a new end. A 25 minute focus is \( 25 \times 60 \times 1000 = 1{,}500{,}000 \) ms.

The scripted test in 09 checks that 15:00 remain after 10 minutes of a 25 minute focus, that 30 minutes spent paused change nothing, that the 4th focus is followed by the 15 minute break, and that a focus still ends on time when the millisecond counter wraps in the middle of it. The program redraws a region only when its text changes, so the screen sends bytes once a second.

| Requirement | Test |
|-------------|------|
| Starts, pauses, resumes with MODE | A scripted press sequence gives the right states |
| Stays accurate | 25:00 ends within one pass of 25 minutes by a stopwatch |
| Never blocks | The `OverrunCounter` shows 0 overruns |
| Beeps at the end of each phase | You hear it, then the next phase begins |
| Redraws only what changed | Only the seconds change on screen each second |

Extensions: hold UP to ask "how long is left?" through the push-to-talk path (Chapters 11 and 14); let the mascot sleep during focus and wake for breaks; count completed focus periods across the day.

### Homework Reminder Buddy

A **homework reminder buddy** shows the next `TEST:` and `DUE:` items and how soon each is. It uses the same title convention as the school agent (Chapter 16): a title that starts with `TEST:` or `DUE:` is a reminder, and anything else is ignored. The program must work *with or without* the agent. It reads `events.json` from the Pico if you copied one (`tools/trim_events.py` cuts the 92-event Cedar Ridge file of 27,187 bytes down to the 50 test and due events, 4,197 bytes), and otherwise uses a three-item list built into the file. The agent link is an upgrade, not a requirement: replace `load_events()` with a request to your server when it is ready.

Dates use plain arithmetic: `day_number(y, m, d)` turns a date into a day count, and the difference of two counts is the days between them, with no `datetime` module. The test checks month ends, a leap day, and that `date_text` undoes `day_number` for 576 dates. A Pico has no calendar until you give it one, so "today" starts at the Cedar Ridge demo date of 2026-10-19 and UP and DOWN move it a day at a time.

On that date the reminders are, soonest first: TOMORROW, the Algebra II test; IN 2 DAYS, the English draft; IN 3 DAYS, the Biology report. An alert and a beep happen once, the first time an item is tomorrow or today, and `Reminders` remembers what it has announced so it does not repeat.

| Requirement | Test |
|-------------|------|
| Works with no agent and no network | Start with no `events.json`: the built-in list appears |
| Reads only TEST and DUE | The picture day and the football game are not shown |
| Sorts soonest first | The three items appear in 1, 2, 3 day order |
| Announces once | Moving the date back and forth does not repeat an alert |
| Respects privacy | Only school events are used; no student data is stored |

Extensions: read the same file from the school server (Chapter 16); add a second alert "3 days before" a test; show the course name from the event.

### Grading a Capstone

Use one rubric for all four projects, so the grade measures the same skills whatever you built. Each criterion has three levels: Meets (full points), Approaching (about half), and Not yet (none).

| Criterion | Points | Meets |
|-----------|--------|-------|
| Function | 5 | Every requirement in your list passes its test, and you show the tests |
| Calibration | 3 | Thresholds come from a measurement the program makes, shown on screen or in the log |
| Reliability | 3 | `selftest.py` passes, and the `OverrunCounter` shows no unexpected overruns |
| Privacy | 3 | The device says what it hears and keeps; a plan exists; nothing stores audio |
| User testing | 3 | Three or more testers, notes kept, at least one change made because of what they did |
| Code and notes | 3 | Pins come from `config.py`, regions redraw only on change, and a README gives wiring and test results |

That is 20 points. A capstone that passes every requirement but skips the user test cannot score above 17.

### User Testing

**User testing** is watching people other than you try to use your device, and writing down what happens. You already know how it works, so you cannot see what a new person sees. The protocol is short and uses `user-test-sheet.md`.

1. **Choose the tasks.** Write 3 or 4 jobs a user would do, in their words: "Start a 25 minute timer." Do not mention buttons.
2. **Choose testers.** Three to five classmates who did not build it. A small group like this typically finds most of the common problems, which is why designers test early and often. Tell each one what you will record and that they may stop at any time; record notes, never their voice or a picture.
3. **Read the script and stay quiet.** Say "I am testing the device, not you." Ask them to think aloud. Do not help unless they are stuck for a full minute.
4. **Record what you see:** done on their own (yes or no), seconds taken, wrong presses or hesitations, and their exact words. Afterward ask what was hardest, what they expected, whether they could tell what the device does with sound, and an ease score from 1 to 5.
5. **Decide what to change.** Merge duplicate problems across sheets and count how many testers hit each. Fix a problem that stopped someone, then any problem two or more testers hit. Change one thing, then test it again with a new person.

*Worked example (invented, to show the method).* Three testers try the study timer. Two press MODE once to start, then hold it expecting it to stop, and instead skip to the break. Both problems come from one cause: nothing on the screen says a long press skips. The change is a one-line hint, "Hold MODE: skip", in the idle screen. The retest with a fourth tester shows no skips. This is the evidence for a design choice, which is what the course outcome "justify the design choices based on user testing with classmates" asks for.

!!! mascot-encourage "Watching Someone Struggle Is Hard"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    It can sting to watch a classmate fumble with something you built, and that is normal. You have already debugged wiring and timing, which are harder. Each fumble is a free lesson you did not have to guess.

## Putting It All Together

You can now find a fault with a probe instead of a guess, check every wire against a list computed from `config.py`, and run a self-test after every change. You can walk a symptom to a cause, keep the whole device inside a 40 ms frame, and build, test, and defend a project that is yours.

Key takeaways:

- Serial output, the REPL, and `mpremote` share one port, so quit Thonny first. Log with levels, a RAM ring, and a capped flash file, and never log audio or words.
- A probe tests one part and prints evidence before a verdict of PASS, FAIL, ASK, or SKIP. The display and amplifier cannot report back, so they stay ASK until a person answers.
- Verify wiring against a table computed from `config.py`; the pin-plan rules catch swapped I2S pairs, reused pins, and wireless-chip pins.
- Diagnose with the cheapest question first, then confirm with the quick test before changing anything.
- A frame overrun counter times the gap between `readinto()` calls. A one-off stall costs latency; a loop that is slow on average loses audio.
- Integrate with a budget (a 19.0 ms typical pass leaves 21.0 ms), slice big jobs, and rerun the regression checklist after every change.
- A capstone has a purpose, testable requirements, calibrated thresholds, a self-test, a privacy statement, and a user test with classmates.

Test yourself with these questions, and click each one to reveal its answer.

??? question "Your clap detector counts every sharp 'p' as a clap. Is the threshold wrong? Click to expand"
    Probably not. The detector watches loudness over 40 ms frames, so a one-frame spike looks the same as a clap. The test shows this limit: single-frame spikes counted 40 times out of 40. To separate them you need another feature, such as a crest-factor check, and you should test it on both kinds of sound.

??? question "A pass takes 148.4 ms once every 2 seconds. Does the microphone lose audio? Click to expand"
    By the model, no. The pass runs \( 148.4/40 - 1 = 2.71 \) frames behind, about 108 ms, which is less than the ring's depth of about 9.8 frames, and the next light passes catch up. It costs latency. If the same pass happened every frame, the model says audio would be lost.

??? question "Why does the self-test report the display as ASK and not PASS? Click to expand"
    The display controller cannot report back to the Pico, so the program can only draw a pattern. A person has to say what they saw. The program turns ASK into PASS or FAIL only when someone answers with UP or DOWN.

!!! mascot-celebration "A Device You Can Trust and Fix"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned to probe a part, verify wiring from `config.py`, write a self-test, diagnose the three classic failures, budget a 40 ms frame across every subsystem, and build and test a capstone with classmates. You can now fix your own Study Buddy and make it yours.
