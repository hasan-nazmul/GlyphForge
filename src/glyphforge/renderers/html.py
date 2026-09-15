"""HTML renderer.

Renders Document IR directly into a standalone, offline-capable HTML5 document.
Includes:
- Standalone HTML5 with <!DOCTYPE html>
- Semantic HTML for all Document IR block and inline nodes
- Pygments syntax highlighting for code blocks
- KaTeX mathematical typography (bundled offline)
- Clean 'technical' theme with CSS variables
- Deterministic heading IDs and Table of Contents
- YAML front matter metadata rendering
"""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound

from glyphforge.model.blocks import (
    Block,
    BlockQuote,
    CodeBlock,
    DisplayMath,
    Heading,
    ImageBlock,
    List,
    ListItem,
    Paragraph,
    Table,
    TableAlignment,
    ThematicBreak,
)
from glyphforge.model.document import Document
from glyphforge.model.inlines import (
    Bold,
    HardBreak,
    Image,
    Inline,
    InlineCode,
    InlineMath,
    Italic,
    Link,
    SoftBreak,
    Strikethrough,
    Text,
)
from glyphforge.renderers.base import BaseRenderer

_ASSETS_DIR = Path(__file__).parent.parent / "assets" / "katex"


class HTMLRenderer(BaseRenderer):
    """Renders Document IR into a standalone, offline HTML document."""

    @property
    def format_name(self) -> str:
        return "HTML"

    @property
    def file_extension(self) -> str:
        return ".html"

    def render(self, document: Document, output_path: Path, **kwargs: Any) -> Path:
        """Render *document* to standalone HTML and write to *output_path*.

        Options
        -------
        toc : bool
            Whether to include a Table of Contents (default: True).
        theme : str
            Theme name (default: 'technical').
        standalone : bool
            Generate a full HTML5 document (default: True).
        """
        toc = kwargs.get("toc", True)
        theme = kwargs.get("theme", "technical")
        standalone = kwargs.get("standalone", True)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy KaTeX fonts alongside if they exist
        fonts_src = _ASSETS_DIR / "fonts"
        fonts_dest = output_path.parent / "fonts"
        if fonts_src.is_dir() and not fonts_dest.exists():
            try:
                shutil.copytree(fonts_src, fonts_dest)
            except Exception:
                pass

        html_content = render_html(
            document=document,
            toc=toc,
            theme=theme,
            standalone=standalone,
        )

        output_path.write_text(html_content, encoding="utf-8")
        return output_path


def render_html(
    document: Document,
    toc: bool = True,
    theme: str = "technical",
    standalone: bool = True,
) -> str:
    """Render a Document IR into an HTML string."""
    builder = _HTMLBuilder(document=document, include_toc=toc, theme=theme)
    body_content = builder.build()

    if not standalone:
        return body_content

    return _wrap_standalone(
        body_content=body_content,
        document=document,
        theme=theme,
    )


class _HTMLBuilder:
    """Walks the Document AST to produce HTML."""

    def __init__(self, document: Document, include_toc: bool = True, theme: str = "technical") -> None:
        self.document = document
        self.include_toc = include_toc
        self.theme = theme
        self._slug_counts: dict[str, int] = {}
        self._heading_id_map: dict[int, str] = {}
        self._headings: list[tuple[int, str, str]] = []  # (level, text, id)
        self._index_headings()

    def _index_headings(self) -> None:
        """Generate deterministic IDs for all headings in AST traversal order."""
        for idx, block in enumerate(self.document.blocks):
            if isinstance(block, Heading):
                plain_text = self._inlines_to_plain_text(block.children)
                slug = _slugify(plain_text)
                count = self._slug_counts.get(slug, 0)
                if count > 0:
                    assigned_id = f"{slug}-{count}"
                else:
                    assigned_id = slug
                self._slug_counts[slug] = count + 1
                self._heading_id_map[idx] = assigned_id
                self._headings.append((block.level, plain_text, assigned_id))

    def build(self) -> str:
        parts: list[str] = []

        # ── Document Header (Front Matter metadata) ───────────────────
        meta = self.document.metadata
        if meta.has_any():
            parts.append(self._render_meta_header(meta))

        # ── Table of Contents ─────────────────────────────────────────
        if self.include_toc and len(self._headings) > 1:
            parts.append(self._render_toc())

        # ── Document Body ─────────────────────────────────────────────
        parts.append('<main class="document-content">')
        for idx, block in enumerate(self.document.blocks):
            parts.append(self._render_block(block, block_index=idx))
        parts.append("</main>")

        return "\n".join(parts)

    def _render_meta_header(self, meta: Any) -> str:
        header_parts = ['<header class="document-header">']
        if meta.title:
            header_parts.append(f'  <h1 class="document-title">{html.escape(meta.title)}</h1>')
        sub_items: list[str] = []
        if meta.author:
            sub_items.append(f'<span class="meta-author">{html.escape(meta.author)}</span>')
        if meta.date:
            sub_items.append(f'<span class="meta-date">{html.escape(str(meta.date))}</span>')
        if meta.subject:
            sub_items.append(f'<span class="meta-subject">{html.escape(meta.subject)}</span>')

        if sub_items:
            header_parts.append(f'  <div class="document-meta">{" &bull; ".join(sub_items)}</div>')

        if meta.tags:
            tag_badges = "".join(
                f'<span class="meta-tag">{html.escape(tag)}</span>' for tag in meta.tags
            )
            header_parts.append(f'  <div class="document-tags">{tag_badges}</div>')

        header_parts.append("</header>")
        return "\n".join(header_parts)

    def _render_toc(self) -> str:
        lines = [
            '<nav class="table-of-contents" aria-label="Table of contents">',
            '  <div class="toc-title">Table of Contents</div>',
            '  <ul class="toc-list">',
        ]
        min_level = min(h[0] for h in self._headings) if self._headings else 1
        for level, text, hid in self._headings:
            indent = "  " * (level - min_level + 2)
            lines.append(
                f'{indent}<li class="toc-item toc-level-{level}">'
                f'<a href="#{hid}">{html.escape(text)}</a></li>'
            )
        lines.append("  </ul>")
        lines.append("</nav>")
        return "\n".join(lines)

    def _render_block(self, block: Block, block_index: int) -> str:
        if isinstance(block, Heading):
            hid = self._heading_id_map.get(block_index, f"heading-{block_index}")
            content = self._render_inlines(block.children)
            return (
                f'<h{block.level} id="{hid}" class="heading">'
                f'{content}'
                f'<a class="heading-anchor" href="#{hid}" aria-hidden="true">#</a>'
                f'</h{block.level}>'
            )

        elif isinstance(block, Paragraph):
            content = self._render_inlines(block.children)
            return f"<p>{content}</p>"

        elif isinstance(block, CodeBlock):
            return self._render_code_block(block)

        elif isinstance(block, DisplayMath):
            # KaTeX display equation with fallback
            escaped_latex = html.escape(block.latex.strip())
            return f'<div class="math-display">\\[{escaped_latex}\\]</div>'

        elif isinstance(block, Table):
            return self._render_table(block)

        elif isinstance(block, List):
            return self._render_list(block)

        elif isinstance(block, BlockQuote):
            inner_blocks = "\n".join(
                self._render_block(child, -1) for child in block.children
            )
            return f"<blockquote>\n{inner_blocks}\n</blockquote>"

        elif isinstance(block, ThematicBreak):
            return "<hr />"

        elif isinstance(block, ImageBlock):
            safe_src = _sanitize_url(block.src)
            alt = html.escape(block.alt)
            caption = f"<figcaption>{html.escape(block.title)}</figcaption>" if block.title else ""
            return f'<figure class="image-block"><img src="{safe_src}" alt="{alt}" />{caption}</figure>'

        return ""

    def _render_code_block(self, block: CodeBlock) -> str:
        code = block.code
        language = (block.language or "").strip().lower()

        # Try syntax highlighting with Pygments
        if language:
            try:
                lexer = get_lexer_by_name(language, stripnl=False)
            except ClassNotFound:
                lexer = TextLexer(stripnl=False)
        else:
            lexer = TextLexer(stripnl=False)

        formatter = HtmlFormatter(nowrap=True)
        highlighted_code = highlight(code, lexer, formatter)

        lang_label = html.escape(language) if language else "text"
        return (
            f'<div class="code-block" data-language="{lang_label}">'
            f'  <div class="code-header">'
            f'    <span class="code-lang">{lang_label}</span>'
            f"  </div>"
            f'  <pre class="highlight"><code>{highlighted_code}</code></pre>'
            f"</div>"
        )

    def _render_table(self, table: Table) -> str:
        lines = ['<div class="table-container">', "  <table>"]

        # Alignments
        align_map = {
            TableAlignment.LEFT: "text-align: left;",
            TableAlignment.CENTER: "text-align: center;",
            TableAlignment.RIGHT: "text-align: right;",
            TableAlignment.NONE: "",
        }

        # Header
        if table.headers:
            lines.append("    <thead>")
            lines.append("      <tr>")
            for col_idx, cell in enumerate(table.headers):
                align_style = ""
                if col_idx < len(table.alignments):
                    style = align_map.get(table.alignments[col_idx], "")
                    if style:
                        align_style = f' style="{style}"'
                content = self._render_inlines(cell.children)
                lines.append(f"        <th{align_style}>{content}</th>")
            lines.append("      </tr>")
            lines.append("    </thead>")

        # Rows
        if table.rows:
            lines.append("    <tbody>")
            for row in table.rows:
                lines.append("      <tr>")
                for col_idx, cell in enumerate(row):
                    align_style = ""
                    if col_idx < len(table.alignments):
                        style = align_map.get(table.alignments[col_idx], "")
                        if style:
                            align_style = f' style="{style}"'
                    content = self._render_inlines(cell.children)
                    lines.append(f"        <td{align_style}>{content}</td>")
                lines.append("      </tr>")
            lines.append("    </tbody>")

        lines.append("  </table>")
        lines.append("</div>")
        return "\n".join(lines)

    def _render_list(self, lst: List) -> str:
        tag = "ol" if lst.ordered else "ul"
        start_attr = f' start="{lst.start}"' if lst.ordered and lst.start != 1 else ""
        lines = [f"<{tag}{start_attr}>"]

        for item in lst.items:
            lines.append(self._render_list_item(item))

        lines.append(f"</{tag}>")
        return "\n".join(lines)

    def _render_list_item(self, item: ListItem) -> str:
        parts: list[str] = []
        if item.checked is not None:
            checked_attr = ' checked=""' if item.checked else ""
            parts.append(
                f'<input type="checkbox" class="task-checkbox" disabled=""{checked_attr}> '
            )

        for child in item.children:
            if isinstance(child, Paragraph):
                parts.append(self._render_inlines(child.children))
            elif isinstance(child, Block):
                parts.append(self._render_block(child, -1))

        content = "\n".join(parts) if len(parts) > 1 else "".join(parts)
        task_class = ' class="task-list-item"' if item.checked is not None else ""
        return f"<li{task_class}>{content}</li>"

    def _render_inlines(self, inlines: list[Inline]) -> str:
        result: list[str] = []
        for inline in inlines:
            result.append(self._render_inline(inline))
        return "".join(result)

    def _render_inline(self, inline: Inline) -> str:
        if isinstance(inline, Text):
            return html.escape(inline.content)

        elif isinstance(inline, Bold):
            return f"<strong>{self._render_inlines(inline.children)}</strong>"

        elif isinstance(inline, Italic):
            return f"<em>{self._render_inlines(inline.children)}</em>"

        elif isinstance(inline, Strikethrough):
            return f"<del>{self._render_inlines(inline.children)}</del>"

        elif isinstance(inline, InlineCode):
            return f"<code>{html.escape(inline.code)}</code>"

        elif isinstance(inline, InlineMath):
            escaped_latex = html.escape(inline.latex.strip())
            return f'<span class="math-inline">\\({escaped_latex}\\)</span>'

        elif isinstance(inline, Link):
            safe_url = _sanitize_url(inline.href)
            title_attr = f' title="{html.escape(inline.title)}"' if inline.title else ""
            text_content = self._render_inlines(inline.children)
            return f'<a href="{safe_url}"{title_attr}>{text_content}</a>'

        elif isinstance(inline, Image):
            safe_src = _sanitize_url(inline.src)
            alt = html.escape(inline.alt)
            title_attr = f' title="{html.escape(inline.title)}"' if inline.title else ""
            return f'<img src="{safe_src}" alt="{alt}"{title_attr} />'

        elif isinstance(inline, SoftBreak):
            return " "

        elif isinstance(inline, HardBreak):
            return "<br />\n"

        return ""

    def _inlines_to_plain_text(self, inlines: list[Inline]) -> str:
        """Extract plain text for slugification and TOC."""
        out: list[str] = []
        for inline in inlines:
            if isinstance(inline, Text):
                out.append(inline.content)
            elif isinstance(inline, (Bold, Italic, Strikethrough, Link)):
                out.append(self._inlines_to_plain_text(inline.children))
            elif isinstance(inline, InlineCode):
                out.append(inline.code)
            elif isinstance(inline, InlineMath):
                out.append(inline.latex)
        return "".join(out)


def _slugify(text: str) -> str:
    """Generate a clean, deterministic anchor ID from text."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip("-")
    return slug or "section"


def _sanitize_url(url: str) -> str:
    """Ensure URLs are safe against XSS (e.g. javascript:)."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme in ("", "http", "https", "mailto", "ftp", "file"):
        return html.escape(url, quote=True)
    return "#unsafe-url"


def _wrap_standalone(body_content: str, document: Document, theme: str) -> str:
    """Wrap rendered body in a complete standalone HTML document with offline assets."""
    title = document.metadata.title or "NoteFlux Document"
    escaped_title = html.escape(title)

    # Metadata tags
    meta_tags: list[str] = []
    if document.metadata.author:
        meta_tags.append(f'<meta name="author" content="{html.escape(document.metadata.author)}" />')
    if document.metadata.date:
        meta_tags.append(f'<meta name="date" content="{html.escape(str(document.metadata.date))}" />')
    if document.metadata.subject:
        meta_tags.append(f'<meta name="subject" content="{html.escape(document.metadata.subject)}" />')
    if document.metadata.tags:
        tags_str = ", ".join(document.metadata.tags)
        meta_tags.append(f'<meta name="keywords" content="{html.escape(tags_str)}" />')
    meta_block = "\n    ".join(meta_tags)
    if meta_block:
        meta_block = "\n    " + meta_block

    # Read offline KaTeX assets if available
    katex_css = ""
    katex_js = ""
    auto_render_js = ""
    try:
        css_file = _ASSETS_DIR / "katex.min.css"
        js_file = _ASSETS_DIR / "katex.min.js"
        auto_file = _ASSETS_DIR / "auto-render.min.js"
        if css_file.exists():
            katex_css = css_file.read_text(encoding="utf-8")
        if js_file.exists():
            katex_js = js_file.read_text(encoding="utf-8")
        if auto_file.exists():
            auto_render_js = auto_file.read_text(encoding="utf-8")
    except Exception:
        pass

    # Pygments theme styles
    pygments_css = HtmlFormatter().get_style_defs(".highlight")

    # Technical Theme CSS
    theme_css = _get_technical_theme_css()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escaped_title}</title>{meta_block}
    <style>
/* ── Theme Styles ────────────────────────────────────────────── */
{theme_css}

/* ── Pygments Syntax Highlighting ────────────────────────────── */
{pygments_css}

/* ── Offline KaTeX Styles ────────────────────────────────────── */
{katex_css}
    </style>
</head>
<body class="theme-{theme}">
    <div class="document-wrapper">
{body_content}
    </div>

    <!-- KaTeX Offline Math Engine -->
    <script>
{katex_js}
    </script>
    <script>
{auto_render_js}
    </script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        if (typeof renderMathInElement === "function") {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "\\\\[", right: "\\\\]", display: true}},
                    {{left: "\\\\(", right: "\\\\)", display: false}},
                    {{left: "$", right: "$", display: false}}
                ],
                throwOnError: false,
                ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
            }});
        }}
    }});
    </script>
</body>
</html>
"""


def _get_technical_theme_css() -> str:
    return """
:root {
    --gf-font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --gf-font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    --gf-font-serif: "Charter", "Bitstream Charter", "Sitka Text", Cambria, Georgia, serif;

    --gf-bg-color: #ffffff;
    --gf-text-color: #1f2328;
    --gf-heading-color: #0d1117;
    --gf-muted-color: #656d76;
    --gf-border-color: #d1d9e0;
    --gf-bg-subtle: #f6f8fa;
    --gf-link-color: #0969da;
    --gf-link-hover: #1a7f37;
    --gf-code-bg: #f6f8fa;
    --gf-math-color: #1f2328;
    --gf-blockquote-border: #0969da;
    --gf-table-stripe: #f8fafc;
    --gf-tag-bg: #eef2f6;
    --gf-tag-text: #24292f;
}

@media (prefers-color-scheme: dark) {
    :root {
        --gf-bg-color: #0d1117;
        --gf-text-color: #e6edf3;
        --gf-heading-color: #ffffff;
        --gf-muted-color: #8b949e;
        --gf-border-color: #30363d;
        --gf-bg-subtle: #161b22;
        --gf-link-color: #4493f8;
        --gf-link-hover: #3fb950;
        --gf-code-bg: #161b22;
        --gf-math-color: #e6edf3;
        --gf-blockquote-border: #4493f8;
        --gf-table-stripe: #161b22;
        --gf-tag-bg: #21262d;
        --gf-tag-text: #c9d1d9;
    }
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: var(--gf-font-sans);
    color: var(--gf-text-color);
    background-color: var(--gf-bg-color);
    line-height: 1.65;
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
}

.document-wrapper {
    max-width: 860px;
    margin: 0 auto;
    padding: 40px 24px 80px 24px;
}

/* ── Header & Metadata ───────────────────────────────────────── */
.document-header {
    border-bottom: 2px solid var(--gf-border-color);
    padding-bottom: 24px;
    margin-bottom: 36px;
}

.document-title {
    font-size: 2.25rem;
    font-weight: 700;
    color: var(--gf-heading-color);
    margin: 0 0 12px 0;
    line-height: 1.25;
}

.document-meta {
    font-size: 0.95rem;
    color: var(--gf-muted-color);
    margin-bottom: 12px;
}

.document-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.meta-tag {
    font-size: 0.8rem;
    padding: 2px 10px;
    border-radius: 12px;
    background: var(--gf-tag-bg);
    color: var(--gf-tag-text);
    border: 1px solid var(--gf-border-color);
}

/* ── Table of Contents ───────────────────────────────────────── */
.table-of-contents {
    background: var(--gf-bg-subtle);
    border: 1px solid var(--gf-border-color);
    border-radius: 6px;
    padding: 16px 20px;
    margin-bottom: 36px;
}

.toc-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 10px;
    color: var(--gf-heading-color);
}

.toc-list {
    list-style: none;
    margin: 0;
    padding: 0;
}

.toc-item {
    margin: 4px 0;
    line-height: 1.4;
}

.toc-item a {
    color: var(--gf-link-color);
    text-decoration: none;
}

.toc-item a:hover {
    text-decoration: underline;
}

.toc-level-1 { font-weight: 600; }
.toc-level-2 { margin-left: 16px; }
.toc-level-3 { margin-left: 32px; font-size: 0.95rem; }
.toc-level-4 { margin-left: 48px; font-size: 0.9rem; }

/* ── Headings ────────────────────────────────────────────────── */
.heading {
    color: var(--gf-heading-color);
    margin-top: 36px;
    margin-bottom: 16px;
    font-weight: 600;
    position: relative;
    scroll-margin-top: 24px;
}

h1.heading {
    font-size: 1.85rem;
    border-bottom: 1px solid var(--gf-border-color);
    padding-bottom: 8px;
}

h2.heading {
    font-size: 1.45rem;
    border-bottom: 1px solid var(--gf-border-color);
    padding-bottom: 6px;
}

h3.heading { font-size: 1.2rem; }
h4.heading { font-size: 1.05rem; }

.heading-anchor {
    margin-left: 8px;
    opacity: 0;
    text-decoration: none;
    color: var(--gf-muted-color);
    font-weight: normal;
    transition: opacity 0.15s ease-in-out;
}

.heading:hover .heading-anchor {
    opacity: 1;
}

/* ── Paragraphs & Text ───────────────────────────────────────── */
p {
    margin: 0 0 16px 0;
}

a {
    color: var(--gf-link-color);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

strong { font-weight: 600; }

code {
    font-family: var(--gf-font-mono);
    font-size: 0.88em;
    padding: 2px 6px;
    background: var(--gf-code-bg);
    border: 1px solid var(--gf-border-color);
    border-radius: 4px;
}

/* ── Code Blocks ─────────────────────────────────────────────── */
.code-block {
    margin: 20px 0;
    border: 1px solid var(--gf-border-color);
    border-radius: 6px;
    overflow: hidden;
    background: var(--gf-code-bg);
}

.code-header {
    display: flex;
    justify-content: flex-end;
    padding: 4px 12px;
    background: var(--gf-bg-subtle);
    border-bottom: 1px solid var(--gf-border-color);
    font-family: var(--gf-font-mono);
    font-size: 0.75rem;
    color: var(--gf-muted-color);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.code-block pre {
    margin: 0;
    padding: 16px;
    overflow-x: auto;
    font-family: var(--gf-font-mono);
    font-size: 0.9rem;
    line-height: 1.5;
}

.code-block code {
    background: none;
    border: none;
    padding: 0;
    font-size: inherit;
}

/* ── Mathematics ─────────────────────────────────────────────── */
.math-display {
    margin: 24px 0;
    padding: 12px 16px;
    overflow-x: auto;
    text-align: center;
    font-size: 1.05rem;
}

.math-inline {
    font-size: 1em;
}

/* ── Tables ──────────────────────────────────────────────────── */
.table-container {
    width: 100%;
    overflow-x: auto;
    margin: 20px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
}

th, td {
    padding: 8px 14px;
    border: 1px solid var(--gf-border-color);
}

th {
    background: var(--gf-bg-subtle);
    font-weight: 600;
}

tbody tr:nth-child(even) {
    background: var(--gf-table-stripe);
}

/* ── Lists ───────────────────────────────────────────────────── */
ul, ol {
    margin: 0 0 16px 0;
    padding-left: 28px;
}

li {
    margin: 4px 0;
}

li > p {
    margin-bottom: 6px;
}

.task-list-item {
    list-style: none;
    margin-left: -20px;
}

.task-checkbox {
    margin-right: 6px;
    vertical-align: middle;
}

/* ── Blockquotes ─────────────────────────────────────────────── */
blockquote {
    margin: 20px 0;
    padding: 12px 20px;
    border-left: 4px solid var(--gf-blockquote-border);
    background: var(--gf-bg-subtle);
    color: var(--gf-muted-color);
    border-radius: 0 6px 6px 0;
}

blockquote > :first-child { margin-top: 0; }
blockquote > :last-child { margin-bottom: 0; }

/* ── Breaks & Media ──────────────────────────────────────────── */
hr {
    border: none;
    border-top: 2px solid var(--gf-border-color);
    margin: 32px 0;
}

.image-block {
    margin: 24px 0;
    text-align: center;
}

.image-block img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
}

figcaption {
    font-size: 0.85rem;
    color: var(--gf-muted-color);
    margin-top: 6px;
}

/* ── Print Styles ────────────────────────────────────────────── */
@media print {
    body {
        font-size: 12pt;
        color: #000;
        background: #fff;
    }
    .document-wrapper {
        max-width: 100%;
        padding: 0;
    }
    .heading-anchor {
        display: none;
    }
    .code-block {
        border: 1px solid #ccc;
        page-break-inside: avoid;
    }
    .math-display {
        page-break-inside: avoid;
    }
    table {
        page-break-inside: avoid;
    }
    h1, h2, h3 {
        page-break-after: avoid;
    }
}
"""
