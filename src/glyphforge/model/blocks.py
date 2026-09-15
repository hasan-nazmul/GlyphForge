"""Block-level AST nodes.

These represent top-level document structure: headings, paragraphs, code blocks,
math blocks, tables, lists, blockquotes, and thematic breaks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from glyphforge.model.inlines import Inline


class TableAlignment(str, Enum):
    """Column alignment for table cells."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    NONE = "none"


@dataclass
class Heading:
    """Section heading (H1–H6)."""

    level: int  # 1–6
    children: list[Inline] = field(default_factory=list)
    source_line: int | None = None


@dataclass
class Paragraph:
    """A paragraph of inline content."""

    children: list[Inline] = field(default_factory=list)


@dataclass
class CodeBlock:
    """Fenced code block. Code content is NEVER modified."""

    code: str
    language: str | None = None
    info: str = ""  # Full info string after language identifier


@dataclass
class DisplayMath:
    """Display (block-level) mathematical expression. LaTeX source is preserved verbatim."""

    latex: str


@dataclass
class TableCell:
    """A single table cell containing inline content."""

    children: list[Inline] = field(default_factory=list)


@dataclass
class Table:
    """A table with headers, rows, and column alignments."""

    headers: list[TableCell] = field(default_factory=list)
    rows: list[list[TableCell]] = field(default_factory=list)
    alignments: list[TableAlignment] = field(default_factory=list)


@dataclass
class ListItem:
    """A list item, which can contain nested blocks (including sub-lists)."""

    children: list[Block] = field(default_factory=list)
    checked: bool | None = None  # None = not a task, True/False = task checkbox


@dataclass
class List:
    """Ordered or unordered list."""

    ordered: bool = False
    start: int = 1  # Starting number for ordered lists
    items: list[ListItem] = field(default_factory=list)


@dataclass
class BlockQuote:
    """Block quotation containing nested blocks."""

    children: list[Block] = field(default_factory=list)


@dataclass
class ThematicBreak:
    """Horizontal rule / thematic break (---)."""

    pass


@dataclass
class ImageBlock:
    """A standalone image (paragraph containing only an image)."""

    src: str
    alt: str = ""
    title: str | None = None


# Union type for all block-level nodes
Block = (
    Heading
    | Paragraph
    | CodeBlock
    | DisplayMath
    | Table
    | List
    | BlockQuote
    | ThematicBreak
    | ImageBlock
)
