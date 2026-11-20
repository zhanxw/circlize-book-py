"""Generate all Chapter 17 figures: Make fun of the package."""

from __future__ import annotations

from datetime import datetime
import math
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import numpy as np

from _common import new_figure, save_fig
from circlize_py import (
    CELL_META,
    circos,
    draw,
    ensure_canvas,
    get_cell_meta_data,
    mm_y,
)


def make_clock() -> None:
    fig = new_figure(6.0, 6.0)
    ax = ensure_canvas(initialize=True)

    circos.par(gap_degree=0, cell_padding=(0, 0, 0, 0), start_degree=90)
    circos.initialize("a", xlim=(0, 12))
    circos.track(ylim=(0, 1), bg_border=None)
    circos.axis(
        major_at=np.arange(0, 13),
        labels=None,
        direction="inside",
        major_tick_length=mm_y(2),
    )
    circos.text(
        np.arange(1, 13),
        np.repeat(1.0, 12) - mm_y(6),
        [str(h) for h in range(1, 13)],
        facing="downward",
    )

    now = datetime.now()
    sec = now.second + (1 if now.microsecond > 0 else 0)
    minute = now.minute
    hour = now.hour % 12

    sec_rad = math.radians(90.0 - sec / 60.0 * 360.0)
    min_rad = math.radians(90.0 - minute / 60.0 * 360.0)
    hour_rad = math.radians(90.0 - hour / 12.0 * 360.0 - minute / 60.0 * 360.0 / 12.0)

    ax.annotate(
        "",
        xy=(math.cos(sec_rad) * 0.8, math.sin(sec_rad) * 0.8),
        xytext=(0.0, 0.0),
        arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0, mutation_scale=12),
    )
    ax.annotate(
        "",
        xy=(math.cos(min_rad) * 0.7, math.sin(min_rad) * 0.7),
        xytext=(0.0, 0.0),
        arrowprops=dict(arrowstyle="-|>", color="black", lw=2.0, mutation_scale=14),
    )
    ax.annotate(
        "",
        xy=(math.cos(hour_rad) * 0.4, math.sin(hour_rad) * 0.4),
        xytext=(0.0, 0.0),
        arrowprops=dict(arrowstyle="-|>", color="black", lw=2.2, mutation_scale=14),
    )
    save_fig(fig, "ch17_clock.png")


def make_dartboard() -> None:
    sectors = [str(i) for i in range(1, 21)]
    dart_labels = [13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10, 6]

    fig = new_figure(6.0, 6.0)
    circos.par(
        gap_degree=0,
        cell_padding=(0, 0, 0, 0),
        start_degree=360.0 / 20.0 / 2.0,
        track_margin=(0, 0),
        clock_wise=False,
    )
    circos.initialize(sectors, xlim=(0, 1))

    circos.track(ylim=(0, 1), sectors=sectors, bg_col="black", track_height=0.15)
    circos.track_text(
        x=np.repeat(0.5, 20),
        y=np.repeat(0.5, 20),
        labels=[str(v) for v in dart_labels],
        cex=0.85,
        sectors=sectors,
        col="#EEEEEE",
        font=2,
        facing="downward",
    )
    circos.track(
        ylim=(0, 1),
        sectors=sectors,
        bg_col=["#E41A1C", "#4DAF4A"] * 10,
        bg_border="#EEEEEE",
        track_height=0.05,
    )
    circos.track(
        ylim=(0, 1),
        sectors=sectors,
        bg_col=["black", "white"] * 10,
        bg_border="#EEEEEE",
        track_height=0.275,
    )
    circos.track(
        ylim=(0, 1),
        sectors=sectors,
        bg_col=["#E41A1C", "#4DAF4A"] * 10,
        bg_border="#EEEEEE",
        track_height=0.05,
    )
    circos.track(
        ylim=(0, 1),
        sectors=sectors,
        bg_col=["black", "white"] * 10,
        bg_border="#EEEEEE",
        track_height=0.375,
    )

    draw.sector(center=(0, 0), start_degree=0, end_degree=360, rou1=0.1, col="#4DAF4A", border="#EEEEEE")
    draw.sector(center=(0, 0), start_degree=0, end_degree=360, rou1=0.05, col="#E41A1C", border="#EEEEEE")
    save_fig(fig, "ch17_dartboard.png")


def make_bagua() -> None:
    sectors = [str(i) for i in range(1, 9)]

    def add_yang_yao() -> None:
        circos.rect(0, 0, 1, 1, col="black")

    def add_yin_yao() -> None:
        circos.rect(0, 0, 0.45, 1, col="black")
        circos.rect(0.55, 0, 1, 1, col="black")

    fig = new_figure(6.0, 6.0)
    circos.par(start_degree=22.5, gap_degree=6)
    circos.initialize(sectors, xlim=(0, 1))

    circos.track(
        ylim=(0, 1),
        sectors=sectors,
        bg_border=None,
        panel_fun=lambda x, y: add_yang_yao() if CELL_META.sector_numeric_index in {2, 5, 7, 8} else add_yin_yao(),
        track_height=0.1,
    )
    circos.track(
        ylim=(0, 1),
        sectors=sectors,
        bg_border=None,
        panel_fun=lambda x, y: add_yang_yao() if CELL_META.sector_numeric_index in {1, 6, 7, 8} else add_yin_yao(),
        track_height=0.1,
    )
    circos.track(
        ylim=(0, 1),
        sectors=sectors,
        bg_border=None,
        panel_fun=lambda x, y: add_yang_yao() if CELL_META.sector_numeric_index in {4, 5, 6, 7} else add_yin_yao(),
        track_height=0.1,
    )

    r = float(get_cell_meta_data("cell.bottom.radius")) - 0.1
    draw.sector(center=(0, 0), start_degree=90, end_degree=-90, rou1=r, col="black", border="black")
    draw.sector(center=(0, 0), start_degree=270, end_degree=90, rou1=r, col="white", border="black")
    draw.sector(center=(0, r / 2), start_degree=0, end_degree=360, rou1=r / 2, col="white", border="white")
    draw.sector(center=(0, -r / 2), start_degree=0, end_degree=360, rou1=r / 2, col="black", border="black")
    draw.sector(center=(0, r / 2), start_degree=0, end_degree=360, rou1=r / 8, col="black", border="black")
    draw.sector(center=(0, -r / 2), start_degree=0, end_degree=360, rou1=r / 8, col="white", border="white")
    save_fig(fig, "ch17_bagua.png")


def main() -> None:
    make_clock()
    make_dartboard()
    make_bagua()


if __name__ == "__main__":
    main()
