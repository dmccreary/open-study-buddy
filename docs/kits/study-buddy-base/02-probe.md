---
title: "Lab 02: The Hardware Probe"
description: "A program that inspects the Pico, its memory, its files, the pin plan, the buttons, the display wiring, and the microphone, then reports what is wired and what is missing."
---

# Lab 02: The Hardware Probe

!!! mascot-welcome "Meet Your Kit's Doctor"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This lab is a program that examines your kit the way a doctor does a checkup, and then tells you exactly which part needs attention. Run it first on a new kit and again any time something stops working. Let's listen closely!

| | |
|---|---|
| **Program** | `02-probe.py` |
| **Parts needed** | The Pico. It checks every other part *as you add it*. |
| **Time** | 10 minutes |
| **Makes sound?** | Never |
| **How to stop** | It ends by itself and prints a summary |

## What You Will Learn

* How a program can check its own hardware
* How `try` and `except` turn a crash into a helpful message
* A clever trick that senses whether a wire is connected, using pull-up and pull-down resistors
* How to read a report, and how to use it to find a wiring mistake

## The Big Idea

Software cannot see wires, but it *can* see the effects of wires. If a pin is connected to a
resistor on the display, the pin reads differently than one connected to nothing. If the
microphone is wired wrongly, it sends nothing but zeros. The probe asks each part a question
that only a wired part can answer.

The probe **never writes to the flash memory or changes a setting**, so it is always safe to
run. A part you have not wired yet shows up as a `WARNING`, not a crash. Run it after adding
each part and you will see that part go from a warning to `ok`.

## The Eight Sections

| # | Section | The question it asks |
|---|---------|----------------------|
| 1 | Board and firmware | Which chip is this, and is it a Pico W or 2 W? |
| 2 | RAM | How much memory is free, and will a 3-second recording fit? |
| 3 | Flash | How much file space is free, and which files are on the board? |
| 4 | Kit files | Are the display driver, fonts, and `config.py` uploaded? |
| 5 | Pin plan | Do the pins follow the I2S rule, and does any pin get used twice? |
| 6 | Buttons | Are all three buttons reading "not pressed"? |
| 7 | Display wiring | Are the SCL, SDA, and BL wires connected? |
| 8 | Microphone | Does the microphone send changing numbers? |

## Walking Through the Code

### Collecting warnings

```python
warnings = []

def warn(message):
    """Record a problem for the summary at the end, and print it now."""
    warnings.append(message)
    print("  WARNING:", message)
```

Instead of stopping at the first problem, the probe keeps a **list** of warnings and prints
the whole list at the end. You learned lists in the course; this is a good use for one. The
probe keeps going so you see *every* problem in one run, not just the first.

### Looking at memory and files

```python
RECORD_BYTES = 3 * 12800 * 4          # 3 s of 32-bit samples at 12800 Hz
try:
    block = bytearray(RECORD_BYTES)
    print("3 s record: fits -- needs", kb(RECORD_BYTES))
    del block
except MemoryError:
    warn("a 3-second recording does not fit in RAM")
```

Lab 07 will record three seconds of sound into one block of memory. The only honest way to
know whether it fits is to **try**. If the Pico cannot find that much room, `bytearray()`
raises `MemoryError`, and the `except` catches it and turns it into a warning.

Notice the number: 3 seconds, times 12,800 samples per second, times 4 bytes per sample is
153,600 bytes. That is 150 KB of the Pico's memory for three seconds of sound.

### Checking the files before importing them

```python
REQUIRED = (
    ("lib/gc9b72.py", "the display driver"),
    ("lib/vga1_8x16.py", "the small font"),
    ...
)
```

The probe checks that these files exist *before* it imports `config.py`. Why? Because
`config.py` itself imports the driver and the fonts. If one were missing, the import would
crash and the probe would never get the chance to tell you which file was missing.

### The pin plan

The probe checks two rules from `config.py`. The first is the I2S rule: the word-select pin
must be exactly **one number higher** than the clock pin (`ws == bclk + 1`). The second is
that no pin number appears twice, because two wires on one pin cannot both work. It also
makes sure nothing uses GP23, GP24, GP25, or GP29, which belong to the WiFi chip.

### Sensing a wire that is not there

This is the cleverest part. The display cannot talk back to the Pico, so how can the probe
tell if its wires are connected? The display module has tiny resistors on three of its pads:
SCL and SDA are pulled **up** (toward 3.3 V), and BL is pulled **down** (toward ground). The
Pico can feel them:

```python
def pin_state(number):
    pin = Pin(number, Pin.IN, Pin.PULL_DOWN)   # the Pico pulls the pin down
    time.sleep_ms(5)
    down = pin.value()
    pin.init(Pin.IN, Pin.PULL_UP)              # now the Pico pulls it up
    time.sleep_ms(5)
    up = pin.value()
    pin.init(Pin.IN)
    if down == up:
        return "high" if up else "low"         # something is holding it
    return "floats"                            # nothing is holding it
```

The probe tries pulling the pin down, then up, and reads it each time:

* If the pin read **the same both times**, something *else* is holding it there. A wire to the
  display is winning against the Pico's weak pull.
* If the reading **followed the Pico's pull**, nothing is attached. The pin is "floating".

You met pull-up and pull-down resistors in the
[Digital Input, Output, and Interrupts](https://dmccreary.github.io/learning-micropython/chapters/06-digital-io-interrupts/)
chapter. This is the same idea, used as a detective tool.

!!! mascot-thinking "A Floating Pin Has No Opinion"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A pin connected to nothing picks up whatever the Pico offers it, like a leaf following the wind. A pin connected to something stays put when you push, and that difference is how the probe sees a wire it cannot touch.

### Listening to the microphone

The probe starts the microphone, throws away the first few reads (the start-up clicks), reads
512 samples, and subtracts the lowest from the highest. A working microphone in a quiet room
sends small, wobbling numbers, so the **spread** is more than zero. A missing or mis-wired
microphone sends a **flat line**: every sample is the same.

## Run It

```bash
mpremote run 02-probe.py
```

Or open it in Thonny and press Run. Read the shell output from the top.

## What PASS Looks Like

At the very end you want to see:

```
Summary
Everything software can check looks good.
```

If a part is not wired yet, you will see a warning for it instead. That is not a failure. It
is the probe doing its job. For example, with only the Pico connected you will see warnings
for the display and the microphone, and each one disappears as you add that part.

## If Something Goes Wrong

| Warning | What it means | What to do |
|---------|---------------|------------|
| `this kit needs a Pico W or Pico 2 W` | Wrong board or firmware | Flash `RPI_PICO2_W` |
| `lib/gc9b72.py is not on the board` | Kit files are missing | Run `./upload-code.sh` |
| `SCL and SDA both float` | Display unplugged or has no power | Check its VCC (3V3) and GND wires |
| `the display's SDA wire to GP3 is missing or loose` | A single loose wire | Push the wire in firmly |
| `the microphone sends a flat line` | Mic wires swapped or loose | Check SCK, WS, SD, VDD, GND, and L/R |
| `microphone failed to start: invalid ws` | WS is not right after SCK | Fix the pin numbers or wires |

!!! mascot-tip "Fixing a Flat-Line Microphone"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    The microphone's SCK, WS, and SD wires are easy to swap, and a swapped microphone starts without any error and sends only zeros. Check them in order: SCK on GP13, WS on GP14, SD on GP15, then VDD on 3V3 and both GND and L/R on GND.

## Try This

1. **Remove a wire.** Pull the display's SDA wire out of the breadboard and run the probe.
   Which line of the report changes? Put it back and run it again.
2. **Break a button.** Hold down the MODE button while the probe runs. What does section 6
   say?
3. **Count your free memory.** How many kilobytes of RAM are free? Change `3 * 12800 * 4` to
   `10 * 12800 * 4` and run it again. Does a 10-second recording fit?
4. **Add your own check.** Add a line that prints the Pico's temperature with
   `machine.ADC(4)`. You will need the formula from the course's
   [internal temperature lab](https://dmccreary.github.io/learning-micropython/basics/02-internal-temperature/).

??? tip "Hint for number 3"
    On a Pico 2 W the heap is a few hundred kilobytes, and a 10-second recording needs 500 KB, so it will not fit. The warning is the proof that Lab 07 is limited to 3 seconds.

## Check Your Understanding

1. Why does the probe check for missing files *before* it imports `config.py`?
2. A pin reads `1` when the Pico pulls it down and `1` when the Pico pulls it up. Is a wire
   connected? What is holding it?
3. Why does a list of warnings work better than stopping at the first problem?

??? question "Answers"
    1. `config.py` imports the driver and fonts, so a missing file would crash the import and
       hide the real problem.
    2. Yes. Something is holding the pin high, such as the display's pull-up resistor on SCL
       or SDA.
    3. You see every problem at once and can fix them all before running again.

## Where Next

The probe could not check the buttons for a missing wire (an unplugged button also reads
"not pressed"). [Lab 03](03-buttons.md) tests that by watching you press them.
