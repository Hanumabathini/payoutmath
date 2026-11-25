#!/usr/bin/env python3
"""Weekly fee watchdog.

Fetches every platform's fee source page and checks that the numbers the site
relies on still appear there. Prints a report and exits 1 if anything looks
changed or unreachable, so the GitHub Action can open an issue.
It never edits fees.json itself: a human (or Claude) checks the change first.
"""
import json, re, sys, urllib.request
from pathlib import Path

FEES = json.loads((Path(__file__).resolve().parent.parent / "data/fees.json").read_text())
UA = "Mozilla/5.0 (compatible; PayoutMath-fee-check/1.0)"
problems, ok, unreachable = [], [], []

for key, p in FEES["platforms"].items():
    try:
        req = urllib.request.Request(p["source"], headers={"User-Agent": UA})
        text = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        text = re.sub(r"<[^>]+>", " ", text)
    except Exception as e:  # unreachable is reported, not fatal on its own
        unreachable.append(f"- **{p['name']}**: could not fetch {p['source']} ({e.__class__.__name__}). Check it by hand.")
        continue
    missing = [s for s in p.get("monitor_strings", []) if s not in text]
    if missing:
        problems.append(f"- **{p['name']}**: no longer shows {', '.join(missing)} on {p['source']}. The fee may have changed.")
    else:
        ok.append(p["name"])

print("Fee check, last manual check " + FEES["checked"])
print("Unchanged: " + (", ".join(ok) or "none"))
if unreachable:
    print("\nCould not reach (some sites block automated checks):\n" + "\n".join(unreachable))
if problems:
    print("\nNeeds a look:\n" + "\n".join(problems))
# A changed fee, or every page unreachable, opens an issue.
if problems or len(unreachable) == len(FEES["platforms"]):
    sys.exit(1)
