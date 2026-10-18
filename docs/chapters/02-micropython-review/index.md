---
title: "MicroPython Review for Embedded Systems"
description: "A refresher on the MicroPython skills the rest of the book assumes: the REPL, Thonny, mpremote, modules, the machine library, GPIO, timers, interrupts, and the memory limits of a microcontroller."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 10:56:47"
version: 1.11
---

# MicroPython Review for Embedded Systems

## Summary

This chapter is a brief refresher, not a first introduction, of the MicroPython skills the rest of the book assumes. It covers the REPL, Thonny, mpremote, modules, the machine library, GPIO, timers, interrupts, and the memory limits that matter on a microcontroller. After this chapter, students can set up their Pico and write small programs that later chapters extend.

## Concepts Covered

This chapter covers the following 20 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| MicroPython Review | 2292 |
| Thonny IDE | 1 |
| REPL | 14 |
| Modules and Imports | 1083 |
| Memory Limits | 108 |
| Byte Arrays | 247 |
| Exceptions | 11 |
| Flash File System | 17 |
| mpremote | 12 |
| machine Library | 1073 |
| Garbage Collection | 5 |
| memoryview | 2 |
| Config File Pattern | 8 |
| Boot and Main Scripts | 1 |
| mip Package Manager | 11 |
| GPIO Pin | 582 |
| Timer | 13 |
| Heap Fragmentation | 1 |
| Interrupt | 5 |
| Interrupt Service Routine | 2 |

## Prerequisites

This chapter assumes only the prerequisites listed in the [course description](../../course-description.md).

---

## A Quick Tune-Up Before We Build

You already know how to blink an LED, read a button, and draw on a display with MicroPython. This chapter does not teach those things from scratch. It gathers the handful of skills that every later chapter leans on, so that when Chapter 8 asks you to read audio samples into a `bytearray` you do not have to stop and remember what one is.

!!! mascot-welcome "Tune-Up Time"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter your Pico will be set up the way the whole book expects, and you will know how to check its memory before a big recording. Let's listen closely! A small tune-up now saves hours of mystery bugs later.

The review is organized as a **MicroPython review** in the plain sense of the phrase: the set of skills for writing, running, and organizing programs on a Raspberry Pi Pico 2 W. We cover the tools you type into, the way code is split into files, the hardware library, the memory you have to work with, and the two ways a program can react to the outside world.

| Section | Question it answers |
|---------|---------------------|
| Tools: Thonny, the REPL, and mpremote | How do I get code onto the Pico and see what it does? |
| Organizing code | How do I split a program into files and keep pin numbers in one place? |
| Talking to hardware | How do I read a pin and wait for an event? |
| Memory | How much room do I have, and what happens when I run out? |

## Tools for Talking to the Pico

Three tools cover almost everything you will do. Each one solves a different problem, so it helps to know which to reach for.

### Thonny IDE

**Thonny** is a free editor with a Python shell built in. Its Run button sends your file to the Pico and starts it, and its Stop button interrupts it. Choose the interpreter "MicroPython (Raspberry Pi Pico)" in the lower right corner so Thonny talks to the board instead of to Python on your computer.

One detail trips up many builders. Run sends a *copy* of your script for that one run. It does not save the file on the Pico. To keep a file on the board, use File, Save as, and pick the Raspberry Pi Pico.

### The REPL

The **REPL** (read-eval-print loop) is the `>>>` prompt where you type one line of Python and see the result immediately. It reads your line, evaluates it, prints the answer, and loops back for the next line. For hardware, the REPL is the fastest experiment you have, because nothing needs to be saved.

```python
>>> from machine import Pin
>>> led = Pin("LED", Pin.OUT)
>>> led.value(1)
>>> led.value(0)
```

Three keys are worth knowing: Ctrl-C stops a running program, Ctrl-D restarts MicroPython (a soft reboot), and Ctrl-E opens paste mode so you can paste several lines at once.

### mpremote

**mpremote** is a command-line tool that does what Thonny does from a terminal, which makes it easy to script. The most useful commands are shown below. Only one program can hold the Pico's serial port at a time, so quit Thonny before you run them.

```bash
mpremote run 02-probe.py
```

That command runs a file from your computer on the Pico without saving it there. To list, copy, and open the shell, use these:

```bash
mpremote fs ls
mpremote fs cp config.py :config.py
mpremote repl
```

The colon in `:config.py` means "on the Pico." The kit's `upload-code.sh` script uses `mpremote` to copy every file the kit needs.

| Task | Thonny | mpremote |
|------|--------|----------|
| Try one line | Type in the shell | `mpremote repl` |
| Run a file once | Run button | `mpremote run file.py` |
| Save a file on the Pico | Save as, Raspberry Pi Pico | `mpremote fs cp file.py :file.py` |
| Stop a program | Stop button | Ctrl-C |

!!! mascot-tip "One Program Owns the Port"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    If `mpremote` says it cannot open the port, Thonny is probably still connected. Quit Thonny (or press its Stop button and close the shell), then run the command again.

## Organizing Code with Modules

A MicroPython program that does real work is too long for one file. The tool for splitting it up is the module, and it is one of the most important ideas in the book, because every kit lab depends on it.

### Modules and Imports

A **module** is a Python file that other files can use. When you write `import config`, MicroPython looks for a file named `config.py`, runs it once, and gives you its names under the prefix `config`. The `from` form brings individual names in directly.

```python
import config                   # use as config.BAUDRATE
from machine import Pin         # use as Pin
import shapes                   # lib/shapes.py from the kit
```

MicroPython searches a short list of folders, called the import path, in order. The list always includes the folder the program runs from, and it includes a folder named `/lib` on the Pico. That is why the kit puts its drivers (`gc9b72.py`, `shapes.py`, and the fonts) in `lib/`, while `config.py` sits at the top level next to the tests.

Two behaviors cause most import confusion.

- **A module runs once.** The first `import config` executes the file. A second `import config` in another file reuses the result and does not run it again.
- **Editing does not reload.** If you change `config.py` and re-upload it, a program that is already running still holds the old version. Stop it and run again.

*Worked example.* Suppose `shapes.py` is missing from the Pico. Running test 04, which contains `import shapes`, stops with `ImportError: no module named 'shapes'`. The error names the file, so the fix is to upload `lib/shapes.py` (the `upload-code.sh` script does this). Reading the last line of an error first, and looking for a name, solves most import problems in under a minute.

The diagram below shows how the kit's files point at each other. Each box is a file, and each arrow is an `import`.

#### Diagram: Kit Import Map

<details markdown="1">
<summary>Kit Import Map</summary>
Type: graph-model
**sim-id:** kit-import-map<br/>
**Library:** vis-network<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** interpret<br/>
**Learning Objective:** The learner will interpret the kit's import map by naming, for 5 selected files, which other files it imports and which folder each file belongs in on the Pico.

**Prerequisites:** module, import, import path, `/lib` folder (all defined in the section "Modules and Imports" above this block).

**Evidence of Mastery:** For each of the 5 files in the table below, the learner selects the files it imports from the full list of 8 files. A selection is correct when it matches the "Kit files it imports" column exactly. Mastery is 4 of 5 correct. Clicking a file to read its description is exploration, not evidence.

**Misconceptions:** (1) Every file must be at the top level of the Pico. (2) A file imports everything that its imports import. (3) Editing a module on the computer updates the copy on the Pico.

**Instructional Rationale:** An Understand-level objective asks the learner to interpret a structure, so the learner reads arrows rather than reciting a rule. Choosing the imports of a file before the answer is shown makes the learner predict from the diagram.

**Content:**

The graph has 8 files. Each file shows its Pico folder and a one-sentence description when selected.

| File | Pico folder | Description | Kit files it imports |
|---|---|---|---|
| 03-buttons.py | top level | Test 03, reports button presses | config |
| 04-hello-world.py | top level | Test 04, draws "Hello World!" | config, shapes |
| 06-listen-meter.py | top level | Test 06, a microphone level meter | config |
| config.py | top level | Every pin number and helper function for the kit | gc9b72, vga1_8x16, vga1_bold_16x32 |
| shapes.py | lib | Circles, rings, polygons, sprites | none |
| gc9b72.py | lib | The display driver | none |
| vga1_8x16.py | lib | The small 8 by 16 font | none |
| vga1_bold_16x32.py | lib | The large 16 by 32 font | none |

Standard-library modules such as `machine`, `time`, `math`, and `struct` are not drawn, and the learner is not asked about them.

**Provenance:** The files, folders, and imports are taken from the kit at `src/kits/study-buddy-base/` in this repository: the test files named, `config.py`, and the four files in `lib/`.

**Rules:** An arrow runs from the importing file to the imported file. A selection is correct when the set of files the learner selects equals the "Kit files it imports" set for that file. A file that imports no kit files is answered by selecting none. Order does not matter.

**Learner Activity:**

1. The learner reads the graph and clicks any file to see its folder and description.
2. The learner starts the check. For each of 5 files (03-buttons.py, 04-hello-world.py, 06-listen-meter.py, config.py, shapes.py), the learner selects the kit files it imports and submits.
3. The sim reveals the correct arrows for that file.
4. After the fifth file, the sim shows the score.

**Feedback:** 5 files, fixed order, one attempt each. Correct: "Correct: <file> imports <list>." Incorrect: "Not quite. <file> imports <list>; <one-sentence reason>." The correct answer is shown right after each submission. A running score "n of 5" is shown.

**Starting State:** The full graph is shown with no file selected, and the question "Which files does 04-hello-world.py need?"

**Chapter Anchors:** The chapter states that `config.py` is at the top level, that the drivers and fonts are in `lib/`, and that test 04 imports `shapes` and `config`.
</details>

### The Config File Pattern

Every kit lab imports `config.py` rather than repeating pin numbers. That is the **config file pattern**: put every hardware fact in one module, and let every other file ask it. Here is a trimmed piece of the kit's `config.py`.

```python
from machine import Pin

BUTTON_MODE_PIN = 13
BUTTON_INCREMENT_PIN = 14
BUTTON_DECREMENT_PIN = 15


def init_buttons():
    mode = Pin(BUTTON_MODE_PIN, Pin.IN, Pin.PULL_UP)
    increment = Pin(BUTTON_INCREMENT_PIN, Pin.IN, Pin.PULL_UP)
    decrement = Pin(BUTTON_DECREMENT_PIN, Pin.IN, Pin.PULL_UP)
    return mode, increment, decrement
```

The three constants hold the pin numbers, and `init_buttons()` builds the three `Pin` objects and returns them. A lab then needs only one line, `mode, up, down = config.init_buttons()`. If you wire a button to a different pin, you change one number in one file and every lab follows.

!!! mascot-thinking "Change It in One Place"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Think of `config.py` as the kit's address book. Programs look up where each part lives instead of memorizing it, so a rewired part is a one-line change instead of a hunt through ten files.

### Boot and Main Scripts

When the Pico powers up, MicroPython runs two special files in order. `boot.py` runs first and is meant for setup, and `main.py` runs next and holds the program that should start by itself. If neither file exists, the Pico just waits at the REPL. A `main.py` left over from an old project will run at power-up even when you did not ask, which is why the kit's README warns that a Pico from a previous kit may start the wrong program. To stop it, delete `main.py` with `mpremote fs rm main.py`.

### mip: Installing Libraries

The **mip package manager** downloads a library and puts it in `/lib`. It needs the Pico to be on Wi-Fi when you run it from the board, or you can run it from your computer through mpremote, which is easier. Chapter 15 uses it to install the MQTT client.

```bash
mpremote mip install umqtt.simple
```

After that, `import umqtt.simple` works in any program. The kit files for this book are not installed with mip; they are plain files you copy.

## Talking to the Hardware

### The machine Library

The **machine library** is MicroPython's window into the chip. Where ordinary Python knows nothing about pins, `machine` gives you a class for each kind of hardware. The kit uses five of them.

| Class | What it controls | Where this book uses it |
|-------|------------------|-------------------------|
| `Pin` | One GPIO pin | Buttons, display control lines, the LED |
| `SPI` | A fast serial bus with a clock and data lines | The display (Chapter 5) |
| `I2S` | A serial bus built for audio | Microphone and speaker (Chapter 8) |
| `Timer` | A hardware timer that calls your function | Periodic work (below) |
| `PWM`, `ADC`, `I2C` | Pulse output, analog input, a two-wire bus | Not used in the kit |

Beyond the classes, `machine.freq()` returns the CPU speed in hertz, and `machine.reset()` restarts the board. Notice the pattern: you create an object for a piece of hardware, then call its methods. Test 02 begins by printing `machine.freq()` so you can see what clock your board runs at.

*Worked example.* The display's SPI bus is created with one line from the kit's `config.init_display()`.

```python
spi = SPI(0, baudrate=24_000_000, sck=Pin(2), mosi=Pin(3))
```

The first argument, `0`, picks SPI block 0. The `baudrate` is the requested clock speed in bits per second, `sck` is the clock pin, and `mosi` is the pin that carries data from the Pico to the display. Chapter 5 explains each of these. The point for now is that every piece of hardware follows the same recipe: choose a block, hand it the pins, and it returns an object you can use.

### GPIO Pins

A **GPIO pin** (general-purpose input/output) is a metal pin the program can either read as a 0 or a 1, or drive to a 0 or a 1. The Pico's pins are labeled GP0, GP1, and so on, and the number in `Pin(13)` is the GP number, not the physical position on the board.

As an input, a pin reads a voltage and reports `1` for high (near 3.3 V) or `0` for low (near 0 V). As an output, it sets that voltage. A pin set up as an input with a **pull-up** is held at 1 by a built-in resistor until something connects it to ground. That is how the kit reads a button.

```python
button = Pin(13, Pin.IN, Pin.PULL_UP)
print(button.value())   # 1 when not pressed, 0 while pressed
```

The button's other leg goes to ground, so pressing it connects the pin to 0 V and the reading flips from 1 to 0. This surprises many builders: *pressed* reads as 0. The kit's labs write `button.value() == 0` to mean "pressed."

Three rules keep you out of trouble.

- **Use names for special pins.** On a Pico W the onboard LED is not on GP25. Write `Pin("LED")`, which works on every board.
- **Leave the wireless pins alone.** GP23, GP24, GP25, and GP29 belong to the wireless chip on a Pico 2 W. Do not wire anything to them.
- **Never connect a pin to more than 3.3 V.** The Pico's pins are 3.3 V parts.

!!! mascot-warning "Pressed Reads as Zero"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A code bug that looks like a broken button is often a flipped test: writing `if button.value():` runs when the button is *not* pressed. Fix it by writing `if button.value() == 0:` and adding a comment that says "pressed."

The table below collects the pin facts from the kit, so you can see them in one place.

| Part | Pico pins | Pin mode |
|------|-----------|----------|
| Buttons MODE, UP, DOWN | GP13, GP14, GP15 | Input with pull-up |
| Display clock, data, reset, data/command, chip select, backlight | GP2 to GP7 | SPI and outputs |
| Microphone clock, word select, data | GP10, GP11, GP12 | I2S receive |
| Amplifier data, bit clock, left/right clock | GP19, GP20, GP21 | I2S transmit |

### Timers

A **timer** is a hardware counter that calls a function for you after a delay, once or over and over. The program keeps doing other work, and the timer interrupts it at the right moment. The `period` is in milliseconds.

```python
from machine import Pin, Timer

led = Pin("LED", Pin.OUT)

def blink(timer):
    led.toggle()

tick = Timer(period=250, mode=Timer.PERIODIC, callback=blink)
```

This blinks the LED every 250 ms with no loop in your main program, so the main program is free to do something else, like draw on the display. `Timer.ONE_SHOT` runs the function once instead. The callback receives the timer object as its only argument, so the function must accept one parameter even if it ignores it. Stop a timer with `tick.deinit()`.

### Interrupts and Interrupt Service Routines

An **interrupt** is a signal from hardware that makes the processor pause what it is doing, run a short function, and then return to where it left off. The short function is the **interrupt service routine** (ISR). A pin can request an interrupt when its signal falls from 1 to 0, rises from 0 to 1, or both.

```python
from machine import Pin

pressed = False

def on_press(pin):
    global pressed
    pressed = True

button = Pin(13, Pin.IN, Pin.PULL_UP)
button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)

while True:
    if pressed:
        pressed = False
        print("MODE pressed")
```

The function `on_press` is the ISR. It does one tiny thing, setting a flag, and the main loop does the real work when it notices the flag. That split is the rule for every ISR you will write: keep it short, do not print or allocate memory inside it, and leave the real work to the main loop.

Polling, which means asking the pin over and over in a loop, can miss a press that starts and ends between two checks. An interrupt cannot miss it, because the hardware notices the edge on its own. The activity below lets you predict which presses a polling loop would catch.

#### Diagram: Polling Versus Interrupt Timeline

<details markdown="1">
<summary>Polling Versus Interrupt Timeline</summary>
Type: microsim
**sim-id:** polling-versus-interrupt-timeline<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** compare<br/>
**Learning Objective:** The learner will compare a polling loop with an interrupt by predicting, for 6 button presses, whether a loop that checks the pin every P milliseconds sees the press, and observing that an interrupt sees all 6.

**Prerequisites:** polling, interrupt, interrupt service routine, falling edge (all defined in the section "Interrupts and Interrupt Service Routines" above this block).

**Evidence of Mastery:** For each of the 6 cases, the learner commits to "seen" or "missed" for the polling loop before the result is shown. A prediction is correct when it matches the Polling result column in Content. Mastery is 5 of 6 correct. Switching to interrupt mode and watching is exploration, not evidence.

**Misconceptions:** (1) A faster loop always catches every press. (2) A very short press is always missed. (3) An interrupt makes the main loop run faster.

**Instructional Rationale:** An Understand-level comparison needs the learner to infer an outcome from a rule rather than watch it. Predicting before the result forces the learner to apply the rule "a poll sees the press only if a check lands inside it," and the interrupt mode then shows why that rule does not apply to hardware edges.

**Content:**

A timeline runs from 0 ms to 220 ms. Polling checks happen at 0 ms and then every P ms. A press is a time interval [start, end) during which the pin reads 0. The polling loop sees a press when at least one check time t satisfies start <= t < end.

| # | P (ms) | Press start (ms) | Press end (ms) | Press length (ms) | Check times inside the press | Polling result | Why (shown as feedback) |
|---|---|---|---|---|---|---|---|
| 1 | 5 | 12 | 22 | 10 | 15, 20 | seen | Two checks land inside the press. |
| 2 | 20 | 12 | 22 | 10 | 20 | seen | The check at 20 ms lands inside the press, by luck. |
| 3 | 20 | 22 | 32 | 10 | none (checks at 20 and 40) | missed | The press starts just after one check and ends before the next. |
| 4 | 100 | 30 | 80 | 50 | none (checks at 0 and 100) | missed | A 50 ms press fits entirely between two checks 100 ms apart. |
| 5 | 100 | 90 | 210 | 120 | 100, 200 | seen | A press longer than P always contains a check. |
| 6 | 50 | 55 | 95 | 40 | none (checks at 50 and 100) | missed | A press shorter than P can fall between two checks. |

In interrupt mode every case is seen at its press start, because the hardware notices the falling edge.

**Provenance:** The numbers are illustrative and the sim labels them "illustrative." The rule that a polling loop misses a press that fits between two checks comes from the chapter section "Interrupts and Interrupt Service Routines."

**Rules:** Checks occur at 0, P, 2P, and so on up to 220 ms. A press is seen by polling when start <= kP < end for some integer k >= 0. In interrupt mode a press is seen at its start time for every case. A press longer than P is always seen by polling.

**Learner Activity:**

1. The learner reads case 1 (P and the press interval) and chooses "seen" or "missed."
2. The sim draws the check times and the press, then shows the result and the Why text.
3. The learner continues through case 6, then sees the score.
4. The learner switches the display to interrupt mode and steps through the six cases again, noticing that every press is marked at its start time.

**Feedback:** 6 cases, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The polling loop <seen or missed> this press: <Why>". The result is revealed after each answer, and a running score "n of 6" is shown.

**Starting State:** Case 1 is shown with the checks marked on the timeline and the question "Will the polling loop see this press?"

**Chapter Anchors:** The chapter states that polling can miss a press that starts and ends between two checks, that an interrupt cannot miss it, and that an ISR should only set a flag.
</details>

!!! mascot-tip "ISR Diet Rules"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Treat your ISR like a note on a sticky pad: set a flag, store one number, and get out. If you catch yourself writing a loop, a `print`, or a list inside an ISR, move that code to the main loop.

## Memory: The Resource That Runs Out

### Memory Limits

A computer you use every day has gigabytes of memory. A Pico 2 W has about 520 KB of RAM in the whole chip, and MicroPython's own working area, the **heap**, is only part of that. A **memory limit** is the hard ceiling you hit when a program asks for more than is left. On a microcontroller you hit it quickly, so you plan for it.

Plan with arithmetic. The kit's microphone produces 12,800 samples per second, and each sample is a 4-byte number. Test 07 records up to 3 seconds before playing back.

\[ \text{bytes} = 12{,}800 \;\tfrac{\text{samples}}{\text{s}} \times 4 \;\tfrac{\text{bytes}}{\text{sample}} \times 3 \text{ s} = 153{,}600 \text{ bytes} \approx 150 \text{ KB} \]

That one buffer is roughly 29 percent of the chip's 520 KB of RAM, and a single unbroken block that big is hard to find once a program has been running a while. Asking for 5 seconds instead (256,000 bytes) is much riskier. Test 07's "Try This" invites you to try it, and test 02 reports how much heap is free so you can predict the result before you run it.

| Resource | Size on a Pico 2 W | What uses it in this book |
|----------|--------------------|---------------------------|
| RAM (whole chip) | about 520 KB | Everything running |
| Heap (MicroPython's share) | printed by test 02 | Your lists, strings, and buffers |
| Flash | about 4 MB | Your program files, fonts, and recordings you save |
| One 3-second recording | 150 KB | Test 07 |

Check free heap at any time with two functions from the `gc` module.

```python
import gc
gc.collect()
print(gc.mem_free(), gc.mem_alloc())
```

`gc.mem_free()` is the number of heap bytes still available, and `gc.mem_alloc()` is the number in use. Printing them before and after a big allocation is the fastest way to learn what your code costs.

### Garbage Collection

Python frees memory for you. When nothing refers to an object any more, it is **garbage**, and the **garbage collector** finds it and returns its memory to the heap. MicroPython runs the collector automatically when it runs short, and you can call `gc.collect()` yourself to run it now.

Running the collector takes time, and the pause can be noticeable in code that must keep up with audio. So real-time programs collect on purpose at a calm moment, for example before they allocate a big buffer, as test 07 does with `gc.collect()` just before creating its 150 KB buffer.

### Heap Fragmentation

Freeing memory is not the same as having it in one piece. **Heap fragmentation** happens when free memory is split into many small gaps between objects that are still in use. The total free bytes may be large, but no single gap is big enough for a large request, and MicroPython raises `MemoryError`.

MicroPython's collector frees garbage but does not move the objects that remain, so it cannot squeeze the gaps together. The practical fix is to allocate your biggest buffers first, right after startup, before the heap has been cut into pieces.

The activity below makes this concrete with a tiny heap of 16 cells.

#### Diagram: Heap Fragmentation Explorer

<details markdown="1">
<summary>Heap Fragmentation Explorer</summary>
Type: microsim
**sim-id:** heap-fragmentation-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** explain<br/>
**Learning Objective:** The learner will explain why a memory request can fail when enough total memory is free, by predicting the outcome of 6 allocation requests on a fragmented 16-cell heap and choosing the reason.

**Prerequisites:** heap, garbage collection, heap fragmentation, MemoryError (all defined in the section "Memory: The Resource That Runs Out" above this block).

**Evidence of Mastery:** For each of the 6 requests, the learner predicts "succeeds" or "MemoryError." For a request predicted to fail, the learner also picks the reason from two choices: "not enough free cells in total" or "no single gap is big enough." A request is correct when the prediction matches the Result column and, for failures, the reason matches the Correct reason column. Mastery is 5 of 6 correct on the first attempt. Pressing the collect and restart controls to watch the heap change is exploration, not evidence.

**Misconceptions:** (1) If the total free memory is large enough, the request succeeds. (2) Garbage collection pushes the remaining objects together. (3) Restarting is the only way to get a big buffer.

**Instructional Rationale:** An Understand-level explanation needs the learner to connect a failure to its cause. Predicting the outcome and then naming the reason separates "not enough memory" from "no single gap big enough," which is the misconception that makes fragmentation confusing.

**Content:**

The heap is a row of 16 cells numbered 1 to 16. Each cell is either free or used. A request for n cells succeeds when some run of n or more consecutive free cells exists, and takes the first such run starting from cell 1.

State X (the starting heap): cells 1, 3, 5, 7, 9, 11, 13, 15 hold the objects A, B, C, D, E, F, G, H (one cell each). Cells 2, 4, 6, 8, 10, 12, 14, 16 are free. That is 8 free cells in total, and the longest run of free cells is 1.

State Y (after "Collect garbage" from state X): the objects B, D, F, and H are garbage and are freed. Objects A, C, E, and G stay where they are. Free cells are 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16. That is 12 free cells, and the longest run is 3.

| # | Heap state | Request (cells) | Result | Correct reason | Why (shown as feedback) |
|---|---|---|---|---|---|
| 1 | X | 1 | succeeds | none asked | Any free cell is a gap of at least 1. |
| 2 | X | 2 | MemoryError | no single gap is big enough | 8 cells are free in total, but every gap is 1 cell wide. |
| 3 | X | 8 | MemoryError | no single gap is big enough | 8 cells are free in total, which equals the request, but they are not together. |
| 4 | Y | 3 | succeeds | none asked | Cells 2 to 4 form a run of 3. |
| 5 | Y | 4 | MemoryError | no single gap is big enough | 12 cells are free, but the longest run is 3. |
| 6 | Y | 13 | MemoryError | not enough free cells in total | Only 12 cells are free in total. |

After the six requests, the learner can restart the heap (all 16 cells free) and allocate in the order "one 8-cell buffer, then the eight 1-cell objects A to H." Everything fits. In the opposite order (A to H spaced one cell apart first), the 8-cell buffer fails.

**Provenance:** The heap size and objects are illustrative, and the sim labels them "illustrative." The statement that MicroPython's collector frees objects but does not move them comes from the chapter section "Heap Fragmentation."

**Rules:** A request for n cells succeeds when the heap has a run of at least n consecutive free cells, and it takes the lowest-numbered such run. "Collect garbage" frees only the cells of objects marked as garbage and never moves any other object. "Restart" frees all 16 cells.

**Learner Activity:**

1. The learner sees state X and reads request 1, then predicts the outcome and, if the prediction is a failure, picks a reason.
2. The sim attempts the allocation on the heap picture and shows the result and the Why text.
3. After request 3, the learner presses "Collect garbage" to reach state Y and continues with requests 4 to 6.
4. After request 6, the learner presses "Restart," then allocates the 8-cell buffer first and the eight objects second, and tries the opposite order.
5. The learner should notice that collecting garbage increased the free total from 8 to 12 but only grew the longest gap from 1 to 3.

**Feedback:** 6 requests, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. <Why>". The result is revealed right after each answer, and a running score "n of 6" is shown.

**Starting State:** State X is shown with request 1 and the question "Will this request succeed?"

**Chapter Anchors:** The chapter states that the collector frees garbage but does not move remaining objects, and that the practical fix is to allocate the biggest buffers first.
</details>

!!! mascot-encourage "Memory Bugs Feel Strange"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    If fragmentation feels slippery, that is normal, because the failure depends on what ran earlier. Rely on what you already do well: measure with `gc.mem_free()`, and allocate the big buffer first thing in your program.

### Byte Arrays

Audio, display data, and network messages are all just sequences of bytes. MicroPython holds them in two types. A `bytes` object is **immutable**, so it cannot change after it is made. A **bytearray** is **mutable**: you can overwrite its contents in place, which is what you need for a buffer that a driver fills over and over.

```python
raw = bytearray(8)       # eight bytes, all zero
raw[0] = 0x34
raw[1] = 0x12
```

Creating a buffer once and reusing it is far kinder to the heap than creating a new one in every loop. The kit does this everywhere, for example `buf = bytearray(FRAME_BYTES)` in test 06, which the microphone fills with `mic.readinto(buf)` again and again. The word `readinto` is the clue: the driver writes into memory you already own, so nothing new is allocated.

Bytes become numbers with the `struct` module. A *format string* says how to read the bytes. The characters that matter here are in the table, where the `<` at the start means the lowest byte comes first (little-endian, which is what the Pico uses).

| Format | Size | Meaning | Where the kit uses it |
|--------|------|---------|-----------------------|
| `b` | 1 byte | signed 8-bit number | not used |
| `h` | 2 bytes | signed 16-bit number | speaker samples |
| `i` | 4 bytes | signed 32-bit number | microphone samples |

*Worked example.* The two bytes `0x34` and `0x12` in the buffer above are one 16-bit number. Reading them gives the high byte first because of little-endian order.

```python
import struct
(value,) = struct.unpack("<h", raw[:2])
print(value)             # 4660, which is 0x1234
```

Test 06 does the same thing on a bigger scale: `struct.unpack("<512i", buf)` turns 2,048 bytes into 512 microphone samples. When the numbers are all the same type, the `array` module (`array("h", ...)`) gives you a typed list that also acts like a buffer, and Chapter 10 uses it for speed.

!!! mascot-warning "Slicing Copies"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Writing `raw[:2]` makes a new two-byte object. In a loop that runs every 20 ms, those copies pile up and trigger garbage collection pauses. Use a memoryview, described next, to point at part of a buffer without copying it.

### memoryview

A **memoryview** is a window onto an existing buffer. Slicing a memoryview gives another window, not a copy, so you can hand a driver "the part of the buffer starting here" for free. Test 07 relies on it to fill a 150 KB buffer in 1,024-byte pieces.

```python
raw = bytearray(MAX_SECONDS * RATE * 4)
view = memoryview(raw)
got = mic.readinto(view[position:position + CHUNK])
```

The `view[position:position + CHUNK]` slice names the next 1,024 bytes of `raw`, and `readinto` fills exactly that part. Because nothing is copied, the loop allocates no memory.

### Exceptions

An **exception** is Python's way of reporting that something went wrong. When code raises one, normal execution stops and Python looks for a matching `except` block. If none is found, the program ends and prints a traceback. Hardware code meets exceptions often: a wrong pin raises `ValueError`, a missing file raises `OSError`, and an oversized buffer raises `MemoryError`.

The most important pattern for this book is `try` with `finally`. A `finally` block runs whether or not an exception happened, which makes it the right place to release hardware.

```python
mic = config.init_microphone()
try:
    while True:
        mic.readinto(buf)
        # ... use the samples ...
finally:
    mic.deinit()
```

The microphone is created before the `try`, so `finally` can always call `deinit()` on it. If you press Stop in Thonny, the interrupt arrives as `KeyboardInterrupt`, the `finally` block runs, and the I2S hardware and its buffer are released cleanly instead of being left running half-finished.

### The Flash File System

Your files live in the Pico's flash memory, organized as a small **flash file system** (littlefs). It behaves like a normal drive: you can open, read, write, list, and delete files with the `open()` function and the `os` module.

```python
import os
print(os.listdir())
stats = os.statvfs("/")
print(stats[0] * stats[3], "bytes free")
```

`os.listdir()` shows the files, and `os.statvfs("/")` describes the drive. Multiplying the block size (item 0) by the number of free blocks (item 3) gives the free bytes. Test 02 prints the same information for the kit.

Flash has one habit that RAM does not: each spot can be rewritten only a limited number of times, and writes are slow. So do not save to a file inside a fast loop. Write a setting when it changes, not every frame, and prefer RAM for anything temporary.

## Putting the Tools Together

Here is the whole workflow you will repeat in every chapter, using only what this chapter covered.

1. Wire a part and add its pins to `config.py` (config file pattern).
2. Upload with `upload-code.sh` (mpremote).
3. Run the matching test file and read its output (REPL and shell).
4. If something fails, read the last line of the error, check the imports and pins, and use `gc.mem_free()` if it says `MemoryError`.
5. When the code works, keep it in a module and import it from the next lab.

Key takeaways:

- Thonny, the REPL, and mpremote all reach the same Pico; use the REPL to experiment and a file to keep what works.
- A module runs once on import, and `config.py` holds every pin so wiring changes happen in one place.
- A pull-up input reads 1 when idle and 0 when pressed.
- A timer calls your function on a schedule, and an interrupt calls an ISR the moment hardware signals; both interrupt the main loop, so keep the callbacks short.
- Memory is scarce: compute buffer sizes, reuse `bytearray` buffers, slice with `memoryview`, and allocate the biggest buffer first.
- Use `try` and `finally` to release hardware when a program stops.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "A button wired with a pull-up reads 1. Is it pressed or released? Click to expand"
    Released. A pull-up holds the pin at 1 until the button connects it to ground, so a pressed button reads 0.

??? question "Free heap shows 100 KB, but a request for a 60 KB buffer raises MemoryError. What likely happened? Click to expand"
    The heap is fragmented. The 100 KB is split into smaller gaps, and no single gap is 60 KB. Allocate large buffers first, right after startup.

!!! mascot-celebration "Ready to Build"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just refreshed modules, the config pattern, pull-up pins, timers, interrupts, and the memory arithmetic that decides whether a recording fits. Your toolbox is ready for the hardware.

In Chapter 3 we leave the code for a moment and turn sound into numbers.
