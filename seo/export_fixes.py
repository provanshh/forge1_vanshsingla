"""
export_fixes.py — write fix artifacts to outputs/
  - outputs/fixes_titles.csv   (rewritten titles)
  - outputs/fixes_redirects.csv (redirect map)
"""
from __future__ import annotations
import csv, os

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")


def write_titles_csv(titles: list[dict]) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, "fixes_titles.csv")
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["url", "old", "new"])
        w.writeheader()
        w.writerows(titles)
    return p


def write_redirects_csv(redirect_map: list[dict]) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, "fixes_redirects.csv")
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["from", "to", "reason"])
        w.writeheader()
        w.writerows(redirect_map)
    return p