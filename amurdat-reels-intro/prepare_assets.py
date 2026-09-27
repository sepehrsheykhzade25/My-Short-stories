"""Cut the animation's image layers out of the reference logo.

Writes to assets/:
  emblem.png   book + infinity lines + stump, script band erased
  wordmark.png AMURDAT / آموردات row

Run:  python prepare_assets.py
"""

import numpy as np
from PIL import Image

SRC = "assets/amurdat_logo_reference.jpg"
PAPER = np.array([249, 243, 237], dtype=float)

EMBLEM_BOX = (140, 105, 497, 545)
SCRIPT_BOX = (165, 295, 474, 334)
WORDMARK_BOX = (25, 568, 615, 626)


def matte(rgb):
    """Alpha from distance to the paper color, then un-blend the paper out
    of edge pixels so cutouts carry no light halo over a dark background."""
    dist = np.sqrt(((rgb - PAPER) ** 2).sum(axis=2))
    a = np.clip((dist - 10.0) / 30.0, 0, 1)
    safe = np.maximum(a, 1e-3)[..., None]
    color = np.clip(PAPER + (rgb - PAPER) / safe, 0, 255)
    return np.dstack([color, a * 255]).astype(np.uint8)


def main():
    rgb = np.array(Image.open(SRC).convert("RGB")).astype(float)
    full = matte(rgb)

    x0, y0, x1, y1 = EMBLEM_BOX
    emblem = full[y0:y1, x0:x1].copy()
    sx0, sy0, sx1, sy1 = SCRIPT_BOX
    emblem[sy0 - y0 - 6:sy1 - y0 + 6, sx0 - x0 - 6:sx1 - x0 + 6, 3] = 0
    Image.fromarray(emblem, "RGBA").save("assets/emblem.png")

    wx0, wy0, wx1, wy1 = WORDMARK_BOX
    Image.fromarray(full[wy0:wy1, wx0:wx1], "RGBA").save("assets/wordmark.png")


if __name__ == "__main__":
    main()
