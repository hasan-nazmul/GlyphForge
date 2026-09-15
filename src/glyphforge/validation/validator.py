"""Document validator.

Checks the Document IR for structural and semantic issues:
  * Heading hierarchy skips
  * Unmatched math delimiters (detected during parsing)
  * Empty code blocks
  * Malformed tables (inconsistent column counts)
  * Empty document
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from glyphforge.model.blocks import (
    Block,
    BlockQuote,
    CodeBlock,
    DisplayMath,
    Heading,
    List,
    Paragraph,
    Table,
)
from glyphforge.model.document import Document
from glyphforge.model.inlines import InlineMath


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    """A single validation finding."""

    severity: Severity
    message: str
    line: int | None = None  # Line number, if known

    @property
    def symbol(self) -> str:
        if self.severity == Severity.ERROR:
            return "✗"
        if self.severity == Severity.WARNING:
            return "⚠"
        return "ℹ"


@dataclass
class ValidationResult:
    """Aggregate validation result."""

    issues: list[ValidationIssue]

    # Statistics
    heading_count: int = 0
    equation_count: int = 0
    display_math_count: int = 0
    inline_math_count: int = 0
    code_block_count: int = 0
    table_count: int = 0
    list_count: int = 0
    blockquote_count: int = 0

    @property
    def is_valid(self) -> bool:
        """True if no errors were found (warnings are OK)."""
        return not any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == Severity.WARNING for i in self.issues)


def validate(document: Document) -> ValidationResult:
    """Validate a Document IR and return findings."""
    issues: list[ValidationIssue] = []
    stats = _Stats()

    # Validate blocks recursively
    _validate_blocks(document.blocks, issues, stats)

    # Check heading hierarchy
    _check_heading_hierarchy(document.blocks, issues)

    # Check for empty document
    if not document.blocks:
        issues.append(ValidationIssue(Severity.WARNING, "Document is empty"))

    return ValidationResult(
        issues=issues,
        heading_count=stats.headings,
        equation_count=stats.display_math + stats.inline_math,
        display_math_count=stats.display_math,
        inline_math_count=stats.inline_math,
        code_block_count=stats.code_blocks,
        table_count=stats.tables,
        list_count=stats.lists,
        blockquote_count=stats.blockquotes,
    )


class _Stats:
    """Mutable counter for document statistics."""

    def __init__(self) -> None:
        self.headings = 0
        self.display_math = 0
        self.inline_math = 0
        self.code_blocks = 0
        self.tables = 0
        self.lists = 0
        self.blockquotes = 0


def _validate_blocks(blocks: list[Block], issues: list[ValidationIssue], stats: _Stats) -> None:
    """Recursively validate blocks and count statistics."""
    for block in blocks:
        if isinstance(block, Heading):
            stats.headings += 1
            # Count inline math in heading
            for inline in block.children:
                if isinstance(inline, InlineMath):
                    stats.inline_math += 1

        elif isinstance(block, Paragraph):
            for inline in block.children:
                if isinstance(inline, InlineMath):
                    stats.inline_math += 1

        elif isinstance(block, DisplayMath):
            stats.display_math += 1
            if not block.latex.strip():
                issues.append(ValidationIssue(Severity.WARNING, "Empty display math block"))

        elif isinstance(block, CodeBlock):
            stats.code_blocks += 1
            if not block.code.strip():
                issues.append(ValidationIssue(Severity.WARNING, "Empty code block"))

        elif isinstance(block, Table):
            stats.tables += 1
            _validate_table(block, issues, stats)

        elif isinstance(block, List):
            stats.lists += 1
            for item in block.items:
                _validate_blocks(item.children, issues, stats)

        elif isinstance(block, BlockQuote):
            stats.blockquotes += 1
            _validate_blocks(block.children, issues, stats)


def _validate_table(table: Table, issues: list[ValidationIssue], stats: _Stats) -> None:
    """Validate table structure."""
    if not table.headers:
        issues.append(ValidationIssue(Severity.WARNING, "Table has no headers"))
        return

    col_count = len(table.headers)
    for i, row in enumerate(table.rows):
        if len(row) != col_count:
            issues.append(
                ValidationIssue(
                    Severity.WARNING,
                    f"Table row {i + 1} has {len(row)} columns, expected {col_count}",
                )
            )

    # Count inline math in table cells
    for cell in table.headers:
        for inline in cell.children:
            if isinstance(inline, InlineMath):
                stats.inline_math += 1
    for row in table.rows:
        for cell in row:
            for inline in cell.children:
                if isinstance(inline, InlineMath):
                    stats.inline_math += 1


def _check_heading_hierarchy(blocks: list[Block], issues: list[ValidationIssue]) -> None:
    """Check for heading hierarchy skips (e.g. H1 → H3 without H2)."""
    headings = [b for b in blocks if isinstance(b, Heading)]
    for i in range(1, len(headings)):
        prev_level = headings[i - 1].level
        curr_level = headings[i].level
        if curr_level > prev_level + 1:
            skipped = ", ".join(f"H{l}" for l in range(prev_level + 1, curr_level))
            issues.append(
                ValidationIssue(
                    Severity.WARNING,
                    f"Heading hierarchy skips {skipped} (H{prev_level} → H{curr_level})",
                    line=headings[i].source_line,
                )
            )
