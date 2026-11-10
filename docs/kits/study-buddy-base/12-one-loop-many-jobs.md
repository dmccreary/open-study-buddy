---
title: "Lab 12: One Loop, Many Jobs"
description: "Run an LED blinker, a spinning dot, a clock, and a button reader all in one loop with no sleep, by checking the clock with ticks_ms, ticks_diff, and ticks_add."
---

# Lab 12: One Loop, Many Jobs

!!! mascot-welcome "Do Everything at Once"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Your Study Buddy can blink a light, spin a dot, count seconds, and listen to buttons all at the same time, with a single loop and not one `sleep` that matters. The trick is one small change in how you think about time. Let's listen closely!

| | |
|---|---|
| **Program** | `12-one-loop-many-jobs.py` |
| **Parts needed** | The onboard LED, the buttons, and the display |
| **Time** | 25 minutes |
| **Makes sound?** | No |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* Why `time.sleep()` freezes everything else
* How to give each job its own **"next time to run"**
* How `ticks_diff()` and `ticks_add()` handle the clock wrapping around
* How to count how fast your loop is going

## The Big Idea

You met non-blocking code in the
[Timers, Timing Functions, and Multi-Core](https://dmccreary.github.io/learning-micropython/chapters/20-timers-multicore/)
chapter. This lab shows it working with four jobs on a real display.

`time.sleep(0.5)` freezes the whole Pico for half a second. During that time the dot cannot
spin and the buttons cannot answer. So instead of waiting, **each job remembers when it should
next run**. The loop goes around thousands of times a second, and each time it asks every job:
"*is it your time yet?*"

```python
if time.ticks_diff(now, next_blink) >= 0:     # time to blink?
    led.value(not led.value())
    next_blink = time.ticks_add(next_blink, blink_ms)
```

Think of it like a kitchen. A cook does not stand and stare at one pot for ten minutes. They set
a timer for each pot and keep working, glancing at the timers as they go.

!!! mascot-thinking "Check the Clock, Don't Wait for It"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Waiting means doing nothing while time passes, and checking means doing useful work between looks at the clock. A program that checks can run as many jobs as it can fit between glances, and a program that waits can only run one.

## Why `ticks_diff` and `ticks_add`?

The millisecond counter, `time.ticks_ms()`, wraps back to zero after a while. If you wrote
`now >= next_blink`, the comparison would give a wrong answer right at the wrap. The two helper
functions get it right **even across the wrap**:

| Function | Use it to |
|----------|-----------|
| `time.ticks_ms()` | Read the clock, in milliseconds |
| `time.ticks_diff(a, b)` | Compute `a - b` safely. Positive means `a` is later. |
| `time.ticks_add(t, ms)` | Compute `t + ms` safely |

## Walking Through the Code

### Each job has a period and a next time

```python
now = time.ticks_ms()
blink_ms, next_blink = 500, now
spin_ms, next_spin = 50, now
clock_ms, next_clock = 1000, now
buttons_ms, next_buttons = 20, now
report_ms, next_report = 1000, now
```

Each job gets two variables: *how often* it runs, and *when it runs next*. They all start at
`now`, so every job runs once right away.

| Job | Every | What it does |
|-----|-------|--------------|
| Blink | 500 ms (changeable) | Flips the LED |
| Spin | 50 ms | Moves a cyan dot one of 36 steps around the rim |
| Clock | 1,000 ms | Shows seconds counting up |
| Buttons | 20 ms | Reads UP, DOWN, MODE |
| Report | 1,000 ms | Shows how many times the loop went round |

### The main loop

```python
while True:
    now = time.ticks_ms()
    loops += 1

    if time.ticks_diff(now, next_blink) >= 0:
        ...
        next_blink = time.ticks_add(next_blink, blink_ms)

    if time.ticks_diff(now, next_spin) >= 0:
        ...
```

Every pass reads the clock once, and then each job checks whether its time has come. If not, the
`if` is false and costs almost nothing. The loop's **speed** shows up as the "loops per second"
number, usually thousands.

### The spinning dot

```python
for step, color in ((spin_step, config.BLACK),
                    ((spin_step + 1) % SPIN_STEPS, config.CYAN)):
    a = 2 * math.pi * step / SPIN_STEPS
    shapes.circle(display, round(CX + SPIN_RADIUS * math.sin(a)),
                  round(CY - SPIN_RADIUS * math.cos(a)), 6, color, config.FILL)
```

This is the polar formula from [Lab 09](09-angles-to-pixels.md). The dot is drawn in black at the
old step (erasing it), then in cyan at the next step. `% SPIN_STEPS` wraps 36 back around to 0.

### The buttons: edges again

```python
value = pin.value()
if value == 0 and last[i] == 1:     # a press is a 1 -> 0 edge
    ...
last[i] = value
```

Each press is an edge, exactly as in Lab 11. UP halves the blink time (faster, but never below
50 ms), DOWN doubles it (slower, up to 2,000 ms), and MODE switches on **sleep mode**.

### Sleep mode: the "obvious" way

```python
if sleep_mode:
    time.sleep(0.5)             # the "obvious" way -- freezes everything
```

This is what a first program would do: sleep in the loop to be "slow enough". Turn it on and see
what happens: the **loops per second** drops from thousands to **2**, the dot stutters, and
the buttons stop answering. In sleep mode you have to **hold** MODE until the loop next looks
at it, up to half a second later.

!!! mascot-warning "Why Sleep Mode Is Hard to Turn Off"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    In sleep mode the loop only looks at the buttons twice a second, so a quick tap on MODE usually falls between two looks and is lost. Press and hold MODE for about a second, and it will be caught on the next pass.

## Run It

Open `12-one-loop-many-jobs.py` and press Run.

## What PASS Looks Like

* The onboard LED blinks.
* A cyan dot spins around the rim, smoothly.
* The seconds count up in big white digits.
* "**N loops per second**" shows a number in the thousands.
* UP and DOWN change the blink speed immediately.
* Turning on sleep mode makes the loop count fall to 2, the dot stutters, and the buttons
  barely respond.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| The dot jumps instead of spinning smoothly | Another job is taking too long | The display is the slow part; keep the dot small |
| Buttons feel slow | Sleep mode is on | Hold MODE until "SLEEP MODE ON" disappears |
| The LED never changes | `blink_ms` is huge | Press UP a few times |
| No LED at all | Plain Pico firmware | See [Lab 01](01-blink.md) |

## Try This

1. **A sixth job.** Add a job that prints `"still here"` every 3,000 ms. You only need three
   lines: a `next_` time, an `if`, and a `ticks_add`.
2. **Catch up or not?** Change job 2's `ticks_add(next_spin, ...)` to `ticks_add(now, ...)`.
   Turn sleep mode on, and then off. What is different? Which version "catches up"?
3. **Super fast blink.** Make `blink_ms` 5. What does loops per second do? Is the Pico
   working harder, or just going around the loop more?
4. **A progress bar.** Add a job that fills a thin bar across the bottom of the screen over
   10 seconds, and then starts over.

??? tip "Hint for number 2"
    With `ticks_add(next_spin, 50)`, each job moves its schedule forward by exactly 50 ms from
    its **planned** time. After the loop has been asleep for a while, the planned times are
    all in the past, so the job runs again and again on every pass until it has caught up, and
    the dot whizzes round. With `ticks_add(now, 50)`, the next run is 50 ms from **now**, so
    missed runs are forgotten and the dot just carries on at its normal speed.

??? tip "Hint for number 3"
    Loops per second is how many times the loop runs, whatever the jobs are doing. Making the
    LED blink faster adds work, but the loop count stays about the same, because checking
    "is it time?" is very quick.

## Check Your Understanding

1. Why is `time.sleep(0.5)` a problem in a program with several jobs?
2. Why use `ticks_diff(now, next_blink) >= 0` instead of `now >= next_blink`?
3. A job runs every 250 ms. How many times does it run in 10 seconds?

??? question "Answers"
    1. It freezes the whole program for half a second, so no other job can run during that time.
    2. The millisecond counter wraps around, and the plain comparison gives the wrong answer at
       the wrap. `ticks_diff` handles it correctly.
    3. 10,000 / 250 = 40 times.

## Where Next

You can now run several jobs together. [Lab 13](13-modes-state-machine.md) shows how to organize
a program that has several *modes*, so three buttons can do many things.

*Review in the course:* [Non-Blocking Timing with ticks_ms and ticks_diff](https://dmccreary.github.io/learning-micropython/chapters/20-timers-multicore/),
and the [Polling Versus Interrupt Timeline](../../sims/polling-versus-interrupt-timeline/index.md) MicroSim in this book.
