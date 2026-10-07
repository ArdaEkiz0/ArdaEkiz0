"""Prep a headshot for ASCII conversion (run once per photo, locally).

1. rembg: remove background, 2. CLAHE: boost local contrast,
3. composite onto white so background maps to the blank end of the ramp.
Usage: python scripts/prep_photo.py source-photo.jpg
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main(src: str, dst: str = "source-prepped.png") -> None:
    img = Image.open(src).convert("RGB")
    no_bg = remove(img)
    arr = np.array(no_bg)
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3] if arr.shape[2] == 4 else None

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(gray)

    white = np.full_like(rgb, 255)
    if alpha is not None:
        mask = (alpha > 10)
        canvas = white.copy()
        canvas[mask] = np.stack([boosted] * 3, axis=-1)[mask]
    else:
        canvas = np.stack([boosted] * 3, axis=-1)
    Image.fromarray(canvas).save(dst)
    print(f"wrote {dst}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python scripts/prep_photo.py source-photo.jpg [out.png]")
        sys.exit(2)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png")
