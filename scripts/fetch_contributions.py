"""Fetch public contribution calendar — no token needed.

Source: https://github.com/users/<username>/contributions (same HTML
fragment the profile page itself uses). Parses day cells + tooltips and
writes data/contributions.json with raw days + derived stats.
"""
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "ArdaEkiz0")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

COUNT_RE = re.compile(r"(\d[\d,]*)\s+contributions?\b", re.I)


def parse_count(tip_text: str) -> int:
    if not tip_text or "No contributions" in tip_text:
        return 0
    m = COUNT_RE.search(tip_text)
    return int(m.group(1).replace(",", "")) if m else 0


def main() -> None:
    r = requests.get(URL, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print("ERROR: no day cells found — GitHub HTML may have changed", file=sys.stderr)
        sys.exit(1)

    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.select("tool-tip")}

    days = []
    for c in cells:
        cid = c.get("id", "")
        d = c.get("data-date", "")
        level = int(c.get("data-level", "0") or 0)
        count = parse_count(tips.get(cid, ""))
        days.append({"date": d, "count": count, "level": level})

    days.sort(key=lambda x: x["date"])
    total = sum(d["count"] for d in days)

    # streaks (active days only)
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] > 0 else 0
        longest = max(longest, cur)
    current = 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        elif d["date"] == date.today().isoformat():
            continue  # today not over yet
        else:
            break

    best = max(days, key=lambda x: x["count"])
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(
            {
                "username": USERNAME,
                "total": total,
                "current_streak": current,
                "longest_streak": longest,
                "best_day": best,
                "monthly": dict(sorted(monthly.items())),
                "days": days,
            },
            f,
            indent=2,
        )
    print(f"{USERNAME}: {total} contributions, {len(days)} days -> {OUT}")


if __name__ == "__main__":
    main()
