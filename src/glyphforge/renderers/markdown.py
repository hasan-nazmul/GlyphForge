"""Canonical Markdown renderer.

Serializes the Document IR back into clean, deterministic, Git-friendly Markdown.
This is the source-of-truth output — it is always generated first, and all
other renderers (HTML, PDF, DOCX) can consume it as input.

Design goals:
  * Readable and manually editable
  * Deterministic: same AST always produces the same text
  * Idempotent: rendering the output of a previous render produces identical text
  * Git-friendly: minimal diff noise
"""

from __future__ import annotations

from pathlib import Path

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
    ThematicBreak,
)
from glyphforge.model.document import Document
from glyphforge.model.inlines import (
    Bold,
    HardBreak,
    Inline,
    InlineCode,
    InlineMath,
    Italic,
    Link,
    Image,
    SoftBreak,
    Strikethrough,
    Text,
)
from glyphforge.renderers.base import BaseRenderer


class MarkdownRenderer(BaseRenderer):
    """Render a Document IR into canonical Markdown."""

    @property
    def format_name(self) -> str:
        return "Markdown"

    @property
    def file_extension(self) -> str:
        return ".md"

    def render(self, document: Document, output_path: Path, **kwargs: Any) -> Path:
        """Render *document* to canonical Markdown and write to *output_path*."""
        text = render_markdown(document)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        return output_path


def render_markdown(document: Document) -> str:
    """Render *document* to a canonical Markdown string."""
    parts: list[str] = []

    # ── Front matter ──────────────────────────────────────────────────
    if document.metadata.has_any():
        parts.append(_render_frontmatter(document))
        parts.append("")

    # ── Blocks ────────────────────────────────────────────────────────
    for i, block in enumerate(document.blocks):
        text = _render_block(block, indent="")
        parts.append(text)
        # Add blank line between blocks (except the very last)
        if i < len(document.blocks) - 1:
            parts.append("")

    # Ensure trailing newline
    result = "\n".join(parts)
    if not result.endswith("\n"):
        result += "\n"
    return result


def _render_frontmatter(document: Document) -> str:
    """Render YAML front matter block."""
    meta = document.metadata
    lines = ["---"]
    if meta.title:
        lines.append(f"title: {meta.title}")
    if meta.author:
        lines.append(f"author: {meta.author}")
    if meta.date:
        lines.append(f"date: {meta.date}")
    if meta.subject:
        lines.append(f"subject: {meta.subject}")
    if meta.tags:
        lines.append("tags:")
        for tag in meta.tags:
            lines.append(f"  - {tag}")
    lines.append("---")
    return "\n".join(lines)


def _render_block(block: Block, indent: str = "") -> str:
    """Render a single block-level node."""
    if isinstance(block, Heading):
        prefix = "#" * block.level
        content = _render_inlines(block.children)
        return f"{indent}{prefix} {content}"

    if isinstance(block, Paragraph):
        content = _render_inlines(block.children)
        return f"{indent}{content}"

    if isinstance(block, CodeBlock):
        lang = block.language or ""
        info = block.info if block.info and block.info != lang else lang
        fence = "```"
        # Use ~~~~ if code contains ```
        if "```" in block.code:
            fence = "~~~~"
        lines = [f"{indent}{fence}{info}"]
        for line in block.code.split("\n"):
            lines.append(f"{indent}{line}")
        lines.append(f"{indent}{fence}")
        return "\n".join(lines)

    if isinstance(block, DisplayMath):
        lines = [f"{indent}$$"]
        for line in block.latex.split("\n"):
            lines.append(f"{indent}{line}")
        lines.append(f"{indent}$$")
        return "\n".join(lines)

    if isinstance(block, Table):
        return _render_table(block, indent)

    if isinstance(block, List):
        return _render_list(block, indent)

    if isinstance(block, BlockQuote):
        inner_parts: list[str] = []
        for child in block.children:
            rendered = _render_block(child, indent="")
            inner_parts.append(rendered)
        inner_text = "\n\n".join(inner_parts)
        # Prefix each line with "> "
        quoted = "\n".join(f"{indent}> {line}" for line in inner_text.split("\n"))
        return quoted

    if isinstance(block, ThematicBreak):
        return f"{indent}---"

    if isinstance(block, ImageBlock):
        title_part = f' "{block.title}"' if block.title else ""
        return f"{indent}![{block.alt}]({block.src}{title_part})"

    return ""


def _render_inlines(inlines: list[Inline]) -> str:
    """Render a list of inline nodes into a string."""
    parts: list[str] = []
    for node in inlines:
        parts.append(_render_inline(node))
    return "".join(parts)


def _render_inline(node: Inline) -> str:
    """Render a single inline node."""
    if isinstance(node, Text):
        return node.content

    if isinstance(node, Bold):
        return f"**{_render_inlines(node.children)}**"

    if isinstance(node, Italic):
        return f"*{_render_inlines(node.children)}*"

    if isinstance(node, Strikethrough):
        return f"~~{_render_inlines(node.children)}~~"

    if isinstance(node, InlineCode):
        # Use double backticks if code contains a single backtick
        if "`" in node.code:
            return f"`` {node.code} ``"
        return f"`{node.code}`"

    if isinstance(node, InlineMath):
        return f"${node.latex}$"

    if isinstance(node, Link):
        text = _render_inlines(node.children)
        if node.title:
            return f'[{text}]({node.href} "{node.title}")'
        return f"[{text}]({node.href})"

    if isinstance(node, Image):
        title_part = f' "{node.title}"' if node.title else ""
        return f"![{node.alt}]({node.src}{title_part})"

    if isinstance(node, SoftBreak):
        return "\n"

    if isinstance(node, HardBreak):
        return "  \n"

    return ""


def _render_table(table: Table, indent: str) -> str:
    """Render a pipe table."""
    lines: list[str] = []

    # Header row
    header_cells = [_render_inlines(cell.children) for cell in table.headers]
    lines.append(f"{indent}| {' | '.join(header_cells)} |")

    # Separator row
    separators: list[str] = []
    for i, alignment in enumerate(table.alignments):
        if alignment.value == "center":
            separators.append(":---:")
        elif alignment.value == "right":
            separators.append("---:")
        elif alignment.value == "left":
            separators.append(":---")
        else:
            separators.append("---")
    lines.append(f"{indent}| {' | '.join(separators)} |")

    # Data rows
    for row in table.rows:
        cells = [_render_inlines(cell.children) for cell in row]
        lines.append(f"{indent}| {' | '.join(cells)} |")

    return "\n".join(lines)


def _render_list(list_node: List, indent: str) -> str:
    """Render an ordered or unordered list."""
    lines: list[str] = []
    for idx, item in enumerate(list_node.items):
        if list_node.ordered:
            marker = f"{list_node.start + idx}."
        else:
            marker = "-"

        item_lines = _render_list_item(item, marker, indent)
        lines.extend(item_lines)

    return "\n".join(lines)


def _render_list_item(item: ListItem, marker: str, indent: str) -> list[str]:
    """Render a single list item, handling nested content."""
    lines: list[str] = []
    continuation_indent = indent + " " * (len(marker) + 1)

    for i, child in enumerate(item.children):
        rendered = _render_block(child, indent="")
        child_lines = rendered.split("\n")

        if i == 0:
            # First block gets the marker
            lines.append(f"{indent}{marker} {child_lines[0]}")
            for cl in child_lines[1:]:
                lines.append(f"{continuation_indent}{cl}")
        else:
            # Subsequent blocks are indented
            for cl in child_lines:
                lines.append(f"{continuation_indent}{cl}")

    return lines
