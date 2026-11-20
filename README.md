# Circular Visualization in Python (`circlize-py`)

Complete Python port of Zuguang Gu's [*Circular Visualization in R*](https://jokergoo.github.io/circlize_book/book/) book, built with [**`circlize-py`**](https://github.com/zhanxw/circlize-py).

- **Read the Live Book (GitHub Pages)**: [https://zhanxw.github.io/circlize-book-py/book/](https://zhanxw.github.io/circlize-book-py/book/)
- **Browse All 173 Figures (Gallery)**: [https://zhanxw.github.io/circlize-book-py/book/gallery.html](https://zhanxw.github.io/circlize-book-py/book/gallery.html)
- **Python Library**: [https://github.com/zhanxw/circlize-py](https://github.com/zhanxw/circlize-py)
- **Original R Book**: [jokergoo.github.io/circlize_book/book/](https://jokergoo.github.io/circlize_book/book/)

---

## Table of Contents

| Chapter | Markdown Source | Figure Script | Live HTML Chapter |
|---|---|---|---|
| **About** | [chapters/index.md](chapters/index.md) | [scripts/ch00_about.py](scripts/ch00_about.py) | [index.html](https://zhanxw.github.io/circlize-book-py/book/index.html) |
| **1. Introduction** | [chapters/01-introduction.md](chapters/01-introduction.md) | [scripts/ch01_introduction.py](scripts/ch01_introduction.py) | [introduction.html](https://zhanxw.github.io/circlize-book-py/book/introduction.html) |
| **2. Circular layout** | [chapters/02-circlize-layout.md](chapters/02-circlize-layout.md) | [scripts/ch02_circlize_layout.py](scripts/ch02_circlize_layout.py) | [circular-layout.html](https://zhanxw.github.io/circlize-book-py/book/circular-layout.html) |
| **3. Graphics** | [chapters/03-graphics.md](chapters/03-graphics.md) | [scripts/ch03_graphics.py](scripts/ch03_graphics.py) | [graphics.html](https://zhanxw.github.io/circlize-book-py/book/graphics.html) |
| **4. Legends** | [chapters/04-legends.md](chapters/04-legends.md) | [scripts/ch04_legends.py](scripts/ch04_legends.py) | [legends.html](https://zhanxw.github.io/circlize-book-py/book/legends.html) |
| **5. Implement high-level circular plots** | [chapters/05-implement-high-level-plots.md](chapters/05-implement-high-level-plots.md) | [scripts/ch05_high_level_plots.py](scripts/ch05_high_level_plots.py) | [high-level-plots.html](https://zhanxw.github.io/circlize-book-py/book/high-level-plots.html) |
| **6. The `circos.heatmap()` function** | [chapters/06-circos-heatmap.md](chapters/06-circos-heatmap.md) | [scripts/ch06_circos_heatmap.py](scripts/ch06_circos_heatmap.py) | [circos-heatmap.html](https://zhanxw.github.io/circlize-book-py/book/circos-heatmap.html) |
| **7. Advanced layout** | [chapters/07-advanced-usage.md](chapters/07-advanced-usage.md) | [scripts/ch07_advanced_layout.py](scripts/ch07_advanced_layout.py) | [advanced-layout.html](https://zhanxw.github.io/circlize-book-py/book/advanced-layout.html) |
| **8. Genomics Introduction** | [chapters/08-genomics-introduction.md](chapters/08-genomics-introduction.md) | — | [genomic-introduction.html](https://zhanxw.github.io/circlize-book-py/book/genomic-introduction.html) |
| **9. Initialize with genomic data** | [chapters/09-initialize-genomic-data.md](chapters/09-initialize-genomic-data.md) | [scripts/ch09_initialize_genomic.py](scripts/ch09_initialize_genomic.py) | [initialize-genomic-plot.html](https://zhanxw.github.io/circlize-book-py/book/initialize-genomic-plot.html) |
| **10. Create plotting regions for genomic data** | [chapters/10-create-plotting-regions.md](chapters/10-create-plotting-regions.md) | [scripts/ch10_genomic_plotting_region.py](scripts/ch10_genomic_plotting_region.py) | [genomic-plotting-region.html](https://zhanxw.github.io/circlize-book-py/book/genomic-plotting-region.html) |
| **11. Modes for `circos.genomicTrack()`** | [chapters/11-modes-of-input.md](chapters/11-modes-of-input.md) | [scripts/ch11_modes_of_input.py](scripts/ch11_modes_of_input.py) | [modes-of-input.html](https://zhanxw.github.io/circlize-book-py/book/modes-of-input.html) |
| **12. High-level genomic functions** | [chapters/12-high-level-genomic-functions.md](chapters/12-high-level-genomic-functions.md) | [scripts/ch12_high_level_genomic.py](scripts/ch12_high_level_genomic.py) | [high-level-genomic-functions.html](https://zhanxw.github.io/circlize-book-py/book/high-level-genomic-functions.html) |
| **13. Nested zooming** | [chapters/13-nested-zooming.md](chapters/13-nested-zooming.md) | [scripts/ch13_nested_zooming.py](scripts/ch13_nested_zooming.py) | [nested-zooming.html](https://zhanxw.github.io/circlize-book-py/book/nested-zooming.html) |
| **14. The `chordDiagram()` function** | [chapters/14-chord-diagram-simple.md](chapters/14-chord-diagram-simple.md) | [scripts/ch14_chord_diagram_simple.py](scripts/ch14_chord_diagram_simple.py) | [the-chorddiagram-function.html](https://zhanxw.github.io/circlize-book-py/book/the-chorddiagram-function.html) |
| **15. Advanced usage of `chordDiagram()`** | [chapters/15-chord-diagram-advanced-usage.md](chapters/15-chord-diagram-advanced-usage.md) | [scripts/ch15_chord_diagram_advanced.py](scripts/ch15_chord_diagram_advanced.py) | [advanced-usage-of-chorddiagram.html](https://zhanxw.github.io/circlize-book-py/book/advanced-usage-of-chorddiagram.html) |
| **16. A complex example of Chord diagram** | [chapters/16-a-complex-example-with-chord-diagram.md](chapters/16-a-complex-example-with-chord-diagram.md) | [scripts/ch16_complex_chord_diagram.py](scripts/ch16_complex_chord_diagram.py) | [a-complex-example-of-chord-diagram.html](https://zhanxw.github.io/circlize-book-py/book/a-complex-example-of-chord-diagram.html) |
| **17. Make fun of the package** | [chapters/17-make-fun.md](chapters/17-make-fun.md) | [scripts/ch17_make_fun.py](scripts/ch17_make_fun.py) | [make-fun-of-the-package.html](https://zhanxw.github.io/circlize-book-py/book/make-fun-of-the-package.html) |
| **★ Figure Gallery & Index** | *(generated by [scripts/build_book.py](scripts/build_book.py))* | — | [gallery.html](https://zhanxw.github.io/circlize-book-py/book/gallery.html) |

---

## Reproducing the Book Locally

### Prerequisites

- Python `>= 3.10` with `circlize-py` (`numpy`, `pandas`, `scipy`, `matplotlib`, `pillow`)
- `pygments` (syntax highlighting) and `pandoc` (Markdown-to-HTML compilation)

```bash
pip install "git+https://github.com/zhanxw/circlize-py.git" pygments
```

### Build Figures, Compile HTML, and Verify

```bash
# 1. Regenerate all PNG figures into docs/book/images/
python scripts/build_all_figures.py

# 2. Compile chapters/*.md and gallery.html into the GitBook static HTML site under docs/book/
python scripts/build_book.py

# 3. Verify all 19 HTML pages, PNG figures, anchors, links, and search index
python scripts/verify_book.py
```

---

## Attribution & Citation

This book is a Python port of the original R book **Circular Visualization in R** by **Zuguang Gu** ([jokergoo/circlize_book](https://github.com/jokergoo/circlize_book)).

If you use **circlize** or **circlize-py** in your research, please cite:

> Gu, Z., Gu, L., Eils, R., Schlesner, M., & Brors, B. (2014). *circlize* implements and enhances circular visualization in R. *Bioinformatics*, 30(19), 2811–2812. DOI: [10.1093/bioinformatics/btu393](https://doi.org/10.1093/bioinformatics/btu393)

Released under the [MIT License](LICENSE).
