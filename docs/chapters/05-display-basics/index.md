---
title: "Display Basics: Pixels, Color, and Frame Size"
description: "How the 360 by 360 round display works: SPI, pixels, RGB565 color, the display driver, frame size, and why redrawing a full frame on every change is too slow."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 11:02:16"
version: 1.11
---

# Display Basics: Pixels, Color, and Frame Size

## Summary

This chapter shows how the 360 by 360 round display works. Students learn SPI, pixels, and RGB565 color, then calculate the size of a full frame and discover why redrawing everything on each update is too slow. After this chapter, students can draw to the display and explain why the next chapter's region-based approach is needed.

## Concepts Covered

This chapter covers the following 13 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| SPI Bus | 94 |
| Pixel | 193 |
| Clock Face Geometry | 4 |
| SPI Display Driver | 47 |
| RGB565 Color | 98 |
| Fonts | 2 |
| Polar to Cartesian | 2 |
| Backlight Control | 1 |
| Frame Buffer | 93 |
| Color Themes | 2 |
| Frame Size Calculation | 92 |
| Full-Frame Update | 45 |
| Update Bandwidth | 46 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 4: The Pico Kit Hardware and Wiring](../04-pico-kit-hardware/index.md)

---

## Why a Screen Is a Math Problem

Your Study Buddy talks to people through a round screen. Putting a picture on it sounds simple, and in a few lines of code it is. The surprise comes when you ask for something smooth, like a moving level meter, while the microphone is also sending 40 ms of sound that must be handled on time. Then the screen turns out to be the slowest part of the whole device.

!!! mascot-welcome "Pictures Cost Bytes"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    In this chapter you will draw on the round screen, and then do the arithmetic that explains why a full redraw is too slow for a device that must also listen. Let's listen closely! You will leave with a number you can calculate for yourself, and it will shape every display decision in the book.

## The SPI Bus

The display connects to the Pico over an **SPI bus**. SPI (Serial Peripheral Interface) is a way for two chips to exchange bytes over a few wires, one bit at a time. One chip is the *controller* (the Pico), and the other is the *peripheral* (the display). Four signals make up a full SPI bus.

| Signal | Also called | Direction | Display wire |
|--------|-------------|-----------|--------------|
| SCK | Clock | Pico to display | SCL (GP2) |
| MOSI | Controller out, peripheral in | Pico to display | SDA (GP3) |
| MISO | Controller in, peripheral out | Display to Pico | Not used |
| CS | Chip select | Pico to display | CS (GP6) |

The clock wire pulses once for every bit. On each pulse, the Pico puts the next bit on the MOSI wire, and the display reads it. This display never talks back, so the MISO wire (labeled SDO on the display board) is left unconnected.

The speed of the bus is its **baud rate**, in bits per second. The kit asks for 24 million bits per second, which MicroPython sets up like this.

```python
spi = SPI(0, baudrate=24_000_000, sck=Pin(2), mosi=Pin(3))
```

The `0` selects SPI block 0, `baudrate` is the speed you request, and `sck` and `mosi` name the two data pins.

!!! mascot-warning "The Rate You Ask For Is Not Always the Rate You Get"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    MicroPython divides a 48 MHz clock and rounds down to the nearest rate it can make, so asking for 20 MHz gives 12 MHz, and nothing exists between 12 and 24 MHz. To see what you really got, print the SPI object. If the picture speckles on long wires, step down to 12,000,000.

The measurements in the kit's `config.py` show the pattern clearly.

| You ask for (Hz) | You get (Hz) |
|------------------|--------------|
| 10,000,000 | 8,000,000 |
| 16,000,000 | 12,000,000 |
| 20,000,000 | 12,000,000 |
| 24,000,000 | 24,000,000 (the ceiling) |
| 62,500,000 | 24,000,000 |

## Pixels and Coordinates

A **pixel** (picture element) is the smallest dot the screen can color. The 360 by 360 display has \( 360 \times 360 = 129{,}600 \) of them. You address each by two numbers, written (x, y). The x number counts columns from the left, and the y number counts rows from the top. The top-left pixel is (0, 0), x increases to the right, and **y increases downward**, which is the opposite of the graphs you draw in math class. The last pixel is (359, 359) and the center of the round screen is (180, 180).

Only the circle inside the square is visible. The kit stores the center in `config.CENTER_X` and `config.CENTER_Y` (both 180), the edge of the glass in `config.RADIUS` (180), and the largest circle you can see completely in `config.SAFE_RADIUS` (168).

*Worked example.* Is the pixel (20, 20) visible? Its distance from the center is \( \sqrt{(20-180)^2 + (20-180)^2} = \sqrt{25600 + 25600} \approx 226 \), which is larger than the radius 180, so it is hidden under the bezel in the corner. The pixel (180, 20) has distance \( |20 - 180| = 160 \), which is less than 168, so it is safely inside the visible ring.

| Pixel | Distance from center | Visible? |
|-------|---------------------|----------|
| (180, 180) | 0 | Yes, the center |
| (180, 20) | 160 | Yes, inside the safe ring |
| (20, 20) | about 226 | No, in the corner |
| (359, 180) | 179 | Barely, at the very edge |

## RGB565 Color

Each pixel needs a color. A computer makes a color by mixing red, green, and blue light, each with a strength. Many systems use one byte (0 to 255) per color, which takes 3 bytes per pixel. This display uses a smaller format called **RGB565** to save memory and time: it packs a color into just 16 bits (2 bytes).

The name tells you the split. Red gets 5 bits, green gets 6 bits, and blue gets 5 bits, for \( 5 + 6 + 5 = 16 \) bits. Five bits give 32 levels of red, 6 bits give 64 levels of green, and 5 bits give 32 levels of blue, so the format has \( 2^{16} = 65{,}536 \) colors. Green gets the extra bit because human eyes are most sensitive to green.

The kit builds a color with `color565(red, green, blue)`, where each argument runs from 0 to 255. It keeps the top bits of each value and packs them.

```python
def color565(red, green=0, blue=0):
    return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3
```

The `& 0xF8` keeps the top 5 bits of red, `& 0xFC` keeps the top 6 bits of green, and `blue >> 3` drops the low 3 bits of blue so that 5 remain. The shifts `<< 8` and `<< 3` slide each part to its place in the 16-bit number.

*Worked example.* Orange is (255, 128, 0). Red: \( 255 \,\&\, 0xF8 = 0xF8 \), shifted left 8 bits gives 0xF800. Green: \( 128 \,\&\, 0xFC = 0x80 \), shifted left 3 gives 0x0400. Blue is 0. Joining them gives \( 0xF800 + 0x0400 = 0xFC00 \). The driver sends the high byte first, so the two bytes on the wire are FC 00.

| Color | (R, G, B) | RGB565 value | Bytes sent |
|-------|-----------|--------------|------------|
| Red | (255, 0, 0) | 0xF800 | F8 00 |
| Green | (0, 255, 0) | 0x07E0 | 07 E0 |
| Blue | (0, 0, 255) | 0x001F | 00 1F |
| Yellow | (255, 255, 0) | 0xFFE0 | FF E0 |
| Cyan | (0, 255, 255) | 0x07FF | 07 FF |
| Orange | (255, 128, 0) | 0xFC00 | FC 00 |
| Gray | (110, 110, 110) | 0x6B6D | 6B 6D |

Try the mixer to see how the bits move.

#### Diagram: RGB565 Color Mixer

<details markdown="1">
<summary>RGB565 Color Mixer</summary>
Type: microsim
**sim-id:** rgb565-color-mixer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/learning-python/tree/main/docs/sims/rgb-color-mixer<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the 16-bit RGB565 value for 6 given colors, using the packing rule, with at least 5 of 6 correct within two attempts each.

**Prerequisites:** pixel, RGB565, bit masking and shifting (all defined in the section "RGB565 Color" above this block).

**Evidence of Mastery:** For each of the 6 colors the learner types the RGB565 value in hexadecimal. An answer is correct when it equals the RGB565 value column in Content, ignoring upper or lower case and a leading "0x". Mastery is 5 of 6 correct, with up to two attempts per color. Moving the exploration sliders and watching the bits is exploration, not evidence.

**Misconceptions:** (1) RGB565 stores 8 bits per color. (2) The extra bit goes to blue. (3) The low bits of each color are kept and the high bits are dropped.

**Instructional Rationale:** Apply-level calculation of a bit-packed value needs the learner to follow the masking and shifting rule step by step. Seeing the 16 bits change with the three color strengths gives the learner a way to check the arithmetic.

**Content:**

For exploration, the learner sets red, green, and blue strengths from 0 to 255 in steps of 1 (unit: none, default 255, 128, 0). The sim shows the color, the three kept bit groups (5, 6, and 5 bits), and the 16-bit value in binary and hexadecimal.

Challenge colors, in this order:

| # | Color | (R, G, B) | RGB565 value | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | Red | (255, 0, 0) | F800 | Red keeps its top 5 bits (11111) in the top of the number. |
| 2 | Green | (0, 255, 0) | 07E0 | Green keeps its top 6 bits (111111) in the middle. |
| 3 | Blue | (0, 0, 255) | 001F | Blue keeps its top 5 bits (11111) in the bottom. |
| 4 | Yellow | (255, 255, 0) | FFE0 | Red 11111 and green 111111 together make FFE0. |
| 5 | Orange | (255, 128, 0) | FC00 | Green 128 keeps 100000, so the green bits are 0x0400 and red is 0xF800. |
| 6 | Gray | (110, 110, 110) | 6B6D | Red 01101, green 011011, and blue 01101 pack to 0110101101101101. |

**Provenance:** The packing rule is `color565` from `src/kits/study-buddy-base/lib/gc9b72.py`. The values in the table were computed with that function.

**Rules:** value = ((R AND 0xF8) shifted left 8) OR ((G AND 0xFC) shifted left 3) OR (B shifted right 3), with R, G, and B whole numbers from 0 to 255. The result is a number from 0 to 65535 shown as four hexadecimal digits.

**Learner Activity:**

1. The learner drags the red, green, and blue controls and sees the color, the kept bit groups, and the 16-bit value update together.
2. The learner starts the challenges. Challenge 1 shows the color and its (R, G, B) numbers.
3. The learner types the RGB565 value in hexadecimal and submits.
4. If it is wrong the first time, the learner may try once more. After a second wrong answer the sim shows the correct value and the Why text.
5. After challenge 6, the sim shows the score. The learner should notice that the 16-bit value only changes when a color crosses a multiple of 8 (or of 4 for green).

**Feedback:** 6 challenges, fixed order, two attempts each. Correct: "Correct: <Why>". First incorrect: "Not quite. Check which bits each color keeps (5, 6, 5). Try again." Second incorrect: "The value is <answer>: <Why>". A running score "n of 6" is shown.

**Starting State:** The mixer shows orange (255, 128, 0) with its bits, and the question "Which bits does each color keep?"

**Chapter Anchors:** The chapter states that RGB565 uses 5, 6, and 5 bits, has 65,536 colors, and that orange (255, 128, 0) is 0xFC00.
</details>

## The SPI Display Driver

Something has to turn "draw a rectangle" into the right commands and bytes. That something is the **SPI display driver**, a MicroPython module for the display's controller chip. The kit's driver is `lib/gc9b72.py`, and its class `GC9B72` takes the SPI bus and the control pins.

```python
display = gc9b72.GC9B72(spi, dc=Pin(5, Pin.OUT), cs=Pin(6, Pin.OUT),
                        reset=Pin(4, Pin.OUT), backlight=Pin(7, Pin.OUT),
                        rotation=0)
```

You do not write this yourself: `config.init_display()` builds the bus, the pins, and the driver and returns the display object. The `dc`, `cs`, and `reset` arguments are the control wires from Chapter 4, and `rotation` turns the picture in steps of 90 degrees.

The driver's drawing methods all follow one pattern: they set a window on the screen, then stream the pixels for that window.

| Method | What it draws |
|--------|---------------|
| `pixel(x, y, color)` | One pixel |
| `fill_rect(x, y, width, height, color)` | A solid rectangle |
| `fill(color)` | The whole screen in one color |
| `hline`, `vline`, `rect` | Lines and an outline |
| `line(x0, y0, x1, y1, color)` | A slanted line, one pixel at a time |
| `text(font, string, x, y, color, background)` | Characters from a bitmap font |
| `blit_buffer(buffer, x, y, width, height)` | A block of ready-made pixels |

Notice what the table does not contain: a `show()` method. Many small displays hold a picture in the microcontroller's memory and send it all at once when you call `show()`. This driver has no such step. Every call streams its bytes to the display immediately, and the display's own memory keeps the result.

!!! mascot-tip "Print Your Sizes First"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Before you call any draw method with a big rectangle, compute `width * height * 2`. That is how many bytes it will send, and it tells you in one second whether the call will be quick or slow.

## Fonts

The driver has no built-in letters. Text comes from a **font**, which is a module that stores a small picture of each character. The kit includes two.

| Font module | Character size | Characters across the screen |
|-------------|----------------|------------------------------|
| `vga1_8x16` (called `SMALL_FONT`) | 8 by 16 pixels | 45 |
| `vga1_bold_16x32` (called `BIG_FONT`) | 16 by 32 pixels | 22 |

The width of a string is its length times the character width. Test 04's "Hello World!" has 12 letters in the big font, so it is \( 12 \times 16 = 192 \) pixels wide, and the helper `config.centered_text()` computes the left edge as \( (360 - 192) / 2 = 84 \).

## The Frame Buffer Idea

A **frame buffer** is a block of memory that holds one complete picture, one value per pixel. A program draws into the frame buffer first, in memory, and then copies the whole thing to the screen. This approach is popular because drawing in memory is fast and the screen never shows a half-finished picture. MicroPython even includes a `framebuf` module for it.

A frame buffer for our display would hold 360 by 360 pixels at 2 bytes each. Whether that is practical depends on a calculation, and the next two sections do it.

## Frame Size Calculation

The **frame size** is the number of bytes in one complete picture. The **frame size calculation** is a single multiplication:

\[ \text{frame bytes} = \text{width} \times \text{height} \times \text{bytes per pixel} \]

*Worked example.* For our display in RGB565, each pixel takes 2 bytes, so a full frame is

\[ 360 \times 360 \times 2 = 259{,}200 \text{ bytes} \approx 253 \text{ KB} \]

The Pico has about 520 KB of SRAM in total. A frame buffer would claim nearly half of all the memory in the chip, and it must be one unbroken block, which Chapter 2 showed is hard to find on a heap that has been in use. MicroPython itself and the audio buffers need the rest. So this kit does not keep a frame buffer on the Pico at all. The display controller already has the picture in its own memory.

The same formula works for any rectangle, and the answers differ enormously.

| What is drawn | Size | Bytes (RGB565) |
|---------------|------|----------------|
| Full frame | 360 by 360 | 259,200 |
| Full frame at 3 bytes per pixel | 360 by 360 | 388,800 |
| Visible circle only | about 101,788 pixels | about 203,575 |
| Level meter bar in test 06 | 200 by 22 | 8,800 |
| A clock-digit box | 100 by 30 | 6,000 |
| One big-font letter | 16 by 32 | 1,024 |

Use the calculator below to practice the formula and to turn the bytes into a time.

#### Diagram: Frame Size and Update Time Calculator

<details markdown="1">
<summary>Frame Size and Update Time Calculator</summary>
Type: microsim
**sim-id:** frame-size-calculator<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** calculate<br/>
**Learning Objective:** The learner will calculate the number of bytes in a rectangle of pixels and the time to send it over SPI at a given baud rate, for 6 challenges, with at least 5 of 6 correct.

**Prerequisites:** pixel, RGB565, frame size calculation, baud rate (all defined in the sections above this block). The time formula is given in the Rules field and shown to the learner after the first challenge.

**Evidence of Mastery:** For each of the 6 challenges the learner types one number. An answer is correct when it is within the tolerance in the Content table. Mastery is 5 of 6 correct on the first attempt. Changing the exploration controls and watching the totals is exploration, not evidence.

**Misconceptions:** (1) A pixel is one byte. (2) Sending data at 24 MHz means 24 million bytes per second. (3) Time depends on how many pixels are visible rather than how many are sent.

**Instructional Rationale:** Apply-level calculation of bytes and time needs repetition with immediate checking. Linking each answer to the same two formulas shows the learner that every display question reduces to a multiplication and a division.

**Content:**

For exploration, the learner sets the width (1 to 360, step 1, unit pixels, default 360), the height (1 to 360, step 1, unit pixels, default 360), the bytes per pixel (1, 2, or 3, default 2), and the baud rate (8,000,000, 12,000,000, or 24,000,000 bits per second, default 24,000,000). The sim shows the bytes, the bits, and the time in milliseconds.

Challenges, in this order:

| # | Question | Answer | Tolerance | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | Bytes in a full 360 by 360 frame at 2 bytes per pixel | 259200 | exactly | 360 x 360 x 2 = 259,200. |
| 2 | Bytes in the 100 by 30 clock-digit box at 2 bytes per pixel | 6000 | exactly | 100 x 30 x 2 = 6,000. |
| 3 | Bytes in a full 360 by 360 frame at 3 bytes per pixel | 388800 | exactly | 360 x 360 x 3 = 388,800. |
| 4 | Bytes in the 200 by 22 level meter at 2 bytes per pixel | 8800 | exactly | 200 x 22 x 2 = 8,800. |
| 5 | Milliseconds to send the 100 by 30 box at 24,000,000 bits per second | 2.0 | within 0.1 | 6,000 bytes x 8 = 48,000 bits, divided by 24,000,000 is 0.002 s. |
| 6 | Milliseconds to send a full 2-byte frame at 12,000,000 bits per second | 172.8 | within 0.1 | 259,200 x 8 = 2,073,600 bits, divided by 12,000,000 is 0.1728 s. |

**Provenance:** The sizes come from the chapter sections "Pixels and Coordinates" and "Frame Size Calculation," and the 200 by 22 meter is the `METER_WIDTH` by `METER_HEIGHT` of test 06. The times use the formula in Rules and ignore command overhead.

**Rules:** bytes = width x height x bytes per pixel. bits = bytes x 8. time in seconds = bits / baud rate. Milliseconds = seconds x 1000. The sim does not include command bytes or Python overhead, and says so.

**Learner Activity:**

1. The learner changes the width, height, bytes per pixel, and baud rate, and sees the bytes, bits, and milliseconds update.
2. The learner starts the challenges. Challenge 1 is shown.
3. The learner types a number and submits.
4. The sim shows whether it is correct and the Why text, then moves to the next challenge.
5. After challenge 6, the sim shows the score. The learner should notice that a full frame takes about 86 ms of wire time at 24 MHz with the default settings, while the small box takes about 2 ms. The calculator leaves out Python overhead, and says so.

**Feedback:** 6 challenges, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The answer is <answer>: <Why>". The answer is revealed right after each submission, and a running score "n of 6" is shown.

**Starting State:** The calculator shows the full frame at 2 bytes per pixel and 24,000,000 bits per second, with the question "How long does it take to send this?"

**Chapter Anchors:** The chapter states a full frame is 259,200 bytes, a full frame at 24 MHz takes 86.4 ms, the 100 by 30 box is 6,000 bytes, and the 200 by 22 meter is 8,800 bytes.
</details>

## Update Bandwidth and the Full-Frame Update

The size of a frame tells us how much data there is. The **update bandwidth** tells us how fast the link can carry it. For SPI, the bandwidth is simply the baud rate: at 24,000,000 bits per second the display can receive at most 3,000,000 bytes per second, because there are 8 bits in a byte.

A **full-frame update** is a redraw of every pixel. Its minimum time is the bits in a frame divided by the bandwidth.

\[ t = \frac{259{,}200 \times 8}{24{,}000{,}000} = \frac{2{,}073{,}600}{24{,}000{,}000} = 0.0864 \text{ s} = 86.4 \text{ ms} \]

That is the *best case*, with every bit of the link doing useful work. In MicroPython the real time is longer, because each SPI call has overhead and the driver sends the screen in small chunks (`fill_rect` sends 256 pixels at a time, so a full screen needs 507 separate data writes). You can measure your own board with a few lines.

```python
import time
import config

display = config.init_display()
config.set_backlight(True)

start = time.ticks_ms()
display.fill(config.RED)
elapsed = time.ticks_diff(time.ticks_ms(), start)
print("full-screen fill took", elapsed, "ms")
```

Your result will be at least 86 ms. At 86.4 ms per frame, the best possible rate is \( 1000 / 86.4 \approx 11.6 \) full frames per second.

The measurements below are from the board used to test this book. The measured times are about 1.5 times the wire time, and the gap is MicroPython's overhead: every SPI call, and every 256-pixel chunk, costs time on top of the bits.

| You ask for (Hz) | You get (Hz) | Best case (ms) | Measured (ms) | Frames per second |
|------------------|--------------|----------------|---------------|-------------------|
| 8,000,000 | 8,000,000 | 259.2 | 334.6 | 3.0 |
| 12,000,000 | 12,000,000 | 172.8 | 231.9 | 4.3 |
| 20,000,000 | 12,000,000 | 172.8 | 232.0 | 4.3 |
| 24,000,000 | 24,000,000 | 86.4 | 129.4 | 7.7 |

So on this board a full-screen fill at the fastest speed takes about 129 ms, which is 7.7 full frames per second, not 11.6. Your own numbers will differ a little. Run `src/chapters/05-display-basics/01-fill-timing.py` and compare.

*Worked example.* Suppose you want the screen to update 10 times a second with full frames. The bandwidth needed is \( 259{,}200 \times 8 \times 10 = 20{,}736{,}000 \) bits per second, which is 86 percent of the 24 MHz link and leaves almost nothing for anything else. At 30 frames per second you would need 62.2 million bits per second, which is more than twice what the bus can carry. Smooth full-screen video is simply not possible on this link.

Now compare with the audio. The microphone frames from Chapter 3 are 40 ms long, and your program must read each one before the next arrives. A single full-frame update takes at least 86.4 ms, and 129 ms when measured, which is more than three whole audio frames. While the Pico is busy pushing pixels to the display, the microphone keeps producing samples that no one is reading.

| Update | Minimum time at 24 MHz | Measured | Fits in a 40 ms audio frame? |
|--------|------------------------|----------|------------------------------|
| Full frame (259,200 bytes) | 86.4 ms | 129 ms | No, over three frames |
| Level meter (8,800 bytes) | 2.9 ms | not measured | Yes |
| Clock-digit box (6,000 bytes) | 2.0 ms | not measured (a 100 by 32 box: 3.8 ms) | Yes |
| One big-font letter (1,024 bytes) | 0.34 ms | not measured | Yes |

!!! mascot-thinking "Send Only What Changed"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A moving meter changes only a small bar, but a full redraw sends every pixel, and nearly all of them are unchanged. The fix is not a faster bus. It is to stop sending pixels that did not change, and that is the whole subject of the next chapter.

## Clock Face Geometry and Polar to Cartesian

Many round-display designs, including the Chrono Smart Clock family this kit comes from, draw a clock face. A clock face is a good test of coordinate skills, because everything sits on a circle around the center (180, 180). **Clock face geometry** is the set of angles and distances you use to place marks and hands on that circle.

An hour mark sits every 30 degrees, since \( 360 / 12 = 30 \). Angles on a clock are measured from the 12 o'clock position, going clockwise. To place a point at a distance \( r \) from the center and an angle \( \theta \), you convert from polar coordinates (angle and distance) to Cartesian coordinates (x and y). This is **polar to Cartesian** conversion.

\[ x = c_x + r \sin\theta, \qquad y = c_y - r \cos\theta \]

Here \( (c_x, c_y) = (180, 180) \). The minus sign in the second formula is there because y grows downward on the screen, as noted earlier.

*Worked example.* Place the 3 o'clock mark on a ring of radius 150. The angle is 90 degrees, so \( x = 180 + 150 \times 1 = 330 \) and \( y = 180 - 150 \times 0 = 180 \). The 1 o'clock mark has angle 30 degrees: \( x = 180 + 150 \times 0.5 = 255 \) and \( y = 180 - 150 \times 0.866 \approx 50 \).

```python
import math
import config
import shapes

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

for hour in range(12):
    angle = math.radians(hour * 30)
    x = config.CENTER_X + round(150 * math.sin(angle))
    y = config.CENTER_Y - round(150 * math.cos(angle))
    shapes.circle(display, x, y, 4, config.WHITE, config.FILL)
```

The loop visits each hour, turns it into an angle in radians with `math.radians`, converts to x and y, and draws a small filled circle there. Twelve dots appear around the screen.

| Hour | Angle | Position on a radius-150 ring |
|------|-------|-------------------------------|
| 12 | 0 degrees | (180, 30) |
| 1 | 30 degrees | (255, 50) |
| 3 | 90 degrees | (330, 180) |
| 6 | 180 degrees | (180, 330) |
| 9 | 270 degrees | (30, 180) |

## Backlight Control

The display's picture is only visible because of a light behind it, the **backlight**, which is controlled by the BL wire on GP7. `config.set_backlight(True)` drives that pin high to turn the light on, and `False` turns it off. Turning the backlight off does not erase the picture, because the controller still holds it, so turning it back on brings the old image back instantly. That makes it a handy way to implement a screen-off or sleep mode later.

## Color Themes

A **color theme** is a named set of colors used together, for example a background, a text color, and an accent. Putting them in one place lets you restyle the whole display by changing a single line, and it will let each school pick its own look in Chapter 16.

```python
NIGHT = {"background": config.BLACK, "text": config.WHITE, "accent": config.CYAN}
DAY = {"background": config.WHITE, "text": config.BLACK, "accent": config.BLUE}
theme = NIGHT
display.fill(theme["background"])
```

A good theme keeps strong contrast between text and background, so words stay readable in a bright classroom.

## Putting It All Together

You can now describe the screen from the wires up. The Pico sends bytes over an SPI bus at up to 24 million bits per second. The driver wraps those bytes in commands, and each pixel is a 16-bit RGB565 value. A full frame is 259,200 bytes, which takes at least 86.4 ms to send (129 ms when measured), and that is more than three audio frames. No frame buffer lives on the Pico, because it would use about half of all SRAM.

Key takeaways:

- SPI is a clocked serial bus; the display uses the clock and data wires only, at up to 24 MHz, but the rate you ask for may be rounded down.
- A pixel is addressed by (x, y), with (0, 0) at the top left and y increasing downward; the center is (180, 180).
- RGB565 packs a color into 16 bits (5 red, 6 green, 5 blue), giving 65,536 colors.
- The frame size formula is width times height times bytes per pixel, so a full frame is 259,200 bytes.
- The best-case time for a full frame at 24 MHz is 86.4 ms, about 11.6 frames per second; measured on the test board it is 129 ms, about 7.7 frames per second.
- Update bandwidth, not drawing logic, is what limits the screen, so send only what changed.
- Polar to Cartesian conversion places clock marks: \( x = c_x + r\sin\theta \), \( y = c_y - r\cos\theta \).

Test yourself with these two questions, and click each one to reveal its answer.

??? question "How many bytes does a 120 by 50 rectangle take in RGB565, and how long to send it at 24,000,000 bits per second? Click to expand"
    \( 120 \times 50 \times 2 = 12{,}000 \) bytes, which is 96,000 bits. Divided by 24,000,000 that is 0.004 s, or 4 ms.

??? question "Why does the kit not keep a frame buffer on the Pico? Click to expand"
    A full frame buffer is 259,200 bytes, nearly half of the chip's 520 KB of SRAM, and it needs one unbroken block of memory. The display controller already holds the picture, so the Pico can send only the parts that change.

!!! mascot-celebration "From Pixels to Bandwidth"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just calculated that a full frame is 259,200 bytes and takes 86.4 ms at best and 129 ms measured, and you packed colors into RGB565. That arithmetic is the reason the next chapter's region updates exist.

In Chapter 6 we stop redrawing everything and write only the pieces that changed.
