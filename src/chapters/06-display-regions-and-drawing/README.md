# Chapter 6 code: Drawing Directly to Display Regions

Chapter: `docs/chapters/06-display-regions-and-drawing/index.md`

```bash
cd src/chapters
./upload-chapter.sh 06 01-pixel-vs-fillrect.py
```

The upload script copies every top-level `.py` file and `sage.rgb565`.
Everything needs the display only.

| File | PASS looks like |
|------|-----------------|
| `01-pixel-vs-fillrect.py` | `fill_rect` and `blit_buffer` send 6,011 bytes; 3,000 `pixel()` calls send 39,000 |
| `02-window-order.py` | Top block: straight stripes. Bottom block: sheared stripes |
| `03-dirty-meter.py` | Bytes per frame: A > B > C |
| `04-text-padding.py` | Top line has leftover letters; bottom line is clean |
| `05-sprite-keyed.py` | Left sprite has a black square; right sprite is only the disc |
| `06-ball-animation.py` | Strip method sends fewer bytes per frame than the whole-box method |
| `07-region-layout.py` | All corners inside; total 50,752 bytes; note your redraw time |
| `08-show-image.py` | Sage appears centered in a round mask in under 100 ms |
| `09-round-mask-table.py` | Row 20 spans x 129 to 231; also runs on a computer |

## Making your own image (the school mascot)

On your computer (needs `pip install pillow`):

```bash
cd src/chapters/06-display-regions-and-drawing/tools
python3 png-to-rgb565.py my-mascot.png ../my-mascot.rgb565 120
```

Then copy it with `mpremote fs cp ../my-mascot.rgb565 :my-mascot.rgb565` and
change `PATH` in `08-show-image.py`.

**Record these numbers:** the three times from `01` (test board: 1,593 ms, 4.3 ms,
3.1 ms), the redraw time of all five regions from `07` (best case 16.9 ms; test
board 28.1 ms), and bytes and time per frame from `03` (test board: 8,822 bytes and
6.4 ms, 7,116 and 5.2 ms, 271 and 0.8 ms).
