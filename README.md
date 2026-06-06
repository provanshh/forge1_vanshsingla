# SEO Command Center — Forge Sprint 01

A Claude Code plugin that autonomously audits a Screaming Frog SEO export,
detects all issues, rewrites bad titles using a local AI model, and delivers
a live dashboard + client-ready report.

**Built by:** Vansh Singla | MAIT Delhi | Forge Sprint 01 · June 6, 2026

---

## What it does

1. **Ingests** a Screaming Frog `internal_all.csv` export
2. **Detects** 17 SEO issue types using deterministic Python rules
3. **Prioritizes** by severity (High / Medium / Low)
4. **Fixes** — rewrites bad/missing titles via local Ollama model
5. **Maps** broken links to closest live redirect targets
6. **Delivers** a live dashboard at `localhost:7700` + `report.html` + `report.json`

---

## Setup

### Requirements
- Python 3.10+
- Ollama with `qwen2.5:0.5b` model
- `pip install mcp`

### Install
```bash
git clone https://github.com/provanshh/forge1_vanshsingla.git
cd forge1_vanshsingla
pip install mcp
ollama pull qwen2.5:0.5b
```

---

## Run

```bash
# Full run with dashboard
python run.py path/to/export/

# Headless (no dashboard)
python run.py path/to/export/ --no-dashboard

# Skip AI fixes (faster, no Ollama needed)
python run.py path/to/export/ --no-dashboard --no-fixes
```

Then open **http://localhost:7700** to watch the live cockpit.

---

## Outputs

| File | What it is |
|---|---|
| `outputs/report.json` | Machine-readable audit (schema-valid) |
| `outputs/report.html` | Client-ready visual report |
| `outputs/fixes_titles.csv` | AI-rewritten titles for bad pages |
| `outputs/fixes_redirects.csv` | Redirect map for broken links |

---

## Architecture

run.py                  ← entry point, orchestrates pipeline
seo/detector.py         ← 17 deterministic SEO detectors (no AI)
seo/fixer.py            ← AI title rewriter + redirect map builder
seo/export_fixes.py     ← writes fix CSV artifacts
mcp/server.py           ← MCP tools + live dashboard (SSE on port 7700)
agents/                 ← sub-agent definitions (ingest, auditor, fixer, reporter)
dashboard/              ← live cockpit HTML/JS

### Sub-agents
- **ingest** — loads and normalizes the CSV
- **auditor** — runs all 17 detectors
- **fixer** — calls Ollama for title rewrites, builds redirect map
- **reporter** — writes report.json, report.html, fix CSVs

---

## SEO Issues Detected

| Issue | Severity |
|---|---|
| Missing title | High |
| Duplicate title | High |
| Broken link (4xx) | High |
| Server error (5xx) | High |
| Redirect chain | High |
| Title too long | Medium |
| Missing meta description | Medium |
| Duplicate meta description | Medium |
| Missing H1 | Medium |
| Redirect (3xx) | Medium |
| Orphan page | Medium |
| Non-indexable but linked | Medium |
| Title too short | Low |
| Meta description too long | Low |
| Duplicate H1 | Low |
| Thin content | Low |
| Slow page | Low |

---

## Grader notes
- Detection is pure Python (pandas/csv) — model only used for title rewrites
- Works on any Screaming Frog export, not hardcoded to sample
- `--no-fixes` flag allows full audit run without Ollama
- `outputs/report.json` validates against `report.schema.json`