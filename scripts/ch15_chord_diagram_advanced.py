"""Generate all Chapter 15 figures: Advanced usage of chordDiagram()."""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import new_figure, save_fig
from circlize_py import (
    CELL_META,
    calc_gap,
    chord_diagram,
    circos,
    ensure_canvas,
    get_all_sector_index,
    get_cell_meta_data,
    highlight,
    mm_h,
    strwidth_canvas,
)


def _make_base_mat() -> tuple[pd.DataFrame, dict[str, str]]:
    rng = np.random.default_rng(999)
    arr = rng.permutation(np.arange(1, 19)).reshape((3, 6), order="F")
    mat = pd.DataFrame(arr, index=[f"S{i}" for i in range(1, 4)], columns=[f"E{i}" for i in range(1, 7)])
    grid_col = {
        "S1": "red",
        "S2": "green",
        "S3": "blue",
        "E1": "grey",
        "E2": "grey",
        "E3": "grey",
        "E4": "grey",
        "E5": "grey",
        "E6": "grey",
    }
    return mat, grid_col


def _make_grouped_matrix() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, int]]:
    rng = np.random.default_rng(321)
    mat1 = pd.DataFrame(rng.normal(size=(5, 5)), index=[f"A{i}" for i in range(1, 6)], columns=[f"B{i}" for i in range(1, 6)])
    mat2 = pd.DataFrame(rng.normal(size=(5, 5)), index=[f"A{i}" for i in range(1, 6)], columns=[f"C{i}" for i in range(1, 6)])
    mat3 = pd.DataFrame(rng.normal(size=(5, 5)), index=[f"B{i}" for i in range(1, 6)], columns=[f"C{i}" for i in range(1, 6)])

    mat = pd.DataFrame(
        0.0,
        index=list(mat2.index) + list(mat3.index),
        columns=list(mat1.columns) + list(mat2.columns),
    )
    mat.loc[mat1.index, mat1.columns] = mat1
    mat.loc[mat2.index, mat2.columns] = mat2
    mat.loc[mat3.index, mat3.columns] = mat3

    grid_col = {}
    for i in range(1, 6):
        grid_col[f"A{i}"] = 2
        grid_col[f"B{i}"] = 3
        grid_col[f"C{i}"] = 4
    return mat, mat1, mat2, mat3, grid_col


def main() -> None:
    mat, grid_col = _make_base_mat()

    # Print circos.info() examples for the book text
    fig_tmp = new_figure(4.0, 4.0)
    chord_diagram(mat)
    buf1 = io.StringIO()
    with redirect_stdout(buf1):
        circos.info()
    print("=== Default chordDiagram circos.info() ===")
    print(buf1.getvalue().strip())
    circos.clear()
    plt.close(fig_tmp)

    fig_tmp2 = new_figure(4.0, 4.0)
    chord_diagram(mat, pre_allocate_tracks=2)
    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        circos.info()
    print("=== pre_allocate_tracks=2 circos.info() ===")
    print(buf2.getvalue().strip())
    circos.clear()
    plt.close(fig_tmp2)

    # 1. Track organization (1x3)
    fig = new_figure(10.5, 3.6)
    ax1, ax2, ax3 = fig.subplots(1, 3)
    fig.subplots_adjust(wspace=0.05)
    plt.sca(ax1)
    chord_diagram(mat, grid_col=grid_col, annotation_track="grid")
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat, grid_col=grid_col, annotation_track=["name", "grid"], annotation_track_height=[0.03, 0.01])
    circos.clear()
    plt.sca(ax3)
    chord_diagram(mat, grid_col=grid_col, annotation_track=None)
    save_fig(fig, "ch15_chord_diagram_default_track.png")

    # 2. Clockwise sector labels in a pre-allocated track
    fig = new_figure(5.5, 5.5)
    ax = ensure_canvas(initialize=True)
    max_w = max(strwidth_canvas(s, ax=ax) for s in list(mat.index) + list(mat.columns))
    chord_diagram(
        mat,
        grid_col=grid_col,
        annotation_track="grid",
        pre_allocate_tracks={"track_height": max_w},
    )
    circos.track(
        track_index=1,
        bg_border=None,
        panel_fun=lambda x, y: circos.text(
            CELL_META.xcenter,
            CELL_META.ylim[0],
            CELL_META.sector_index,
            facing="clockwise",
            nice_facing=True,
            adj=(0.0, 0.5),
        ),
    )
    save_fig(fig, "ch15_chord_diagram_labels_show.png")

    # 3. Long rotated clockwise labels with dynamic circle_margin
    mat_long = mat.copy()
    mat_long.index = [f"Source_Group_{i}" for i in range(1, 4)]
    mat_long.columns = [f"Endpoint_Category_{i}" for i in range(1, 7)]
    gcol_long = {
        **{f"Source_Group_{i}": c for i, c in enumerate(["red", "green", "blue"], 1)},
        **{f"Endpoint_Category_{i}": "grey" for i in range(1, 7)},
    }
    fig = new_figure(6.2, 6.2)
    ax = ensure_canvas(initialize=True)
    max_long_w = max(strwidth_canvas(s, cex=0.8, ax=ax) for s in list(mat_long.index) + list(mat_long.columns))
    margin = max(0.05, max_long_w * 1.15)
    circos.par(circle_margin=(margin, margin, margin, margin))
    chord_diagram(
        mat_long,
        grid_col=gcol_long,
        annotation_track="grid",
        pre_allocate_tracks={"track_height": 0.05},
    )
    circos.par(points_overflow_warning=False)
    circos.track(
        track_index=1,
        bg_border=None,
        panel_fun=lambda x, y: circos.text(
            CELL_META.xcenter,
            CELL_META.ylim[0],
            CELL_META.sector_index,
            facing="clockwise",
            nice_facing=True,
            adj=(0.0, 0.5),
            cex=0.8,
        ),
    )
    save_fig(fig, "ch15_chord_diagram_labels_circle_margin.png")

    # 4. Sector labels inside grids
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, annotation_track=["grid", "axis"], annotation_track_height=mm_h(5))
    for si in get_all_sector_index():
        xlim = get_cell_meta_data("xlim", sector_index=si, track_index=1)
        ylim = get_cell_meta_data("ylim", sector_index=si, track_index=1)
        circos.text(
            float(np.mean(xlim)),
            float(np.mean(ylim)),
            si,
            sector_index=si,
            track_index=1,
            facing="bending.inside",
            nice_facing=True,
            col="white",
        )
    save_fig(fig, "ch15_chord_diagram_labels_inside.png")

    # 5. Adjust label direction based on sector width
    rng2 = np.random.default_rng(123)
    mat2 = np.abs(rng2.normal(size=(10, 10)))
    # Make a couple of rows/cols narrower so < 10 degrees triggers visibly
    mat2[0, :] *= 0.25
    mat2[:, 1] *= 0.25
    fig = new_figure(6.0, 6.0)
    ax = ensure_canvas(initialize=True)
    max_w2 = max(strwidth_canvas(s, ax=ax) for s in [f"R{i}" for i in range(1, 11)] + [f"C{i}" for i in range(1, 11)])
    np.random.seed(123)
    chord_diagram(
        mat2,
        annotation_track="grid",
        pre_allocate_tracks={"track_height": max_w2 * 1.3},
    )

    def _panel_adaptive_labels(x, y):
        xlim = get_cell_meta_data("xlim")
        xplot = get_cell_meta_data("xplot")
        ylim = get_cell_meta_data("ylim")
        sector_name = get_cell_meta_data("sector.index")
        if abs(xplot[1] - xplot[0]) < 12:
            circos.text(
                float(np.mean(xlim)),
                ylim[0],
                sector_name,
                facing="clockwise",
                nice_facing=True,
                adj=(0.0, 0.5),
                col="red",
                cex=0.85,
            )
        else:
            circos.text(
                float(np.mean(xlim)),
                ylim[0],
                sector_name,
                facing="inside",
                nice_facing=True,
                adj=(0.5, 0.0),
                col="blue",
                cex=0.85,
            )

    circos.track(track_index=1, panel_fun=_panel_adaptive_labels, bg_border=None)
    save_fig(fig, "ch15_chord_diagram_labels_multiple_style.png")

    # 6. Customize sector axes (absolute + percentage)
    fig = new_figure(6.0, 6.0)
    chord_diagram(
        mat,
        grid_col=grid_col,
        annotation_track="grid",
        pre_allocate_tracks={"track_height": mm_h(5)},
    )
    for si in get_all_sector_index():
        circos.axis(h="top", labels_cex=0.35, sector_index=si, track_index=2)

    def _panel_pct_axes(x, y):
        xlim = get_cell_meta_data("xlim")
        ylim = get_cell_meta_data("ylim")
        sector_name = get_cell_meta_data("sector.index")
        xplot = get_cell_meta_data("xplot")
        circos.lines(xlim, [float(np.mean(ylim)), float(np.mean(ylim))], lty=3)
        by = 0.2 if abs(xplot[1] - xplot[0]) > 30 else 0.5
        for p in np.arange(by, 1.0 + 1e-9, by):
            circos.text(
                p * (xlim[1] - xlim[0]) + xlim[0],
                float(np.mean(ylim)) + 0.1,
                f"{int(round(p * 100))}%",
                cex=0.4,
                adj=(0.5, 0.0),
                nice_facing=True,
            )
        circos.text(float(np.mean(xlim)), 1.0, sector_name, nice_facing=True, adj=(0.5, 0.0))

    circos.track(track_index=1, panel_fun=_panel_pct_axes, bg_border=None)
    save_fig(fig, "ch15_chord_diagram_axes.png")

    # 7. Horizontal and vertical symmetry
    fig = new_figure(8.6, 4.3)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06)
    plt.sca(ax1)
    circos.par(start_degree=0)
    chord_diagram(mat, grid_col=grid_col, big_gap=20)
    ax1.axhline(0, linestyle="--", color="#00000080", linewidth=1.0)
    circos.clear()
    plt.sca(ax2)
    circos.par(start_degree=90)
    chord_diagram(mat, grid_col=grid_col, big_gap=20)
    ax2.axvline(0, linestyle="--", color="#00000080", linewidth=1.0)
    save_fig(fig, "ch15_chord_diagram_sym.png")

    # 8. Compare two Chord diagrams side-by-side using calc_gap
    rng_cmp = np.random.default_rng(77)
    mat_cmp1 = pd.DataFrame(
        rng_cmp.integers(1, 21, size=(5, 5)),
        index=[f"R{i}" for i in range(1, 6)],
        columns=[f"C{i}" for i in range(1, 6)],
    )
    mat_cmp2 = mat_cmp1 / 2.0
    gap = calc_gap(mat_cmp1, mat_cmp2, big_gap=10, small_gap=1)
    print(f"=== calc_gap result: {gap:.2f} degrees ===")

    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(
        mat_cmp1,
        directional=1,
        grid_col=list(range(1, 6)) * 2,
        transparency=0.5,
        big_gap=10,
        small_gap=1,
    )
    ax1.set_title("mat1 (full scale, big_gap = 10)", fontsize=9.5)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(
        mat_cmp2,
        directional=1,
        grid_col=list(range(1, 6)) * 2,
        transparency=0.5,
        big_gap=gap,
        small_gap=1,
    )
    ax2.set_title(f"mat2 = mat1 / 2 (big_gap = {gap:.1f})", fontsize=9.5)
    save_fig(fig, "ch15_chord_diagram_compare.png")

    # 9. Compare two Chord diagrams side-by-side using xmax
    rs1 = mat_cmp1.abs().sum(axis=1)
    cs1 = mat_cmp1.abs().sum(axis=0)
    xmax_map = {**rs1.to_dict(), **cs1.to_dict()}
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(
        mat_cmp1,
        directional=1,
        grid_col=list(range(1, 6)) * 2,
        transparency=0.5,
        big_gap=10,
        small_gap=1,
    )
    ax1.set_title("mat1 (reference sector widths)", fontsize=9.5)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(
        mat_cmp2,
        directional=1,
        grid_col=list(range(1, 6)) * 2,
        transparency=0.5,
        big_gap=10,
        small_gap=1,
        xmax=xmax_map,
    )
    ax2.set_title("mat2 with xmax = mat1 sector totals", fontsize=9.5)
    save_fig(fig, "ch15_chord_diagram_compare_xmax.png")

    # 10. Multi-group Chord diagram (A, B, C)
    mat_g, mat1, mat2, mat3, gcol_g = _make_grouped_matrix()
    nm = list(dict.fromkeys(list(mat_g.index) + list(mat_g.columns)))
    group_abc = {s: s[0] for s in nm}
    fig = new_figure(6.0, 6.0)
    chord_diagram(mat_g, group=group_abc, grid_col=gcol_g)
    save_fig(fig, "ch15_chord_grouped.png")

    # 11. Multi-group Chord diagram (1..5)
    group_num = {s: s[1:] for s in nm}
    fig = new_figure(6.0, 6.0)
    chord_diagram(mat_g, group=group_num, grid_col=gcol_g)
    save_fig(fig, "ch15_chord_grouped2.png")

    # 12. Multi-group Chord diagram controlling group order (C, A, B)
    rng_perm = np.random.default_rng(11)
    nm_shuffled = list(rng_perm.permutation(nm))
    prefix_map = {"C": "1_C", "A": "2_A", "B": "3_B"}
    group_ord = {s: prefix_map[s[0]] for s in nm_shuffled}
    fig = new_figure(6.0, 6.0)
    chord_diagram(mat_g, group=group_ord, grid_col=gcol_g)
    save_fig(fig, "ch15_chord_grouped3.png")

    # 13. Multi-group Chord diagram with big_gap and small_gap
    fig = new_figure(6.0, 6.0)
    chord_diagram(mat_g, group=group_abc, grid_col=gcol_g, big_gap=20, small_gap=5)
    save_fig(fig, "ch15_chord_grouped4.png")

    # 14. Customized multi-group Chord diagram with highlight.sector
    fig = new_figure(6.0, 6.0)
    chord_diagram(
        mat_g,
        group=group_abc,
        grid_col=gcol_g,
        annotation_track=["grid", "axis"],
        pre_allocate_tracks={"track_height": mm_h(4), "track_margin": [mm_h(4), 0.0]},
    )
    circos.track(
        track_index=2,
        bg_border=None,
        panel_fun=lambda x, y: circos.text(
            CELL_META.xcenter,
            CELL_META.ycenter,
            CELL_META.sector_index,
            cex=0.6,
            nice_facing=True,
        ),
    )
    highlight.sector(list(mat1.index), track_index=1, col="red", text="A", cex=0.8, text_col="white", nice_facing=True)
    highlight.sector(list(mat1.columns), track_index=1, col="green", text="B", cex=0.8, text_col="white", nice_facing=True)
    highlight.sector(list(mat2.columns), track_index=1, col="blue", text="C", cex=0.8, text_col="white", nice_facing=True)
    save_fig(fig, "ch15_chord_grouped5.png")


if __name__ == "__main__":
    main()
