# Minnetonka Middle School East Study Buddy demo

A one-screen demo for the Study Buddy base kit: the Lake Minnetonka sailboat
badge at the top, **"MME Buddy"** under it, and a mock-up of the week's
upcoming events on a Minnetonka blue round display.

Minnetonka Middle School East is a real school (see
`docs/schools/minnetonka-middle-school-east/`). Its website shows no mascot,
so the sailboat is a **placeholder** drawn for this demo, not an official
school mark. The colors match the Minnetonka Public Schools website (blue
`#003698`, light blue `#8BB4FD`). The three events are a mock-up typed into
the demo, not read from the school calendar.

| File | What it does |
|---|---|
| `01-mme-buddy.py` | Draws the badge, the title, three events and the school name. |
| `sailboat-140.rgb565` | The sailboat badge, 140 x 140, raw RGB565 (39,200 bytes). |
| `tools/mascot-to-rgb565.py` | Rebuilds `sailboat-140.rgb565` from the PNG (runs on your computer). |
| `upload.sh` | Sends the kit files and this demo to the Pico, then runs it. |

**Parts needed:** the display only (wire it as in `../../kits/study-buddy-base/`).

```bash
./upload.sh
```

**PASS:** the sailboat badge (white sails, navy hull, blue waves) is centered
near the top of a Minnetonka blue screen. "MME Buddy" is white below it, then
three event lines with the day in light blue and the event in white:

```
Wednesday: Science Quiz
Thursday: Robotics Club
Friday: Book Report Due
```

and "Minnetonka Middle School East" in light blue at the bottom, nothing cut
off by the bezel.
