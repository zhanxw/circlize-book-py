"""Generate all figures for Chapter 4 (Legends)."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

import _common
from circlize import add_transparency, circos, color_ramp2


COL_FUN = color_ramp2([-2.0, 0.0, 2.0], ["green", "yellow", "red"])


def draw_example_circle(seed: int = 12345) -> None:
    """Render the two-track + links circular plot reused across Chapter 4."""
    rng = np.random.default_rng(seed)
    sectors = list("abcdefghij")
    circos.initialize(sectors, xlim=(0.0, 1.0))

    def panel_track1(x, y):
        circos.points(rng.uniform(size=20), rng.uniform(size=20), cex=0.5, pch=16, col=2)
        circos.points(rng.uniform(size=20), rng.uniform(size=20), cex=0.5, pch=16, col=3)

    circos.track(ylim=(0.0, 1.0), panel_fun=panel_track1)

    def panel_track2(x, y):
        circos.lines(np.sort(rng.uniform(size=20)), rng.uniform(size=20), col=4)
        circos.lines(np.sort(rng.uniform(size=20)), rng.uniform(size=20), col=5)

    circos.track(ylim=(0.0, 1.0), panel_fun=panel_track2)

    for _ in range(10):
        s1 = str(rng.choice(sectors))
        s2 = str(rng.choice(sectors))
        p1 = np.sort(rng.uniform(size=10))[:2]
        p2 = np.sort(rng.uniform(size=10))[:2]
        col = add_transparency(COL_FUN(float(rng.normal())), transparency=0.5)
        circos.link(s1, p1, s2, p2, col=col)

    circos.clear()


def build_ch04_directly_add() -> None:
    """Figure 4.1: Directly overlay vertical legends in the bottom-left corner."""
    fig = _common.new_figure(5.0, 5.0)
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.92])
    plt.sca(ax)
    draw_example_circle()

    _common.add_discrete_legend(
        fig,
        [("label1", 2), ("label2", 3)],
        kind="point",
        title="Track1",
        loc="lower left",
        bbox_to_anchor=(0.02, 0.43),
        fontsize=8.0,
        title_fontsize=8.5,
    )
    _common.add_discrete_legend(
        fig,
        [("label3", 4), ("label4", 5)],
        kind="line",
        title="Track2",
        loc="lower left",
        bbox_to_anchor=(0.02, 0.27),
        fontsize=8.0,
        title_fontsize=8.5,
    )
    _common.add_colorbar(
        fig,
        COL_FUN,
        vmin=-2.0,
        vmax=2.0,
        rect=[0.04, 0.04, 0.032, 0.19],
        title="Links",
        ticks=[-2, -1, 0, 1, 2],
        fontsize=8.0,
        title_fontsize=8.5,
    )
    _common.save_fig(fig, "ch04_directly_add.png")


def build_ch04_two_legends() -> None:
    """Figure 4.2: Split legends across bottom-left and bottom-right corners."""
    fig = _common.new_figure(6.2, 5.0)
    ax = fig.add_axes([0.06, 0.04, 0.88, 0.92])
    plt.sca(ax)
    draw_example_circle()

    _common.add_discrete_legend(
        fig,
        [("label1", 2), ("label2", 3)],
        kind="point",
        title="Track1",
        loc="lower left",
        bbox_to_anchor=(0.02, 0.19),
        fontsize=8.0,
        title_fontsize=8.5,
    )
    _common.add_discrete_legend(
        fig,
        [("label3", 4), ("label4", 5)],
        kind="line",
        title="Track2",
        loc="lower left",
        bbox_to_anchor=(0.02, 0.03),
        fontsize=8.0,
        title_fontsize=8.5,
    )
    _common.add_colorbar(
        fig,
        COL_FUN,
        vmin=-2.0,
        vmax=2.0,
        rect=[0.89, 0.05, 0.028, 0.22],
        title="Links",
        ticks=[-2, -1, 0, 1, 2],
        fontsize=8.0,
        title_fontsize=8.5,
    )
    _common.save_fig(fig, "ch04_two_legends.png")


def build_ch04_right_legend() -> None:
    """Figure 4.3: Dedicated right-side legend column via GridSpec."""
    fig = _common.new_figure(7.0, 5.2)
    gs = fig.add_gridspec(1, 2, width_ratios=[4.2, 1.2], left=0.02, right=0.96, top=0.97, bottom=0.03, wspace=0.04)

    ax_circ = fig.add_subplot(gs[0, 0])
    plt.sca(ax_circ)
    draw_example_circle()

    ax_leg = fig.add_subplot(gs[0, 1])
    ax_leg.set_axis_off()
    pos = ax_leg.get_position()

    _common.add_discrete_legend(
        fig,
        [("label1", 2), ("label2", 3)],
        kind="point",
        title="Track1",
        loc="upper left",
        bbox_to_anchor=(pos.x0, pos.y0 + 0.78 * pos.height),
        fontsize=8.5,
        title_fontsize=9.0,
    )
    _common.add_discrete_legend(
        fig,
        [("label3", 4), ("label4", 5)],
        kind="line",
        title="Track2",
        loc="upper left",
        bbox_to_anchor=(pos.x0, pos.y0 + 0.59 * pos.height),
        fontsize=8.5,
        title_fontsize=9.0,
    )
    _common.add_colorbar(
        fig,
        COL_FUN,
        vmin=-2.0,
        vmax=2.0,
        rect=[pos.x0 + 0.012, pos.y0 + 0.16 * pos.height, 0.025, 0.22 * pos.height],
        title="Links",
        ticks=[-2, -1, 0, 1, 2],
        fontsize=8.5,
        title_fontsize=9.0,
    )
    _common.save_fig(fig, "ch04_right_legend.png")


def build_ch04_bottom_legend() -> None:
    """Figure 4.4: Dedicated bottom horizontal legend layout via GridSpec."""
    fig = _common.new_figure(5.6, 6.4)
    gs = fig.add_gridspec(2, 1, height_ratios=[4.3, 1.0], left=0.03, right=0.97, top=0.98, bottom=0.04, hspace=0.03)

    ax_circ = fig.add_subplot(gs[0, 0])
    plt.sca(ax_circ)
    draw_example_circle()

    ax_leg = fig.add_subplot(gs[1, 0])
    ax_leg.set_axis_off()
    pos = ax_leg.get_position()

    _common.add_discrete_legend(
        fig,
        [("label1", 2), ("label2", 3)],
        kind="point",
        title="Track1",
        loc="center left",
        bbox_to_anchor=(pos.x0 + 0.02 * pos.width, pos.y0 + 0.50 * pos.height),
        ncol=2,
        fontsize=8.0,
        title_fontsize=8.5,
    )
    _common.add_discrete_legend(
        fig,
        [("label3", 4), ("label4", 5)],
        kind="line",
        title="Track2",
        loc="center left",
        bbox_to_anchor=(pos.x0 + 0.34 * pos.width, pos.y0 + 0.50 * pos.height),
        ncol=2,
        fontsize=8.0,
        title_fontsize=8.5,
    )
    _common.add_colorbar(
        fig,
        COL_FUN,
        vmin=-2.0,
        vmax=2.0,
        rect=[pos.x0 + 0.68 * pos.width, pos.y0 + 0.42 * pos.height, 0.28 * pos.width, 0.16 * pos.height],
        title="Links",
        ticks=[-2, -1, 0, 1, 2],
        orientation="horizontal",
        fontsize=8.0,
        title_fontsize=8.5,
    )
    _common.save_fig(fig, "ch04_bottom_legend.png")


def main() -> None:
    build_ch04_directly_add()
    build_ch04_two_legends()
    build_ch04_right_legend()
    build_ch04_bottom_legend()
    print("Generated 4 figures for Chapter 4.")


if __name__ == "__main__":
    main()
