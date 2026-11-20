"""Shared utilities for generating circlize-book-py book figures."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Sequence

# Ensure MPLCONFIGDIR points to a writable directory before importing matplotlib
_mpl_dir = Path("/tmp/mplconfig")
_mpl_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_mpl_dir))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_SRC = REPO_ROOT.parent / "src"
if WORKSPACE_SRC.exists() and str(WORKSPACE_SRC) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_SRC))

from circlize_py import circos, color_to_hex  # noqa: E402

CHAPTERS_DIR = REPO_ROOT / "chapters"
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = REPO_ROOT / "docs"
BOOK_DIR = DOCS_DIR / "book"
IMAGES_DIR = BOOK_DIR / "images"
ASSETS_DIR = BOOK_DIR / "assets"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def reset_state() -> None:
    """Reset circlize global state, parameters, and close all Matplotlib figures."""
    circos.clear()
    circos.par(RESET=True)
    plt.close("all")


def new_figure(width: float = 6.5, height: float = 6.5, dpi: int = 140) -> plt.Figure:
    """Reset circlize state and return a clean Matplotlib figure."""
    reset_state()
    return plt.figure(figsize=(width, height), dpi=dpi, facecolor="white")


def save_fig(
    fig: plt.Figure,
    filename: str,
    dpi: int = 140,
    tight: bool = True,
    pad_inches: float = 0.12,
) -> Path:
    """Save figure to docs/book/images/ and clean up circlize & matplotlib state."""
    out = IMAGES_DIR / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        save_kwargs: dict[str, Any] = {"dpi": dpi, "facecolor": "white"}
        if tight:
            save_kwargs["bbox_inches"] = "tight"
            save_kwargs["pad_inches"] = pad_inches
        fig.savefig(out, **save_kwargs)
    finally:
        reset_state()
    return out


def overlay_axes(fig: plt.Figure, base_ax: Any = None) -> Any:
    """Create a transparent Axes overlaying base_ax for multi-circle plots."""
    if base_ax is None:
        base_ax = fig.axes[0] if fig.axes else fig.add_subplot(111)
    ax = fig.add_axes(base_ax.get_position(), frameon=False)
    ax.patch.set_alpha(0.0)
    ax.set_axis_off()
    plt.sca(ax)
    return ax


def colorramp_to_cmap(
    col_fun: Any,
    vmin: float,
    vmax: float,
    n: int = 256,
    name: str = "circlize_ramp",
) -> LinearSegmentedColormap:
    """Sample a circlize colorRamp2 callable into a Matplotlib colormap."""
    vals = np.linspace(float(vmin), float(vmax), int(n))
    cols = [color_to_hex(col_fun(float(v)), include_alpha=True) for v in vals]
    return LinearSegmentedColormap.from_list(name, cols, N=n)


def add_colorbar(
    fig: plt.Figure,
    col_fun: Any,
    vmin: float,
    vmax: float,
    rect: Sequence[float],
    title: str = "",
    ticks: Sequence[float] | None = None,
    orientation: str = "vertical",
    fontsize: float = 8.5,
    title_fontsize: float = 9.0,
) -> Any:
    """Draw a continuous colorbar legend inside explicit figure coordinates [l, b, w, h]."""
    cax = fig.add_axes(list(rect))
    cmap = colorramp_to_cmap(col_fun, vmin, vmax)
    norm = Normalize(vmin=float(vmin), vmax=float(vmax))
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cb = fig.colorbar(sm, cax=cax, orientation=orientation)
    if ticks is not None:
        cb.set_ticks(list(ticks))
    cb.ax.tick_params(labelsize=fontsize)
    if title:
        if orientation == "vertical":
            cb.ax.set_title(title, loc="left", fontsize=title_fontsize, fontweight="bold", pad=6)
        else:
            cb.ax.set_title(title, loc="left", fontsize=title_fontsize, fontweight="bold", pad=4)
    return cb


def add_discrete_legend(
    ax_or_fig: Any,
    items: Sequence[tuple[str, str]],
    kind: str = "patch",
    title: str = "",
    loc: str = "center",
    bbox_to_anchor: Any = None,
    ncol: int = 1,
    fontsize: float = 8.5,
    title_fontsize: float = 9.0,
    lwd: float = 2.0,
    markersize: float = 6.0,
    frameon: bool = False,
) -> Any:
    """Add a clean discrete point, line, or patch legend to a figure or axes."""
    handles = []
    for label, color in items:
        hex_col = color_to_hex(color, include_alpha=True)
        if kind == "point":
            handles.append(
                Line2D(
                    [0], [0],
                    marker="o",
                    linestyle="None",
                    markerfacecolor=hex_col,
                    markeredgecolor=hex_col,
                    markersize=markersize,
                    label=label,
                )
            )
        elif kind == "line":
            handles.append(Line2D([0], [0], color=hex_col, lw=lwd, label=label))
        else:
            handles.append(Patch(facecolor=hex_col, edgecolor="#333333", linewidth=0.5, label=label))

    kwargs: dict[str, Any] = {
        "handles": handles,
        "loc": loc,
        "ncol": ncol,
        "fontsize": fontsize,
        "frameon": frameon,
        "title": title if title else None,
        "title_fontsize": title_fontsize,
    }
    if bbox_to_anchor is not None:
        kwargs["bbox_to_anchor"] = bbox_to_anchor
    leg = ax_or_fig.legend(**kwargs)
    if leg is not None and title:
        leg.get_title().set_fontweight("bold")
        leg._legend_box.align = "left"
    return leg
