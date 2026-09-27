"""
Amurdat Reels Intro — 8s vertical (1080x1920) animation.

Story: a tree stands on the logo's stump, time accelerates through
day/night, the tree is cut and regrows twice (each cut on a night beat),
the final cut leaves the stump, the book and its lines grow up out of the
stump, the Old Persian script writes itself in, its translation appears,
and the wordmark locks a final frame that is the logo itself.

The stump, book, infinity lines and wordmark are the real logo artwork
(cut out by prepare_assets.py). The tree is drawn in the logo's own
vocabulary: the stump's violet fill with carved grain lines for the
trunk and limbs, and the grass-tuft leaf fans for the foliage.

Run:
    python prepare_assets.py                     # once, builds assets/
    manim -pql amurdat_intro.py AmurdatIntro     # draft
    manim -pqh amurdat_intro.py AmurdatIntro     # final
"""

import numpy as np
from PIL import Image
from manim import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_height = 8.0
config.frame_width = config.frame_height * config.pixel_width / config.pixel_height

# Palette — sampled from the logo.
PAPER = "#F9F3ED"
NIGHT = "#2A2438"
BARK = "#5D4686"
LEAF = "#8776A1"
LEAF_LIGHT = "#B3A7CC"
DIM_GOLD = "#8B7255"
BRIGHT_GOLD = "#D9B26B"
GOLD = "#B08D5A"
INK = "#4A3B7A"

config.background_color = PAPER

EMBLEM_PATH = "assets/emblem.png"
WORDMARK_PATH = "assets/wordmark.png"

# Emblem image geometry, in its own pixels (see prepare_assets.py).
EMBLEM_PX = (357, 440)
FACE_PX = (180.0, 313.5)      # stump cut-face ellipse center
FACE_A_PX, FACE_B_PX = 135.0, 22.5
STUMP_CARVES_PX = (75.0, 102.0, 142.0, 188.0, 252.5)  # carved lines at the body's top
SCRIPT_PX = (179.5, 209.5)    # center of the erased script band
SCRIPT_W_PX = 309.0
REVEAL_FEATHER_PX = 45.0

# Final layout: emblem, then the wordmark slot below it, centered as a block.
EMBLEM_HEIGHT = 3.8
WORDMARK_WIDTH = 2.81
WORDMARK_GAP = 0.63
BLOCK_CENTER_Y = 0.3

S = EMBLEM_HEIGHT / EMBLEM_PX[1]
_block_h = EMBLEM_HEIGHT + WORDMARK_GAP + WORDMARK_WIDTH * 58 / 590
EMBLEM_TOP = BLOCK_CENTER_Y + _block_h / 2
EMBLEM_CENTER = np.array([0, EMBLEM_TOP - EMBLEM_HEIGHT / 2, 0])


def px(u, v):
    """Emblem pixel coordinates -> scene coordinates."""
    return np.array([(u - EMBLEM_PX[0] / 2) * S, EMBLEM_TOP - v * S, 0])


FACE = px(*FACE_PX)
FACE_A, FACE_B = FACE_A_PX * S, FACE_B_PX * S


def F(n):
    """n frames, in seconds."""
    return n / config.frame_rate


def rot(v, a):
    c, s = np.cos(a), np.sin(a)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1], 0])


# ========================================================================
# Tree, drawn in the logo's vocabulary
# ========================================================================

def bezier(p0, c, p1, n):
    ts = np.linspace(0, 1, n)[:, None]
    return (1 - ts) ** 2 * p0 + 2 * (1 - ts) * ts * c + ts ** 2 * p1


def tapered_limb(p0, c, p1, w0, w1, n=16):
    """A filled limb whose width tapers from w0 to w1 along a curve."""
    pts = bezier(p0, c, p1, n)
    ts = np.linspace(0, 1, n)
    tang = 2 * (1 - ts)[:, None] * (c - p0) + 2 * ts[:, None] * (p1 - c)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True)
    nrm = np.stack([-tang[:, 1], tang[:, 0], np.zeros(n)], axis=1)
    half = ((w0 + (w1 - w0) * ts) / 2)[:, None]
    outline = list(pts + nrm * half) + list((pts - nrm * half)[::-1])
    return Polygon(*outline, fill_color=BARK, fill_opacity=1, stroke_width=0)


def leaf(base, angle, length, width, color):
    """The logo's grass-tuft leaf: a filled lens with pointed tips, its
    base at `base`, pointing along `angle`."""
    t = np.linspace(0, 1, 12)
    xs = length * t
    ys = width / 2 * np.sin(np.pi * t)
    pts = [np.array([x, y, 0]) for x, y in zip(xs, ys)]
    pts += [np.array([x, -y, 0]) for x, y in zip(xs[::-1][1:-1], ys[::-1][1:-1])]
    shape = Polygon(*pts, fill_color=color, fill_opacity=1, stroke_width=0)
    return shape.rotate(angle, about_point=ORIGIN).shift(base)


def make_tree(trunk_h, crown_w, crown_h, leaf_size, n_leaves, seed, bg):
    """Returns (cap, trunk, crown). cap hides the stump's cut face while a
    tree stands on it; trunk and crown sit above."""
    rng = np.random.default_rng(seed)
    base = FACE
    top_half = FACE_A * 0.42

    # Exactly the face's width (no ears past the stump's edges), and a
    # little taller so it overlaps the body's top edge and hides the seam.
    cap = Ellipse(width=2 * FACE_A, height=2 * FACE_B + 8 * S,
                  fill_color=BARK, fill_opacity=1, stroke_width=0).move_to(base)

    # Concave sides continuing the stump's root flare. Leaving the face's
    # tips at ~60° keeps them outside its (very flat) upper arc, so the
    # trunk swallows the cap's upper half and no lip shows.
    left = bezier(base + LEFT * FACE_A, base + LEFT * FACE_A * 0.62 + UP * trunk_h * 0.55,
                  base + LEFT * top_half + UP * trunk_h, 20)
    right = left * np.array([-1, 1, 1]) + np.array([2 * base[0], 0, 0])
    body = Polygon(*left, *right[::-1], fill_color=BARK, fill_opacity=1, stroke_width=0)

    # Grain lines start exactly where the stump's own carved lines begin,
    # so they read as the same cracks running up the trunk.
    grain = VGroup()
    for u in STUMP_CARVES_PX:
        f = (u - FACE_PX[0]) / FACE_A_PX
        p0 = px(u, FACE_PX[1] + FACE_B_PX + 5)
        p1 = base + RIGHT * top_half * f + UP * trunk_h * rng.uniform(0.8, 1.0)
        c = base + RIGHT * top_half * f * 1.15 + UP * trunk_h * 0.3
        line = VMobject(stroke_width=2.2).set_points_smoothly(list(bezier(p0, c, p1, 6)))
        line.add_updater(lambda m: m.set_stroke(color=bg.get_fill_color()))
        grain.add(line)
    trunk = VGroup(body, grain)

    top = base + UP * trunk_h
    crown_c = top + UP * crown_h * 0.62
    crotch = Ellipse(width=top_half * 2.1, height=top_half * 0.9,
                     fill_color=BARK, fill_opacity=1, stroke_width=0).move_to(top)
    limbs = VGroup(crotch)
    for dx, dy, w0 in ((-1.0, 0.55, 0.42), (1.0, 0.6, 0.42), (-0.3, 1.0, 0.34), (0.35, 0.95, 0.34)):
        p0 = top + RIGHT * dx * top_half * 0.5
        p1 = crown_c + RIGHT * dx * crown_w * 0.3 + UP * (dy - 0.7) * crown_h * 0.5
        c = top + RIGHT * dx * crown_w * 0.12 + UP * crown_h * 0.2
        limbs.add(tapered_limb(p0, c, p1, w0, 0.04))

    # Foliage: a dense mass of the grass-tuft leaf, each pointing away from
    # a hub below the crown's center so the silhouette reads as fans.
    hub = crown_c + DOWN * crown_h * 0.35
    shades = []
    for _ in range(n_leaves):
        r = np.sqrt(rng.random())
        th = rng.uniform(0, TAU)
        p = crown_c + np.array([np.cos(th) * r * crown_w / 2, np.sin(th) * r * crown_h / 2, 0])
        ang = np.arctan2(p[1] - hub[1], p[0] - hub[0]) + rng.uniform(-0.45, 0.45)
        height_t = (p[1] - (crown_c[1] - crown_h / 2)) / crown_h
        tone = height_t * 0.8 + r * 0.3 + rng.uniform(-0.25, 0.25)
        color = BARK if tone < 0.35 else LEAF if tone < 0.72 else LEAF_LIGHT
        size = leaf_size * rng.uniform(0.75, 1.1)
        shades.append((tone, leaf(p - rot(RIGHT, ang) * size * 0.4, ang, size, size * 0.3, color)))
    shades.sort(key=lambda t: t[0])
    leaves = VGroup(*[m for _, m in shades])

    crown = VGroup(limbs, leaves)
    crown.pivot = top
    return cap, trunk, crown


def make_script(center, width, color):
    """The logo's Old Persian text, stroke-only so it writes in as linework."""
    s = Text("\U000103BA\U000103C1\U000103D1\U000103A2 \U000103A0\U000103B6\U000103BC\U000103AB"
             "\U000103A0 \U000103AD\U000103A0\U000103B4\U000103A0", font="Noto Sans Old Persian")
    s.set_fill(opacity=0).set_stroke(color=color, width=1.6, opacity=1)
    s.width = width
    return s.move_to(center)


class EmblemReveal:
    """The emblem image with a movable reveal front: everything at or below
    the stump's cut face is always shown; above it, pixels appear as
    `height` (pixels above the face) passes them, with a soft edge."""

    def __init__(self):
        self.rgba = np.array(Image.open(EMBLEM_PATH).convert("RGBA"))
        h, w = self.rgba.shape[:2]
        vv, uu = np.mgrid[0:h, 0:w].astype(float)
        cx, cy = FACE_PX
        rel = np.clip(1 - ((uu - cx) / FACE_A_PX) ** 2, 0, 1)
        arc_top = np.where(np.abs(uu - cx) < FACE_A_PX, cy - FACE_B_PX * np.sqrt(rel), cy)
        self.above = arc_top - vv
        self.full_height = cy + REVEAL_FEATHER_PX
        self.mob = ImageMobject(self.frame(0))
        self.mob.height = EMBLEM_HEIGHT
        self.mob.move_to(EMBLEM_CENTER)

    def frame(self, height):
        k = np.clip((height - self.above) / REVEAL_FEATHER_PX, 0, 1)
        k[self.above <= 0] = 1
        out = self.rgba.copy()
        out[..., 3] = (self.rgba[..., 3] * k).astype(np.uint8)
        return out

    def set(self, height):
        self.mob.pixel_array = self.frame(height)


# ========================================================================
# Scene
# ========================================================================

class AmurdatIntro(Scene):
    def construct(self):
        bg = Rectangle(width=config.frame_width + 0.5, height=config.frame_height + 0.5,
                       stroke_width=0, fill_color=PAPER, fill_opacity=1)
        bg.set_z_index(-10)
        self.add(bg)

        emblem = EmblemReveal()

        def grow(cap, trunk, crown, n):
            trunk.save_state()
            trunk.stretch(0.02, 1, about_point=FACE)
            crown.save_state()
            crown.scale(0.05, about_point=crown.pivot)
            self.add(cap, trunk, crown)
            self.play(AnimationGroup(FadeIn(cap), Restore(trunk), Restore(crown), lag_ratio=0.3),
                      run_time=F(n), rate_func=smooth)

        def cut(cap, trunk, crown, n):
            above = Group(trunk, crown)
            pivot = FACE + RIGHT * FACE_A
            self.remove(cap)
            self.play(above.animate.rotate(-0.5, about_point=pivot)
                      .shift(RIGHT * 0.35 + DOWN * 0.25).set_opacity(0),
                      run_time=F(n), rate_func=rush_into)
            self.remove(trunk, crown)

        # ---- Beat 1 (0.0-0.5) Establish: full tree on the stump ----------
        cap, trunk, crown = make_tree(1.3, 3.9, 2.1, 0.36, 320, seed=3, bg=bg)
        self.add(emblem.mob, cap, trunk, crown)
        self.wait(F(15))

        # ---- Beat 2 (0.5-2.0) Day/night, accelerating ----------------------
        for i, half in enumerate((7, 6, 5, 4)):
            sway = 0.03 if i % 2 == 0 else -0.03
            self.play(bg.animate.set_fill(NIGHT),
                      Rotate(crown, sway, about_point=crown.pivot),
                      run_time=F(half), rate_func=smooth)
            self.play(bg.animate.set_fill(PAPER),
                      Rotate(crown, -sway, about_point=crown.pivot),
                      run_time=F(half), rate_func=smooth)
        self.wait(F(1))

        # ---- Beat 3 (2.0-4.0) Cut on the night beat, regrow — twice ------
        for size in ((0.75, 2.4, 1.35, 0.28, 120, 5), (1.0, 3.1, 1.75, 0.32, 200, 6)):
            self.play(bg.animate.set_fill(NIGHT), run_time=F(5))
            cut(cap, trunk, crown, 5)
            self.play(bg.animate.set_fill(PAPER), run_time=F(5))
            cap, trunk, crown = make_tree(*size, bg=bg)
            grow(cap, trunk, crown, 15)

        # ---- Beat 4 (4.0-4.5) Final cut — only the stump remains ---------
        cut(cap, trunk, crown, 10)
        self.wait(F(5))

        # ---- Beat 5 (4.5-5.5) Book grows up out of the stump -------------
        height = ValueTracker(0)
        emblem.mob.add_updater(lambda m: emblem.set(height.get_value()))
        self.play(height.animate.set_value(emblem.full_height), run_time=F(30), rate_func=smooth)
        emblem.mob.clear_updaters()

        # ---- Beat 6 (5.5-6.5) Script writes in, dim to bright gold -------
        script = make_script(px(*SCRIPT_PX), SCRIPT_W_PX * S, DIM_GOLD)
        self.play(Write(script), run_time=F(21))
        self.play(script.animate.set_stroke(color=BRIGHT_GOLD), run_time=F(9))

        # ---- Beat 7 (6.5-6.8) Script settles to its resting gold ---------
        self.play(script.animate.set_stroke(color=GOLD), run_time=F(9))

        # ---- Beat 8 (6.8-7.6) Translation fades in, in the wordmark slot -
        wordmark = ImageMobject(WORDMARK_PATH)
        wordmark.width = WORDMARK_WIDTH
        wordmark.next_to(emblem.mob, DOWN, buff=WORDMARK_GAP)
        translation = Text("“Knowledge is the only Immortal”",
                           font="Noto Serif", slant=ITALIC, color=INK)
        translation.width = WORDMARK_WIDTH * 0.95
        translation.move_to(wordmark)
        self.play(FadeIn(translation, shift=UP * 0.06), run_time=F(24))

        # ---- Beat 9 (7.6-8.0) Wordmark replaces translation; hold --------
        self.play(FadeOut(translation, run_time=F(3)), FadeIn(wordmark, run_time=F(6)))
        self.wait(F(6))
