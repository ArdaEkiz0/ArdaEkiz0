"""Self-typing motto line. SMIL clip wipe (same proven pattern as the
portrait) + blinking block cursor. Freezes with full text visible."""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "typing.svg")
BG, FG, CURSOR = "#0d1117", "#39d353", "#39d353"
TEXT = "building tax tools that file themselves"
FS = 22
CHAR_W = FS * 0.602
TW = len(TEXT) * CHAR_W
X0 = round((860 - TW) / 2)
BASE = 36

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="860" height="56" viewBox="0 0 860 56" role="img" aria-label="{TEXT}">
<rect width="860" height="56" rx="10" fill="{BG}"/>
<clipPath id="typeclip"><rect x="0" y="0" width="0" height="56"><animate attributeName="width" from="0" to="860" dur="2.2s" fill="freeze"/></rect></clipPath>
<text x="{X0}" y="{BASE}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FS}" fill="{FG}" clip-path="url(#typeclip)">$ {TEXT}</text>
<rect x="{X0 + 2 * CHAR_W + TW:.0f}" y="{BASE - 17}" width="12" height="22" fill="{CURSOR}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>
</svg>
"""
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(f"wrote {OUT}")
