# GLO Study Buddy demo

A one-screen demo for the Study Buddy base kit: the GLO Coding Club griffin
in a round badge at the top, **"Groves Buddy"** under it, and a mock-up of the
week's upcoming events on a Groves blue round display.

Groves Learning Organization is a real organization (see
`docs/schools/glo/`). The griffin artwork comes from the GLO Coding Club site
(`glo-coding-club` repository, `docs/img/mascot/welcome.png`), and the colors
match groveslearning.org (blue `#00649B`, cyan `#01BADE`). The three events
are a mock-up typed into the demo, not read from a GLO calendar.

| File | What it does |
|---|---|
| `01-glo-buddy.py` | Draws the badge, the title, three events and the organization name. |
| `griffin-140.rgb565` | The griffin badge, 140 x 140, raw RGB565 (39,200 bytes). |
| `tools/mascot-to-rgb565.py` | Rebuilds `griffin-140.rgb565` from the PNG (runs on your computer). |
| `upload.sh` | Sends the kit files and this demo to the Pico, then runs it. |

**Parts needed:** the display only (wire it as in `../../kits/study-buddy-base/`).

```bash
./upload.sh
```

**PASS:** the griffin is waving from a white disc with a cyan ring, centered
near the top of a Groves blue screen. "Groves Buddy" is white below it, then
three event lines with the day in cyan and the event in white:

```
Wednesday: Coding Club
Thursday: Calculus Quiz
Friday: Harvest Dance
```

and "Groves Learning Organization" in cyan at the bottom, nothing cut off by
the bezel.
