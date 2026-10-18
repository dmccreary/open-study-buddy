---
title: "Drawing Directly to Display Regions"
description: "How to write straight to the display one region at a time: drawing windows, dirty regions, text, icons, sprites, animation, image loading, and a school mascot inside the round display mask."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 11:04:58"
version: 1.11
---

# Drawing Directly to Display Regions

## Summary

This chapter teaches students to write directly to the display, one region at a time. They set a drawing window, track dirty regions, and use them to render text, icons, sprites, and animation. It ends by loading images and displaying a school mascot inside the round display mask.

## Concepts Covered

This chapter covers the following 13 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Direct Region Write | 44 |
| Drawing Window | 19 |
| Dirty Region | 17 |
| Text Rendering | 1 |
| Hand Drawing | 1 |
| Icons | 2 |
| Region Layout | 14 |
| Sprite | 1 |
| Animation | 2 |
| Image Loading | 4 |
| School Mascot | 3 |
| Round Display Mask | 1 |
| Display Refresh Rate | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 5: Display Basics: Pixels, Color, and Frame Size](../05-display-basics/index.md)

---

## Send Only What Changed

Chapter 5 ended with a hard number: a full-frame update costs at least 86.4 ms, and your audio frames arrive every 40 ms. The way out is not a faster wire. It is a smarter habit: whenever something on the screen changes, find the smallest rectangle that contains the change, and send only that.

!!! mascot-welcome "Small Boxes, Fast Screen"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter your screen will update a level meter in a few milliseconds and show a picture of a school mascot inside the round glass. Let's listen closely! Fast displays are mostly about knowing what *not* to redraw.

## The Drawing Window

When the display controller receives pixels, it needs to know where they go. The **drawing window** is a rectangle on the screen that the controller is ready to fill. You set it by sending the column range, the row range, and the "write memory" command, which are exactly the three commands you traced in Chapter 4. After that, every pixel you send lands inside the window, filling it in reading order: left to right along the top row, then the next row down, and so on until the window is full.

*Worked example.* Set a window of 4 columns and 2 rows with its top-left at (10, 20). The window covers x from 10 to 13 and y from 20 to 21. You then send 8 pixels. They land like this.

| Pixel sent | Lands at (x, y) |
|-----------|-----------------|
| 1st | (10, 20) |
| 2nd | (11, 20) |
| 3rd | (12, 20) |
| 4th | (13, 20) |
| 5th | (10, 21) |
| 6th | (11, 21) |
| 7th | (12, 21) |
| 8th | (13, 21) |

The driver hides these steps inside its private `_set_window()` method. You will rarely call it yourself, but you must know the reading order, because it tells you how to arrange pixels in a buffer.

## Direct Region Write

A **direct region write** is the technique built on that window: set the window to the rectangle you want, then stream all of its pixels in one go. Compare the cost of doing the same job two ways. To paint a 100 by 30 box one pixel at a time, you call `pixel()` 3,000 times, and each call sends 13 bytes (Chapter 4), a total of 39,000 bytes. To paint it with a single `fill_rect()`, the driver sets the window once (11 bytes of commands and ranges) and then sends 3,000 pixels at 2 bytes each, a total of 6,011 bytes, about one-sixth as much.

| Method | Calls | Bytes on the wire | Minimum time at 24 MHz |
|--------|-------|-------------------|------------------------|
| `pixel()` 3,000 times | 3,000 | 39,000 | 13 ms |
| `fill_rect()` once | 1 | 6,011 | 2.0 ms |
| `blit_buffer()` once | 1 | 6,011 | 2.0 ms |

For a region with different colors in it, you build the pixels in a buffer and send them with `blit_buffer(buffer, x, y, width, height)`. The buffer is a `bytearray` of `width * height * 2` bytes, ordered row by row, with each color as two bytes, high byte first.

```python
width, height = 4, 2
pixels = bytearray(width * height * 2)

for i in range(width * height):
    color = config.RED if i % 2 == 0 else config.BLUE
    pixels[i * 2] = color >> 8
    pixels[i * 2 + 1] = color & 0xFF

display.blit_buffer(pixels, 10, 20, width, height)
```

The loop alternates red and blue pixels, splits each 16-bit color into its two bytes, and sends the whole 4 by 2 block with one call.

!!! mascot-warning "A Buffer of the Wrong Size"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If the buffer holds fewer bytes than `width * height * 2`, the last pixels of the window are never filled. If it holds more, the extra pixels wrap into the wrong place. When a picture looks sheared or has stripes, print `len(buffer)` and compare it with `width * height * 2`.

## Dirty Regions

A **dirty region** is a rectangle whose content on the screen is out of date because the underlying data changed. Updating the screen then becomes a loop of three simple steps: remember what you drew last time, compare it with what you should draw now, and redraw only the regions where the two differ.

The kit's test 06 does this for its level meter. It keeps `drawn_width`, the width of the bar currently on screen, and only redraws when the new width differs by at least 2 pixels.

```python
width = int(METER_WIDTH * meter_fraction(bits))
if abs(width - drawn_width) >= 2:
    display.fill_rect(METER_X, METER_Y, width, METER_HEIGHT, color)
    display.fill_rect(METER_X + width, METER_Y,
                      METER_WIDTH - width, METER_HEIGHT, TRACK)
    drawn_width = width
```

The `if` is the dirty test. If the meter has not moved by 2 pixels, nothing is sent at all. Otherwise two rectangles are drawn: the filled bar and the empty track after it. The 2-pixel margin stops the bar from flickering on tiny changes.

The status line in the same test uses a different dirty test. It stores whether the room was loud on the last frame (`heard`) and redraws the words "I hear you!" or "Listening..." only when that value flips. Most frames, the status region sends zero bytes.

!!! mascot-thinking "Remember, Compare, Redraw"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Dirty-region code always has a memory: the last value drawn. Without it, the program cannot tell a change from a repeat. When your display flickers or runs slowly, ask first: what is this code remembering, and when does it compare?

## Text Rendering

**Text rendering** draws characters from a font into the window. The driver's `text(font, string, x, y, color, background)` method draws each glyph with its background color, so a glyph is an opaque rectangle. That means drawing new text over old text covers the old letters, but only inside the cells the new text uses.

If the new text is shorter than the old text, the leftover letters stay on screen. The kit solves this by padding every string to a fixed width, as in this helper from tests 06 and 07.

```python
def put(text, y, font, color, width):
    config.centered_text(display, font, text.center(width), y, color)
```

The `str.center(width)` method adds spaces on both sides until the string is `width` characters long. Drawing "I hear you!" and "Listening..." both at width 14 means the second one fully erases the first, with no separate erase step.

!!! mascot-tip "Pad the Text, Skip the Erase"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Pick the longest string a text region will ever show, and pad every string to that many characters. One `text()` call then draws and erases in a single pass, and the region never needs a separate clearing step.

## Hand Drawing, Icons, and Sprites

### Hand Drawing

**Hand drawing** means building a picture from shapes you place yourself in code, instead of loading a stored image. The kit's `shapes.py` provides the shapes: `circle`, `ring`, `ellipse`, `poly`, and `triangle`. Everything is built from horizontal runs, because on this display one `hline` of forty pixels costs far less than forty calls to `pixel()`. A face made of two filled circles for eyes and a bottom-half ellipse arc for a smile is a few lines of code, and it sends far fewer bytes than a stored image of the same size would.

### Icons

An **icon** is a small, simple picture that stands for an idea: a Wi-Fi symbol, a microphone, a speaker. Icons live in fixed boxes, commonly 24 by 24 or 32 by 32 pixels. A 32 by 32 icon is \( 32 \times 32 \times 2 = 2{,}048 \) bytes, so it redraws in under 1 ms. The best habit is to draw each icon once into a buffer and then `blit_buffer()` it whenever its state changes. A status icon's dirty test is the simplest of all: redraw only when the state flips from, say, "connected" to "disconnected."

### Sprites

A **sprite** is a small image that you place and move around, such as a mascot's eye or a bouncing dot. In the kit, `shapes.sprite(width, height, background)` makes a blank buffer, `sprite_pixel()` sets a pixel in it, and `display.blit_buffer()` stamps it on the screen.

The plain `blit_buffer()` is opaque: it paints the sprite's whole rectangle, including its background. To make part of the sprite transparent, the kit offers `shapes.blit_keyed()`, which skips every pixel equal to a *key color*, black by default. It is slower because it sends the sprite in runs of visible pixels, so use it for small sprites and prefer plain `blit_buffer()` when the sprite can have a solid background.

```python
dot = shapes.sprite(16, 16, config.BLACK)
for y in range(16):
    for x in range(16):
        if (x - 8) ** 2 + (y - 8) ** 2 <= 49:
            shapes.sprite_pixel(dot, 16, x, y, config.CYAN)
shapes.blit_keyed(display, dot, 100, 100, 16, 16)
```

The loops build a cyan disc of radius 7 inside a black 16 by 16 sprite. The `blit_keyed` call then stamps only the cyan pixels, leaving whatever was behind the dot visible. A 16 by 16 sprite is 512 bytes.

## Animation

**Animation** is a sequence of small updates that look like motion. On this display, the trick is the same as before: do not redraw the picture, redraw only what moved. For a ball that slides to the right by 4 pixels each frame, the pixels that change are a 4-pixel strip left behind by the ball and the new pixels it covers.

```python
BALL = 20
y = 90
x = 40
display.fill_rect(x, y, BALL, BALL, config.CYAN)

while x < 280:
    display.fill_rect(x, y, 4, BALL, config.BLACK)      # erase the strip
    x += 4
    display.fill_rect(x + BALL - 4, y, 4, BALL, config.CYAN)   # new strip
    time.sleep_ms(20)
```

Each pass erases a 4 by 20 strip on the left and fills a 4 by 20 strip on the right, 80 pixels each, or 160 bytes each, instead of the whole 20 by 20 box. This ball is a square, and a round ball needs `shapes.circle`, but the dirty-region idea is identical.

The picture changes at most as fast as your loop and your bandwidth allow. Frames that arrive faster than the eye can follow, around 10 to 15 per second for simple motion, are enough to look smooth.

## Region Layout

A **region layout** is the plan that divides the screen into named rectangles, each updated on its own. With a layout, "the time changed" becomes "redraw the time region and nothing else." A layout for the Study Buddy needs five regions. The positions below were chosen so that all four corners of every rectangle are inside the safe circle of radius 168 around (180, 180).

| Region | x | y | Width | Height | Bytes (RGB565) | Min time at 24 MHz |
|--------|---|---|-------|--------|----------------|--------------------|
| Status bar | 120 | 30 | 120 | 20 | 4,800 | 1.6 ms |
| Time | 130 | 72 | 100 | 32 | 6,400 | 2.1 ms |
| Mascot | 148 | 112 | 64 | 64 | 8,192 | 2.7 ms |
| Spectrum | 80 | 190 | 200 | 40 | 16,000 | 5.3 ms |
| Agent message | 60 | 240 | 240 | 32 | 15,360 | 5.1 ms |
| All five together | | | | | 50,752 | 16.9 ms |

Redrawing *every* region costs 50,752 bytes, about 16.9 ms, which is roughly five times cheaper than the 259,200-byte full frame. In practice most frames redraw only one or two regions, and the spectrum region alone costs 5.3 ms.

Now apply the dirty-region rule to six events. For each, decide which regions need redrawing.

#### Diagram: Dirty Region Planner

<details markdown="1">
<summary>Dirty Region Planner</summary>
Type: microsim
**sim-id:** dirty-region-planner<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** apply<br/>
**Learning Objective:** The learner will apply the dirty-region rule to 6 device events by selecting exactly the regions that must be redrawn for each, with at least 5 of 6 correct on the first attempt.

**Prerequisites:** dirty region, region layout, direct region write (all defined in the sections above this block, including the five regions in the table "Region Layout").

**Evidence of Mastery:** For each of the 6 events the learner selects zero or more of the five regions. A selection is correct when the set of selected regions equals the Dirty regions column in Content. Mastery is 5 of 6 correct on the first attempt. Viewing the region sizes before answering is allowed and is not scored.

**Misconceptions:** (1) Any event requires a full-screen redraw. (2) A region should be redrawn on every frame whether or not its content changed. (3) Changing the mascot's pose does not require redrawing the mascot region.

**Instructional Rationale:** Apply-level use of a rule requires the learner to carry it out on new cases. Deciding the set of dirty regions for each event, and then seeing the byte cost of the choice next to the cost of a full frame, ties the rule to the bandwidth reason for it.

**Content:**

The sim shows the five regions of the table "Region Layout" with their byte sizes: Status bar 4,800; Time 6,400; Mascot 8,192; Spectrum 16,000; Agent message 15,360. A full frame is 259,200 bytes.

Events, in this order:

| # | Event shown to the learner | Dirty regions | Bytes sent | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | A new audio frame arrives and the spectrum values are different from the last frame. | Spectrum | 16,000 | Only the spectrum content changed. |
| 2 | The clock minute changes from 12:34 to 12:35. | Time | 6,400 | Only the clock digits changed. |
| 3 | The Pico connects to Wi-Fi and the status icon changes. | Status bar | 4,800 | The icon lives in the status bar. |
| 4 | The student presses Mode and the device enters Listening mode, which changes the mascot's pose and the status text. | Status bar, Mascot | 12,992 | Both the pose and the status text changed. |
| 5 | The agent replies "Test on Friday" and the mascot switches to a speaking pose. | Agent message, Mascot | 23,552 | The words and the pose changed. |
| 6 | A silent room produces an audio frame whose spectrum values equal the last frame. | none | 0 | Nothing changed, so nothing is sent. |

**Provenance:** The regions and bytes come from the chapter table "Region Layout." The events are illustrative, and the sim labels them "illustrative."

**Rules:** A region is dirty when the content shown in it would be different after the event. The bytes sent are the sum of the sizes of the dirty regions. The full frame is 259,200 bytes. The saving shown is 259,200 minus the bytes sent.

**Learner Activity:**

1. The learner reads event 1 and selects the regions that must be redrawn (none is allowed).
2. The learner submits.
3. The sim shows the correct set, the bytes sent, how that compares to 259,200, and the Why text.
4. The learner continues through event 6, then sees the score.
5. The learner should notice that event 6 sends nothing and that event 5 is the most expensive at 23,552 bytes, still far less than a full frame.

**Feedback:** 6 events, fixed order, one attempt each. Correct: "Correct: <Why> (<bytes> bytes, <percent of full frame>%)". Incorrect: "Not quite. The dirty regions are <set>: <Why>". The correct set is revealed after each submission, and a running score "n of 6" is shown.

**Starting State:** The five regions are shown unselected with their sizes, and event 1 is shown with the question "Which regions must be redrawn?"

**Chapter Anchors:** The chapter states that the five regions are the status bar, time, mascot, spectrum, and agent message; that redrawing all five costs 50,752 bytes (about 16.9 ms); and that a full frame is 259,200 bytes.
</details>

## The Round Display Mask

The **round display mask** is the shape of the visible area: a circle of radius 180 centered on (180, 180), or radius 168 for the area that is always fully visible. A rectangle that pokes out of the circle wastes pixels on the hidden corners.

For any row, you can compute the width of the visible span from the circle equation. A row at vertical distance \( dy \) from the center has half-width \( \sqrt{r^2 - dy^2} \).

*Worked example.* Row y = 20 is 160 pixels above the center. With r = 168 the half-width is \( \sqrt{168^2 - 160^2} = \sqrt{2624} \approx 51 \). So only the x range from about 129 to 231 (102 pixels) is visible on that row, not the full 360. Content placed near the top or bottom of the screen has to be narrow. Content near the middle can be wide.

| Row y | Distance from center | Visible x range (r = 168) | Visible width |
|-------|---------------------|---------------------------|---------------|
| 20 | 160 | 129 to 231 | 102 |
| 60 | 120 | 62 to 298 | 235 |
| 120 | 60 | 23 to 337 | 314 |
| 180 | 0 | 12 to 348 | 336 |

You apply the mask in two ways: by choosing region rectangles whose corners fall inside the circle (as the layout table does), and by shaping images so that their corners are black, as the next section does.

## Image Loading

An image is just a long list of RGB565 pixels, so **image loading** means reading those bytes from a file and sending them to a window. The work splits between your computer and the Pico. On your computer, a small Python script resizes the picture, blacks out everything outside a circle, and writes the pixels as raw RGB565 bytes, high byte first. On the Pico, a loader reads the file in chunks and sends each chunk with `blit_buffer()`.

The conversion script uses the Pillow imaging library (`pip install pillow`) and runs on your computer, not on the Pico.

```python
import sys
from PIL import Image, ImageDraw

def convert(src, dst, size=120):
    image = Image.open(src).convert("RGBA")
    image.thumbnail((size, size))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    offset = ((size - image.width) // 2, (size - image.height) // 2)
    canvas.paste(image, offset, image)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    black = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    canvas = Image.composite(canvas, black, mask)
    rgb = canvas.convert("RGB").tobytes()
    with open(dst, "wb") as out:
        for i in range(0, len(rgb), 3):
            r, g, b = rgb[i], rgb[i + 1], rgb[i + 2]
            value = (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3
            out.write(value.to_bytes(2, "big"))

convert(sys.argv[1], sys.argv[2])
```

The function shrinks the picture to fit in a 120 by 120 square, centers it on black, keeps only the pixels inside the inscribed circle, and writes each pixel with the same packing rule as `color565`. A 120 by 120 image makes a file of \( 120 \times 120 \times 2 = 28{,}800 \) bytes. Copy it to the Pico with `mpremote fs cp sage.rgb565 :sage.rgb565`.

The loader on the Pico reads the file a few rows at a time so that it never holds the whole image in memory.

```python
def show_image(display, path, x, y, size, rows_per_chunk=10):
    chunk = bytearray(size * rows_per_chunk * 2)
    with open(path, "rb") as f:
        for row in range(0, size, rows_per_chunk):
            f.readinto(chunk)
            display.blit_buffer(chunk, x, y + row, size, rows_per_chunk)
```

The buffer `chunk` holds 10 rows, which is \( 120 \times 10 \times 2 = 2{,}400 \) bytes. `readinto` fills it from the file with no new allocation, and `blit_buffer` places it at the right row. Twelve chunks cover the 120 rows. The size must divide evenly by `rows_per_chunk`, which it does here. A call such as `show_image(display, "sage.rgb565", 120, 120, 120)` centers the image on the screen.

Loading reads 28,800 bytes from flash and sends them over SPI, a minimum of \( 28{,}800 \times 8 / 24{,}000{,}000 \approx 9.6 \) ms. You do it once when a screen appears, not every frame.

## The School Mascot

A **school mascot** is the character that gives each school's device its own identity. In this book the base character is Sage the owl, and Chapter 16 lets each school swap in its own. A mascot image is just an image like the one above, so the same pipeline applies: choose a picture, convert it, copy it, show it in the mascot region.

A mascot needs three design choices for a round display.

- **Keep the important part in the middle.** Faces near the corners of the square image are cut by the mask.
- **Use a plain background.** A flat color around the character compresses the information and avoids visual noise on a small screen.
- **Keep it small.** The layout above gives the mascot a 64 by 64 region (8,192 bytes), and a larger 120 by 120 image costs 28,800 bytes. Bigger pictures are fine for a splash screen, but they should not be redrawn every frame.

## Display Refresh Rate

The **display refresh rate** is how many times per second the picture on the screen is updated, measured in hertz. Two different rates are easy to confuse. The panel itself continuously redraws the glass from the controller's memory at a fixed rate that you cannot change. The rate that matters for animation is the *update* rate: how often your program sends new pixels.

The update rate is limited by the regions you send. If the spectrum region costs at least 5.3 ms, the display could in theory be updated about 190 times a second, but the audio frame arrives every 40 ms, so the useful rate is 25 per second. That is more than enough to look smooth. Python overhead and time spent on other jobs bring the real number lower.

| Update | Minimum time | Theoretical maximum rate |
|--------|--------------|--------------------------|
| Full frame | 86.4 ms | 11.6 per second |
| Spectrum region | 5.3 ms | 188 per second |
| Time region | 2.1 ms | 469 per second |
| Audio frame cadence | 40 ms | 25 per second |

## Putting It All Together

You now draw the way a fast embedded display has to: set a window, stream only the pixels that changed, and remember what is on screen so the next frame can tell what changed. Text pads itself to erase old letters, icons and sprites live in small buffers, and images arrive from flash in chunks.

Key takeaways:

- A drawing window is a rectangle that receives pixels in reading order; a direct region write sets the window and then streams the pixels in one go.
- A single `fill_rect` of 100 by 30 pixels sends about one-sixth of the bytes of 3,000 `pixel()` calls.
- A dirty region is a rectangle that is out of date; remember what you drew, compare, and redraw only where it differs.
- Pad text to a fixed width so that one call draws and erases.
- A region layout names the rectangles; the five-region layout costs 50,752 bytes if all are redrawn, 16.9 ms, versus 86.4 ms for a full frame.
- The round display mask means rectangles near the top or bottom must be narrow; images are masked to a circle when converted.
- Image loading reads raw RGB565 from flash a few rows at a time and sends each chunk with `blit_buffer`.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "A string shows 'Listening...' and is then replaced by 'Done', but part of the old word is still visible. What went wrong and how do you fix it? Click to expand"
    The new string is shorter, so only its own cells were redrawn. Pad both strings to the same fixed width with `str.center(width)`, so the second call covers every cell the first one used.

??? question "Why is the mascot region 8,192 bytes and not 8,192 pixels? Click to expand"
    The region is 64 by 64 pixels, which is 4,096 pixels, and each RGB565 pixel takes 2 bytes, so \( 4096 \times 2 = 8{,}192 \) bytes.

!!! mascot-celebration "Regions, Not Frames"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned to set a drawing window, track dirty regions, lay out five independent regions that cost 16.9 ms instead of 86.4 ms, and load a masked mascot from flash. Your screen can now keep up with your microphone.

In Chapter 7 we give the device its hands: three buttons, a state machine, and device modes.
