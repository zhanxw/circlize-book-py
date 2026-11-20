"""Generate all figures for Chapter 7 (Advanced layout)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import _common
from circlize import (
    CELL_META,
    circos,
    get_cell_meta_data,
    mm_y,
    rand_color,
)


def build_ch07_circlize_zoom() -> None:
    """Figure 7.1: Horizontal zooming of sectors a and partial sector b."""
    rng = np.random.default_rng(123)
    df = pd.DataFrame(
        {
            "sectors": rng.choice(list("abcdef"), size=400, replace=True),
            "x": rng.normal(size=400),
            "y": rng.normal(size=400),
        }
    )

    zoom_df_a = df[df["sectors"] == "a"].copy()
    zoom_df_b = df[df["sectors"] == "b"].sort_values("x").iloc[:10].copy()
    zoom_df = pd.concat([zoom_df_a, zoom_df_b], ignore_index=True)
    zoom_df["sectors"] = "zoom_" + zoom_df["sectors"]
    df2 = pd.concat([df, zoom_df], ignore_index=True)

    normal_sectors = list("abcdef")
    zoomed_sectors = ["zoom_a", "zoom_b"]
    sector_order = normal_sectors + zoomed_sectors

    xrange = df2.groupby("sectors")["x"].agg(lambda s: float(s.max() - s.min()))
    norm_sum = float(xrange.loc[normal_sectors].sum())
    zoom_sum = float(xrange.loc[zoomed_sectors].sum())
    sector_width = [float(xrange[s]) / norm_sum for s in normal_sectors] + [
        float(xrange[s]) / zoom_sum for s in zoomed_sectors
    ]

    sectors_cat = pd.Categorical(df2["sectors"], categories=sector_order, ordered=True)

    fig = _common.new_figure(6.4, 6.4)
    circos.par(start_degree=90, points_overflow_warning=False)
    circos.initialize(sectors_cat, x=df2["x"], sector_width=sector_width)

    def panel_zoom(x, y):
        circos.points(x, y, col="red", pch=16, cex=0.5)
        circos.text(
            CELL_META.xcenter,
            CELL_META.cell_ylim[1] + mm_y(2.0),
            CELL_META.sector_index,
            nice_facing=True,
        )

    circos.track(sectors_cat, x=df2["x"], y=df2["y"], panel_fun=panel_zoom)

    circos.link(
        "a",
        get_cell_meta_data("cell.xlim", sector_index="a"),
        "zoom_a",
        get_cell_meta_data("cell.xlim", sector_index="zoom_a"),
        border=None,
        col="#00000020",
    )
    circos.link(
        "b",
        [float(zoom_df_b["x"].iloc[0]), float(zoom_df_b["x"].iloc[9])],
        "zoom_b",
        get_cell_meta_data("cell.xlim", sector_index="zoom_b"),
        rou1=get_cell_meta_data("cell.top.radius", sector_index="b"),
        border=None,
        col="#00000020",
    )
    circos.clear()
    _common.save_fig(fig, "ch07_circlize_zoom.png")


def build_ch07_circlize_part() -> None:
    """Figure 7.2: Visualizing one quarter of the circle using canvas_xlim/canvas_ylim."""
    rng = np.random.default_rng(77)
    df = pd.DataFrame(
        {
            "sectors": ["a"] * 100,
            "x": rng.uniform(size=100),
            "y": rng.uniform(size=100),
        }
    )
    yr = (float(df["y"].min()), float(df["y"].max()))

    fig = _common.new_figure(9.6, 4.8)
    ax1, ax2 = fig.subplots(1, 2)

    # Left: full circle with [0, 1] x [0, 1] quadrant box drawn on top
    plt.sca(ax1)
    circos.par(start_degree=90, gap_degree=0)
    circos.initialize(list("abcd"), xlim=(0.0, 1.0))
    circos.track(ylim=yr)
    circos.update(sector_index="a", bg_border="black")
    circos.points(df["x"], df["y"], pch=16, cex=0.5)
    circos.track(ylim=yr)
    circos.update(sector_index="a", bg_border="black")
    circos.lines(np.arange(1, 101) / 100.0, df["y"])
    circos.clear()
    ax1.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0, fill=False, edgecolor="black", linewidth=1.0))
    ax1.text(0.0, -0.04, "0", ha="center", va="top", fontsize=9)
    ax1.text(1.0, -0.04, "1", ha="center", va="top", fontsize=9)
    ax1.text(-0.04, 1.0, "1", ha="right", va="center", fontsize=9)

    # Right: restrict canvas to [0, 1] x [0, 1] and use gap_after=270
    plt.sca(ax2)
    circos.par(canvas_xlim=(0.0, 1.0), canvas_ylim=(0.0, 1.0), start_degree=90, gap_after=270)
    circos.initialize(["a"], xlim=(0.0, 1.0))
    circos.track(
        df["sectors"],
        x=df["x"],
        y=df["y"],
        panel_fun=lambda x, y: circos.points(x, y, pch=16, cex=0.5),
    )
    circos.track(
        df["sectors"],
        x=df["x"],
        y=df["y"],
        panel_fun=lambda x, y: circos.lines(np.arange(1, 101) / 100.0, y),
    )
    circos.clear()
    ax2.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0, fill=False, edgecolor="black", linewidth=1.0, clip_on=False))
    ax2.text(0.0, -0.03, "0", ha="center", va="top", fontsize=9, clip_on=False)
    ax2.text(1.0, -0.03, "1", ha="center", va="top", fontsize=9, clip_on=False)
    ax2.text(-0.03, 1.0, "1", ha="right", va="center", fontsize=9, clip_on=False)

    fig.subplots_adjust(left=0.03, right=0.97, top=0.95, bottom=0.06, wspace=0.14)
    _common.save_fig(fig, "ch07_circlize_part.png")


def build_ch07_circlize_part2() -> None:
    """Figure 7.3: Showing a subset of cells in selected tracks."""
    rng = np.random.default_rng(101)
    sectors = list("abcd")
    df = pd.DataFrame(
        {
            "sectors": ["a"] * 100,
            "x": rng.uniform(size=100),
            "y": rng.uniform(size=100),
        }
    )

    fig = _common.new_figure(6.0, 6.0)
    circos.initialize(sectors, xlim=(0.0, 1.0))

    # Track 1: subset of data directly passed to circos.track
    circos.track(
        df["sectors"],
        x=df["x"],
        y=df["y"],
        panel_fun=lambda x, y: circos.points(x, y, pch=16, cex=0.5),
    )

    # Track 2: empty track first, then selectively draw cell 'a'
    circos.track(ylim=(float(df["y"].min()), float(df["y"].max())), bg_border=None)
    circos.update(sector_index="a", bg_border="black")
    circos.points(df["x"], df["y"], pch=16, cex=0.5)

    circos.track(sectors=sectors, ylim=(0.0, 1.0))
    circos.track(sectors=sectors, ylim=(0.0, 1.0))
    circos.clear()
    _common.save_fig(fig, "ch07_circlize_part2.png")


def build_ch07_circlize_nested() -> None:
    """Figure 7.4: Concentric nested circular plots via overlay_axes."""
    fig = _common.new_figure(11.4, 3.9)
    ax1, ax2, ax3 = fig.subplots(1, 3)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.94, bottom=0.10, wspace=0.25)

    # Panel 1: outer circle on [-1, 1]
    plt.sca(ax1)
    circos.initialize(list("abcd"), xlim=(0.0, 1.0))
    circos.track(
        ylim=(0.0, 1.0),
        panel_fun=lambda x, y: circos.text(0.5, 0.5, "outer circos", nice_facing=True, cex=0.75),
    )
    circos.clear()
    ax1.set_axis_on()
    ax1.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax1.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax1.tick_params(labelsize=8)

    # Panel 2: inner circle on [-2, 2]
    plt.sca(ax2)
    circos.par(canvas_xlim=(-2.0, 2.0), canvas_ylim=(-2.0, 2.0))
    circos.initialize(list("abc"), xlim=(0.0, 1.0))
    circos.track(
        ylim=(0.0, 1.0),
        panel_fun=lambda x, y: circos.text(0.5, 0.5, "inner circos", nice_facing=True, cex=0.5),
    )
    circos.clear()
    ax2.set_axis_on()
    ax2.set_xticks([-2.0, -1.0, 0.0, 1.0, 2.0])
    ax2.set_yticks([-2.0, -1.0, 0.0, 1.0, 2.0])
    ax2.tick_params(labelsize=8)

    # Panel 3: combined concentric overlay
    plt.sca(ax3)
    circos.initialize(list("abcd"), xlim=(0.0, 1.0))
    circos.track(
        ylim=(0.0, 1.0),
        panel_fun=lambda x, y: circos.text(0.5, 0.5, "outer circos", nice_facing=True, cex=0.75),
    )
    circos.clear()

    _common.overlay_axes(fig, ax3)
    circos.par(canvas_xlim=(-2.0, 2.0), canvas_ylim=(-2.0, 2.0))
    circos.initialize(list("abc"), xlim=(0.0, 1.0))
    circos.track(
        ylim=(0.0, 1.0),
        panel_fun=lambda x, y: circos.text(0.5, 0.5, "inner circos", nice_facing=True, cex=0.5),
    )
    circos.clear()

    _common.save_fig(fig, "ch07_circlize_nested.png")


def build_ch07_circlize_separated() -> None:
    """Figure 7.5: Two separated circular plots combined via shifted canvas limits."""
    sectors = list("abcd")
    fig = _common.new_figure(11.4, 3.9)
    ax1, ax2, ax3 = fig.subplots(1, 3)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.94, bottom=0.10, wspace=0.25)

    # Panel 1: first half-circle shifted toward bottom-left
    plt.sca(ax1)
    circos.par(canvas_xlim=(-1.0, 1.5), canvas_ylim=(-1.0, 1.5), start_degree=-45, points_overflow_warning=False)
    circos.initialize(sectors, xlim=(0.0, 1.0))
    circos.track(ylim=(0.0, 1.0), bg_col=None, bg_border=None)
    circos.update(sector_index="a")
    circos.text(0.5, 0.5, "first one", nice_facing=True, cex=0.7)
    circos.update(sector_index="b")
    circos.text(0.5, 0.5, "first one", nice_facing=True, cex=0.7)
    circos.clear()
    ax1.set_axis_on()
    ax1.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0, 1.5])
    ax1.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0, 1.5])
    ax1.tick_params(labelsize=8)

    # Panel 2: second half-circle shifted toward top-right
    plt.sca(ax2)
    circos.par(canvas_xlim=(-1.5, 1.0), canvas_ylim=(-1.5, 1.0), start_degree=-45, points_overflow_warning=False)
    circos.initialize(sectors, xlim=(0.0, 1.0))
    circos.track(ylim=(0.0, 1.0), bg_col=None, bg_border=None)
    circos.update(sector_index="d")
    circos.text(0.5, 0.5, "second one", nice_facing=True, cex=0.7)
    circos.update(sector_index="c")
    circos.text(0.5, 0.5, "second one", nice_facing=True, cex=0.7)
    circos.clear()
    ax2.set_axis_on()
    ax2.set_xticks([-1.5, -1.0, -0.5, 0.0, 0.5, 1.0])
    ax2.set_yticks([-1.5, -1.0, -0.5, 0.0, 0.5, 1.0])
    ax2.tick_params(labelsize=8)

    # Panel 3: overlaid together on one canvas
    plt.sca(ax3)
    circos.par(canvas_xlim=(-1.0, 1.5), canvas_ylim=(-1.0, 1.5), start_degree=-45, points_overflow_warning=False)
    circos.initialize(sectors, xlim=(0.0, 1.0))
    circos.track(ylim=(0.0, 1.0), bg_col=None, bg_border=None)
    circos.update(sector_index="a")
    circos.text(0.5, 0.5, "first one", nice_facing=True, cex=0.7)
    circos.update(sector_index="b")
    circos.text(0.5, 0.5, "first one", nice_facing=True, cex=0.7)
    circos.clear()

    _common.overlay_axes(fig, ax3)
    circos.par(canvas_xlim=(-1.5, 1.0), canvas_ylim=(-1.5, 1.0), start_degree=-45, points_overflow_warning=False)
    circos.initialize(sectors, xlim=(0.0, 1.0))
    circos.track(ylim=(0.0, 1.0), bg_col=None, bg_border=None)
    circos.update(sector_index="d")
    circos.text(0.5, 0.5, "second one", nice_facing=True, cex=0.7)
    circos.update(sector_index="c")
    circos.text(0.5, 0.5, "second one", nice_facing=True, cex=0.7)
    circos.clear()

    _common.save_fig(fig, "ch07_circlize_separated.png")


def build_ch07_circlize_diff_radius() -> None:
    """Figure 7.6: Four overlaid plots drawing cells at different radii."""
    rng = np.random.default_rng(55)
    sectors = list("abcd")
    lim = [1.0, 1.1, 1.2, 1.3]

    fig = _common.new_figure(6.2, 6.2)
    base_ax = fig.add_subplot(111)

    for i, lval in enumerate(lim):
        if i == 0:
            plt.sca(base_ax)
        else:
            _common.overlay_axes(fig, base_ax)
        circos.par(canvas_xlim=(-lval, lval), canvas_ylim=(-lval, lval), track_height=0.4)
        circos.initialize(sectors, xlim=(0.0, 1.0))
        circos.track(ylim=(0.0, 1.0), bg_border=None)
        circos.update(sector_index=sectors[i], bg_border="black")
        circos.points(rng.uniform(size=10), rng.uniform(size=10), pch=16)
        circos.clear()

    _common.save_fig(fig, "ch07_circlize_diff_radius.png")


def build_ch07_circlize_multiple_layout() -> None:
    """Figure 7.7: Arrange 9 circular plots in a 3x3 Matplotlib subplot grid."""
    rng = np.random.default_rng(12345)
    fig = _common.new_figure(8.4, 8.4)
    axes = fig.subplots(3, 3)

    sectors = [str(k) for k in range(1, 9)]
    for ax in axes.ravel():
        plt.sca(ax)
        circos.par(cell_padding=(0.0, 0.0, 0.0, 0.0))
        circos.initialize(sectors, xlim=(0.0, 1.0))
        circos.track(
            ylim=(0.0, 1.0),
            track_height=0.05,
            bg_col=rand_color(8),
            bg_border=None,
        )
        for _ in range(20):
            s1, s2 = rng.choice(sectors, size=2, replace=False)
            circos.link(
                str(s1),
                rng.uniform(size=2),
                str(s2),
                rng.uniform(size=2),
                col=rand_color(1, transparency=0.4)[0],
                border=None,
            )
        circos.clear()

    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.05, hspace=0.05)
    _common.save_fig(fig, "ch07_circlize_multiple_layout.png")


def main() -> None:
    build_ch07_circlize_zoom()
    build_ch07_circlize_part()
    build_ch07_circlize_part2()
    build_ch07_circlize_nested()
    build_ch07_circlize_separated()
    build_ch07_circlize_diff_radius()
    build_ch07_circlize_multiple_layout()
    print("Generated 7 figures for Chapter 7.")


if __name__ == "__main__":
    main()
