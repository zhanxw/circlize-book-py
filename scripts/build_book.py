"""Compile chapters/*.md into a GitBook-style static HTML site under docs/book/."""

from __future__ import annotations

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
BOOK_DIR = REPO_ROOT / "docs" / "book"
ASSETS_DIR = BOOK_DIR / "assets"

REPO_URL = "https://github.com/zhanxw/circlize-book-py"
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


@dataclass
class SectionItem:
    level: int
    number: str
    title: str
    anchor: str


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
) -> tuple[str, str, list[SectionItem], list[dict[str, str]]]:
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

    return processed_html, chapter_title, sections, search_entries


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
    full_ch_title = f"Chapter {ch.num} {ch.title}" if ch.num else ch.title
    page_title = f"{full_ch_title} | {BOOK_TITLE}"

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
        <div>Published with <strong>circlize-py</strong></div>
        <div><a href="{html.escape(REPO_URL)}" target="_blank" rel="noopener">GitHub Repository</a> &middot; <a href="https://jokergoo.github.io/circlize_book/book/" target="_blank" rel="noopener">Original R Book</a></div>
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
        <main class="page-inner">
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

    compiled: list[CompiledChapter] = []
    all_search: list[dict[str, str]] = []

    for num, md_name, html_name, default_title, part_header in CHAPTERS:
        md_path = CHAPTERS_DIR / md_name
        if not md_path.exists():
            raise FileNotFoundError(f"Missing chapter markdown: {md_path}")
        md_text = _strip_part_markers(md_path.read_text(encoding="utf-8"))
        raw_html = _pandoc_to_html(md_text, pandoc_bin)
        hl_html = _highlight_code_blocks(raw_html)
        body_html, title, sections, search_entries = _process_headings_and_sections(
            hl_html, num, html_name, default_title
        )
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

    for idx, ch in enumerate(compiled):
        prev_ch = compiled[idx - 1] if idx > 0 else None
        next_ch = compiled[idx + 1] if idx + 1 < len(compiled) else None
        page_html = _render_page(ch, compiled, prev_ch, next_ch)
        out_path = BOOK_DIR / ch.html_name
        out_path.write_text(page_html, encoding="utf-8")

    search_path = ASSETS_DIR / "search_index.json"
    search_path.write_text(json.dumps(all_search, indent=2), encoding="utf-8")
    print(f"Built {len(compiled)} book HTML pages and {len(all_search)} search entries in {BOOK_DIR}")


if __name__ == "__main__":
    main()
