---
name: school-generator
description: Generates a school's custom Open Study Buddy - the docs page in docs/schools/{SCHOOL-ID}/ and a MicroPython home-screen mock-up in src/schools/{SCHOOL-ID}/ that draws the school's logo or mascot badge, the buddy's name (like "Groves Buddy"), and three synthetic upcoming events on the kit's round 360x360 display. Works from a school name, a short description, or a link to the school's web site, and from real or invented schools. Use this skill whenever the user wants to add a school, district, club or learning organization to the book, "make a buddy for" a school, mock up a school's study buddy screen, onboard a pilot school, or turn a school scaffold page into a working demo - even if they never say "school-generator".
---

# School Generator

Builds a school's custom study buddy in two places, both keyed by a
kebab-case `{SCHOOL-ID}` (for example `minnetonka-middle-school-east`):

| Folder | What goes there |
|---|---|
| `docs/schools/{SCHOOL-ID}/` | The school's page: profile, mascot or logo, colors, a rendered picture of the buddy's home screen, and (real schools) a to-do list of what to confirm with the school |
| `src/schools/{SCHOOL-ID}/` | `01-{slug}-buddy.py` (MicroPython for the Pico 2 W), the badge as raw RGB565, the tool that makes it, `upload.sh`, `README.md`, and `school.json` |

The home screen is always the same proven layout: a 140 x 140 badge at the
top, the buddy name in the big font, a short accent rule, three
"Day: event" lines, and the school name (or slogan) at the bottom, on the
school's color. Four hand-built schools in `src/schools/`
(`cedar-ridge-high-school`, `minnetonka-middle-school-east`, `glo`,
`the-thinking-spot`) work on real hardware; the templates here are
distilled from them, so stick to that layout rather than inventing a new
one. A new layout would need testing on a real panel.

The work is split so you do the judgment and the scripts do the
mechanics: you research the school and write one `school.json` spec, and
`scripts/build_school.py` writes every file, renders the badge, runs the
demo on a fake display to make a preview PNG, and adds the school to
`docs/schools/index.md` and the `mkdocs.yml` nav.

Run the scripts with the `mkdocs` conda env's `python3` (it has Pillow
and cairosvg).

## Step 1: Pin down the school

Work out three things before writing anything.

**Real or synthetic.** A link to a school site, or the name of a school
that exists, means **real**. A request to invent one ("make up a rural
K-8 school with a heron mascot") means **synthetic**. If you cannot tell,
ask. The difference matters: a real school's page may only state facts
the school published or supplied, while a synthetic school's page can
invent everything (that is its purpose: demos that never touch real
student or school data).

**Facts (real schools).** If you have a link, fetch it (WebFetch) and the
"About" or profile page. Collect what the school publishes about itself:
official name, grades, district, city and state, website, mascot or team
name, and brand colors. The school's own site counts in full, including
its meta description, and a plain reading of it is fine ("four-year
comprehensive high school" means grades 9-12). Facts found only on other
sites (Wikipedia, the state high school league) can go in the profile
only with that source named in the cell. Anything you cannot find is
`*To be provided*`, not a guess.

Brand colors hide in the CSS, which WebFetch strips out. Fetch the raw
homepage HTML with `curl -sL` into a scratch folder and grep it for theme
variables (`--primary-color`, `--secondary-color`, `--brand`) or the
most-used hex values.

**Existing scaffold.** Look in `docs/schools/` and `src/schools/` for the
id first. Several real organizations already have a scaffold page
(profile table and to-do list, no demo). Read it and carry every fact and
checked to-do item into `school.json`, then build with `--force`. If
`src/schools/{SCHOOL-ID}/` already holds hand-built code (any of the four
examples), stop and ask before overwriting it.

## Step 2: Choose the names

| Field | Rule | Example |
|---|---|---|
| `id` | the full name exactly as the school writes it, kebab-cased: no abbreviations, and no added words (Prairie Wind Elementary is `prairie-wind-elementary`, not `...-elementary-school`) | `minnetonka-middle-school-east` |
| `short_name` | what students call it | `MME`, `Groves`, `Cedar Ridge` |
| `buddy_name` | `short_name` + " Buddy", 20 letters max | `Groves Buddy` |
| `program_slug` | kebab-case short name | `mme` -> `01-mme-buddy.py` |
| `footer` | the full name if it is 29 letters or fewer; otherwise a slogan or a shortened name | `Minnetonka Middle School East` |

The limits come from the round glass: the big font is 16 px a letter and
the bottom line sits where the circle is narrow. Screen text must be
plain ASCII, because the bitmap fonts have no curly quotes, accents or
long dashes (they draw as blanks).

## Step 3: Pick the screen colors

Three colors: `background` (fills the screen), `accent` (the weekday
names, the rule, and the bottom line), and `text` (the buddy name and the
events). Use the school's own colors when they are known and say where
they came from in `colors.source`. The background should be the school's
dark color so white or cream text reads well; the build script warns
when text or accent is under 4.5:1 contrast against it, and you should
fix that rather than ship it, because the screen is read from across a
desk.

## Step 4: The badge art

The badge is the most visible part of the screen. In order of preference:

1. **Artwork the user supplied, or that the school's page records
   permission for** (as GLO and The Thinking Spot did). Save it under
   `docs/schools/{SCHOOL-ID}/img/` and point `mascot.source` at it.
2. **Otherwise, draw an original placeholder badge** as an SVG at
   `docs/schools/{SCHOOL-ID}/img/{mascot-name}.svg`. School logos are
   trademarks, so do not download, trace or imitate an official logo
   without permission. Draw something that nods to the school's mascot,
   team name or place (Minnetonka's sailboat nods to the lake and the
   Skippers) in the school colors. For a real school set
   `"placeholder": true` so the docs, code comments and to-do list all say
   it is not an official mark. (A synthetic school's art is its official
   mascot, so leave `placeholder` out.)

Read `references/mascot-art.md` before drawing: it gives the SVG canvas,
the round-badge structure and what survives being shrunk to 140 px.

`mascot.style` picks how the art becomes a badge:

- `plain`: the art is already a round badge (or has a transparent
  background that looks good on the screen color). It is shrunk and laid
  on the background. Use this for SVG badges you draw.
- `disc`: the art goes inside a white disc with an accent ring. Use this
  for supplied art whose colors would vanish into the background, like
  GLO's blue griffin on Groves blue.

## Step 5: Write three synthetic events

Three `[day, event]` pairs for Wednesday, Thursday and Friday (the
examples' convention), each "Day: event" line 32 letters or fewer. Make
them feel like *this* school's week: a quiz in a subject it teaches, a
club or team that fits it, and a social event (Homecoming Dance, Harvest
Dance, Science Fair). They are a mock-up, so they are invented even for
real schools, and the generated docs and code say so. Never use real
student or staff names.

## Step 6: Write school.json and build

Write the spec to `src/schools/{SCHOOL-ID}/school.json`. Every field is
described, with a full example, in `references/school-spec.md`; read it
now. The script adds the boilerplate itself (the "Real organization" or
"Synthetic school" note box, the Study Buddy Demo section, and the
real-school to-do list), so keep `summary` to a description of the school
and do not repeat those disclaimers in it. Then:

```bash
python3 skills/school-generator/scripts/build_school.py . src/schools/{SCHOOL-ID}/school.json
```

Add `--force` only when you are deliberately replacing a scaffold page or
your own earlier output. The script stops with a clear message on a
missing field, text that will not fit, a non-ASCII letter, or a file it
would overwrite; fix the spec and run it again.

## Step 7: Look at the preview, then verify

1. **Read the preview PNG** it prints
   (`docs/schools/{SCHOOL-ID}/img/{slug}-buddy-preview.png`). This is the
   demo program running against a fake display with the kit's real
   fonts, so it is what the device will show. Check that the badge reads
   at 140 px, nothing is cramped, and the colors look like the school.
   If the script printed a bezel WARNING, shorten that line.
2. Run `mkdocs build --strict` (never start or stop `mkdocs serve`; the
   author runs it). The script already added the page to the `nav:` and
   to the table in `docs/schools/index.md`; check both landed sensibly.
3. Report honestly: the preview is a faithful render, but nobody has run
   it on a real Pico yet. Say so, and give the command to try it:
   `cd src/schools/{SCHOOL-ID} && ./upload.sh`.

Mention the published URL with the repo name in it:
`https://dmccreary.github.io/open-study-buddy/schools/{SCHOOL-ID}/`.

## Changing a school later

Edit `school.json` and rebuild with `--force`. Hand edits to generated
files are lost on a rebuild, so put lasting changes in the spec (the docs
page's profile, mascot prose and to-do list all live there). To change
only the drawing, edit the SVG and rebuild.
