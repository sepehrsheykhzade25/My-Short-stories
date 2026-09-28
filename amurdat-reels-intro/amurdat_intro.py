"""
Amurdat Reels Intro — 10s vertical (1080x1920) animation.

Story: a tree stands on the logo's stump while the sun and stars wheel
around it, faster and faster; the tree is cut and regrows twice (each cut
at midnight), the final cut leaves the stump, the logo's lines draw
themselves up out of the stump and the book fades in above them, the Old
Persian script writes itself in, and the tagline and AMURDAT wordmark
settle beneath a final frame that holds for two seconds.

The stump, book, infinity lines and wordmark are the real logo artwork
(cut out by prepare_assets.py). The tree, sun and stars are drawn in the
logo's own vocabulary: the stump's violet fill and carved lines, the
grass-tuft leaf shape, the stump's growth rings and the script's gold.

Run:
    python prepare_assets.py                     # once, builds assets/
    manim -pql amurdat_intro.py AmurdatIntro     # draft
    manim -pqh amurdat_intro.py AmurdatIntro     # final
"""

import heapq

import numpy as np
from PIL import Image
from manim import *
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import distance_transform_edt

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_height = 8.0
config.frame_width = config.frame_height * config.pixel_width / config.pixel_height

# Palette — sampled from the logo.
PAPER = "#F9F3ED"
DUSK = "#1E1A33"
DUSK_OPACITY = 0.12           # night is a faint tint, not a flash
BARK = "#5D4686"
LEAF = "#8776A1"
LEAF_LIGHT = "#B3A7CC"
DIM_GOLD = "#8B7255"
BRIGHT_GOLD = "#D9B26B"
GOLD = "#B08D5A"
PALE_GOLD = "#E3CB9A"
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
BOOK_EDGE_PX = 96.0           # book's lower edge; it dips to ~110 at the spine
BOOK_DIP_PX = (178.0, 18.0, 120.0)  # spine column, dip depth, dip half-width
LINE_FEATHER_PX = 8.0         # soft tip on the lines as they draw

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

# The sky wheel: sun and stars on opposite sides of one circle around the
# tree. They rise and set at the stump's cut face.
SKY_CENTER = FACE + UP * 1.0
SKY_RADIUS = 2.35
HORIZON_Y = FACE[1]
HORIZON_FADE = 0.6

# Days elapsed at time t (seconds). Slow at first, then ever faster; the
# half-days land on the three cuts, so each cut happens at midnight.
DAYS = PchipInterpolator([0.0, 0.8, 1.9, 2.55, 3.05, 3.95, 4.77, 5.2],
                         [-0.12, -0.06, 0.5, 1.0, 1.5, 2.5, 3.5, 4.1])


def F(n):
    """n frames, in seconds."""
    return n / config.frame_rate


def rot(v, a):
    c, s = np.cos(a), np.sin(a)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1], 0])


def polar(a):
    return np.array([np.cos(a), np.sin(a), 0])


def smooth_step(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


# ========================================================================
# Shapes in the logo's vocabulary
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


def make_sun(r=0.2):
    """Gold disc, two growth-ring outlines like the stump's, and rays in the
    grass-tuft leaf shape, alternating long and short."""
    disc = Circle(radius=r, fill_color=GOLD, fill_opacity=1, stroke_width=0)
    rings = VGroup(*[Circle(radius=r * f, stroke_color=GOLD, stroke_width=1.6, stroke_opacity=o)
                     for f, o in ((1.45, 0.9), (1.8, 0.5))])
    rays = VGroup()
    for i in range(12):
        a = i * TAU / 12
        length = r * (1.05 if i % 2 == 0 else 0.7)
        rays.add(leaf(polar(a) * r * 2.05, a, length, length * 0.32,
                      GOLD if i % 2 == 0 else PALE_GOLD))
    return VGroup(rings, rays, disc)


def make_star(size, color):
    """Four-point sparkle: two crossed grass-tuft leaves, long and short."""
    return VGroup(
        leaf(np.array([-1, -1, 0]) * size * 0.2, PI / 4, size * 0.57, size * 0.14, color),
        leaf(np.array([1, -1, 0]) * size * 0.2, 3 * PI / 4, size * 0.57, size * 0.14, color),
        leaf(LEFT * size / 2, 0, size, size * 0.2, color),
        leaf(DOWN * size / 2, PI / 2, size, size * 0.2, color),
    )


# Stars, placed around the anti-sun point of the wheel:
# (offset angle, radius, size, color). size 0 is a small dot.
STARS = [(-0.62, 2.1, 0.34, PALE_GOLD), (-0.35, 2.2, 0.46, LEAF_LIGHT),
         (-0.05, 2.5, 0.30, PALE_GOLD), (0.2, 2.05, 0.52, LEAF_LIGHT),
         (0.42, 2.45, 0.28, PALE_GOLD), (0.6, 2.05, 0.40, LEAF_LIGHT),
         (-0.18, 1.85, 0.22, LEAF_LIGHT), (0.48, 1.7, 0.20, PALE_GOLD),
         (-0.45, 2.55, 0, PALE_GOLD), (0.05, 1.95, 0, LEAF_LIGHT), (-0.25, 2.45, 0, PALE_GOLD),
         (0.3, 2.6, 0, LEAF_LIGHT), (0.72, 2.35, 0, PALE_GOLD), (-0.75, 2.4, 0, LEAF_LIGHT),
         (0.12, 2.75, 0, LEAF_LIGHT)]


def remember_opacity(mob):
    for m in mob.family_members_with_points():
        m.base_fill = m.get_fill_opacity()
        m.base_stroke = m.get_stroke_opacity()
    return mob


def fade(mob, a):
    """Scale each part's own fill and stroke opacity, so stroke-only rings
    stay stroke-only (set_opacity would fill them in)."""
    for m in mob.family_members_with_points():
        m.set_fill(opacity=m.base_fill * a, family=False)
        m.set_stroke(opacity=m.base_stroke * a, family=False)


class Sky:
    def __init__(self):
        self.sun = remember_opacity(make_sun(0.2))
        self.stars = []
        for off, r, size, color in STARS:
            mob = make_star(size, color) if size else Dot(radius=0.028, color=color)
            self.stars.append((remember_opacity(mob), off, r))
        self.group = VGroup(self.sun, *[m for m, _, _ in self.stars])
        self.presence = ValueTracker(1)

    def update(self, t):
        """Place everything for time t; return how dark it is (0..1)."""
        sun_a = PI / 2 - TAU * float(DAYS(t))
        presence = self.presence.get_value()
        sun_h = np.sin(sun_a)
        # Stars only come out once the sun is down.
        starlight = smooth_step((0.15 - sun_h) / 0.45)
        for mob, a, r, light in [(self.sun, sun_a, SKY_RADIUS, 1.0)] + [
                (m, sun_a + PI + off, r, starlight) for m, off, r in self.stars]:
            p = SKY_CENTER + polar(a) * r
            mob.move_to(p)
            fade(mob, presence * light * np.clip((p[1] - HORIZON_Y) / HORIZON_FADE, 0, 1))
        return presence * smooth_step((0.3 - sun_h) / 1.3)


# ========================================================================
# Tree
# ========================================================================

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


# ========================================================================
# Emblem: the stump always, then the lines drawing up, then the book
# ========================================================================

def path_distance(mask, seeds, start):
    """Distance along `mask` pixels (8-connected) from the seed pixels,
    each seed starting at start[seed]. Unreached pixels stay inf."""
    h, w = mask.shape
    dist = np.full(mask.shape, np.inf)
    heap = []
    for v, u in zip(*np.nonzero(seeds)):
        dist[v, u] = start[v, u]
        heap.append((dist[v, u], v, u))
    heapq.heapify(heap)
    steps = [(dv, du, np.hypot(dv, du)) for dv in (-1, 0, 1) for du in (-1, 0, 1) if dv or du]
    while heap:
        d, v, u = heapq.heappop(heap)
        if d > dist[v, u]:
            continue
        for dv, du, c in steps:
            nv, nu = v + dv, u + du
            if 0 <= nv < h and 0 <= nu < w and mask[nv, nu] and d + c < dist[nv, nu]:
                dist[nv, nu] = d + c
                heapq.heappush(heap, (d + c, nv, nu))
    return dist


class EmblemReveal:
    """The emblem image, revealed in layers: the stump is always shown; the
    thin lines draw themselves outward from the stump's rim, following
    each line like a pen; the book fades in last."""

    def __init__(self):
        self.rgba = np.array(Image.open(EMBLEM_PATH).convert("RGBA"))
        alpha = self.rgba[..., 3].astype(float)
        h, w = alpha.shape
        vv, uu = np.mgrid[0:h, 0:w].astype(float)
        cx, cy = FACE_PX
        rel = np.clip(1 - ((uu - cx) / FACE_A_PX) ** 2, 0, 1)
        arc_top = np.where(np.abs(uu - cx) < FACE_A_PX, cy - FACE_B_PX * np.sqrt(rel), cy)
        above = arc_top - vv

        self.stump = above <= 3
        spine_u, dip, dip_w = BOOK_DIP_PX
        book_edge = BOOK_EDGE_PX + dip * np.clip(1 - np.abs(uu - spine_u) / dip_w, 0, 1) ** 1.5
        self.book = ~self.stump & (vv < book_edge)
        lines = ~self.stump & ~self.book & (alpha > 25)

        # Lines start at the stump's rim. Any line not connected to the rim
        # starts when the front reaches its height instead.
        dist = path_distance(lines, lines & (above <= 9), np.zeros_like(alpha))
        stray = lines & np.isinf(dist)
        if stray.any():
            dist = np.minimum(dist, path_distance(stray, stray, np.maximum(above, 0)))
        # Faint anti-aliased pixels take the distance of the nearest line pixel.
        known = np.isfinite(dist)
        _, (iv, iu) = distance_transform_edt(~known, return_indices=True)
        self.dist = np.where(known, dist, dist[iv, iu])
        self.line_length = float(self.dist[np.isfinite(self.dist) & ~self.stump & ~self.book].max())

        self.mob = ImageMobject(self.frame(0, 0))
        self.mob.height = EMBLEM_HEIGHT
        self.mob.move_to(EMBLEM_CENTER)

    def frame(self, drawn, book):
        """drawn: how far (in pixels along each line) the lines have drawn;
        book: the book's opacity."""
        k = np.clip((drawn - self.dist) / LINE_FEATHER_PX, 0, 1)
        k[self.book] = book
        k[self.stump] = 1
        out = self.rgba.copy()
        out[..., 3] = (self.rgba[..., 3] * k).astype(np.uint8)
        return out

    def show(self, drawn, book):
        self.mob.pixel_array = self.frame(drawn, book)


# ========================================================================
# Scene
# ========================================================================

class AmurdatIntro(Scene):
    def construct(self):
        dusk = Rectangle(width=config.frame_width + 0.5, height=config.frame_height + 0.5,
                         stroke_width=0, fill_color=DUSK, fill_opacity=0)
        dusk.set_z_index(10)

        # The sky follows the renderer's own video clock (it advances with
        # every written frame), behind everything else. Summing updater dt's
        # would drift: each animation's first frame gets dt=0. The dt
        # parameter is still needed: it marks the updater as time-based, or
        # manim freezes the frame during waits.
        sky = Sky()

        def tick(_, dt=0):
            dusk.set_fill(opacity=DUSK_OPACITY * sky.update(self.renderer.time))

        tick(None)
        sky.group.add_updater(tick)
        self.add(sky.group, dusk)

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

        def cut(cap, trunk, crown, n, *also):
            above = Group(trunk, crown)
            pivot = FACE + RIGHT * FACE_A
            self.remove(cap)
            self.play(above.animate(run_time=F(n), rate_func=rush_into)
                      .rotate(-0.5, about_point=pivot)
                      .shift((RIGHT * 0.35 + DOWN * 0.25) * K).set_opacity(0), *also)
            self.remove(trunk, crown)

        # ---- 0.0-0.8  A full tree stands on the stump, the sun is up -----
        cap, trunk, crown = make_tree(FULL_TREE, seed=3)
        self.add(emblem.mob, cap, trunk, crown)
        self.wait(F(24))

        # ---- 0.8-2.8  Time passes: the sky wheel turns, ever faster ------
        self.wait(F(60))

        # ---- 2.8-4.6  Cut at midnight, regrow — twice ---------------------
        # First a thin sprout from the cut face, then a broad, full tree.
        for size, seed, sprout in ((SPROUT, 5, True), (BROAD_TREE, 6, False)):
            self.wait(F(5))
            cut(cap, trunk, crown, 5)
            self.wait(F(5))
            cap, trunk, crown = make_tree(size, seed, sprout)
            grow(cap, trunk, crown, 12)

        # ---- 4.6-5.1  Final cut; the sky fades, only the stump remains ---
        cut(cap, trunk, crown, 10, sky.presence.animate(run_time=F(15)).set_value(0))
        sky.group.clear_updaters()
        self.remove(sky.group, dusk)

        # ---- 5.1-6.9  The lines draw up out of the stump; the book fades --
        drawn, book = ValueTracker(0), ValueTracker(0)
        emblem.mob.add_updater(lambda m: emblem.show(drawn.get_value(), book.get_value()))
        self.play(drawn.animate.set_value(emblem.line_length + LINE_FEATHER_PX),
                  run_time=F(42), rate_func=linear)
        self.play(book.animate.set_value(1), run_time=F(12), rate_func=smooth)
        emblem.mob.clear_updaters()

        # ---- 6.9-7.5  The script writes in -------------------------------
        script = make_script(px(*SCRIPT_PX), SCRIPT_W_PX * S, DIM_GOLD)
        self.play(Write(script), run_time=F(18))

        # ---- 7.5-8.0  Script brightens and settles; tagline, then AMURDAT -
        tagline = Text("“Knowledge is the only Immortal”",
                       font="Noto Serif", slant=ITALIC, color=INK)
        tagline.width = TAGLINE_WIDTH
        tagline.next_to(emblem.mob, DOWN, buff=0.28)
        wordmark = ImageMobject(WORDMARK_PATH)
        wordmark.width = WORDMARK_WIDTH
        wordmark.next_to(tagline, DOWN, buff=0.2)
        self.play(
            Succession(script.animate(run_time=F(6)).set_stroke(color=BRIGHT_GOLD),
                       script.animate(run_time=F(9)).set_stroke(color=GOLD)),
            FadeIn(tagline, shift=UP * 0.05, run_time=F(12)),
            Succession(Wait(run_time=F(5)), FadeIn(wordmark, shift=UP * 0.05, run_time=F(10))),
        )

        # ---- 8.0-10.0  Hold the finished logo ---------------------------
        self.wait(F(60))
