# Chapter 4 code: The Pico Kit Hardware and Wiring

Chapter: `docs/chapters/04-pico-kit-hardware/index.md`

```bash
cd src/chapters
./upload-chapter.sh 04 02-pin-table.py
```

| File | Parts needed | PASS looks like |
|------|--------------|-----------------|
| `01-pixel-spi-bytes.py` | Display | `pixel()` = 13 bytes; `fill_rect` 100 x 30 = 6,011 bytes |
| `02-pin-table.py` | none | Table prints, last line says PASS |
| `03-floating-pin-demo.py` | Pico, **GP16 left unconnected** | Pull-up reads all 1; pull-down reads all 0 when the pin is driven low first. If it reads 1 after being driven high, your Pico has the pull-down quirk the chapter describes |
| `04-display-visible-area.py` | Display | Green ring fully visible; corner dot hidden |
| `05-wifi-scan.py` | Pico | Your school's network is listed on a channel 1 to 14 |

The kit's own tests (`src/kits/study-buddy-base/01` to `07`) already cover
the wiring of each part; these files check the numbers in the chapter's tables.
