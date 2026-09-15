"""Table parsing helpers.

Provides utilities for parsing Markdown pipe tables, including tables
containing inline math, bold text, code spans, and escaped pipes.
"""

from __future__ import annotations

import re

from glyphforge.model.blocks import Table, TableAlignment, TableCell
from glyphforge.model.inlines import Inline


def parse_alignment(separator_row: str) -> list[TableAlignment]:
    """Parse the separator row of a pipe table and return column alignments.

    Example separator rows:
        ``|---|---|``     → [NONE, NONE]
        ``|:---|---:|``   → [LEFT, RIGHT]
        ``|:---:|---|``   → [CENTER, NONE]
    """
    cells = _split_table_row(separator_row)
    alignments: list[TableAlignment] = []
    for cell in cells:
        cell = cell.strip()
        left = cell.startswith(":")
        right = cell.endswith(":")
        if left and right:
            alignments.append(TableAlignment.CENTER)
        elif left:
            alignments.append(TableAlignment.LEFT)
        elif right:
            alignments.append(TableAlignment.RIGHT)
        else:
            alignments.append(TableAlignment.NONE)
    return alignments


def _split_table_row(row: str) -> list[str]:
    """Split a pipe-table row into cells, respecting escaped pipes.

    Handles:
    - Leading and trailing pipe characters
    - Escaped pipes (``\\|``) within cells
    - Code spans containing pipes
    """
    # Strip leading/trailing pipes and whitespace
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]

    cells: list[str] = []
    current: list[str] = []
    i = 0
    in_code = False

    while i < len(row):
        ch = row[i]

        if ch == "`" and not in_code:
            in_code = True
            current.append(ch)
        elif ch == "`" and in_code:
            in_code = False
            current.append(ch)
        elif ch == "\\" and i + 1 < len(row) and row[i + 1] == "|":
            current.append("|")
            i += 1
        elif ch == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
        i += 1

    # Append the last cell
    cells.append("".join(current).strip())
    return cells


_SEPARATOR_RE = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")


def is_separator_row(line: str) -> bool:
    """Return True if *line* is a table separator row (e.g. ``|---|---|``)."""
    return bool(_SEPARATOR_RE.match(line.strip()))
