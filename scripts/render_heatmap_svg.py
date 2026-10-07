"""Render data/contributions.json as an animated GitHub-style heatmap SVG.

53-week x 7-day grid of rounded boxes. Reveal plays once on load with a
diagonal slide-down (CSS keyframes, frozen end-state — no looping), so it
animates inside a GitHub README via <img>. No JS, no external assets.
"""
import json
import os
from datetime import date

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(BASE, "data", "contributions.json")
OUT = os.path.join(BASE, "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP, STEP = 11, 3, 14
LEFT, TOP = 59, 34  # (860 - 53*14) / 2: heatmap spans full 860 width
BG, FG, MUTED = "#0d1117", "#e6edf3", "#7d8590"
ACCENT = "#39d353"


def main() -> None:
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    days = data["days"]
    # group into week columns (Mon-first); pad first column
    weeks: list[list] = []
    col: list = []
    # GitHub calendar starts Sunday; keep simple chronological chunking by 7
    # aligned to the actual weekday of the first day.
    from datetime import datetime
    first_wd = datetime.strptime(days[0]["date"], "%Y-%m-%d").weekday()  # Mon=0
    # convert to Sun=0 grid
    first_sun = (first_wd + 1) % 7
    col = [None] * first_sun
    for d in days:
        col.append(d)
        if len(col) == 7:
            weeks.append(col)
            col = []
    if col:
        col += [None] * (7 - len(col))
        weeks.append(col)
    weeks = weeks[-53:]  # classic 53-week window

    w = LEFT + 53 * STEP + LEFT
    h = TOP + 7 * STEP + 62
    assert w == 860, w  # keep aligned with the 370 + 490 columns below

    rects = []
    for ci, week in enumerate(weeks):
        for ri, d in enumerate(week):
            x, y = LEFT + ci * STEP, TOP + ri * STEP
            if d is None:
                fill, tip = "#0d1117", ""
            else:
                fill = PALETTE[min(d["level"], 4)]
                tip = f"{d['date']}: {d['count']}"
            delay = round((ci * 7 + ri) * 0.004, 3)  # diagonal reveal
            rects.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{fill}" class="cell" style="animation-delay:{delay}s">'
                f"<title>{tip}</title></rect>"
            )

    total = data["total"]
    today = date.today().isoformat()
    footer = (f"{total:,} contributions in the last year"
              f"  ·  {data['longest_streak']}-day best streak  ·  updated {today}")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Contribution heatmap for {data['username']}">
<style>
text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
.cell {{ opacity: 0; transform: translateY(-6px); animation: drop .45s ease-out forwards; }}
@keyframes drop {{ to {{ opacity: 1; transform: translateY(0); }} }}
@media (prefers-reduced-motion: reduce) {{ .cell {{ animation: none; opacity: 1; transform: none; }} }}
</style>
<rect width="{w}" height="{h}" rx="10" fill="{BG}"/>
<text x="{LEFT}" y="20" fill="{FG}" font-size="13">contributions · {data['username']}</text>
<text x="{w - 12}" y="20" fill="{MUTED}" font-size="11" text-anchor="end">Less {" ".join(f'&#9632;' for _ in PALETTE)} More</text>
{"".join(rects)}
<text x="{LEFT}" y="{h - 22}" fill="{MUTED}" font-size="11">{footer}</text>
<text x="{w - 12}" y="{h - 22}" fill="{ACCENT}" font-size="11" text-anchor="end">self-rendered SVG · no tracker</text>
</svg>
"""
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(weeks)} weeks)")


if __name__ == "__main__":
    main()
