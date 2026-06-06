"""
fixer.py — AI-powered title/meta rewriter and redirect map builder.
Uses local Ollama model via HTTP API. No internet needed after model pull.
"""
from __future__ import annotations
import json, urllib.request, urllib.error

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:0.5b"


def _ask(prompt: str) -> str:
    """Send a prompt to Ollama, return the response text."""
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_ctx": 2048}
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["response"].strip()
    except Exception as e:
        return f"ERROR: {e}"


def rewrite_titles(issues: list[dict], rows: list[dict]) -> list[dict]:
    """
    For each URL with missing/bad title, ask the model to write a good one.
    Returns list of {url, old, new} dicts.
    """
    # find URLs needing title fixes
    bad_urls = set()
    for issue in issues:
        if issue["type"] in ("missing_title", "title_too_long", "title_too_short"):
            bad_urls.update(issue["affected_urls"])

    if not bad_urls:
        return []

    # build a lookup: url -> row
    row_map = {r["Address"]: r for r in rows}
    fixes = []

    for url in list(bad_urls)[:20]:  # cap at 20 to save quota
        row = row_map.get(url, {})
        old_title = (row.get("Title 1", "") or "").strip()
        h1 = (row.get("H1-1", "") or "").strip()
        meta = (row.get("Meta Description 1", "") or "").strip()
        path = url.split("/")[-1].replace("-", " ").replace("_", " ").strip() or url

        prompt = (
            f"Write an SEO page title for this webpage.\n"
            f"URL path: {path}\n"
            f"H1 heading: {h1 or 'not available'}\n"
            f"Meta description: {meta[:100] if meta else 'not available'}\n"
            f"Current title: {old_title or 'missing'}\n\n"
            f"Rules: under 60 characters, descriptive, no clickbait.\n"
            f"Reply with ONLY the title text, nothing else."
        )

        new_title = _ask(prompt)

        # validate length — re-ask once if too long
        if len(new_title) > 65 and not new_title.startswith("ERROR"):
            new_title = _ask(
                f"Shorten this page title to under 60 characters. "
                f"Reply with ONLY the title text: {new_title}"
            )

        fixes.append({"url": url, "old": old_title, "new": new_title[:65]})

    return fixes


def build_redirect_map(issues: list[dict], rows: list[dict]) -> list[dict]:
    """
    For each broken link (4xx), find the closest live page and suggest a redirect.
    Returns list of {from, to, reason} dicts.
    """
    broken = []
    for issue in issues:
        if issue["type"] == "broken_link":
            broken = issue["affected_urls"]
            break

    if not broken:
        return []

    # get all live URLs as candidates
    live_urls = [r["Address"] for r in rows
                 if str(r.get("Status Code", "")).strip() == "200"]

    redirect_map = []
    for bad_url in broken[:15]:  # cap at 15
        # simple heuristic: find live URL with most path overlap
        bad_parts = set(bad_url.lower().replace("-", " ").replace("/", " ").split())
        best, best_score = None, 0
        for live in live_urls:
            live_parts = set(live.lower().replace("-", " ").replace("/", " ").split())
            score = len(bad_parts & live_parts)
            if score > best_score:
                best, best_score = live, score

        to_url = best or (live_urls[0] if live_urls else "/")
        redirect_map.append({
            "from": bad_url,
            "to": to_url,
            "reason": f"404 page — redirected to closest matching live URL"
        })

    return redirect_map

def rewrite_metas(issues: list[dict], rows: list[dict]) -> list[dict]:
    """
    For each URL with missing/long meta description, write a good one.
    Returns list of {url, old, new} dicts.
    """
    bad_urls = set()
    for issue in issues:
        if issue["type"] in ("missing_meta_description", "meta_description_too_long"):
            bad_urls.update(issue["affected_urls"])

    if not bad_urls:
        return []

    row_map = {r["Address"]: r for r in rows}
    fixes = []

    for url in list(bad_urls)[:15]:
        row = row_map.get(url, {})
        old_meta = (row.get("Meta Description 1", "") or "").strip()
        title = (row.get("Title 1", "") or "").strip()
        h1 = (row.get("H1-1", "") or "").strip()
        path = url.split("/")[-1].replace("-", " ").replace("_", " ").strip() or url

        prompt = (
            f"Write an SEO meta description for this webpage.\n"
            f"URL path: {path}\n"
            f"Page title: {title or 'not available'}\n"
            f"H1 heading: {h1 or 'not available'}\n"
            f"Current meta: {old_meta[:100] if old_meta else 'missing'}\n\n"
            f"Rules: between 120-155 characters, descriptive, include a call to action.\n"
            f"Reply with ONLY the meta description text, nothing else."
        )

        new_meta = _ask(prompt)

        if len(new_meta) > 160 and not new_meta.startswith("ERROR"):
            new_meta = _ask(
                f"Shorten this meta description to under 155 characters. "
                f"Reply with ONLY the text: {new_meta}"
            )

        fixes.append({"url": url, "old": old_meta, "new": new_meta[:155]})

    return fixes