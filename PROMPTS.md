# PROMPTS.md — my key prompts log

Keep the handful of prompts that actually moved the build. Not every message — the ones that
mattered: the system/sub-agent prompts, the ones you iterated on, the "this finally worked"
moment. This shows how you direct an AI, which is graded (challenge brief section 08).

Format per entry:
- **Prompt** (paste it)
- **For:** what you were trying to do
- **Revised?** did you have to change it, and why

---

## Example (replace with your own)

- **Prompt:** "Extend seo/detector.py to detect redirect chains: build a map of {Address ->
  Redirect URL} for all 3xx rows, then a chain exists when a Redirect URL is itself a key in
  that map. Add a redirect_chain issue (High). Run python seo/detector.py and show counts."
- **For:** adding the redirect-chain detector
- **Revised?** Yes — first version flagged single redirects as chains; added the "target is
  also a redirecting URL" condition.

---

## Key prompt pattern for title rewriting
- One URL at a time to the model (never batch raw rows)
- Ask for title only, no explanation, within 60 chars

## Title rewrite prompt (fixer.py)
- Prompt includes: URL path, H1, meta, current title
- Rules: under 60 chars, no clickbait, reply with title only
- Added validation loop: re-asks if title > 65 chars
- Works one URL at a time to stay within free quota