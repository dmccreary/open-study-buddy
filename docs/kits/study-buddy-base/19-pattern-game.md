---
title: "Lab 19: Pattern Memory Game"
description: "Build a memory game with colored wedges that light up and play notes. Repeat the growing pattern with the buttons, using a state machine, edge-detected buttons, precomputed shapes, and sound together."
---

# Lab 19: Pattern Memory Game

!!! mascot-welcome "Your Final Build"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    You have learned colors, angles, fast drawing, buttons, timing, state machines, and sound, and now they all work together in one game. Your Study Buddy shows a pattern, you repeat it, and each round gets a little longer and a little faster. Let's listen closely, because the notes are your best clue!

| | |
|---|---|
| **Program** | `19-pattern-game.py` |
| **Parts needed** | The whole kit: display, buttons, speaker, and the onboard LED |
| **Time** | 40 minutes |
| **Makes sound?** | **Yes** |
| **How to stop** | Press **Stop** in Thonny, or Ctrl-C |

## How to Play

The screen shows three wedges, one for each button:

| Button | Wedge | Note |
|--------|-------|------|
| **MODE** | Red, at the top | C5, 523 Hz |
| **UP** | Green, lower right | E5, 659 Hz |
| **DOWN** | Blue, lower left | G5, 784 Hz |

1. Press any button to start.
2. The buddy lights wedges and plays their notes: **watch and listen**.
3. When the onboard LED lights, it is **your turn**. Repeat the pattern with the buttons.
4. If you are right, the next round adds one more step, and the steps come a little faster.
5. If you are wrong, or wait 5 seconds, the game is over and shows your score.

The three notes are C, E, and G, a **C major chord**, so any pattern you play sounds like a
little tune.

## What You Will Learn

* How several earlier ideas combine into **one program**
* How to keep a game's memory in a **list** that grows
* How to **precompute** a shape once and replay it quickly
* How a **state machine** with four states runs a game

## The Big Idea: Every Part, Every Lab

This lab is a recap of the whole kit. Here is where each idea comes from:

| Idea in the game | From |
|------------------|------|
| A **state machine**: READY, SHOW, LISTEN, OVER | [Lab 13](13-modes-state-machine.md) |
| A **list** as the game's memory that grows by one random step each round | Course chapter on collections |
| **Angles to pixels** to build each wedge | [Lab 09](09-angles-to-pixels.md) |
| **Send only what changed**: a wedge is computed once, then replayed | [Lab 10](10-flicker-free-text.md) |
| **Edges and debounce** for the buttons | [Lab 11](11-button-bounce.md) |
| **Not waiting**: a quick second press is never missed | [Lab 12](12-one-loop-many-jobs.md) |
| **Samples make sound**: each wedge's note is made at the start | [Lab 14](14-samples-make-sound.md) |

!!! mascot-thinking "Big Programs Are Small Ideas Combined"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    The game has 300 lines but not one new idea. Every piece is something you have already built and tested on its own, and that is the secret of large programs: tested small parts, assembled carefully.

## Walking Through the Code

### The wedge table

```python
WEDGES = (("MODE", 0, config.RED, config.color565(70, 0, 0), 523),
          ("UP", 120, config.GREEN, config.color565(0, 70, 0), 659),
          ("DOWN", 240, config.BLUE, config.color565(0, 0, 90), 784))
```

One row per wedge: its **name**, its **middle angle** (0, 120, and 240 degrees apart, evenly
around the circle), its **bright** color, its **dim** color, and its **note** in hertz. A wedge
shows its dim color most of the time and its bright color while it is "lit".

### Drawing a wedge, once

This is the cleverest part. Drawing a ring-shaped wedge with `shapes.poly()` works out where
every row of the shape starts and ends, which takes a long time. But the wedge never changes
shape, so the program does that work **once, at the start**, and remembers the result as a list of
horizontal runs `(x, y, length)`.

```python
class RunRecorder:
    def __init__(self):
        self.runs = []

    def hline(self, x, y, length, color):
        self.runs.append((x, y, length))
```

`shapes.poly()` draws a filled shape by calling `display.hline(...)` for each row. The
`RunRecorder` is a **stand-in for the display** that has an `hline` method that, instead of
drawing, **writes the call down**. Pass the recorder to `shapes.poly()` and it fills in the list
of runs without drawing a single pixel.

```python
def paint(which, lit):
    name, middle, bright, dim, freq = WEDGES[which]
    color = bright if lit else dim
    for x, y, length in runs[which]:
        display.hline(x, y, length, color)
```

Lighting a wedge now just **replays** the saved runs in a different color. That is fast enough
that the light and the sound start together.

!!! mascot-tip "Stand-In Objects"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    If a function only *calls methods* on an object you give it, you can hand it a fake object that has the same methods. The `RunRecorder` trick works for testing, for recording, and for sending the same drawing to two places at once.

The wedge's outline is built from two arcs: points every 5 degrees along the **outer** edge
(radius 164), and back along the **inner** edge (radius 82). Each wedge is 110 degrees wide, which
leaves 10 degrees of black between wedges.

### Sounds, made once

```python
show_tones = [tone(w[4], TONE_MS) for w in WEDGES]
press_tones = [tone(w[4], PRESS_MS) for w in WEDGES]
buzz = tone(110, 600, "square")
```

Calculating a sine wave takes time. So all the notes are made **once at the start**, while the
screen says "getting ready". Playing a note later is just `audio.write(...)`. The game-over
**buzz** is a 110 Hz **square wave**, which sounds harsh on purpose.

### The game's states

```python
READY, SHOW, LISTEN, OVER = range(4)
state = READY
pattern = []                     # the game's memory: wedge numbers
position = 0                     # how far through the pattern you are
```

`range(4)` hands out the numbers 0, 1, 2, and 3 to four names, so the code can say `state == LISTEN` instead of `state == 2`.

| State | What happens | Leaves when |
|-------|--------------|-------------|
| **READY** | Shows "READY" and your best score | Any button press |
| **SHOW** | Adds a random step, plays the whole pattern | The pattern has played |
| **LISTEN** | Waits for your presses | You finish it, make a mistake, or time out |
| **OVER** | Shows your score, buzzes, and flashes the step you missed | A press (after 1 second), or 4 seconds idle |

### SHOW: grow the pattern

```python
pattern.append(random.randrange(3))
...
gap = max(LEAST_GAP_MS, FIRST_GAP_MS - 20 * round_number)
for step in pattern:
    flash(step, show_tones[step], TONE_MS)
    time.sleep_ms(gap)
```

The pattern is a **list** of numbers 0, 1, and 2. Each round `append`s one new random number. The
`gap` between steps shrinks by 20 ms a round, from 300 ms down to a minimum of 60 ms. The
`max(LEAST_GAP_MS, ...)` is the clamp trick from Lab 07: it stops the gap from shrinking below
60 ms. By round 12, the game is as fast as it will go.

`flash()` lights the wedge, plays its note, waits for the note, and puts the light out.

!!! mascot-warning "It's Fine to Sleep Here (But Not in LISTEN)"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    SHOW uses `time.sleep_ms` because while the buddy is playing the pattern, you are not supposed to press anything. LISTEN never sleeps for long, because a second quick press could be missed, as Lab 12 showed, so check the context before you decide that `sleep` is a bug.

### LISTEN: check each press

```python
if button is not None:
    ...
    if button != pattern[position]:
        game_over(now)
        continue
    paint(button, True)
    audio.write(press_tones[button])
    lit = button
    lit_until = time.ticks_add(now, PRESS_MS)
    position += 1
    if position == len(pattern):        # the whole pattern: right!
        ...
        state = SHOW
```

`pressed(now)` returns the number of a button that just went down, using the edge-and-debounce
code from Lab 11, or `None`. For each press, the game checks it against the pattern at
`position`:

* **Wrong?** Game over.
* **Right?** Light the wedge, play its note, and move on one step.
* **Reached the end?** The round is won, and the state goes back to SHOW for a longer pattern.

The wedge you press stays lit for `PRESS_MS` (200 ms), and the program checks `lit_until` with
`ticks_diff` on later passes. It does **not** sleep: that is the Lab 12 technique, and it lets a quick next
press be caught.

If 5 seconds pass without any press (`TIMEOUT_MS`), the game ends too.

### OVER: show the score

The score is `len(pattern) - 1`, the number of rounds you completed (the round you failed does
not count). The game keeps your `best` since you started, buzzes, and flashes the wedge you should
have pressed three times, so you learn from the mistake. For a second, presses are ignored,
because the wrong press may still be bouncing.

## Run It

Open `19-pattern-game.py` and press Run. When the screen says **READY**, press any button.

## What PASS Looks Like

* A pattern plays, with each wedge lighting up and sounding its note.
* The LED lights when it is your turn.
* The buttons light and sound their wedges.
* A right answer goes on to a longer pattern.
* A wrong one (or 5 seconds of waiting) buzzes, and shows your score and your best.

The shell prints each round, for example `Round 3: MODE UP UP`, and `Game over: 2 right. Best: 2`.

## If Something Goes Wrong

| What you see or hear | Likely cause | Fix |
|----------------------|--------------|-----|
| The screen is blank | Display wiring | Run [Lab 04](04-hello-world.md) |
| No sound | Speaker wiring | Run [Lab 05](05-speaker-tones.md) |
| A button does nothing | Wiring | Run [Lab 03](03-buttons.md) |
| Game ends on a correct press | Bounce | Raise `DEBOUNCE_MS` |
| A new game starts before you want it to | A press in the OVER state starts a new game after 1 second | Wait for READY, or raise the `1000` in the OVER state |
| `MemoryError` at "getting ready" | Not enough RAM for the three notes | Lower `TONE_MS` or `PRESS_MS` |

## Try This

1. **A fourth wedge.** There are only three buttons, but a long press could be a fourth. What
   would have to change in `WEDGES` and `pressed()`?
2. **Strict mode.** Make the game end on the first mistake of a pattern you have already seen
   twice. (Hint: you need to remember each round's result.)
3. **Save the best score.** Save the best score to a file (`open("best.txt", "w")`) so it
   survives a power cycle. Read it back at the start.
4. **Your own tune.** Change the notes in `WEDGES`. Which three notes sound best together?
5. **Harder and easier.** Change `FIRST_GAP_MS` and `LEAST_GAP_MS`. What is the fastest you can
   keep up with?

??? tip "Hint for number 3"
    Reading: wrap `open("best.txt")` in `try`/`except OSError` (the file will not exist the
    first time), and use `int(f.read())`. Writing: inside `game_over()`, when `best` goes up,
    open `"best.txt"` with `"w"` and write `str(best)`. Writing a file takes a few milliseconds, so
    only do it when the score *improves*. You met file handling in the
    [File Systems](https://dmccreary.github.io/learning-micropython/chapters/21-file-systems-debugging/)
    chapter of the course.

??? tip "Hint for number 1"
    A short press could be one wedge each, and a press held for more than 600 ms could be the
    fourth. You would need to measure how long a button was held, as in Lab 03's Try This.
    `WEDGES` would get a fourth row with its own angle (90 degrees apart instead of 120), and wedge widths
    would need to shrink.

## Check Your Understanding

1. Why does the game compute each wedge's runs once, instead of every time it lights?
2. What does the `RunRecorder` do?
3. Why is `time.sleep_ms` fine in the SHOW state but a problem in LISTEN?
4. If you are in round 5, how many steps are in the pattern, and what is the score if you
   fail it?

??? question "Answers"
    1. Filling a shape is slow. Doing it once and replaying the saved lines is fast enough for
       the light and sound to start together.
    2. It stands in for the display. `shapes.poly()` calls its `hline`, and instead of drawing,
       it records each line so the game can replay them later.
    3. In SHOW you are only watching, so freezing is harmless. In LISTEN, a sleep could make
       the game miss a quick button press.
    4. Five steps. The score is `5 - 1 = 4`, because the round you failed does not count.

!!! mascot-celebration "You Built a Whole Game"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You used a state machine, a growing list, precomputed shapes, debounced buttons, non-blocking timing, and synthesized notes in one working program, which makes you a real embedded programmer. Every part of your Study Buddy kit now has a job, and you know how each one works.

## Where Next

* **Run the finished demo.** Copy `main.py` to the Pico and power it up. You can now read every
  demo's source and understand it.
* **Build your own game.** Reuse the wedge table, the state machine, and the tone maker for a new
  game, such as a reaction timer or a rhythm game.
* **Keep going in the book.** Chapter 12 uses the microphone for **wake-word detection**, and
  Chapter 13 connects your Study Buddy to an AI agent.

*Related in this book:* [Chapter 7: Buttons, State Machines, and Device Modes](../../chapters/07-buttons-and-device-modes/index.md)
