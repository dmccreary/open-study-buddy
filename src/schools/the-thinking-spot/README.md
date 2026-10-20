# The Thinking Spot Study Buddy demo

A one-screen demo for the Study Buddy base kit: the Thinking Spot tree logo
with **"The Thinking Spot Buddy is Live"** under it, on the round display.

Logo artwork: `docs/schools/the-thinking-spot/` (copied from the
thinking-spot-demos repository). Used with permission from Arun Batchu,
co-owner of The Thinking Spot.

| File | What it does |
|---|---|
| `01-buddy-is-live.py` | Draws the logo and the two lines of text. |
| `tree-logo.rgb565` | The logo, 150 x 170, raw RGB565 (51,000 bytes). |
| `tools/logo-to-rgb565.py` | Rebuilds `tree-logo.rgb565` from the JPEG (runs on your computer). |
| `upload.sh` | Sends the kit files and this demo to the Pico, then runs it. |

**Parts needed:** the display only (wire it as in `../../kits/study-buddy-base/`).

```bash
./upload.sh
```

**PASS:** the tree logo is centered near the top, with "The Thinking Spot" in
purple and "Buddy is Live" in green below it, nothing cut off by the bezel.
