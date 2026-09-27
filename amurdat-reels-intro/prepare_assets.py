"""Cut the animation's image layers out of the reference logo.

Writes to assets/:
  emblem.png   book + infinity lines + stump; the gold script is removed
               and the lines that ran behind it are redrawn unbroken, so
               the animated script can write in over them
  wordmark.png the AMURDAT wordmark

Run:  python prepare_assets.py
"""

import numpy as np
from PIL import Image, ImageDraw

SRC = "assets/amurdat_logo_reference.jpg"
PAPER = np.array([249, 243, 237], dtype=float)

EMBLEM_BOX = (140, 105, 497, 545)
SCRIPT_ROWS = (289, 341)          # script band, erased and redrawn (logo px)
SCRIPT_COLS = (159, 481)
WORDMARK_BOX = (30, 568, 210, 626)

# Every line that crosses the script band, measured just above (y=288) and
# just below (y=342) it: (x, dx/dy) at each end, and the ink sample point.
# Loop tips also carry the logo's extreme x for that tip.
LEMNISCATE = (93, 75, 118)
FAN = (150, 140, 170)
BAND_LINES = [
    # (top x, top slope, bottom x, bottom slope, color, width px, alpha, tip x)
    (196.0, -2.2, 198.9, 2.0, LEMNISCATE, 1.35, 0.9, 183.5),   # left loop tip
    (442.8, 2.2, 439.9, -2.0, LEMNISCATE, 1.35, 0.9, 456.0),   # right loop tip
    (269.1, 3.0, 354.8, 2.7, LEMNISCATE, 1.35, 0.9, None),     # crossing, \
    (369.4, -3.0, 283.7, -2.6, LEMNISCATE, 1.35, 0.9, None),   # crossing, /
    (164.8, 0.0, 169.3, 0.15, FAN, 1.2, 0.5, None),           # outer left
    (474.3, 0.0, 469.7, -0.15, FAN, 1.2, 0.5, None),          # outer right
    (196.0, 0.05, 198.9, 0.05, FAN, 1.0, 0.4, None),    # these two run straight
    (276.4, 1.3, 283.0, -1.4, FAN, 1.0, 0.4, None),
    (362.5, -1.2, 356.5, 1.4, FAN, 1.0, 0.4, None),
    (445.0, -0.04, 443.0, -0.04, FAN, 1.0, 0.4, None),  # past the loop tips
]


def matte(rgb):
    """Alpha from distance to the paper color, then un-blend the paper out
    of edge pixels so cutouts carry no light halo over a dark background."""
    dist = np.sqrt(((rgb - PAPER) ** 2).sum(axis=2))
    a = np.clip((dist - 10.0) / 30.0, 0, 1)
    safe = np.maximum(a, 1e-3)[..., None]
    color = np.clip(PAPER + (rgb - PAPER) / safe, 0, 255)
    return np.dstack([color, a * 255]).astype(np.uint8)


def cubic(p0, t0, p3, t3, k0, k3, n=80):
    p1, p2 = p0 + t0 * k0, p3 - t3 * k3
    s = np.linspace(0, 1, n)[:, None]
    return (1 - s) ** 3 * p0 + 3 * (1 - s) ** 2 * s * p1 + 3 * (1 - s) * s ** 2 * p2 + s ** 3 * p3


def band_curve(xt, st, xb, sb, tip):
    y0, y1 = SCRIPT_ROWS[0] - 1.0, SCRIPT_ROWS[1] + 1.0
    p0, p3 = np.array([xt, y0]), np.array([xb, y1])
    t0 = np.array([st, 1.0]) / np.hypot(st, 1.0)
    t3 = np.array([sb, 1.0]) / np.hypot(sb, 1.0)
    span = np.linalg.norm(p3 - p0)
    if tip is None:
        return cubic(p0, t0, p3, t3, span * 0.4, span * 0.4)
    # Grow the handles until the curve's extreme x reaches the logo's tip.
    lo, hi = 1.0, 200.0
    for _ in range(40):
        k = (lo + hi) / 2
        xs = cubic(p0, t0, p3, t3, k, k)[:, 0]
        reach = xs.min() if tip < xt else xs.max()
        if abs(reach - xt) < abs(tip - xt):
            lo = k
        else:
            hi = k
    return cubic(p0, t0, p3, t3, lo, lo)


def draw_band_lines(emblem, ox, oy, ss=8):
    """Redraw the band's lines, supersampled for clean anti-aliasing."""
    h, w = emblem.shape[:2]
    layer = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    for xt, st, xb, sb, color, width, alpha, tip in BAND_LINES:
        pts = band_curve(xt, st, xb, sb, tip) - [ox, oy]
        ImageDraw.Draw(layer).line([tuple(p * ss) for p in pts],
                                   fill=color + (int(255 * alpha),),
                                   width=int(width * ss), joint="curve")
    layer = np.array(layer.resize((w, h), Image.LANCZOS)).astype(float)
    a = layer[..., 3:] / 255
    base_a = emblem[..., 3:] / 255
    out_a = a + base_a * (1 - a)
    out_c = (layer[..., :3] * a + emblem[..., :3] * base_a * (1 - a)) / np.maximum(out_a, 1e-6)
    return np.dstack([out_c, out_a * 255]).astype(np.uint8)


def main():
    rgb = np.array(Image.open(SRC).convert("RGB")).astype(float)
    full = matte(rgb)

    x0, y0, x1, y1 = EMBLEM_BOX
    emblem = full[y0:y1, x0:x1].copy()
    (r0, r1), (c0, c1) = SCRIPT_ROWS, SCRIPT_COLS
    emblem[r0 - y0:r1 - y0, c0 - x0:c1 - x0, 3] = 0
    emblem = draw_band_lines(emblem, x0, y0)
    Image.fromarray(emblem, "RGBA").save("assets/emblem.png")

    wx0, wy0, wx1, wy1 = WORDMARK_BOX
    Image.fromarray(full[wy0:wy1, wx0:wx1], "RGBA").save("assets/wordmark.png")


if __name__ == "__main__":
    main()
