---
title: "Lab 10: Flicker-Free Text"
description: "Compare three ways to redraw a counter on the display: erase then draw, overwrite, and send only what changed. See which flicker and measure how long each takes."
---

# Lab 10: Flicker-Free Text

!!! mascot-welcome "Why Do Screens Flicker?"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    You are about to run three counters side by side, each redrawn a different way, and only one of them will look perfect. The reason is a secret about how your display really works. Let's listen closely!

| | |
|---|---|
| **Program** | `10-flicker-free-text.py` |
| **Parts needed** | The display |
| **Time** | 20 minutes |
| **Makes sound?** | No |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* Why **drawing is sending**: every pixel is real data traveling down a wire
* Why **erasing first** causes flicker
* How to **overwrite** and how to **send only what changed**
* How to measure how long code takes with `time.ticks_us()`

## The Big Idea

This display has **no memory you can draw into first**. On a computer or a phone, programs draw
into a hidden picture and then show it all at once. Here, every pixel you draw is **two bytes
sent down the SPI wire, right then**, and the glass shows it the moment it lands.

That has two consequences:

1. **Anything you send is visible.** If you paint a box black and *then* draw a number, the
   eye sees the empty black box for a moment. That is **flicker**.
2. **Everything you send takes time.** Fewer pixels means a faster update.

Here are the three methods:

| Method | What it does | Flickers? | Bytes per update (4 digits) |
|--------|--------------|-----------|-----------------------------|
| **A. Erase, then draw** | Fills the box black, then draws the new number | **Yes** | 4,096 + 4,096 = 8,192 |
| **B. Overwrite** | Draws the new number right on top of the old one | No | 4,096 |
| **C. Only what changed** | Draws only the digits that are different | No | 1,024 per changed digit |

Each big digit is 16 x 32 pixels, and each pixel is 2 bytes: 16 x 32 x 2 = **1,024 bytes**. Four
digits are 4,096 bytes.

!!! mascot-thinking "The Font Draws Its Own Background"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Notice the call `display.text(BIG, text, x, y, color, config.BLACK)`: it takes a background color. The font paints every pixel of each letter's box, the black ones as well as the colored ones, so a new letter completely covers the old one and no erasing is needed.

## Walking Through the Code

### Three drawing functions

```python
def draw_a(text, y, color):
    display.fill_rect(X, y, BOX_W, BIG.HEIGHT, config.BLACK)   # erase...
    display.text(BIG, text, X, y, color, config.BLACK)         # ...then draw

def draw_b(text, y, color):
    display.text(BIG, text, X, y, color, config.BLACK)         # just draw

def draw_c(text, y, color):
    global shown_c
    for i in range(DIGITS):
        if shown_c is None or text[i] != shown_c[i]:           # only if different
            display.text(BIG, text[i], X + i * BIG.WIDTH, y, color,
                         config.BLACK)
    shown_c = text
```

Compare them side by side:

* **A** sends the black box (4,096 bytes), then sends the number on top (4,096 more).
* **B** only sends the number.
* **C** remembers what is on the screen (`shown_c`) and compares each digit of the new text to
  the old. Going from `0041` to `0042`, only the last digit is different, so only one digit
  (1,024 bytes) is sent.

The `global shown_c` line is needed because the function **changes** a variable defined
outside it.

### A table of drawers

```python
DRAWERS = (draw_a, draw_b, draw_c)
```

Functions in Python are values, so a tuple can hold them. The main loop then calls
`DRAWERS[i](text, y, color)` and treats all three the same way. You will see this "list of
functions" idea again in [Lab 13](13-modes-state-machine.md).

### Timing each method

```python
start = time.ticks_us()
DRAWERS[i](text, y, color)
totals[i] += time.ticks_diff(time.ticks_us(), start)
```

`time.ticks_us()` is a counter in **microseconds** (millionths of a second).
`time.ticks_diff()` subtracts safely, even when the counter wraps around. Every 100 updates,
the program divides each total by 100 to get an average, and shows it on the screen in
milliseconds.

## Run It

Open `10-flicker-free-text.py` and press Run. Look at the three numbers. All three counters count the same, but they do not look the same.

## What PASS Looks Like

* The **A** counter (red) visibly **flickers**.
* The **B** counter (yellow) and the **C** counter (green) do **not**.
* Under each counter, a time in milliseconds per update. **C takes the least time**, often
  several times less than A.

The shell also prints a line every 100 updates:

```
ms per update  A <largest>  B <middle>  C <smallest>
```

Your exact numbers depend on your Pico, but their order should be A, then B, then C, from slowest to fastest.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| All three look the same | Your camera or eyes cannot see it | Look from the side; try recording with a phone in slow motion |
| C is not the fastest | The digits all change every time | That happens when counting by large steps; see Try This 1 |
| Garbled numbers in C | `shown_c` was not updated | Make sure `shown_c = text` runs at the end |

## Try This

1. **Count by 7.** Change `count += 1` to `count += 7`. C now changes more digits each time.
   How much slower does it get?
2. **Eight digits.** Set `DIGITS = 8` and use `"%08d"`. Which method suffers most? Why does A
   grow the fastest?
3. **Do the math.** One big digit is 16 x 32 pixels x 2 bytes. At 24 MHz (3 million bytes a
   second), how long should one digit take? Is the measured time close? Where does the rest go?
4. **Make a dirty-region plan.** Open the
   [Dirty Region Planner](../../sims/dirty-region-planner/index.md) and figure out how many
   pixels you would save on a clock face that changes only its seconds.

??? tip "Hint for number 3"
    1,024 bytes / 3,000,000 bytes per second is about 0.34 milliseconds per digit. A real
    update takes longer because the Pico also has to run Python code to prepare each pixel's
    bytes and to send the commands that tell the display where to draw. The wire is not the
    only cost.

## Check Your Understanding

1. Why does method A flicker?
2. Why does method B not need to erase first?
3. How many bytes does one 16 x 32 pixel digit take, at 2 bytes per pixel?
4. If you counted by 1000 (`0000`, `1000`, `2000`, ...), which digits change each time? Is C
   still the fastest?

??? question "Answers"
    1. It paints the box black first, so there is a moment where the number is missing and
       the eye sees an empty box.
    2. The font draws each letter's background color too, so a new digit covers the old one
       completely.
    3. 16 x 32 x 2 = 1,024 bytes.
    4. Only the first digit changes each time, so C sends one digit instead of four. It is
       the fastest, by an even bigger margin.

## Where Next

Now you know the single most important rule for fast, smooth screens: **send only what changed.**
Labs 11 to 13 turn to the buttons. [Lab 11](11-button-bounce.md) lets you see what a button press
looks like to the Pico.

*Related in this book:* [Chapter 6: Drawing Directly to Display Regions](../../chapters/06-display-regions-and-drawing/index.md)
