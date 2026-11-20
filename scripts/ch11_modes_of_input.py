"""Generate figures for Chapter 11: Modes for circos.genomicTrack()."""

from __future__ import annotations

import numpy as np

from _common import new_figure, save_fig
from circlize_py import (
    CELL_META,
    circos,
    colorRamp2,
    generateRandomBed,
    get,
    getI,
    rand_color,
)


def _label_track(ax, letter: str) -> None:
    pos = get.cell.meta.data("yplot")
    ax.text(
        -0.015,
        float(np.mean(pos)),
        letter,
        ha="right",
        va="center",
        fontsize=10,
        clip_on=False,
    )


def fig_application_points() -> None:
    fig = new_figure(6.5, 6.5)
    ax = fig.add_subplot(111)
    circos.par(
        track_height=0.1,
        start_degree=90,
        canvas_xlim=(0.0, 1.0),
        canvas_ylim=(0.0, 1.0),
        gap_degree=270,
    )
    circos.initializeWithIdeogram(chromosome_index="chr1", plot_type=None, ax=ax)

    # Track A: normal mode, single numeric column
    bed = generateRandomBed(nr=300, seed=999)
    circos.genomicTrack(
        bed,
        panel_fun=lambda region, value, **kwargs: circos.genomicPoints(
            region, value, pch=16, cex=0.5, **kwargs
        ),
    )
    _label_track(ax, "A")

    # Track B: stack mode, single numeric column
    def panel_b(region, value, **kwargs):
        circos.genomicPoints(region, value, pch=16, cex=0.5, **kwargs)
        i = getI(**kwargs)
        circos.lines(CELL_META.cell_xlim, [i, i], lty=2, col="#00000040")

    circos.genomicTrack(bed, stack=True, panel_fun=panel_b)
    _label_track(ax, "B")

    # Track C: normal mode, list of two DataFrames
    bed1 = generateRandomBed(nr=300, seed=1001)
    bed2 = generateRandomBed(nr=300, seed=1002)
    bed_list = [bed1, bed2]

    def panel_c(region, value, **kwargs):
        i = getI(**kwargs)
        circos.genomicPoints(region, value, pch=16, cex=0.5, col=i, **kwargs)

    circos.genomicTrack(bed_list, panel_fun=panel_c)
    _label_track(ax, "C")

    # Track D: stack mode, list of two DataFrames
    def panel_d(region, value, **kwargs):
        i = getI(**kwargs)
        circos.genomicPoints(region, value, pch=16, cex=0.5, col=i, **kwargs)
        circos.lines(CELL_META.cell_xlim, [i, i], lty=2, col="#00000040")

    circos.genomicTrack(bed_list, stack=True, panel_fun=panel_d)
    _label_track(ax, "D")

    # Track E: normal mode, DataFrame with 4 numeric columns
    bed4 = generateRandomBed(nr=300, nc=4, seed=1003)
    circos.genomicTrack(
        bed4,
        panel_fun=lambda region, value, **kwargs: circos.genomicPoints(
            region, value, pch=16, cex=0.5, col=[1, 2, 3, 4], **kwargs
        ),
    )
    _label_track(ax, "E")

    # Track F: stack mode, DataFrame with 4 numeric columns
    def panel_f(region, value, **kwargs):
        i = getI(**kwargs)
        circos.genomicPoints(region, value, pch=16, cex=0.5, col=i, **kwargs)
        circos.lines(CELL_META.cell_xlim, [i, i], lty=2, col="#00000040")

    circos.genomicTrack(bed4, stack=True, panel_fun=panel_f)
    _label_track(ax, "F")

    circos.clear()
    save_fig(fig, "ch11_genomic_application_points.png")


def fig_application_lines() -> None:
    fig = new_figure(6.5, 6.5)
    ax = fig.add_subplot(111)
    circos.par(
        track_height=0.08,
        start_degree=90,
        canvas_xlim=(0.0, 1.0),
        canvas_ylim=(0.0, 1.0),
        gap_degree=270,
        cell_padding=(0.0, 0.0, 0.0, 0.0),
    )
    circos.initializeWithIdeogram(chromosome_index="chr1", plot_type=None, ax=ax)

    # Track A: simple lines
    bed = generateRandomBed(nr=500, seed=2001)
    circos.genomicTrack(
        bed,
        panel_fun=lambda region, value, **kwargs: circos.genomicLines(region, value, **kwargs),
    )
    _label_track(ax, "A")

    # Track B: area filled
    circos.genomicTrack(
        bed,
        panel_fun=lambda region, value, **kwargs: circos.genomicLines(region, value, area=True, **kwargs),
    )
    _label_track(ax, "B")

    # Track C: vertical histogram bars (type='h')
    circos.genomicTrack(
        bed,
        panel_fun=lambda region, value, **kwargs: circos.genomicLines(region, value, type="h", **kwargs),
    )
    _label_track(ax, "C")

    # Track D: list of two DataFrames
    bed1 = generateRandomBed(nr=500, seed=2002)
    bed2 = generateRandomBed(nr=500, seed=2003)
    bed_list = [bed1, bed2]
    circos.genomicTrack(
        bed_list,
        panel_fun=lambda region, value, **kwargs: circos.genomicLines(
            region, value, col=getI(**kwargs), **kwargs
        ),
    )
    _label_track(ax, "D")

    # Track E: list of two DataFrames under stack mode
    circos.genomicTrack(
        bed_list,
        stack=True,
        panel_fun=lambda region, value, **kwargs: circos.genomicLines(
            region, value, col=getI(**kwargs), **kwargs
        ),
    )
    _label_track(ax, "E")

    # Track F: 4 numeric columns under normal mode
    bed4 = generateRandomBed(nr=500, nc=4, seed=2004)
    circos.genomicTrack(
        bed4,
        panel_fun=lambda region, value, **kwargs: circos.genomicLines(
            region, value, col=[1, 2, 3, 4], **kwargs
        ),
    )
    _label_track(ax, "F")

    # Track G: 4 numeric columns under stack mode
    circos.genomicTrack(
        bed4,
        stack=True,
        panel_fun=lambda region, value, **kwargs: circos.genomicLines(
            region, value, col=getI(**kwargs), **kwargs
        ),
    )
    _label_track(ax, "G")

    # Track H: horizontal segments at y value with per-region colors
    bed_h = generateRandomBed(nr=200, seed=2005)

    def panel_h(region, value, **kwargs):
        cols = rand_color(len(region), seed=2006)
        for k in range(len(region)):
            circos.genomicLines(
                region.iloc[[k]],
                value.iloc[[k]],
                type="segment",
                lwd=2,
                col=cols[k],
                **kwargs,
            )

    circos.genomicTrack(bed_h, panel_fun=panel_h)
    _label_track(ax, "H")

    circos.clear()
    save_fig(fig, "ch11_genomic_application_lines.png")


def fig_application_rect() -> None:
    fig = new_figure(6.5, 6.5)
    ax = fig.add_subplot(111)
    circos.par(
        track_height=0.15,
        start_degree=90,
        canvas_xlim=(0.0, 1.0),
        canvas_ylim=(0.0, 1.0),
        gap_degree=270,
    )
    circos.initializeWithIdeogram(chromosome_index="chr1", plot_type=None, ax=ax)
    col_fun = colorRamp2(breaks=[-1.0, 0.0, 1.0], colors=["green", "black", "red"])

    # Track A: 4 numeric columns under stack mode (heatmap)
    bed4 = generateRandomBed(nr=100, nc=4, seed=3001)
    circos.genomicTrack(
        bed4,
        stack=True,
        panel_fun=lambda region, value, **kwargs: circos.genomicRect(
            region, value, col=col_fun(value.iloc[:, 0]), border=None, **kwargs
        ),
    )
    _label_track(ax, "A")

    # Track B: list of two DataFrames under stack mode
    bed1 = generateRandomBed(nr=100, seed=3002)
    bed2 = generateRandomBed(nr=100, seed=3003)
    bed_list = [bed1, bed2]

    def panel_rect_b(region, value, **kwargs):
        i = getI(**kwargs)
        circos.genomicRect(
            region,
            value,
            ytop=i + 0.3,
            ybottom=i - 0.3,
            col=col_fun(value.iloc[:, 0]),
            **kwargs,
        )

    circos.genomicTrack(bed_list, stack=True, panel_fun=panel_rect_b)
    _label_track(ax, "B")

    # Track C: list of two DataFrames under normal mode with explicit ylim
    circos.genomicTrack(bed_list, ylim=(0.5, 2.5), panel_fun=panel_rect_b)
    _label_track(ax, "C")

    # Track D: barplot-like rectangles with ybottom=0
    bed_d = generateRandomBed(nr=200, seed=3004)

    def panel_rect_d(region, value, **kwargs):
        cols = np.where(value.iloc[:, 0] > 0, "red", "green").tolist()
        circos.genomicRect(region, value, ytop_column=0, ybottom=0.0, col=cols, **kwargs)
        circos.lines(CELL_META.cell_xlim, [0.0, 0.0], lty=2, col="#00000040")

    circos.genomicTrack(bed_d, panel_fun=panel_rect_d)
    _label_track(ax, "D")

    circos.clear()
    save_fig(fig, "ch11_genomic_application_rect.png")


def main() -> None:
    fig_application_points()
    fig_application_lines()
    fig_application_rect()


if __name__ == "__main__":
    main()
