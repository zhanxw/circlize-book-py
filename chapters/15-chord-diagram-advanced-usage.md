# Advanced usage of `chordDiagram()`

The default style of `chord_diagram()` (or `chordDiagram()`) handles most relational plots cleanly, and because it is built on standard `circlize-py` tracks, you can customize track layouts, sector labels, axes, symmetry, cross-diagram scales, and multi-group arrangements in depth.

Since matrix and adjacency-list inputs share the same customization pipeline, we illustrate these techniques with adjacency matrices (`pandas.DataFrame` / `numpy.ndarray`). Throughout this chapter, we reuse the 3x6 example matrix `mat` and color dictionary `grid_col`:

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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

rng = np.random.default_rng(999)
arr = rng.permutation(np.arange(1, 19)).reshape((3, 6), order="F")
mat = pd.DataFrame(arr, index=[f"S{i}" for i in range(1, 4)], columns=[f"E{i}" for i in range(1, 7)])
grid_col = {
    "S1": "red", "S2": "green", "S3": "blue",
    "E1": "grey", "E2": "grey", "E3": "grey",
    "E4": "grey", "E5": "grey", "E6": "grey",
}
```

## Organization of tracks

By default, `chord_diagram()` creates two tracks: track 1 for sector names and track 2 for colored grids with axes:

```python
chord_diagram(mat)
circos.info()
circos.clear()
```

```text
All your sectors:
['S1', 'S2', 'S3', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6']

All your tracks:
[1, 2]

Your current sector.index is E6
Your current track.index is 2
```

These tracks are controlled via `annotation_track` (any subset of `["name", "grid", "axis"]`, or `None`) and `annotation_track_height` (relative to the unit circle radius, or physical units via `mm_h()`). Axes are drawn only when `"grid"` is included in `annotation_track`:

```python
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10.5, 3.6))

plt.sca(ax1)
chord_diagram(mat, grid_col=grid_col, annotation_track="grid")
circos.clear()

plt.sca(ax2)
chord_diagram(
    mat,
    grid_col=grid_col,
    annotation_track=["name", "grid"],
    annotation_track_height=[0.03, 0.01],
)
circos.clear()

plt.sca(ax3)
chord_diagram(mat, grid_col=grid_col, annotation_track=None)
circos.clear()
```

![Track organization controlled by `annotation_track` and `annotation_track_height`.](images/ch15_chord_diagram_default_track.png)

You can pre-allocate empty outer tracks before drawing the Chord diagram using `pre_allocate_tracks`, then populate them later:

```python
chord_diagram(mat, pre_allocate_tracks=2)
circos.info()
circos.clear()
```

```text
All your sectors:
['S1', 'S2', 'S3', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6']

All your tracks:
[1, 2, 3, 4]

Your current sector.index is E6
Your current track.index is 4
```

Each pre-allocated track uses the following defaults, which can be overridden by passing a `dict` (single track) or a `list[dict]` (multiple tracks):

```python
{
    "ylim": [0.0, 1.0],
    "track_height": circos.par("track.height"),
    "bg_col": None,
    "bg_border": None,
    "bg_lty": 1,
    "bg_lwd": 1.0,
    "track_margin": circos.par("track.margin"),
}
```

For example:

```python
chord_diagram(mat, annotation_track=None, pre_allocate_tracks={"track_height": 0.3})
circos.clear()

# Or two pre-allocated tracks with per-track dictionaries:
chord_diagram(
    mat,
    annotation_track=None,
    pre_allocate_tracks=[{"track_height": 0.1}, {"bg_border": "black"}],
)
circos.clear()
```

## Customize sector labels

Because `chord_diagram()` does not directly expose text-facing options for sector labels, the cleanest approach is to omit `"name"` from `annotation_track`, pre-allocate an outer track, and populate track 1 afterward with `circos.track(track_index=1, ..., bg_border=None)`. Remember to pass `bg_border=None` so track 1 stays borderless:

```python
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
circos.clear()
```

![Clockwise radial sector labels added in a pre-allocated outer track.](images/ch15_chord_diagram_labels_show.png)

When labels are long and oriented radially (`"clockwise"` or `"reverse.clockwise"`), they can extend past the unit circle. Measuring the longest label with `strwidth_canvas()` and dynamically expanding `circos.par(circle_margin=...)` (or `canvas_xlim` / `canvas_ylim`) keeps every label comfortably inside the figure:

```python
mat_long = mat.copy()
mat_long.index = [f"Source_Group_{i}" for i in range(1, 4)]
mat_long.columns = [f"Endpoint_Category_{i}" for i in range(1, 7)]
gcol_long = {
    **{f"Source_Group_{i}": c for i, c in enumerate(["red", "green", "blue"], 1)},
    **{f"Endpoint_Category_{i}": "grey" for i in range(1, 7)},
}

ax = ensure_canvas(initialize=True)
max_long_w = max(
    strwidth_canvas(s, cex=0.8, ax=ax) for s in list(mat_long.index) + list(mat_long.columns)
)
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
circos.clear()
```

![Long rotated clockwise sector labels accommodated via dynamic `circle_margin`.](images/ch15_chord_diagram_labels_circle_margin.png)

You can also place sector names directly inside the grid bars by explicitly passing `sector_index` and `track_index` to `get_cell_meta_data()` and `circos.text()`:

```python
chord_diagram(
    mat,
    grid_col=grid_col,
    annotation_track=["grid", "axis"],
    annotation_track_height=mm_h(5),
)
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
circos.clear()
```

![Curved sector labels drawn inside the grid cells.](images/ch15_chord_diagram_labels_inside.png)

Or choose label orientation dynamically based on each sector's angular width (`abs(xplot[1] - xplot[0])`): narrow sectors get radial `"clockwise"` labels while wide sectors get tangential `"inside"` labels:

```python
rng2 = np.random.default_rng(123)
mat2 = np.abs(rng2.normal(size=(10, 10)))
mat2[0, :] *= 0.25
mat2[:, 1] *= 0.25

ax = ensure_canvas(initialize=True)
max_w2 = max(
    strwidth_canvas(s, ax=ax)
    for s in [f"R{i}" for i in range(1, 11)] + [f"C{i}" for i in range(1, 11)]
)

chord_diagram(mat2, annotation_track="grid", pre_allocate_tracks={"track_height": max_w2 * 1.3})

def panel_adaptive_labels(x, y):
    xlim = get_cell_meta_data("xlim")
    xplot = get_cell_meta_data("xplot")
    ylim = get_cell_meta_data("ylim")
    sector_name = get_cell_meta_data("sector.index")
    if abs(xplot[1] - xplot[0]) < 12:
        circos.text(
            float(np.mean(xlim)), ylim[0], sector_name,
            facing="clockwise", nice_facing=True, adj=(0.0, 0.5), col="red", cex=0.85,
        )
    else:
        circos.text(
            float(np.mean(xlim)), ylim[0], sector_name,
            facing="inside", nice_facing=True, adj=(0.5, 0.0), col="blue", cex=0.85,
        )

circos.track(track_index=1, panel_fun=panel_adaptive_labels, bg_border=None)
circos.clear()
```

![Adaptive sector label direction based on sector angular width.](images/ch15_chord_diagram_labels_multiple_style.png)

## Customize sector axes

With a pre-allocated outer track, you can combine standard absolute value axes on the grid track (`track_index=2`) with custom relative percentage axes in the outer track (`track_index=1`). Notice that narrow sectors (< 30 degrees) automatically use coarser 50% ticks while wider sectors use 20% ticks:

```python
chord_diagram(
    mat,
    grid_col=grid_col,
    annotation_track="grid",
    pre_allocate_tracks={"track_height": mm_h(5)},
)
for si in get_all_sector_index():
    circos.axis(h="top", labels_cex=0.35, sector_index=si, track_index=2)

def panel_pct_axes(x, y):
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

circos.track(track_index=1, panel_fun=panel_pct_axes, bg_border=None)
circos.clear()
```

![Dual sector axes combining absolute value ticks and custom percentage labels.](images/ch15_chord_diagram_axes.png)

## Put horizontally or vertically symmetric

When row and column sectors form two non-overlapping groups, `chord_diagram()` automatically centers the two groups around `circos.par(start_degree=...)`. Setting `start_degree=0` yields horizontal symmetry across `y = 0`, while `start_degree=90` yields vertical symmetry across `x = 0`:

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.6, 4.3))

plt.sca(ax1)
circos.par(start_degree=0)
chord_diagram(mat, grid_col=grid_col, big_gap=20)
ax1.axhline(0, linestyle="--", color="#00000080", linewidth=1.0)
circos.clear()

plt.sca(ax2)
circos.par(start_degree=90)
chord_diagram(mat, grid_col=grid_col, big_gap=20)
ax2.axvline(0, linestyle="--", color="#00000080", linewidth=1.0)
circos.clear()
```

![Rotating two-group Chord diagrams for horizontal (`start_degree=0`) or vertical (`start_degree=90`) symmetry.](images/ch15_chord_diagram_sym.png)

## Compare two Chord diagrams

By default, Chord diagram sector widths are normalized to fill `360 - sum(gaps)` degrees, so comparing two matrices with different total link weights side-by-side requires putting them on a common scale. **circlize-py** provides two complementary ways to achieve this: `calc_gap()` and `xmax`.

### Equal arc scale via `calc_gap()`

When comparing two non-overlapping two-group matrices where `sum(|mat1|) >= sum(|mat2|)`, `calc_gap(mat1, mat2, big_gap=..., small_gap=...)` computes the exact `big_gap` for the second diagram so that one data unit spans the same arc angle in both plots (provided `small_gap` matches):

```python
rng_cmp = np.random.default_rng(77)
mat_cmp1 = pd.DataFrame(
    rng_cmp.integers(1, 21, size=(5, 5)),
    index=[f"R{i}" for i in range(1, 6)],
    columns=[f"C{i}" for i in range(1, 6)],
)
mat_cmp2 = mat_cmp1 / 2.0

gap = calc_gap(mat_cmp1, mat_cmp2, big_gap=10, small_gap=1)
# gap is 79.0 degrees

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.6, 4.5))

plt.sca(ax1)
chord_diagram(
    mat_cmp1, directional=1, grid_col=list(range(1, 6)) * 2,
    transparency=0.5, big_gap=10, small_gap=1,
)
ax1.set_title("mat1 (full scale, big_gap = 10)", fontsize=9.5)
circos.clear()

plt.sca(ax2)
chord_diagram(
    mat_cmp2, directional=1, grid_col=list(range(1, 6)) * 2,
    transparency=0.5, big_gap=gap, small_gap=1,
)
ax2.set_title(f"mat2 = mat1 / 2 (big_gap = {gap:.1f})", fontsize=9.5)
circos.clear()
```

![Comparing two Chord diagrams on a common unit scale using `calc_gap()`.](images/ch15_chord_diagram_compare.png)

### Matching per-sector capacity via `xmax`

Alternatively, passing `xmax` (a `dict` or `pd.Series` mapping sector names to maximum capacities) fixes the total width of each individual sector across plots, leaving unused empty space on smaller sectors:

```python
rs1 = mat_cmp1.abs().sum(axis=1)
cs1 = mat_cmp1.abs().sum(axis=0)
xmax_map = {**rs1.to_dict(), **cs1.to_dict()}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.6, 4.5))

plt.sca(ax1)
chord_diagram(
    mat_cmp1, directional=1, grid_col=list(range(1, 6)) * 2,
    transparency=0.5, big_gap=10, small_gap=1,
)
ax1.set_title("mat1 (reference sector widths)", fontsize=9.5)
circos.clear()

plt.sca(ax2)
chord_diagram(
    mat_cmp2, directional=1, grid_col=list(range(1, 6)) * 2,
    transparency=0.5, big_gap=10, small_gap=1, xmax=xmax_map,
)
ax2.set_title("mat2 with xmax = mat1 sector totals", fontsize=9.5)
circos.clear()
```

![Comparing two Chord diagrams by pinning per-sector widths with `xmax`.](images/ch15_chord_diagram_compare_xmax.png)

## Multiple-group Chord diagram {#multiple-group-chord-diagram}

When sectors fall into more than two groups, the `group` parameter of `chord_diagram()` automatically orders sectors by group and places `big_gap` between groups and `small_gap` within groups. This works identically for matrix and adjacency-list inputs.

Let's construct a 10x10 matrix connecting three groups (`A`, `B`, and `C`):

```python
rng = np.random.default_rng(321)
mat1 = pd.DataFrame(rng.normal(size=(5, 5)), index=[f"A{i}" for i in range(1, 6)], columns=[f"B{i}" for i in range(1, 6)])
mat2 = pd.DataFrame(rng.normal(size=(5, 5)), index=[f"A{i}" for i in range(1, 6)], columns=[f"C{i}" for i in range(1, 6)])
mat3 = pd.DataFrame(rng.normal(size=(5, 5)), index=[f"B{i}" for i in range(1, 6)], columns=[f"C{i}" for i in range(1, 6)])

mat_g = pd.DataFrame(0.0, index=list(mat2.index) + list(mat3.index), columns=list(mat1.columns) + list(mat2.columns))
mat_g.loc[mat1.index, mat1.columns] = mat1
mat_g.loc[mat2.index, mat2.columns] = mat2
mat_g.loc[mat3.index, mat3.columns] = mat3

nm = list(dict.fromkeys(list(mat_g.index) + list(mat_g.columns)))
gcol_g = {s: (2 if s[0] == "A" else (3 if s[0] == "B" else 4)) for s in nm}
```

Pass a dictionary (or `pd.Series`) mapping each sector name to its group label:

```python
group_abc = {s: s[0] for s in nm}
chord_diagram(mat_g, group=group_abc, grid_col=gcol_g)
circos.clear()
```

![Grouped Chord diagram separating sectors into groups `A`, `B`, and `C`.](images/ch15_chord_grouped.png)

Changing the grouping dictionary immediately regroups the exact same matrix—for example, grouping by trailing index (`1` through `5`):

```python
group_num = {s: s[1:] for s in nm}
chord_diagram(mat_g, group=group_num, grid_col=gcol_g)
circos.clear()
```

![Grouped Chord diagram with sectors grouped by numeric suffix `1`–`5`.](images/ch15_chord_grouped2.png)

In **circlize-py**, `group` preserves insertion order of sectors *within* each group and sorts the group labels lexicographically. Thus, shuffling the key insertion order shuffles within-group sector ordering, and using sortable group labels (such as `"1_C"`, `"2_A"`, `"3_B"`) puts groups in any desired `C`, `A`, `B` sequence:

```python
nm_shuffled = list(np.random.default_rng(11).permutation(nm))
prefix_map = {"C": "1_C", "A": "2_A", "B": "3_B"}
group_ord = {s: prefix_map[s[0]] for s in nm_shuffled}
chord_diagram(mat_g, group=group_ord, grid_col=gcol_g)
circos.clear()
```

![Controlling group order (`C`, `A`, `B`) and within-group sector permutation via `group`.](images/ch15_chord_grouped3.png)

Use `big_gap` and `small_gap` to tune between-group and within-group spacing:

```python
chord_diagram(mat_g, group=group_abc, grid_col=gcol_g, big_gap=20, small_gap=5)
circos.clear()
```

![Adjusting between-group (`big_gap=20`) and within-group (`small_gap=5`) gaps.](images/ch15_chord_grouped4.png)

For a richer multi-group layout, pre-allocate an outer track, place sector labels inside the grid cells (now track 2), and use `highlight.sector()` on track 1 to draw group-level banners:

```python
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
        CELL_META.xcenter, CELL_META.ycenter, CELL_META.sector_index,
        cex=0.6, nice_facing=True,
    ),
)
highlight.sector(list(mat1.index), track_index=1, col="red", text="A", cex=0.8, text_col="white", nice_facing=True)
highlight.sector(list(mat1.columns), track_index=1, col="green", text="B", cex=0.8, text_col="white", nice_facing=True)
highlight.sector(list(mat2.columns), track_index=1, col="blue", text="C", cex=0.8, text_col="white", nice_facing=True)
circos.clear()
```

![Customized multi-group Chord diagram with group banners drawn via `highlight.sector()`.](images/ch15_chord_grouped5.png)

Under the hood, `group` simply computes an ordered sector list and a matching `gap_after` vector for `circos.par()`. You can achieve the exact same layout manually with `order` and `circos.par(gap_after=...)`:

```python
ordered_sectors = [s for _, s in sorted((grp, sec) for sec, grp in group_abc.items())]
circos.par(gap_after=[1, 1, 1, 1, 5, 1, 1, 1, 1, 5, 1, 1, 1, 1, 5])
chord_diagram(mat_g, order=ordered_sectors, grid_col=gcol_g)
circos.clear()
```
