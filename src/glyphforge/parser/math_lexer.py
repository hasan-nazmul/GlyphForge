r"""Character-level math state machine.

This module implements a single-pass, O(n) state machine that scans text and
identifies math spans — both inline (``$...$``, ``\(...\)``) and display
(``$$...$$``, ``\[...\]``) — while correctly ignoring:

* Currency amounts (``$100``, ``$5.99``)
* Shell variables (``$PATH``, ``$HOME``)
* Dollar signs inside code spans (``` `$x` ```)
* Escaped dollar signs (``\$``)

The public API is :func:`scan_math`, which returns a list of :class:`MathSpan`
objects identifying the location and kind of each math expression found.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


class MathKind(Enum):
    INLINE = auto()
    DISPLAY = auto()


@dataclass(frozen=True, slots=True)
class MathSpan:
    """A located math expression in the source text.

    *start* and *end* are byte offsets into the original string.
    The span covers the **delimiters and content** — e.g. for ``$x^2$``
    start points at the first ``$`` and end points one past the final ``$``.
    """

    start: int
    end: int
    kind: MathKind
    latex: str  # The LaTeX content between delimiters (delimiters stripped)


def scan_math(text: str) -> list[MathSpan]:
    """Scan *text* and return all math spans found.

    This is a character-level state machine, not a regex.
    """
    spans: list[MathSpan] = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        # ── Skip code spans ──────────────────────────────────────────
        if ch == "`":
            i = _skip_code_span(text, i, n)
            continue

        # ── Backslash-prefixed delimiters: \( \) \[ \] ───────────────
        if ch == "\\" and i + 1 < n:
            nch = text[i + 1]
            if nch == "(":
                span = _scan_backslash_inline(text, i, n)
                if span is not None:
                    spans.append(span)
                    i = span.end
                    continue
            elif nch == "[":
                span = _scan_backslash_display(text, i, n)
                if span is not None:
                    spans.append(span)
                    i = span.end
                    continue
            elif nch == "$":
                # Escaped dollar — skip both characters
                i += 2
                continue

        # ── Dollar-sign delimiters ────────────────────────────────────
        if ch == "$":
            # Check for display math $$...$$
            if i + 1 < n and text[i + 1] == "$":
                span = _scan_dollar_display(text, i, n)
                if span is not None:
                    spans.append(span)
                    i = span.end
                    continue
                # If no closing found, skip both dollars
                i += 2
                continue

            # Attempt inline math $...$
            span = _scan_dollar_inline(text, i, n)
            if span is not None and _is_valid_inline_math(text, span, n):
                spans.append(span)
                i = span.end
                continue

            # Not matched — move on
            i += 1
            continue

        i += 1

    return spans


# ── Internal scanning helpers ────────────────────────────────────────────────


def _skip_code_span(text: str, start: int, n: int) -> int:
    """Skip past a backtick code span and return the index after its close."""
    # Count opening backticks
    i = start
    ticks = 0
    while i < n and text[i] == "`":
        ticks += 1
        i += 1
    # Find matching closing backticks
    target = "`" * ticks
    close = text.find(target, i)
    if close == -1:
        return n  # Unclosed — skip to end
    return close + ticks


def _scan_backslash_inline(text: str, start: int, n: int) -> MathSpan | None:
    r"""Scan ``\( ... \)``."""
    # start points at '\'
    content_start = start + 2  # skip \(
    j = content_start
    while j < n - 1:
        if text[j] == "\\" and text[j + 1] == ")":
            latex = text[content_start:j]
            if latex.strip():  # Reject empty math
                return MathSpan(start=start, end=j + 2, kind=MathKind.INLINE, latex=latex)
            return None
        j += 1
    return None


def _scan_backslash_display(text: str, start: int, n: int) -> MathSpan | None:
    r"""Scan ``\[ ... \]``."""
    content_start = start + 2
    j = content_start
    while j < n - 1:
        if text[j] == "\\" and text[j + 1] == "]":
            latex = text[content_start:j]
            if latex.strip():
                return MathSpan(start=start, end=j + 2, kind=MathKind.DISPLAY, latex=latex)
            return None
        j += 1
    return None


def _scan_dollar_display(text: str, start: int, n: int) -> MathSpan | None:
    """Scan ``$$ ... $$``."""
    content_start = start + 2
    j = content_start
    while j < n - 1:
        if text[j] == "$" and text[j + 1] == "$":
            # Make sure we are not looking at $$$$ as two empties
            latex = text[content_start:j]
            if latex.strip():
                return MathSpan(start=start, end=j + 2, kind=MathKind.DISPLAY, latex=latex)
            return None
        j += 1
    return None


def _scan_dollar_inline(text: str, start: int, n: int) -> MathSpan | None:
    """Scan ``$...$`` for inline math.

    Inline math must:
    * Not contain unescaped newlines (multi-line → display).
    * Not start with a space immediately after ``$``.
    * Not end with a space immediately before the closing ``$``.
    """
    content_start = start + 1
    if content_start >= n:
        return None

    # Reject leading space
    if text[content_start] == " ":
        return None

    j = content_start
    while j < n:
        ch = text[j]
        if ch == "\n":
            return None  # Multi-line — not inline math
        if ch == "\\" and j + 1 < n and text[j + 1] == "$":
            j += 2  # Skip escaped dollar
            continue
        if ch == "$":
            latex = text[content_start:j]
            # Reject trailing space or empty
            if not latex or latex.endswith(" "):
                return None
            return MathSpan(start=start, end=j + 1, kind=MathKind.INLINE, latex=latex)
        j += 1
    return None


def _is_valid_inline_math(text: str, span: MathSpan, n: int) -> bool:
    """Validate that a scanned $...$ span is genuinely math and not currency/prose/shell-var.

    Handles false positives like:
    * Currency ranges: ``$10-$20`` (span covering ``$10-$``)
    * Multiple currency amounts: ``($10), Option B ($20)``
    * Currency with rate/interval: ``$10/hr-$20/hr``
    * Trailing separators before closing dollar: ``$10,$`` or ``$10;$``
    * Shell variable false matches: ``$FOO:$BAR`` or ``$FOO/$BAR``
    """
    latex = span.latex

    # 1. Pure number in math ($1$, $24$, $100$, $3.14$, $1,000$, $-1$, $+5$)
    #    In LaTeX / Markdown, writing numbers in math mode is standard.
    if re.match(r"^[+-]?\d+([.,]\d+)*$", latex):
        # Ensure the closing $ is not immediately followed by a digit
        # (e.g. $10-$20 where closing $ was actually the $ of $20)
        if span.end < n and text[span.end].isdigit():
            return False
        return True

    # 2. If closing $ is immediately followed by a digit, the closing $ was
    #    likely an opening currency sign of another amount (e.g. $20 in $10-$20)
    if span.end < n and text[span.end].isdigit():
        return False

    # 3. Inline math should not end with trailing punctuation/operators right before $
    if latex.endswith(("-", ",", ";", ":", "/")):
        return False

    # 4. If the span starts with a number (e.g. $10...):
    if re.match(r"^\d", latex):
        # Multiple space-separated English prose words indicate body text, not LaTeX
        if re.search(r"[a-zA-Z]{2,}\s+[a-zA-Z]{2,}", latex):
            return False
        # Unbalanced parentheses indicate cross-boundary matching like ($10), ($20)
        if latex.count("(") != latex.count(")"):
            return False

    # 5. Shell variable false matches like $FOO:$BAR -> latex="FOO:"
    if re.match(r"^[A-Z_][A-Z0-9_]*[/:]$", latex):
        return False

    return True


def _is_currency_or_var(text: str, pos: int, n: int) -> bool:
    """Determine if the ``$`` at *pos* is a currency sign or shell variable.

    Heuristics:
    * ``$`` followed by one or more digits (optionally with ``.`` and more digits),
      then a non-letter → currency, UNLESS followed by a closing ``$`` (math like ``$1$``, ``$24$``).
    * ``$`` followed by an uppercase letter sequence resembling a shell variable
      name (e.g. ``$PATH``, ``$HOME``), then a non-alnum boundary → shell variable.
    """
    if pos + 1 >= n:
        return False

    next_ch = text[pos + 1]

    # Currency: $100, $5.99, $3,000
    if next_ch.isdigit():
        j = pos + 2
        while j < n and (text[j].isdigit() or text[j] in ".,"):
            j += 1
        # If immediately closed by $, it's inline math ($1$, $24$, $100$)
        if j < n and text[j] == "$":
            return False
        # After the number, must NOT be a letter that would indicate LaTeX (e.g. $3x$)
        if j >= n or not text[j].isalpha():
            return True
        return False

    # Shell variable: $PATH, $HOME, $TERM (all-uppercase identifiers)
    if next_ch.isupper() or next_ch == "_":
        j = pos + 1
        while j < n and (text[j].isupper() or text[j] == "_" or text[j].isdigit()):
            j += 1
        if j < n and text[j] == "$":
            return False
        # Shell vars are all-caps; if followed by lowercase, it's likely math
        if j > pos + 2:  # At least 2 uppercase chars
            if j >= n or not text[j].isalpha():
                return True
    return False
