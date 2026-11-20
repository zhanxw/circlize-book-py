"""Generate figures for Chapter 1 (Introduction)."""

from __future__ import annotations

import math
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Circle

from circlize_py import (
    CELL_META,
    as_dendrogram,
    chordDiagram,
    circos,
    colorRamp2,
    color_branches,
    draw,
    generateRandomBed,
    highlight,
    load_extdata,
    mm_y,
    rand_color,
)

import _common


def _make_glance_data() -> pd.DataFrame:
    rng = np.random.default_rng(999)
    n = 1000
    return pd.DataFrame(
        {
            "sectors": rng.choice(list("abcdefgh"), size=n, replace=True),
            "x": rng.normal(size=n),
            "y": rng.uniform(size=n),
        }
    )


def _draw_glance_up_to(stage: int) -> plt.Figure:
    """Render the quick-glance progressive example up to `stage` (1..6)."""
    df = _make_glance_data()
    rng_t3 = np.random.default_rng(101)
    rng_t4 = np.random.default_rng(202)

    fig = _common.new_figure(width=6.2, height=6.2, dpi=140)
    circos.par(track_height=0.1, points_overflow_warning=False)
    circos.initialize(df["sectors"], x=df["x"])

    # Stage 1: Track 1 with axis, sector labels, points, and text
    def _panel_t1(x, y):
        circos.text(
            CELL_META.xcenter,
            CELL_META.cell.ylim[1] + mm_y(5),
            CELL_META.sector_index,
        )
        circos.axis(labels_cex=0.6)

    circos.track(df["sectors"], y=df["y"], panel_fun=_panel_t1)
    col = ["#FF0000", "#00FF00"] * 4
    circos.trackPoints(df["sectors"], df["x"], df["y"], col=col, pch=16, cex=0.5)
    circos.text(-1, 0.5, "text", sector_index="a", track_index=1)

    if stage >= 2:
        bgcol = ["#EFEFEF", "#CCCCCC"] * 4
        circos.trackHist(df["sectors"], df["x"], bin_size=0.2, bg_col=bgcol, col=None)

    if stage >= 3:
        def _panel_t3(x, y):
            ind = rng_t3.choice(len(x), size=10, replace=False)
            x2 = x[ind]
            y2 = y[ind]
            od = np.argsort(x2)
            circos.lines(x2[od], y2[od])

        circos.track(df["sectors"], x=df["x"], y=df["y"], panel_fun=_panel_t3)

    if stage >= 4:
        circos.update(sector_index="d", track_index=2, bg_col="#FF8080", bg_border="black")
        circos.points(x=np.arange(-2, 3), y=np.repeat(0.5, 5), col="white")
        circos.text(CELL_META.xcenter, CELL_META.ycenter, "updated", col="white")

    if stage >= 5:
        def _panel_t4(x, y):
            xlim = CELL_META.xlim
            ylim = CELL_META.ylim
            breaks = np.arange(xlim[0], xlim[1], 0.1)
            if len(breaks) < 2:
                breaks = np.linspace(xlim[0], xlim[1], 6)
            n_breaks = len(breaks)
            seed_val = int(rng_t4.integers(1, 100000))
            circos.rect(
                breaks[:-1],
                np.repeat(ylim[0], n_breaks - 1),
                breaks[1:],
                np.repeat(ylim[1], n_breaks - 1),
                col=rand_color(n_breaks - 1, seed=seed_val),
                border=None,
            )

        circos.track(ylim=[0.0, 1.0], panel_fun=_panel_t4)

    if stage >= 6:
        circos.link("a", 0, "b", 0, h=0.4)
        circos.link("c", [-0.5, 0.5], "d", [-0.5, 0.5], col="red", border="blue", h=0.2)
        circos.link("e", 0, "g", [-1.0, 1.0], col="green", border="black", lwd=2, lty=2)

    circos.clear()
    return fig


def make_examples_overview() -> Path:
    """Create a 3x3 showcase composite highlighting circlize-py capabilities."""
    fig = _common.new_figure(width=11.0, height=11.0, dpi=140)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.02, wspace=0.08, hspace=0.08)

    # Panel 1: Multi-track general circular plot
    ax1 = fig.add_subplot(3, 3, 1)
    plt.sca(ax1)
    rng1 = np.random.default_rng(11)
    secs1 = list("abcdefgh")
    fa1 = np.repeat(secs1, 80)
    x1 = rng1.normal(size=len(fa1))
    y1 = rng1.normal(size=len(fa1))
    circos.par(track_height=0.14, points_overflow_warning=False)
    circos.initialize(fa1, x=x1, ax=ax1)
    circos.track(
        ylim=[-3, 3],
        bg_col=rand_color(8, luminosity="light", seed=11),
        panel_fun=lambda x, y: (
            circos.axis(labels=False, major_tick_length=mm_y(0.8)),
            circos.text(CELL_META.xcenter, CELL_META.ycenter, CELL_META.sector_index, cex=0.65),
        ),
    )
    circos.track(
        fa1,
        x=x1,
        y=y1,
        panel_fun=lambda x, y: circos.points(x, y, pch=16, cex=0.25, col="#1B9E77"),
    )
    circos.trackHist(fa1, x1, bin_size=0.4, col="#377EB880", border="#377EB8")
    circos.link("a", 0, "e", 0, col="#E41A1C80", lwd=1.4)
    circos.link("b", [-1, 1], "f", [-1, 1], col="#7570B355", border="#7570B3")
    circos.clear()

    # Panel 2: Circular Keith Haring doodle
    ax2 = fig.add_subplot(3, 3, 2)
    plt.sca(ax2)
    doodle_imgs = load_extdata("doodle")
    circos.par(cell_padding=[0.0, 0.0, 0.0, 0.0], gap_degree=2.0)
    circos.initialize(list("abcdefghijklmnop"), xlim=[0, 1], ax=ax2)
    circos.track(
        ylim=[0, 1],
        track_height=0.25,
        bg_border=None,
        panel_fun=lambda x, y: circos.raster(
            doodle_imgs[CELL_META.sector_numeric_index - 1],
            CELL_META.xcenter,
            CELL_META.ycenter,
            width=CELL_META.xrange,
            height=CELL_META.yrange,
            facing="bending.inside",
            scaling=0.35,
        ),
    )
    circos.track(
        ylim=[0, 1],
        track_height=0.25,
        bg_border=None,
        panel_fun=lambda x, y: circos.raster(
            doodle_imgs[CELL_META.sector_numeric_index + 15],
            CELL_META.xcenter,
            CELL_META.ycenter,
            width=CELL_META.xrange,
            height=CELL_META.yrange,
            facing="bending.inside",
            scaling=0.35,
        ),
    )
    circos.clear()

    # Panel 3: Human genomic ideogram with tracks, heatmap, and links
    ax3 = fig.add_subplot(3, 3, 3)
    plt.sca(ax3)
    bed_pts = generateRandomBed(nr=180, nc=1, seed=3)
    bed_hm = generateRandomBed(nr=90, nc=4, seed=4)
    l1 = generateRandomBed(nr=25, nc=0, seed=5)
    l2 = generateRandomBed(nr=25, nc=0, seed=6)
    nl = min(len(l1), len(l2))
    circos.par(points_overflow_warning=False)
    circos.initializeWithIdeogram(plot_type=("ideogram", "labels"), labels_cex=0.45, ax=ax3)
    circos.genomicTrack(
        bed_pts,
        track_height=0.14,
        panel_fun=lambda r, v, **kw: circos.genomicPoints(r, v, numeric_column=0, pch=16, cex=0.3, col="#E41A1C", **kw),
    )
    circos.genomicHeatmap(
        bed_hm,
        col=colorRamp2([-1.5, 0.0, 1.5], ["#2166AC", "#F7F7F7", "#B2182B"]),
        side="inside",
        heatmap_height=0.12,
    )
    circos.genomicLink(l1.iloc[:nl], l2.iloc[:nl], col=rand_color(nl, transparency=0.4, seed=7))
    highlight.chromosome("chr1", col="#FF000020", border="red")
    circos.clear()

    # Panel 4: Yin-Yang and Bagua trigrams
    ax4 = fig.add_subplot(3, 3, 4)
    plt.sca(ax4)
    circos.par(gap_degree=8, start_degree=90 + 45 / 2, points_overflow_warning=False)
    circos.initialize([f"T{i}" for i in range(8)], xlim=[0, 1], ax=ax4)
    trigrams = [
        (1, 1, 1),
        (0, 1, 1),
        (1, 0, 1),
        (0, 0, 1),
        (1, 1, 0),
        (0, 1, 0),
        (1, 0, 0),
        (0, 0, 0),
    ]
    for bar_idx in range(3):
        def _draw_tri(x, y, b=bar_idx):
            bits = trigrams[CELL_META.sector_numeric_index - 1]
            if bits[b] == 1:
                circos.rect(0.05, 0.15, 0.95, 0.85, col="black", border="black")
            else:
                circos.rect(0.05, 0.15, 0.43, 0.85, col="black", border="black")
                circos.rect(0.57, 0.15, 0.95, 0.85, col="black", border="black")

        circos.track(ylim=[0, 1], track_height=0.07, bg_border=None, panel_fun=_draw_tri)

    # Central Yin-Yang emblem
    r_yy = 0.56
    draw.sector(90, 270, rou1=r_yy, col="black", border="black", clock_wise=False)
    draw.sector(270, 90, rou1=r_yy, col="white", border="black", clock_wise=False)
    ax4.add_patch(Circle((0, r_yy / 2), r_yy / 2, facecolor="white", edgecolor="none"))
    ax4.add_patch(Circle((0, -r_yy / 2), r_yy / 2, facecolor="black", edgecolor="none"))
    ax4.add_patch(Circle((0, r_yy / 2), r_yy / 7, facecolor="black", edgecolor="none"))
    ax4.add_patch(Circle((0, -r_yy / 2), r_yy / 7, facecolor="white", edgecolor="none"))
    ax4.add_patch(Circle((0, 0), r_yy, facecolor="none", edgecolor="black", linewidth=1.2))
    circos.clear()

    # Panel 5: Dartboard
    ax5 = fig.add_subplot(3, 3, 5)
    plt.sca(ax5)
    nums = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
    circos.par(start_degree=90 + 9, gap_degree=0, cell_padding=[0, 0, 0, 0], track_margin=[0, 0], points_overflow_warning=False)
    circos.initialize([str(n) for n in nums], xlim=[0, 1], ax=ax5)
    circos.track(
        ylim=[0, 1],
        track_height=0.14,
        bg_col="black",
        bg_border="white",
        panel_fun=lambda x, y: circos.text(0.5, 0.5, CELL_META.sector_index, col="white", cex=0.55, facing="inside", niceFacing=True),
    )
    odd_even_rg = ["#E41A1C" if i % 2 == 0 else "#2CA02C" for i in range(20)]
    odd_even_bw = ["black" if i % 2 == 0 else "#F5F2E9" for i in range(20)]
    circos.track(ylim=[0, 1], track_height=0.07, bg_col=odd_even_rg, bg_border="white")
    circos.track(ylim=[0, 1], track_height=0.28, bg_col=odd_even_bw, bg_border="white")
    circos.track(ylim=[0, 1], track_height=0.07, bg_col=odd_even_rg, bg_border="white")
    circos.track(ylim=[0, 1], track_height=0.30, bg_col=odd_even_bw, bg_border="white")
    draw.sector(0, 360, rou1=0.14, col="#2CA02C", border="white", lwd=0.8)
    draw.sector(0, 360, rou1=0.06, col="#E41A1C", border="white", lwd=0.8)
    circos.clear()

    # Panel 6: Nested zoom WGBS DMR
    ax6 = fig.add_subplot(3, 3, 6)
    plt.sca(ax6)
    wb = load_extdata("tagments_WGBS_DMR")
    dmr1 = wb["DMR1"]
    tagments = wb["tagments"]
    corr = wb["correspondance"]
    col_meth = colorRamp2([-0.8, 0.0, 0.8], ["blue", "white", "red"])

    def _f1():
        circos.par(gap_degree=1.5, track_margin=(0.0, 0.005))
        circos.genomicInitialize(tagments, plot_type=None, ax=ax6)
        circos.genomicTrack(
            dmr1,
            ylim=(-1.0, 1.0),
            track_height=0.15,
            bg_col="#EFEFEF",
            panel_fun=lambda region, value: circos.genomicPoints(
                region,
                value,
                pch=16,
                cex=0.35,
                col=[col_meth(v) for v in value.iloc[:, 0]],
            ),
        )

    def _f2():
        circos.initializeWithIdeogram(
            chromosome_index=corr.iloc[:, 0].unique().tolist(),
            plot_type=("ideogram", "labels"),
            track_height=0.06,
            labels_cex=0.45,
        )
        circos.genomicTrack(
            corr.iloc[:, 0:3],
            ylim=(0.0, 1.0),
            track_height=0.1,
            panel_fun=lambda region, value: circos.genomicRect(region, ybottom=0.1, ytop=0.9, col="#377EB880"),
        )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        circos.nested(
            _f1,
            _f2,
            corr.iloc[:, [3, 4, 5, 0, 1, 2]],
            connection_col=rand_color(len(corr), transparency=0.75, seed=9),
            connection_border="#555555",
        )
    circos.clear()

    # Panel 7: Phylogenetic dendrogram (bird.orders)
    ax7 = fig.add_subplot(3, 3, 7)
    plt.sca(ax7)
    hc = load_extdata("bird.orders")
    dend = color_branches(as_dendrogram(hc), k=5, col=["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00"])
    labels = dend.labels()
    n_leaves = len(labels)
    dend_height = float(dend.height)
    circos.par(cell_padding=[0.0, 0.0, 0.0, 0.0])
    circos.initialize(["birds"], xlim=[0.0, float(n_leaves)], ax=ax7)
    circos.track(
        ylim=[0.0, 1.0],
        bg_border=None,
        track_height=0.32,
        panel_fun=lambda x, y: [
            circos.text(i + 0.5, 0.0, lbl, facing="clockwise", niceFacing=True, adj=(0.0, 0.5), cex=0.45)
            for i, lbl in enumerate(labels)
        ],
    )
    circos.track(
        ylim=[0.0, dend_height],
        bg_border=None,
        track_height=0.48,
        panel_fun=lambda x, y: circos.dendrogram(dend, max_height=dend_height, facing="inside"),
    )
    circos.clear()

    # Panel 8: Directional Chord diagram
    ax8 = fig.add_subplot(3, 3, 8)
    plt.sca(ax8)
    rng8 = np.random.default_rng(7)
    mat8 = pd.DataFrame(
        rng8.integers(5, 25, size=(3, 4)),
        index=["S1", "S2", "S3"],
        columns=["E1", "E2", "E3", "E4"],
    )
    grid_col8 = {
        "S1": "#E41A1C",
        "S2": "#377EB8",
        "S3": "#4DAF4A",
        "E1": "#999999",
        "E2": "#B3B3B3",
        "E3": "#CCCCCC",
        "E4": "#7F7F7F",
    }
    chordDiagram(
        mat8,
        grid_col=grid_col8,
        directional=1,
        direction_type=["diffHeight", "arrows"],
        link_arr_type="big.arrow",
        diffHeight=-0.04,
        ax=ax8,
    )
    circos.clear()

    # Panel 9: Split circular heatmap with dendrogram
    ax9 = fig.add_subplot(3, 3, 9)
    plt.sca(ax9)
    rng9 = np.random.default_rng(101)
    mat9 = rng9.normal(size=(48, 8))
    mat9[:16, :4] += 1.6
    mat9[16:32, 4:] += 1.6
    df9 = pd.DataFrame(mat9, index=[f"G{i}" for i in range(48)], columns=[f"C{j}" for j in range(8)])
    split9 = ["Grp1"] * 16 + ["Grp2"] * 16 + ["Grp3"] * 16
    col_fun9 = colorRamp2([-2.0, 0.0, 2.0], ["#00AA00", "#111111", "#EE0000"])
    circos.par(gap_after=[4, 4, 12])
    circos.heatmap(df9, split=split9, col=col_fun9, dend_side="inside", track_height=0.30, ax=ax9)
    circos.clear()

    return _common.save_fig(fig, "ch01_examples_overview.png", dpi=140, tight=True, pad_inches=0.1)


def main() -> None:
    out_paths = [make_examples_overview()]
    stage_files = [
        (1, "ch01_glance_track_1.png"),
        (2, "ch01_glance_track_2.png"),
        (3, "ch01_glance_track_3.png"),
        (4, "ch01_glance_track_update.png"),
        (5, "ch01_glance_track_4.png"),
        (6, "ch01_glance_track_links.png"),
    ]
    for stage, fname in stage_files:
        fig = _draw_glance_up_to(stage)
        out_paths.append(_common.save_fig(fig, fname, dpi=140))

    for p in out_paths:
        print(f"Generated {p}")


if __name__ == "__main__":
    main()
