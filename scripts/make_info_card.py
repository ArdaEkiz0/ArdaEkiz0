"""Neofetch-style info card for ArdaEkiz0. Lines fade/slide in on load."""
import os

BASE = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(BASE, "info-card.svg")

BG, FG, MUTED = "#0d1117", "#e6edf3", "#7d8590"
GREEN, BLUE, YELLOW, CYAN = "#39d353", "#58a6ff", "#e3b341", "#39c5cf"

ROWS = [
    ("Now", "SMMM · building tax & accounting automation", GREEN),
    ("Focus", "e-Invoice · KDV cross-check · ledger bots", BLUE),
    ("Stack", "Python · Playwright · Tkinter · SQLite", CYAN),
    ("Ship", "kdv-check v2.9 · luca-mizan · e-kesinti", YELLOW),
]

lines = []
y = 78
for i, (k, v, color) in enumerate(ROWS):
    delay = round(0.35 + i * 0.3, 2)
    lines.append(
        f'<g class="row" style="animation-delay:{delay}s">'
        f'<text x="28" y="{y}" fill="{color}" font-size="13" font-weight="bold">{k}</text>'
        f'<text x="92" y="{y}" fill="{MUTED}" font-size="13">›</text>'
        f'<text x="112" y="{y}" fill="{FG}" font-size="12">{v}</text></g>'
    )
    y += 30

# escape XML specials in values
svg_body = "\n".join(lines).replace("&", "&amp;")

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="490" height="300" viewBox="0 0 490 300" role="img" aria-label="About Arda M. Ekiz">
<style>
text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
.row {{ opacity: 0; transform: translateX(10px); animation: slide .5s ease-out forwards; }}
@keyframes slide {{ to {{ opacity: 1; transform: translateX(0); }} }}
@media (prefers-reduced-motion: reduce) {{ .row {{ animation: none; opacity: 1; transform: none; }} }}
</style>
<rect width="490" height="300" rx="10" fill="{BG}"/>
<circle cx="26" cy="26" r="5" fill="#ff5f56"/>
<circle cx="44" cy="26" r="5" fill="#ebbd2e"/>
<circle cx="62" cy="26" r="5" fill="#27c93f"/>
<text x="245" y="30" fill="{MUTED}" font-size="12" text-anchor="middle">arda@github ~ $ whoami</text>
<text x="28" y="58" fill="{GREEN}" font-size="14" font-weight="bold">Arda M. Ekiz</text>
<text x="150" y="58" fill="{MUTED}" font-size="12">— SMMM · Software Developer · TR</text>
{svg_body}
<text x="28" y="262" fill="{MUTED}" font-size="11">python · javascript · sqlite · git · vscode</text>
</svg>
"""
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(f"wrote {OUT}")
