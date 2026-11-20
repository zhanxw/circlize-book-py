"""Generate all 28 figures for Chapter 3 (Graphics)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from circlize_py import (
    CELL_META,
    circos,
    circlize,
    cm_x,
    draw,
    get_cell_meta_data,
    highlight,
    load_extdata,
    mm_y,
    rand_color,
)

import _common


def _loess_1d(x: np.ndarray, y: np.ndarray, span: float = 0.75) -> tuple[np.ndarray, np.ndarray]:
    """Pure-NumPy local linear tricube LOESS fit and pointwise standard error."""
    n = len(x)
    k = max(3, int(np.ceil(span * n)))
    y_hat = np.empty(n, dtype=float)
    h_diag = np.empty(n, dtype=float)
    resid = np.empty(n, dtype=float)

    for i in range(n):
        dists = np.abs(x - x[i])
        max_d = np.partition(dists, min(k - 1, n - 1))[min(k - 1, n - 1)]
        max_d = max(max_d, 1e-12)
        u = np.clip(dists / max_d, 0.0, 1.0)
        w = (1.0 - u ** 3) ** 3
        X = np.column_stack([np.ones(n), x - x[i]])
        WX = X * w[:, None]
        xtwx = X.T @ WX + 1e-12 * np.eye(2)
        inv_xtwx = np.linalg.inv(xtwx)
        beta = inv_xtwx @ (WX.T @ y)
        y_hat[i] = beta[0]
        # Hat matrix row: e_0^T (X^T W X)^{-1} X^T W
        h_row = inv_xtwx[0, :] @ (WX.T)
        h_diag[i] = float(np.sum(h_row ** 2))
        resid[i] = y[i] - y_hat[i]

    dof = max(1.0, float(n) - 3.0)
    sigma = float(np.sqrt(np.sum(resid ** 2) / dof))
    se = sigma * np.sqrt(np.maximum(h_diag, 1e-6))
    return y_hat, se


def make_rand_color() -> Path:
    """Port rand_color() showcase grid from 03-graphics.Rmd."""
    fig = _common.new_figure(width=7.6, height=5.8, dpi=140)
    ax = fig.add_subplot(111)
    xs = np.arange(1, 11)
    specs = [
        (1, dict(luminosity="random"), "luminosity='random'"),
        (2, dict(luminosity="bright"), "luminosity='bright'"),
        (3, dict(luminosity="light"), "luminosity='light'"),
        (4, dict(luminosity="dark"), "luminosity='dark'"),
        (5, dict(hue="red", luminosity="bright"), "hue='red', bright"),
        (6, dict(hue="green", luminosity="bright"), "hue='green', bright"),
        (7, dict(hue="blue", luminosity="bright"), "hue='blue', bright"),
        (8, dict(hue="monochrome", luminosity="bright"), "hue='monochrome', bright"),
    ]
    for idx, (y_row, kw, label) in enumerate(specs):
        cols = rand_color(10, seed=100 + idx, **kw)
        ax.scatter(xs, np.repeat(y_row, 10), s=520, c=cols, edgecolors="none")
        ax.text(10.7, y_row, label, va="center", ha="left", fontsize=8.5, family="monospace")
    ax.set_xlim(0.3, 15.6)
    ax.set_ylim(0.3, 8.7)
    ax.axis("off")
    return _common.save_fig(fig, "ch03_rand_color.png", dpi=140)


def make_lines() -> Path:
    """Port src/intro-08-lines.R illustrating line types, baselines, and filled areas."""
    fig = _common.new_figure(width=6.6, height=6.6, dpi=140)
    rng = np.random.default_rng(123)
    sectors = list("abcdefghi")
    circos.par(points_overflow_warning=False)
    circos.initialize(sectors, xlim=[0.0, 10.0])
    circos.track(ylim=[0.0, 10.0], track_height=0.5)

    def _xy():
        return np.sort(rng.uniform(0, 10, size=10)), rng.uniform(0, 8, size=10)

    x, y = _xy()
    circos.lines(x, y, sector_index="a")
    circos.text(5, 9, "type = 'l'", sector_index="a", facing="outside", cex=0.72)

    x, y = _xy()
    circos.lines(x, y, sector_index="b", type="o", cex=0.55)
    circos.text(5, 9, "type = 'o'", sector_index="b", facing="outside", cex=0.72)

    x, y = _xy()
    circos.lines(x, y, sector_index="c", type="h")
    circos.text(5, 9, "type = 'h'", sector_index="c", facing="outside", cex=0.72)

    x, y = _xy()
    cols = ["red" if v > 5 else "green" for v in y]
    circos.lines(x, y, sector_index="d", type="h", baseline=5, col=cols, lwd=2)
    circos.text(5, 9, "type = 'h', baseline = 5\ncol set as list", sector_index="d", facing="outside", cex=0.65)

    x, y = _xy()
    circos.lines(x, y, sector_index="e", type="s")
    circos.text(5, 9, "type = 's'", sector_index="e", facing="outside", cex=0.72)

    x, y = _xy()
    circos.lines(x, y, sector_index="f", area=True)
    circos.text(5, 9, "type = 'l', area = True", sector_index="f", cex=0.68)

    x, y = _xy()
    circos.lines(x, y, sector_index="g", type="o", area=True, cex=0.55)
    circos.text(5, 9, "type = 'o', area = True", sector_index="g", cex=0.68)

    x, y = _xy()
    circos.lines(x, y, sector_index="h", type="s", area=True)
    circos.text(5, 9, "type = 's', area = True", sector_index="h", cex=0.68)

    x, y = _xy()
    circos.lines(x, y, sector_index="i", area=True, baseline="top")
    circos.text(5, 9, "type = 'l', area = True\nbaseline = 'top'", sector_index="i", cex=0.65)

    circos.clear()
    return _common.save_fig(fig, "ch03_lines.png", dpi=140)


def make_linecurve() -> Path:
    """Port src/intro-08-linescurve.R showing straight Cartesian line -> circular arc."""
    fig = _common.new_figure(width=8.6, height=3.0, dpi=140)
    pts = np.linspace(0.0, 1.0, 20)

    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot([0.0, 1.0], [0.0, 1.0], color="black", linewidth=1.2)
    ax1.scatter(pts, pts, s=28, color="black")
    ax1.set_xlim(0.0, 1.0)
    ax1.set_ylim(0.0, 1.0)
    ax1.set_xticks([])
    ax1.set_yticks([])

    ax2 = fig.add_subplot(1, 2, 2)
    plt.sca(ax2)
    circos.par(points_overflow_warning=False, canvas_ylim=[0.0, 1.0], gap_degree=180, start_degree=0, clock_wise=False)
    circos.initialize(["a"], xlim=[0.0, 1.0], ax=ax2)
    circos.track(
        ylim=[0.0, 1.0],
        track_height=0.4,
        panel_fun=lambda x, y: (
            circos.lines([0.0, 1.0], [0.0, 1.0]),
            circos.points(pts, pts, pch=16, cex=0.6),
        ),
    )
    circos.clear()
    return _common.save_fig(fig, "ch03_linecurve.png", dpi=140)


def make_segments() -> Path:
    """Port circlize-segments figure from 03-graphics.Rmd."""
    fig = _common.new_figure(width=6.0, height=6.0, dpi=140)
    circos.initialize(list("abcdefgh"), xlim=[0.0, 1.0])

    def _panel(x, y):
        vals = np.array([0.2, 0.4, 0.6, 0.8])
        circos.segments(vals, 0.1, vals, 0.9)
        circos.segments(0.1, vals, 0.9, vals)

    circos.track(ylim=[0.0, 1.0], track_height=0.3, panel_fun=_panel)
    circos.clear()
    return _common.save_fig(fig, "ch03_segments.png", dpi=140)


def make_text() -> Path:
    """Port src/intro-09-text.R demonstrating all 7 text facing options."""
    fig = _common.new_figure(width=6.4, height=6.4, dpi=140)
    circos.par(points_overflow_warning=False)
    circos.initialize(list("abcd"), xlim=[0.0, 10.0])

    def _panel(x, y):
        circos.text(3, 1, "inside", facing="inside", cex=0.8)
        circos.text(7, 1, "outside", facing="outside", cex=0.8)
        circos.text(0, 5, "reverse.clockwise", facing="reverse.clockwise", adj=[0.5, 0.0], cex=0.8)
        circos.text(10, 5, "clockwise", facing="clockwise", adj=[0.5, 0.0], cex=0.8)
        circos.text(5, 5, "downward", facing="downward", cex=0.8)
        circos.text(3, 9, "====bending.inside====", facing="bending.inside", cex=0.75)
        circos.text(7, 9, "====bending.outside====", facing="bending.outside", cex=0.75)

    circos.track(ylim=[0.0, 10.0], track_height=0.5, panel_fun=_panel)
    circos.clear()
    return _common.save_fig(fig, "ch03_text.png", dpi=140)


def make_text_nice_facing() -> Path:
    """Port src/intro-09-text-niceFacing.R (3x2 comparison grid)."""
    fig = _common.new_figure(width=9.6, height=13.6, dpi=140)

    # First 4 panels: 8 sectors with two tracks
    specs_4 = [
        ("clockwise", "reverse.clockwise", [0.0, 0.5], 5, 3, 7, 5, "facing = 'clockwise'\nadj = (0, 0.5)", "facing = 'reverse.clockwise'\nadj = (0, 0.5)"),
        ("reverse.clockwise", "clockwise", [1.0, 0.5], 3, 5, 7, 5, "facing = 'reverse.clockwise'\nadj = (1, 0.5)", "facing = 'clockwise'\nadj = (1, 0.5)"),
        ("inside", "outside", [0.5, 0.0], 5, 3, 5, 7, "facing = 'inside'\nadj = (0.5, 0)", "facing = 'outside'\nadj = (0.5, 0)"),
        ("outside", "inside", [0.5, 1.0], 5, 3, 5, 7, "facing = 'outside'\nadj = (0.5, 1)", "facing = 'inside'\nadj = (0.5, 1)"),
    ]

    for p_idx, (f1, f2, adj, x1, y1, x2, y2, lbl1, lbl2) in enumerate(specs_4, start=1):
        ax = fig.add_subplot(3, 2, p_idx)
        plt.sca(ax)
        circos.par(points_overflow_warning=False)
        circos.initialize(list("abcdefgh"), xlim=[0.0, 10.0], ax=ax)

        def _make_pf(facing_str, title_str):
            def _pf(x, y):
                if CELL_META.sector_index == "f":
                    circos.text(5, 5, title_str, facing="inside", cex=0.58)
                else:
                    circos.points(x1, y1, pch=16, col="red", cex=0.8)
                    circos.text(x1, y1, "rawText", facing=facing_str, adj=adj, cex=0.65)
                    circos.points(x2, y2, pch=16, col="red", cex=0.8)
                    circos.text(x2, y2, "niceFacing", facing=facing_str, nice_facing=True, adj=adj, cex=0.65)

            return _pf

        circos.track(ylim=[0.0, 10.0], track_height=0.2, panel_fun=_make_pf(f1, lbl1))
        circos.track(ylim=[0.0, 10.0], track_height=0.2, panel_fun=_make_pf(f2, lbl2))
        circos.clear()

    # Last 2 panels: bending.inside & bending.outside
    specs_bend = [
        (5, "bending.inside", "bending.outside", [0.5, 0.0], "facing = 'bending.inside'\nadj = (0.5, 0)", "facing = 'bending.outside'\nadj = (0.5, 0)"),
        (6, "bending.outside", "bending.inside", [0.5, 1.0], "facing = 'bending.outside'\nadj = (0.5, 1)", "facing = 'bending.inside'\nadj = (0.5, 1)"),
    ]
    for p_idx, f1, f2, adj, lbl1, lbl2 in specs_bend:
        ax = fig.add_subplot(3, 2, p_idx)
        plt.sca(ax)
        circos.par(start_degree=90, points_overflow_warning=False)
        circos.initialize(list("abcd"), xlim=[0.0, 10.0], sector_width=[7 / 3, 7 / 3, 7 / 3, 1.0], ax=ax)

        def _make_bend_pf(facing_str, title_str, reps_raw, reps_nice):
            def _pf(x, y):
                if CELL_META.sector_index == "d":
                    circos.text(5, 5, title_str, facing="inside", cex=0.55)
                else:
                    circos.points(5, 3, pch=16, col="red", cex=0.8)
                    circos.text(5, 3, "rawText" * reps_raw, facing=facing_str, adj=adj, cex=0.62)
                    circos.points(5, 7, pch=16, col="red", cex=0.8)
                    circos.text(5, 7, "niceFacing" * reps_nice, facing=facing_str, nice_facing=True, adj=adj, cex=0.62)

            return _pf

        circos.track(ylim=[0.0, 10.0], track_height=0.2, panel_fun=_make_bend_pf(f1, lbl1, 4, 3))
        circos.track(ylim=[0.0, 10.0], track_height=0.2, panel_fun=_make_bend_pf(f2, lbl2, 3, 2))
        circos.clear()

    return _common.save_fig(fig, "ch03_text_nice_facing.png", dpi=140)


def make_errorline() -> Path:
    """Port src/intro-10-smooth.R using circos.polygon for LOESS SE ribbon."""
    fig = _common.new_figure(width=5.8, height=5.8, dpi=140)
    rng = np.random.default_rng(123)
    circos.initialize(list("abcd"), xlim=[0.0, 1.0])

    def _panel(x, y):
        x1 = np.sort(rng.uniform(0.0, 1.0, size=20))
        y1 = x1 + rng.normal(size=20)
        fit, se = _loess_1d(x1, y1, span=0.75)
        d1 = np.concatenate([x1, x1[::-1]])
        d2 = np.concatenate([fit + se, (fit - se)[::-1]])
        circos.polygon(d1, d2, col="#CCCCCC", border=None)
        circos.points(x1, y1, cex=0.5)
        circos.lines(x1, fit)

    circos.track(ylim=[-3.0, 3.0], track_height=0.4, panel_fun=_panel)
    circos.clear()
    return _common.save_fig(fig, "ch03_errorline.png", dpi=140)


def make_xaxis() -> Path:
    """Port src/intro-11-axis.R showing 8 x-axis customizations."""
    fig = _common.new_figure(width=6.6, height=6.6, dpi=140)
    sectors = list("abcdefgh")
    circos.par(points_overflow_warning=False)
    circos.initialize(sectors, xlim=[0.0, 10.0])
    circos.track(
        ylim=[0.0, 10.0],
        track_height=0.1,
        bg_border=None,
        panel_fun=lambda x, y: circos.text(5, 10, CELL_META.sector_index, nice_facing=True),
    )
    circos.track(ylim=[0.0, 10.0])

    circos.axis(labels_nice_facing=False, sector_index="a", labels_cex=0.8)
    circos.axis(labels_nice_facing=False, sector_index="b", direction="inside", labels_facing="outside", labels_cex=0.8)
    circos.axis(labels_nice_facing=False, sector_index="c", h="bottom", labels_cex=0.8)
    circos.axis(labels_nice_facing=False, sector_index="d", h="bottom", direction="inside", labels_facing="reverse.clockwise", labels_cex=0.8)
    circos.axis(labels_nice_facing=False, sector_index="e", h=5, major_at=[1, 3, 5, 7, 9], labels_cex=0.8)
    circos.axis(labels_nice_facing=False, sector_index="f", h=5, major_at=[1, 3, 5, 7, 9], labels=["a", "c", "e", "g", "f"], minor_ticks=0, labels_cex=0.8)
    circos.axis(labels_nice_facing=False, sector_index="g", h=5, major_at=[1, 3, 5, 7, 9], labels=["a1", "c1", "e1", "g1", "f1"], major_tick=False, labels_facing="reverse.clockwise", labels_cex=0.8)
    circos.axis(
        labels_nice_facing=False,
        sector_index="h",
        h=2,
        major_at=[1, 3, 5, 7, 9],
        labels=["a1", "c1", "e1", "g1", "f1"],
        major_tick_length=mm_y(5, sector_index="h", track_index=2),
        minor_ticks=2,
        labels_facing="clockwise",
        labels_cex=0.8,
    )
    circos.clear()
    return _common.save_fig(fig, "ch03_xaxis.png", dpi=140)


def make_yaxis() -> Path:
    """Port src/intro-11-yaxis.R showing left and right y-axes."""
    fig = _common.new_figure(width=6.2, height=6.2, dpi=140)
    sectors = list("abcdefgh")
    circos.par(points_overflow_warning=False, gap_degree=8)
    circos.initialize(sectors, xlim=[0.0, 10.0])
    circos.track(ylim=[0.0, 10.0], track_height=0.5)
    for s in ["b", "c", "d"]:
        circos.yaxis(side="left", sector_index=s, labels_cex=0.75)
    for s in ["e", "f", "g"]:
        circos.yaxis(side="right", sector_index=s, labels_cex=0.75)
    circos.clear()
    return _common.save_fig(fig, "ch03_yaxis.png", dpi=140)


def make_barplot() -> Path:
    """Port circlize-barplot (1D, signed, and stacked matrix barplots)."""
    fig = _common.new_figure(width=10.0, height=5.0, dpi=140)
    rng = np.random.default_rng(11)
    pos = np.arange(1, 11) - 0.5

    ax1 = fig.add_subplot(1, 2, 1)
    plt.sca(ax1)
    circos.initialize(list("abcd"), xlim=[0.0, 10.0], ax=ax1)
    circos.track(
        ylim=[0.0, 1.0],
        panel_fun=lambda x, y: circos.barplot(rng.uniform(0, 1, size=10), pos, col=list(range(1, 11))),
    )
    def _signed(x, y):
        val = rng.uniform(-1.0, 1.0, size=10)
        circos.barplot(val, pos, col=[2 if v > 0 else 3 for v in val])
    circos.track(ylim=[-1.0, 1.0], panel_fun=_signed)
    circos.clear()

    ax2 = fig.add_subplot(1, 2, 2)
    plt.sca(ax2)
    circos.initialize(list("abcd"), xlim=[0.0, 10.0], ax=ax2)
    circos.track(
        ylim=[0.0, 4.0],
        panel_fun=lambda x, y: circos.barplot(rng.uniform(0, 1, size=(10, 4)), pos, col=[2, 3, 4, 5]),
    )
    circos.clear()
    return _common.save_fig(fig, "ch03_barplot.png", dpi=140)


def make_boxplot() -> Path:
    """Port circlize-boxplot (one-by-one vs batch list/matrix)."""
    fig = _common.new_figure(width=10.0, height=5.0, dpi=140)
    rng = np.random.default_rng(22)

    ax1 = fig.add_subplot(1, 2, 1)
    plt.sca(ax1)
    circos.initialize(list("abcd"), xlim=[0.0, 10.0], ax=ax1)
    def _single_box(x, y):
        for p in np.arange(0.5, 10.0, 1.0):
            circos.boxplot(rng.uniform(0, 1, size=10), p, cex=0.6)
    circos.track(ylim=[0.0, 1.0], panel_fun=_single_box)
    circos.clear()

    ax2 = fig.add_subplot(1, 2, 2)
    plt.sca(ax2)
    circos.initialize(list("abcd"), xlim=[0.0, 10.0], ax=ax2)
    circos.track(
        ylim=[0.0, 1.0],
        panel_fun=lambda x, y: circos.boxplot(
            [rng.uniform(0, 1, size=10) for _ in range(10)],
            np.arange(1, 11) - 0.5,
            col=list(range(1, 11)),
            cex=0.6,
        ),
    )
    circos.clear()
    return _common.save_fig(fig, "ch03_boxplot.png", dpi=140)


def make_violinplot() -> Path:
    """Port circlize-violinplot (one-by-one vs batch list/matrix)."""
    fig = _common.new_figure(width=10.0, height=5.0, dpi=140)
    rng = np.random.default_rng(33)

    ax1 = fig.add_subplot(1, 2, 1)
    plt.sca(ax1)
    circos.initialize(list("abcd"), xlim=[0.0, 10.0], ax=ax1)
    def _single_vio(x, y):
        for p in np.arange(0.5, 10.0, 1.0):
            circos.violin(rng.uniform(0, 1, size=10), p, cex=0.5)
    circos.track(ylim=[0.0, 1.0], panel_fun=_single_vio)
    circos.clear()

    ax2 = fig.add_subplot(1, 2, 2)
    plt.sca(ax2)
    circos.initialize(list("abcd"), xlim=[0.0, 10.0], ax=ax2)
    circos.track(
        ylim=[0.0, 1.0],
        panel_fun=lambda x, y: circos.violin(
            [rng.uniform(0, 1, size=10) for _ in range(10)],
            np.arange(1, 11) - 0.5,
            col=list(range(1, 11)),
            cex=0.5,
        ),
    )
    circos.clear()
    return _common.save_fig(fig, "ch03_violinplot.png", dpi=140)


def make_circular_arrow() -> Path:
    """Port circular-arrow figure comparing arrow_position='end' and 'start'."""
    fig = _common.new_figure(width=10.0, height=5.0, dpi=140)
    cols = rand_color(4, seed=44)
    tails = ["point", "normal", "point", "normal"]

    for col_idx, pos in enumerate(("end", "start"), start=1):
        ax = fig.add_subplot(1, 2, col_idx)
        plt.sca(ax)
        circos.initialize(list("abcd"), xlim=[0.0, 1.0], ax=ax)
        circos.track(
            ylim=[0.0, 1.0],
            bg_border=None,
            track_height=0.4,
            panel_fun=lambda x, y, p=pos: circos.arrow(
                x1=0.0,
                x2=1.0,
                y=0.5,
                width=0.4,
                arrow_head_width=0.6,
                arrow_head_length=cm_x(1.0),
                col=cols[CELL_META.sector_numeric_index - 1],
                tail=tails[CELL_META.sector_numeric_index - 1],
                arrow_position=p,
            ),
        )
        circos.clear()

    return _common.save_fig(fig, "ch03_circular_arrow.png", dpi=140)


def make_cell_cycle() -> Path:
    """Port cell-cycle figure using circos.arrow."""
    fig = _common.new_figure(width=5.6, height=5.6, dpi=140)
    phases = ["G1", "S", "G2", "M"]
    cell_cycle = pd.DataFrame(
        {
            "phase": pd.Categorical(phases, categories=phases, ordered=True),
            "hour": [11.0, 8.0, 4.0, 1.0],
        }
    )
    colors = ["#66C2A5", "#FC8D62", "#8DA0CB", "#E78AC3"]
    circos.par(start_degree=90, points_overflow_warning=False)
    xlim = np.column_stack([np.zeros(4), cell_cycle["hour"].to_numpy()])
    circos.initialize(cell_cycle["phase"], xlim=xlim)

    def _panel(x, y):
        circos.arrow(
            CELL_META.xlim[0],
            CELL_META.xlim[1],
            arrow_head_width=CELL_META.yrange * 0.8,
            arrow_head_length=cm_x(0.5),
            col=colors[CELL_META.sector_numeric_index - 1],
        )
        circos.text(CELL_META.xcenter, CELL_META.ycenter, CELL_META.sector_index, facing="downward")
        circos.axis(h=1.0, major_at=np.arange(0, int(round(CELL_META.xlim[1])) + 1), minor_ticks=1, labels_cex=0.6)

    circos.track(ylim=[0.0, 1.0], bg_border=None, track_height=0.3, panel_fun=_panel)
    circos.clear()
    return _common.save_fig(fig, "ch03_cell_cycle.png", dpi=140)


def make_labels() -> Path:
    """Port circos.labels inside vs outside figure."""
    fig = _common.new_figure(width=10.0, height=5.0, dpi=140)
    sectors = list("abcdefgh")

    ax1 = fig.add_subplot(1, 2, 1)
    plt.sca(ax1)
    circos.initialize(sectors=sectors, xlim=[0.0, 1.0], ax=ax1)
    circos.track(ylim=[0.0, 1.0])
    circos.labels(["a", "a", "b", "b"], x=[0.1, 0.12, 0.4, 0.6], labels=["0.1", "0.12", "0.4", "0.6"])
    circos.clear()

    ax2 = fig.add_subplot(1, 2, 2)
    plt.sca(ax2)
    circos.initialize(sectors=sectors, xlim=[0.0, 1.0], ax=ax2)
    circos.labels(["a", "a", "b", "b"], x=[0.1, 0.12, 0.4, 0.6], labels=["0.1", "0.12", "0.4", "0.6"], side="outside")
    circos.track(ylim=[0.0, 1.0])
    circos.clear()

    return _common.save_fig(fig, "ch03_labels.png", dpi=140)


def make_raster_normal() -> Path:
    """Port raster-normal figure using bundled Rlogo.png."""
    fig = _common.new_figure(width=5.8, height=5.8, dpi=140)
    img = load_extdata("Rlogo.png")
    circos.par(start_degree=90)
    circos.initialize(list("abcde"), xlim=[0.0, 1.0])
    facings = ["inside", "outside", "reverse.clockwise", "clockwise", "downward"]

    def _panel(x, y):
        f = facings[CELL_META.sector_numeric_index - 1]
        circos.raster(img, CELL_META.xcenter, CELL_META.ycenter, width="1cm", facing=f)
        circos.text(CELL_META.xcenter, CELL_META.ycenter, f, facing="inside", nice_facing=True, cex=0.85)

    circos.track(ylim=[0.0, 1.0], panel_fun=_panel)
    circos.clear()
    return _common.save_fig(fig, "ch03_raster_normal.png", dpi=140)


def make_raster_doodle() -> Path:
    """Port raster-doodle figure using bundled doodle dataset with bending.inside."""
    fig = _common.new_figure(width=6.0, height=6.0, dpi=140)
    imgs = load_extdata("doodle")
    circos.par(cell_padding=[0.0, 0.0, 0.0, 0.0])
    circos.initialize(list("abcdefghijklmnop"), xlim=[0.0, 1.0])

    circos.track(
        ylim=[0.0, 1.0],
        track_height=0.25,
        bg_border=None,
        panel_fun=lambda x, y: circos.raster(
            imgs[CELL_META.sector_numeric_index - 1],
            CELL_META.xcenter,
            CELL_META.ycenter,
            width=CELL_META.xrange,
            height=CELL_META.yrange,
            facing="bending.inside",
            scaling=0.5,
        ),
    )
    circos.track(
        ylim=[0.0, 1.0],
        track_height=0.25,
        bg_border=None,
        panel_fun=lambda x, y: circos.raster(
            imgs[CELL_META.sector_numeric_index + 15],
            CELL_META.xcenter,
            CELL_META.ycenter,
            width=CELL_META.xrange,
            height=CELL_META.yrange,
            facing="bending.inside",
            scaling=0.5,
        ),
    )
    circos.clear()
    return _common.save_fig(fig, "ch03_raster_doodle.png", dpi=140)


def _init_link_track(ax=None) -> None:
    sectors = list("abcdefgh")
    circos.par(points_overflow_warning=False)
    circos.initialize(sectors, xlim=[0.0, 10.0], ax=ax)
    circos.track(sectors, ylim=[0.0, 1.0], bg_col="grey", bg_border=None, track_height=0.05)


def make_link_example() -> Path:
    """Port link-example figure."""
    fig = _common.new_figure(width=5.4, height=5.4, dpi=140)
    _init_link_track()
    circos.link("a", 5, "c", 5, border="black")
    circos.link("b", 5, "d", [4, 6], border="black")
    circos.link("a", [2, 3], "f", [4, 6], border="black")
    circos.link("e", [2, 3], "g", 5, border="black")
    circos.clear()
    return _common.save_fig(fig, "ch03_link_example.png", dpi=140)


def make_link_end() -> Path:
    """Port link-end figure showing rou2=0.5."""
    fig = _common.new_figure(width=5.4, height=5.4, dpi=140)
    _init_link_track()
    circos.link("a", 5, "c", 5, rou2=0.5, border="black")
    circos.link("b", 5, "d", [4, 6], rou2=0.5, border="black")
    circos.link("a", [2, 3], "f", [4, 6], rou2=0.5, border="black")
    circos.clear()
    return _common.save_fig(fig, "ch03_link_end.png", dpi=140)


def make_link_height() -> Path:
    """Port link-height figure comparing default h vs h=0.5, h2=0.2."""
    fig = _common.new_figure(width=5.4, height=5.4, dpi=140)
    _init_link_track()
    circos.link("a", 10, "b", [1, 9], border="black")
    circos.text(9, -8, "default h", adj=[0.0, 0.5], sector_index="a", facing="downward")
    circos.link("c", 10, "d", [1, 9], h=0.5, h2=0.2, border="black")
    circos.text(1, -3, "h = 0.5\nh2 = 0.2", adj=[0.0, 0.5], sector_index="e", facing="downward")
    circos.clear()
    return _common.save_fig(fig, "ch03_link_height.png", dpi=140)


def make_link_ratio() -> Path:
    """Port link-ratio (1x3) figure showing h_ratio = 0.7, 0.5, 0.3."""
    fig = _common.new_figure(width=11.4, height=4.0, dpi=140)
    rng = np.random.default_rng(77)
    sectors = list("abcdefgh")
    s1 = rng.choice(sectors, size=100, replace=True)
    p1 = rng.uniform(0, 10, size=100)
    s2 = rng.choice(sectors, size=100, replace=True)
    p2 = rng.uniform(0, 10, size=100)

    titles = ["h_ratio = 0.7", "h_ratio = 0.5\ndefault", "h_ratio = 0.3"]
    for idx, (hr, ttl) in enumerate(zip((0.7, 0.5, 0.3), titles), start=1):
        ax = fig.add_subplot(1, 3, idx)
        plt.sca(ax)
        _init_link_track(ax=ax)
        for i in range(100):
            circos.link(s1[i], p1[i], s2[i], p2[i], h_ratio=hr)
        circos.clear()
        ax.text(-1.0, 1.0, ttl, ha="left", va="top", fontsize=9.5)

    return _common.save_fig(fig, "ch03_link_ratio.png", dpi=140)


def make_link_shape() -> Path:
    """Port link-shape figure showing h and Bezier weight w variations."""
    fig = _common.new_figure(width=5.8, height=5.8, dpi=140)
    sectors = list("abcdefgh")
    circos.par(points_overflow_warning=False, circle_margin=[0.28, 0.02, 0.02, 0.28])
    circos.initialize(sectors, xlim=[0.0, 10.0])
    circos.track(sectors, ylim=[0.0, 1.0], bg_col="grey", bg_border=None, track_height=0.05)
    circos.link("a", 5, "b", 5)
    circos.text(10, -5, "default", facing="outside", sector_index="a", cex=0.8)
    circos.link("b", 5, "c", 5, h=0.2)
    circos.text(10, -5, "h=0.2", facing="outside", sector_index="b", cex=0.8)
    circos.link("c", 5, "d", 5, h=0.8)
    circos.text(10, -5, "h=0.8", facing="outside", sector_index="c", cex=0.8)
    circos.link("d", 5, "e", 5, w=2)
    circos.text(10, -5, "w=2", facing="downward", sector_index="d", cex=0.8)
    circos.link("e", 5, "f", 5, w=-0.5)
    circos.text(10, 5, "w=-0.5", sector_index="e", cex=0.8)
    circos.link("f", 5, "g", 5, w=0.1, h=0.3)
    circos.text(10, -5, "w=0.1\nh=0.3", sector_index="f", cex=0.8)
    circos.clear()
    return _common.save_fig(fig, "ch03_link_shape.png", dpi=140)


def make_link_hill() -> Path:
    """Port link-hill figure for self-overlapping ribbon."""
    fig = _common.new_figure(width=5.4, height=5.4, dpi=140)
    _init_link_track()
    circos.link("a", [2, 6], "a", [3, 7])
    circos.clear()
    return _common.save_fig(fig, "ch03_link_hill.png", dpi=140)


def make_link_arrow() -> Path:
    """Port link-arrow figure showing directional arrows and big.arrow ribbons."""
    fig = _common.new_figure(width=5.4, height=5.4, dpi=140)
    _init_link_track()
    circos.link("a", 5, "b", 5, directional=1, arr_length=0.2)
    circos.link("c", [3, 7], "d", [3, 7], directional=1, arr_col="white", arr_length=0.2)
    circos.link("e", [4, 6], "f", [4, 6], directional=1, arr_type="big.arrow", arr_length=0.04)
    circos.clear()
    return _common.save_fig(fig, "ch03_link_arrow.png", dpi=140)


def make_draw_sector_general() -> Path:
    """Port draw-sector-general standalone polar wedge examples."""
    fig = _common.new_figure(width=5.4, height=5.4, dpi=140)
    ax = fig.add_subplot(111)
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    draw.sector(20, 0, ax=ax)
    draw.sector(30, 60, rou1=0.8, rou2=0.5, clock_wise=False, col="#FF000080", ax=ax)
    draw.sector(350, 1000, col="#00FF0080", border=None, ax=ax)
    draw.sector(0, 180, rou1=0.25, center=(-0.5, 0.5), border=2, lwd=2, lty=2, ax=ax)
    draw.sector(0, 360, rou1=0.7, rou2=0.6, col="#0000FF80", ax=ax)
    circos.clear()
    return _common.save_fig(fig, "ch03_draw_sector_general.png", dpi=140)


def make_highlight() -> Path:
    """Port circlize-highlight figure using draw.sector and cell metadata."""
    fig = _common.new_figure(width=5.6, height=5.6, dpi=140)
    sectors = list("abcdefgh")
    circos.initialize(sectors, xlim=[0.0, 1.0])
    for _ in range(3):
        circos.track(ylim=[0.0, 1.0])
    circos.info(plot=True)

    draw.sector(
        get_cell_meta_data("cell.start.degree", sector_index="a"),
        get_cell_meta_data("cell.end.degree", sector_index="a"),
        rou1=get_cell_meta_data("cell.top.radius", track_index=1),
        col="#FF000040",
    )
    draw.sector(
        0,
        360,
        rou1=get_cell_meta_data("cell.top.radius", track_index=1),
        rou2=get_cell_meta_data("cell.bottom.radius", track_index=1),
        col="#00FF0040",
    )
    draw.sector(
        get_cell_meta_data("cell.start.degree", sector_index="e"),
        get_cell_meta_data("cell.end.degree", sector_index="f"),
        rou1=get_cell_meta_data("cell.top.radius", track_index=2),
        rou2=get_cell_meta_data("cell.bottom.radius", track_index=3),
        col="#0000FF40",
    )
    pos = circlize([0.2, 0.8], [0.2, 0.8], sector_index="h", track_index=2)
    draw.sector(pos[0, "theta"], pos[1, "theta"], pos[0, "rou"], pos[1, "rou"], clock_wise=True, col="#00FFFF40")
    circos.clear()
    return _common.save_fig(fig, "ch03_highlight.png", dpi=140)


def make_highlight_sector() -> Path:
    """Port circlize-highlight-sector figure using highlight.sector()."""
    fig = _common.new_figure(width=5.8, height=5.8, dpi=140)
    sectors = list("abcdefgh")
    circos.initialize(sectors, xlim=[0.0, 1.0])
    for _ in range(4):
        circos.track(ylim=[0.0, 1.0])
    circos.info(plot=True)

    highlight.sector(
        ["a", "h"],
        track_index=1,
        text="a and h belong to a same group",
        facing="bending.inside",
        nice_facing=True,
        text_vjust="6mm",
        cex=0.8,
    )
    highlight.sector("c", col="#00FF0040")
    highlight.sector("d", col=None, border="red", lwd=2)
    highlight.sector("e", col="#0000FF40", track_index=[2, 3])
    highlight.sector(["f", "g"], col=None, border="green", lwd=2, track_index=[2, 3], padding=[0.1, 0.1, 0.1, 0.1])
    highlight.sector(sectors, col="#FFFF0040", track_index=4)
    circos.clear()
    return _common.save_fig(fig, "ch03_highlight_sector.png", dpi=140)


def make_matplotlib_integration() -> Path:
    """Port circlize-base figure demonstrating Matplotlib Axes integration."""
    fig = _common.new_figure(width=6.0, height=6.0, dpi=140)
    ax = fig.add_subplot(111)
    sectors = list("abcd")
    circos.initialize(sectors, xlim=[0.0, 1.0], ax=ax)
    vals = np.arange(1, 21) / 20.0
    circos.track(ylim=[0.0, 1.0], panel_fun=lambda x, y: circos.points(vals, vals))

    ax.text(0.0, 0.0, "This is\nthe center", ha="center", va="center", fontsize=14)
    handle = Line2D([0], [0], marker="o", linestyle="None", markerfacecolor="none", markeredgecolor="black", markersize=6)
    ax.legend([handle], ["This is the legend"], loc="lower left", frameon=True, fontsize=9)
    ax.set_title("This is the title", fontsize=14, fontweight="bold", pad=10)
    circos.clear()
    return _common.save_fig(fig, "ch03_matplotlib_integration.png", dpi=140)


def main() -> None:
    funcs = [
        make_rand_color,
        make_lines,
        make_linecurve,
        make_segments,
        make_text,
        make_text_nice_facing,
        make_errorline,
        make_xaxis,
        make_yaxis,
        make_barplot,
        make_boxplot,
        make_violinplot,
        make_circular_arrow,
        make_cell_cycle,
        make_labels,
        make_raster_normal,
        make_raster_doodle,
        make_link_example,
        make_link_end,
        make_link_height,
        make_link_ratio,
        make_link_shape,
        make_link_hill,
        make_link_arrow,
        make_draw_sector_general,
        make_highlight,
        make_highlight_sector,
        make_matplotlib_integration,
    ]
    for fn in funcs:
        out = fn()
        print(f"Generated {out}")


if __name__ == "__main__":
    main()
