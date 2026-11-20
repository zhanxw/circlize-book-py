"""Verify generated book HTML pages, PNG figures, internal links, and search index."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
BOOK_DIR = DOCS_DIR / "book"
ASSETS_DIR = BOOK_DIR / "assets"

EXPECTED_HTML_FILES = [
    "index.html",
    "introduction.html",
    "circular-layout.html",
    "graphics.html",
    "legends.html",
    "high-level-plots.html",
    "circos-heatmap.html",
    "advanced-layout.html",
    "genomic-introduction.html",
    "initialize-genomic-plot.html",
    "genomic-plotting-region.html",
    "modes-of-input.html",
    "high-level-genomic-functions.html",
    "nested-zooming.html",
    "the-chorddiagram-function.html",
    "advanced-usage-of-chorddiagram.html",
    "a-complex-example-of-chord-diagram.html",
    "make-fun-of-the-package.html",
    "gallery.html",
]


class _BookPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.images: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if "id" in attr_map and attr_map["id"]:
            self.ids.add(attr_map["id"])
        if tag == "img" and attr_map.get("src"):
            self.images.append(attr_map["src"] or "")
        if tag == "a" and attr_map.get("href"):
            self.links.append(attr_map["href"] or "")


_SECTION_RE = re.compile(r'<section class="normal markdown-section">(.*?)</section>', re.S)
_TABLE_RE = re.compile(r"<table\b.*?</table>", re.S)


def main() -> None:
    errors: list[str] = []

    for req in (
        DOCS_DIR / ".nojekyll",
        DOCS_DIR / "index.html",
        ASSETS_DIR / "gitbook.css",
        ASSETS_DIR / "gitbook.js",
        ASSETS_DIR / "search_index.json",
    ):
        if not req.exists():
            errors.append(f"Missing required file: {req}")

    page_ids: dict[str, set[str]] = {}
    page_links: dict[str, list[str]] = {}
    referenced_images: set[Path] = set()

    for fname in EXPECTED_HTML_FILES:
        fpath = BOOK_DIR / fname
        if not fpath.exists():
            errors.append(f"Missing HTML chapter page: {fpath}")
            continue
        html_text = fpath.read_text(encoding="utf-8")
        parser = _BookPageParser()
        parser.feed(html_text)
        page_ids[fname] = parser.ids
        page_links[fname] = parser.links

        for src in parser.images:
            if src.startswith(("http://", "https://", "data:")):
                continue
            img_path = (BOOK_DIR / src).resolve()
            if not img_path.exists():
                errors.append(f"{fname}: broken image src {src!r} -> {img_path}")
            else:
                referenced_images.add(img_path)

        sec_m = _SECTION_RE.search(html_text)
        if sec_m:
            sec_body = sec_m.group(1)
            if r"\@ref(" in sec_body or "@ref(fig:" in sec_body:
                errors.append(f"{fname}: leftover bookdown @ref() artifact")
            if "knitr::" in sec_body:
                errors.append(f"{fname}: leftover knitr:: artifact")
            sec_no_tables = _TABLE_RE.sub("", sec_body)
            if "library(circlize)" in sec_no_tables:
                errors.append(f"{fname}: leftover library(circlize) outside comparison tables")

        if fname == "gallery.html":
            n_cards = len(re.findall(r'<div class="gallery-card"', html_text))
            if n_cards < 170:
                errors.append(f"gallery.html: expected >= 170 .gallery-card elements, found {n_cards}")

    for img_path in sorted(referenced_images):
        sz = img_path.stat().st_size
        if sz <= 3000:
            errors.append(f"Image too small ({sz} bytes): {img_path}")
            continue
        try:
            with Image.open(img_path) as im:
                im.verify()
            with Image.open(img_path) as im:
                w, h = im.size
                std = float(np.asarray(im.convert("RGB")).std())
            if w < 200 or h < 150:
                errors.append(f"Image dimensions too small ({w}x{h}): {img_path}")
            elif std <= 2.0:
                errors.append(f"Image appears blank (std={std:.2f}): {img_path}")
        except Exception as exc:
            errors.append(f"Invalid image {img_path}: {exc}")

    all_pngs = sorted((BOOK_DIR / "images").glob("*.png"))
    if not referenced_images:
        errors.append("No PNG images referenced across the entire book!")

    broken_links = 0
    for fname, links in page_links.items():
        for href in links:
            if not href or href.startswith(("http://", "https://", "mailto:", "javascript:")):
                continue
            target_file, frag = urldefrag(href)
            if not target_file:
                target_file = fname
            if target_file not in page_ids:
                errors.append(f"{fname}: broken link target {href!r}")
                broken_links += 1
                continue
            if frag and frag not in page_ids[target_file]:
                errors.append(f"{fname}: broken anchor #{frag} in {target_file} (href={href!r})")
                broken_links += 1

    search_path = ASSETS_DIR / "search_index.json"
    if search_path.exists():
        data = json.loads(search_path.read_text(encoding="utf-8"))
        indexed_pages = {urldefrag(item["url"])[0] for item in data}
        for fname in EXPECTED_HTML_FILES:
            if fname not in indexed_pages:
                errors.append(f"search_index.json missing entries for {fname}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        raise SystemExit(1)

    print(
        f"BOOK VERIFICATION PASSED: {len(EXPECTED_HTML_FILES)}/{len(EXPECTED_HTML_FILES)} chapters, "
        f"{len(referenced_images)} verified PNG figures ({len(all_pngs)} total PNGs on disk), "
        f"{broken_links} broken links."
    )


if __name__ == "__main__":
    main()
