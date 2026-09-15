"""Document and Metadata models — the top-level IR container."""

from __future__ import annotations

from dataclasses import dataclass, field

from glyphforge.model.blocks import Block


@dataclass
class Metadata:
    """Document metadata extracted from YAML front matter."""

    title: str | None = None
    author: str | None = None
    date: str | None = None
    subject: str | None = None
    tags: list[str] = field(default_factory=list)
    raw_frontmatter: str | None = None  # Preserved verbatim for round-trip fidelity

    def has_any(self) -> bool:
        """Return True if any metadata field is populated."""
        return bool(self.title or self.author or self.date or self.subject or self.tags)


@dataclass
class Document:
    """The root of the document IR tree.

    A Document is the result of parsing raw input.  It contains:
    - metadata: optional YAML front matter
    - blocks: ordered list of block-level AST nodes
    """

    metadata: Metadata = field(default_factory=Metadata)
    blocks: list[Block] = field(default_factory=list)
    source_path: str | None = None  # Original file path, if known

    # ── Statistics helpers ────────────────────────────────────────────
    def count_by_type(self, block_type: type) -> int:
        """Count top-level blocks of a given type."""
        return sum(1 for b in self.blocks if isinstance(b, block_type))
