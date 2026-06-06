# DECISIONS.md — decision & learnings log

A short running note of the real choices you made: what you tried, what failed and why, what
you changed. This is your engineering judgement on the record — it is what separates a builder
from a button-presser, and it is graded (challenge brief section 08).

Append a 1–2 line entry whenever you make a real decision or hit/fix a wall. Add a timestamp.

Format:
`[HH:MM] <decision or problem> → <what you did and why>`

---

## Example (replace with your own)
- `[10:20]` Chose plain-csv parsing over pandas → fewer deps, fast enough for 5k rows, model
  quota saved for the fixer.
- `[11:05]` Title detector over-counted duplicates → realized non-indexable pages were
  included; added an indexable+200 filter (per rulebook).
- `[12:40]` Dashboard wasn't updating live → MCP tool wasn't emitting the SSE event; added
  `_emit("issue", row)` in extract.

---

## My log

## 12:10 - Added all 10 missing detectors
- Completed rulebook: title_too_short, missing_meta, duplicate_meta, meta_too_long,
  missing_h1, duplicate_h1, redirect_chain, thin_content, non_indexable_but_linked, slow_page
- Result: 4 issue types → 12 issue types detected
- Used defaultdict pattern for duplicate detection (same as starter)

## 12:15 - Model setup
- 16GB RAM, using gemma3:4b via ollama cloud
- Set OLLAMA_CONTEXT_LENGTH=65536