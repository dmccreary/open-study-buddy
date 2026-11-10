---
title: "Lab 04: Hello World on the Display"
description: "Start the round 360 x 360 GC9B72 display, clear it, and draw a cyan ring with centered text, learning how the screen is addressed and why the corners are never seen."
---

# Lab 04: Hello World on the Display

!!! mascot-welcome "Time to Give Your Buddy a Face"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Up to now your Study Buddy could only talk through the shell. In this lab it says "Hello World!" on a round color screen, and everything you build from here on will show up there. Let's listen closely!

| | |
|---|---|
| **Program** | `04-hello-world.py` |
| **Parts needed** | The display |
| **Time** | 10 minutes |
| **Makes sound?** | No |
| **How to stop** | The program ends by itself after drawing |

## What You Will Learn

* How to start the display with one line, `config.init_display()`
* How the screen's **x and y coordinates** work
* Why the round screen has a **safe radius**
* How to center text, using the width of a font

## Wiring

The display uses the Pico's first SPI bus (SPI0). You learned SPI in the
[Communication Protocols](https://dmccreary.github.io/learning-micropython/chapters/08-communication-protocols/)
chapter, and the display is the same idea as the SPI OLED screens there, only bigger and in
color.

| Display pin | Pico pin | Wire color in the kit | What it does |
|-------------|----------|-----------------------|--------------|
| GND | GND | black | Ground |
| VCC | 3V3 | red | Power |
| SCL | GP2 | orange | SPI clock |
| SDA | GP3 | yellow | SPI data (the pixels) |
| RST | GP4 | green | Reset |
| DC | GP5 | blue | Says "this byte is a command" or "this byte is a pixel" |
| CS | GP6 | purple | Chip select |
| BL | GP7 | gray | Backlight |

The module also has SDO and TE pads. Leave them unconnected: the driver never uses them.

## The Big Idea

The display is a grid of **360 x 360 pixels**. Every pixel has an x (how far from the left)
and a y (how far from the top). The point `(0, 0)` is the **top-left**, and `y` grows
**downward**, which surprises people who remember graphs from math class.

```
(0,0) ───────────► x
  │
  │
  ▼
  y                         (359, 359)
```

But the glass is **round**. Only the circle drawn inside the square is visible, and the four
corners of the square are hidden under the bezel. Drawing there wastes time sending pixels
that nobody will ever see. `config.py` stores the geometry for you:

| Name in `config.py` | Value | Meaning |
|---------------------|-------|---------|
| `WIDTH`, `HEIGHT` | 360 | The size of the square |
| `CENTER_X`, `CENTER_Y` | 180 | The middle of the screen |
| `RADIUS` | 180 | The edge of the glass |
| `SAFE_RADIUS` | 168 | The biggest circle you can draw without the bezel clipping it |

## The Program

```python
import config
import shapes

display = config.init_display()
config.set_backlight(True)

display.fill(config.BLACK)

shapes.ring(display, config.CENTER_X, config.CENTER_Y, config.SAFE_RADIUS,
            config.CYAN, 3)

config.centered_text(display, config.BIG_FONT, "Hello World!",
                     config.CENTER_Y - 16, config.YELLOW)
config.centered_text(display, config.SMALL_FONT, "Study Buddy is alive",
                     config.CENTER_Y + 30, config.WHITE)

print("Drawn: look at the screen.")
```

## Walking Through the Code

**`import config` and `import shapes`.** `config` holds every pin and color for the kit, and
`shapes` is a small library (in `lib/shapes.py`) that draws circles, rings, and polygons.

**`display = config.init_display()`** does a lot of work in one line. It starts the SPI bus at
24 MHz, sets up the reset, DC, chip-select, and backlight pins, and builds the display object
that the driver provides. Look at `init_display()` in `config.py` to see everything it does.
Putting this in `config.py` means no lab has to repeat it.

**`config.set_backlight(True)`** turns the backlight on. Without it, the display is drawing
but you cannot see anything.

**`display.fill(config.BLACK)`** paints every pixel black. Colors such as `BLACK`, `CYAN`, and
`YELLOW` are numbers stored in `config.py`. [Lab 08](08-color-mixing.md) explains how a color
is a number.

**`shapes.ring(display, x, y, radius, color, thickness)`** draws a circle outline. Here it is
centered on the screen, with a radius of 168, in cyan, 3 pixels thick. That puts the ring
right at the visible edge of the glass.

**`config.centered_text(...)`** draws text so that it is centered left to right. The big font
is 16 pixels wide per letter, so `"Hello World!"` (12 letters) is 12 x 16 = **192 pixels wide**.
To center it, the function computes the left edge:

```python
x = (WIDTH - len(text) * font.WIDTH) // 2
```

That is (360 - 192) / 2 = **84** pixels from the left. The `//` means whole-number division.

!!! mascot-tip "Centering Anything"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    To center anything, subtract its width from the screen's width and divide by two. You will use that same recipe for text, bars, and pictures in every lab from here on.

**The `y` values.** `CENTER_Y - 16` places the top of the big letters 16 pixels above the
middle. The big letters are 32 pixels tall, so half of the height (16) sits above the center
line and half below. The small caption goes at `CENTER_Y + 30`, just under the big text.

## Run It

Open `04-hello-world.py` and press Run. The Pico draws and the program ends. The picture stays
on the screen, because the display remembers what was last drawn until you draw something else.

## What PASS Looks Like

The screen goes black, then shows a cyan ring, **Hello World!** in big yellow letters, and the
small caption "Study Buddy is alive" underneath. All the letters are inside the ring, and none
are cut off.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| Completely dark | Backlight or power | Check BL (GP7) and the VCC and GND wires |
| Bright white screen or random noise | SPI or control wires | Check SCL (GP2), SDA (GP3), RST (GP4), DC (GP5), CS (GP6) |
| Picture works but is speckled or torn | Wires too long or loose | Use short wires, or set `BAUDRATE = 12_000_000` in `config.py` |
| `ImportError: no module named 'gc9b72'` | The `lib/` folder is not on the Pico | Run `./upload-code.sh` |
| Text cut off at the sides | Text too long | Shorten it, or use the small font |

!!! mascot-warning "Blank Screen, But Lab 02 Said All OK?"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Lab 02 can feel the SCL, SDA, and BL wires but not RST, DC, or CS, because those three have no resistor to sense. If the probe is clean and the screen is blank, check RST on GP4, DC on GP5, and CS on GP6 by eye.

## Try This

1. **Your name.** Change `"Hello World!"` to your name. How long can a name be before it runs
   off the ring?
2. **Small font.** Swap `BIG_FONT` for `SMALL_FONT`. The small font is 8 pixels wide, so how
   many more letters fit across the screen?
3. **A new color.** Replace `config.YELLOW` with `config.color565(255, 128, 0)` for orange.
   (Lab 08 shows how this function works.)
4. **A second ring.** Add another ring with `shapes.ring(...)` at a smaller radius, such as 140,
   in magenta. Try three rings in a row.
5. **Off center.** What happens if you change `config.CENTER_X` to `0` in a call to
   `shapes.ring`? Which parts of the ring do you lose?

??? tip "Hint for number 2"
    The screen is 360 pixels wide. Big letters are 16 wide, so 360 / 16 = 22 letters. Small
    letters are 8 wide, so 360 / 8 = 45. But the round edge cuts off the ends of a long line,
    so the safe number is smaller near the top and bottom.

## Check Your Understanding

1. Which corner of the screen is `(0, 0)`, and which way does `y` grow?
2. Why is `SAFE_RADIUS` smaller than `RADIUS`?
3. How wide, in pixels, is `"Study Buddy is alive"` in the small font?

??? question "Answers"
    1. The top-left corner. `y` grows **downward**.
    2. The bezel (the plastic edge) covers the outermost pixels of the glass. A ring at the full
       radius would be partly hidden.
    3. 20 letters x 8 pixels = 160 pixels.

!!! mascot-celebration "Your Buddy Has a Face"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just started an SPI display, found the center of a round screen, and centered text by computing its width. That is the foundation for every picture in the rest of the kit.

## Where Next

The display works. Next, [Lab 05](05-speaker-tones.md) gives your Study Buddy a voice.

*Review in the course:* [OLED Drawing Methods](https://dmccreary.github.io/learning-micropython/chapters/16-oled-drawing-animation/)
