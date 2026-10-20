# Cover Image Prompt

Please generate a professional-quality cover image for this textbook.
This image will be used in social media previews and must follow the
formatting guidelines for an Open Graph image preview.

**Required specifications:**
- Format: PNG
- Wide-landscape format
- Size: 1200x630 pixels (1.91:1 aspect ratio)
- This is the Open Graph standard for social media previews

The image has four layers, back to front: background montage, color
treatment, mascot, and title text.

## Subject & Tone

Open Study Buddy is a hands-on textbook about building a low-cost, fully open,
personal AI study-buddy device from a Raspberry Pi Pico 2 W, a round 360 x 360
color display, a digital microphone, a small speaker, and three push buttons.
The device listens, shows what it heard, speaks answers aloud, and announces
school tests and project due dates. The intended audience is high school
students (grades 9-12), coding clubs, and the teachers who run school maker
programs. The visual tone should be friendly, modern, and technical: the
excitement of a student maker project that actually works, not the cold look of
corporate AI.

## Title

Place **Open Study Buddy** in the center of the image, in a clean, highly
legible, bold sans-serif font. Use a white font color with a subtle drop shadow
or a dark navy scrim behind it so it stays readable against the busy montage
background. Add a small subtitle line beneath it in a lighter weight:
"Build your own open AI agent with MicroPython". Do not shrink the title to fit;
instead simplify the background directly behind the text.

## Background Montage

Arrange a montage of the following 8 concepts around the title, each rendered
in a consistent flat-vector illustration style (see Style below) so the
composition reads as one image rather than a collage of unrelated styles:

1. **The Open Study Buddy device** (hero element, right of the title) - a small
   desk device whose face is a large round color display showing a friendly
   glowing "listening" ring and a short text bubble, with a tiny circuit board
   and three small round push buttons (Mode, Up, Down) at its base.
2. **Raspberry Pi Pico 2 W** - a small green microcontroller board with a
   silver Wi-Fi module, drawn top-down with gold pads along both edges.
3. **FFT audio spectrum** - a row of glowing vertical bars of varying height in
   teal-to-amber gradient, like a live equalizer, sitting on a dark baseline.
4. **Sound waveform** - a smooth blue sine wave with evenly spaced sample dots
   along it, showing sampling.
5. **INMP441 microphone and speaker** - a tiny round microphone breakout board
   next to a small speaker cone, with curved sound-wave arcs between them.
6. **MQTT school alert** - a school-building icon sending dotted lines to three
   small devices, with a speech-bubble badge reading "TEST TOMORROW".
7. **School calendar** - a monthly calendar page with two dates circled in
   orange, one marked with a small test-paper icon, one with a flag.
8. **Privacy shield with microphone** - a shield containing a microphone with a
   small mute slash and a green "listening" indicator dot, signaling
   consent-first design.

Optionally add a few faint circuit-trace lines and Wi-Fi arcs connecting the
elements, kept very low contrast so they do not add clutter.

## Mascot

Place the book's mascot, **Sage the Owl**, in the lower-left corner, sized so it
does not overlap the title text. Sage is a small, compact, flat-vector cartoon
owl with a slate-blue body (#2E6DA4), a cream chest, small round
orange-framed glasses, orange beak and feet (#F5871F), bright curious eyes, and
a warm closed-mouth smile. Sage is roughly two heads tall and has a transparent
background. Pose: welcoming, with one wing slightly raised in greeting. Use
the existing reference image `docs/img/mascot/welcome.png` for consistency.

## Style & Composition

- Illustration style: flat vector with clean lines and bold simple shapes,
  matching Sage's art style. Apply it to every montage element.
- Color palette: deep navy and slate blue (matching Sage) for the background,
  with teal accents and warm orange (#F5871F) highlights; small touches of
  Pico green on the circuit board.
- Lighting/mood: bright and optimistic, with a soft glow around the device
  display and the spectrum bars, as if the device is switched on.
- Composition: title centered, montage elements arranged in a loose ring around
  it with the device as the largest element, Sage in the lower-left, generous
  negative space immediately behind the title so it stays readable. Keep all
  important content inside a safe margin of about 5% from each edge, since
  social platforms crop the edges.

## Avoid

- Do not render dense paragraphs of illegible text anywhere in the image. The
  only readable text should be the title, the subtitle, and the short
  "TEST TOMORROW" badge.
- Avoid generic stock-photo cliches (handshakes, isolated lightbulbs, people
  pointing at whiteboards, glowing human-shaped robots or brains).
- Avoid photorealistic human faces; show no students' faces.
- Do not use any commercial AI product logos or trademarks.
- Do not let montage elements visually compete with or overlap the title.
- Do not draw the round display as a rectangle; it must be a circle.
