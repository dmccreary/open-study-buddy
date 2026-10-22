# Drawing a placeholder badge

The badge is shown at 140 x 140 pixels on a screen read from arm's
length, so it has to work as an icon, not an illustration. The model to
copy is `docs/schools/minnetonka-middle-school-east/img/sailboat.svg`;
read it before drawing your own.

## Canvas and structure

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 360" width="360" height="360"
     role="img" aria-labelledby="t d">
  <title id="t">Harbor Point heron, mascot of Harbor Point Middle School</title>
  <desc id="d">One sentence describing the badge.</desc>
  <defs><clipPath id="scene"><circle cx="180" cy="180" r="160"/></clipPath></defs>

  <!-- rings: dark outer ring, light inner ring -->
  <circle cx="180" cy="180" r="180" fill="#DARK"/>
  <circle cx="180" cy="180" r="170" fill="#FFFFFF"/>

  <g clip-path="url(#scene)" stroke-linejoin="round" stroke-linecap="round">
    <!-- background (sky, field, water) then the subject -->
  </g>
</svg>
```

- 360 x 360 viewBox, everything inside a circle. The corners are left
  transparent so the `plain` badge style lays them on the screen color.
- Two rings (a dark outer ring and a white or light inner ring) separate
  the badge from the background, so it reads even when the scene shares
  the screen color.
- Clip the scene to `r="160"`.

## What survives 140 px

- **One subject, big.** The subject should fill about two thirds of the
  circle. A sailboat, a heron, a paw print, an acorn: one shape.
- **Thick outlines.** Stroke widths of 5-7 at 360 px become 2-3 px on the
  device; a 1 px line at 360 disappears.
- **Flat color, 4-6 colors**, all from the school palette plus white. No
  gradients, filters, blur or drop shadows; they turn to mud in RGB565.
- **At most one or two letters** (Minnetonka's sail has an "E"), at 26 px
  or more. The buddy name is already printed under the badge, so the
  badge never needs the school's name in it.
- No embedded raster images and no web fonts: the SVG must render the
  same in cairosvg and the browser.

## Ideas that are safe to draw

Base the subject on something the school is known for that is not its
logo: the team name (Skippers -> sailboat), the local landscape (lake,
bluffs, prairie, pine), the school's namesake, or a subject it is known
for (a gear for a STEM school). Never trace or recreate the school's
actual logo or a pro or college team's mark.

When the team name is shared with famous marks (Trojans, Spartans,
Wildcats, Bulldogs), pick a different angle on the same idea instead of
the usual helmet or snarling head: Wayzata's Trojans became a wooden
Trojan horse on wheels, which no well-known logo uses. A friendly
full-body animal is safer than an aggressive head profile.

## Check it

To see the badge alone while you draw, before any build:

```bash
cairosvg docs/schools/{SCHOOL-ID}/img/{name}.svg -o /tmp/badge-140.png -W 140 -H 140
```

and read the PNG. Then `build_school.py` renders the SVG to `img/{name}-360.png` and the badge
to the preview. Look at the preview: if the subject is hard to
recognize at that size, simplify it (fewer details, thicker strokes,
bigger shape) and rebuild with `--force`.
