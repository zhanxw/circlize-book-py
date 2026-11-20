"""Generate figures for Chapter 2 (Circular layout)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import ConnectionPatch

from circlize_py import (
    CELL_META,
    circos,
    circlize,
    cm_h,
    cm_x,
    cm_y,
    draw,
    get_cell_meta_data,
    inch_h,
    load_extdata,
    mm_h,
    mm_x,
    mm_y,
    polar2Cartesian,
    set_track_gap,
)

import _common


def make_coordinate_transformation() -> Path:
    """Port src/intro-03-transformation.R showing data -> polar -> canvas coordinates."""
    fig = _common.new_figure(width=10.0, height=5.4, dpi=140)
    gs = fig.add_gridspec(3, 2, width_ratios=[1.0, 1.15], height_ratios=[1.0, 0.28, 1.05], wspace=0.22, hspace=0.15)

    rng = np.random.default_rng(7)
    x = np.arange(1, 11, dtype=float)
    y = rng.uniform(0.0, 10.0, size=10)

    # Panel 1: Data coordinate (Cartesian rectangle)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(x, y, color="black", linewidth=1.2)
    ax1.text(2.0, 0.0, "text", fontsize=14, ha="center", va="center")
    ax1.add_patch(plt.Rectangle((5.0, 2.0), 2.0, 6.0, fill=False, edgecolor="black", linewidth=1.0))
    ax1.set_xlim(0.0, 10.0)
    ax1.set_ylim(0.0, 10.0)
    ax1.set_yticks([])
    ax1.set_xticks([0, 2, 4, 6, 8, 10])
    ax1.tick_params(labelsize=8)
    ax1.set_title("Data coordinate", fontsize=10, fontweight="bold", pad=6)

    # Panel 2: Polar coordinate (zoomed sector "a")
    ax2 = fig.add_subplot(gs[2, 0])
    plt.sca(ax2)
    sectors = list("abc")
    circos.par(
        canvas_xlim=[-math.sqrt(3) / 2.0, math.sqrt(3) / 2.0],
        canvas_ylim=[0.3, 1.0],
        start_degree=30,
        track_margin=[0.0, 0.0],
        gap_degree=0.0,
        clock_wise=False,
        points_overflow_warning=False,
    )
    circos.initialize(sectors, xlim=[0.0, 10.0], ax=ax2)
    circos.track(sectors, ylim=[0.0, 10.0], track_height=0.4, bg_border=None)
    circos.update(sector_index="a", track_index=1, bg_border="black")
    circos.lines(x, y, sector_index="a", track_index=1, straight=True)
    circos.text(2.0, 0.0, "text", cex=1.4, sector_index="a", track_index=1)
    circos.rect(5.0, 2.0, 7.0, 8.0, sector_index="a", track_index=1)
    circos.axis(h="bottom", major_at=[0, 2, 4, 6, 8, 10], labels_cex=0.65, sector_index="a", track_index=1)
    circos.clear()
    ax2.text(0.0, 0.25, "Polar coordinate", ha="center", va="top", fontsize=10, fontweight="bold")

    # Panel 3: Canvas coordinate (full [-1, 1] x [-1, 1] Matplotlib Axes)
    ax3 = fig.add_subplot(gs[:, 1])
    plt.sca(ax3)
    circos.par(points_overflow_warning=False)
    circos.initialize(sectors, xlim=[1.0, 10.0], ax=ax3)
    circos.track(sectors, ylim=[0.0, 10.0], track_height=0.4)
    circos.update(sector_index="c", track_index=1, bg_border="black")
    circos.lines(x, y, sector_index="c", track_index=1, straight=True)
    circos.text(2.0, 0.0, "text", cex=1.3, sector_index="c", track_index=1)
    circos.rect(5.0, 2.0, 7.0, 8.0, sector_index="c", track_index=1)
    circos.axis(h="bottom", major_at=[0, 2, 4, 6, 8, 10], labels_cex=0.65, sector_index="c", track_index=1)
    circos.clear()

    ax3.set_axis_on()
    ax3.set_xlim(-1.05, 1.05)
    ax3.set_ylim(-1.05, 1.05)
    ax3.set_aspect("equal", adjustable="box")
    ax3.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax3.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax3.tick_params(labelsize=8)
    ax3.set_title("Canvas coordinate", fontsize=10, fontweight="bold", pad=6)

    # Arrows connecting Data -> Polar -> Canvas
    con1 = ConnectionPatch(
        xyA=(5.0, -1.8), coordsA=ax1.transData,
        xyB=(0.0, 1.02), coordsB=ax2.transData,
        arrowstyle="-|>", mutation_scale=14, lw=1.4, color="#333333",
    )
    con2 = ConnectionPatch(
        xyA=(0.75, 0.65), coordsA=ax2.transData,
        xyB=(-1.08, -0.35), coordsB=ax3.transData,
        arrowstyle="-|>", mutation_scale=14, lw=1.4, color="#333333",
    )
    fig.add_artist(con1)
    fig.add_artist(con2)

    return _common.save_fig(fig, "ch02_coordinate_transformation.png", dpi=140)


def make_circlize_order() -> Path:
    """Port src/intro-02-order.R showing step-by-step circular plot construction."""
    fig = _common.new_figure(width=10.5, height=8.2, dpi=140)
    gs = fig.add_gridspec(3, 4, width_ratios=[1.45, 2.0, 1.45, 2.0], wspace=0.1, hspace=0.12)
    rng = np.random.default_rng(42)

    def _text_cell(row: int, col: int, label: str) -> None:
        ax = fig.add_subplot(gs[row, col])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.text(0.5, 0.5, label, ha="center", va="center", fontsize=10.5, family="monospace")

    def _init_4(ax):
        circos.par(gap_degree=5)
        xlim_mat = np.array([[0, 1], [0, 2], [0, 3], [0, 4]], dtype=float)
        circos.initialize(["1", "2", "3", "4"], xlim=xlim_mat, ax=ax)

    # Step 1: circos.initialize()
    _text_cell(0, 0, "circos.initialize()")
    ax_s1 = fig.add_subplot(gs[0, 1])
    plt.sca(ax_s1)
    _init_4(ax_s1)
    circos.track(ylim=[0, 1], bg_border=None)
    for sid in ["1", "2", "3", "4"]:
        de = get_cell_meta_data("cell.start.degree", sid, 1) - circos.par("gap.degree") / 2.0
        rad = math.radians(de)
        ax_s1.plot([0.0, math.cos(rad)], [0.0, math.sin(rad)], linestyle="--", color="#999999", linewidth=1.0)
    draw.sector(start_degree=0, end_degree=360, rou1=1.0, col=None, lty=2, border="#999999")
    circos.clear()

    # Step 2: circos.track()
    _text_cell(0, 2, "circos.track()")
    ax_s2 = fig.add_subplot(gs[0, 3])
    plt.sca(ax_s2)
    _init_4(ax_s2)
    circos.track(ylim=[0, 1])
    circos.clear()

    # Pre-generate deterministic points for tracks 1 and 2
    pts_t1 = [
        (rng.uniform(0, k + 1, size=20), rng.uniform(0, 1, size=20))
        for k in range(4)
    ]
    pts_t2 = [
        (rng.uniform(0, k + 1, size=20), rng.uniform(0, 1, size=20))
        for k in range(4)
    ]

    def _draw_pts_t1(x, y):
        idx = CELL_META.sector_numeric_index - 1
        circos.points(pts_t1[idx][0], pts_t1[idx][1], pch=16, cex=0.55)

    def _draw_pts_t2(x, y):
        idx = CELL_META.sector_numeric_index - 1
        circos.points(pts_t2[idx][0], pts_t2[idx][1], pch=16, cex=0.55)

    # Step 3: add graphics to track 1
    _text_cell(1, 0, "circos.points()\ncircos.lines()\ncircos.text()\n...")
    ax_s3 = fig.add_subplot(gs[1, 1])
    plt.sca(ax_s3)
    _init_4(ax_s3)
    circos.track(ylim=[0, 1], panel_fun=_draw_pts_t1)
    circos.clear()

    # Step 4: second circos.track()
    _text_cell(1, 2, "circos.track()")
    ax_s4 = fig.add_subplot(gs[1, 3])
    plt.sca(ax_s4)
    _init_4(ax_s4)
    circos.track(ylim=[0, 1], panel_fun=_draw_pts_t1)
    circos.track(ylim=[0, 1])
    circos.clear()

    # Step 5: add graphics to track 2
    _text_cell(2, 0, "circos.points()\ncircos.lines()\ncircos.text()\n...")
    ax_s5 = fig.add_subplot(gs[2, 1])
    plt.sca(ax_s5)
    _init_4(ax_s5)
    circos.track(ylim=[0, 1], panel_fun=_draw_pts_t1)
    circos.track(ylim=[0, 1], panel_fun=_draw_pts_t2)
    circos.clear()

    # Step 6: clear
    _text_cell(2, 2, "...\ncircos.clear()")
    ax_s6 = fig.add_subplot(gs[2, 3])
    ax_s6.axis("off")

    return _common.save_fig(fig, "ch02_circlize_order.png", dpi=140)


def make_circlize_coordinate() -> Path:
    """Port src/intro-04-coordinate.R showing sectors, tracks, and cell grid."""
    fig = _common.new_figure(width=6.0, height=6.0, dpi=140)
    rng = np.random.default_rng(12)
    letters = list("abcdefghij")
    perm = rng.permutation(letters).tolist()
    sectors = pd.Categorical(letters, categories=perm, ordered=True)

    circos.par(cell_padding=[0.0, 0.0, 0.0, 0.0], points_overflow_warning=False)
    circos.initialize(sectors=sectors, xlim=[0.0, 10.0])
    for _ in range(4):
        circos.track(ylim=[0.0, 10.0])

    for s in letters:
        circos.rect(0, 0, 10, 10, sector_index=s, track_index=2, col="#FF000040")
    for t in range(1, 5):
        circos.rect(0, 0, 10, 10, sector_index="a", track_index=t, col="#0000FF40")

    circos.info(plot=True)
    circos.clear()
    return _common.save_fig(fig, "ch02_circlize_coordinate.png", dpi=140)


def make_circlize_factor() -> Path:
    """Port src/intro-05-factor.R comparing default alphabetical vs explicit category order."""
    fig = _common.new_figure(width=10.0, height=5.0, dpi=140)
    fa = ["d", "f", "e", "c", "g", "b", "a"]

    ax1 = fig.add_subplot(1, 2, 1)
    plt.sca(ax1)
    s1 = pd.Categorical(fa)
    circos.initialize(sectors=s1, xlim=[0.0, 1.0], ax=ax1)
    circos.track(ylim=[0.0, 1.0])
    circos.info(plot=True)
    ax1.text(0.0, 0.0, "pd.Categorical(sectors)", ha="center", va="center", fontsize=11)
    circos.clear()

    ax2 = fig.add_subplot(1, 2, 2)
    plt.sca(ax2)
    s2 = pd.Categorical(fa, categories=fa, ordered=True)
    circos.initialize(sectors=s2, xlim=[0.0, 1.0], ax=ax2)
    circos.track(ylim=[0.0, 1.0])
    circos.info(plot=True)
    ax2.text(0.0, 0.0, "pd.Categorical(sectors,\n  categories=sectors)", ha="center", va="center", fontsize=11)
    circos.clear()

    return _common.save_fig(fig, "ch02_circlize_factor.png", dpi=140)


def _draw_direction_panel(ax, clock_wise: bool, start_degree: float, label: str) -> None:
    plt.sca(ax)
    sectors = list("abcdefgh")
    circos.par(
        track_margin=[0.1, 0.1],
        clock_wise=clock_wise,
        start_degree=start_degree,
        gap_degree=[2, 10] * 4,
        cell_padding=[0.05, 3, 0.05, 3],
        points_overflow_warning=False,
    )
    circos.initialize(sectors=sectors, xlim=[0.0, 10.0], ax=ax)

    def _panel(x, y):
        circos.text(5.0, 5.0, CELL_META.sector_index, nice_facing=True)
        xlim = CELL_META.xlim
        circos.lines(xlim, [0.0, 0.0])
        circos.lines([9.0, 10.0], [0.5, 0.0])
        circos.lines([9.0, 10.0], [-0.5, 0.0])
        circos.lines([0.0, 0.0], xlim)
        circos.lines([0.5, 0.0], [9.0, 10.0])
        circos.lines([-0.5, 0.0], [9.0, 10.0])

    circos.track(ylim=[0.0, 10.0], track_height=0.4, panel_fun=_panel)
    circos.clear()

    # Outer curved direction arrows on the unit circle
    xs = np.linspace(-0.7, 0.7, 100)
    top_y = np.sqrt(1.0 - xs ** 2)
    bot_y = -np.sqrt(1.0 - xs ** 2)
    ax.plot(xs, top_y, color="black", linewidth=1.0)
    ax.plot(xs, bot_y, color="black", linewidth=1.0)
    if not clock_wise:
        ax.annotate("", xy=(xs[0], top_y[0]), xytext=(xs[2], top_y[2]), arrowprops=dict(arrowstyle="->", lw=1.2, color="black"))
        ax.annotate("", xy=(xs[-1], bot_y[-1]), xytext=(xs[-3], bot_y[-3]), arrowprops=dict(arrowstyle="->", lw=1.2, color="black"))
    else:
        ax.annotate("", xy=(xs[-1], top_y[-1]), xytext=(xs[-3], top_y[-3]), arrowprops=dict(arrowstyle="->", lw=1.2, color="black"))
        ax.annotate("", xy=(xs[0], bot_y[0]), xytext=(xs[2], bot_y[2]), arrowprops=dict(arrowstyle="->", lw=1.2, color="black"))

    ax.text(0.0, 0.0, label, ha="center", va="center", fontsize=8.5)


def make_circlize_direction() -> Path:
    """Port src/intro-07-direction.R comparing counter-clockwise vs clockwise sector order."""
    fig = _common.new_figure(width=10.0, height=5.0, dpi=140)
    ax1 = fig.add_subplot(1, 2, 1)
    _draw_direction_panel(ax1, False, 30.0, "circos.par(clock_wise=False,\nstart_degree=30)")
    ax2 = fig.add_subplot(1, 2, 2)
    _draw_direction_panel(ax2, True, -30.0, "circos.par(clock_wise=True,\nstart_degree=-30)")
    return _common.save_fig(fig, "ch02_circlize_direction.png", dpi=140)


def make_circlize_axis_direction() -> Path:
    """Port src/intro-07-axis-direction.R comparing xaxis.clock.wise=True vs False."""
    fig = _common.new_figure(width=10.0, height=5.0, dpi=140)
    sectors = list("abcdefgh")

    for col_idx, xcw in enumerate((True, False), start=1):
        ax = fig.add_subplot(1, 2, col_idx)
        plt.sca(ax)
        circos.par(
            track_margin=[0.1, 0.1],
            clock_wise=False,
            cell_padding=[0.05, 3, 0.05, 3],
            xaxis_clock_wise=xcw,
            points_overflow_warning=False,
        )
        circos.initialize(sectors=sectors, xlim=[0.0, 10.0], ax=ax)

        def _panel(x, y):
            circos.text(5.0, 5.0, CELL_META.sector_index, nice_facing=True)
            xlim = CELL_META.xlim
            circos.lines(xlim, [0.0, 0.0])
            circos.lines([9.0, 10.0], [0.5, 0.0])
            circos.lines([9.0, 10.0], [-0.5, 0.0])
            circos.lines([0.0, 0.0], xlim)
            circos.lines([0.5, 0.0], [9.0, 10.0])
            circos.lines([-0.5, 0.0], [9.0, 10.0])

        circos.track(ylim=[0.0, 10.0], track_height=0.4, panel_fun=_panel)
        circos.clear()
        ax.text(0.0, 0.0, f"circos.par(\n  xaxis_clock_wise={xcw}\n)", ha="center", va="center", fontsize=8.5)

    return _common.save_fig(fig, "ch02_circlize_axis_direction.png", dpi=140)


def make_circlize_region() -> Path:
    """Port src/intro-06-region.R illustrating cell padding, track margin, and gap degree."""
    fig = _common.new_figure(width=6.4, height=6.4, dpi=140)
    rng = np.random.default_rng(19)
    sectors = list("abcdefgh")

    circos.par(
        canvas_xlim=[0.0, 1.0],
        canvas_ylim=[0.0, 1.0],
        gap_degree=3.0,
        start_degree=20.0,
        track_margin=[0.05, 0.05],
        cell_padding=[0.03, 2.0, 0.03, 2.0],
        clock_wise=False,
        points_overflow_warning=False,
    )
    circos.initialize(sectors=sectors, xlim=[0.0, 10.0])

    def _draw_track_region(margin_frac: float):
        def _panel(x, y):
            xlim = CELL_META.xlim
            ylim = CELL_META.ylim
            cx = CELL_META.cell.xlim
            cy = CELL_META.cell.ylim
            span_y = cy[1] - cy[0]
            circos.rect(xlim[0], ylim[0], xlim[1], ylim[1], col="#377EB8", border="black", lwd=1.0)
            circos.rect(cx[0], cy[1], cx[1], cy[1] + span_y * margin_frac, col="#984EA3", border=None)
            circos.rect(cx[0], cy[0] - span_y * margin_frac, cx[1], cy[0], col="#984EA3", border=None)
            circos.lines(np.arange(11), rng.uniform(0, 10, size=11))
            circos.rect(cx[0], cy[0], cx[1], cy[1], col=None, border="black", lwd=1.8)

        return _panel

    circos.track(ylim=[0.0, 10.0], track_height=0.1, bg_border=None, bg_col="#E41A1C", panel_fun=_draw_track_region(0.5))
    circos.track(ylim=[0.0, 10.0], track_height=0.3, bg_border=None, bg_col="#E41A1C", panel_fun=_draw_track_region(1.0 / 6.0))
    circos.track(ylim=[0.0, 10.0], track_height=0.1, bg_border=None, bg_col="#E41A1C", panel_fun=_draw_track_region(0.5))

    ax = plt.gca()
    for r in (1.0, 0.8, 0.4, 0.2):
        xs = np.linspace(0.0, r, 500)
        ys = np.sqrt(np.maximum(r ** 2 - xs ** 2, 0.0))
        ax.plot(xs, ys, linestyle=":", color="black", linewidth=1.6)

    draw.sector(center=(0.0, 0.0), start_degree=17, end_degree=20, rou1=1.0, rou2=0.2, col="#4DAF4A", clock_wise=False)
    draw.sector(center=(0.0, 0.0), start_degree=62, end_degree=65, rou1=1.0, rou2=0.2, col="#4DAF4A", clock_wise=False)

    circos.text(5.0, 5.0, "plotting region", sector_index="a", track_index=2, cex=0.8)
    circos.text(5.0, 10.5, "cell.padding[2]", sector_index="a", track_index=2, cex=0.75)
    circos.text(5.0, -0.5, "cell.padding[0]", sector_index="a", track_index=2, cex=0.75)
    circos.text(-0.3, 5.0, "cell.padding[1]", facing="clockwise", sector_index="a", track_index=2, cex=0.75)
    circos.text(10.1, 5.0, "cell.padding[3]", facing="clockwise", sector_index="a", track_index=2, cex=0.75)
    circos.text(5.0, -2.0, "track.margin[0]", sector_index="a", track_index=2, cex=0.75)
    circos.text(5.0, 12.0, "track.margin[1]", sector_index="a", track_index=2, cex=0.75)
    circos.text(-1.2, 5.0, "gap.degree", facing="clockwise", sector_index="a", track_index=2, cex=0.75)
    circos.text(10.8, 5.0, "gap.degree", facing="clockwise", sector_index="a", track_index=2, cex=0.75)

    circos.clear()
    return _common.save_fig(fig, "ch02_circlize_region.png", dpi=140)


def make_polar_to_cartesian() -> Path:
    """Offline equivalent of circular-pokemon using bundled doodle tiles via polar2Cartesian."""
    fig = _common.new_figure(width=6.4, height=6.4, dpi=140)
    imgs = load_extdata("doodle")
    names = [f"tile_{i:02d}" for i in range(1, len(imgs) + 1)]

    circos.par(points_overflow_warning=False)
    circos.initialize(names, xlim=[0.0, 1.0])
    ax = plt.gca()

    def _panel(x, y):
        pos = polar2Cartesian(circlize(CELL_META.xcenter, CELL_META.ycenter))
        img = imgs[CELL_META.sector_numeric_index - 1]
        circos.text(
            CELL_META.xcenter,
            CELL_META.cell.ylim[0] - mm_y(2),
            CELL_META.sector_index,
            facing="clockwise",
            nice_facing=True,
            adj=[1.0, 0.5],
            cex=0.6,
        )
        cx, cy = float(pos[0, 0]), float(pos[0, 1])
        ax.imshow(
            img,
            extent=(cx - 0.04, cx + 0.04, cy - 0.04, cy + 0.04),
            origin="upper",
            zorder=3,
        )

    circos.track(ylim=[0.0, 1.0], track_height=0.14, bg_border="black", panel_fun=_panel)
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    circos.clear()
    return _common.save_fig(fig, "ch02_polar_to_cartesian.png", dpi=140)


def make_unit_convert() -> Path:
    """Port unit-convert figure from 02-circlize-layout.Rmd."""
    fig = _common.new_figure(width=6.2, height=6.2, dpi=140)
    rng = np.random.default_rng(77)
    sectors = list("abcdefghij")
    xlim = np.column_stack([np.zeros(10), rng.uniform(0.5, 1.5, size=10)])

    circos.par(cell_padding=[0.0, 0.0, 0.0, 0.0], track_margin=[0.0, 0.0])
    circos.initialize(sectors, xlim=xlim)
    circos.track(
        ylim=[0.0, 1.0],
        track_height=mm_h(5),
        panel_fun=lambda x, y: circos.lines([0.0, mm_x(5)], [0.5, 0.5], col="blue"),
    )
    circos.track(
        ylim=[0.0, 1.0],
        track_height=cm_h(1),
        track_margin=[0.0, mm_h(2)],
        panel_fun=lambda x, y: circos.lines([CELL_META.xcenter, CELL_META.xcenter], [0.0, cm_y(1)], col="red"),
    )
    circos.track(
        ylim=[0.0, 1.0],
        track_height=inch_h(1),
        track_margin=[0.0, mm_h(5)],
        panel_fun=lambda x, y: circos.lines(
            [0.0, cm_x(math.sqrt(2) / 2.0)],
            [0.0, cm_y(math.sqrt(2) / 2.0)],
            col="orange",
        ),
    )
    circos.clear()
    return _common.save_fig(fig, "ch02_unit_convert.png", dpi=140)


def make_set_track_gap() -> Path:
    """Port set-track-gap figure from 02-circlize-layout.Rmd."""
    fig = _common.new_figure(width=6.0, height=6.0, dpi=140)
    circos.initialize(list("abcdefghij"), xlim=[0.0, 1.0])
    circos.track(ylim=[0.0, 1.0])
    set_track_gap(mm_h(2))
    circos.track(ylim=[0.0, 1.0])
    set_track_gap(cm_h(0.5))
    circos.track(ylim=[0.0, 1.0])
    circos.clear()
    return _common.save_fig(fig, "ch02_set_track_gap.png", dpi=140)


def main() -> None:
    funcs = [
        make_coordinate_transformation,
        make_circlize_order,
        make_circlize_coordinate,
        make_circlize_factor,
        make_circlize_direction,
        make_circlize_axis_direction,
        make_circlize_region,
        make_polar_to_cartesian,
        make_unit_convert,
        make_set_track_gap,
    ]
    for fn in funcs:
        out = fn()
        print(f"Generated {out}")


if __name__ == "__main__":
    main()
