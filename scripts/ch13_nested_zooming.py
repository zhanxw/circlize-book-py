"""Generate figures for Chapter 13: Nested zooming."""

from __future__ import annotations

import numpy as np
import pandas as pd

from _common import new_figure, save_fig
from circlize_py import (
    CELL_META,
    add_transparency,
    circos,
    get,
    load_extdata,
    mm_h,
    mm_y,
    rand_color,
)


def _prepare_nested_toy_data():
    rng = np.random.default_rng(123)
    letters8 = list("abcdefgh")
    df = pd.DataFrame(
        {
            "cate": rng.choice(letters8, size=400, replace=True),
            "x": rng.uniform(0.0, 1.0, size=400),
            "y": rng.uniform(0.0, 1.0, size=400),
        }
    )
    df = df.sort_values(["cate", "x"]).reset_index(drop=True)
    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    cuts = pd.cut(df["x"], bins=bins, include_lowest=False)
    df["start"] = cuts.apply(lambda iv: float(iv.left)).astype(float)
    df["end"] = cuts.apply(lambda iv: float(iv.right)).astype(float)
    df["interval_x"] = [f"({s:g},{e:g}]" for s, e in zip(df["start"], df["end"])]
    df["name"] = df["cate"] + ":" + df["interval_x"]

    unique_names = df["name"].unique()
    chosen = set(rng.choice(unique_names, size=20, replace=False))
    df2 = df[df["name"].isin(chosen)].copy()

    correspondance = df2[["cate", "start", "end", "name"]].copy()
    correspondance["start_2"] = df2["start"].to_numpy()
    correspondance["end_2"] = df2["end"].to_numpy()
    correspondance = correspondance.drop_duplicates().reset_index(drop=True)

    zoom_sector = df2[["name", "start", "end", "cate"]].drop_duplicates().reset_index(drop=True)
    zoom_data = df2[["name", "x", "y"]].reset_index(drop=True)
    data = df[["cate", "x", "y"]].copy()
    sector = pd.DataFrame({"cate": letters8, "start": 0.0, "end": 1.0})
    return sector, data, zoom_sector, zoom_data, correspondance


def fig_nested_normal_and_outside() -> None:
    sector, data, zoom_sector, zoom_data, correspondance = _prepare_nested_toy_data()

    def f1():
        circos.par(gap_degree=10, points_overflow_warning=False)
        circos.initialize(sector.iloc[:, 0], xlim=sector.iloc[:, 1:3])
        circos.track(
            data.iloc[:, 0],
            x=data.iloc[:, 1],
            y=data.iloc[:, 2],
            ylim=(0.0, 1.0),
            panel_fun=lambda x, y: circos.points(x, y, pch=16, cex=0.5, col="red"),
        )

    def f2():
        circos.par(gap_degree=2, cell_padding=(0.0, 0.0, 0.0, 0.0))
        circos.initialize(zoom_sector.iloc[:, 0], xlim=zoom_sector.iloc[:, 1:3].to_numpy())
        circos.track(
            zoom_data.iloc[:, 0],
            x=zoom_data.iloc[:, 1],
            y=zoom_data.iloc[:, 2],
            panel_fun=lambda x, y: circos.points(x, y, pch=16, cex=0.5),
        )

    fig1 = new_figure(6.5, 6.5)
    circos.nested(f1, f2, correspondance)
    save_fig(fig1, "ch13_nested_normal.png")

    fig2 = new_figure(6.5, 6.5)
    circos.nested(f2, f1, correspondance.iloc[:, [3, 4, 5, 0, 1, 2]])
    save_fig(fig2, "ch13_nested_outside.png")


def fig_nested_complex() -> None:
    sector, data, zoom_sector, zoom_data, correspondance = _prepare_nested_toy_data()
    letters8 = list("abcdefgh")
    sector_col = dict(zip(letters8, rand_color(8, transparency=0.5, seed=123)))

    def f1():
        circos.par(gap_degree=10, points_overflow_warning=False)
        circos.initialize(sector.iloc[:, 0], xlim=sector.iloc[:, 1:3])

        def panel_f1(x, y):
            si = CELL_META.sector_index
            sub_corr = correspondance[correspondance.iloc[:, 0] == si]
            for _, row in sub_corr.iterrows():
                circos.rect(
                    float(row.iloc[1]),
                    CELL_META.cell_ylim[0],
                    float(row.iloc[2]),
                    CELL_META.cell_ylim[1],
                    col=sector_col[si],
                    border=sector_col[si],
                )
            circos.points(x, y, pch=16, cex=0.5)
            circos.text(
                CELL_META.xcenter,
                CELL_META.ylim[1] + mm_y(2),
                si,
                niceFacing=True,
                adj=(0.5, 0.0),
            )

        circos.track(
            data.iloc[:, 0],
            x=data.iloc[:, 1],
            y=data.iloc[:, 2],
            ylim=(0.0, 1.0),
            panel_fun=panel_f1,
        )

    def f2():
        circos.par(gap_degree=2, cell_padding=(0.0, 0.0, 0.0, 0.0))
        circos.initialize(zoom_sector.iloc[:, 0], xlim=zoom_sector.iloc[:, 1:3].to_numpy())
        circos.track(
            zoom_data.iloc[:, 0],
            x=zoom_data.iloc[:, 1],
            y=zoom_data.iloc[:, 2],
            panel_fun=lambda x, y: circos.points(x, y, pch=16, cex=0.5),
            bg_col=[sector_col[c] for c in zoom_sector["cate"]],
            track_margin=(0.0, 0.0),
        )

    fig = new_figure(6.5, 6.5)
    circos.nested(
        f1,
        f2,
        correspondance,
        connection_col=[sector_col[c] for c in correspondance.iloc[:, 0]],
    )
    save_fig(fig, "ch13_nested_complex.png")


def fig_dmr() -> None:
    wb = load_extdata("tagments_WGBS_DMR")
    tagments = wb["tagments"]
    DMR1 = wb["DMR1"]
    correspondance = wb["correspondance"]

    chrs_22 = [f"chr{i}" for i in range(1, 23)]
    chr_bg_color = dict(zip(chrs_22, rand_color(22, transparency=0.8, seed=77)))

    def f1():
        circos.par(gap_after=2, start_degree=90)
        circos.initializeWithIdeogram(
            chromosome_index=chrs_22,
            plot_type=("ideogram", "labels"),
            ideogram_height=0.03,
        )

    def f2():
        circos.par(
            cell_padding=(0.0, 0.0, 0.0, 0.0),
            gap_after=[1] * (len(tagments) - 1) + [10],
        )
        circos.genomicInitialize(tagments, plot_type=None)
        bg_cols = [chr_bg_color[c] for c in tagments["chr"]]

        def panel_dmr(region, value, **kwargs):
            for h in np.arange(-0.6, 0.61, 0.2):
                circos.lines(CELL_META.cell_xlim, [h, h], lty=3, col="#AAAAAA")
            circos.lines(CELL_META.cell_xlim, [0.0, 0.0], lty=3, col="#888888")
            cols = np.where(value.iloc[:, 0] > 0, "#E41A1C", "#377EB8").tolist()
            circos.genomicPoints(region, value, col=cols, pch=16, cex=0.5)

        circos.genomicTrack(
            DMR1,
            ylim=(-0.6, 0.6),
            panel_fun=panel_dmr,
            bg_col=bg_cols,
            track_margin=(0.02, 0.0),
        )
        circos.yaxis(
            side="left",
            at=np.arange(-0.6, 0.61, 0.3),
            sector_index=get.all.sector.index()[0],
            labels_cex=0.4,
        )
        circos.track(
            ylim=(0.0, 1.0),
            track_height=mm_h(2),
            bg_col=add_transparency(bg_cols, 0.0),
        )

    fig = new_figure(6.8, 6.8)
    circos.nested(
        f1,
        f2,
        correspondance,
        connection_col=[chr_bg_color[c] for c in correspondance.iloc[:, 0]],
    )
    save_fig(fig, "ch13_dmr.png")


def main() -> None:
    fig_nested_normal_and_outside()
    fig_nested_complex()
    fig_dmr()


if __name__ == "__main__":
    main()
