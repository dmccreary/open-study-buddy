# Mascot Image Prompt: Gale the Griffin

Self-contained prompts for generating the Cedar Ridge High School mascot with an AI image
tool. Paste the **Main Prompt** and the **Negative Prompt** as they are; they do not depend on
any other file. The character facts match [mascot.md](mascot.md).

## Where the Image Is Used

The image is drawn on the kit's **round 360 × 360 pixel color display**, so it must stay clear at
a small size and on a phone-sized screen. That drives three rules in the prompt: bold outlines,
flat colors with no gradients, and one simple subject centered in a circle.

## Main Prompt

```text
A friendly high-school sports mascot logo: a griffin (eagle head and lion body) in a bold, flat
vector cartoon style, shown as a round badge. Show the griffin's head and upper chest, facing
three-quarters to the right, with a confident, upbeat, slightly competitive expression and a
small proud smile. Cream-white feathered eagle head, a strong gold hooked beak, large expressive
eyes with a determined eyebrow, pointed gold ear tufts, and a feathered chest. Behind the
head, two spread wings in forest green with gold feather tips. A hint of a gold lion mane at the
neck. Thick, clean, dark-green outlines of even weight. Flat solid colors with simple cel
shading only, no gradients, no textures, no fine detail. Color palette limited to forest green
(#1F5D3A), gold (#F2B632), cream (#FFF1D0), dark green outline (#0F3320), and deep gold
(#C98A00) for feather detail. The subject sits inside a circle with a gold ring border, on a
solid forest-green background. Centered composition with generous padding so nothing touches
the edge of the circle. Square 1:1 image, high resolution, sports-team mascot style, readable
at 64 pixels wide.
```

## Negative Prompt

```text
text, letters, words, numbers, watermark, signature, realistic, photograph, 3D render,
gradient, glow, drop shadow, fine texture, busy background, extra limbs, extra heads, multiple
characters, scary, aggressive, snarling, blood, weapon, human body, cropped, off-center, blurry,
low contrast
```

## Settings

| Setting | Value |
|---------|-------|
| Aspect ratio | 1:1 (square) |
| Size | 1024 × 1024 or larger; scale down to 360 × 360 afterward |
| Style | Flat vector, sports-team mascot, sticker or badge style |
| Background | Solid forest green inside the circle. If the tool supports transparency, make the corners outside the circle transparent. If not, use a flat white background and remove it afterward. |
| Variations | Generate 4 or more and pick the one that stays clearest when shrunk |

## Check Before Accepting an Image

- [ ] The griffin has an eagle head and beak, and the wings read clearly as wings.
- [ ] The expression is friendly and confident, not angry.
- [ ] It uses mostly the five palette colors, with no gradients.
- [ ] There is **no text** in the image. The device draws the school name itself.
- [ ] The subject fits inside the circle with a margin on every side.
- [ ] It is still recognizable when shrunk to about 64 × 64 pixels.

## After Generating

1. Crop to a square, centered on the badge.
2. Scale to **360 × 360** pixels.
3. Mask everything outside the circle so the corners are transparent, or flood them black, since the round display never shows the corners.
4. Save the files as `img/griffin.png` (full size) and `img/griffin-360.png` (display size) in this folder, replacing the placeholder art, then update the image links in `index.md` and `mascot.md` if the file names change.

## Optional Pose Variants

Use the Main Prompt and swap only the pose and expression line. These match the device states
the kit can show.

| Variant | Replace the expression with | Device state |
|---------|----------------------------|--------------|
| `griffin-listening` | head tilted, one ear tuft raised, eyes wide and attentive | Listening |
| `griffin-thinking` | eyes looking up and to the side, one wing raised to the beak | Thinking |
| `griffin-cheer` | beak open in a cheer, wings spread wide, eyes bright | Test or event announcement |
| `griffin-sleep` | eyes closed, calm smile, wings folded | Idle or muted |
