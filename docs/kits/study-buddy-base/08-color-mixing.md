---
title: "Lab 08: How the Display Mixes Color"
description: "Learn RGB565, the 16-bit color format used by the round display: five bits of red, six of green, five of blue. Draw three color strips and a full rainbow ring."
---

# Lab 08: How the Display Mixes Color

!!! mascot-welcome "Every Color Is Just a Number"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    The seven tests are done, so from here each lab explains one idea about how your kit works. First up is color: how a tiny screen makes every color of the rainbow out of just three lights. Let's listen closely, and look closely too!

| | |
|---|---|
| **Program** | `08-color-mixing.py` |
| **Parts needed** | The display |
| **Time** | 20 minutes |
| **Makes sound?** | No |
| **How to stop** | The program ends by itself after drawing |

## What You Will Learn

* How red, green, and blue lights mix to make any color
* How **16 bits** are shared out as **5 + 6 + 5** (this is **RGB565**)
* How to read a color number in **binary** and **hexadecimal**
* How to draw a polygon with `shapes.poly()` and loop over a ring of colors

## The Big Idea

Every pixel on the screen is three tiny lights: one red, one green, one blue. To make yellow,
turn red and green on and blue off. To make white, turn all three on. To make orange, red is
full, green is half, and blue is off.

The display wants **16 bits** for each pixel. You cannot divide 16 evenly into three, so the
bits are shared out like this:

```
bit:  15 14 13 12 11 | 10  9  8  7  6  5 |  4  3  2  1  0
       r  r  r  r  r |  g  g  g  g  g  g |  b  b  b  b  b
```

| Color | Bits | Number of shades |
|-------|------|------------------|
| Red | 5 | 2<sup>5</sup> = 32 |
| Green | 6 | 2<sup>6</sup> = 64 |
| Blue | 5 | 2<sup>5</sup> = 32 |

Green gets the extra bit because human eyes are **most sensitive to green**, so extra shades of
green are the ones you would notice if they were missing.

The function `color565(red, green, blue)` takes three ordinary numbers from 0 to 255 (the
way you wrote colors in the course) and packs them into 16 bits by **keeping only the top
bits** of each one. The calculation is a single line in the driver:

```python
return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3
```

* `red & 0xF8` keeps the top 5 bits of red, then `<< 8` slides them to bits 15 to 11.
* `green & 0xFC` keeps the top 6 bits of green, then `<< 3` slides them to bits 10 to 5.
* `blue >> 3` throws away the bottom 3 bits of blue, leaving 5 bits in the right place.

!!! mascot-thinking "Throwing Away Detail on Purpose"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A 16-bit color has 65,536 possible colors, where a full 24-bit color has more than 16 million. The display throws away the bits your eye notices least so that every pixel is two bytes instead of three, which means the screen updates 50 percent faster.

## Walking Through the Code

### Part 1: Show the packing in the shell

```python
for name, rgb in (("orange", (255, 128, 0)), ("sky blue", (90, 170, 255)),
                  ("white", (255, 255, 255))):
    color = config.color565(*rgb)
    bits = "{:016b}".format(color)
    print("{:9} {:>15} -> 0x{:04X} = {} {} {}".format(
        name, str(rgb), color, bits[:5], bits[5:11], bits[11:]))
```

The loop uses `*rgb` to unpack a tuple into three arguments. `"{:016b}"` formats a number as 16
binary digits, and `"0x{:04X}"` formats it as 4 hexadecimal digits. Slicing the string
(`bits[:5]`, `bits[5:11]`, `bits[11:]`) pulls out the red, green, and blue parts.

The shell shows:

| Color | RGB in | In 16 bits (r, g, b) | Hex |
|-------|--------|----------------------|-----|
| orange | (255, 128, 0) | `11111 100000 00000` | 0xFC00 |
| sky blue | (90, 170, 255) | `01011 101010 11111` | 0x5D5F |
| white | (255, 255, 255) | `11111 111111 11111` | 0xFFFF |

Check sky blue's red yourself: 90 in binary is `01011010`. The top five bits are `01011`, and the
bottom three (`010`) get thrown away.

### Part 2: Three strips, one per color

```python
STRIPS = (("red: 5 bits, 32 shades", 32, 11),
          ("green: 6 bits, 64 shades", 64, 5),
          ("blue: 5 bits, 32 shades", 32, 0))
...
for i in range(STRIP_W):
    level = i * shades // STRIP_W         # 0 .. shades-1 across the strip
    display.vline(STRIP_X + i, y + 18, STRIP_H, level << shift)
```

Each strip is 200 vertical lines wide. For each line, `level` counts up from 0 to the number
of shades minus one, and `level << shift` slides it to the right place in the 16 bits. That
means the program builds a color number **directly from bits**, without calling `color565()`.

Look closely at the red and blue strips: you can see **steps**, because there are only 32 shades
spread over 200 pixels. The green strip has steps half as wide.

### Part 3: A ring of every hue

A ring of hues is built from 72 wedges of 5 degrees each. For each wedge,
`hue_to_rgb(hue)` mixes **two** lights at a time:

| Hue | Color | What is happening |
|-----|-------|-------------------|
| 0° | red | red full |
| 60° | yellow | green rises |
| 120° | green | red falls |
| 180° | cyan | blue rises |
| 240° | blue | green falls |
| 300° | magenta | red rises |

Inside each 60-degree sector, one color rises from 0 to 255 and another falls from 255 to 0.
The function finds the sector with `int(hue / 60) % 6`, and the position inside it from the
fractional part. [Lab 09](09-angles-to-pixels.md) explains the `sin` and `cos` that place each wedge.
Each wedge is four corners, drawn with `shapes.poly()` as a filled polygon, and each overlaps the next by half a degree
so no gaps show.

## Run It

Open `08-color-mixing.py` and press Run. For a way to experiment with the same numbers, open
the [RGB565 Color Mixer](../../sims/rgb565-color-mixer/index.md) MicroSim and slide the three
colors yourself.

## What PASS Looks Like

* Three strips fade from black to full **red**, **green**, and **blue**. The red and blue strips
  show visible steps.
* A rainbow ring goes all the way around the edge of the screen.
* The shell lists how the three colors are packed into bits.

## If Something Goes Wrong

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| Colors look wrong (red where blue should be) | Display color order | This kit's driver is set up right; check you have not edited `gc9b72.py` |
| Gaps between the wedges | Wedge overlap too small | Make `a1` a bit larger than `step * 5 + 5` |
| The ring is cut off at the edges | `OUTER` too large | `OUTER` must be at most `SAFE_RADIUS` |

## Try This

1. **Same color?** `color565(7, 7, 7)` and `color565(0, 0, 0)` look almost the same. Print both in
   binary with `"{:016b}".format(...)`. Which of the three parts are the same, and which part
   is not? What is the smallest red that is not black?
2. **Fewer green shades.** Change the green strip's shades from 64 to 32 (and its label). Can
   you see the steps now? This is what green would look like with only 5 bits.
3. **Find the bits.** Print white, gray, and yellow in 16 bits. Which bits are on for each?
4. **Your own color.** Pick a color from a paint program, write down its red, green, and blue
   numbers, and show it as a filled circle with `shapes.circle`.

??? tip "Hint for number 1"
    Red keeps the top 5 bits, so 7 (`00000111`) becomes `00000`, which is the same as 0. The
    smallest red that survives is 8 (`00001000`). Blue works the same way. Green keeps the
    top **6** bits, so 7 (`00000111`) becomes `000001`, which is not zero, and the smallest
    green that survives is 4.

## Check Your Understanding

1. How many different colors can RGB565 make?
2. Why does green get 6 bits instead of 5?
3. What is the RGB565 number for pure red (255, 0, 0), in binary?

??? question "Answers"
    1. 32 x 64 x 32 = 65,536 colors.
    2. Human eyes are most sensitive to green, so extra shades of green are the ones you would
       notice missing.
    3. `11111 000000 00000`, which is `0xF800`, the same as `config.RED`.

## Where Next

The rainbow ring used angles and radii to place its wedges. [Lab 09](09-angles-to-pixels.md)
explains exactly how.

*Review in the course:* [Color Displays and E-Paper Screens](https://dmccreary.github.io/learning-micropython/chapters/17-color-epaper-displays/)
