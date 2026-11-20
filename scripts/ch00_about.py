"""Generate cover artwork for Chapter 0 (About)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matplotlib.patches import Rectangle
from circlize_py import CELL_META, circos, load_extdata

import _common


def make_cover() -> Path:
    """Create the book cover artwork featuring the circular Keith Haring doodle."""
    imgs = load_extdata("doodle")
    fig = _common.new_figure(width=7.5, height=9.0, dpi=150)

    # Title at top, footer at bottom, circular doodle centered inside a crisp frame
    ax = fig.add_axes([0.11, 0.16, 0.78, 0.66])
    ax.set_aspect("equal", adjustable="box")

    circos.par(
        cell_padding=[0.0, 0.0, 0.0, 0.0],
        gap_degree=2.0,
        track_margin=[0.015, 0.015],
        canvas_xlim=[-1.12, 1.12],
        canvas_ylim=[-1.12, 1.12],
        points_overflow_warning=False,
    )
    sectors = list("abcdefghijklmnop")
    circos.initialize(sectors, xlim=[0.0, 1.0], ax=ax)

    def _draw_outer(x, y):
        idx = CELL_META.sector_numeric_index - 1
        circos.raster(
            imgs[idx],
            CELL_META.xcenter,
            CELL_META.ycenter,
            width=CELL_META.xrange,
            height=CELL_META.yrange,
            facing="bending.inside",
            scaling=0.5,
        )

    def _draw_inner(x, y):
        idx = CELL_META.sector_numeric_index + 15
        circos.raster(
            imgs[idx],
            CELL_META.xcenter,
            CELL_META.ycenter,
            width=CELL_META.xrange,
            height=CELL_META.yrange,
            facing="bending.inside",
            scaling=0.5,
        )

    circos.track(ylim=[0.0, 1.0], track_height=0.25, bg_border=None, panel_fun=_draw_outer)
    circos.track(ylim=[0.0, 1.0], track_height=0.25, bg_border=None, panel_fun=_draw_inner)

    frame = Rectangle((-1.08, -1.08), 2.16, 2.16, fill=False, edgecolor="#111111", linewidth=2.2)
    ax.add_patch(frame)
    circos.clear()

    fig.text(
        0.5,
        0.90,
        "CIRCULAR VISUALIZATION\nIN PYTHON",
        ha="center",
        va="center",
        fontsize=22,
        fontweight="bold",
        color="#111111",
        linespacing=1.25,
    )
    fig.text(
        0.5,
        0.825,
        "circlize-py Edition",
        ha="center",
        va="center",
        fontsize=12.5,
        color="#444444",
    )
    fig.text(
        0.5,
        0.095,
        "Ported from Zuguang Gu's circlize",
        ha="center",
        va="center",
        fontsize=13,
        fontweight="normal",
        color="#222222",
    )

    return _common.save_fig(fig, "ch00_cover.png", dpi=150, tight=True, pad_inches=0.25)


def main() -> None:
    out = make_cover()
    print(f"Generated {out}")


if __name__ == "__main__":
    main()
