"""Generate all Chapter 14 figures: The chordDiagram() function."""

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
from scipy.stats import rankdata

from _common import new_figure, save_fig
from circlize_py import (
    chord_diagram,
    circos,
    color_ramp2,
    mm_h,
    rand_color,
)


def _make_base_data() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    rng = np.random.default_rng(999)
    arr = rng.permutation(np.arange(1, 19)).reshape((3, 6), order="F")
    rn = [f"S{i}" for i in range(1, 4)]
    cn = [f"E{i}" for i in range(1, 7)]
    mat = pd.DataFrame(arr, index=rn, columns=cn)
    df = pd.DataFrame(
        {
            "from": np.tile(rn, len(cn)),
            "to": np.repeat(cn, len(rn)),
            "value": arr.ravel(order="F"),
        }
    )
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
    return mat, df, grid_col


def main() -> None:
    mat, df, grid_col = _make_base_data()

    # 1. Basic usage
    fig = new_figure(5.5, 5.5)
    np.random.seed(999)
    chord_diagram(mat)
    save_fig(fig, "ch14_chord_diagram_basic.png")

    # 2. Sector order
    fig = new_figure(8.6, 4.3)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06)
    plt.sca(ax1)
    np.random.seed(101)
    chord_diagram(mat, order=["S2", "S1", "S3", "E4", "E1", "E5", "E2", "E6", "E3"])
    circos.clear()
    plt.sca(ax2)
    np.random.seed(101)
    chord_diagram(mat, order=["S2", "S1", "E4", "E1", "S3", "E5", "E2", "E6", "E3"])
    save_fig(fig, "ch14_chord_diagram_basic_order.png")

    # 3. Adjust by circos.par(gap_after=...)
    fig = new_figure(5.5, 5.5)
    np.random.seed(102)
    circos.par(gap_after=[5] * (mat.shape[0] - 1) + [15] + [5] * (mat.shape[1] - 1) + [15])
    chord_diagram(mat)
    save_fig(fig, "ch14_chord_diagram_basic_gap_after.png")

    # 4. big_gap
    fig = new_figure(5.5, 5.5)
    np.random.seed(103)
    chord_diagram(mat, big_gap=30)
    save_fig(fig, "ch14_chord_diagram_basic_big_gap.png")

    # 5. start_degree & clock_wise vs reversed order
    fig = new_figure(8.6, 4.3)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06)
    plt.sca(ax1)
    np.random.seed(104)
    circos.par(start_degree=85, clock_wise=False)
    chord_diagram(mat)
    circos.clear()
    plt.sca(ax2)
    np.random.seed(104)
    circos.par(start_degree=85)
    chord_diagram(mat, order=list(reversed(mat.columns)) + list(reversed(mat.index)))
    save_fig(fig, "ch14_chord_diagram_basic_start_degree.png")

    # 6. Set grid colors (mat vs mat.T)
    fig = new_figure(8.6, 4.3)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06)
    plt.sca(ax1)
    chord_diagram(mat, grid_col=grid_col)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat.T, grid_col=grid_col)
    save_fig(fig, "ch14_chord_diagram_grid_color.png")

    # 7. transparency = 0
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, transparency=0)
    save_fig(fig, "ch14_chord_diagram_color_transparency.png")

    # 8. Color matrix for links
    np.random.seed(105)
    col_mat = np.asarray(rand_color(mat.size, transparency=0.5), dtype=object).reshape(mat.shape, order="F")
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, col=col_mat)
    save_fig(fig, "ch14_chord_diagram_color_mat.png")

    # 9. Color mapping function
    col_fun = color_ramp2([float(mat.to_numpy().min()), float(mat.to_numpy().max())], ["#FFEEEE", "#FF0000"], transparency=0.5)
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, col=col_fun)
    save_fig(fig, "ch14_chord_diagram_color_fun.png")

    # 10. row_col and column_col
    fig = new_figure(8.6, 4.3)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06)
    plt.sca(ax1)
    chord_diagram(mat, grid_col=grid_col, row_col=[1, 2, 3])
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat, grid_col=grid_col, column_col=[1, 2, 3, 4, 5, 6])
    save_fig(fig, "ch14_chord_diagram_color_row_col.png")

    # 11. Link border scalar
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, link_lwd=2, link_lty=2, link_border="red")
    save_fig(fig, "ch14_chord_diagram_style_scalar.png")

    # 12. Link border full matrix
    lwd_mat = np.ones(mat.shape, dtype=float)
    lwd_mat[mat.to_numpy() > 12] = 2.0
    border_mat = np.full(mat.shape, np.nan, dtype=object)
    border_mat[mat.to_numpy() > 12] = "red"
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, link_lwd=lwd_mat, link_border=border_mat)
    save_fig(fig, "ch14_chord_diagram_style_fullmat.png")

    # 13. Link border submatrix (embedded into full matrix with NaN for unmarked links)
    border_mat2 = np.full(mat.shape, np.nan, dtype=object)
    border_mat2[1, :] = "black"
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, link_lwd=2, link_border=border_mat2)
    save_fig(fig, "ch14_chord_diagram_style_submatrix.png")

    # 14. Link border via 3-column DataFrames
    lty_df = pd.DataFrame({"rn": ["S1", "S2", "S3"], "cn": ["E5", "E6", "E4"], "lty": [1, 2, 3]})
    lwd_df = pd.DataFrame({"rn": ["S1", "S2", "S3"], "cn": ["E5", "E6", "E4"], "lwd": [2, 2, 2]})
    border_df = pd.DataFrame({"rn": ["S1", "S2", "S3"], "cn": ["E5", "E6", "E4"], "border": [1, 1, 1]})
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, link_lty=lty_df, link_lwd=lwd_df, link_border=border_df)
    save_fig(fig, "ch14_chord_diagram_style_dataframe.png")

    # 15. Highlight links by row_col transparency
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, row_col=["#FF000080", "#00FF0010", "#0000FF10"])
    save_fig(fig, "ch14_chord_diagram_highlight_row.png")

    # 16. Highlight links by color matrix
    col_mat_hl = col_mat.copy()
    col_mat_hl[mat.to_numpy() < 12] = "#00000000"
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, col=col_mat_hl)
    save_fig(fig, "ch14_chord_diagram_highlight_mat.png")

    # 17. Highlight links by 3-column DataFrame
    col_df = pd.DataFrame(
        {
            "rn": ["S1", "S2", "S3"],
            "cn": ["E5", "E6", "E4"],
            "col": ["#FF000080", "#00FF0080", "#0000FF80"],
        }
    )
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat, grid_col=grid_col, col=col_df)
    save_fig(fig, "ch14_chord_diagram_highlight_df.png")

    # 18. Highlight links by link_visible
    fig = new_figure(5.5, 5.5)
    chord_diagram(df, grid_col=grid_col, link_visible=df["value"] >= 10)
    save_fig(fig, "ch14_chord_diagram_link_visible.png")

    # 19. Order of positioning links on sectors
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(mat, grid_col=grid_col, link_sort=True, link_decreasing=True)
    ax1.set_title("link_sort = True, link_decreasing = True", fontsize=9.5)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat, grid_col=grid_col, link_sort=True, link_decreasing=False)
    ax2.set_title("link_sort = True, link_decreasing = False", fontsize=9.5)
    save_fig(fig, "ch14_chord_diagram_link_order1.png")

    # 20. z-index of adding links
    zmat = rankdata(mat.to_numpy()).reshape(mat.shape)
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(mat, grid_col=grid_col, transparency=0)
    ax1.set_title("Default z-order", fontsize=10)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat, grid_col=grid_col, transparency=0, link_zindex=zmat)
    ax2.set_title("link_zindex = rank(mat)", fontsize=10)
    save_fig(fig, "ch14_chord_diagram_link_order2.png")

    # 21. link_largest_ontop
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(mat, grid_col=grid_col, transparency=0, link_largest_ontop=False)
    ax1.set_title("link_largest_ontop = False", fontsize=10)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat, grid_col=grid_col, transparency=0, link_largest_ontop=True)
    ax2.set_title("link_largest_ontop = True", fontsize=10)
    save_fig(fig, "ch14_chord_diagram_link_largest_ontop.png")

    # 22. Self-links
    df2 = pd.DataFrame({"start": ["a", "b", "c", "a"], "end": ["a", "a", "b", "c"]})
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(df2, grid_col=[1, 2, 3], self_link=1)
    ax1.set_title("self_link = 1", fontsize=10)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(df2, grid_col=[1, 2, 3], self_link=2)
    ax2.set_title("self_link = 2", fontsize=10)
    save_fig(fig, "ch14_chord_diagram_self_link.png")

    # 23. Symmetric matrix
    rng_sym = np.random.default_rng(42)
    mat3 = rng_sym.normal(size=(5, 5))
    cor_mat = pd.DataFrame(np.corrcoef(mat3, rowvar=False), index=list("abcde"), columns=list("abcde"))
    col_fun_sym = color_ramp2([-1, 0, 1], ["green", "white", "red"])
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(cor_mat, grid_col=[1, 2, 3, 4, 5], symmetric=True, col=col_fun_sym)
    ax1.set_title("symmetric = True", fontsize=10)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(cor_mat, grid_col=[1, 2, 3, 4, 5], col=col_fun_sym)
    ax2.set_title("symmetric = False", fontsize=10)
    save_fig(fig, "ch14_chord_diagram_symmetric.png")

    # 24. Directional simple (1x3)
    fig = new_figure(10.5, 3.6)
    ax1, ax2, ax3 = fig.subplots(1, 3)
    fig.subplots_adjust(wspace=0.05)
    plt.sca(ax1)
    chord_diagram(mat, grid_col=grid_col, directional=1)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat, grid_col=grid_col, directional=1, diff_height=mm_h(5))
    circos.clear()
    plt.sca(ax3)
    chord_diagram(mat, grid_col=grid_col, directional=-1)
    save_fig(fig, "ch14_chord_diagram_directional_simple.png")

    # 25. Directional with overlapping row and column names
    rng2 = np.random.default_rng(77)
    mat2 = pd.DataFrame(
        rng2.permutation(np.arange(1, 101))[:35].reshape((5, 7), order="F"),
        index=list("abcde"),
        columns=list("abcdefg"),
    )
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat2, grid_col=list(range(1, 8)), directional=1, row_col=list(range(1, 6)))
    save_fig(fig, "ch14_chord_diagram_directional_overlap.png")

    # 26. Directional without self links
    mat3_ns = mat2.copy()
    for cn in set(mat3_ns.index) & set(mat3_ns.columns):
        mat3_ns.loc[cn, cn] = 0
    fig = new_figure(5.5, 5.5)
    chord_diagram(mat3_ns, grid_col=list(range(1, 8)), directional=1, row_col=list(range(1, 6)))
    save_fig(fig, "ch14_chord_diagram_directional_non_selfloop.png")

    # 27. Directional arrows on subset of links (no diffHeight)
    dt_mat = np.full(mat.shape, "none", dtype=object)
    dt_mat[0, 4] = "arrows"
    dt_mat[1, 5] = "arrows"
    dt_mat[2, 3] = "arrows"
    fig = new_figure(5.5, 5.5)
    chord_diagram(
        mat,
        grid_col=grid_col,
        directional=1,
        direction_type=dt_mat,
        link_arr_col="black",
        link_arr_length=0.2,
    )
    save_fig(fig, "ch14_chord_diagram_directional_arrow.png")

    # 28. Directional diffHeight + arrows on subset of links
    dt_df = pd.DataFrame(
        {
            "rn": ["S1", "S2", "S3"],
            "cn": ["E5", "E6", "E4"],
            "type": ["diffHeight+arrows", "diffHeight+arrows", "diffHeight+arrows"],
        }
    )
    fig = new_figure(5.5, 5.5)
    chord_diagram(
        mat,
        grid_col=grid_col,
        directional=1,
        direction_type=dt_df,
        link_arr_col="black",
        link_arr_length=0.2,
    )
    save_fig(fig, "ch14_chord_diagram_directional_arrow2.png")

    # 29. Big arrows
    rng_x = np.random.default_rng(123)
    matx = rng_x.normal(size=(8, 8))
    fig = new_figure(5.5, 5.5)
    np.random.seed(201)
    chord_diagram(
        matx,
        directional=1,
        direction_type=["diffHeight", "arrows"],
        link_arr_type="big.arrow",
    )
    save_fig(fig, "ch14_chord_diagram_directional_arrow3.png")

    # 30. Big arrows with negative diff_height
    fig = new_figure(5.5, 5.5)
    np.random.seed(201)
    chord_diagram(
        matx,
        directional=1,
        direction_type=["diffHeight", "arrows"],
        link_arr_type="big.arrow",
        diff_height=-mm_h(2),
    )
    save_fig(fig, "ch14_chord_diagram_directional_arrow4.png")

    # 31. link_target_prop and target_prop_height
    fig = new_figure(8.6, 4.3)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06)
    plt.sca(ax1)
    chord_diagram(mat, grid_col=grid_col, directional=1, link_target_prop=False)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat, grid_col=grid_col, directional=1, diff_height=mm_h(10), target_prop_height=mm_h(8))
    save_fig(fig, "ch14_chord_diagram_link_target_prop.png")

    # 32. Scaling on sectors
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(mat, grid_col=grid_col)
    ax1.set_title("Default", fontsize=10)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat, grid_col=grid_col, scale=True)
    ax2.set_title("scale = True", fontsize=10)
    save_fig(fig, "ch14_chord_diagram_scale.png")

    # Verify reduce behavior in stdout
    mat_red = pd.DataFrame(
        rng_x.normal(size=(6, 6)),
        index=[f"R{i}" for i in range(1, 7)],
        columns=[f"C{i}" for i in range(1, 7)],
    )
    mat_red.iloc[1, :] = 1e-10
    mat_red.iloc[:, 2] = 1e-10
    fig_tmp = new_figure(4.0, 4.0)
    chord_diagram(mat_red)
    buf = io.StringIO()
    with redirect_stdout(buf):
        circos.info()
    print("=== Reduce circos.info() ===")
    print(buf.getvalue().strip())
    circos.clear()
    plt.close(fig_tmp)

    # 33. Multiple links between the same pair of sectors
    rng_m = np.random.default_rng(55)
    pairs = [(r, c) for c in list("ABCD") for r in list("abc")]
    df_pos = pd.DataFrame(pairs, columns=["from", "to"])
    df_pos["value"] = rng_m.integers(1, 11, size=len(pairs))
    df_neg = pd.DataFrame(pairs, columns=["from", "to"])
    df_neg["value"] = -rng_m.integers(1, 11, size=len(pairs))
    df_multi = pd.concat([df_pos, df_neg], ignore_index=True)
    grid_col_m = {s: idx for idx, s in enumerate(list("abcABCD"), start=1)}

    fig = new_figure(5.5, 5.5)
    chord_diagram(
        df_multi,
        col=np.where(df_multi["value"] > 0, "red", "green"),
        grid_col=grid_col_m,
    )
    save_fig(fig, "ch14_chord_diagram_multiple_link.png")

    # 34. Split positive and negative links
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(df_multi, col="red", link_visible=df_multi["value"] > 0, grid_col=grid_col_m)
    ax1.set_title("Positive links", fontsize=10)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(df_multi, col="green", link_visible=df_multi["value"] < 0, grid_col=grid_col_m)
    ax2.set_title("Negative links", fontsize=10)
    save_fig(fig, "ch14_chord_diagram_multiple_link_split.png")

    # 35. Unequal width of link ends
    df_uneq = pd.DataFrame(pairs, columns=["from", "to"])
    df_uneq["value"] = 1
    df_uneq["value2"] = 3
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(df_uneq.iloc[:, :3], grid_col=grid_col_m)
    ax1.set_title("One column of values", fontsize=10)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(df_uneq.iloc[:, :4], grid_col=grid_col_m)
    ax2.set_title("Two columns of values", fontsize=10)
    save_fig(fig, "ch14_chord_diagram_unequal_end_width.png")

    # 36. Overlapping incoming/outgoing sub-intervals via link_overlap
    mat_ov = pd.DataFrame(
        [[0, 12, 8, 5], [6, 0, 10, 4], [9, 7, 0, 11], [3, 14, 6, 0]],
        index=list("abcd"),
        columns=list("abcd"),
    )
    gcol_ov = {"a": 1, "b": 2, "c": 3, "d": 4}
    fig = new_figure(8.6, 4.5)
    ax1, ax2 = fig.subplots(1, 2)
    fig.subplots_adjust(wspace=0.06, top=0.88)
    plt.sca(ax1)
    chord_diagram(mat_ov, grid_col=gcol_ov, directional=1, link_overlap=False)
    ax1.set_title("link_overlap = False", fontsize=10)
    circos.clear()
    plt.sca(ax2)
    chord_diagram(mat_ov, grid_col=gcol_ov, directional=1, link_overlap=True)
    ax2.set_title("link_overlap = True", fontsize=10)
    save_fig(fig, "ch14_chord_diagram_link_overlap.png")


if __name__ == "__main__":
    main()
