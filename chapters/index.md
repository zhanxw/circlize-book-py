# About {#about}

This is the Python documentation of [**circlize-py**](https://github.com/zhanxw/circlize-master) — a pure-Python port of Zuguang Gu's [**circlize**](https://cran.r-project.org/package=circlize) package for circular visualization, built on `numpy`, `pandas`, `matplotlib`, `scipy`, and `Pillow`. Examples in this book are generated under `circlize_py` version `0.4.16` (matching R `circlize` v0.4.16).

> **Quick Browse:** Looking for a visual overview of every plot in the book? Open the [**Figure Gallery & Master Index**](gallery.html) to browse, filter, zoom, inspect Python snippets, and jump straight to any of the 173 example figures.

If you use **circlize** / **circlize-py** in your publications, please cite the original paper:

> Gu, Z. (2014) circlize implements and enhances circular visualization in R. *Bioinformatics*, 30(19), 2811–2812. DOI: [10.1093/bioinformatics/btu393](https://doi.org/10.1093/bioinformatics/btu393)

![Circular Visualization in Python cover](images/ch00_cover.png)

## Installation {#installation}

From the repository root (requires Python >= 3.10):

```bash
pip install -e ".[dev]"
```

Once installed, both top-level package names can be imported interchangeably:

```python
import circlize_py
# or
import circlize
```

## R-to-Python migration & 3-way API parity {#r-to-python-migration}

Every exported function in `circlize-py` supports **three interchangeable calling styles** alongside automatic keyword normalization so R dotted or camelCase keyword arguments (such as `track_height` / `track.height`, `nice_facing` / `niceFacing`, `bg_col` / `bg.col`, `pre_allocate_tracks` / `preAllocateTracks`) translate directly:

| Style | Example calls | Original R (`library(circlize)`) | Notes |
| --- | --- | --- | --- |
| **Idiomatic Python (`snake_case`)** | `circos_initialize(...)`, `circos_track(...)`, `chord_diagram(...)`, `color_ramp2(...)` | `circos.initialize(...)`, `circos.track(...)`, `chordDiagram(...)`, `colorRamp2(...)` | Recommended for new Python codebases |
| **R camelCase (`NAMESPACE` aliases)** | `circos_trackPlotRegion(...)`, `chordDiagram(...)`, `colorRamp2(...)`, `generateRandomBed(...)` | `circos.trackPlotRegion(...)`, `chordDiagram(...)`, `colorRamp2(...)`, `generateRandomBed(...)` | Exact top-level R camelCase names |
| **R dot-syntax namespaces** | `circos.initialize(...)`, `circos.par(...)`, `circos.track(...)`, `draw.sector(...)`, `highlight.sector(...)`, `reverse.circlize(...)`, `read.cytoband(...)` | `circos.initialize(...)`, `circos.par(...)`, `circos.track(...)`, `draw.sector(...)`, `highlight.sector(...)`, `reverse.circlize(...)`, `read.cytoband(...)` | Mirrors R scripts nearly line-for-line |

> **Note:** Python built-ins `set` and `print` are intentionally **not** shadowed by dot namespaces. Use `set_current_cell(...)`, `set_current_sector_index(...)`, `set_current_track_index(...)`, and `circos.info()` directly.

## Indexing & key conventions {#indexing-conventions}

To combine Python conventions cleanly with faithful R `circlize` porting, keep the following indexing rules in mind:

1. **1-based `track_index` and `CELL_META.sector.numeric.index` vs. 0-based heatmap rows:**
   - `track_index` is **1-based** (`1, 2, ..., n_tracks`), matching R `circlize` (`track_index=1` is the outermost track).
   - `CELL_META.sector.numeric.index` (or `CELL_META.sector_numeric_index`) is **1-based** (`1..n_sectors`), matching R; `CELL_META.sector_idx` gives the **0-based** Python sector position (`0..n_sectors - 1`).
   - Heatmap row selectors follow **0-based Python indexing**: `CELL_META.subset` and `CELL_META.row_order` contain 0-based row indices (`0..n_rows - 1`), and `circos.heatmap.link(row_ind1, row_ind2)` and `circos.heatmap.get.x(row_ind)` accept either 0-based integer indices or row-name strings.
2. **Genomic value column selectors:**
   - Column-name strings (e.g., `numeric_column="value1"`, `labels_column="gene"`) and 0-based integer indices are supported, with automatic 1-based fallback when `idx == df.shape[1]` for compatibility with R BED scripts.
3. **Literal padding with `I(...)`:**
   - Import `from circlize_py import I` when passing raw data-coordinate values to `padding=I([...])` in `highlight.sector(...)`.
4. **Colors and coordinate matrices:**
   - All 657 R named colors (e.g., `"grey50"`, `"red3"`), R palette indices `1..8`, `#RRGGBB` / `#RRGGBBAA` hex strings, and Matplotlib colors work natively.
   - `circlize()` and `reverse.circlize()` return a `NamedMatrix2D` supporting NumPy indexing (`pos[0, 0]`), named column selection (`pos[:, "theta"]`), and attribute access (`pos.theta`, `pos.rou`, `pos.x`, `pos.y`).

## Python environment {#python-environment}

Figures and code outputs in this edition were verified in the following environment:

```text
Python       : 3.14.10
circlize_py  : 0.4.16
numpy        : 2.5.5
pandas       : 3.1.1
matplotlib   : 3.11.2
scipy        : 1.18.1
Pillow       : 13.0.0
Platform     : macOS (Darwin)
```
