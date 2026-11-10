---
title: "Lab 13: Modes as a State Machine"
description: "Build a three-mode program (color, count, dice) where MODE switches modes and UP and DOWN mean something different in each, using a state variable and a table of functions."
---

# Lab 13: Modes as a State Machine

!!! mascot-welcome "Three Buttons, Endless Features"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    A watch, a microwave, and a phone each have only a few buttons and do dozens of things. They all use the same pattern, and by the end of this lab you will own it. Let's listen closely!

| | |
|---|---|
| **Program** | `13-modes-state-machine.py` |
| **Parts needed** | The buttons and the display |
| **Time** | 30 minutes |
| **Makes sound?** | No |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## What You Will Learn

* What a **state machine** is
* How to keep a program's current **mode** in one variable
* How to store **functions in a table** and call them by number
* How to add a mode by adding **one line**

## The Big Idea

With only three buttons, every button must mean different things at different times. Here, MODE
steps between three **modes** (the programmers' word is **states**), and UP and DOWN do
something different in each:

| State | UP does | DOWN does |
|-------|---------|-----------|
| **COLOR** | Next color | Previous color |
| **COUNT** | Count up | Count down |
| **DICE** | Roll one die | Roll two dice |

The program keeps one variable, `state`, that says which mode it is in. Each state is a table
entry with **two small functions**:

| Function | When it runs | Its job |
|----------|--------------|---------|
| `enter()` | Once, when you arrive in the state | Draw the screen for this state |
| `button(name)` | Each time UP or DOWN is pressed | Do whatever the button means here |

The main loop does **not care** which state it is in. It finds a button press and hands it to
the current state's `button()` function.

!!! mascot-thinking "Same Loop, Different Behavior"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Notice what is missing: there is no giant `if state == COLOR ... elif state == COUNT ...` anywhere in the main loop. The program picks the right behavior by *looking it up*, so the loop never has to change when you add a mode.

Look at the [Device Mode State Machine](../../sims/device-mode-state-machine/index.md) MicroSim in this book to see
the same idea animated.

## Walking Through the Code

### The table

```python
STATES = (("COLOR", color_enter, color_button),
          ("COUNT", count_enter, count_button),
          ("DICE", dice_enter, dice_button))
state = 0
```

`STATES` is a tuple of tuples. Each inner tuple is **(name, enter function, button function)**.
Functions are values in Python, so they sit in a table just like numbers or strings. The
variable `state` is just the **position** in the table: 0 is COLOR, 1 is COUNT, 2 is DICE.

### The main loop

```python
for i, name in enumerate(("MODE", "UP", "DOWN")):
    value = pins[i].value()
    if value != last[i] and time.ticks_diff(now, changed_at[i]) > DEBOUNCE_MS:
        last[i] = value
        changed_at[i] = now
        if value == 0:                       # a press
            if name == "MODE":
                go_to((state + 1) % len(STATES))
            else:
                STATES[state][2](name)       # the state's button()
```

This is the edge-plus-debounce loop from Labs 03 and 11. When it sees a press:

* **MODE:** moves to the next state with `(state + 1) % len(STATES)`. The `%` (remainder)
  wraps 3 back to 0, so after DICE comes COLOR again.
* **UP or DOWN:** calls `STATES[state][2](name)`. That is: look in the table at row `state`,
  take item `2` (the button function), and call it with the button's name.

### Changing state

```python
def go_to(new_state):
    global state
    state = new_state
    print("state ->", STATES[state][0])
    draw_tabs()
    STATES[state][1]()              # the new state's enter()
```

Moving to a new state does three things: remember it, redraw the tabs along the top with the
current one highlighted, and run that state's `enter()` function, which draws the stage.

### A state's own memory

```python
color_index = 0

def color_button(name):
    global color_index
    color_index = (color_index + (1 if name == "UP" else -1)) % len(COLORS)
    color_show()
```

Each state keeps its own variables (`color_index`, `count`). They are **not reset** when you
leave. Go to COUNT, count to 5, switch to DICE and back, and the 5 is still there.

### The dice

```python
PIPS = {1: ((1, 1),), 2: ((0, 0), (2, 2)), 3: ((0, 0), (1, 1), (2, 2)), ...}
DIE = 80

def draw_die(x, y, value):
    display.fill_rect(x, y, DIE, DIE, config.WHITE)
    for column, row in PIPS[value]:
        shapes.circle(display, x + 16 + column * 24, y + 16 + row * 24, 7,
                      config.BLACK, config.FILL)
```

A **dictionary** maps each die value to the list of dots (called *pips*) it needs, written as
`(column, row)` in a 3-by-3 grid. A 3 is the dots at `(0,0)`, `(1,1)`, `(2,2)`: the
diagonal. Each pip is placed 24 pixels from its neighbor.

`random.randint(1, 6)` picks the roll. At the start, `random.seed(time.ticks_us())` mixes in the
clock so the dice are different each time you run the program. Without that, the Pico could
roll the same sequence after every reset.

## Run It

Open `13-modes-state-machine.py` and press Run.

## What PASS Looks Like

* Three tabs across the top: **COLOR**, **COUNT**, and **DICE**, with the current one highlighted
  in cyan.
* **MODE** moves the highlight along and wraps around.
* In **COLOR**, UP and DOWN change a big circle through eight colors, and its name shows underneath.
* In **COUNT**, UP and DOWN change a big number.
* In **DICE**, UP rolls one die and DOWN rolls two, and shows the total.
* The shell prints `state -> COLOR`, `state -> COUNT`, and so on.

!!! mascot-tip "Adding a Mode Is Easy"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    To add a state, write its two functions and add one line to `STATES`. Nothing else in the program changes, because the main loop and the tabs read the table.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| A press does two things | Bounce | Check `DEBOUNCE_MS` (it is 40 here) |
| `KeyError` on dice | A roll outside 1 to 6 | `PIPS` needs an entry for every value |
| Old pictures stay behind when you change state | `enter()` did not call `clear_stage()` | Make sure every `enter()` starts by clearing |
| `NameError: name 'color_show'` | Functions defined in the wrong order | Define a function before the code that calls it runs |

## Try This

1. **A fourth state, COIN.** UP flips a coin and shows **HEADS** or **TAILS**. Write
   `coin_enter()` and `coin_button()`, and add one line to `STATES`.
2. **Remember or forget.** The count survives leaving and coming back to COUNT. Why? Make it
   reset to 0 every time you *enter* the state instead.
3. **Long press.** Make a long press of MODE (over a second) go **backwards** through the
   states. Where in the loop would you measure how long it was held?
4. **Show the state in the LED.** Light the onboard LED only in the DICE state.

??? tip "Hint for number 1"
    Follow the pattern of the other states:

    ```python
    def coin_enter():
        clear_stage()
        put("UP: flip a coin", 270, DIM)

    def coin_button(name):
        face = "HEADS" if random.randint(0, 1) == 0 else "TAILS"
        put(face, CY - 16, config.YELLOW, BIG, 6)

    STATES = (("COLOR", color_enter, color_button),
              ("COUNT", count_enter, count_button),
              ("DICE", dice_enter, dice_button),
              ("COIN", coin_enter, coin_button))
    ```

    The tabs are laid out from `len(STATES)`, so with four states you may need to shrink the
    7-character label width so they fit on the round screen.

??? tip "Hint for number 2"
    The count lives in a global variable that nothing resets. Put `count = 0` at the top of
    `count_enter()` (with `global count`) to make it start fresh every time.

## Check Your Understanding

1. What does the variable `state` store?
2. What does `STATES[state][2](name)` do, step by step?
3. Why does a state machine make it easy to add a new mode?
4. What does `(state + 1) % len(STATES)` do when `state` is 2?

??? question "Answers"
    1. The position in the `STATES` table of the current mode.
    2. It looks up row `state` in the table, takes the third item (the button function), and
       calls it with the button's name.
    3. Each state is two functions plus one table line, so you add a mode without changing the
       main loop.
    4. `(2 + 1) % 3` is 0, so it wraps around to the first state.

!!! mascot-celebration "You Know the Pattern Behind Every Gadget"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You have used a state variable, a table of functions, and edge-detected buttons together, which is the same skeleton inside digital watches, microwaves, and the finished Study Buddy demo. Every mode you add from now on is two functions and one line.

## Where Next

Next, the kit gets back to *sound*. [Lab 14](14-samples-make-sound.md) shows you what a sound wave
looks like as a list of dots.

*Related in this book:* [Chapter 7: Buttons, State Machines, and Device Modes](../../chapters/07-buttons-and-device-modes/index.md)
