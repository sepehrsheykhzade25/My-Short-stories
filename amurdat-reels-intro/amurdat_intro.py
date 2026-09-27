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

# ----------------------------------------------------------------------
# The book/infinity-band/stump emblem and the AMURDAT/Farsi wordmark are
# cropped straight out of the reference logo (background made transparent)
# rather than hand-built from vector primitives — repeated attempts to
# redraw those shapes by hand kept missing the logo's actual proportions
# and line quality. Only the script (real Old Persian text, animated
# separately) and the tree/cut/regrow build-up remain hand-drawn.
# ----------------------------------------------------------------------
EMBLEM_PATH = "assets/emblem.png"
WORDMARK_PATH = "assets/wordmark.png"
EMBLEM_HEIGHT = 5.0
EMBLEM_CENTER = np.array([0, 0.1, 0])
SCRIPT_CENTER = np.array([0, 0.22, 0])
STUMP_TOP_Y = -0.64


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


def curved_branch(start, end, bow=ORIGIN, color=VIOLET, sw=THIN):
    """A gently bowed branch line (smooth curve, not a straight stick),
    so it reads with the same flowing hand-drawn quality as the book
    pages, infinity band and stump rings."""
    mid = (start + end) / 2 + bow
    b = VMobject(color=color, stroke_width=sw)
    b.set_points_smoothly([start, mid, end])
    return b


def make_tree(trunk_h=3.0, canopy_r=1.15, seed=1, base_point=ORIGIN):
    """A single gently bowed trunk with two short flourish branches near
    the top, and one clean canopy outline — kept to a few deliberate
    strokes with open negative space between them, matching the
    logo's minimal, confident linework (single clean curves for the
    book pages, infinity lobes, stump rings) rather than a dense tangle
    of overlapping shapes."""
    rng = np.random.default_rng(seed)
    top = base_point + UP * trunk_h
    bow = rng.uniform(-0.06, 0.06) * trunk_h

    trunk = VGroup()
    main = VMobject(color=VIOLET, stroke_width=2.6)
    main.set_points_smoothly([
        base_point, base_point + UP * trunk_h * 0.5 + RIGHT * bow, top,
    ])
    trunk.add(main)

    for direction in (LEFT, RIGHT):
        start = base_point + UP * trunk_h * 0.86 + RIGHT * bow * 0.86
        end = start + UP * 0.3 + direction * 0.4
        trunk.add(curved_branch(start, end, bow=direction * 0.08 + UP * 0.08, sw=THIN))

    canopy = organic_loop(radius=canopy_r, bumps=9, wobble=0.1, seed=seed,
                           color=VIOLET, sw=THIN)
    canopy.move_to(top + UP * canopy_r * 0.8)

    group = VGroup(trunk, canopy)
    group.trunk = trunk
    group.canopy = canopy
    return group


def grass_tuft(base, direction, color=LAVENDER, seed=0):
    """A small cluster of pointed blades, fanning from a base point."""
    rng = np.random.default_rng(seed)
    tuft = VGroup()
    for i in range(4):
        ang = -0.55 + i * 0.37 + rng.uniform(-0.06, 0.06)
        length = rng.uniform(0.14, 0.22)
        tip = base + direction * length * np.cos(ang) + UP * length * (0.7 + abs(np.sin(ang)))
        mid = (base + tip) / 2 + UP * 0.03
        blade = VMobject(color=color, stroke_width=1.3)
        blade.set_points_smoothly([base, mid, tip])
        tuft.add(blade)
    return tuft


def make_stump(center=ORIGIN, width=1.6):
    """A single dark root-mass silhouette (not separate stick roots): a
    filled shape with a wavy, tapering bottom edge, carved by thin
    cream-colored gap lines to suggest individual root strands, with
    concentric ripple rings on the cut top surface."""
    top_y = center[1]
    half_top = width / 2
    half_bottom = half_top * 1.3
    n = 9
    base_bottom_y = top_y - 1.05

    rng = np.random.default_rng(11)
    tip_xs = np.linspace(-half_bottom, half_bottom, n)
    tip_ys = [base_bottom_y + rng.uniform(-0.08, 0.08) for _ in tip_xs]

    boundary = [np.array([center[0] - half_top, top_y, 0])]
    for x, y in zip(tip_xs, tip_ys):
        boundary.append(np.array([center[0] + x, y, 0]))
    boundary.append(np.array([center[0] + half_top, top_y, 0]))

    body = VMobject(color=VIOLET, fill_color=VIOLET, fill_opacity=1.0, stroke_width=1.3)
    body.set_points_smoothly(boundary + [boundary[0]])

    gaps = VGroup()
    for i in range(1, n - 1):
        x, y = tip_xs[i], tip_ys[i]
        top_pt = np.array([center[0] + x * 0.88, top_y - 0.04, 0])
        bot_pt = np.array([center[0] + x, y - 0.03, 0])
        gap = Line(top_pt, bot_pt, color=CREAM, stroke_width=1.5)
        gaps.add(gap)

    rings = VGroup(*[
        Ellipse(width=width * 0.92 * (0.32 + 0.17 * i), height=0.10 * (0.32 + 0.17 * i),
                color=LAVENDER, stroke_width=1.3)
        .move_to(np.array([center[0], top_y + 0.015, 0]))
        for i in range(5)
    ])

    leaf_l = grass_tuft(np.array([center[0] - half_bottom - 0.02, base_bottom_y + 0.35, 0]),
                         LEFT, seed=7)
    leaf_r = grass_tuft(np.array([center[0] + half_bottom + 0.02, base_bottom_y + 0.35, 0]),
                         RIGHT, seed=8)

    stump = VGroup(body, gaps, rings, leaf_l, leaf_r)
    stump.body = body
    stump.rings = rings
    stump.gaps = gaps
    return stump


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

        # Layout anchors. stump_center matches where the real emblem
        # image's stump sits (STUMP_TOP_Y), so the hand-built stump used
        # for the cut/regrow build-up lines up with it for the crossfade.
        stump_center = np.array([0, STUMP_TOP_Y, 0])
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
            # fill/stroke opacity instead of flattening it to 1. Remove
            # the just-cut trunk first: stretch_to_fit_height squashes it
            # but leaves its stroke visible as a thin bar if not removed.
            self.remove(tree)
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
        self.remove(tree)
        self.wait(0.18)

        # ----------------------------------------------------------
        # Beat 5  (0:04.5 - 0:05.5)  Book forms from the stump: the
        # hand-built stump dissolves into the real book+infinity+stump
        # emblem (cropped from the logo, script band left transparent so
        # the animated script in beat 6 can write into that exact gap).
        # ----------------------------------------------------------
        emblem = ImageMobject(EMBLEM_PATH)
        emblem.height = EMBLEM_HEIGHT
        emblem.move_to(EMBLEM_CENTER)

        self.play(
            FadeOut(stump, run_time=0.6),
            FadeIn(emblem, scale=1.05, run_time=0.7),
        )
        self.wait(0.3)

        # ----------------------------------------------------------
        # Beat 6  (0:05.5 - 0:06.5)  Ancient script writes in
        # ----------------------------------------------------------
        script = make_script(SCRIPT_CENTER, target_width=3.6, color=DIM_GOLD)

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
        translation.next_to(emblem, DOWN, buff=0.3)
        self.play(FadeIn(translation, shift=UP * 0.08), run_time=0.8)

        # ----------------------------------------------------------
        # Beat 9  (0:07.6 - 0:08.0)  Wordmark locks, translation fades
        # ----------------------------------------------------------
        wordmark = ImageMobject(WORDMARK_PATH)
        wordmark.width = 3.7
        wordmark.to_edge(DOWN, buff=0.4)

        self.play(
            FadeIn(wordmark),
            FadeOut(translation),
            run_time=0.4,
        )
        self.wait(0.3)
