---
title: "Lab 03: Buttons on the Console"
description: "Watch the three push buttons report every press and release in the Thonny shell, using pull-up resistors, a list for each button, and a debounce timer."
---

# Lab 03: Buttons on the Console

!!! mascot-welcome "Three Buttons, Many Possibilities"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    MODE, UP, and DOWN are the only controls your Study Buddy has, and a clever program can do a lot with three buttons. In this lab you will make sure all three talk to the Pico. Let's listen closely!

| | |
|---|---|
| **Program** | `03-buttons.py` |
| **Parts needed** | The three buttons (MODE on GP16, UP on GP17, DOWN on GP18) |
| **Time** | 10 minutes |
| **Makes sound?** | No |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* Why a pressed button reads **0** and an unpressed one reads **1**
* How one loop can watch three buttons using lists and a `for` loop
* What **debouncing** is, in a first, simple form (Lab 11 explores it deeply)

## Wiring

Each button has two legs. One leg goes to a Pico pin, and the other goes to **GND**:

| Button | Pico pin | Other leg |
|--------|----------|-----------|
| MODE | GP16 | GND |
| UP | GP17 | GND |
| DOWN | GP18 | GND |

There is no resistor to add. The Pico has a built-in **pull-up resistor** on each pin that you
turn on in software, as you learned in the
[Digital Input, Output, and Interrupts](https://dmccreary.github.io/learning-micropython/chapters/06-digital-io-interrupts/)
chapter.

## The Big Idea

With a pull-up, the pin is gently pulled toward 3.3 V, so it reads **1** when nothing touches
it. Pressing the button connects the pin to GND, and the pin reads **0**. That means the
numbers look backwards: **pressed is 0, not pressed is 1.**

| Button state | Pin reads | Program tests |
|--------------|-----------|---------------|
| Not pressed | 1 (high) | `value() == 1` |
| Pressed | 0 (low) | `value() == 0` |

!!! mascot-warning "Pressed Means Zero"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    It feels backwards that a press gives `0`, and forgetting this flips every button in your program. Write `is_down = buttons[i].value() == 0` once, then use the name `is_down` everywhere, so you only have to get it right one time.

## Walking Through the Code

### Setting up

```python
led = config.init_led()
buttons = config.init_buttons()
labels = ("MODE", "UP", "DOWN")
pins = (config.BUTTON_MODE_PIN, config.BUTTON_INCREMENT_PIN,
        config.BUTTON_DECREMENT_PIN)
```

`config.init_buttons()` creates all three `Pin` objects with the pull-up turned on and hands
them back as three values. The labels and the pin numbers go in **tuples** (lists that never
change), in the same order, so `labels[1]` is "UP" and `pins[1]` is 17.

### One list entry per button

```python
pressed = [False, False, False]        # what we last reported
last_change = [0, 0, 0]                # when it last changed, in ms
counts = [0, 0, 0]                     # presses seen
```

The program needs to remember three things *about each button*, so it makes three lists with
three slots each. Slot 0 belongs to MODE, slot 1 to UP, and slot 2 to DOWN. Every time the
loop looks at button `i`, it reads and writes slot `i` of each list.

### The main loop

```python
while True:
    now = time.ticks_ms()
    for i in range(3):
        is_down = buttons[i].value() == 0
        if is_down != pressed[i] and \
                time.ticks_diff(now, last_change[i]) > DEBOUNCE_MS:
            pressed[i] = is_down
            last_change[i] = now
            if is_down:
                counts[i] += 1
                print("{:<5} GP{} pressed   (press #{})".format(
                    labels[i], pins[i], counts[i]))
            else:
                print("{:<5} GP{} released".format(labels[i], pins[i]))
```

Read the `if` as a sentence: "*If the button is in a different state than the one I last
reported, **and** it has been more than 30 milliseconds since it last changed, then report it.*"

* `is_down != pressed[i]` finds a **change**. It does nothing while you hold the button, and
  that is why you get one message per press and not thousands.
* `time.ticks_diff(now, last_change[i]) > DEBOUNCE_MS` is the debounce. Metal contacts rattle
  for a few milliseconds when they touch, and the pin flickers between 0 and 1. By ignoring
  changes that come within 30 ms of the last one, the rattle counts as a single press. You
  will see the rattle with your own eyes in [Lab 11](11-button-bounce.md).

### The LED and the PASS message

```python
led.value(1 if any(pressed) else 0)

if not reported_pass and all(counts):
    reported_pass = True
    print("PASS: all three buttons work.")
```

`any(pressed)` is `True` if at least one button is down, so the onboard LED lights while you
hold a button. `all(counts)` is `True` only when every count is above zero, which means each
button has been pressed at least once. Then the program prints `PASS` one time.

## Run It

Open `03-buttons.py` in Thonny, press Run, then press and release each button.

## What PASS Looks Like

The shell shows a line for every press and every release, and then the PASS message:

```
Press each button. Waiting...
MODE  GP16 pressed   (press #1)
MODE  GP16 released
UP    GP17 pressed   (press #1)
UP    GP17 released
DOWN  GP18 pressed   (press #1)
DOWN  GP18 released

PASS: all three buttons work.
(Keep pressing, or press Stop to end the test.)
```

The onboard LED is lit for as long as a button is held down.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| One button never reports | Loose wire, or wired to the wrong pin | Reseat the wire; check the pin numbers above |
| A button reports pressed all the time | Its pin is shorted to GND | Check that the leg is not touching GND |
| One push gives many "pressed" lines | Contact bounce | Raise `DEBOUNCE_MS` to 50 |
| Nothing prints at all | The labs were not uploaded, or `config.py` is missing | Run `./upload-code.sh` and try again |

Remember that the probe in [Lab 02](02-probe.md) could not tell if a button's wire was missing,
because an unplugged button also reads 1. This lab can, because it needs *you* to press it.

## Try This

1. **Bounce hunter.** Change `DEBOUNCE_MS` to `0` and press each button as hard and fast as you
   can. Do you ever see two "pressed" lines for one push?
2. **Hold time.** Print how long each button was held, in milliseconds, when it is released.
   You will need to remember `time.ticks_ms()` at the press.
3. **Secret code.** Print `"UNLOCKED"` when the buttons are pressed in the order MODE, UP,
   UP, DOWN.
4. **Reverse the logic.** Change `== 0` to `== 1` and run it. What happens, and why?

??? tip "Hint for number 3"
    Keep a list called `sequence`. Each time a button is pressed, append its label. If the
    list is longer than four items, delete the first one with `sequence.pop(0)`. Then compare
    it to `["MODE", "UP", "UP", "DOWN"]`.

## Check Your Understanding

1. Why does a pressed button read `0`?
2. What does `all(counts)` mean when `counts` is `[3, 0, 1]`?
3. Why does the program remember `pressed[i]` instead of just printing whenever a button is
   down?

??? question "Answers"
    1. Pressing connects the pin to GND (0 volts), which wins against the weak pull-up to
       3.3 V.
    2. It is `False`. The second slot is zero, so UP has never been pressed, and `all()`
       needs every item to be non-zero.
    3. Without the memory, a held button would print a line thousands of times a second. The
       memory lets the program report only the *change*.

## Where Next

Buttons work. [Lab 04](04-hello-world.md) brings in the round display.

*Review in the course:* [Reading a Button Press and Button Debouncing](https://dmccreary.github.io/learning-micropython/chapters/06-digital-io-interrupts/)
