#!/usr/bin/env python3
"""
run.py — headless runner for the SEO Command Center (also the grader's entry point).
"""
from __future__ import annotations
import argparse, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mcp"))
sys.path.insert(0, HERE)
import server

sys.path.insert(0, os.path.join(HERE, "seo"))
from fixer import rewrite_titles, build_redirect_map


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export_dir")
    ap.add_argument("--no-dashboard", action="store_true")
    ap.add_argument("--no-fixes", action="store_true", help="skip AI fix calls")
    args = ap.parse_args()

    if not args.no_dashboard:
        server.start_dashboard()
        print(f"[seo] dashboard: http://localhost:{server.PORT}", flush=True)
        time.sleep(1)

    t0 = time.time()

    # 1. load
    server.seo_load(args.export_dir)
    print(f"[seo] loaded {server.RUN['urls']} URLs from {args.export_dir}", flush=True)

    # 2. detect
    server.seo_detect()
    issues = server.RUN["issues"]
    print(f"[seo] detected {len(issues)} issue types", flush=True)

    # 3. AI fixes (skip with --no-fixes or if ollama not running)
    titles_fixes = []
    redirect_map = []
    if not args.no_fixes:
        print("[seo] running AI fixes (title rewrites + redirect map)...", flush=True)
        try:
            titles_fixes = rewrite_titles(issues, server.RUN["rows"])
            print(f"[seo] rewrote {len(titles_fixes)} titles", flush=True)
            redirect_map = build_redirect_map(issues, server.RUN["rows"])
            print(f"[seo] built redirect map: {len(redirect_map)} entries", flush=True)
        except Exception as e:
            print(f"[seo] fix step skipped ({e})", flush=True)
    server.seo_set_fixes(titles_fixes, redirect_map)
    server.RUN["model_calls"] = len(titles_fixes) + len(redirect_map)

    # 4. recommendations
    sorted_issues = sorted(issues, key=lambda x: {"High":0,"Medium":1,"Low":2}.get(x["severity"],3))
    recs = []
    for i in sorted_issues[:5]:
        recs.append(f"Fix {i['count']} {i['severity']}-severity '{i['type']}' issue(s) — affects {i['count']} URLs.")
    if not recs:
        recs.append("No issues detected on this crawl.")
    server.seo_recommend(recs)

    # 5. write outputs
    server.RUN["duration_sec"] = round(time.time() - t0, 1)
    server.seo_report()
    server.seo_export()

    s = server.RUN["summary"]
    print("\n=== SEO AUDIT RESULT ===")
    print(f"Site         : {server.RUN['site']}  ({server.RUN['urls']} URLs)")
    print(f"Total issues : {s['total_issues']}  (High {s['by_severity'].get('High',0)} / "
          f"Medium {s['by_severity'].get('Medium',0)} / Low {s['by_severity'].get('Low',0)})")
    print(f"Title fixes  : {len(titles_fixes)}")
    print(f"Redirect map : {len(redirect_map)} entries")
    print(f"Duration     : {server.RUN['duration_sec']}s")
    print("Wrote outputs/report.json and outputs/report.html")


if __name__ == "__main__":
    main()
    