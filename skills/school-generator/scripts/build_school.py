#!/usr/bin/env python3
"""Build a school's Study Buddy folders from one school.json spec.

    python3 build_school.py <repo-root> <path/to/school.json> [--force]

Writes, for the school id in the spec:

    docs/schools/<id>/index.md                 the school page
    docs/schools/<id>/img/<mascot>-360.png     (rendered from the SVG, if the mascot is an SVG)
    docs/schools/<id>/img/<slug>-buddy-preview.png   computer-rendered picture of the screen
    src/schools/<id>/school.json               copy of the spec (the source of truth)
    src/schools/<id>/01-<slug>-buddy.py        MicroPython demo for the round display
    src/schools/<id>/<mascot>-140.rgb565       the badge, raw RGB565
    src/schools/<id>/tools/mascot-to-rgb565.py rebuilds the .rgb565 from the artwork
    src/schools/<id>/upload.sh                 copies kit + demo to the Pico and runs it
    src/schools/<id>/README.md

and adds the school to docs/schools/index.md and the Schools section of
mkdocs.yml nav (skipped if already there).

Existing files are never overwritten without --force. See
references/school-spec.md for every field in school.json.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL / "assets" / "templates"

# Character limits proven on the real panel by the working examples
# (Cedar Ridge's 17-letter title, its 32-letter Friday line, and
# Minnetonka's 29-letter bottom line). preview_screen.py also checks the
# geometry, so these are a fast first gate.
MAX_BUDDY = 20      # BIG_FONT, 16 px per letter
MAX_EVENT = 32      # "Day: what", SMALL_FONT, 8 px per letter
MAX_FOOTER = 29     # SMALL_FONT, low on the glass where it is narrow
MAX_EVENTS = 3


class SpecError(Exception):
    pass


# ---------------------------------------------------------------- helpers

def fill(template, values):
    text = (TEMPLATES / template).read_text()
    for key, value in values.items():
        text = text.replace("@@{}@@".format(key), str(value))
    left = re.findall(r"@@[A-Z_]+@@", text)
    if left:
        raise SpecError("template {} has unfilled tokens: {}".format(template, sorted(set(left))))
    return text


def comment(text, width=76):
    """Wrap prose into '# ' comment lines."""
    out = []
    for para in text.strip().split("\n\n"):
        out += textwrap.wrap(para, width - 2, break_on_hyphens=False) or [""]
        out.append("")
    return "\n".join(("# " + line).rstrip() for line in out[:-1])


def hex_rgb(value, field):
    m = re.fullmatch(r"#?([0-9A-Fa-f]{6})", value or "")
    if not m:
        raise SpecError("{} must be a hex color like #003698, not {!r}".format(field, value))
    h = m.group(1).upper()
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)), "#" + h


def luminance(rgb):
    def chan(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def const_name(color_name, taken):
    name = re.sub(r"[^A-Za-z0-9]+", "_", color_name).strip("_").upper() or "COLOR"
    if name[0].isdigit():
        name = "C_" + name
    while name in taken:
        name += "_2"
    taken.add(name)
    return name


def noun(mascot):
    """How prose refers to the mascot: mascot.noun, else the file-name noun with spaces."""
    return mascot.get("noun") or mascot["name"].replace("-", " ")


def pystr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def md_cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def write(path, text, force, written):
    if path.exists() and not force:
        raise SpecError("{} already exists (re-run with --force to overwrite)".format(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    written.append(path)


# ---------------------------------------------------------------- spec

def load_spec(path):
    spec = json.loads(Path(path).read_text())
    need = ["id", "name", "kind", "description", "summary", "short_name", "buddy_name",
            "program_slug", "footer", "colors", "mascot", "events"]
    missing = [k for k in need if not spec.get(k)]
    if missing:
        raise SpecError("school.json is missing: " + ", ".join(missing))
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", spec["id"]):
        raise SpecError("id must be kebab-case (lowercase words joined by hyphens): " + spec["id"])
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", spec["program_slug"]):
        raise SpecError("program_slug must be kebab-case: " + spec["program_slug"])
    if spec["kind"] not in ("real", "synthetic"):
        raise SpecError("kind must be 'real' or 'synthetic'")
    if spec["kind"] == "real" and not spec.get("org_type"):
        raise SpecError("real schools need org_type (for the index table), e.g. 'Middle school'")

    m = spec["mascot"]
    for k in ("source", "name", "phrase", "alt", "style", "section_title", "section_text"):
        if not m.get(k):
            raise SpecError("mascot is missing: " + k)
    if m["style"] not in ("plain", "disc"):
        raise SpecError("mascot.style must be 'plain' or 'disc'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", m["name"]):
        raise SpecError("mascot.name is used in file names, so it must be kebab-case: " + m["name"])

    c = spec["colors"]
    for k in ("background", "accent", "text"):
        if not (c.get(k) and c[k].get("hex") and c[k].get("name")):
            raise SpecError("colors.{} needs hex and name".format(k))
        c[k]["rgb"], c[k]["hex"] = hex_rgb(c[k]["hex"], "colors.{}.hex".format(k))
    if not c.get("source"):
        raise SpecError("colors.source must say where the colors came from")

    events = spec["events"]
    if not 1 <= len(events) <= MAX_EVENTS:
        raise SpecError("give 1 to {} events; a fourth line falls under the bezel".format(MAX_EVENTS))

    errors = []
    screen = [("buddy_name", spec["buddy_name"], MAX_BUDDY), ("footer", spec["footer"], MAX_FOOTER)]
    for i, ev in enumerate(events):
        if len(ev) != 2:
            raise SpecError("each event is [day, what], e.g. [\"Wednesday\", \"Science Quiz\"]")
        screen.append(("event {}".format(i + 1), "{}: {}".format(*ev), MAX_EVENT))
    for label, text, limit in screen:
        if len(text) > limit:
            errors.append("{} {!r} is {} letters; the limit is {}".format(label, text, len(text), limit))
        bad = sorted({ch for ch in text if not 0x20 <= ord(ch) < 0x7F})
        if bad:
            errors.append("{} {!r} has letters the bitmap font cannot draw: {} "
                          "(use plain ASCII: straight quotes, no accents or dashes)".format(label, text, bad))
    if errors:
        raise SpecError("text will not fit or draw on the round screen:\n  " + "\n  ".join(errors))
    return spec


def contrast_warnings(spec):
    c = spec["colors"]
    out = []
    for k in ("text", "accent"):
        ratio = contrast(c[k]["rgb"], c["background"]["rgb"])
        if ratio < 4.5:
            out.append("colors.{} {} on background {} has contrast {:.1f}:1 (want 4.5:1 or more); "
                       "small text will be hard to read".format(k, c[k]["hex"], c["background"]["hex"], ratio))
    return out


# ---------------------------------------------------------------- mascot art

def prepare_art(spec, docs_dir):
    """Return the raster source path (relative to docs_dir) the badge tool reads."""
    source = docs_dir / spec["mascot"]["source"]
    if not source.exists():
        raise SpecError("mascot.source not found: {}".format(source))
    if source.suffix.lower() != ".svg":
        return spec["mascot"]["source"]
    png = source.with_name("{}-360.png".format(spec["mascot"]["name"]))
    try:
        import cairosvg
    except ImportError:
        raise SpecError("cairosvg is needed to render the SVG mascot: pip install cairosvg")
    cairosvg.svg2png(url=str(source), write_to=str(png), output_width=360, output_height=360)
    return str(png.relative_to(docs_dir))


# ---------------------------------------------------------------- src/

def program_header(spec, image_file):
    m = spec["mascot"]
    lines = "{} Study Buddy demo: \"{}\" with upcoming events".format(spec["short_name"], spec["buddy_name"])
    p1 = ("Shows {} at the top, the words \"{}\" under it, and a mock-up of three events "
          "coming up this week, on a {} round screen. Needs the display and {} on the Pico "
          "(upload.sh copies both).").format(m["phrase"], spec["buddy_name"],
                                             spec["colors"]["background"]["name"], image_file)
    p2 = ""
    if spec["kind"] == "synthetic":
        p2 += "{} is a synthetic school, invented for demos. ".format(spec["name"])
    elif m.get("placeholder"):
        p2 += "The {} is a placeholder mascot drawn for this demo, not an official school mark. ".format(
            noun(m))
    p2 += ("The events are typed in below as a mock-up, not read from the school calendar. "
           "This is a picture of what the buddy will look like, not the calendar agent itself "
           "(that is Chapter 16).")
    return "# {}\n{}\n#\n{}".format(lines, comment(p1), comment(p2))


def build_src(spec, repo, src_dir, art_rel, force, written):
    c, m = spec["colors"], spec["mascot"]
    program = "01-{}-buddy.py".format(spec["program_slug"])
    image_file = "{}-140.rgb565".format(m["name"])
    taken = {"BACKGROUND"}
    accent_const = const_name(c["accent"]["name"], taken)
    text_const = const_name(c["text"]["name"], taken)
    rgb_args = lambda k: ", ".join("0x{:02X}".format(v) for v in c[k]["rgb"])
    events = "\n".join("    ({}, {}),".format(pystr(day + ":"), pystr(what)) for day, what in spec["events"])

    values = {
        "HEADER": program_header(spec, image_file),
        "PASS": comment("PASS: the {} badge is centered near the top, the title is {}, the {} and \"{}\" "
                        "are inside the glass and none of the letters are cut off by the bezel.".format(
                            noun(m), c["text"]["name"],
                            "three events" if len(spec["events"]) == 3 else "events", spec["footer"])),
        "MASCOT_NAME": noun(m),
        "TEXT_NAME": c["text"]["name"],
        "ACCENT_NAME": c["accent"]["name"],
        "PROGRAM": program,
        "IMAGE_FILE": image_file,
        "COLOR_COMMENT": comment("{} colors, {}.".format(spec["short_name"], c["source"].rstrip("."))),
        "BG_RGB": rgb_args("background"),
        "BG_NAME": c["background"]["name"],
        "ACCENT_CONST": accent_const,
        "ACCENT_RGB": rgb_args("accent"),
        "TEXT_CONST": text_const,
        "TEXT_RGB": rgb_args("text"),
        "EVENTS": events,
        "BUDDY_NAME": spec["buddy_name"],
        "BUDDY_LEN": len(spec["buddy_name"]),
        "BUDDY_PX": len(spec["buddy_name"]) * 16,
        "FOOTER": spec["footer"].replace('"', '\\"'),
        "FOOTER_LEN": len(spec["footer"]),
        "FOOTER_PX": len(spec["footer"]) * 8,
    }
    write(src_dir / program, fill("buddy.py.tmpl", values), force, written)

    upload = src_dir / "upload.sh"
    write(upload, fill("upload.sh.tmpl", {"SHORT": spec["short_name"], "PROGRAM": program,
                                          "IMAGE_FILE": image_file}), force, written)
    upload.chmod(0o755)

    svg_note = ""
    if m["source"].lower().endswith(".svg"):
        svg_note = ("#\n# To change the drawing itself, edit {0} and re-render the PNG:\n"
                    "#   cairosvg {0} -o {1} -W 360 -H 360\n").format(Path(m["source"]).name, Path(art_rel).name)
    tool_values = {
        "SHORT": spec["short_name"],
        "MASCOT_NAME": noun(m),
        "SOURCE_NAME": "a {} x {} image".format(360, 360) if svg_note else Path(art_rel).name,
        "BG_NAME": c["background"]["name"],
        "ACCENT_NAME": c["accent"]["name"],
        "PROGRAM": program,
        "SVG_NOTE": svg_note,
        "BG_HEX_TUPLE": ", ".join("0x{:02X}".format(v) for v in c["background"]["rgb"]),
        "ACCENT_HEX_TUPLE": ", ".join("0x{:02X}".format(v) for v in c["accent"]["rgb"]),
        "ID": spec["id"],
        "SOURCE_PATH": art_rel,
        "IMAGE_FILE": image_file,
    }
    template = "tool-disc.py.tmpl" if m["style"] == "disc" else "tool-plain.py.tmpl"
    tool = src_dir / "tools" / "mascot-to-rgb565.py"
    if m["style"] == "plain":
        tool_values.pop("ACCENT_NAME")
    write(tool, fill(template, tool_values), force, written)

    write(src_dir / "README.md", readme(spec, program, image_file), force, written)

    # Run the tool exactly as a student would, so the .rgb565 is what the tool makes.
    result = subprocess.run([sys.executable, str(tool)], capture_output=True, text=True)
    if result.returncode != 0:
        raise SpecError("tools/mascot-to-rgb565.py failed:\n" + result.stderr)
    written.append(src_dir / image_file)
    return program, image_file


def readme(spec, program, image_file):
    c, m = spec["colors"], spec["mascot"]
    kind_line = {
        "synthetic": "{} is a synthetic school, invented for demos; its page is `docs/schools/{}/`.".format(
            spec["name"], spec["id"]),
        "real": "{} is a real organization (see `docs/schools/{}/`).".format(spec["name"], spec["id"]),
    }[spec["kind"]]
    if spec["kind"] == "real" and m.get("placeholder"):
        kind_line += (" The {} is a **placeholder** drawn for this demo, not an official "
                      "school mark.").format(noun(m))
    kind_line += " The colors come {}. The events are a mock-up typed into the demo, not read from a school calendar.".format(
        c["source"].rstrip("."))
    events = "\n".join("{}: {}".format(d, w) for d, w in spec["events"])
    return """# {short} Study Buddy demo

{intro}

{kind_line}

| File | What it does |
|---|---|
| `{program}` | Draws the badge, the title, the events and the bottom line. |
| `{image}` | The badge, 140 x 140, raw RGB565 (39,200 bytes). |
| `tools/mascot-to-rgb565.py` | Rebuilds `{image}` from the artwork (runs on your computer). |
| `upload.sh` | Sends the kit files and this demo to the Pico, then runs it. |
| `school.json` | The spec this folder was generated from (school-generator skill). |

**Parts needed:** the display only (wire it as in `../../kits/study-buddy-base/`).

```bash
./upload.sh
```

**PASS:** the {mascot} badge is centered near the top of a {bg} screen.
"{buddy}" is {text} below it, then {n} event lines with the day in {accent}
and the event in {text}:

```
{events}
```

and "{footer}" in {accent} at the bottom, nothing cut off by the bezel.
""".format(short=spec["short_name"], intro="\n".join(textwrap.wrap(
               "A one-screen demo for the Study Buddy base kit: {} at the top, **\"{}\"** under it, and a mock-up "
               "of the week's upcoming events on a {} round display.".format(m["phrase"], spec["buddy_name"],
                                                                            c["background"]["name"]),
               76, break_on_hyphens=False)), buddy=spec["buddy_name"],
           bg=c["background"]["name"], kind_line="\n".join(textwrap.wrap(kind_line, 76, break_on_hyphens=False)),
           program=program, image=image_file, mascot=noun(m),
           text=c["text"]["name"], accent=c["accent"]["name"], n=len(spec["events"]),
           events=events, footer=spec["footer"])


# ---------------------------------------------------------------- docs/

def repo_url(repo):
    mk = (repo / "mkdocs.yml").read_text()
    m = re.search(r"^repo_url:\s*['\"]?([^'\"\s]+)", mk, re.M)
    return m.group(1).rstrip("/") if m else None


def default_todo(spec):
    m = spec["mascot"]
    what = noun(m)
    if m.get("placeholder"):
        art = ("[ ] Ask whether the school has a mascot or logo it would rather show, and get permission "
               "to use it on the device display. Until then the demo uses the placeholder {}.".format(what))
    elif m.get("permission"):
        art = "[x] Get permission to show the {} on the device display: {}".format(what, m["permission"])
    else:
        art = "[ ] Get permission from the organization to show the {} on the device display.".format(what)
    return [
        "[ ] Confirm the exact name and slogan with the organization.",
        art,
        "[ ] Get a calendar: a published academic calendar, or a hand-built `events.json` and "
        "`calendar.ics` (see the [Cedar Ridge calendar](../cedar-ridge-high-school/calendar.md) for the format).",
        "[ ] Agree on which dates, if any, may use the `TEST:` and `DUE:` title prefixes.",
        "[ ] Run `./upload.sh` on a real kit and check the PASS line in `src/schools/{}/README.md`.".format(spec["id"]),
    ]


def build_docs(spec, repo, docs_dir, art_rel, program, preview_name, force, written):
    c, m, sid = spec["colors"], spec["mascot"], spec["id"]
    shown = m["source"]                       # SVG on the web page when we have one
    out = ["---",
           "title: {}".format(spec["name"]),
           "description: {}".format(spec["description"]),
           "image: schools/{}/{}".format(sid, art_rel),
           "---",
           "# {}".format(spec["name"]), ""]
    if spec["kind"] == "synthetic" and spec.get("slogan"):
        out += ["![{}]({}){{ width=\"220\" align=\"right\" }}".format(m["alt"], shown), "",
                "> **{}**".format(spec["slogan"]), "", spec["summary"].strip(), ""]
    else:
        out += [spec["summary"].strip(), "",
                "![{}]({}){{ width=\"220\" }}".format(m["alt"], shown), ""]

    if spec["kind"] == "real":
        out += ['!!! warning "Real organization: do not invent details"',
                "    Unlike [Cedar Ridge High School](../cedar-ridge-high-school/index.md), which is fictional,",
                "    this folder describes a real organization. Add only facts the organization has provided or",
                "    published itself, and never put real student names or grades here.", ""]
    else:
        out += ['!!! note "Synthetic school"',
                "    {} is **not a real school**. It was invented so demos and tests never need".format(spec["name"]),
                "    real student or school data.", ""]

    out += ["## {}".format("Profile" if spec["kind"] == "real" else "School Facts"), "",
            "| Item | Value |", "|------|-------|"]
    for item, value in spec.get("profile") or [["Name", spec["name"]]]:
        out.append("| {} | {} |".format(md_cell(item), md_cell(value)))
    out.append("")

    out += ["## {}".format(m["section_title"]), "", m["section_text"].strip(), ""]
    if m.get("palette"):
        out += ["| Color | Hex | Used for |", "|-------|-----|----------|"]
        out += ["| {} | `{}` | {} |".format(md_cell(n), h, md_cell(u)) for n, h, u in m["palette"]]
        out.append("")
    files = []
    if m["source"].lower().endswith(".svg"):
        files.append("| [{0}]({1}) | Vector | Editing and web pages |".format(Path(m["source"]).name, m["source"]))
    files.append("| [{0}]({1}) | {2} | Source for the device badge (`src/schools/{3}/`) |".format(
        Path(art_rel).name, art_rel, "360 x 360" if art_rel.endswith("-360.png") else "Original", sid))
    out += ["| File | Size | Use |", "|------|------|-----|"] + files + [""]

    base = repo_url(repo)
    code = "src/schools/{}/".format(sid)
    code_link = "[`{}`]({}/tree/main/{})".format(code, base, code) if base else "`{}`".format(code)
    events = ", ".join("{}: {}".format(d, w) for d, w in spec["events"])
    out += ["## Study Buddy Demo", "",
            "![The {} home screen: the {} badge, the title {}, and three upcoming events](img/{}){{ width=\"320\" }}".format(
                spec["buddy_name"], noun(m), spec["buddy_name"], preview_name), "",
            "This is the home screen of **{}**, the school's custom study buddy, as the kit's round "
            "display shows it. The picture is rendered on a computer from the demo program with the "
            "kit's own fonts, so it matches the device pixel for pixel.".format(spec["buddy_name"]), "",
            "| | |", "|---|---|",
            "| Buddy name | {} |".format(spec["buddy_name"]),
            "| Upcoming events | {} (a synthetic mock-up, not the school calendar) |".format(md_cell(events)),
            "| Screen colors | {} `{}` background, {} `{}` accent, {} `{}` text |".format(
                c["background"]["name"], c["background"]["hex"], c["accent"]["name"], c["accent"]["hex"],
                c["text"]["name"], c["text"]["hex"]),
            "| Demo code | {} (`{}`) |".format(code_link, program), "",
            "To run it on a kit, plug in the Pico and run `./upload.sh` from that folder.", ""]

    todo = spec.get("todo") or (default_todo(spec) if spec["kind"] == "real" else [])
    if todo:
        out += ["## Still To Do", ""]
        for item in todo:
            item = item if item.startswith("[") else "[ ] " + item
            out.append("- " + item)
        out.append("")

    write(docs_dir / "index.md", "\n".join(out), force, written)


def update_index(spec, repo, changed):
    path = repo / "docs" / "schools" / "index.md"
    if not path.exists():
        return
    lines = path.read_text().split("\n")
    if any("({}/index.md)".format(spec["id"]) in l for l in lines):
        return
    if spec["kind"] == "real":
        row = "| [{}]({}/index.md) | {} |".format(spec["name"], spec["id"], md_cell(spec["org_type"]))
        start = next((i for i, l in enumerate(lines) if l.startswith("## Real")), None)
    else:
        row = "| [{}]({}/index.md) | {} | {} |".format(spec["name"], spec["id"], md_cell(spec.get("slogan") or ""),
                                                       md_cell(spec["mascot"].get("label") or spec["mascot"]["name"]))
        start = 0
    if start is None:
        return
    table = [i for i in range(start, len(lines)) if lines[i].startswith("|")]
    # the first contiguous table after start
    last = None
    for i in table:
        if last is None or i == last + 1:
            last = i
        else:
            break
    if last is None:
        return
    lines.insert(last + 1, row)
    path.write_text("\n".join(lines))
    changed.append(path)


def synthetic_ids(repo):
    """School ids linked from the synthetic table (before '## Real') of docs/schools/index.md."""
    path = repo / "docs" / "schools" / "index.md"
    if not path.exists():
        return []
    head = path.read_text().split("## Real")[0]
    return re.findall(r"\]\(([a-z0-9-]+)/index\.md\)", head)


def update_nav(spec, repo, changed):
    path = repo / "mkdocs.yml"
    target = "schools/{}/index.md".format(spec["id"])
    text = path.read_text()
    if target in text:
        return
    lines = text.split("\n")
    anchor = next((i for i, l in enumerate(lines) if l.strip().endswith("schools/index.md")), None)
    if anchor is None:
        print("NOTE: no schools/index.md in mkdocs.yml nav; add {} by hand".format(target))
        return
    depth = lambda line: len(line) - len(line.lstrip())
    indent = depth(lines[anchor])
    last = anchor
    for i in range(anchor + 1, len(lines)):
        if not lines[i].strip() or depth(lines[i]) < indent:
            break
        last = i
    if spec["kind"] == "synthetic":
        # Keep the synthetic schools together, right after the last one in the
        # nav (Cedar Ridge), instead of after the real organizations.
        hits = [i for i in range(anchor + 1, last + 1)
                if any("schools/{}/".format(s) in lines[i] for s in synthetic_ids(repo))]
        if hits:
            top = max(i for i in range(anchor + 1, hits[-1] + 1) if depth(lines[i]) == indent)
            last = top
            while last + 1 < len(lines) and lines[last + 1].strip() and depth(lines[last + 1]) > indent:
                last += 1
    title = spec["name"]
    if re.search(r"[:#\[\]{}&*!|>'\"%@`]", title):
        title = '"{}"'.format(title.replace('"', '\\"'))
    lines.insert(last + 1, "{}- {}: {}".format(" " * indent, title, target))
    path.write_text("\n".join(lines))
    changed.append(path)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", type=Path)
    ap.add_argument("spec", type=Path)
    ap.add_argument("--force", action="store_true", help="overwrite files that already exist")
    args = ap.parse_args()
    repo = args.repo.resolve()

    try:
        spec = load_spec(args.spec)
        for w in contrast_warnings(spec):
            print("WARNING:", w)
        sid = spec["id"]
        docs_dir = repo / "docs" / "schools" / sid
        src_dir = repo / "src" / "schools" / sid
        written, changed = [], []

        art_rel = prepare_art(spec, docs_dir)
        spec_copy = src_dir / "school.json"
        if args.spec.resolve() != spec_copy.resolve():
            src_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.spec, spec_copy)
        program, _ = build_src(spec, repo, src_dir, art_rel, args.force, written)

        preview_name = "{}-buddy-preview.png".format(spec["program_slug"])
        result = subprocess.run([sys.executable, str(SKILL / "scripts" / "preview_screen.py"), str(repo), sid,
                                 "--out", str(docs_dir / "img" / preview_name)], capture_output=True, text=True)
        print(result.stdout.strip())
        if result.returncode == 2:
            raise SpecError("the demo program failed to run in the preview:\n" + result.stdout + result.stderr)

        build_docs(spec, repo, docs_dir, art_rel, program, preview_name, args.force, written)
        update_index(spec, repo, changed)
        update_nav(spec, repo, changed)
    except SpecError as e:
        print("ERROR:", e)
        return 1

    print("\nwrote:")
    extra = [docs_dir / art_rel] if art_rel != spec["mascot"]["source"] else []
    for p in written + extra + [docs_dir / "img" / preview_name]:
        print("  ", p.relative_to(repo))
    for p in changed:
        print("updated:", p.relative_to(repo))
    return result.returncode     # 1 if the preview found text under the bezel


if __name__ == "__main__":
    sys.exit(main())
