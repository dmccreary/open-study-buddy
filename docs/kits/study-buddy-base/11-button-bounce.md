---
title: "Lab 11: What a Button Press Really Looks Like"
description: "See contact bounce for yourself by counting pin changes, naive presses, and debounced presses for each button, and learn the difference between a button's level and its edge."
---

# Lab 11: What a Button Press Really Looks Like

!!! mascot-welcome "Buttons Are Messier Than They Look"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    To you a button press is one clean click. To the Pico it can be a dozen flickers in a few thousandths of a second, and in this lab you will count them. Let's listen closely, because this one is full of tiny surprises!

| | |
|---|---|
| **Program** | `11-button-bounce.py` |
| **Parts needed** | The three buttons and the display |
| **Time** | 20 minutes |
| **Makes sound?** | No |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* The difference between a button's **level** and its **edge**
* What **contact bounce** is, and why it happens
* How **debouncing** removes it
* How to keep separate lists of values for each of several buttons

## The Big Idea

### Level versus edge

`button.value()` tells you the **level**: `0` while the button is held, `1` when it is not. But
most programs do not care that the button *is down*. They care that it *just went down*. That
moment, when the reading changes from `1` to `0`, is the **edge**.

| | Level | Edge |
|---|-------|------|
| **Question** | "Is it down right now?" | "Did it just go down?" |
| **True for** | As long as you hold it | One instant |
| **Good for** | Holding to record (Lab 07) | Counting, stepping through modes |

To find the edge, **remember the last reading**, and act only when the new reading differs.

### Bounce

A button is two bits of metal. When you push them together they do not touch once and stay
there. They **rattle**: touch, spring apart, touch again, for a few milliseconds. A fast loop
sees every rattle as a new press.

```
Pin reads:   1 1 1 0 1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1
                   ▲ the press starts          ▲ the release rattles too
```

### Debounce

The fix is to **only believe a new level once the pin has stayed there long enough**. People
cannot press a button 30 times a second, so anything faster than that is the metal, not your
finger. While the metal rattles, the pin never holds still for 30 ms, so the rattle is
ignored. Once it settles, the press counts **once**.

!!! mascot-thinking "Ignoring Is a Skill"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A debounce does not fix the button, it teaches the program what to trust. The rattle still happens, and the program simply waits until the pin has been quiet for a moment before it believes what it sees.

## Walking Through the Code

### Six lists, three buttons

```python
last_raw = [1, 1, 1]          # the last reading of each pin
changes = [0, 0, 0]           # every 1->0 or 0->1 the loop saw
naive = [0, 0, 0]             # 1->0 edges with no debounce at all
real = [0, 0, 0]              # debounced presses
steady = [1, 1, 1]            # the debounced level: what we believe
changed_at = [0, 0, 0]        # when the pin last changed at all
```

Each list has one slot for MODE, one for UP, and one for DOWN. Together, the six lists are the
program's memory. The three counters you see on the screen are:

| On screen | Counts | Meaning |
|-----------|--------|---------|
| **changes** | Every `1 to 0` and `0 to 1` | Everything the pin did, rattle included |
| **naive** | Every `1 to 0` only | What a beginner's program would call "presses" |
| **real** | Only debounced presses | What actually happened |

### The loop has no sleep

```python
while True:
    now = time.ticks_ms()
    for i in range(3):
        raw = pins[i].value()
        if raw != last_raw[i]:
            # An edge. Count it, every one, bounce or not...
            last_raw[i] = raw
            changed_at[i] = now
            changes[i] += 1
            if raw == 0:
                naive[i] += 1
```

The loop on purpose has **no `sleep`**, so it reads the pins as fast as it possibly can and
catches every rattle. Look at the first `if`: it fires on *any* difference from the last
reading. It records the time of the change in `changed_at[i]`, and counts it.

### The debounce

```python
if raw != steady[i] and time.ticks_diff(now, changed_at[i]) >= DEBOUNCE_MS:
    steady[i] = raw
    if raw == 0:
        real[i] += 1
```

Read it as a sentence: "*If the pin is now at a different level from the one I believe in
(`steady`), **and** it has stayed unchanged for at least 30 ms, then believe it.*" Because
`changed_at[i]` is reset on every rattle, the clock keeps restarting until the pin finally holds
still. Only then does `real[i]` go up by one.

### Showing the numbers

```python
def number(font, value, x, y, color):
    display.text(font, "%3d" % (value % 1000), x - 3 * font.WIDTH // 2, y,
                 color, config.BLACK)
```

`"%3d"` always makes a 3-character number, padded with spaces on the left. Because the font draws
its own background, this covers the previous number completely, with no erasing. That is the
overwrite trick from [Lab 10](10-flicker-free-text.md).

The circle above each button fills in cyan while `steady[i] == 0`, which means while the debounced
button is held.

## Run It

Open `11-button-bounce.py` and press Run. Press each button in different ways: slow and
firm, then quick and light. Watch the **changes**, **naive**, and **real** counters.

## What PASS Looks Like

* Each press adds **1** to **real**.
* **naive** is the same as **real**, or higher. Any difference is bounce that the debounce
  caught.
* **changes** is at least double **real**, because each press has an edge down and an edge up,
  and more if it bounced.
* The circle above each button fills while it is held.

The shell prints a line for every change the loop saw, and a `PRESS #` line for every real
press.

!!! mascot-tip "Cheap Buttons Bounce More"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    If you never see any bounce, your buttons are good ones, so try pressing them slowly and hard, then quickly and lightly, and watch for the first extra count. A button that bounces a lot is a perfect test subject for your debounce time.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| **real** is 0 after a press | The press was too short, or the wire is loose | Press longer than 30 ms; check the wire |
| **naive** always equals **real** | Your buttons are very clean | Try quick, light presses; that is good news |
| **changes** goes up by 1 only | Only the press edge was seen | The release edge counts too; release the button |
| The numbers do not change | Nothing is drawn | Check that you ran Lab 04 first |

## Try This

1. **No debounce.** Set `DEBOUNCE_MS` to `0`. Does **real** now match **naive**?
2. **Too slow.** Set `DEBOUNCE_MS` to `300`. Every press still counts, but watch the circle: how
   long after you press does it fill? That delay is the price of a long debounce. What is the
   shortest debounce time that never counts a bounce?
3. **A sleep "fix".** Add `time.sleep_ms(50)` at the bottom of the loop. Do the bounces
   disappear? Why is that not a good fix? (Hint: try a very quick tap.)
4. **Long press.** Count how long each button was held. When it is released, print the number
   of milliseconds it was down.

??? tip "Hint for number 3"
    A `sleep_ms(50)` makes the loop look only 20 times a second, so it often misses the
    rattle entirely. But it will also miss a **real** tap shorter than 50 ms, and it freezes
    the whole program, so nothing else can run. Lab 12 shows the better fix.

## Check Your Understanding

1. What is the difference between a button's level and its edge?
2. Why does the debounce keep resetting `changed_at[i]` on every change?
3. Why would a very long debounce, such as 1 second, be a bad idea for a game?

??? question "Answers"
    1. The level is whether it is down right now. The edge is the moment it changed.
    2. So the 30 ms countdown restarts every time the contacts rattle. The press is only
       believed after the pin has held still for the full time.
    3. You would have to hold each button for a whole second before it did anything, and a quick
       tap would never count.

## Where Next

Your program can now tell what a real press is. But you still used a `sleep` in many places,
and `sleep` freezes everything else. [Lab 12](12-one-loop-many-jobs.md) shows how to do
several jobs at once.

*Review in the course:* [Button Debouncing](https://dmccreary.github.io/learning-micropython/chapters/06-digital-io-interrupts/),
and the [Button Bounce and Debounce Visualizer](../../sims/debounce-bounce-visualizer/index.md) MicroSim in this book.
