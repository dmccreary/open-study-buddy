---
title: "Lab 09: Angles to Pixels on a Round Screen"
description: "Use sine and cosine to turn an angle and a radius into x and y pixel positions, drawing a clock face with 60 tick marks and a sweeping second hand."
---

# Lab 09: Angles to Pixels on a Round Screen

!!! mascot-welcome "A Clock Face from Two Lines of Math"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    A round screen begs to be a clock, and a clock is easiest to draw when you think in angles instead of pixels. Two lines of trigonometry will place every tick, every number, and a second hand that sweeps all the way around. Let's listen closely!

| | |
|---|---|
| **Program** | `09-angles-to-pixels.py` |
| **Parts needed** | The display |
| **Time** | 25 minutes |
| **Makes sound?** | No |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* How to convert an **angle and a radius** to an **x and y** position
* Why the formula has a **minus sign** for y
* How to **erase and redraw** a moving object without clearing the whole screen
* How to center text on a point, using the font's size

## The Big Idea

On a round screen you naturally think "**how far around** and **how far out**". Those two
numbers are an **angle** and a **radius**, and together they are called **polar coordinates**.
But the display only understands **x and y**. Sine and cosine translate between them:

```python
x = center_x + radius * sin(angle)
y = center_y - radius * cos(angle)
```

This clock measures its angle like a real clock: **0 degrees points straight up**, and the angle
grows **clockwise**.

| Time on the clock | Angle | sin | cos | Where the point lands |
|-------------------|-------|-----|-----|-----------------------|
| 12 o'clock | 0° | 0 | 1 | straight above center |
| 3 o'clock | 90° | 1 | 0 | straight right of center |
| 6 o'clock | 180° | 0 | -1 | straight below center |
| 9 o'clock | 270° | -1 | 0 | straight left of center |

Why the **minus sign** on `y`? Because on the screen `y` grows **downward** (you learned that in
[Lab 04](04-hello-world.md)). A point *above* the center has a *smaller* `y`, so
we subtract. Without the minus, 12 o'clock would be at the bottom.

!!! mascot-thinking "Two Languages for One Point"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    "Three o'clock, 100 pixels out" and "x = 280, y = 180" describe the very same dot in two languages, and `sin` and `cos` are the translators. Pick whichever language makes your problem easiest, and translate at the very last step.

## Walking Through the Code

### The translator function

```python
def polar(angle_degrees, radius):
    a = math.radians(angle_degrees)
    return (round(CX + radius * math.sin(a)),
            round(CY - radius * math.cos(a)))
```

Python's `math.sin` and `math.cos` want **radians**, so `math.radians()` converts degrees first.
The function returns `(x, y)` rounded to whole pixels, because pixels cannot be fractions.
Everything else in this lab calls `polar()`.

### 60 tick marks

```python
for second in range(60):
    length = 16 if second % 5 == 0 else 7
    color = config.WHITE if second % 5 == 0 else DIM
    x0, y0 = polar(second * 6, OUTER)
    x1, y1 = polar(second * 6, OUTER - length)
    display.line(x0, y0, x1, y1, color)
```

A full circle is 360 degrees and a minute has 60 seconds, so each second is
360 / 60 = **6 degrees**. Each tick is a short line from the rim (radius `OUTER`) inward. Every
fifth tick (`second % 5 == 0`, using the **remainder** operator `%`) is longer and brighter, to
mark the hours.

### The four numbers

```python
for number, angle in (("12", 0), ("3", 90), ("6", 180), ("9", 270)):
    x, y = polar(angle, OUTER - 38)
    display.text(BIG, number, x - len(number) * BIG.WIDTH // 2,
                 y - BIG.HEIGHT // 2, config.CYAN, config.BLACK)
```

`polar()` tells you where the **center** of each number should be. But `display.text()` wants
the **top-left corner** of the text. So the code moves back half the text's width and half its
height. You used the same trick to center "Hello World!" in Lab 04.

### The second hand

```python
def draw_hand(second, color):
    tip_x, tip_y = polar(second * 6, HAND)
    for dx, dy in ((0, 0), (1, 0), (0, 1)):
        display.line(CX + dx, CY + dy, tip_x + dx, tip_y + dy, color)
    return tip_x, tip_y
```

One line is only 1 pixel thick, which is too thin to see well. Drawing **three lines side by side**, shifted by
one pixel, makes a hand 3 pixels thick.

### Moving the hand without clearing the screen

```python
second = time.localtime()[5]
if second != shown:
    if shown is not None:
        draw_hand(shown, config.BLACK)          # erase the old hand
    tip_x, tip_y = draw_hand(second, config.RED)
```

`time.localtime()[5]` is the current second. The loop checks the time 50 times a second but
only **redraws when the second changes**. To move the hand it:

1. Draws the **old** hand again in black, which erases it
2. Draws the **new** hand in red

That is much cheaper than clearing the whole screen and redrawing all 60 ticks every second, and
nothing else on the screen flickers. [Lab 10](10-flicker-free-text.md) takes this idea further.

!!! mascot-warning "Erasing Can Leave Scars"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    The black hand passes over the tick marks and the center dot and erases bits of them, and that is why the program draws the center dot again after every move. If you ever see missing pixels where an erased shape crossed another, redraw the thing underneath.

The readout line shows the hand's angle and where its tip is **relative to the center**:
`tip_x - CX` and `tip_y - CY`. At 15 seconds, the angle is 90 degrees and the tip is straight to
the right: positive x and zero y.

## Run It

Open `09-angles-to-pixels.py` and press Run. It runs until you stop it.

!!! mascot-tip "The Clock Might Start at the Wrong Time"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    The Pico has no battery clock, so on its own its time starts at a default. Thonny sets it when it connects, and if the hand moves once a second, it is working, even if the time is not right. Lab 18 shows how to get the correct time from the internet.

## What PASS Looks Like

* A ring of 60 ticks, longer at every fifth tick
* The numbers 12, 3, 6, and 9 in cyan
* A red second hand that moves once a second
* A yellow line at the bottom showing the angle and the tip position, such as
  `15s  90 deg x +92 y  +0`

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| The hand does not move | The clock is not running | Reconnect with Thonny, or check `time.localtime()` in the shell |
| The hand goes counter-clockwise | The sign of the angle is wrong | Make sure it is `second * 6`, not `-second * 6` |
| 12 appears at the bottom | You dropped the minus sign in `y` | Use `CY - radius * cos(a)` |
| Ticks are cut off | `OUTER` is bigger than `SAFE_RADIUS` | Keep `OUTER` at most `SAFE_RADIUS` |

## Try This

1. **Backwards.** Make the hand run backwards by using `60 - second` instead of `second`.
2. **A minute hand.** Add a minute hand, 70 pixels long, using `time.localtime()[4] * 6`. What
   angle should it have at 30 minutes?
3. **No minus.** Take the minus sign out of `polar()`. Which way does the hand go now, and where
   does it start?
4. **A smooth sweep.** Use `time.ticks_ms()` to move the hand a little every 50 ms, so it
   sweeps instead of ticking.
5. **Tick colors.** Make the 12, 3, 6, and 9 ticks red.

??? tip "Hint for number 2"
    At 30 minutes the minute hand is halfway around: 30 x 6 = 180 degrees, pointing straight
    down. Draw it with a function like `draw_hand`, but with a different length and color. Don't forget
    to erase the old minute hand only when the minute changes.

??? tip "Hint for number 3"
    Without the minus, `y = CY + radius * cos(a)`. At angle 0, cos is 1, so the hand starts
    pointing **down**, and it moves counter-clockwise from there.

## Check Your Understanding

1. How many degrees does a hand move each second? Each minute (for the minute hand)?
2. What is the `x, y` position of a point at 90 degrees and radius 100, if the center is (180, 180)?
3. Why does the code convert degrees to radians?

??? question "Answers"
    1. The second hand moves 6 degrees a second. The minute hand also moves 6 degrees a minute.
    2. x = 180 + 100 x sin(90°) = 280, y = 180 - 100 x cos(90°) = 180. It is (280, 180), straight
       to the right.
    3. `math.sin` and `math.cos` measure angles in radians, not degrees.

## Where Next

You now know how to put anything at any angle. [Lab 10](10-flicker-free-text.md) answers a
different question: how to change what is on the screen without a flicker.

*Review in the course:* [OLED Drawing Methods and Animation](https://dmccreary.github.io/learning-micropython/chapters/16-oled-drawing-animation/)
