---
title: "Lab 01: Blink the Onboard LED"
description: "The first test of the Study Buddy base kit: blink the Pico 2 W's onboard LED to prove the board, the USB cable, and the MicroPython firmware all work."
---

# Lab 01: Blink the Onboard LED

!!! mascot-welcome "Every Gadget Starts with a Blink"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Before you wire a screen, a microphone, or a speaker, you will make one tiny light blink. If it blinks, you have a working brain for your Study Buddy and every later lab will start from solid ground. Let's listen closely!

| | |
|---|---|
| **Program** | `01-blink-onboard-led.py` |
| **Parts needed** | Just the Pico 2 W and a USB cable |
| **Time** | 5 minutes |
| **Makes sound?** | No |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* How to run a program on the Pico from Thonny
* Why `Pin("LED")` works on the Pico 2 W
* How to make a program do one thing forever with `while True`

## Why Start Here?

When something goes wrong later, you will want to know whether the *problem is your wiring* or
*the board itself*. This program imports nothing from the kit, so it cannot fail because of a
loose wire. If it fails, the problem is the board, the USB cable, or the MicroPython firmware.
Nothing else.

!!! mascot-thinking "Test One Thing at a Time"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Engineers call this **isolating** a problem. A program that uses only the Pico can only be broken by the Pico, so a blinking LED tells you exactly where *not* to look when later labs misbehave.

## The Program

This is the whole program. You have seen blink programs before in the
[Digital Input, Output, and Interrupts](https://dmccreary.github.io/learning-micropython/chapters/06-digital-io-interrupts/)
chapter of the course, so this one should feel familiar.

```python
NAME = "01-blink-onboard-led.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import sleep

led = Pin("LED", Pin.OUT)

while True:
    led.toggle()
    sleep(0.25)
```

## Walking Through the Code

**Lines 1 to 3: a name tag.** Every lab starts by printing its own file name and version
number. When you have several labs on the Pico, this tells you which one is actually running.

**`from machine import Pin`** brings in the `Pin` class, which controls the Pico's pins. You
used it in the course to turn LEDs on and off.

**`led = Pin("LED", Pin.OUT)`** is the interesting line. On a plain Raspberry Pi Pico, the
onboard LED is wired to pin 25, so you would write `Pin(25, Pin.OUT)`. On the Pico **W** and
**2 W**, the LED moved: it hangs off the WiFi chip instead. MicroPython hides this detail
behind the *name* `"LED"`, so `Pin("LED")` works on every Pico board, and `Pin(25)` does not.

!!! mascot-warning "The LED Stays Dark? Check Your Firmware"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    The `"LED"` name only works with the **wireless** MicroPython firmware, `RPI_PICO2_W`. If you flashed the plain `RPI_PICO2` file, the LED stays dark or you get an error, so download the W version and flash it again.

**`while True:`** repeats the indented lines forever. The loop only ends when you press Stop.

**`led.toggle()`** flips the LED: on becomes off, off becomes on. It is shorter than writing
`led.value(1 - led.value())`.

**`sleep(0.25)`** pauses for a quarter of a second. One toggle every quarter second means the
LED is on for 0.25 s, off for 0.25 s, so it makes **two complete blinks every second**.

## Run It

1. Plug the Pico into your computer with a USB cable that carries data (some cables only
   charge).
2. Open `01-blink-onboard-led.py` in Thonny.
3. Check that the bottom-right corner of Thonny says **MicroPython (Raspberry Pi Pico)**.
4. Press the green **Run** button.

Or from a terminal:

```bash
mpremote run 01-blink-onboard-led.py
```

## What PASS Looks Like

The small green LED next to the USB connector blinks twice a second, and the shell prints
`01-blink-onboard-led.py v1.0`. Press **Stop** to end the test.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| Thonny says it cannot connect | USB cable is power-only, or the port is busy | Try another cable; close any other program that is using the Pico |
| An error mentioning `LED` | Plain Pico firmware instead of the W firmware | Flash `RPI_PICO2_W` |
| The program runs but the LED is dark | Wrong firmware, or a damaged board | Reflash; try another Pico |

## Try This

1. **Slow it down.** Change `0.25` to `1`. How many blinks per minute do you get now?
2. **Fast and furious.** Change it to `0.05`. At what point does the blinking look like a
   steady light?
3. **Heartbeat.** Replace the loop body with `led.on()`, `sleep(0.1)`, `led.off()`,
   `sleep(0.1)`, `led.on()`, `sleep(0.1)`, `led.off()`, `sleep(0.7)`. Does it look like a
   heartbeat?
4. **Morse code.** Make the LED blink S-O-S: three short blinks, three long blinks, three
   short blinks.

??? tip "Hint for number 4"
    Write a function `blink(seconds)` that turns the LED on, sleeps, turns it off, and sleeps
    a short gap. Then S is `blink(0.2)` three times and O is `blink(0.6)` three times. You
    learned functions in the
    [Collections, Control Flow, and Functions](https://dmccreary.github.io/learning-micropython/chapters/02-control-flow-functions/)
    chapter.

## Check Your Understanding

1. Why does this lab use `Pin("LED")` instead of `Pin(25)`?
2. What would happen if you left out the `while True:` loop?
3. Why is it a good idea to run a program that imports nothing before the rest of the kit
   is wired?

??? question "Answers"
    1. On the Pico W and Pico 2 W, the LED is connected to the WiFi chip, not to pin 25.
       The name `"LED"` works on all Pico boards.
    2. The LED would toggle once and the program would end, so you would see one quick change
       and then nothing.
    3. If it fails, you know the problem is the board, cable, or firmware, because there is
       no wiring to blame.

## Where Next

You can now run a program on the Pico. Next, [Lab 02](02-probe.md) writes a program that
inspects the whole board and tells you what is wired and what is missing.

*Review in the course:* [Your First LED Blink](https://dmccreary.github.io/learning-micropython/basics/01-blink/)
