"""Inline-level AST nodes.

These represent content within a paragraph, heading, table cell, or list item.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Text:
    """Plain text content."""

    content: str

    def __repr__(self) -> str:
        truncated = self.content[:40] + "..." if len(self.content) > 40 else self.content
        return f"Text({truncated!r})"


@dataclass
class Bold:
    """Bold (strong emphasis) content."""

    children: list[Inline] = field(default_factory=list)


@dataclass
class Italic:
    """Italic (emphasis) content."""

    children: list[Inline] = field(default_factory=list)


@dataclass
class Strikethrough:
    """Strikethrough content."""

    children: list[Inline] = field(default_factory=list)


@dataclass
class InlineCode:
    """Inline code span. Content is never modified."""

    code: str


@dataclass
class InlineMath:
    """Inline mathematical expression. LaTeX source is preserved verbatim."""

    latex: str


@dataclass
class Link:
    """Hyperlink."""

    href: str
    children: list[Inline] = field(default_factory=list)
    title: str | None = None


@dataclass
class Image:
    """Inline image reference."""

    src: str
    alt: str = ""
    title: str | None = None


@dataclass
class SoftBreak:
    """Soft line break (typically rendered as a space)."""

    pass


@dataclass
class HardBreak:
    """Hard line break (explicit <br> or trailing spaces)."""

    pass


# Union type for all inline nodes
Inline = (
    Text
    | Bold
    | Italic
    | Strikethrough
    | InlineCode
    | InlineMath
    | Link
    | Image
    | SoftBreak
    | HardBreak
)
