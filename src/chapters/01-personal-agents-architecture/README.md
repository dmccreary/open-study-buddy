# Chapter 1 code: Personal Agents and the Open Study Buddy Architecture

Chapter: `docs/chapters/01-personal-agents-architecture/index.md`

Nothing here needs hardware. Run both files on your computer:

```bash
python3 01-rule-based-decide.py
python3 02-contract-check.py
```

| File | What it shows | PASS looks like |
|------|---------------|-----------------|
| `01-rule-based-decide.py` | The `decide()` rule-based brain from "Rule-Based Agents" | Last line says PASS |
| `02-contract-check.py` | `request.json` and `reply.json` match the request-reply contract | Last line says PASS |
| `request.json`, `reply.json` | The two JSON messages from "The Request-Reply Contract" | |

`01-rule-based-decide.py` also runs on the Pico (`mpremote run`).
