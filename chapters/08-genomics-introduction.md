# Introduction {#genomic-introduction}

Circular visualization is popular in Genomics and related omics fields. It is
efficient in revealing associations in high-dimensional genomic data. In genomic
plots, categories are usually chromosomes and values along the x-axes are
genomic positions, though they can also be any kind of general genomic
categories.

To make genomics analysis straightforward, **circlize-py** provides a family of
functions focused on genomic plots. These functions mirror the basic graphics
primitives but expect tabular genomic input data:

- `circos.genomicTrack()` (or `circos.genomicTrackPlotRegion()`): create a new track and add graphics.
- `circos.genomicPoints()`: low-level function, add points.
- `circos.genomicLines()`: low-level function, add lines or segments.
- `circos.genomicRect()`: low-level function, add rectangles.
- `circos.genomicText()`: low-level function, add text.
- `circos.genomicLink()`: add links.

Like the rest of **circlize-py**, every genomic function supports three
equivalent naming conventions (`circos.genomicTrack()`,
`circos_genomic_track()`, and `circos_genomicTrack()`), as well as R-style
keyword argument normalization (for example, `track_height` or `track.height`).
Because genomic functions are implemented on top of the basic circular
functions (`circos.track()`, `circos.points()`, etc.), you can freely mix both
sets of functions in the same plot.

## Input data {#input-data}

Genomic data is usually stored as a `pandas.DataFrame` where the first three
columns define the genomic regions and the remaining columns store values
associated with those regions. Each genomic region consists of three elements:
the genomic category (most commonly a chromosome name), the start position, and
the end position. This structure corresponds to the standard
[_BED_](https://genome.ucsc.edu/FAQ/FAQformat#format1) format widely used in
genomic research.

**circlize-py** provides `generateRandomBed()` (`generate_random_bed()`) to
generate synthetic genomic intervals for testing and prototyping. Positions are
sampled uniformly across the chromosomes of the specified genome (human `hg19`
by default), with the number of intervals per chromosome approximately
proportional to chromosome length. The parameters `nr` and `nc` control the
approximate number of rows and the number of value columns, respectively. Note
that `nr` is not always identical to `len(bed)` because per-chromosome counts
are rounded and adjusted to even break counts. The `fun` argument accepts a
callable taking an integer `k` and returning a sequence of `k` values, and `seed`
fixes the random generator for reproducibility.

```python
import string
import numpy as np
from circlize_py import generateRandomBed

bed = generateRandomBed(seed=999)
print(bed.head())
```

```text
    chr      start        end    value1
0  chr1    24535.0   378453.0  0.414901
1  chr1   529930.0   682796.0 -0.104398
2  chr1   740441.0   879381.0 -0.173096
3  chr1   965029.0  1225682.0 -0.494252
4  chr1  1443954.0  1769984.0  0.553933
```

```python
bed2 = generateRandomBed(nr=200, nc=4, seed=999)
print(len(bed2))
```

```text
205
```

```python
rng = np.random.default_rng(999)
bed3 = generateRandomBed(
    nc=2,
    fun=lambda k: rng.choice(list(string.ascii_lowercase), size=k, replace=True),
    seed=999,
)
print(bed3.head())
```

```text
    chr      start        end value1 value2
0  chr1    24535.0   378453.0      v      b
1  chr1   529930.0   682796.0      u      w
2  chr1   740441.0   879381.0      e      x
3  chr1   965029.0  1225682.0      e      z
4  chr1  1443954.0  1769984.0      e      f
```

All genomic plotting functions in **circlize-py** accept either a single
BED-like `pandas.DataFrame` or a `list[pandas.DataFrame]` representing genomic
data measured across multiple conditions or cohorts.
