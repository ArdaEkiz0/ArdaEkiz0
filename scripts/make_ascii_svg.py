"""Convert the prepped photo to a self-typing monochrome ASCII SVG.

Downsamples to a char grid, maps brightness through a density ramp
(bright -> sparse, dark -> dense), one fill color. Each row wipes in
left-to-right with a cursor block, top to bottom, then freezes (SMIL).
Usage: python scripts/make_ascii_svg.py [source-prepped.png]
"""
import sys

from PIL import Image

RAMP = " .`:-=+*cs#%@"
COLS, ROWS = 58, 40
OUT = "avi-ascii.svg"
FILL, BG = "#c9d1d9", "#0d1117"


def main(src: str = "source-prepped.png") -> None:
    img = Image.open(src).convert("L")
    # autocrop white margins so the subject fills the panel
    import numpy as np
    a = np.array(img)
    ys, xs = np.where(a < 245)
    if len(xs):
        x0, x1 = max(int(xs.min()) - 6, 0), min(int(xs.max()) + 6, img.width)
        y0, y1 = max(int(ys.min()) - 6, 0), min(int(ys.max()) + 6, img.height)
        img = img.crop((x0, y0, x1, y1))
    img = img.resize((COLS, ROWS))
    px = img.load()
    n = len(RAMP)
    lines = []
    for r in range(ROWS):
        # dark -> dense (@), bright -> blank (space): invert brightness
        line = "".join(
            RAMP[min((255 - int(px[c, r])) * n // 256, n - 1)]
            for c in range(COLS)
        ).rstrip()
        lines.append(line)

    row_h, top = 6.95, 12
    h = 300  # match info-card height so the two columns align
    parts = []
    for i, line in enumerate(lines):
        esc = line.replace("&", "&amp;").replace("<", "&lt;")
        dur, begin = 0.28, round(i * 0.045, 3)
        baseline = top + i * row_h
        clip_y = round(baseline - 8, 1)
        parts.append(
            f'<g><clipPath id="clip{i}"><rect x="0" y="{clip_y}" width="0" height="10">'
            f'<animate attributeName="width" from="0" to="370" dur="{dur}s" '
            f'begin="{begin}s" fill="freeze"/></rect></clipPath>'
            f'<text x="8" y="{baseline:.1f}" font-size="7" '
            f'fill="{FILL}" clip-path="url(#clip{i})">{esc if esc else " "}</text></g>'
        )
    total = round(ROWS * 0.045 + 0.4, 2)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="370" height="{h:.0f}" '
        f'viewBox="0 0 370 {h:.0f}" role="img" aria-label="ASCII portrait">'
        f'<rect width="370" height="{h:.0f}" rx="10" fill="{BG}"/>'
        f'<g font-family="ui-monospace,Menlo,Consolas,monospace">'
        + "".join(parts) +
        f'<rect width="370" height="{h:.0f}" fill="none">'
        f'<animate attributeName="opacity" values="1;1" dur="{total}s" fill="freeze"/>'
        f"</rect></g></svg>"
    )
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f"wrote {OUT} ({COLS}x{ROWS})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png")
