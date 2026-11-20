"""Generate all 28 figures for Chapter 6 (The circos.heatmap() function)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from scipy.cluster.vq import kmeans2
from scipy.stats import pearsonr

import _common
from circlize import (
    CELL_META,
    DendrogramNode,
    as_dendrogram,
    circos,
    color_branches,
    color_ramp2,
    convert_x,
    convert_y,
    get_cell_meta_data,
    get_current_track_index,
    hclust_from_data,
    rand_color,
)


def _make_base_data():
    """Create the 100x10 matrix and 5-group split from Chapter 6."""
    rng = np.random.default_rng(123)
    mat1 = np.vstack(
        [
            np.hstack([rng.normal(1.0, 1.0, (50, 5)), rng.normal(-1.0, 1.0, (50, 5))]),
            np.hstack([rng.normal(-1.0, 1.0, (50, 5)), rng.normal(1.0, 1.0, (50, 5))]),
        ]
    )
    perm = rng.permutation(100)
    mat1 = mat1[perm, :]
    df1 = pd.DataFrame(
        mat1,
        index=[f"R{i}" for i in range(1, 101)],
        columns=[f"C{i}" for i in range(1, 11)],
    )
    split_raw = rng.choice(list("abcde"), size=100, replace=True)
    split = pd.Categorical(split_raw, categories=list("abcde"), ordered=True)
    col_fun1 = color_ramp2([-2.0, 0.0, 2.0], ["blue", "white", "red"])
    return df1, split, col_fun1


def _dendsort_node(dend: DendrogramNode) -> DendrogramNode:
    """Custom recursive dendrogram sorter placing tighter subtrees first (like dendsort)."""
    root = dend.copy()

    def _sort(node: DendrogramNode) -> float:
        if node.leaf:
            return 0.0
        child_scores = [(_sort(c), c) for c in node.children]
        child_scores.sort(key=lambda pair: pair[0])
        node.children = [p[1] for p in child_scores]
        return float(node.height) if all(c.leaf for c in node.children) else min(s for s, _ in child_scores)

    _sort(root)
    root._recompute_stats()
    return root


def build_ch06_normal_heatmap() -> None:
    """Figure 6.1: Standard linear split heatmap corresponding to mat1 + split."""
    df1, split, col_fun1 = _make_base_data()
    cmap = _common.colorramp_to_cmap(col_fun1, -2.0, 2.0)

    col_hc = hclust_from_data(df1.to_numpy().T)
    col_od = as_dendrogram(col_hc).leaf_indices()

    levels = list(split.categories)
    counts = [int((split == lv).sum()) for lv in levels]

    fig = _common.new_figure(5.4, 6.2)
    gs = fig.add_gridspec(
        len(levels),
        2,
        width_ratios=[4.2, 0.6],
        height_ratios=counts,
        hspace=0.06,
        wspace=0.08,
        left=0.08,
        right=0.88,
        top=0.95,
        bottom=0.08,
    )

    for i, lv in enumerate(levels):
        ax = fig.add_subplot(gs[i, 0])
        sub = df1.iloc[np.asarray(split == lv), col_od]
        row_od = as_dendrogram(hclust_from_data(sub.to_numpy())).leaf_indices()
        sub = sub.iloc[row_od, :]
        ax.imshow(sub.to_numpy(), aspect="auto", cmap=cmap, vmin=-2.0, vmax=2.0, interpolation="nearest")
        ax.set_ylabel(lv, rotation=0, labelpad=10, va="center", fontsize=9, fontweight="bold")
        ax.set_yticks([])
        if i == len(levels) - 1:
            ax.set_xticks(range(len(col_od)))
            ax.set_xticklabels([df1.columns[j] for j in col_od], fontsize=8, rotation=45, ha="right")
        else:
            ax.set_xticks([])

    ax_cb = fig.add_subplot(gs[:, 1])
    ax_cb.set_axis_off()
    pos = ax_cb.get_position()
    _common.add_colorbar(
        fig,
        col_fun1,
        -2.0,
        2.0,
        rect=[pos.x0 + 0.01, pos.y0 + 0.30 * pos.height, 0.032, 0.35 * pos.height],
        title="mat1",
        ticks=[-2, -1, 0, 1, 2],
    )
    _common.save_fig(fig, "ch06_normal_heatmap.png")


def build_ch06_basic_split_and_nosplit() -> None:
    df1, split, col_fun1 = _make_base_data()

    # Figure 6.2: Split circular heatmap
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap(df1, split=split, col=col_fun1)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_split.png")

    # Figure 6.3: Unsplit circular heatmap
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap(df1, col=col_fun1)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_nosplit.png")


def build_ch06_layout_and_order() -> None:
    df1, split, col_fun1 = _make_base_data()

    # Figure 6.4: Control layout with circos.par + track styling + sector labels
    fig = _common.new_figure(6.2, 6.2)
    circos.par(start_degree=90, gap_degree=10, points_overflow_warning=False)
    circos.heatmap(
        df1,
        split=split,
        col=col_fun1,
        track_height=0.4,
        bg_border="green",
        bg_lwd=2.0,
        bg_lty=2,
        show_sector_labels=True,
    )
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_layout.png")

    # Figure 6.5: Control sector order via pd.Categorical
    fig = _common.new_figure(6.2, 6.2)
    circos.par(points_overflow_warning=False)
    split_rev = pd.Categorical(split.astype(str), categories=["e", "d", "c", "b", "a"], ordered=True)
    circos.heatmap(df1, split=split_rev, col=col_fun1, show_sector_labels=True)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_order.png")


def build_ch06_dend_and_rownames() -> None:
    df1, split, col_fun1 = _make_base_data()

    # Figure 6.6: dend_side inside vs outside
    fig = _common.new_figure(10.0, 5.0)
    ax1, ax2 = fig.subplots(1, 2)
    plt.sca(ax1)
    circos.heatmap(df1, split=split, col=col_fun1, dend_side="inside")
    circos.clear()
    ax1.text(0.0, 0.0, 'dend_side = "inside"', ha="center", va="center", fontsize=9)
    plt.sca(ax2)
    circos.heatmap(df1, split=split, col=col_fun1, dend_side="outside")
    circos.clear()
    ax2.text(0.0, 0.0, 'dend_side = "outside"', ha="center", va="center", fontsize=9)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.05)
    _common.save_fig(fig, "ch06_heatmap_dend_side.png")

    # Figure 6.7: rownames_side inside vs outside
    fig = _common.new_figure(10.0, 5.0)
    ax1, ax2 = fig.subplots(1, 2)
    plt.sca(ax1)
    circos.par(points_overflow_warning=False)
    circos.heatmap(df1, split=split, col=col_fun1, rownames_side="inside")
    circos.clear()
    ax1.text(0.0, 0.0, 'rownames_side = "inside"', ha="center", va="center", fontsize=9)
    plt.sca(ax2)
    circos.par(points_overflow_warning=False)
    circos.heatmap(df1, split=split, col=col_fun1, rownames_side="outside")
    circos.clear()
    ax2.text(0.0, 0.0, 'rownames_side = "outside"', ha="center", va="center", fontsize=9)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.08)
    _common.save_fig(fig, "ch06_heatmap_rownames_side.png")

    # Figure 6.8: both dend_side and rownames_side
    fig = _common.new_figure(10.0, 5.0)
    ax1, ax2 = fig.subplots(1, 2)
    plt.sca(ax1)
    circos.par(points_overflow_warning=False)
    circos.heatmap(df1, split=split, col=col_fun1, dend_side="inside", rownames_side="outside")
    circos.clear()
    plt.sca(ax2)
    circos.par(points_overflow_warning=False)
    circos.heatmap(df1, split=split, col=col_fun1, dend_side="outside", rownames_side="inside")
    circos.clear()
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.08)
    _common.save_fig(fig, "ch06_heatmap_dend_and_rownames.png")

    # Figure 6.9: graphic parameters for row names
    rng = np.random.default_rng(77)
    nr = len(df1)
    fig = _common.new_figure(6.4, 6.4)
    circos.par(points_overflow_warning=False)
    circos.heatmap(
        df1,
        split=split,
        col=col_fun1,
        rownames_side="outside",
        rownames_col=[(i % 10) + 1 for i in range(1, nr + 1)],
        rownames_cex=rng.uniform(0.3, 2.0, size=nr),
        rownames_font=[(i % 4) + 1 for i in range(1, nr + 1)],
    )
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_rownames_gp.png")


def build_ch06_clustering_and_callbacks() -> None:
    df1, split, col_fun1 = _make_base_data()

    # Figure 6.10: cluster=True vs cluster=False
    fig = _common.new_figure(10.0, 5.0)
    ax1, ax2 = fig.subplots(1, 2)
    plt.sca(ax1)
    circos.heatmap(df1, split=split, col=col_fun1, cluster=True)
    circos.clear()
    ax1.text(0.0, 0.0, "cluster = True", ha="center", va="center", fontsize=10)
    plt.sca(ax2)
    circos.heatmap(df1, split=split, col=col_fun1, cluster=False)
    circos.clear()
    ax2.text(0.0, 0.0, "cluster = False", ha="center", va="center", fontsize=10)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.05)
    _common.save_fig(fig, "ch06_heatmap_cluster.png")

    # Figure 6.11: default reorder_dendrogram vs custom dendsort node sorting
    fig = _common.new_figure(10.0, 5.0)
    ax1, ax2 = fig.subplots(1, 2)
    plt.sca(ax1)
    circos.heatmap(df1, split=split, col=col_fun1, dend_side="inside")
    circos.clear()
    ax1.text(0.0, 0.0, "reorder by row means", ha="center", va="center", fontsize=9)
    plt.sca(ax2)
    circos.heatmap(
        df1,
        split=split,
        col=col_fun1,
        dend_side="inside",
        dend_callback=lambda dend, m, si: _dendsort_node(dend),
    )
    circos.clear()
    ax2.text(0.0, 0.0, "reorder by custom node sort", ha="center", va="center", fontsize=9)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.05)
    _common.save_fig(fig, "ch06_heatmap_dend_reorder.png")

    # Figure 6.12: color_branches k=1 per split sector
    dend_col = {s: idx for idx, s in enumerate("abcde", start=1)}
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap(
        df1,
        split=split,
        col=col_fun1,
        dend_side="inside",
        dend_track_height=0.2,
        dend_callback=lambda dend, m, si: color_branches(dend, k=1, col=[dend_col[si]]),
    )
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_dend_col_split.png")

    # Figure 6.13: color_branches k=4 on unsplit heatmap
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap(
        df1,
        col=col_fun1,
        dend_side="inside",
        dend_track_height=0.2,
        dend_callback=lambda dend, m, si: color_branches(dend, k=4, col=[2, 3, 4, 5]),
    )
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_dend_col_unsplit.png")


def build_ch06_multi_track_heatmaps() -> None:
    df1, split, col_fun1 = _make_base_data()
    rng = np.random.default_rng(456)
    df2 = df1.iloc[rng.permutation(len(df1)), :].copy()
    col_fun2 = color_ramp2([-2.0, 0.0, 2.0], ["green", "white", "red"])

    # Figure 6.14: mat1 first (clusters & outer dend), then mat2
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap(df1, split=split, col=col_fun1, dend_side="outside")
    circos.heatmap(df2, col=col_fun2)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_multi1.png")

    # Figure 6.15: mat2 first (clusters & outer dend), then mat1
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap(df2, split=split, col=col_fun2, dend_side="outside")
    circos.heatmap(df1, col=col_fun1)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_multi2.png")

    # Figure 6.16: explicit circos.heatmap.initialize(df1) before mat2 then mat1
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap.initialize(df1, split=split)
    circos.heatmap(df2, col=col_fun2, dend_side="outside")
    circos.heatmap(df1, col=col_fun1)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_multi_init1.png")

    # Figure 6.17: initialize with full df1, draw halves on two tracks
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap.initialize(df1, split=split)
    circos.heatmap(df1.iloc[:, :5], col=col_fun1)
    circos.heatmap(df1.iloc[:, 5:], col=col_fun1)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_multi_init2.png")


def build_ch06_with_other_tracks_and_annotations() -> None:
    df1, split, col_fun1 = _make_base_data()
    mat1_arr = df1.to_numpy()
    row_mean = mat1_arr[:, :5].mean(axis=1)

    # Figure 6.18: heatmap + points track
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap(df1, split=split, col=col_fun1)

    def panel_points(x, y):
        y_vals = row_mean[CELL_META.subset][CELL_META.row_order]
        circos.lines(CELL_META.cell_xlim, [0.0, 0.0], lty=2, col="grey")
        cols = np.where(y_vals > 0.0, "red", "blue")
        circos.points(np.arange(len(y_vals)) + 0.5, y_vals, col=cols, pch=16, cex=0.5)

    circos.track(
        ylim=(float(row_mean.min()), float(row_mean.max())),
        panel_fun=panel_points,
        cell_padding=(0.02, 0.0, 0.02, 0.0),
    )
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_points.png")

    # Figure 6.19: points track first via circos.heatmap.initialize
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap.initialize(df1, split=split)
    circos.track(
        ylim=(float(row_mean.min()), float(row_mean.max())),
        panel_fun=panel_points,
        cell_padding=(0.02, 0.0, 0.02, 0.0),
    )
    circos.heatmap(df1, col=col_fun1)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_points_first.png")

    # Figure 6.20: heatmap + boxplot track
    fig = _common.new_figure(6.0, 6.0)
    circos.heatmap(df1, split=split, col=col_fun1)

    def panel_boxplot(x, y):
        m = mat1_arr[CELL_META.subset, :5][CELL_META.row_order, :]
        n_rows = m.shape[0]
        circos.boxplot(m.T, pos=np.arange(n_rows) + 0.5, pch=16, cex=0.3)
        circos.lines(CELL_META.cell_xlim, [0.0, 0.0], lty=2, col="grey")

    circos.track(
        ylim=(float(mat1_arr.min()), float(mat1_arr.max())),
        panel_fun=panel_boxplot,
        cell_padding=(0.02, 0.0, 0.02, 0.0),
    )
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_boxplot.png")

    # Figure 6.21: custom sector labels
    fig = _common.new_figure(6.2, 6.2)
    circos.par(points_overflow_warning=False)
    circos.heatmap(df1, split=split, col=col_fun1)

    def panel_sector_lbl(x, y):
        circos.text(
            CELL_META.xcenter,
            CELL_META.cell_ylim[1] + float(convert_y(2.0, "mm")),
            f"this is group {CELL_META.sector_index}",
            facing="bending.inside",
            cex=0.8,
            adj=(0.5, 0.0),
            nice_facing=True,
        )

    circos.track(track_index=get_current_track_index(), panel_fun=panel_sector_lbl, bg_border=None)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_sector_labels.png")

    # Figure 6.22: column names in wide gap after 5th sector
    fig = _common.new_figure(6.4, 6.4)
    circos.par(gap_after=[2, 2, 2, 2, 10], points_overflow_warning=False)
    circos.heatmap(df1, split=split, col=col_fun1, track_height=0.4)

    def panel_colnames(x, y):
        if CELL_META.sector_numeric_index == 5:
            cn = list(df1.columns)
            n_cn = len(cn)
            circos.text(
                np.repeat(CELL_META.cell_xlim[1], n_cn) + float(convert_x(1.0, "mm")),
                np.arange(n_cn) + 0.5,
                cn,
                cex=0.55,
                adj=(0.0, 0.5),
                facing="inside",
            )

    circos.track(track_index=get_current_track_index(), panel_fun=panel_colnames, bg_border=None)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_colnames.png")

    # Figure 6.23: column group annotations in gap after 5th sector
    fig = _common.new_figure(6.4, 6.4)
    circos.par(gap_after=[2, 2, 2, 2, 10], points_overflow_warning=False)
    circos.heatmap(df1, split=split, col=col_fun1, track_height=0.4)

    def panel_colgroup(x, y):
        if CELL_META.sector_numeric_index == 5:
            x1 = float(CELL_META.cell_xlim[1] + convert_x(1.0, "mm"))
            x2 = float(CELL_META.cell_xlim[1] + convert_x(5.0, "mm"))
            xm = float(CELL_META.cell_xlim[1] + convert_x(3.0, "mm"))
            circos.rect(x1, 0.0, x2, 5.0, col="orange", border=None)
            circos.text(xm, 2.5, "group 1", cex=0.55, facing="clockwise")
            circos.rect(x1, 5.0, x2, 10.0, col="pink", border=None)
            circos.text(xm, 7.5, "group 2", cex=0.55, facing="clockwise")

    circos.track(track_index=get_current_track_index(), panel_fun=panel_colgroup, bg_border=None)
    circos.clear()
    _common.save_fig(fig, "ch06_heatmap_colgroup.png")

    # Figure 6.24: simple circular heatmap with legend
    fig = _common.new_figure(7.0, 5.6)
    gs = fig.add_gridspec(1, 2, width_ratios=[4.8, 1.0], left=0.02, right=0.96, top=0.97, bottom=0.03, wspace=0.03)
    ax_circ = fig.add_subplot(gs[0, 0])
    plt.sca(ax_circ)
    circos.heatmap(df1, split=split, col=col_fun1)
    circos.clear()

    ax_leg = fig.add_subplot(gs[0, 1])
    ax_leg.set_axis_off()
    pos = ax_leg.get_position()
    _common.add_colorbar(
        fig,
        col_fun1,
        -2.0,
        2.0,
        rect=[pos.x0 + 0.01, pos.y0 + 0.35 * pos.height, 0.03, 0.30 * pos.height],
        title="mat1",
        ticks=[-2, -1, 0, 1, 2],
    )
    _common.save_fig(fig, "ch06_heatmap_legend.png")


def _generate_random_omics_data():
    """Port of jokergoo's random_matrices.R dataset (1000 DMRs x 20 samples)."""
    rng = np.random.default_rng(888)

    def rand_meth(k: int, mean: float) -> np.ndarray:
        return (rng.uniform(size=k) - 0.5) * min(1.0 - mean, mean) + mean

    mean_meth = np.concatenate([rand_meth(300, 0.3), rand_meth(700, 0.7)])
    rows_meth = []
    for m in mean_meth:
        if m < 0.3:
            rows_meth.append(np.concatenate([rand_meth(10, m), rand_meth(10, m + 0.2)]))
        elif m > 0.7:
            rows_meth.append(np.concatenate([rand_meth(10, m), rand_meth(10, m - 0.2)]))
        else:
            step = float(rng.choice([1.0, -1.0])) * 0.2
            rows_meth.append(np.concatenate([rand_meth(10, m), rand_meth(10, m + step)]))
    mat_meth = np.vstack(rows_meth)
    sample_cols = [f"sample{i}" for i in range(1, 21)]
    df_meth = pd.DataFrame(mat_meth, index=[f"DMR{i}" for i in range(1000)], columns=sample_cols)

    direction = np.where(mat_meth[:, :10].mean(axis=1) - mat_meth[:, 10:].mean(axis=1) > 0, "hyper", "hypo")

    rows_expr = []
    for row in mat_meth:
        sd_val = (float(rng.uniform()) - 0.5) * 0.4 + 0.5
        noisy = row + rng.normal(0.0, sd_val, size=len(row))
        rows_expr.append(-(noisy - noisy.mean()) / noisy.std(ddof=1))
    mat_expr = np.vstack(rows_expr)
    df_expr = pd.DataFrame(mat_expr, index=df_meth.index, columns=sample_cols)

    cor_pvalue = np.array(
        [-np.log10(max(pearsonr(mat_meth[i], mat_expr[i]).pvalue, 1e-300)) for i in range(len(mat_meth))]
    )

    gene_type = rng.choice(
        ["protein_coding", "lincRNA", "microRNA", "psedo-gene", "others"],
        size=len(mat_meth),
        replace=True,
        p=[0.6, 0.1, 0.1, 0.1, 0.1],
    )

    anno_gene = []
    for m in mean_meth:
        if m > 0.6 and rng.uniform() < 0.8:
            anno_gene.append("intragenic")
        elif m < 0.4 and rng.uniform() < 0.4:
            anno_gene.append("TSS")
        else:
            anno_gene.append("intergenic")
    anno_gene = np.array(anno_gene)

    dist = []
    for m in mean_meth:
        if m < 0.6 and rng.uniform() < 0.8:
            dist.append(round((float(rng.uniform()) - 0.5) * 1_000_000 + 500_000))
        elif m < 0.3 and rng.uniform() < 0.4:
            dist.append(round((float(rng.uniform()) - 0.5) * 1_000 + 500))
        else:
            dist.append(round((float(rng.uniform()) - 0.5) * 100_000 + 50_000))
    dist = np.array(dist, dtype=float)

    def rand_enhancer(m: float) -> float:
        if m < 0.4 and rng.uniform() < 0.6:
            return float(rng.uniform())
        if rng.uniform() < 0.1:
            return float(rng.uniform())
        return 0.0

    anno_enhancer = pd.DataFrame(
        {
            "enhancer_1": [rand_enhancer(m) for m in mean_meth],
            "enhancer_2": [rand_enhancer(m) for m in mean_meth],
            "enhancer_3": [rand_enhancer(m) for m in mean_meth],
        },
        index=df_meth.index,
    )

    _, km_labels = kmeans2(mat_meth, 5, minit="points", seed=123)
    km = pd.Categorical([f"cluster{c + 1}" for c in km_labels], categories=[f"cluster{i}" for i in range(1, 6)], ordered=True)

    df_link = pd.DataFrame(
        {
            "from_index": rng.integers(0, len(mat_meth), size=20),
            "to_index": rng.integers(0, len(mat_meth), size=20),
        }
    )

    return {
        "mat_meth": df_meth,
        "mat_expr": df_expr,
        "direction": direction,
        "cor_pvalue": cor_pvalue,
        "gene_type": gene_type,
        "anno_gene": anno_gene,
        "dist": dist,
        "anno_enhancer": anno_enhancer,
        "km": km,
        "df_link": df_link,
    }


def _omics_color_maps(data: dict):
    col_meth = color_ramp2([0.0, 0.5, 1.0], ["blue", "white", "red"])
    col_direction = {"hyper": "red", "hypo": "blue"}
    col_expr = color_ramp2([-2.0, 0.0, 2.0], ["green", "white", "red"])
    col_pvalue = color_ramp2([0.0, 2.0, 4.0], ["white", "white", "red"])
    set3 = ["#8DD3C7", "#FFFFB3", "#BEBADA", "#FB8072", "#80B1D3"]
    gt_levels = ["protein_coding", "lincRNA", "microRNA", "psedo-gene", "others"]
    col_gene_type = dict(zip(gt_levels, set3))
    set1 = ["#E41A1C", "#377EB8", "#4DAF4A"]
    ag_levels = ["intragenic", "TSS", "intergenic"]
    col_anno_gene = dict(zip(ag_levels, set1))
    col_dist = color_ramp2([0.0, 10000.0], ["black", "white"])
    col_enhancer = color_ramp2([0.0, 1.0], ["white", "orange"])
    return {
        "col_meth": col_meth,
        "col_direction": col_direction,
        "col_expr": col_expr,
        "col_pvalue": col_pvalue,
        "col_gene_type": col_gene_type,
        "col_anno_gene": col_anno_gene,
        "col_dist": col_dist,
        "col_enhancer": col_enhancer,
    }


def build_ch06_complex_examples() -> None:
    data = _generate_random_omics_data()
    cmaps = _omics_color_maps(data)

    # Figure 6.25: Linear layout reference preview (stacked multi-omics heatmaps)
    fig = _common.new_figure(9.0, 6.0)
    km = data["km"]
    clusters = list(km.categories)
    counts = [int((km == cl).sum()) for cl in clusters]
    col_widths = [3.6, 0.35, 3.6, 0.35, 0.35, 0.35, 0.35, 0.85]
    gs = fig.add_gridspec(
        len(clusters),
        len(col_widths),
        width_ratios=col_widths,
        height_ratios=counts,
        hspace=0.05,
        wspace=0.08,
        left=0.07,
        right=0.98,
        top=0.90,
        bottom=0.08,
    )

    cmap_meth = _common.colorramp_to_cmap(cmaps["col_meth"], 0.0, 1.0)
    cmap_expr = _common.colorramp_to_cmap(cmaps["col_expr"], -2.0, 2.0)
    cmap_pval = _common.colorramp_to_cmap(cmaps["col_pvalue"], 0.0, 4.0)
    cmap_dist = _common.colorramp_to_cmap(cmaps["col_dist"], 0.0, 10000.0)
    cmap_enh = _common.colorramp_to_cmap(cmaps["col_enhancer"], 0.0, 1.0)

    def _cat_to_rgb(vals, mapping):
        return np.array([mcolors.to_rgb(mapping[v]) for v in vals]).reshape(-1, 1, 3)

    headers = ["Methylation", "Dir", "Expression", "P-val", "Gene", "Anno", "Dist", "Enhancer"]
    for i, cl in enumerate(clusters):
        mask = np.asarray(km == cl)
        sub_meth = data["mat_meth"].to_numpy()[mask]
        od = as_dendrogram(hclust_from_data(sub_meth)).leaf_indices()

        panels = [
            (sub_meth[od], cmap_meth, 0.0, 1.0),
            (_cat_to_rgb(data["direction"][mask][od], cmaps["col_direction"]), None, None, None),
            (data["mat_expr"].to_numpy()[mask][od], cmap_expr, -2.0, 2.0),
            (data["cor_pvalue"][mask][od].reshape(-1, 1), cmap_pval, 0.0, 4.0),
            (_cat_to_rgb(data["gene_type"][mask][od], cmaps["col_gene_type"]), None, None, None),
            (_cat_to_rgb(data["anno_gene"][mask][od], cmaps["col_anno_gene"]), None, None, None),
            (data["dist"][mask][od].reshape(-1, 1), cmap_dist, 0.0, 10000.0),
            (data["anno_enhancer"].to_numpy()[mask][od], cmap_enh, 0.0, 1.0),
        ]
        for j, (arr, cm, vmin, vmax) in enumerate(panels):
            ax = fig.add_subplot(gs[i, j])
            if cm is None:
                ax.imshow(arr, aspect="auto", interpolation="nearest")
            else:
                ax.imshow(arr, aspect="auto", cmap=cm, vmin=vmin, vmax=vmax, interpolation="nearest")
            ax.set_xticks([])
            ax.set_yticks([])
            if j == 0:
                ax.set_ylabel(cl, rotation=0, labelpad=26, va="center", fontsize=8)
            if i == 0:
                ax.set_title(headers[j], fontsize=8.5, fontweight="bold", pad=6)

    _common.save_fig(fig, "ch06_complex_linear.png")

    def _draw_complex_circle(with_links: bool = False) -> None:
        circos.heatmap(data["mat_meth"], split=data["km"], col=cmaps["col_meth"], track_height=0.12)
        circos.heatmap(data["direction"], col=cmaps["col_direction"], track_height=0.01)
        circos.heatmap(data["mat_expr"], col=cmaps["col_expr"], track_height=0.12)
        circos.heatmap(data["cor_pvalue"], col=cmaps["col_pvalue"], track_height=0.01)
        circos.heatmap(data["gene_type"], col=cmaps["col_gene_type"], track_height=0.01)
        circos.heatmap(data["anno_gene"], col=cmaps["col_anno_gene"], track_height=0.01)
        circos.heatmap(data["dist"], col=cmaps["col_dist"], track_height=0.01)
        circos.heatmap(data["anno_enhancer"], col=cmaps["col_enhancer"], track_height=0.03)
        if with_links:
            link_cols = rand_color(len(data["df_link"]), seed=99)
            for idx, row in data["df_link"].iterrows():
                circos.heatmap.link(int(row["from_index"]), int(row["to_index"]), col=link_cols[idx])
        circos.clear()

    # Figure 6.26: Multi-omics 8-track circular heatmap (no links)
    fig = _common.new_figure(6.4, 6.4)
    _draw_complex_circle(with_links=False)
    _common.save_fig(fig, "ch06_complex_no_links.png")

    # Figure 6.27: Multi-omics 8-track circular heatmap with 20 DMR links
    fig = _common.new_figure(6.4, 6.4)
    _draw_complex_circle(with_links=True)
    _common.save_fig(fig, "ch06_complex_with_links.png")

    # Figure 6.28: Complete multi-omics circular heatmap + links + all 8 legends
    fig = _common.new_figure(9.6, 6.2)
    gs = fig.add_gridspec(1, 2, width_ratios=[5.8, 3.3], left=0.01, right=0.98, top=0.98, bottom=0.02, wspace=0.02)
    ax_circ = fig.add_subplot(gs[0, 0])
    plt.sca(ax_circ)
    _draw_complex_circle(with_links=True)

    ax_leg = fig.add_subplot(gs[0, 1])
    ax_leg.set_axis_off()
    pos = ax_leg.get_position()

    # Column 1 inside right legend box
    c1_x = pos.x0 + 0.02 * pos.width
    _common.add_colorbar(
        fig,
        cmaps["col_meth"],
        0.0,
        1.0,
        rect=[c1_x, pos.y0 + 0.72 * pos.height, 0.022, 0.20 * pos.height],
        title="Methylation",
        ticks=[0.0, 0.25, 0.5, 0.75, 1.0],
        fontsize=7.5,
        title_fontsize=8.0,
    )
    _common.add_discrete_legend(
        fig,
        list(cmaps["col_direction"].items()),
        kind="patch",
        title="Direction",
        loc="upper left",
        bbox_to_anchor=(c1_x - 0.01, pos.y0 + 0.67 * pos.height),
        fontsize=7.5,
        title_fontsize=8.0,
    )
    _common.add_colorbar(
        fig,
        cmaps["col_expr"],
        -2.0,
        2.0,
        rect=[c1_x, pos.y0 + 0.34 * pos.height, 0.022, 0.20 * pos.height],
        title="Expression",
        ticks=[-2, -1, 0, 1, 2],
        fontsize=7.5,
        title_fontsize=8.0,
    )
    cb_pval = _common.add_colorbar(
        fig,
        cmaps["col_pvalue"],
        0.0,
        4.0,
        rect=[c1_x, pos.y0 + 0.05 * pos.height, 0.022, 0.20 * pos.height],
        title="P-value",
        ticks=[0.0, 2.0, 4.0],
        fontsize=7.5,
        title_fontsize=8.0,
    )
    cb_pval.set_ticklabels(["1", "0.01", "0.0001"])

    # Column 2 inside right legend box
    c2_x = pos.x0 + 0.50 * pos.width
    _common.add_discrete_legend(
        fig,
        list(cmaps["col_gene_type"].items()),
        kind="patch",
        title="Gene type",
        loc="upper left",
        bbox_to_anchor=(c2_x - 0.01, pos.y0 + 0.96 * pos.height),
        fontsize=7.5,
        title_fontsize=8.0,
    )
    _common.add_discrete_legend(
        fig,
        list(cmaps["col_anno_gene"].items()),
        kind="patch",
        title="Gene anno",
        loc="upper left",
        bbox_to_anchor=(c2_x - 0.01, pos.y0 + 0.71 * pos.height),
        fontsize=7.5,
        title_fontsize=8.0,
    )
    cb_dist = _common.add_colorbar(
        fig,
        cmaps["col_dist"],
        0.0,
        10000.0,
        rect=[c2_x, pos.y0 + 0.34 * pos.height, 0.022, 0.20 * pos.height],
        title="Dist to TSS",
        ticks=[0.0, 5000.0, 10000.0],
        fontsize=7.5,
        title_fontsize=8.0,
    )
    cb_dist.set_ticklabels(["0kb", "5kb", "10kb"])
    cb_enh = _common.add_colorbar(
        fig,
        cmaps["col_enhancer"],
        0.0,
        1.0,
        rect=[c2_x, pos.y0 + 0.05 * pos.height, 0.022, 0.20 * pos.height],
        title="Enhancer overlap",
        ticks=[0.0, 0.25, 0.5, 0.75, 1.0],
        fontsize=7.5,
        title_fontsize=8.0,
    )
    cb_enh.set_ticklabels(["0%", "25%", "50%", "75%", "100%"])

    _common.save_fig(fig, "ch06_complex_with_legends.png")


def main() -> None:
    build_ch06_normal_heatmap()
    build_ch06_basic_split_and_nosplit()
    build_ch06_layout_and_order()
    build_ch06_dend_and_rownames()
    build_ch06_clustering_and_callbacks()
    build_ch06_multi_track_heatmaps()
    build_ch06_with_other_tracks_and_annotations()
    build_ch06_complex_examples()
    print("Generated 28 figures for Chapter 6.")


if __name__ == "__main__":
    main()
