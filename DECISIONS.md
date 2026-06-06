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

## 12:08 - Added all 10 missing detectors
- Completed rulebook: title_too_short, missing_meta, duplicate_meta, meta_too_long,
  missing_h1, duplicate_h1, redirect_chain, thin_content, non_indexable_but_linked, slow_page
- Result: 4 issue types → 12 issue types detected
- Used defaultdict pattern for duplicate detection (same as starter)

## 12:21 - Model setup
- 16GB RAM, attempting gemma3:4b via ollama cloud
- Set OLLAMA_CONTEXT_LENGTH=65536

## 12:25 - Built fixer.py
- AI title rewriter using Ollama HTTP API
- Redirect map builder using pure Python path matching
- Capped at 20 title rewrites to save model quota

## 12:29 - Wired fixer into run.py
- Added --no-fixes flag for runs without Ollama
- Fix step fails gracefully if model unavailable

## 12:35 - Champion tier fix CSVs
- outputs/fixes_titles.csv and outputs/fixes_redirects.csv writing correctly

## 12:38 - Full pipeline verified end to end
- Dashboard live at localhost:7700, all 12 issue types showing
- 20 title rewrites, 6 redirect entries
- Duration: 40.9s on sample export

## 13:01 - Ollama disk space issue + fix
- C: drive full, moved OLLAMA_MODELS to D:\ollama-models via setx
- WinError 10061 = ollama serve not running in background
- Switched to qwen2.5:0.5b (397MB) instead of gemma3:4b (3.3GB)

## 13:04 - README completed
- Full setup, architecture, issue list, outputs documented

## 13:27 - Final state
- 10 commits done, all timestamps verified against git log
- 12 issue types detected across all severity levels
- Dashboard live, report.json schema-valid, fix CSVs writing
- Waiting for qwen2.5:0.5b download to verify AI title rewrites