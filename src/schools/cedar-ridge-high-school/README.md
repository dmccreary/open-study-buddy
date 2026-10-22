# Cedar Ridge Study Buddy demo

A one-screen demo for the Study Buddy base kit: Gale the Griffin at the top,
**"Cedar Ridge Buddy"** under it, and a mock-up of the week's upcoming events
on the round display.

Cedar Ridge High School is a synthetic school; its mascot, colors and calendar
live in `docs/schools/cedar-ridge-high-school/`. The three events on this
screen are typed into the demo, not read from `events.json`.

| File | What it does |
|---|---|
| `01-upcoming-events.py` | Draws the mascot, the title, three events and the slogan. |
| `griffin-140.rgb565` | The mascot badge, 140 x 140, raw RGB565 (39,200 bytes). |
| `tools/mascot-to-rgb565.py` | Rebuilds `griffin-140.rgb565` from the PNG (runs on your computer). |
| `upload.sh` | Sends the kit files and this demo to the Pico, then runs it. |

**Parts needed:** the display only (wire it as in `../../kits/study-buddy-base/`).

```bash
./upload.sh
```

**PASS:** the griffin badge is centered near the top on a dark green screen,
"Cedar Ridge Buddy" is gold below it, then three event lines with the day in
gold and the event in cream:

```
Wednesday: Calculus Quiz
Thursday: Coding Club
Friday: Homecoming Ultimate Game
```

and "Aim high. Listen closely." at the bottom, nothing cut off by the bezel.
