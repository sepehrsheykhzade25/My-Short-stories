"""
Amurdat Reels Intro — 8s vertical (1080x1920) animation.

Story: a tree stands, time accelerates through day/night, the tree is cut
and regrown twice (each cut landing on a night beat), the final cut leaves
a stump, a book grows from the stump on curved lines that cross into an
infinity band, ancient script writes itself in along the band, its English
translation appears, and the AMURDAT wordmark locks the final frame — which
should read as the logo.

Run:
    manim -pql amurdat_intro.py AmurdatIntro   # draft
    manim -pqh amurdat_intro.py AmurdatIntro   # final
"""

import numpy as np
from manim import *

# ----------------------------------------------------------------------
# Canvas: 1080x1920 (9:16). Keep frame_height fixed, derive frame_width.
# ----------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_height = 8.0
config.frame_width = config.frame_height * config.pixel_width / config.pixel_height
config.background_color = "#F3EDE4"

# ----------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------
CREAM = "#F3EDE4"
VIOLET = "#4A3B7A"
GOLD = "#B08D5A"
LAVENDER = "#C9C3D9"
NIGHT = "#2A2438"
DIM_GOLD = "#8B7255"
BRIGHT_GOLD = "#D9B26B"

THIN = 2.2
MED = 3.0


# ========================================================================
# Reusable hand-drawn-style builders
# ========================================================================

def organic_loop(radius=1.0, bumps=10, wobble=0.14, seed=0, color=VIOLET, sw=THIN):
    """A closed, slightly irregular outline — used for tree foliage."""
    rng = np.random.default_rng(seed)
    angles = np.linspace(0, TAU, bumps, endpoint=False)
    pts = []
    for a in angles:
        r = radius * (1 + rng.uniform(-wobble, wobble))
        pts.append(r * np.array([np.cos(a), np.sin(a), 0]))
    pts.append(pts[0])
    shape = VMobject(color=color, stroke_width=sw)
    shape.set_points_smoothly(pts)
    return shape


def make_tree(trunk_h=3.0, canopy_r=1.15, seed=1, base_point=ORIGIN):
    """Trunk (with two small branch forks) + organic canopy outline."""
    trunk = VGroup()
    top = base_point + UP * trunk_h
    main = Line(base_point, top, color=VIOLET, stroke_width=MED)
    fork_l = Line(top, top + UP * 0.35 + LEFT * 0.32, color=VIOLET, stroke_width=THIN)
    fork_r = Line(top, top + UP * 0.35 + RIGHT * 0.32, color=VIOLET, stroke_width=THIN)
    mid = base_point + UP * trunk_h * 0.6
    branch_l = Line(mid, mid + UP * 0.4 + LEFT * 0.5, color=VIOLET, stroke_width=THIN)
    branch_r = Line(mid, mid + UP * 0.4 + RIGHT * 0.5, color=VIOLET, stroke_width=THIN)
    trunk.add(main, fork_l, fork_r, branch_l, branch_r)

    canopy = organic_loop(radius=canopy_r, bumps=11, wobble=0.16, seed=seed,
                           color=VIOLET, sw=THIN)
    canopy.move_to(top + UP * canopy_r * 0.75)

    group = VGroup(trunk, canopy)
    group.trunk = trunk
    group.canopy = canopy
    return group


def make_stump(center=ORIGIN, width=1.5):
    """Dark filled stump with ring ripples on top and roots fanning below."""
    top_y = center[1]
    bottom_y = top_y - 0.85
    half_top = width / 2
    half_bot = width / 2 * 1.35

    body = Polygon(
        np.array([center[0] - half_top, top_y, 0]),
        np.array([center[0] + half_top, top_y, 0]),
        np.array([center[0] + half_bot, bottom_y, 0]),
        np.array([center[0] - half_bot, bottom_y, 0]),
        color=VIOLET, fill_color=VIOLET, fill_opacity=1.0, stroke_width=1.5,
    )

    rings = VGroup(*[
        Ellipse(width=width * 0.9 * (0.45 + 0.28 * i), height=0.14 * (0.45 + 0.28 * i),
                color=LAVENDER, stroke_width=1.6)
        .move_to(np.array([center[0], top_y + 0.02, 0]))
        for i in range(3)
    ])

    roots = VGroup()
    n_roots = 9
    for i in range(n_roots):
        t = i / (n_roots - 1)
        x_start = center[0] - half_bot + t * (2 * half_bot)
        start = np.array([x_start, bottom_y, 0])
        spread = (t - 0.5) * 1.3
        end = start + DOWN * 0.55 + RIGHT * spread * 0.35
        root = Line(start, end, color=VIOLET, stroke_width=1.4)
        roots.add(root)

    leaf_l = organic_loop(radius=0.16, bumps=6, wobble=0.2, seed=7, color=LAVENDER, sw=1.4)
    leaf_l.move_to(np.array([center[0] - half_bot - 0.05, bottom_y + 0.12, 0]))
    leaf_r = organic_loop(radius=0.16, bumps=6, wobble=0.2, seed=8, color=LAVENDER, sw=1.4)
    leaf_r.move_to(np.array([center[0] + half_bot + 0.05, bottom_y + 0.12, 0]))

    stump = VGroup(roots, body, rings, leaf_l, leaf_r)
    stump.body = body
    stump.rings = rings
    stump.roots = roots
    return stump


def make_book(center=ORIGIN, width=2.6, height=1.05):
    """Open book: two curved pages meeting at a center spine point."""
    hw = width / 2
    spine = center + DOWN * height * 0.35
    top_dip = center + UP * height * 0.62

    def page(direction):
        """Closed gull-wing petal: spine -> outer bulge -> outer peak ->
        inward down to the shared top dip, giving a real page silhouette
        instead of a bare V line."""
        outer_bulge = center + direction * hw * 0.98 + UP * height * 0.05
        outer_peak = center + direction * hw * 0.62 + UP * height * 0.55
        pts = [
            spine,
            outer_bulge,
            outer_peak,
            top_dip,
        ]
        curve = VMobject(color=VIOLET, stroke_width=MED)
        curve.set_points_smoothly(pts)
        return curve

    left_page = page(LEFT)
    right_page = page(RIGHT)

    # a few short "page edge" ticks fanning along the top of each page
    ticks = VGroup()
    for direction in (LEFT, RIGHT):
        for i in range(3):
            f = 0.3 + i * 0.28
            base = center + UP * height * (0.3 + f * 0.28) + direction * hw * f * 0.85
            tick = Line(base, base + UP * 0.13, color=VIOLET, stroke_width=1.4)
            ticks.add(tick)

    spine_line = Line(top_dip, spine, color=VIOLET, stroke_width=1.6)

    book = VGroup(left_page, right_page, spine_line, ticks)
    book.left_page = left_page
    book.right_page = right_page
    book.spine_line = spine_line
    book.spine_point = spine
    book.ticks = ticks
    return book


def make_infinity_band(stump_top, book_spine, width=1.7, height=0.95):
    """A figure-eight of crossing curves linking stump to book — the
    logo's signature infinity loop, built from two crossing bezier arcs
    plus a few thin fan lines."""
    cx = (stump_top[0] + book_spine[0]) / 2
    cy = (stump_top[1] + book_spine[1]) / 2
    left_c = np.array([cx - width / 2, cy, 0])
    right_c = np.array([cx + width / 2, cy, 0])

    def lobe(c, sign):
        loop = VMobject(color=VIOLET, stroke_width=1.8)
        pts = [
            c + sign * LEFT * width * 0.32 + UP * height * 0.42,
            c + sign * LEFT * width * 0.55,
            c + sign * LEFT * width * 0.32 + DOWN * height * 0.42,
            c,
            c + sign * RIGHT * width * 0.32 + UP * height * 0.42,
        ]
        loop.set_points_smoothly(pts)
        return loop

    lobe_l = lobe(left_c, -1)
    lobe_r = lobe(right_c, 1)

    fan = VGroup()
    for t in np.linspace(-1, 1, 5):
        start = stump_top + RIGHT * t * width * 0.45
        end = book_spine + RIGHT * t * width * 0.25
        mid = np.array([cx + t * width * 0.1, cy, 0])
        curve = VMobject(color=LAVENDER, stroke_width=1.1)
        curve.set_points_smoothly([start, mid, end])
        fan.add(curve)

    band = VGroup(fan, lobe_l, lobe_r)
    band.fan = fan
    band.lobe_l = lobe_l
    band.lobe_r = lobe_r
    return band


SCRIPT_TEXT = "\U000103BA\U000103C1\U000103D1\U000103A2 \U000103A0\U000103B6\U000103BC\U000103AB\U000103A0 \U000103AD\U000103A0\U000103B4\U000103A0"
# Old Persian cuneiform (U+103A0-U+103D5), supplied by the brand as the
# correct reading of the logo's script band.


def make_script(center, target_width=2.6, color=GOLD, stroke_w=1.6):
    """The real Old Persian text, rendered stroke-only (no fill) so it
    reads as thin linework, matching every other element in the mark."""
    script = Text(SCRIPT_TEXT, font="Noto Sans Old Persian")
    script.set_fill(opacity=0)
    script.set_stroke(color=color, width=stroke_w, opacity=1)
    script.width = target_width
    script.move_to(center)
    return script


# ========================================================================
# Scene
# ========================================================================

class AmurdatIntro(Scene):
    def construct(self):
        fw, fh = config.frame_width, config.frame_height

        bg = Rectangle(width=fw + 0.5, height=fh + 0.5, stroke_width=0,
                        fill_color=CREAM, fill_opacity=1.0)
        bg.set_z_index(-10)
        self.add(bg)

        # Layout anchors (portrait canvas: logo cluster sits in the upper
        # two-thirds, wordmark row near the bottom, with clear air between
        # the stump's roots and the wordmark).
        stump_center = np.array([0, -1.4, 0])
        book_center = np.array([0, 1.75, 0])
        ground_y = stump_center[1] - 0.05

        # ----------------------------------------------------------
        # Beat 1  (0:00.0 - 0:00.5)  Establish: full grown tree
        # ----------------------------------------------------------
        ground = Line(LEFT * 1.4, RIGHT * 1.4, color=LAVENDER, stroke_width=1.4)
        ground.move_to([0, ground_y, 0])

        tree = make_tree(trunk_h=2.6, canopy_r=1.05, seed=3,
                          base_point=np.array([0, ground_y, 0]))

        self.add(ground)
        self.play(FadeIn(tree, shift=UP * 0.1), run_time=0.4)
        self.wait(0.1)

        # ----------------------------------------------------------
        # Beat 2  (0:00.5 - 0:02.0)  Accelerating day/night pulses
        # ----------------------------------------------------------
        def sway(mob, angle):
            mob.canopy.rotate(angle, about_point=mob.trunk.get_top())

        cycle_times = [0.46, 0.40, 0.32, 0.24]
        for i, ct in enumerate(cycle_times):
            half = ct / 2
            sign = 1 if i % 2 == 0 else -1
            self.play(
                bg.animate.set_fill(NIGHT),
                Rotate(tree.canopy, angle=sign * 0.05, about_point=tree.trunk.get_top()),
                run_time=half, rate_func=smooth,
            )
            self.play(
                bg.animate.set_fill(CREAM),
                Rotate(tree.canopy, angle=-sign * 0.05, about_point=tree.trunk.get_top()),
                run_time=half, rate_func=smooth,
            )

        # ----------------------------------------------------------
        # Beat 3  (0:02.0 - 0:04.0)  Cut / regrow, x2, cuts land on dark
        # ----------------------------------------------------------
        # Built once, correctly styled (filled body, stroke-only rings and
        # roots); revealed with a plain self.add at the cut instant rather
        # than an opacity animation, since set_opacity() on a VGroup would
        # flatten fill and stroke together and wreck the stroke-only parts.
        stump = make_stump(center=stump_center, width=1.35)

        heights = [1.35, 1.9]     # regrow targets after each cut (partial)
        canopy_rs = [0.55, 0.85]

        for cut_i in range(2):
            # dark beat rises
            self.play(bg.animate.set_fill(NIGHT), run_time=0.18)

            # the cut: trunk snaps down to stump height, canopy vanishes
            self.play(
                tree.trunk.animate.stretch_to_fit_height(0.001).move_to(stump_center),
                tree.canopy.animate.scale(0.05).move_to(stump_center).set_opacity(0),
                run_time=0.16, rate_func=rush_into,
            )
            if cut_i == 0:
                self.add(stump)

            # dark beat falls back to cream, stump remains
            self.play(bg.animate.set_fill(CREAM), run_time=0.16)

            # regrow (partial) — FadeIn preserves each part's own
            # fill/stroke opacity instead of flattening it to 1.
            new_tree = make_tree(trunk_h=heights[cut_i], canopy_r=canopy_rs[cut_i],
                                  seed=5 + cut_i, base_point=stump_center)
            self.play(FadeIn(new_tree), run_time=0.5, rate_func=smooth)
            tree = new_tree

        # ----------------------------------------------------------
        # Beat 4  (0:04.0 - 0:04.5)  Final cut — stump only, settle
        # ----------------------------------------------------------
        self.play(
            tree.animate.scale(0.4, about_point=stump_center).set_opacity(0),
            FadeOut(ground, run_time=0.32),
            bg.animate.set_fill(CREAM),
            run_time=0.32, rate_func=rush_into,
        )
        self.wait(0.18)

        # ----------------------------------------------------------
        # Beat 5  (0:04.5 - 0:05.5)  Book forms from the stump
        # ----------------------------------------------------------
        stump_top = stump_center + UP * 0.0
        book = make_book(center=book_center, width=2.8, height=1.15)
        band = make_infinity_band(stump_top + UP * 0.15, book.spine_point,
                                   width=1.7, height=1.5)
        band.move_to(((stump_top + UP * 0.15) + book.spine_point) / 2)

        self.play(
            Create(band.fan), run_time=0.35,
        )
        self.play(
            Create(band.lobe_l), Create(band.lobe_r),
            run_time=0.35,
        )
        self.play(
            Create(book.left_page), Create(book.right_page),
            Create(book.spine_line), Create(book.ticks),
            run_time=0.3,
        )

        # ----------------------------------------------------------
        # Beat 6  (0:05.5 - 0:06.5)  Ancient script writes in
        # ----------------------------------------------------------
        script_center = band.get_center() + UP * 0.02
        script = make_script(script_center, target_width=2.5, color=DIM_GOLD)

        self.play(Write(script), run_time=0.7)
        self.play(script.animate.set_stroke(color=BRIGHT_GOLD), run_time=0.3)

        # ----------------------------------------------------------
        # Beat 7  (0:06.5 - 0:06.8)  Script settles to resting gold
        # ----------------------------------------------------------
        self.play(script.animate.set_stroke(color=GOLD), run_time=0.3)

        # ----------------------------------------------------------
        # Beat 8  (0:06.8 - 0:07.6)  Translation fades in
        # ----------------------------------------------------------
        translation = Text(
            "“Knowledge is the only Immortal”",
            font="Noto Serif", slant=ITALIC, color=VIOLET,
        ).scale(0.34)
        translation.next_to(script, DOWN, buff=0.45)
        self.play(FadeIn(translation, shift=UP * 0.08), run_time=0.8)

        # ----------------------------------------------------------
        # Beat 9  (0:07.6 - 0:08.0)  Wordmark locks, translation fades
        # ----------------------------------------------------------
        wordmark = Text("AMURDAT", font="Sans", weight=BOLD, color=VIOLET)
        wordmark.scale(0.38)
        wordmark.to_corner(DL, buff=0.35)

        farsi = Text("آموردات", font="Noto Naskh Arabic", weight=BOLD, color=VIOLET)
        farsi.scale(0.38)
        farsi.to_corner(DR, buff=0.35)

        self.play(
            FadeIn(wordmark), FadeIn(farsi),
            FadeOut(translation),
            run_time=0.4,
        )
        self.wait(0.3)
