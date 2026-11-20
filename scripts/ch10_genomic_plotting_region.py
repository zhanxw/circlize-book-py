"""Generate figures for Chapter 10: Create plotting regions for genomic data."""

from __future__ import annotations

import numpy as np

from _common import new_figure, save_fig
from circlize_py import circos, generateRandomBed, rand_color


def fig_genomic_links() -> None:
    rng = np.random.default_rng(123)
    bed1 = generateRandomBed(nr=100, seed=123)
    bed1 = bed1.iloc[rng.choice(len(bed1), size=20, replace=False)].reset_index(drop=True)
    bed2 = generateRandomBed(nr=100, seed=124)
    bed2 = bed2.iloc[rng.choice(len(bed2), size=20, replace=False)].reset_index(drop=True)

    fig = new_figure(6.5, 6.5)
    circos.initializeWithIdeogram()
    circos.genomicLink(
        bed1,
        bed2,
        col=rand_color(len(bed1), transparency=0.5, seed=123),
        border=None,
    )
    circos.clear()
    save_fig(fig, "ch10_genomic_links.png")


def main() -> None:
    fig_genomic_links()


if __name__ == "__main__":
    main()
