"""Compile chapters/*.md into a GitBook-style static HTML site under docs/book/."""

from __future__ import annotations

import ast
import html
import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name

REPO_ROOT = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = REPO_ROOT / "chapters"
SCRIPTS_DIR = REPO_ROOT / "scripts"
BOOK_DIR = REPO_ROOT / "docs" / "book"
ASSETS_DIR = BOOK_DIR / "assets"

REPO_URL = "https://github.com/zhanxw/circlize-book-py"
LIBRARY_URL = "https://github.com/zhanxw/circlize-py"
BOOK_TITLE = "Circular Visualization in Python"
BOOK_SUBTITLE = "circlize-py Book Edition"

CHAPTERS: list[tuple[str, str, str, str, str | None]] = [
    ("", "index.md", "index.html", "About", None),
    ("1", "01-introduction.md", "introduction.html", "Introduction", "I General Functionality"),
    ("2", "02-circlize-layout.md", "circular-layout.html", "Circular layout", None),
    ("3", "03-graphics.md", "graphics.html", "Graphics", None),
    ("4", "04-legends.md", "legends.html", "Legends", None),
    ("5", "05-implement-high-level-plots.md", "high-level-plots.html", "Implement high-level circular plots", None),
    ("6", "06-circos-heatmap.md", "circos-heatmap.html", "The circos.heatmap() function", None),
    ("7", "07-advanced-usage.md", "advanced-layout.html", "Advanced layout", None),
    ("8", "08-genomics-introduction.md", "genomic-introduction.html", "Introduction", "II Applications in Genomics"),
    ("9", "09-initialize-genomic-data.md", "initialize-genomic-plot.html", "Initialize with genomic data", None),
    ("10", "10-create-plotting-regions.md", "genomic-plotting-region.html", "Create plotting regions for genomic data", None),
    ("11", "11-modes-of-input.md", "modes-of-input.html", "Modes for circos.genomicTrack()", None),
    ("12", "12-high-level-genomic-functions.md", "high-level-genomic-functions.html", "High-level genomic functions", None),
    ("13", "13-nested-zooming.md", "nested-zooming.html", "Nested zooming", None),
    ("14", "14-chord-diagram-simple.md", "the-chorddiagram-function.html", "The chordDiagram() function", "III Visualize Relations"),
    ("15", "15-chord-diagram-advanced-usage.md", "advanced-usage-of-chorddiagram.html", "Advanced usage of chordDiagram()", None),
    ("16", "16-a-complex-example-with-chord-diagram.md", "a-complex-example-of-chord-diagram.html", "A complex example of Chord diagram", None),
    ("17", "17-make-fun.md", "make-fun-of-the-package.html", "Make fun of the package", "IV Others"),
]

PART_DEFS: list[tuple[str, str]] = [
    ("all", "All Parts"),
    ("part0", "About"),
    ("part1", "Part I: General (Ch. 1–7)"),
    ("part2", "Part II: Genomics (Ch. 8–13)"),
    ("part3", "Part III: Chord Diagrams (Ch. 14–16)"),
    ("part4", "Part IV: Fun (Ch. 17)"),
]

KNOWN_APIS: list[str] = [
    "circos.heatmap.initialize",
    "circos.heatmap.link",
    "circos.heatmap.get.x",
    "circos.heatmap",
    "circos.initializeWithIdeogram",
    "circos.initializeCircularGenome",
    "circos.genomicPosTransformLines",
    "circos.genomicTrackPlotRegion",
    "circos.genomicInitialize",
    "circos.genomicIdeogram",
    "circos.genomicHeatmap",
    "circos.genomicLabels",
    "circos.genomicRainfall",
    "circos.genomicDensity",
    "circos.genomicPoints",
    "circos.genomicLines",
    "circos.genomicRect",
    "circos.genomicText",
    "circos.genomicLink",
    "circos.genomicAxis",
    "circos.genomicTrack",
    "circos.nested",
    "circos.trackPlotRegion",
    "circos.updatePlotRegion",
    "circos.initialize",
    "circos.trackHist",
    "circos.trackPoints",
    "circos.trackLines",
    "circos.trackText",
    "circos.dendrogram",
    "circos.barplot",
    "circos.boxplot",
    "circos.violin",
    "circos.arrow",
    "circos.labels",
    "circos.raster",
    "circos.points",
    "circos.lines",
    "circos.segments",
    "circos.polygon",
    "circos.rect",
    "circos.text",
    "circos.axis",
    "circos.yaxis",
    "circos.link",
    "circos.track",
    "circos.update",
    "circos.par",
    "circos.info",
    "chordDiagramFromDataFrame",
    "chordDiagramFromMatrix",
    "chordDiagram",
    "chord_diagram",
    "calc_gap",
    "colorRamp2",
    "color_ramp2",
    "rand_color",
    "add_transparency",
    "highlight.sector",
    "highlight.chromosome",
    "draw.sector",
    "reverse.circlize",
    "circlize",
    "posTransform.text",
    "posTransform.default",
    "genomicDensity",
    "rainfallTransform",
    "generateRandomBed",
    "color_branches",
    "as_dendrogram",
    "hclust_from_data",
    "set_track_gap",
    "load_extdata",
    "read.cytoband",
    "read.chromInfo",
    "CELL_META",
]


@dataclass
class SectionItem:
    level: int
    number: str
    title: str
    anchor: str


@dataclass
class GalleryItem:
    fig_id: str
    badge: str
    chap_num: str
    chap_short: str
    chap_title: str
    html_name: str
    part_key: str
    src: str
    caption: str
    section_label: str
    section_anchor: str
    api_tags: list[str]
    code_raw: str
    code_html: str


@dataclass
class CompiledChapter:
    num: str
    md_name: str
    html_name: str
    title: str
    part_header: str | None
    body_html: str
    sections: list[SectionItem] = field(default_factory=list)
    search_entries: list[dict[str, str]] = field(default_factory=list)
    extra_main_class: str = ""


def _find_pandoc() -> str:
    for candidate in ("/opt/homebrew/bin/pandoc", shutil.which("pandoc")):
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise RuntimeError("pandoc executable not found on system.")


def _strip_part_markers(md_text: str) -> str:
    return re.sub(r"^#\s+\(PART\)\s+.*$", "", md_text, flags=re.MULTILINE)


def _pandoc_to_html(md_text: str, pandoc_bin: str) -> str:
    fmt = (
        "markdown+pipe_tables+backtick_code_blocks+fenced_code_blocks"
        "+header_attributes+auto_identifiers-tex_math_dollars"
    )
    cmd = [pandoc_bin, "-f", fmt, "-t", "html5", "--syntax-highlighting=none"]
    proc = subprocess.run(cmd, input=md_text, text=True, capture_output=True)
    if proc.returncode != 0:
        cmd_fb = [pandoc_bin, "-f", fmt, "-t", "html5", "--no-highlight"]
        proc = subprocess.run(cmd_fb, input=md_text, text=True, capture_output=True, check=True)
    return proc.stdout


_CODE_BLOCK_RE = re.compile(
    r'<pre(?:\s+class="([^"]*)")?><code(?:\s+class="([^"]*)")?>(.*?)</code></pre>',
    re.DOTALL,
)


def _highlight_python(code_raw: str) -> str:
    formatter = HtmlFormatter(nowrap=True)
    try:
        lexer = get_lexer_by_name("python")
    except Exception:
        lexer = TextLexer()
    highlighted = highlight(code_raw, lexer, formatter).rstrip("\n")
    return (
        '<div class="code-wrapper">'
        '<pre class="codehilite"><code>'
        f"{highlighted}"
        "</code></pre></div>"
    )


def _highlight_code_blocks(raw_html: str) -> str:
    formatter = HtmlFormatter(nowrap=True)

    def _repl(match: re.Match[str]) -> str:
        pre_cls = match.group(1) or ""
        code_cls = match.group(2) or ""
        code_raw = html.unescape(match.group(3))

        lang = ""
        for cls in (pre_cls, code_cls):
            for tok in cls.split():
                if tok.startswith("language-"):
                    lang = tok[len("language-"):]
                    break
                elif tok not in ("sourceCode",):
                    lang = tok
                    break
            if lang:
                break

        try:
            lexer = get_lexer_by_name(lang) if lang else TextLexer()
        except Exception:
            lexer = TextLexer()

        highlighted = highlight(code_raw, lexer, formatter).rstrip("\n")
        return (
            '<div class="code-wrapper">'
            '<pre class="codehilite"><code>'
            f"{highlighted}"
            "</code></pre></div>"
        )

    return _CODE_BLOCK_RE.sub(_repl, raw_html)


_HEADING_RE = re.compile(r"<h([1-3])([^>]*)>(.*?)</h\1>", re.DOTALL)
_ATTR_ID_RE = re.compile(r'id="([^"]+)"')
_LEADING_NUM_RE = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+")
_TAG_STRIP_RE = re.compile(r"<[^>]+>")


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    return s or "section"


def _strip_tags(fragment: str) -> str:
    return html.unescape(_TAG_STRIP_RE.sub("", fragment)).strip()


def _process_headings_and_sections(
    body_html: str, chap_num: str, html_name: str, default_title: str
) -> tuple[str, str, list[SectionItem], list[dict[str, str]], list[tuple[int, str, str]]]:
    sections: list[SectionItem] = []
    seen_ids: set[str] = set()
    sec_counters = [0, 0]
    chapter_title = default_title

    matches = list(_HEADING_RE.finditer(body_html))
    chunks_out: list[str] = []
    search_entries: list[dict[str, str]] = []
    last_end = 0

    heading_records: list[tuple[int, int, int, str, str, str]] = []

    for m in matches:
        level = int(m.group(1))
        attrs = m.group(2) or ""
        inner = m.group(3)
        plain = _strip_tags(inner)
        plain_clean = _LEADING_NUM_RE.sub("", plain).strip() or plain

        id_m = _ATTR_ID_RE.search(attrs)
        anchor = id_m.group(1) if id_m else _slugify(plain_clean)
        base_anchor = anchor
        suffix = 2
        while anchor in seen_ids:
            anchor = f"{base_anchor}-{suffix}"
            suffix += 1
        seen_ids.add(anchor)

        num_label = ""
        if level == 1:
            chapter_title = plain_clean
            if chap_num:
                num_label = chap_num
        elif level == 2:
            sec_counters[0] += 1
            sec_counters[1] = 0
            num_label = f"{chap_num}.{sec_counters[0]}" if chap_num else ""
            sections.append(SectionItem(level=2, number=num_label, title=plain_clean, anchor=anchor))
        elif level == 3:
            if sec_counters[0] == 0:
                sec_counters[0] = 1
            sec_counters[1] += 1
            num_label = f"{chap_num}.{sec_counters[0]}.{sec_counters[1]}" if chap_num else ""
            sections.append(SectionItem(level=3, number=num_label, title=plain_clean, anchor=anchor))

        inner_clean = _LEADING_NUM_RE.sub("", inner, count=1) if _LEADING_NUM_RE.match(plain) else inner
        num_span = f'<span class="header-section-number">{html.escape(num_label)}</span> ' if num_label else ""
        anchor_link = f'<a class="anchor-section" aria-label="Anchor link to section" href="#{html.escape(anchor)}">#</a>'
        new_heading = f'<h{level} id="{html.escape(anchor)}">{num_span}{inner_clean}{anchor_link}</h{level}>'

        heading_records.append((m.start(), m.end(), level, num_label, plain_clean, anchor))
        chunks_out.append(body_html[last_end:m.start()])
        chunks_out.append(new_heading)
        last_end = m.end()

    chunks_out.append(body_html[last_end:])
    processed_html = "".join(chunks_out)

    # Track heading start offsets inside processed_html for figure section matching
    processed_headings: list[tuple[int, str, str]] = []
    for hm in _HEADING_RE.finditer(processed_html):
        h_attrs = hm.group(2) or ""
        h_id_m = _ATTR_ID_RE.search(h_attrs)
        h_anchor = h_id_m.group(1) if h_id_m else ""
        h_label = re.sub(r"\s*#\s*$", "", _strip_tags(hm.group(3))).strip()
        processed_headings.append((hm.start(), h_label, h_anchor))

    if not heading_records:
        text_plain = re.sub(r"\s+", " ", _strip_tags(body_html)).strip()
        search_entries.append({
            "url": html_name,
            "title": f"{chap_num} {chapter_title}".strip(),
            "text": text_plain[:4000],
        })
    else:
        for idx, rec in enumerate(heading_records):
            start_pos = rec[1]
            end_pos = heading_records[idx + 1][0] if idx + 1 < len(heading_records) else len(body_html)
            seg_text = re.sub(r"\s+", " ", _strip_tags(body_html[start_pos:end_pos])).strip()
            num_label = rec[3]
            plain_clean = rec[4]
            anchor = rec[5]
            full_title = f"{num_label} {plain_clean}".strip()
            url = html_name if rec[2] == 1 else f"{html_name}#{anchor}"
            search_entries.append({
                "url": url,
                "title": full_title,
                "text": seg_text[:4000],
            })

    return processed_html, chapter_title, sections, search_entries, processed_headings


_PNG_NAME_RE = re.compile(r"(ch[0-9]{2}_[A-Za-z0-9_]+\.png)")
_SAVE_FIG_RE = re.compile(r'save_fig\([^)]*"(ch[0-9]{2}_[A-Za-z0-9_]+\.png)"')


def _slice_single_figure_block(func_src: str, png_name: str) -> str:
    """When a helper function emits multiple PNGs, extract the slice for `png_name`."""
    lines = func_src.splitlines()
    save_indices: list[tuple[int, str]] = []
    for idx, ln in enumerate(lines):
        m = _SAVE_FIG_RE.search(ln)
        if m:
            save_indices.append((idx, m.group(1)))
    if len(save_indices) <= 1:
        return func_src

    target_idx = -1
    prev_save_idx = -1
    for i, (ln_idx, name) in enumerate(save_indices):
        if name == png_name:
            target_idx = ln_idx
            prev_save_idx = save_indices[i - 1][0] if i > 0 else -1
            break
    if target_idx < 0:
        return func_src

    start_idx = prev_save_idx + 1 if prev_save_idx >= 0 else 0
    while start_idx < target_idx and not lines[start_idx].strip():
        start_idx += 1
    sliced = "\n".join(lines[start_idx : target_idx + 1]).strip()
    if prev_save_idx >= 0:
        # Dedent body lines when sliced out of a function body
        import textwrap
        sliced = textwrap.dedent(sliced)
    return sliced or func_src


def _build_script_function_map() -> dict[str, str]:
    """Map each `chXX_*.png` filename to its generating Python function source via AST."""
    mapping: dict[str, str] = {}
    for sc in sorted(SCRIPTS_DIR.glob("ch[0-9][0-9]_*.py")):
        src = sc.read_text(encoding="utf-8")
        tree = ast.parse(src)
        lines = src.splitlines()
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.end_lineno is not None:
                func_src = "\n".join(lines[node.lineno - 1 : node.end_lineno])
                pngs = list(dict.fromkeys(_PNG_NAME_RE.findall(func_src)))
                for png in pngs:
                    if png not in mapping or node.name != "main":
                        mapping[png] = _slice_single_figure_block(func_src, png)
    return mapping


_MD_TOKEN_RE = re.compile(
    r"(^#{1,3}\s+.*$)|(```python\n.*?\n```)|(!\[[^\]]*\]\((images/[^)]+)\))",
    re.MULTILINE | re.DOTALL,
)


def _extract_markdown_figure_code(md_text: str) -> dict[str, str]:
    """Map `images/...` paths in Markdown to their directly preceding Python code block."""
    out: dict[str, str] = {}
    last_code: str | None = None
    for m in _MD_TOKEN_RE.finditer(md_text):
        if m.group(1):
            last_code = None
        elif m.group(2):
            last_code = m.group(2)[len("```python\n") : -len("\n```")].strip()
        elif m.group(3):
            src = m.group(4).strip()
            if last_code:
                out[src] = last_code
            last_code = None
    return out


def _extract_api_tags(code_raw: str, caption: str) -> list[str]:
    """Extract up to 4 representative circlize-py API identifiers from code/caption."""
    tags: list[str] = []
    haystack = f"{code_raw}\n{caption}"
    for api in KNOWN_APIS:
        if api == "circlize" and "circlize_py" in haystack:
            # Avoid false match on `from circlize_py import ...`
            cleaned = re.sub(r"from\s+circlize(?:_py)?\s+import[^\n]*", "", haystack)
            if not re.search(r"\bcirclize\s*\(", cleaned):
                continue
        if api in haystack:
            if not any(api in existing and api != existing for existing in tags):
                tags.append(api)
                if len(tags) >= 4:
                    break
    if not tags:
        # Check snake_case aliases for common calls
        snake_pairs = [
            ("circos_initialize", "circos.initialize"),
            ("circos_track", "circos.track"),
            ("circos_points", "circos.points"),
            ("circos_lines", "circos.lines"),
            ("circos_heatmap", "circos.heatmap"),
            ("circos_genomic", "circos.genomicTrack"),
            ("chord_diagram", "chordDiagram"),
        ]
        for snake, label in snake_pairs:
            if snake in haystack and label not in tags:
                tags.append(label)
                if len(tags) >= 4:
                    break
    return tags or ["circlize-py"]


def _part_key_for_chapter(chap_num: str) -> str:
    if not chap_num:
        return "part0"
    n = int(chap_num)
    if 1 <= n <= 7:
        return "part1"
    if 8 <= n <= 13:
        return "part2"
    if 14 <= n <= 16:
        return "part3"
    return "part4"


_FIGURE_RE = re.compile(
    r"<figure\b[^>]*>\s*<img\s+([^>]*?)/?>\s*(.*?)</figure>",
    re.DOTALL,
)
_ATTR_SRC_RE = re.compile(r'src="([^"]+)"')
_ATTR_ALT_RE = re.compile(r'alt="([^"]*)"')
_FIGCAPTION_RE = re.compile(r"<figcaption\b[^>]*>(.*?)</figcaption>", re.DOTALL)
_REDUNDANT_FIG_PREFIX_RE = re.compile(r"^\s*Figure\s+\d+(?:\.\d+)?[:.\s]+", re.IGNORECASE)


def _process_figures_and_collect(
    body_html: str,
    chap_num: str,
    chap_title: str,
    html_name: str,
    headings: list[tuple[int, str, str]],
    md_code_map: dict[str, str],
    script_fn_map: dict[str, str],
) -> tuple[str, list[GalleryItem]]:
    items: list[GalleryItem] = []
    seen_fig_ids: set[str] = set()
    chunks_out: list[str] = []
    last_end = 0

    part_key = _part_key_for_chapter(chap_num)
    chap_short = "About" if not chap_num else f"Ch. {chap_num}"

    for idx, m in enumerate(_FIGURE_RE.finditer(body_html), start=1):
        img_attrs = m.group(1)
        tail_html = m.group(2)

        src_m = _ATTR_SRC_RE.search(img_attrs)
        src = src_m.group(1) if src_m else ""
        alt_m = _ATTR_ALT_RE.search(img_attrs)
        alt_text = html.unescape(alt_m.group(1)) if alt_m else ""

        cap_m = _FIGCAPTION_RE.search(tail_html)
        raw_cap = _strip_tags(cap_m.group(1)) if cap_m else alt_text
        raw_cap = re.sub(r"\s+", " ", raw_cap).strip()
        caption = _REDUNDANT_FIG_PREFIX_RE.sub("", raw_cap).strip() or raw_cap or Path(src).stem

        base_id = f"fig-{_slugify(Path(src).stem)}"
        fig_id = base_id
        suffix = 2
        while fig_id in seen_fig_ids:
            fig_id = f"{base_id}-{suffix}"
            suffix += 1
        seen_fig_ids.add(fig_id)

        badge = "Fig 0.1" if not chap_num else f"Fig {chap_num}.{idx}"

        sec_label = chap_title
        sec_anchor = headings[0][2] if headings else ""
        for h_pos, h_lbl, h_anc in headings:
            if h_pos <= m.start():
                sec_label = h_lbl
                sec_anchor = h_anc
            else:
                break

        png_name = Path(src).name
        code_raw = md_code_map.get(src) or script_fn_map.get(png_name) or "# See chapter script in scripts/"
        code_html = _highlight_python(code_raw)
        api_tags = _extract_api_tags(code_raw, caption)

        chunks_out.append(body_html[last_end : m.start()])
        chunks_out.append(f'<figure id="{html.escape(fig_id, quote=True)}"><img {img_attrs}/>{tail_html}</figure>')
        last_end = m.end()

        items.append(
            GalleryItem(
                fig_id=fig_id,
                badge=badge,
                chap_num=chap_num or "0",
                chap_short=chap_short,
                chap_title=chap_title,
                html_name=html_name,
                part_key=part_key,
                src=src,
                caption=caption,
                section_label=sec_label,
                section_anchor=sec_anchor,
                api_tags=api_tags,
                code_raw=code_raw,
                code_html=code_html,
            )
        )

    chunks_out.append(body_html[last_end:])
    return "".join(chunks_out), items


def _build_gallery_html(items: list[GalleryItem], compiled_chapters: list[CompiledChapter]) -> str:
    part_counts: dict[str, int] = {"all": len(items)}
    ch_counts: dict[str, int] = {}
    for it in items:
        part_counts[it.part_key] = part_counts.get(it.part_key, 0) + 1
        ch_counts[it.chap_num] = ch_counts.get(it.chap_num, 0) + 1

    part_pills = []
    for pkey, plabel in PART_DEFS:
        cnt = part_counts.get(pkey, 0)
        if pkey != "all" and cnt == 0:
            continue
        cls = "filter-pill active" if pkey == "all" else "filter-pill"
        part_pills.append(
            f'<button type="button" class="{cls}" data-filter-part="{pkey}">'
            f"{html.escape(plabel)} ({cnt})</button>"
        )

    ch_pills = ['<button type="button" class="filter-pill active" data-filter-chapter="all">All Ch.</button>']
    for ch in compiled_chapters:
        cnum = ch.num or "0"
        if ch_counts.get(cnum, 0) == 0:
            continue
        lbl = "About" if cnum == "0" else f"Ch.{cnum}"
        ch_pills.append(
            f'<button type="button" class="filter-pill" data-filter-chapter="{html.escape(cnum)}">'
            f"{html.escape(lbl)}</button>"
        )

    cards_html: list[str] = []
    rows_html: list[str] = []

    for it in items:
        target_href = f"{it.html_name}#{it.fig_id}"
        search_blob = " ".join([
            it.badge,
            it.chap_short,
            it.chap_title,
            it.section_label,
            it.caption,
            Path(it.src).stem.replace("_", " "),
            " ".join(it.api_tags),
        ])
        api_buttons = "".join(
            f'<button type="button" class="api-pill" data-api="{html.escape(tag)}">{html.escape(tag)}</button>'
            for tag in it.api_tags
        )
        sec_display = it.section_label or it.chap_title

        cards_html.append(f"""<div class="gallery-card" data-part="{html.escape(it.part_key)}" data-chapter="{html.escape(it.chap_num)}" data-search="{html.escape(search_blob)}">
  <div class="gallery-card-head">
    <span class="gallery-head-meta">
      <span class="gallery-badge">{html.escape(it.badge)}</span>
      <span class="gallery-ch-label">{html.escape(it.chap_short)}</span>
    </span>
    <a class="gallery-jump-link" href="{html.escape(target_href)}">Go to {html.escape(it.chap_short)} &rarr;</a>
  </div>
  <button type="button" class="gallery-thumb-btn" data-full-src="{html.escape(it.src)}" data-fig-badge="{html.escape(it.badge)}" data-caption="{html.escape(it.caption)}" data-chapter-url="{html.escape(target_href)}" data-chapter-label="{html.escape(it.chap_short)}" aria-label="Zoom {html.escape(it.badge)}: {html.escape(it.caption)}">
    <img src="{html.escape(it.src)}" alt="{html.escape(it.badge)}: {html.escape(it.caption)}" loading="lazy">
  </button>
  <div class="gallery-card-body">
    <p class="gallery-caption">{html.escape(it.caption)}</p>
    <div class="gallery-sec-ref">{html.escape(sec_display)}</div>
    <div class="gallery-api-row">{api_buttons}</div>
  </div>
  <details class="gallery-code-details">
    <summary>Show / Hide Python Code</summary>
    {it.code_html}
  </details>
</div>""")

        api_spans = " ".join(f'<span class="api-pill">{html.escape(tag)}</span>' for tag in it.api_tags)
        rows_html.append(
            f'<tr data-part="{html.escape(it.part_key)}" data-chapter="{html.escape(it.chap_num)}" data-search="{html.escape(search_blob)}">'
            f'<td><a href="{html.escape(target_href)}"><strong>{html.escape(it.badge)}</strong></a></td>'
            f"<td>{html.escape(it.chap_short)}</td>"
            f"<td>{html.escape(sec_display)}</td>"
            f'<td><a href="{html.escape(target_href)}">{html.escape(it.caption)}</a></td>'
            f"<td>{api_spans}</td>"
            "</tr>"
        )

    total = len(items)
    return f"""<h1 id="figure-gallery">Figure Gallery &amp; Master Index<a class="anchor-section" aria-label="Anchor link to section" href="#figure-gallery">#</a></h1>
<p>Browse all <strong>{total} reproducible circular visualization figures</strong> across the book. Filter by book Part, Chapter, keyword, or <code>circlize-py</code> API pill below, click any thumbnail to zoom in, expand the inline Python code, or jump directly to the corresponding section in each chapter.</p>

<div class="gallery-controls">
  <div class="filter-row">
    <span class="filter-label">Part:</span>
    {"".join(part_pills)}
  </div>
  <div class="filter-row">
    <span class="filter-label">Chapter:</span>
    {"".join(ch_pills)}
  </div>
  <div class="gallery-search-row">
    <input id="gallery-search-input" type="search" placeholder="Filter figures by keyword, plot type, or circlize API (e.g. chordDiagram, heatmap, rainfall, ideogram, dendrogram)..." aria-label="Filter gallery figures">
    <span id="gallery-visible-count" class="gallery-visible-count">Showing {total} of {total} figures</span>
    <button id="gallery-toggle-code" type="button" class="gallery-action-btn">Expand All Code</button>
  </div>
</div>

<h2 id="visual-gallery">Visual Figure Gallery<a class="anchor-section" aria-label="Anchor link to section" href="#visual-gallery">#</a></h2>
<div id="gallery-grid" class="gallery-grid">
{"".join(cards_html)}
</div>

<h2 id="master-index">Master Index Table<a class="anchor-section" aria-label="Anchor link to section" href="#master-index">#</a></h2>
<div class="gallery-table-wrap">
  <table id="gallery-index-table" class="gallery-index-table">
    <thead>
      <tr>
        <th>Figure</th>
        <th>Chapter</th>
        <th>Section</th>
        <th>Description</th>
        <th>Key APIs</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows_html)}
    </tbody>
  </table>
</div>

<div id="gallery-lightbox" class="gallery-lightbox" role="dialog" aria-modal="true" aria-labelledby="lightbox-badge" hidden>
  <div class="gallery-lightbox-dialog">
    <div class="gallery-lightbox-head">
      <strong id="lightbox-badge">Figure</strong>
      <div class="gallery-lightbox-actions">
        <button id="lightbox-prev" type="button" class="gallery-lightbox-btn" aria-label="Previous figure">&larr; Prev</button>
        <button id="lightbox-next" type="button" class="gallery-lightbox-btn" aria-label="Next figure">Next &rarr;</button>
        <button id="lightbox-close" type="button" class="gallery-lightbox-btn" aria-label="Close lightbox">&times; Close</button>
      </div>
    </div>
    <div class="gallery-lightbox-media">
      <img id="lightbox-img" alt="Zoomed figure preview">
    </div>
    <div class="gallery-lightbox-foot">
      <span id="lightbox-caption"></span>
      <a id="lightbox-open-chapter" href="index.html" class="gallery-lightbox-btn">Open in Chapter &rarr;</a>
    </div>
  </div>
</div>
"""


def _build_sidebar_html(chapters: list[CompiledChapter], current_html: str) -> str:
    items: list[str] = []
    for ch in chapters:
        if ch.part_header:
            items.append(f'<li class="part"><span>{html.escape(ch.part_header)}</span></li>')
        is_active = ch.html_name == current_html
        cls = "chapter active" if is_active else "chapter"
        num_html = f'<span class="header-section-number">{html.escape(ch.num)}</span>' if ch.num else ""
        sub_html = ""
        if ch.sections:
            lis = []
            for sec in ch.sections:
                sec_cls = f"level-{sec.level}"
                sec_num = f'<span class="header-section-number">{html.escape(sec.number)}</span> ' if sec.number else ""
                lis.append(
                    f'<li class="{sec_cls}"><a href="{html.escape(ch.html_name)}#{html.escape(sec.anchor)}">'
                    f"{sec_num}{html.escape(sec.title)}</a></li>"
                )
            sub_html = "<ul>" + "\n".join(lis) + "</ul>"
        items.append(
            f'<li class="{cls}"><a href="{html.escape(ch.html_name)}">'
            f"{num_html}<span>{html.escape(ch.title)}</span></a>{sub_html}</li>"
        )
    return "\n".join(items)


def _render_page(
    ch: CompiledChapter,
    chapters: list[CompiledChapter],
    prev_ch: CompiledChapter | None,
    next_ch: CompiledChapter | None,
) -> str:
    sidebar_items = _build_sidebar_html(chapters, ch.html_name)
    full_ch_title = f"Chapter {ch.num} {ch.title}" if ch.num.isdigit() else ch.title
    page_title = f"{full_ch_title} | {BOOK_TITLE}"
    main_cls = "page-inner " + ch.extra_main_class if ch.extra_main_class else "page-inner"

    prev_arrow = (
        f'<a href="{html.escape(prev_ch.html_name)}" class="navigation navigation-prev" '
        f'aria-label="Previous chapter: {html.escape(prev_ch.title)}" title="Previous: {html.escape(prev_ch.title)}">&#8249;</a>'
        if prev_ch
        else ""
    )
    next_arrow = (
        f'<a href="{html.escape(next_ch.html_name)}" class="navigation navigation-next" '
        f'aria-label="Next chapter: {html.escape(next_ch.title)}" title="Next: {html.escape(next_ch.title)}">&#8250;</a>'
        if next_ch
        else ""
    )

    prev_btn = (
        f'<a href="{html.escape(prev_ch.html_name)}">&larr; {html.escape((prev_ch.num + " " if prev_ch.num else "") + prev_ch.title)}</a>'
        if prev_ch
        else "<span></span>"
    )
    next_btn = (
        f'<a href="{html.escape(next_ch.html_name)}">{html.escape((next_ch.num + " " if next_ch.num else "") + next_ch.title)} &rarr;</a>'
        if next_ch
        else "<span></span>"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page_title)}</title>
  <meta name="description" content="Python port of Circular Visualization in R using circlize-py.">
  <link rel="stylesheet" href="assets/gitbook.css">
</head>
<body>
  <div class="book">
    <nav class="book-summary" aria-label="Table of Contents">
      <div class="book-summary-header">
        <a class="book-summary-title" href="index.html">{html.escape(BOOK_TITLE)}</a>
        <span class="book-summary-subtitle">{html.escape(BOOK_SUBTITLE)}</span>
      </div>
      <div class="book-search-box">
        <input id="book-search-input" type="search" placeholder="Search book..." aria-label="Search book">
      </div>
      <ul class="summary">
        {sidebar_items}
        <li class="divider"></li>
      </ul>
      <div class="summary-footer">
        <div>Published with <a href="{html.escape(LIBRARY_URL)}" target="_blank" rel="noopener"><strong>circlize-py</strong></a></div>
        <div><a href="{html.escape(REPO_URL)}" target="_blank" rel="noopener">Book Repo</a> &middot; <a href="{html.escape(LIBRARY_URL)}" target="_blank" rel="noopener">circlize-py</a> &middot; <a href="https://jokergoo.github.io/circlize_book/book/" target="_blank" rel="noopener">Original R Book</a></div>
      </div>
    </nav>

    <div class="book-body">
      <header class="book-header">
        <div class="header-left">
          <button id="sidebar-toggle" class="toolbar-btn" type="button" title="Toggle Table of Contents" aria-label="Toggle Table of Contents">&#9776;</button>
          <button id="search-toggle-btn" class="toolbar-btn" type="button" title="Search" aria-label="Search">&#128269;</button>
          <h1 class="header-title"><a href="index.html">{html.escape(BOOK_TITLE)}</a></h1>
        </div>
        <div class="header-right">
          <a class="toolbar-btn" href="gallery.html" title="Browse All Example Figures">Gallery</a>
          <div class="dropdown">
            <button id="font-settings-btn" class="toolbar-btn" type="button" title="Font and Theme Settings" aria-label="Font Settings">A</button>
            <div id="font-settings-menu" class="dropdown-menu">
              <div class="dropdown-row">
                <button id="font-size-dec" type="button">A-</button>
                <button id="font-size-inc" type="button">A+</button>
              </div>
              <div class="dropdown-row">
                <button type="button" data-font="sans">Sans</button>
                <button type="button" data-font="serif">Serif</button>
              </div>
              <div class="dropdown-row">
                <button type="button" data-theme="white">White</button>
                <button type="button" data-theme="sepia">Sepia</button>
                <button type="button" data-theme="night">Night</button>
              </div>
            </div>
          </div>
          <a class="toolbar-btn" href="{html.escape(REPO_URL)}" target="_blank" rel="noopener" title="View on GitHub">GitHub</a>
        </div>
      </header>

      <div class="page-wrapper">
        <main class="{html.escape(main_cls)}">
          <div id="search-results" aria-live="polite"></div>
          <section class="normal markdown-section">
            {ch.body_html}
          </section>
          <nav class="chapter-footer-nav" aria-label="Chapter Navigation">
            {prev_btn}
            {next_btn}
          </nav>
        </main>
        {prev_arrow}
        {next_arrow}
      </div>
    </div>
  </div>
  <script src="assets/gitbook.js"></script>
</body>
</html>
"""


def main() -> None:
    pandoc_bin = _find_pandoc()
    BOOK_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    script_fn_map = _build_script_function_map()
    compiled: list[CompiledChapter] = []
    all_search: list[dict[str, str]] = []
    gallery_items: list[GalleryItem] = []

    for num, md_name, html_name, default_title, part_header in CHAPTERS:
        md_path = CHAPTERS_DIR / md_name
        if not md_path.exists():
            raise FileNotFoundError(f"Missing chapter markdown: {md_path}")
        md_raw = md_path.read_text(encoding="utf-8")
        md_code_map = _extract_markdown_figure_code(md_raw)
        md_text = _strip_part_markers(md_raw)
        raw_html = _pandoc_to_html(md_text, pandoc_bin)
        hl_html = _highlight_code_blocks(raw_html)
        body_html, title, sections, search_entries, processed_headings = _process_headings_and_sections(
            hl_html, num, html_name, default_title
        )
        body_html, ch_gallery_items = _process_figures_and_collect(
            body_html, num, title, html_name, processed_headings, md_code_map, script_fn_map
        )
        gallery_items.extend(ch_gallery_items)
        compiled.append(
            CompiledChapter(
                num=num,
                md_name=md_name,
                html_name=html_name,
                title=title,
                part_header=part_header,
                body_html=body_html,
                sections=sections,
                search_entries=search_entries,
            )
        )
        all_search.extend(search_entries)

    # Append Figure Gallery & Master Index page
    gallery_html_body = _build_gallery_html(gallery_items, compiled)
    gallery_search = [
        {
            "url": "gallery.html#visual-gallery",
            "title": "Figure Gallery - Visual Figure Gallery",
            "text": " ".join(f"{it.badge} {it.caption} {' '.join(it.api_tags)}" for it in gallery_items)[:4000],
        },
        {
            "url": "gallery.html#master-index",
            "title": "Figure Gallery - Master Index Table",
            "text": "Master index table of all example figures, chapters, sections, and circlize-py APIs.",
        },
    ]
    compiled.append(
        CompiledChapter(
            num="★",
            md_name="",
            html_name="gallery.html",
            title="Figure Gallery",
            part_header="Gallery & Index",
            body_html=gallery_html_body,
            sections=[
                SectionItem(2, "", "Visual Figure Gallery", "visual-gallery"),
                SectionItem(2, "", "Master Index Table", "master-index"),
            ],
            search_entries=gallery_search,
            extra_main_class="gallery-page-inner",
        )
    )
    all_search.extend(gallery_search)

    for idx, ch in enumerate(compiled):
        prev_ch = compiled[idx - 1] if idx > 0 else None
        next_ch = compiled[idx + 1] if idx + 1 < len(compiled) else None
        page_html = _render_page(ch, compiled, prev_ch, next_ch)
        out_path = BOOK_DIR / ch.html_name
        out_path.write_text(page_html, encoding="utf-8")

    search_path = ASSETS_DIR / "search_index.json"
    search_path.write_text(json.dumps(all_search, indent=2), encoding="utf-8")
    print(
        f"Built {len(compiled)} book HTML pages ({len(gallery_items)} gallery figures) "
        f"and {len(all_search)} search entries in {BOOK_DIR}"
    )


if __name__ == "__main__":
    main()
