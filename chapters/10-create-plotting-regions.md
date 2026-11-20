# Create plotting regions for genomic data {#genomic-plotting-region}

Genomic tracks are created and populated with `circos.genomicTrackPlotRegion()`
or its shorter alias `circos.genomicTrack()`. In the examples below, chromosomes
serve as the genomic categories and `data` is a BED-format `pandas.DataFrame`
whose first three columns are `(chr, start, end)` and whose remaining columns
hold associated values. More complex input structures (such as lists of
`DataFrame`s and `stack=True` mode) are covered in
[Modes for circos.genomicTrack()](modes-of-input.html).

Just like `circos.track()`, `circos.genomicTrack()` takes a user-defined
callback `panel_fun` applied to every cell, but with a genomic signature:

```python
circos.genomicTrackPlotRegion(
    data,
    panel_fun=lambda region, value, **kwargs: circos.genomicPoints(region, value, **kwargs),
)
```

Inside `panel_fun`, low-level genomic functions draw graphics in the current
cell. `circos.genomicTrack()` slices `data` for the active chromosome and passes
two `DataFrame`s to `panel_fun`:

- `region`: a two-column `DataFrame` containing `start` and `end` positions in
  the current chromosome (analogous to x values).
- `value`: a `DataFrame` containing the remaining columns starting from the
  fourth column onward (analogous to y values).

Always include `**kwargs` at the end of `panel_fun` and forward `**kwargs` to
inner `circos.genomic*()` calls. **circlize-py** uses `**kwargs` (together with
internal genomic state) to pass layer metadata such as `numeric_column`,
`stack`, and the layer index used by `getI(**kwargs)` (explained in
[Modes for circos.genomicTrack()](modes-of-input.html)).

The snippet below inspects `region` and `value` inside `panel_fun`:

```python
from circlize_py import CELL_META, circos, generateRandomBed

bed = generateRandomBed(nc=2, seed=123)
print(bed.head(2))
```

```text
    chr     start       end    value1    value2
0  chr1   46456.0  203165.0  0.328482  1.053208
1  chr1  253848.0  376923.0 -0.392262  0.901414
```

```python
circos.initializeWithIdeogram(plot_type=None)

def inspect_panel(region, value, **kwargs):
    if CELL_META.sector_index == "chr1":
        print(region.head(2))
        print(value.head(2))

circos.genomicTrackPlotRegion(bed, panel_fun=inspect_panel)
circos.clear()
```

```text
      start       end
0   46456.0  203165.0
1  253848.0  376923.0
     value1    value2
0  0.328482  1.053208
1 -0.392262  0.901414
```

Because `circos.genomicTrack()` creates a track, it must know the y-axis data
range (`ylim`). You can either specify `numeric_column` (column name strings,
0-based column indices, or a sequence of columns) or set `ylim` explicitly.
When neither is supplied, all numeric columns after the first three columns are
automatically used to infer `ylim`:

```python
circos.genomicTrackPlotRegion(
    data,
    ylim=(0, 1),
    panel_fun=lambda region, value, **kwargs: circos.genomicPoints(region, value, **kwargs),
)
circos.genomicTrackPlotRegion(
    data,
    numeric_column=["value1", "value2"],
    panel_fun=lambda region, value, **kwargs: circos.genomicPoints(region, value, **kwargs),
)
```

Because genomic functions are implemented using basic **circlize-py** tracks,
`circos.info()` can be called at any point to inspect sector and track
metadata.

The remainder of this chapter summarizes the low-level `circos.genomic*()`
functions. Full multi-track visual examples appear together in
[Modes for circos.genomicTrack()](modes-of-input.html).

## Points {#genomic-points}

`circos.genomicPoints()` mirrors `circos.points()`. It expects a two-column
`region` `DataFrame` and a `value` `DataFrame`. Each point is placed horizontally
at the midpoint `(start + end) / 2` of its region, and vertically at the
column(s) selected by `numeric_column`. If multiple columns are selected, points
are added once per column.

If `numeric_column` is set in `circos.genomicTrack()`, forwarding `**kwargs` to
`circos.genomicPoints(region, value, **kwargs)` automatically propagates the
selected value columns. If `numeric_column` is omitted in both places, all
numeric columns in `value` are plotted.

**Column indexing convention:** In **circlize-py**, column name strings (such as
`"value1"`) are always unambiguous. When using integer indices, Python 0-based
indexing applies: in the full BED table passed to `circos.genomicTrack()`, value
columns start at index `3` (e.g. `numeric_column=3` for the 4th column),
whereas inside `panel_fun` the `value` `DataFrame` starts at index `0` (e.g.
`numeric_column=0` for the first value column). When `numeric_column` is passed
from `circos.genomicTrack()` via `**kwargs`, 3 is subtracted automatically. For
convenience when porting R scripts, **circlize-py** also applies a 1-based
fallback whenever `idx == df.shape[1]` (so `numeric_column=1` on a 1-column
`value` table or `numeric_column=4` on a 4-column BED table still selects that
column).

```python
circos.genomicPoints(region, value, numeric_column=[0, 1])
circos.genomicPoints(region, value, cex=0.6, pch=16)
circos.genomicPoints(region, value, sector_index="chr1", track_index=1)

circos.genomicTrack(
    data,
    numeric_column=3,
    panel_fun=lambda region, value, **kwargs: circos.genomicPoints(region, value, **kwargs),
)
```

When a single numeric column is plotted, graphical parameters such as `pch`,
`cex`, and `col` may be scalars or sequences of length `len(region)`. When
multiple numeric columns are plotted, graphical parameters may be scalars or
sequences matching the number of numeric columns.

Conceptually, `circos.genomicPoints()` wraps `circos.points()` as follows:

```python
def genomic_points_concept(region, value, numeric_column=(0,), **kwargs):
    x = 0.5 * (region.iloc[:, 1] + region.iloc[:, 0])
    for col_idx in numeric_column:
        y = value.iloc[:, col_idx]
        circos.points(x, y, **kwargs)
```

## Lines {#genomic-lines}

`circos.genomicLines()` mirrors `circos.lines()`, with the same multi-column
and graphical-parameter rules as `circos.genomicPoints()`:

```python
circos.genomicLines(region, value, **kwargs)
circos.genomicLines(region, value, numeric_column=[0, 1])
circos.genomicLines(region, value, area=True, baseline=0.0, border="black")
circos.genomicLines(region, value, sector_index="chr1", track_index=1)
```

**circlize-py** also supports `type="segment"` (or `lty="segment"` in R-ported
calls) to draw each genomic interval as a horizontal segment spanning from
`start` to `end` at its numeric y-value (see Track H in
[Lines](modes-of-input.html#modes-lines)):

```python
circos.genomicLines(region, value, lwd=2, type="segment")
```

## Text {#genomic-text}

In `circos.genomicText()`, y-positions can come from `numeric_column` or an
explicit scalar/sequence `y`, and text strings can come from `labels_column` or
an explicit sequence `labels`:

```python
circos.genomicText(region, value, **kwargs)
circos.genomicText(region, value, y=1.0, labels=labels)
circos.genomicText(region, value, numeric_column=0, labels_column=1)
circos.genomicText(region, value, facing="clockwise", niceFacing=True, adj=(0.0, 0.5))
circos.genomicText(region, value, sector_index="chr1", track_index=1)
```

## Rectangles {#genomic-rectangles}

For `circos.genomicRect()`, horizontal bounds (`xleft` and `xright`) come
directly from the region `start` and `end` columns. You only specify vertical
bounds via `ytop`/`ybottom` or `ytop_column`/`ybottom_column`:

```python
circos.genomicRect(region, value, ytop=1.0, ybottom=0.0)
circos.genomicRect(region, value, ytop_column=1, ybottom=0.0)
circos.genomicRect(region, value, col="steelblue", border="black")
```

## Links {#genomic-links}

`circos.genomicLink()` takes two BED-like `DataFrame`s (`region1` and
`region2`) and draws chord ribbons between paired genomic intervals
(Figure 10.1). All extra graphical parameters are forwarded to `circos.link()`.

```python
import numpy as np
from circlize_py import circos, generateRandomBed, rand_color

rng = np.random.default_rng(123)
bed1 = generateRandomBed(nr=100, seed=123)
bed1 = bed1.iloc[rng.choice(len(bed1), size=20, replace=False)].reset_index(drop=True)
bed2 = generateRandomBed(nr=100, seed=124)
bed2 = bed2.iloc[rng.choice(len(bed2), size=20, replace=False)].reset_index(drop=True)

circos.initializeWithIdeogram()
circos.genomicLink(
    bed1,
    bed2,
    col=rand_color(len(bed1), transparency=0.5, seed=123),
    border=None,
)
circos.clear()
```

![Figure 10.1: Add links from two sets of genomic regions.](images/ch10_genomic_links.png)

## Mixed use of general circlize functions

Because `panel_fun` executes inside each cell just like `circos.track()`, you
can freely combine `circos.genomic*()` primitives with general `circos.*()`
calls such as reference lines, custom text, and axes:

```python
from circlize_py import CELL_META, circos

def mixed_panel(region, value, **kwargs):
    circos.genomicPoints(region, value, **kwargs)
    for h in (-1.0, -0.5, 0.0, 0.5, 1.0):
        circos.lines(CELL_META.cell_xlim, [h, h], lty=2, col="grey")
    circos.text(CELL_META.xcenter, 0.9, CELL_META.sector_index, cex=0.7)
    circos.axis("top")

circos.genomicTrack(bed, ylim=(-1.0, 1.0), panel_fun=mixed_panel)
```
