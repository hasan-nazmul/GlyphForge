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

            # Check whether this is currency / shell var rather than math
            if _is_currency_or_var(text, i, n):
                i += 1
                continue

            # Attempt inline math $...$
            span = _scan_dollar_inline(text, i, n)
            if span is not None:
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


def _is_currency_or_var(text: str, pos: int, n: int) -> bool:
    """Determine if the ``$`` at *pos* is a currency sign or shell variable.

    Heuristics:
    * ``$`` followed by one or more digits (optionally with ``.`` and more digits),
      then a non-letter → currency.
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
        # After the number, must NOT be a letter that would indicate LaTeX (e.g. $3x$)
        if j >= n or not text[j].isalpha():
            return True
        return False

    # Shell variable: $PATH, $HOME, $TERM (all-uppercase identifiers)
    if next_ch.isupper() or next_ch == "_":
        j = pos + 1
        while j < n and (text[j].isupper() or text[j] == "_" or text[j].isdigit()):
            j += 1
        # Shell vars are all-caps; if followed by lowercase, it's likely math
        if j > pos + 2:  # At least 2 uppercase chars
            if j >= n or not text[j].isalpha():
                return True
    return False
