"""Generate all Chapter 16 figures: A complex example of Chord diagram."""

from __future__ import annotations

import json
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import DATA_DIR, add_colorbar, new_figure, save_fig
from circlize_py import (
    CELL_META,
    chord_diagram,
    circos,
    color_ramp2,
    color_to_hex,
    get_cell_meta_data,
    mm_y,
)


STATE_COLORS = {
    "TssA": "#E41A1C",
    "TssAFlnk": "#E41A1C",
    "TxFlnk": "#E41A1C",
    "Tx": "#E41A1C",
    "TxWk": "#E41A1C",
    "EnhG": "#E41A1C",
    "Enh": "#E41A1C",
    "ZNF/Rpts": "#E41A1C",
    "Het": "#377EB8",
    "TssBiv": "#377EB8",
    "BivFlnk": "#377EB8",
    "EnhBiv": "#377EB8",
    "ReprPC": "#377EB8",
    "ReprPCWk": "#377EB8",
    "Quies": "black",
}


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], dict[str, str], np.ndarray, float]:
    with open(DATA_DIR / "chromatin_transition.json", encoding="utf-8") as fh:
        raw = json.load(fh)

    all_states: list[str] = list(raw["mat"]["rownames"])
    n_states = len(all_states)
    rn = [f"R_{i}" for i in range(1, n_states + 1)]
    cn = [f"C_{i}" for i in range(1, n_states + 1)]

    mat_arr = np.array(raw["mat"]["values"], dtype=float)
    unchanged_prop = float(np.trace(mat_arr) / np.sum(mat_arr))
    np.fill_diagonal(mat_arr, 0.0)

    mat = pd.DataFrame(mat_arr, index=rn, columns=cn)
    meth_mat_1 = pd.DataFrame(np.array(raw["meth_mat_1"]["values"], dtype=float), index=rn, columns=cn)
    meth_mat_2 = pd.DataFrame(np.array(raw["meth_mat_2"]["values"], dtype=float), index=rn, columns=cn)

    state_col2: dict[str, str] = {}
    for i, st in enumerate(all_states, start=1):
        state_col2[f"R_{i}"] = STATE_COLORS[st]
        state_col2[f"C_{i}"] = STATE_COLORS[st]

    qati = float(np.quantile(mat_arr, 0.7))
    colmat = np.empty(mat_arr.shape, dtype=object)
    for i in range(n_states):
        hx = color_to_hex(state_col2[rn[i]], include_alpha=False)
        for j in range(n_states):
            colmat[i, j] = hx + ("A0" if mat_arr[i, j] > qati else "20")

    return mat, meth_mat_1, meth_mat_2, all_states, state_col2, colmat, unchanged_prop


def _step1_chord(
    mat: pd.DataFrame,
    colmat: np.ndarray,
    state_col2: dict[str, str],
) -> pd.DataFrame:
    circos.par(cell_padding=(0, 0, 0, 0), points_overflow_warning=False)
    cdm_res = chord_diagram(
        mat,
        col=colmat,
        grid_col=state_col2,
        directional=True,
        annotation_track="grid",
        big_gap=10,
        small_gap=1,
        pre_allocate_tracks={"track_height": 0.1},
        link_target_prop=False,
    )
    circos.par(points_overflow_warning=False)
    return cdm_res


def _step2_axes() -> None:
    def _panel_t2(x, y) -> None:
        if abs(CELL_META.cell_start_degree - CELL_META.cell_end_degree) > 3:
            sn = CELL_META.sector_index
            i_state = int(sn.split("_")[1])
            circos.text(
                CELL_META.xcenter,
                CELL_META.ycenter,
                str(i_state),
                col="white",
                font=2,
                cex=0.7,
                adj=(0.5, 0.5),
                nice_facing=True,
            )
            xlim = CELL_META.xlim
            breaks = np.arange(0.0, float(xlim[1]) + 1e-9, 4e5)
            circos.axis(
                major_at=breaks,
                labels=[f"{int(round(b / 1000))}KB" for b in breaks],
                labels_cex=0.5,
            )

    circos.track(track_index=2, panel_fun=_panel_t2, bg_border=None)


def _step3_target_prop(cdm_res: pd.DataFrame, state_col2: dict[str, str]) -> None:
    for _, row in cdm_res.iterrows():
        v1 = float(row["value1"])
        if v1 > 0:
            rn = str(row["rn"])
            cn = str(row["cn"])
            x1 = float(row["x1"])
            y_top = -float(mm_y(1.0, sector_index=rn, track_index=2))
            y_bot = -float(mm_y(2.0, sector_index=rn, track_index=2))
            circos.rect(
                x1,
                y_bot,
                x1 - abs(v1),
                y_top,
                col=state_col2[cn],
                border=state_col2[cn],
                sector_index=rn,
                track_index=2,
            )


def _step4_methylation(
    cdm_res: pd.DataFrame,
    mat: pd.DataFrame,
    meth_mat_1: pd.DataFrame,
    meth_mat_2: pd.DataFrame,
) -> tuple[object, object, float]:
    combined = np.concatenate([meth_mat_1.to_numpy().ravel(), meth_mat_2.to_numpy().ravel()])
    abs_max = float(np.nanquantile(np.abs(combined - 0.5), 0.95))
    col_fun = color_ramp2([0.5 - abs_max, 0.5, 0.5 + abs_max], ["blue", "white", "red"])
    col_fun2 = color_ramp2([-abs_max, 0.0, abs_max], ["green", "white", "orange"])

    ylim = get_cell_meta_data("ylim", sector_index=str(mat.index[0]), track_index=1)
    y1 = float(ylim[0]) + (float(ylim[1]) - float(ylim[0])) * 0.4
    y2 = float(ylim[1])

    for _, row in cdm_res.iterrows():
        v1 = float(row["value1"])
        if v1 <= 0:
            continue
        rn = str(row["rn"])
        cn = str(row["cn"])
        x1 = float(row["x1"])
        x2 = float(row["x2"])
        m1_val = float(meth_mat_1.loc[rn, cn])
        m2_val = float(meth_mat_2.loc[rn, cn])

        c_m1 = col_fun(m1_val)
        c_d12 = col_fun2(m2_val - m1_val)
        c_m2 = col_fun(m2_val)
        c_d21 = col_fun2(m1_val - m2_val)

        circos.rect(x1, y1, x1 - abs(v1), y1 + (y2 - y1) * 0.45, col=c_m1, border=c_m1, sector_index=rn, track_index=1)
        circos.rect(x1, y1 + (y2 - y1) * 0.55, x1 - abs(v1), y2, col=c_d12, border=c_d12, sector_index=rn, track_index=1)
        circos.rect(x2, y1, x2 - abs(v1), y1 + (y2 - y1) * 0.45, col=c_m2, border=c_m2, sector_index=cn, track_index=1)
        circos.rect(x2, y1 + (y2 - y1) * 0.55, x2 - abs(v1), y2, col=c_d21, border=c_d21, sector_index=cn, track_index=1)

    return col_fun, col_fun2, abs_max


def _draw_state_legend(fig: plt.Figure, all_states: list[str], rect: list[float]) -> None:
    lax = fig.add_axes(rect)
    lax.set_xlim(0.0, 1.0)
    lax.set_ylim(0.0, len(all_states) + 1.4)
    lax.axis("off")

    lax.text(0.0, len(all_states) + 0.55, "Chromatin States", fontsize=9.0, fontweight="bold", va="bottom", ha="left")
    n = len(all_states)
    for idx, st in enumerate(all_states, start=1):
        y_pos = n - idx + 0.15
        box = mpatches.Rectangle((0.0, y_pos), 0.14, 0.72, facecolor=STATE_COLORS[st], edgecolor="none")
        lax.add_patch(box)
        lax.text(0.07, y_pos + 0.36, str(idx), color="white", fontsize=7.5, fontweight="bold", ha="center", va="center")
        lax.text(0.20, y_pos + 0.36, st, color="#222222", fontsize=8.0, ha="left", va="center")


def main() -> None:
    mat, meth_mat_1, meth_mat_2, all_states, state_col2, colmat, unchanged_prop = _load_data()
    print(f"Unchanged chromatin state proportion: {unchanged_prop:.6f}")
    print("mat.iloc[:4, :4]:\n", mat.iloc[:4, :4])
    print("meth_mat_1.iloc[:4, :4]:\n", meth_mat_1.iloc[:4, :4])

    # Step 1: initial Chord diagram
    fig = new_figure(6.0, 6.0)
    cdm_res = _step1_chord(mat, colmat, state_col2)
    print("cdm_res.head():\n", cdm_res.head())
    save_fig(fig, "ch16_step1_chord.png")

    # Step 2: state indices + KB axes
    fig = new_figure(6.0, 6.0)
    cdm_res = _step1_chord(mat, colmat, state_col2)
    _step2_axes()
    save_fig(fig, "ch16_step2_axes.png")

    # Step 3: target proportion bars
    fig = new_figure(6.0, 6.0)
    cdm_res = _step1_chord(mat, colmat, state_col2)
    _step2_axes()
    _step3_target_prop(cdm_res, state_col2)
    save_fig(fig, "ch16_step3_target_prop.png")

    # Step 4: pre-allocated outer methylation rings
    fig = new_figure(6.0, 6.0)
    cdm_res = _step1_chord(mat, colmat, state_col2)
    _step2_axes()
    _step3_target_prop(cdm_res, state_col2)
    col_fun, col_fun2, abs_max = _step4_methylation(cdm_res, mat, meth_mat_1, meth_mat_2)
    print(f"abs_max (95th percentile of |meth - 0.5|): {abs_max:.4f}")
    save_fig(fig, "ch16_step4_methylation.png")

    # Step 5: full annotated plot with chromatin-state and methylation legends
    fig = new_figure(8.0, 6.2)
    ax = fig.add_axes([0.02, 0.04, 0.72, 0.92])
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-1.0, 1.0)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.sca(ax)

    cdm_res = _step1_chord(mat, colmat, state_col2)
    _step2_axes()
    _step3_target_prop(cdm_res, state_col2)
    col_fun, col_fun2, _ = _step4_methylation(cdm_res, mat, meth_mat_1, meth_mat_2)

    _draw_state_legend(fig, all_states, rect=[0.76, 0.45, 0.22, 0.50])
    add_colorbar(
        fig,
        col_fun,
        vmin=0.5 - abs_max,
        vmax=0.5 + abs_max,
        rect=[0.76, 0.25, 0.025, 0.14],
        title="Mean Methylation",
        ticks=[0.1, 0.3, 0.5, 0.7, 0.9],
        fontsize=7.5,
        title_fontsize=8.5,
    )
    add_colorbar(
        fig,
        col_fun2,
        vmin=-abs_max,
        vmax=abs_max,
        rect=[0.76, 0.04, 0.025, 0.14],
        title="Mean Difference",
        ticks=[-0.4, -0.2, 0.0, 0.2, 0.4],
        fontsize=7.5,
        title_fontsize=8.5,
    )
    save_fig(fig, "ch16_final_with_legends.png")


if __name__ == "__main__":
    main()
