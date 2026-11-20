"""Generate figures for Chapter 9: Initialize with genomic data."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from _common import new_figure, save_fig
from circlize_py import (
    CELL_META,
    circos,
    generateRandomBed,
    get,
    highlight,
    load_extdata,
    mm_h,
    mm_y,
    rand_color,
    read,
)


def fig_ideogram_default() -> None:
    fig = new_figure(6.5, 6.5)
    ax = fig.add_subplot(111)
    circos.initializeWithIdeogram(ax=ax)
    ax.text(0.0, 0.0, "default", ha="center", va="center", fontsize=11)
    circos.clear()
    save_fig(fig, "ch09_ideogram_default.png")


def fig_ideogram_subset() -> None:
    fig = new_figure(6.5, 6.5)
    ax = fig.add_subplot(111)
    circos.initializeWithIdeogram(chromosome_index=[f"chr{c}" for c in (3, 5, 2, 8)], ax=ax)
    ax.text(0.0, 0.0, "subset of chromosomes", ha="center", va="center", fontsize=10)
    circos.clear()
    save_fig(fig, "ch09_ideogram_subset.png")


def fig_ideogram_track() -> None:
    fig = new_figure(10.0, 5.0)
    ax1 = fig.add_subplot(1, 2, 1)
    circos.initializeWithIdeogram(plot_type=("axis", "labels"), ax=ax1)
    ax1.text(0.0, 0.0, "plot_type = ('axis', 'labels')", ha="center", va="center", fontsize=9.5)
    circos.clear()

    ax2 = fig.add_subplot(1, 2, 2)
    circos.initializeWithIdeogram(plot_type=None, ax=ax2)
    ax2.text(0.0, 0.0, "plot_type = None", ha="center", va="center", fontsize=9.5)
    circos.clear()
    save_fig(fig, "ch09_ideogram_track.png")


def fig_ideogram_par() -> None:
    fig = new_figure(10.0, 5.0)
    ax1 = fig.add_subplot(1, 2, 1)
    circos.par(start_degree=90)
    circos.initializeWithIdeogram(ax=ax1)
    circos.clear()
    ax1.text(0.0, 0.0, "start_degree = 90", ha="center", va="center", fontsize=9.5)

    ax2 = fig.add_subplot(1, 2, 2)
    circos.par(gap_degree=[2, 4] * 12)
    circos.initializeWithIdeogram(ax=ax2)
    circos.clear()
    ax2.text(0.0, 0.0, "gap_degree = [2, 4] * 12", ha="center", va="center", fontsize=9.5)
    save_fig(fig, "ch09_ideogram_par.png")


def fig_customize_chromosome() -> None:
    fig = new_figure(6.5, 6.5)
    np.random.seed(123)
    circos.initializeWithIdeogram(plot_type=None)

    def panel_chr(x, y):
        chr_name = CELL_META.sector_index
        xlim = CELL_META.xlim
        ylim = CELL_META.ylim
        circos.rect(xlim[0], 0.0, xlim[1], 1.0, col=rand_color(1)[0])
        circos.text(
            float(np.mean(xlim)),
            float(np.mean(ylim)),
            chr_name,
            cex=0.7,
            col="white",
            facing="inside",
            niceFacing=True,
        )

    circos.track(ylim=(0.0, 1.0), panel_fun=panel_chr, track_height=0.15, bg_border=None)
    circos.clear()
    save_fig(fig, "ch09_customize_chromosome.png")


def fig_gene_model() -> None:
    tp_family = load_extdata("tp_family_df")
    fig = new_figure(6.5, 6.5)
    circos.genomicInitialize(tp_family)
    circos.track(
        ylim=(0.0, 1.0),
        bg_col=["#FF000040", "#00FF0040", "#0000FF40"],
        bg_border=None,
        track_height=0.05,
    )
    n = int(tp_family.groupby("gene")["transcript"].nunique().max())

    def panel_tx(region, value, **kwargs):
        all_tx = list(dict.fromkeys(value["transcript"].tolist()))
        for i, tx in enumerate(all_tx, start=1):
            mask = (value["transcript"] == tx).to_numpy()
            sub = region.iloc[mask]
            current_tx_start = float(sub.iloc[:, 0].min())
            current_tx_end = float(sub.iloc[:, 1].max())
            y_pos = n - i + 1
            circos.lines([current_tx_start, current_tx_end], [y_pos, y_pos], col="#CCCCCC")
            circos.genomicRect(
                sub,
                ytop=y_pos + 0.4,
                ybottom=y_pos - 0.4,
                col="orange",
                border=None,
            )

    circos.genomicTrack(
        tp_family,
        ylim=(0.5, n + 0.5),
        panel_fun=panel_tx,
        bg_border=None,
        track_height=0.4,
    )
    circos.clear()
    save_fig(fig, "ch09_gene_model.png")


def _extend_chromosomes(bed: pd.DataFrame, chromosome: list[str], prefix: str = "zoom_") -> pd.DataFrame:
    zoom_bed = bed[bed.iloc[:, 0].isin(chromosome)].copy()
    zoom_bed.iloc[:, 0] = prefix + zoom_bed.iloc[:, 0].astype(str)
    return pd.concat([bed, zoom_bed], ignore_index=True)


def fig_zoom() -> None:
    cytoband = read.cytoband()
    cytoband_df = cytoband["df"]
    chromosome = cytoband["chromosome"]
    chr_len = cytoband["chr.len"]

    normal_lens = np.array([chr_len[c] for c in chromosome], dtype=float)
    zoom_lens = np.array([chr_len[c] for c in ("chr1", "chr2")], dtype=float)
    sector_width = np.concatenate([normal_lens / normal_lens.sum(), zoom_lens / zoom_lens.sum()])

    fig = new_figure(6.5, 6.5)
    circos.par(start_degree=90)
    circos.initializeWithIdeogram(
        _extend_chromosomes(cytoband_df, ["chr1", "chr2"]),
        sector_width=sector_width,
    )
    bed = generateRandomBed(nr=500, seed=999)
    circos.genomicTrack(
        _extend_chromosomes(bed, ["chr1", "chr2"]),
        panel_fun=lambda region, value, **kwargs: circos.genomicPoints(
            region, value, pch=16, cex=0.3, **kwargs
        ),
    )
    circos.link(
        "chr1",
        get.cell.meta.data("cell.xlim", sector_index="chr1"),
        "zoom_chr1",
        get.cell.meta.data("cell.xlim", sector_index="zoom_chr1"),
        col="#00000020",
        border=None,
    )
    circos.clear()
    save_fig(fig, "ch09_zoom.png")


def _build_combined_cytoband() -> tuple[pd.DataFrame, list[str]]:
    human_cytoband = read.cytoband(species="hg19")["df"].copy()
    mouse_cytoband = read.cytoband(species="mm10")["df"].copy()
    human_cytoband.iloc[:, 0] = "human_" + human_cytoband.iloc[:, 0].astype(str)
    mouse_cytoband.iloc[:, 0] = "mouse_" + mouse_cytoband.iloc[:, 0].astype(str)
    cytoband = pd.concat([human_cytoband, mouse_cytoband], ignore_index=True)
    chromosome_index = [f"human_chr{c}" for c in list(range(1, 23)) + ["X", "Y"]] + [
        f"mouse_chr{c}" for c in reversed(list(range(1, 20)) + ["X", "Y"])
    ]
    return cytoband, chromosome_index


def fig_combined_default() -> None:
    cytoband, chromosome_index = _build_combined_cytoband()
    fig = new_figure(6.8, 6.8)
    circos.initializeWithIdeogram(cytoband, chromosome_index=chromosome_index)
    circos.clear()
    save_fig(fig, "ch09_combined_default.png")


def fig_combined_improved() -> None:
    cytoband, chromosome_index = _build_combined_cytoband()
    fig = new_figure(6.8, 6.8)
    circos.par(gap_after=[1] * 23 + [5] + [1] * 20 + [5], points_overflow_warning=False)
    circos.initializeWithIdeogram(cytoband, plot_type=None, chromosome_index=chromosome_index)
    circos.track(
        ylim=(0.0, 1.0),
        panel_fun=lambda x, y: circos.text(
            CELL_META.xcenter,
            CELL_META.ylim[1] + mm_y(2),
            re.sub(r".*chr", "", CELL_META.sector_index),
            cex=0.6,
            niceFacing=True,
        ),
        track_height=mm_h(1),
        cell_padding=(0.0, 0.0, 0.0, 0.0),
        bg_border=None,
    )
    highlight.chromosome(
        [f"human_chr{c}" for c in list(range(1, 23)) + ["X", "Y"]],
        col="red",
        track_index=1,
    )
    highlight.chromosome(
        [f"mouse_chr{c}" for c in list(range(1, 20)) + ["X", "Y"]],
        col="blue",
        track_index=1,
    )
    circos.genomicIdeogram(cytoband)
    circos.clear()
    save_fig(fig, "ch09_combined_improved.png")


def _build_combined_chrom_info(chromosome_index: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    human_chromInfo = read.chromInfo(species="hg19")["df"].copy()
    mouse_chromInfo = read.chromInfo(species="mm10")["df"].copy()
    human_chromInfo.iloc[:, 0] = "human_" + human_chromInfo.iloc[:, 0].astype(str)
    mouse_chromInfo.iloc[:, 0] = "mouse_" + mouse_chromInfo.iloc[:, 0].astype(str)
    chromInfo = pd.concat([human_chromInfo, mouse_chromInfo], ignore_index=True)
    chromInfo["_ord"] = pd.Categorical(chromInfo.iloc[:, 0], categories=chromosome_index, ordered=True)
    chromInfo = chromInfo.sort_values("_ord").drop(columns=["_ord"]).reset_index(drop=True)
    return chromInfo, human_chromInfo, mouse_chromInfo


def fig_combined_genomic_initialize() -> None:
    _, chromosome_index = _build_combined_cytoband()
    chromInfo, _, _ = _build_combined_chrom_info(chromosome_index)

    fig = new_figure(6.8, 6.8)
    circos.par(gap_after=[1] * 23 + [5] + [1] * 20 + [5], points_overflow_warning=False)
    circos.genomicInitialize(chromInfo, plot_type=None)
    circos.track(
        ylim=(0.0, 1.0),
        panel_fun=lambda x, y: circos.text(
            CELL_META.xcenter,
            CELL_META.ylim[1] + mm_y(2),
            re.sub(r".*chr", "", CELL_META.sector_index),
            cex=0.6,
            niceFacing=True,
        ),
        track_height=mm_h(1),
        cell_padding=(0.0, 0.0, 0.0, 0.0),
        bg_border=None,
    )
    highlight.chromosome(
        [f"human_chr{c}" for c in list(range(1, 23)) + ["X", "Y"]],
        col="red",
        track_index=1,
    )
    highlight.chromosome(
        [f"mouse_chr{c}" for c in list(range(1, 20)) + ["X", "Y"]],
        col="blue",
        track_index=1,
    )
    circos.track(ylim=(0.0, 1.0))
    circos.clear()
    save_fig(fig, "ch09_combined_genomic_initialize.png")


def fig_combined_more_tracks() -> None:
    cytoband, chromosome_index = _build_combined_cytoband()
    chromInfo, human_chromInfo, mouse_chromInfo = _build_combined_chrom_info(chromosome_index)

    fig = new_figure(6.8, 6.8)
    ax = fig.add_subplot(111)
    circos.par(gap_after=[1] * 23 + [5] + [1] * 20 + [5], points_overflow_warning=False)
    circos.genomicInitialize(chromInfo, plot_type=None, ax=ax)
    circos.track(
        ylim=(0.0, 1.0),
        panel_fun=lambda x, y: circos.text(
            CELL_META.xcenter,
            CELL_META.ylim[1] + mm_y(2),
            re.sub(r".*chr", "", CELL_META.sector_index),
            cex=0.6,
            niceFacing=True,
        ),
        track_height=mm_h(1),
        cell_padding=(0.0, 0.0, 0.0, 0.0),
        bg_border=None,
    )
    highlight.chromosome(
        [f"human_chr{c}" for c in list(range(1, 23)) + ["X", "Y"]],
        col="red",
        track_index=1,
    )
    highlight.chromosome(
        [f"mouse_chr{c}" for c in list(range(1, 20)) + ["X", "Y"]],
        col="blue",
        track_index=1,
    )
    circos.genomicIdeogram(cytoband)

    human_df = generateRandomBed(200, species="hg19", seed=201)
    mouse_df = generateRandomBed(200, species="mm10", seed=202)
    human_df.iloc[:, 0] = "human_" + human_df.iloc[:, 0].astype(str)
    mouse_df.iloc[:, 0] = "mouse_" + mouse_df.iloc[:, 0].astype(str)
    df = pd.concat([human_df, mouse_df], ignore_index=True)
    np.random.seed(123)
    circos.genomicTrack(
        df,
        panel_fun=lambda region, value, **kwargs: circos.genomicPoints(
            region, value, col=rand_color(1)[0], cex=0.5, **kwargs
        ),
    )

    human_mid = pd.DataFrame(
        {
            "chr": [f"human_chr{i}" for i in range(1, 20)],
            "mid": np.round((human_chromInfo.iloc[:19, 1].to_numpy() + human_chromInfo.iloc[:19, 2].to_numpy()) / 2.0),
        }
    )
    mouse_mid = pd.DataFrame(
        {
            "chr": [f"mouse_chr{i}" for i in range(1, 20)],
            "mid": np.round((mouse_chromInfo.iloc[:19, 1].to_numpy() + mouse_chromInfo.iloc[:19, 2].to_numpy()) / 2.0),
        }
    )
    circos.genomicLink(human_mid, mouse_mid, col=rand_color(19, seed=303))
    circos.clear()
    ax.text(-0.9, -0.8, "Human\ngenome", ha="center", va="center", fontsize=10, clip_on=False)
    ax.text(0.9, 0.8, "Mouse\ngenome", ha="center", va="center", fontsize=10, clip_on=False)
    save_fig(fig, "ch09_combined_more_tracks.png")


def main() -> None:
    fig_ideogram_default()
    fig_ideogram_subset()
    fig_ideogram_track()
    fig_ideogram_par()
    fig_customize_chromosome()
    fig_gene_model()
    fig_zoom()
    fig_combined_default()
    fig_combined_improved()
    fig_combined_genomic_initialize()
    fig_combined_more_tracks()


if __name__ == "__main__":
    main()
