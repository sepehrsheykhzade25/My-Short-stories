"""
Amurdat Reels Intro — 8s vertical (1080x1920) animation.

Story: a tree stands on the logo's stump, time accelerates through
day/night, the tree is cut and regrows twice (each cut on a night beat),
the final cut leaves the stump, the book and its lines grow up out of the
stump, the Old Persian script writes itself in, and the tagline and
AMURDAT wordmark settle beneath a final frame that is the logo itself.

The stump, book, infinity lines and wordmark are the real logo artwork
(cut out by prepare_assets.py). The tree is drawn in the logo's own
vocabulary: the stump's violet fill with carved grain lines for the
trunk and limbs, and the grass-tuft leaf for the foliage.

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
DUSK = "#1E1A33"
DUSK_OPACITY = 0.5            # night dims the whole scene, it doesn't black it out
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
SCRIPT_PX = (179.5, 210.0)    # center of the script band
SCRIPT_W_PX = 309.0
REVEAL_FEATHER_PX = 45.0

K = 0.75                      # overall scale of the logo, tree and type

# Trees: (trunk height, crown width, crown height, leaf size, leaf count),
# in scene units at K=1.
FULL_TREE = (1.3, 3.9, 2.1, 0.36, 320)
SPROUT = (0.9, 1.25, 1.0, 0.24, 55)
BROAD_TREE = (1.15, 3.5, 1.5, 0.34, 240)

EMBLEM_HEIGHT = 3.8 * K
S = EMBLEM_HEIGHT / EMBLEM_PX[1]

# Place the emblem so the full-grown tree (stump roots to crown top) sits
# dead center in the frame.
_trunk_h, _, _crown_h, _leaf, _ = FULL_TREE
_tree_h = ((EMBLEM_PX[1] - FACE_PX[1]) * S
           + K * (_trunk_h + _crown_h * 1.12 + _leaf * 0.66))
EMBLEM_TOP = -_tree_h / 2 + EMBLEM_HEIGHT
EMBLEM_CENTER = np.array([0, EMBLEM_TOP - EMBLEM_HEIGHT / 2, 0])

TAGLINE_WIDTH = 2.67 * K
WORDMARK_WIDTH = 0.86 * K


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


def make_trunk(trunk_h, rng):
    """A full-width trunk continuing the stump's root flare, plus the cap
    that hides the cut face beneath it."""
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
        grain.add(VMobject(stroke_color=PAPER, stroke_width=2.2 * K)
                  .set_points_smoothly(list(bezier(p0, c, p1, 6))))
    return VGroup(cap), VGroup(body, grain), top_half


def make_sprout(trunk_h):
    """A young shoot rising from the middle of the cut face; the rings
    stay visible around it."""
    stem = tapered_limb(FACE + DOWN * FACE_B * 0.3, FACE + UP * trunk_h * 0.5 + RIGHT * 0.04,
                        FACE + UP * trunk_h, 0.16 * K, 0.07 * K)
    return VGroup(), VGroup(stem), 0.05 * K


def make_tree(size, seed, sprout=False):
    """Returns (cap, trunk, crown). cap hides the stump's cut face while a
    full trunk stands on it; trunk and crown sit above."""
    trunk_h, crown_w, crown_h, leaf_size, n_leaves = [v * K for v in size[:4]] + [size[4]]
    rng = np.random.default_rng(seed)
    cap, trunk, top_half = make_sprout(trunk_h) if sprout else make_trunk(trunk_h, rng)

    top = FACE + UP * trunk_h
    crown_c = top + UP * crown_h * 0.62
    crotch = Ellipse(width=max(top_half * 2.1, 0.12 * K), height=max(top_half * 0.9, 0.1 * K),
                     fill_color=BARK, fill_opacity=1, stroke_width=0).move_to(top)
    limbs = VGroup(crotch)
    limb_w = 0.42 * K if not sprout else 0.1 * K
    for dx, dy, w in ((-1.0, 0.55, 1.0), (1.0, 0.6, 1.0), (-0.3, 1.0, 0.8), (0.35, 0.95, 0.8)):
        p0 = top + RIGHT * dx * top_half * 0.5
        p1 = crown_c + RIGHT * dx * crown_w * 0.3 + UP * (dy - 0.7) * crown_h * 0.5
        c = top + RIGHT * dx * crown_w * 0.12 + UP * crown_h * 0.2
        limbs.add(tapered_limb(p0, c, p1, limb_w * w, 0.03 * K))

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
        leaf_len = leaf_size * rng.uniform(0.75, 1.1)
        shades.append((tone, leaf(p - rot(RIGHT, ang) * leaf_len * 0.4, ang,
                                  leaf_len, leaf_len * 0.3, color)))
    shades.sort(key=lambda t: t[0])
    leaves = VGroup(*[m for _, m in shades])

    crown = VGroup(limbs, leaves)
    crown.pivot = top
    return cap, trunk, crown


def make_script(center, width, color):
    """The logo's Old Persian text as gold linework. The paper fill hides
    the infinity lines behind each glyph, as in the logo."""
    s = Text("\U000103BA\U000103C1\U000103D1\U000103A2 \U000103A0\U000103B6\U000103BC\U000103AB"
             "\U000103A0 \U000103AD\U000103A0\U000103B4\U000103A0", font="Noto Sans Old Persian")
    s.set_fill(PAPER, opacity=1).set_stroke(color=color, width=1.6 * K, opacity=1)
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
        dusk = Rectangle(width=config.frame_width + 0.5, height=config.frame_height + 0.5,
                         stroke_width=0, fill_color=DUSK, fill_opacity=0)
        dusk.set_z_index(10)
        self.add(dusk)

        def night(n, anims=()):
            self.play(dusk.animate.set_fill(opacity=DUSK_OPACITY), *anims,
                      run_time=F(n), rate_func=smooth)

        def day(n, anims=()):
            self.play(dusk.animate.set_fill(opacity=0), *anims,
                      run_time=F(n), rate_func=smooth)

        emblem = EmblemReveal()

        def grow(cap, trunk, crown, n):
            trunk.save_state()
            trunk.stretch(0.02, 1, about_point=FACE)
            crown.save_state()
            crown.scale(0.05, about_point=crown.pivot)
            self.add(cap, trunk, crown)
            anims = [Restore(trunk), Restore(crown)]
            if len(cap):
                anims.insert(0, FadeIn(cap))
            self.play(AnimationGroup(*anims, lag_ratio=0.3), run_time=F(n), rate_func=smooth)

        def cut(cap, trunk, crown, n):
            above = Group(trunk, crown)
            pivot = FACE + RIGHT * FACE_A
            self.remove(cap)
            self.play(above.animate.rotate(-0.5, about_point=pivot)
                      .shift((RIGHT * 0.35 + DOWN * 0.25) * K).set_opacity(0),
                      run_time=F(n), rate_func=rush_into)
            self.remove(trunk, crown)

        # ---- Beat 1 (0.0-0.5) Establish: full tree on the stump ----------
        cap, trunk, crown = make_tree(FULL_TREE, seed=3)
        self.add(emblem.mob, cap, trunk, crown)
        self.wait(F(15))

        # ---- Beat 2 (0.5-2.0) Day/night: slow at first, then racing ------
        for i, half in enumerate((10, 6, 4, 2)):
            sway = 0.03 if i % 2 == 0 else -0.03
            night(half, [Rotate(crown, sway, about_point=crown.pivot)])
            day(half, [Rotate(crown, -sway, about_point=crown.pivot)])
        self.wait(F(1))

        # ---- Beat 3 (2.0-4.0) Cut on the night beat, regrow — twice ------
        # First a thin sprout from the cut face, then a broad, full tree.
        for size, seed, sprout in ((SPROUT, 5, True), (BROAD_TREE, 6, False)):
            night(5)
            cut(cap, trunk, crown, 5)
            day(5)
            cap, trunk, crown = make_tree(size, seed, sprout)
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

        # ---- Beats 8-9 (6.8-8.0) Tagline, then AMURDAT beneath it; hold --
        tagline = Text("“Knowledge is the only Immortal”",
                       font="Noto Serif", slant=ITALIC, color=INK)
        tagline.width = TAGLINE_WIDTH
        tagline.next_to(emblem.mob, DOWN, buff=0.28)
        wordmark = ImageMobject(WORDMARK_PATH)
        wordmark.width = WORDMARK_WIDTH
        wordmark.next_to(tagline, DOWN, buff=0.2)
        self.play(AnimationGroup(FadeIn(tagline, shift=UP * 0.05),
                                 FadeIn(wordmark, shift=UP * 0.05), lag_ratio=0.5),
                  run_time=F(24))
        self.wait(F(12))
