# Make fun of the package {#make-fun-of-the-package}

Because **circlize-py** provides low-level circular geometry primitives (`circos.axis()`, `circos.text()`, `circos.rect()`, `draw.sector()`) on top of Matplotlib, it can also draw playful non-genomic circular graphics. Below are three classic examples.

## A clock

The first example draws an analog clock face. The key function is `circos.axis()` inside a single full-circle sector where major tick `0` overlaps with major tick `12`.

After setting up the dial (`0`–`12` ticks and `downward` hour labels), we compute the angles of the second, minute, and hour hands from the current wall-clock time (`datetime.now()`) and draw the hands directly in canvas coordinates (`[-1, 1] x [-1, 1]`) with Matplotlib's `ax.annotate()`:

```python
from datetime import datetime
import math
import numpy as np
from circlize_py import circos, ensure_canvas, mm_y

ax = ensure_canvas(initialize=True)

circos.par(gap_degree=0, cell_padding=(0, 0, 0, 0), start_degree=90)
circos.initialize("a", xlim=(0, 12))
circos.track(ylim=(0, 1), bg_border=None)
circos.axis(
    major_at=np.arange(0, 13),
    labels=None,
    direction="inside",
    major_tick_length=mm_y(2),
)
circos.text(
    np.arange(1, 13),
    np.repeat(1.0, 12) - mm_y(6),
    [str(h) for h in range(1, 13)],
    facing="downward",
)

now = datetime.now()
sec = now.second + (1 if now.microsecond > 0 else 0)
minute = now.minute
hour = now.hour % 12

sec_rad = math.radians(90.0 - sec / 60.0 * 360.0)
min_rad = math.radians(90.0 - minute / 60.0 * 360.0)
hour_rad = math.radians(90.0 - hour / 12.0 * 360.0 - minute / 60.0 * 360.0 / 12.0)

ax.annotate(
    "",
    xy=(math.cos(sec_rad) * 0.8, math.sin(sec_rad) * 0.8),
    xytext=(0.0, 0.0),
    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0, mutation_scale=12),
)
ax.annotate(
    "",
    xy=(math.cos(min_rad) * 0.7, math.sin(min_rad) * 0.7),
    xytext=(0.0, 0.0),
    arrowprops=dict(arrowstyle="-|>", color="black", lw=2.0, mutation_scale=14),
)
ax.annotate(
    "",
    xy=(math.cos(hour_rad) * 0.4, math.sin(hour_rad) * 0.4),
    xytext=(0.0, 0.0),
    arrowprops=dict(arrowstyle="-|>", color="black", lw=2.2, mutation_scale=14),
)

circos.clear()
```

![A clock.](images/ch17_clock.png)

## A dartboard

The second example builds a regulation 20-sector dartboard. Five tracks with custom `track_height` values form the number ring, double ring, outer single area, triple ring, and inner single area, while two `draw.sector()` calls add the outer green bullseye (`rou1=0.1`) and inner red bullseye (`rou1=0.05`). Setting `start_degree=360/20/2` (`9` degrees) and `clock_wise=False` aligns sector `20` vertically at 12 o'clock, and `circos.track_text()` places the sector scores around the black outer ring:

```python
import numpy as np
from circlize_py import circos, draw

sectors = [str(i) for i in range(1, 21)]
dart_labels = [13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10, 6]

circos.par(
    gap_degree=0,
    cell_padding=(0, 0, 0, 0),
    start_degree=360.0 / 20.0 / 2.0,
    track_margin=(0, 0),
    clock_wise=False,
)
circos.initialize(sectors, xlim=(0, 1))

circos.track(ylim=(0, 1), sectors=sectors, bg_col="black", track_height=0.15)
circos.track_text(
    x=np.repeat(0.5, 20),
    y=np.repeat(0.5, 20),
    labels=[str(v) for v in dart_labels],
    cex=0.85,
    sectors=sectors,
    col="#EEEEEE",
    font=2,
    facing="downward",
)
circos.track(
    ylim=(0, 1), sectors=sectors,
    bg_col=["#E41A1C", "#4DAF4A"] * 10, bg_border="#EEEEEE", track_height=0.05,
)
circos.track(
    ylim=(0, 1), sectors=sectors,
    bg_col=["black", "white"] * 10, bg_border="#EEEEEE", track_height=0.275,
)
circos.track(
    ylim=(0, 1), sectors=sectors,
    bg_col=["#E41A1C", "#4DAF4A"] * 10, bg_border="#EEEEEE", track_height=0.05,
)
circos.track(
    ylim=(0, 1), sectors=sectors,
    bg_col=["black", "white"] * 10, bg_border="#EEEEEE", track_height=0.375,
)

draw.sector(center=(0, 0), start_degree=0, end_degree=360, rou1=0.1, col="#4DAF4A", border="#EEEEEE")
draw.sector(center=(0, 0), start_degree=0, end_degree=360, rou1=0.05, col="#E41A1C", border="#EEEEEE")

circos.clear()
```

![A dartboard.](images/ch17_dartboard.png)

## Ba-Gua and Tai-Ji

The third example renders [Ba-Gua](https://en.wikipedia.org/wiki/Bagua) and the central [Tai-Ji](http://en.wikipedia.org/wiki/Taiji_(philosophy)) symbol using `circos.rect()` and `draw.sector()`.

Ba-Gua originated in ancient Chinese philosophy thousands of years ago, combining two basic signs—the solid *Yang* line (`add_yang_yao`) and the broken *Yin* line (`add_yin_yao`)—across three concentric tracks and eight sectors to form the eight trigrams. At the center sits Tai-Ji, representing duality and continuous mutual transformation between complementary opposites (*Yin* and *Yang*), each containing a seed of the other:

```python
from circlize_py import CELL_META, circos, draw, get_cell_meta_data

sectors = [str(i) for i in range(1, 9)]
circos.par(start_degree=22.5, gap_degree=6)
circos.initialize(sectors, xlim=(0, 1))

# Yang yao is a single solid bar
def add_yang_yao():
    circos.rect(0, 0, 1, 1, col="black")

# Yin yao is a broken bar (two segments)
def add_yin_yao():
    circos.rect(0, 0, 0.45, 1, col="black")
    circos.rect(0.55, 0, 1, 1, col="black")

circos.track(
    ylim=(0, 1), sectors=sectors, bg_border=None, track_height=0.1,
    panel_fun=lambda x, y: add_yang_yao() if CELL_META.sector_numeric_index in {2, 5, 7, 8} else add_yin_yao(),
)
circos.track(
    ylim=(0, 1), sectors=sectors, bg_border=None, track_height=0.1,
    panel_fun=lambda x, y: add_yang_yao() if CELL_META.sector_numeric_index in {1, 6, 7, 8} else add_yin_yao(),
)
circos.track(
    ylim=(0, 1), sectors=sectors, bg_border=None, track_height=0.1,
    panel_fun=lambda x, y: add_yang_yao() if CELL_META.sector_numeric_index in {4, 5, 6, 7} else add_yin_yao(),
)

# Bottom radius of the innermost track
r = float(get_cell_meta_data("cell.bottom.radius")) - 0.1

# Draw Tai-Ji (default draw.sector direction is clockwise)
draw.sector(center=(0, 0), start_degree=90, end_degree=-90, rou1=r, col="black", border="black")
draw.sector(center=(0, 0), start_degree=270, end_degree=90, rou1=r, col="white", border="black")
draw.sector(center=(0, r / 2), start_degree=0, end_degree=360, rou1=r / 2, col="white", border="white")
draw.sector(center=(0, -r / 2), start_degree=0, end_degree=360, rou1=r / 2, col="black", border="black")
draw.sector(center=(0, r / 2), start_degree=0, end_degree=360, rou1=r / 8, col="black", border="black")
draw.sector(center=(0, -r / 2), start_degree=0, end_degree=360, rou1=r / 8, col="white", border="white")

circos.clear()
```

![Ba-Gua and Tai-Ji.](images/ch17_bagua.png)
