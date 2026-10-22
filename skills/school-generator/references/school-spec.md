# school.json reference

One JSON file describes a school. Write it at
`src/schools/{SCHOOL-ID}/school.json` and pass that path to
`build_school.py`, which reads it and never rewrites it. (If you pass a
spec from somewhere else, the script copies it there, so the school can
always be rebuilt from that folder.)

## Fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | kebab-case folder name used in both `docs/schools/` and `src/schools/` |
| `name` | yes | official full name (page title, nav entry, index table) |
| `kind` | yes | `"real"` or `"synthetic"` |
| `org_type` | real only | the index table's Type column: `High school`, `Middle school`, `Coding club`, `University`... |
| `description` | yes | one sentence for the page's `description:` front matter and social cards |
| `summary` | yes | the intro paragraph under the title (Markdown): describe the school; the real/synthetic note box is added for you |
| `slogan` | no | synthetic schools: shown as a pull quote and in the index table |
| `short_name` | yes | what students call the school; used in code comments |
| `buddy_name` | yes | the big title on the screen, 20 letters max, usually `short_name + " Buddy"` |
| `program_slug` | yes | kebab-case; the program is `01-{program_slug}-buddy.py` |
| `footer` | yes | bottom line of the screen, 29 letters max |
| `profile` | no | `[["Item", "Value"], ...]` rows for the Profile / School Facts table (Markdown allowed in values) |
| `colors.background` / `.accent` / `.text` | yes | each `{"hex": "#RRGGBB", "name": "Groves blue"}`; the names appear in code and docs |
| `colors.source` | yes | where the colors came from, phrased to follow "colors, ...": `"from groveslearning.org (primary blue, accent cyan)"` |
| `mascot.source` | yes | art file, relative to `docs/schools/{SCHOOL-ID}/` (`img/heron.svg`); `.svg` is rendered to `img/{name}-360.png` |
| `mascot.name` | yes | kebab-case noun used in file names: `heron` -> `heron-140.rgb565` |
| `mascot.noun` | no | how prose names the mascot when `name` with spaces would be wrong, e.g. `"Trojan horse"` (keeps the capital); defaults to `name` with hyphens as spaces |
| `mascot.phrase` | yes | how the code and README refer to the badge: `"the Harbor Point heron badge"` |
| `mascot.alt` | yes | alt text for the image on the docs page |
| `mascot.label` | no | synthetic schools: the index table's Mascot column, e.g. `"Hattie the Heron"` |
| `mascot.style` | yes | `"plain"` (art is the badge) or `"disc"` (art inside a white disc with an accent ring) |
| `mascot.placeholder` | no | real schools: `true` when the art was drawn for the demo and is not an official mark (ignored for synthetic schools) |
| `mascot.permission` | no | real schools with supplied art: who granted permission, for the to-do list |
| `mascot.section_title` | yes | heading for the mascot section, e.g. `"Placeholder Mascot: the Harbor Point Heron"` |
| `mascot.section_text` | yes | Markdown paragraph(s): what the art shows, why, and (if placeholder) that it is not official |
| `mascot.palette` | no | `[["Color name", "#HEX", "Used for"], ...]` table under the mascot section |
| `events` | yes | 1-3 `[day, event]` pairs; `"{day}: {event}"` must be 32 letters max |
| `todo` | no | replaces the default real-school to-do list; strings, `"[x] ..."` for done items |

All on-screen text (`buddy_name`, `footer`, `events`) must be plain ASCII.

## Example: a synthetic school with a drawn placeholder badge

```json
{
  "id": "harbor-point-middle-school",
  "name": "Harbor Point Middle School",
  "kind": "synthetic",
  "description": "A synthetic lakeside middle school with a heron mascot, for demonstrating the Open Study Buddy kit.",
  "summary": "A grades 6-8 school on the shore of a northern lake, where students canoe in the fall and\nrun a winter science fair on the ice.",
  "slogan": "Stand tall. Think deep.",
  "short_name": "Harbor Point",
  "buddy_name": "Harbor Buddy",
  "program_slug": "harbor",
  "footer": "Stand tall. Think deep.",
  "profile": [
    ["Name", "Harbor Point Middle School"],
    ["Slogan", "Stand tall. Think deep."],
    ["Mascot", "Hattie the Heron"],
    ["Grades", "6-8"],
    ["School colors", "Deep teal `#0B4F5C` and sunrise orange `#F28C28`"]
  ],
  "colors": {
    "background": {"hex": "#0B4F5C", "name": "deep teal"},
    "accent": {"hex": "#F28C28", "name": "sunrise orange"},
    "text": {"hex": "#FFFFFF", "name": "white"},
    "source": "from the school's invented brand (deep teal, sunrise orange)"
  },
  "mascot": {
    "source": "img/heron.svg",
    "name": "heron",
    "phrase": "Hattie the Heron's badge",
    "alt": "A gray-blue heron standing in teal water inside an orange ring",
    "label": "Hattie the Heron",
    "style": "plain",
    "section_title": "Mascot: Hattie the Heron",
    "section_text": "Hattie is a great blue heron standing in the shallows, drawn as a round badge in the school colors.",
    "palette": [
      ["Deep teal", "#0B4F5C", "Water, screen background"],
      ["Sunrise orange", "#F28C28", "Ring, beak"]
    ]
  },
  "events": [
    ["Wednesday", "Earth Science Quiz"],
    ["Thursday", "Robotics Club"],
    ["Friday", "Fall Harvest Dance"]
  ]
}
```

## What a real school changes

- `"kind": "real"` and an `org_type`.
- `profile` holds only published or supplied facts; use `*To be provided*`
  for the rest (Slogan, Calendar and Contact for approval usually are).
- With no supplied art, `"placeholder": true` and a `section_text` that
  says the art was drawn for the demo and is not an official school mark.
- No `slogan` unless the school publishes one; the footer is then the
  school name.
- The default to-do list (confirm name and slogan, mascot permission,
  calendar, TEST:/DUE: prefixes, run on a real kit) is added for you.
