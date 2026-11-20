"""Generate figures for Chapter 12: High-level genomic functions."""

from __future__ import annotations

import string

import numpy as np
import pandas as pd

from _common import new_figure, save_fig
from circlize_py import (
    circos,
    colorRamp2,
    generateRandomBed,
    get,
    load_extdata,
    posTransform,
)


def fig_ideogram() -> None:
    fig = new_figure(6.5, 6.5)
    circos.initializeWithIdeogram(plot_type=("labels", "axis"))
    circos.track(ylim=(0.0, 1.0))
    circos.genomicIdeogram()
    circos.genomicIdeogram(track_height=0.2)
    circos.clear()
    save_fig(fig, "ch12_ideogram.png")


def fig_genomic_heatmap() -> None:
    bed = generateRandomBed(nr=100, nc=4, seed=401)
    col_fun = colorRamp2([-1.0, 0.0, 1.0], ["green", "black", "red"])

    fig = new_figure(10.5, 5.2)
    ax1 = fig.add_subplot(1, 2, 1)
    circos.initializeWithIdeogram(ax=ax1)
    circos.genomicHeatmap(bed, col=col_fun, side="inside", border="white")
    circos.clear()

    ax2 = fig.add_subplot(1, 2, 2)
    circos.initializeWithIdeogram(plot_type=None, ax=ax2)
    line_cols = (pd.Categorical(bed.iloc[:, 0]).codes + 1).tolist()
    circos.genomicHeatmap(bed, col=col_fun, side="outside", line_col=line_cols)
    circos.genomicIdeogram()
    circos.clear()
    save_fig(fig, "ch12_genomic_heatmap.png")


def fig_genomic_labels() -> None:
    rng = np.random.default_rng(402)
    bed = generateRandomBed(
        nr=50,
        fun=lambda k: rng.choice(list(string.ascii_lowercase), size=k, replace=True),
        seed=402,
    )
    bed.iloc[0, 3] = "aaaaa"

    fig = new_figure(10.5, 5.2)
    ax1 = fig.add_subplot(1, 2, 1)
    circos.initializeWithIdeogram(ax=ax1)
    circos.genomicLabels(bed, labels_column=3, side="inside")
    circos.clear()

    ax2 = fig.add_subplot(1, 2, 2)
    circos.initializeWithIdeogram(plot_type=None, ax=ax2)
    grp_cols = (pd.Categorical(bed.iloc[:, 0]).codes + 1).tolist()
    circos.genomicLabels(bed, labels_column=3, side="outside", col=grp_cols, line_col=grp_cols)
    circos.genomicIdeogram()
    circos.clear()
    save_fig(fig, "ch12_genomic_labels.png")


def fig_pos_transform() -> None:
    bed = generateRandomBed(nr=400, fun=lambda k: np.repeat("text", k), seed=123458)
    bed = bed.drop(bed.index[8:13]).reset_index(drop=True)

    fig = new_figure(9.0, 9.0)

    # Panel 1: posTransform.text, direction = 'outside'
    ax1 = fig.add_subplot(2, 2, 1)
    circos.par(
        start_degree=90,
        canvas_xlim=(0.0, 1.0),
        canvas_ylim=(0.0, 1.0),
        gap_degree=270,
        cell_padding=(0.0, 0.0, 0.0, 0.0),
        track_margin=(0.005, 0.005),
    )
    circos.initializeWithIdeogram(plot_type=("axis",), chromosome_index="chr1", ax=ax1)
    circos.genomicTrackPlotRegion(
        bed,
        ylim=(0.0, 1.0),
        panel_fun=lambda region, value, **kw: circos.genomicText(
            region,
            value,
            y=0.0,
            labels_column=0,
            facing="clockwise",
            adj=(0.0, 0.5),
            posTransform=posTransform.text,
            cex=0.8,
            niceFacing=False,
        ),
        track_height=0.1,
        bg_border=None,
    )
    i_track1 = get.cell.meta.data("track.index")
    circos.genomicPosTransformLines(
        bed,
        posTransform=lambda region, value: posTransform.text(
            region, y=0.0, labels=value.iloc[:, 0], cex=0.8, track_index=i_track1
        ),
        direction="outside",
    )
    circos.genomicTrackPlotRegion(
        bed,
        ylim=(0.0, 1.0),
        panel_fun=lambda region, value, **kw: circos.points(
            0.5 * (region.iloc[:, 0] + region.iloc[:, 1]),
            np.full(len(region), 0.5),
            pch=16,
        ),
        track_height=0.02,
        bg_border=None,
    )
    circos.clear()
    ax1.text(0.02, 0.05, "posTransform.text\ndirection = 'outside'", ha="left", va="bottom", fontsize=9)

    # Panel 2: posTransform.default, direction = 'outside'
    ax2 = fig.add_subplot(2, 2, 2)
    circos.par(
        start_degree=90,
        canvas_xlim=(0.0, 1.0),
        canvas_ylim=(0.0, 1.0),
        gap_degree=270,
        cell_padding=(0.0, 0.0, 0.0, 0.0),
        track_margin=(0.005, 0.005),
    )
    circos.initializeWithIdeogram(plot_type=("axis",), chromosome_index="chr1", ax=ax2)
    circos.genomicTrackPlotRegion(
        bed,
        ylim=(0.0, 1.0),
        panel_fun=lambda region, value, **kw: circos.genomicText(
            region,
            value,
            y=0.0,
            labels_column=0,
            facing="clockwise",
            adj=(0.0, 0.5),
            posTransform=posTransform.default,
            cex=0.8,
            niceFacing=False,
        ),
        track_height=0.1,
        bg_border=None,
    )
    circos.genomicPosTransformLines(bed, posTransform=posTransform.default, direction="outside")
    circos.genomicTrackPlotRegion(
        bed,
        ylim=(0.0, 1.0),
        panel_fun=lambda region, value, **kw: circos.points(
            0.5 * (region.iloc[:, 0] + region.iloc[:, 1]),
            np.full(len(region), 0.5),
            pch=16,
        ),
        track_height=0.02,
        bg_border=None,
    )
    circos.clear()
    ax2.text(0.02, 0.05, "posTransform.default\ndirection = 'outside'", ha="left", va="bottom", fontsize=9)

    # Panel 3: posTransform.text, direction = 'inside'
    ax3 = fig.add_subplot(2, 2, 3)
    circos.par(
        start_degree=90,
        canvas_xlim=(0.0, 1.0),
        canvas_ylim=(0.0, 1.0),
        gap_degree=270,
        cell_padding=(0.0, 0.0, 0.0, 0.0),
        track_margin=(0.005, 0.005),
    )
    circos.initializeWithIdeogram(plot_type=("axis",), chromosome_index="chr1", ax=ax3)
    circos.par(cell_padding=(0.0, 0.0, 0.0, 0.0))
    circos.genomicTrackPlotRegion(
        bed,
        ylim=(0.0, 1.0),
        panel_fun=lambda region, value, **kw: circos.points(
            0.5 * (region.iloc[:, 0] + region.iloc[:, 1]),
            np.full(len(region), 0.5),
            pch=16,
        ),
        track_height=0.02,
        bg_border=None,
    )
    circos.genomicTrackPlotRegion(bed, ylim=(0.0, 1.0), track_height=0.1, bg_border=None)
    i_track3 = get.cell.meta.data("track.index")
    circos.genomicTrackPlotRegion(
        bed,
        ylim=(0.0, 1.0),
        panel_fun=lambda region, value, **kw: circos.genomicText(
            region,
            value,
            y=1.0,
            labels_column=0,
            facing="clockwise",
            adj=(1.0, 0.5),
            posTransform=posTransform.text,
            cex=0.8,
            niceFacing=False,
        ),
        track_height=0.1,
        bg_border=None,
    )
    circos.genomicPosTransformLines(
        bed,
        posTransform=lambda region, value: posTransform.text(
            region, y=1.0, labels=value.iloc[:, 0], cex=0.8, track_index=i_track3 + 1
        ),
        direction="inside",
        track_index=i_track3,
    )
    circos.clear()
    ax3.text(0.02, 0.05, "posTransform.text\ndirection = 'inside'", ha="left", va="bottom", fontsize=9)

    # Panel 4: posTransform.text, direction = 'inside', padding = 0.2
    ax4 = fig.add_subplot(2, 2, 4)
    circos.par(
        start_degree=90,
        canvas_xlim=(0.0, 1.0),
        canvas_ylim=(0.0, 1.0),
        gap_degree=270,
        cell_padding=(0.0, 0.0, 0.0, 0.0),
        track_margin=(0.005, 0.005),
    )
    circos.initializeWithIdeogram(plot_type=("axis",), chromosome_index="chr1", ax=ax4)
    circos.par(cell_padding=(0.0, 0.0, 0.0, 0.0))
    circos.genomicTrackPlotRegion(
        bed,
        ylim=(0.0, 1.0),
        panel_fun=lambda region, value, **kw: circos.points(
            0.5 * (region.iloc[:, 0] + region.iloc[:, 1]),
            np.full(len(region), 0.5),
            pch=16,
        ),
        track_height=0.02,
        bg_border=None,
    )
    circos.genomicTrackPlotRegion(bed, ylim=(0.0, 1.0), track_height=0.1, bg_border=None)
    i_track4 = get.cell.meta.data("track.index")
    circos.genomicTrackPlotRegion(
        bed,
        ylim=(0.0, 1.0),
        panel_fun=lambda region, value, **kw: circos.genomicText(
            region,
            value,
            y=1.0,
            labels_column=0,
            facing="clockwise",
            adj=(1.0, 0.5),
            posTransform=posTransform.text,
            cex=0.8,
            niceFacing=False,
            padding=0.2,
        ),
        track_height=0.1,
        bg_border=None,
    )
    circos.genomicPosTransformLines(
        bed,
        posTransform=lambda region, value: posTransform.text(
            region, y=1.0, labels=value.iloc[:, 0], cex=0.8, track_index=i_track4 + 1, padding=0.2
        ),
        direction="inside",
        track_index=i_track4,
    )
    circos.clear()
    ax4.text(0.02, 0.05, "posTransform.text\ndirection = 'inside'\npadding = 0.2", ha="left", va="bottom", fontsize=9)

    save_fig(fig, "ch12_pos_transform.png")


def fig_genomic_axis() -> None:
    fig = new_figure(6.5, 6.5)
    circos.initializeWithIdeogram(plot_type=None)
    circos.genomicIdeogram()
    circos.track(
        track_index=get.current.track.index(),
        panel_fun=lambda x, y: circos.genomicAxis(h="top"),
    )
    circos.track(ylim=(0.0, 1.0), track_height=0.1)
    circos.track(
        track_index=get.current.track.index(),
        panel_fun=lambda x, y: circos.genomicAxis(h="bottom", direction="inside"),
    )
    circos.clear()
    save_fig(fig, "ch12_genomic_axis.png")


def fig_genomic_rainfall() -> None:
    dmr = load_extdata("DMR")
    DMR_hyper = dmr["DMR_hyper"]
    DMR_hypo = dmr["DMR_hypo"]

    fig = new_figure(6.5, 6.5)
    circos.initializeWithIdeogram(chromosome_index=[f"chr{i}" for i in range(1, 23)])
    circos.genomicRainfall(
        [DMR_hyper, DMR_hypo],
        pch=16,
        cex=0.4,
        col=["#FF000080", "#0000FF80"],
    )
    circos.genomicDensity(DMR_hyper, col="#FF000080", track_height=0.1)
    circos.genomicDensity(DMR_hypo, col="#0000FF80", track_height=0.1)
    circos.clear()
    save_fig(fig, "ch12_genomic_rainfall.png")


def fig_genomic_density_count() -> None:
    dmr = load_extdata("DMR")
    DMR_hyper = dmr["DMR_hyper"]

    fig = new_figure(6.5, 6.5)
    circos.initializeWithIdeogram(chromosome_index=[f"chr{i}" for i in range(1, 23)])
    circos.genomicDensity(DMR_hyper, col="#FF000080", track_height=0.1)
    circos.genomicDensity(DMR_hyper, col="#FF000080", count_by="number", track_height=0.1)
    circos.clear()
    save_fig(fig, "ch12_genomic_density_count.png")


def main() -> None:
    fig_ideogram()
    fig_genomic_heatmap()
    fig_genomic_labels()
    fig_pos_transform()
    fig_genomic_axis()
    fig_genomic_rainfall()
    fig_genomic_density_count()


if __name__ == "__main__":
    main()
