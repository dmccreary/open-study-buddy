---
title: "Kit Import Map"
description: "The learner will interpret the kit's import map by naming, for 5 selected files, which other files it imports and which folder each file belongs in on the Pico."
status: scaffold
library: vis-network
bloom_level: Understand
---

# Kit Import Map



<iframe src="main.html" width="100%" height="600"></iframe>

[Run MicroSim in Fullscreen](main.html){ .md-button .md-button--primary }

## Specification

The full specification below is extracted from
[Chapter 2: MicroPython Review for Embedded Systems](../../chapters/02-micropython-review/index.md).

```text
Type: graph-model
**sim-id:** kit-import-map<br/>
**Library:** vis-network<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** interpret<br/>
**Learning Objective:** The learner will interpret the kit's import map by naming, for 5 selected files, which other files it imports and which folder each file belongs in on the Pico.

**Prerequisites:** module, import, import path, `/lib` folder (all defined in the section "Modules and Imports" above this block).

**Evidence of Mastery:** For each of the 5 files in the table below, the learner selects the files it imports from the full list of 8 files. A selection is correct when it matches the "Kit files it imports" column exactly. Mastery is 4 of 5 correct. Clicking a file to read its description is exploration, not evidence.

**Misconceptions:** (1) Every file must be at the top level of the Pico. (2) A file imports everything that its imports import. (3) Editing a module on the computer updates the copy on the Pico.

**Instructional Rationale:** An Understand-level objective asks the learner to interpret a structure, so the learner reads arrows rather than reciting a rule. Choosing the imports of a file before the answer is shown makes the learner predict from the diagram.

**Content:**

The graph has 8 files. Each file shows its Pico folder and a one-sentence description when selected.

| File | Pico folder | Description | Kit files it imports |
|---|---|---|---|
| 03-buttons.py | top level | Test 03, reports button presses | config |
| 04-hello-world.py | top level | Test 04, draws "Hello World!" | config, shapes |
| 06-listen-meter.py | top level | Test 06, a microphone level meter | config |
| config.py | top level | Every pin number and helper function for the kit | gc9b72, vga1_8x16, vga1_bold_16x32 |
| shapes.py | lib | Circles, rings, polygons, sprites | none |
| gc9b72.py | lib | The display driver | none |
| vga1_8x16.py | lib | The small 8 by 16 font | none |
| vga1_bold_16x32.py | lib | The large 16 by 32 font | none |

Standard-library modules such as `machine`, `time`, `math`, and `struct` are not drawn, and the learner is not asked about them.

**Provenance:** The files, folders, and imports are taken from the kit at `src/kits/study-buddy-base/` in this repository: the test files named, `config.py`, and the four files in `lib/`.

**Rules:** An arrow runs from the importing file to the imported file. A selection is correct when the set of files the learner selects equals the "Kit files it imports" set for that file. A file that imports no kit files is answered by selecting none. Order does not matter.

**Learner Activity:**

1. The learner reads the graph and clicks any file to see its folder and description.
2. The learner starts the check. For each of 5 files (03-buttons.py, 04-hello-world.py, 06-listen-meter.py, config.py, shapes.py), the learner selects the kit files it imports and submits.
3. The sim reveals the correct arrows for that file.
4. After the fifth file, the sim shows the score.

**Feedback:** 5 files, fixed order, one attempt each. Correct: "Correct: <file> imports <list>." Incorrect: "Not quite. <file> imports <list>; <one-sentence reason>." The correct answer is shown right after each submission. A running score "n of 5" is shown.

**Starting State:** The full graph is shown with no file selected, and the question "Which files does 04-hello-world.py need?"

**Chapter Anchors:** The chapter states that `config.py` is at the top level, that the drivers and fonts are in `lib/`, and that test 04 imports `shapes` and `config`.
```

## Related Resources

- [Chapter 2: MicroPython Review for Embedded Systems](../../chapters/02-micropython-review/index.md)
