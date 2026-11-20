"""Generate all figures for Chapter 5 (Implement high-level circular plots)."""

from __future__ import annotations

import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

import _common
from circlize import (
    CELL_META,
    as_dendrogram,
    circos,
    color_branches,
    color_ramp2,
    cutree,
    hclust_from_data,
    load_extdata,
    mm_x,
)


def build_ch05_circular_barplot() -> None:
    """Figure 5.1: Single-sector horizontal circular barplot."""
    rng = np.random.default_rng(123)
    category = [f"category_{i}" for i in range(1, 10)]
    percent = np.sort(rng.integers(40, 81, size=9))
    cmap = plt.get_cmap("rainbow")
    color = [mcolors.to_hex(cmap(v)) for v in np.linspace(1.0, 0.0, len(percent))]

    fig = _common.new_figure(6.2, 6.2)
    circos.par(start_degree=90, cell_padding=(0.0, 0.0, 0.0, 0.0), points_overflow_warning=False)
    circos.initialize(["a"], xlim=(0.0, 100.0))

    def panel_bar(x, y):
        xlim = CELL_META.xlim
        ys = np.arange(1, 10, dtype=float)
        circos.segments(np.repeat(xlim[0], 9), ys, np.repeat(xlim[1], 9), ys, col="#CCCCCC")
        circos.rect(np.zeros(9), ys - 0.45, percent, ys + 0.45, col=color, border="white")
        circos.text(
            xlim[0] - mm_x(2.0, h=ys),
            ys,
            [f"{cat} - {pct}%" for cat, pct in zip(category, percent)],
            facing="downward",
            adj=(1.0, 0.5),
            cex=0.8,
        )
        breaks = np.arange(0, 86, 5)
        circos.axis(
            h="top",
            major_at=breaks,
            labels=[f"{b}%" for b in breaks],
            labels_cex=0.6,
        )

    circos.track(ylim=(0.5, len(percent) + 0.5), track_height=0.8, bg_border=None, panel_fun=panel_bar)
    circos.clear()
    _common.save_fig(fig, "ch05_circular_barplot.png")


def build_ch05_circular_histograms() -> None:
    """Figure 5.2: Three-track circular histograms (default, fixed bin_size, density)."""
    rng = np.random.default_rng(42)
    x = rng.normal(size=1600)
    sectors = rng.choice(list("abcdefghijklmnop"), size=1600, replace=True)

    fig = _common.new_figure(6.4, 6.4)
    circos.initialize(sectors, x=x)
    circos.trackHist(sectors, x=x, col="#999999", border="#999999")
    circos.trackHist(sectors, x=x, bin_size=0.1, col="#999999", border="#999999")
    circos.trackHist(sectors, x=x, draw_density=True, col="#999999", border="#999999")
    circos.clear()
    _common.save_fig(fig, "ch05_circular_histograms.png")


def build_ch05_phylogenetic_tree() -> None:
    """Figure 5.3: Bird orders phylogenetic tree (facing outside vs inside)."""
    hc = load_extdata("bird.orders")
    labels = hc.labels
    ct = cutree(hc, 6)
    n = len(labels)
    dend = color_branches(as_dendrogram(hc), k=6, col=list(range(1, 7)))
    dend_height = float(dend.height)

    fig = _common.new_figure(10.0, 5.2)
    ax1, ax2 = fig.subplots(1, 2)

    # Left: facing outside (labels outer, dendrogram inner)
    plt.sca(ax1)
    circos.par(cell_padding=(0.0, 0.0, 0.0, 0.0), points_overflow_warning=False)
    circos.initialize(["a"], xlim=(0.0, float(n)))
    circos.track(
        ylim=(0.0, 1.0),
        bg_border=None,
        track_height=0.3,
        panel_fun=lambda x, y: [
            circos.text(
                i + 0.5,
                0.0,
                labels[i],
                adj=(0.0, 0.5),
                facing="clockwise",
                nice_facing=True,
                col=ct[labels[i]],
                cex=0.55,
            )
            for i in range(n)
        ],
    )
    circos.track(
        ylim=(0.0, dend_height),
        bg_border=None,
        track_height=0.4,
        panel_fun=lambda x, y: circos.dendrogram(dend),
    )
    circos.clear()

    # Right: facing inside (dendrogram outer, labels inner)
    plt.sca(ax2)
    circos.par(cell_padding=(0.0, 0.0, 0.0, 0.0), points_overflow_warning=False)
    circos.initialize(["a"], xlim=(0.0, float(n)))
    circos.track(
        ylim=(0.0, dend_height),
        bg_border=None,
        track_height=0.4,
        panel_fun=lambda x, y: circos.dendrogram(dend, facing="inside"),
    )
    circos.track(
        ylim=(0.0, 1.0),
        bg_border=None,
        track_height=0.3,
        panel_fun=lambda x, y: [
            circos.text(
                i + 0.5,
                1.0,
                labels[i],
                adj=(1.0, 0.5),
                facing="clockwise",
                nice_facing=True,
                col=ct[labels[i]],
                cex=0.55,
            )
            for i in range(n)
        ],
    )
    circos.clear()
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.06)
    _common.save_fig(fig, "ch05_phylogenetic_tree.png")


def build_ch05_circular_heatmap() -> None:
    """Figure 5.4: Manually constructed multi-sector circular heatmaps + dendrograms."""
    rng = np.random.default_rng(123)
    mat = rng.normal(size=(100, 10))
    col_fun = color_ramp2([-2.0, 0.0, 2.0], ["green", "black", "red"])
    sectors = np.repeat(["a", "b"], [30, 70])
    mat_list = {
        "a": mat[sectors == "a", :],
        "b": mat[sectors == "b", :],
    }
    dend_list = {
        k: as_dendrogram(hclust_from_data(v))
        for k, v in mat_list.items()
    }

    fig = _common.new_figure(6.0, 6.0)
    circos.par(cell_padding=(0.0, 0.0, 0.0, 0.0), gap_degree=5)
    circos.initialize(["a", "b"], xlim=np.array([[0.0, 30.0], [0.0, 70.0]]))

    def panel_heatmap(x, y):
        si = CELL_META.sector_index
        m = mat_list[si]
        dend = dend_list[si]
        m2 = m[dend.leaf_indices(), :]
        col_mat = col_fun(m2)
        nr, nc = m2.shape
        xs_left = np.arange(nr, dtype=float)
        xs_right = xs_left + 1.0
        for i in range(nc):
            circos.rect(
                xs_left,
                np.repeat(float(nc - i - 1), nr),
                xs_right,
                np.repeat(float(nc - i), nr),
                border=col_mat[:, i],
                col=col_mat[:, i],
            )

    circos.track(ylim=(0.0, 10.0), bg_border=None, panel_fun=panel_heatmap)

    max_height = max(float(d.height) for d in dend_list.values())
    circos.track(
        ylim=(0.0, max_height),
        bg_border=None,
        track_height=0.3,
        panel_fun=lambda x, y: circos.dendrogram(
            dend_list[CELL_META.sector_index],
            max_height=max_height,
        ),
    )
    circos.clear()
    _common.save_fig(fig, "ch05_circular_heatmap.png")


def main() -> None:
    build_ch05_circular_barplot()
    build_ch05_circular_histograms()
    build_ch05_phylogenetic_tree()
    build_ch05_circular_heatmap()
    print("Generated 4 figures for Chapter 5.")


if __name__ == "__main__":
    main()
