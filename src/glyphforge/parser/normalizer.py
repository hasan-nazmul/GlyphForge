"""Pass 1 — Protection & Normalization.

This module implements the first pass of the three-pass parser pipeline:

1. Extract and protect fenced code blocks with sentinel placeholders.
2. Extract and protect display math blocks (``$$…$$``, ``\\[…\\]``) with sentinels.
3. Normalize remaining math delimiters (``\\(…\\)`` → ``$…$``) while
   preserving currency and shell variables.

After this pass, the text is safe to feed into markdown-it-py without
risk of LaTeX braces, backslashes, or pipe characters being misinterpreted.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field

from glyphforge.parser.math_lexer import MathKind, MathSpan, scan_math

SENTINEL_PREFIX = "\uE000GLYPH"
SENTINEL_SUFFIX = "\uE001"


@dataclass
class SentinelEntry:
    """A placeholder entry in the sentinel map."""

    sentinel: str
    kind: str  # "code_block", "display_math", "inline_math"
    content: str  # Raw content (code text or LaTeX)
    language: str | None = None  # For code blocks
    info: str = ""  # Full info string for code blocks


@dataclass
class NormalizationResult:
    """Result of Pass 1 normalization."""

    text: str  # The text with sentinels replacing protected regions
    sentinel_map: dict[str, SentinelEntry] = field(default_factory=dict)


# ── Regex for fenced code blocks ─────────────────────────────────────────────
_FENCED_CODE_RE = re.compile(
    r"^(`{3,}|~{3,})([^\n]*)\n(.*?)\n\1[ \t]*$",
    re.MULTILINE | re.DOTALL,
)

# ── Regex for display math blocks ────────────────────────────────────────────
# $$...$$ (possibly multi-line)
_DISPLAY_DOLLAR_RE = re.compile(
    r"\$\$\n?(.*?)\n?\$\$",
    re.DOTALL,
)

# \[...\] (possibly multi-line)
_DISPLAY_BRACKET_RE = re.compile(
    r"\\\[\n?(.*?)\n?\\\]",
    re.DOTALL,
)


def _make_sentinel(kind: str) -> str:
    """Generate a unique sentinel string."""
    uid = uuid.uuid4().hex[:12]
    return f"{SENTINEL_PREFIX}:{kind}:{uid}{SENTINEL_SUFFIX}"


def repair_broken_tables(text: str) -> str:
    """Repair markdown tables where cells or rows are fragmented across multiple lines with blank lines."""
    lines = text.splitlines()
    result: list[str] = []
    i = 0
    in_table = False
    expected_pipes = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for start of a table (header row followed by delimiter row)
        if not in_table and i + 1 < len(lines):
            next_stripped = lines[i + 1].strip()
            if "|" in stripped and re.match(r"^\|?\s*:?-+:?\s*(\|(\s*:?-+:?\s*\|?)+)+$", next_stripped):
                in_table = True
                expected_pipes = stripped.count("|")
                result.append(line)
                result.append(lines[i + 1])
                i += 2
                continue

        if in_table:
            # Table ended if line is a thematic break (---), heading (#), or bold section
            if stripped.startswith("---") or stripped.startswith("#") or re.match(r"^\*\*[^*]+\*\*", stripped):
                in_table = False
                result.append(line)
                i += 1
                continue

            # If line is completely empty, check if subsequent lines continue the table row
            if not stripped:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and (lines[j].strip().startswith("|") or " |" in lines[j]):
                    if result and result[-1].strip().startswith("|") and result[-1].count("|") < expected_pipes:
                        i += 1
                        continue
                in_table = False
                result.append(line)
                i += 1
                continue

            # If current line starts with | or contains |
            if stripped.startswith("|") or ("|" in stripped and result and result[-1].strip().startswith("|")):
                if result and result[-1].strip().startswith("|") and result[-1].count("|") < expected_pipes:
                    prev = result.pop()
                    merged = prev.rstrip() + " " + stripped.lstrip()
                    result.append(merged)
                    i += 1
                    continue
                else:
                    result.append(line)
                    i += 1
                    continue
            else:
                in_table = False
                result.append(line)
                i += 1
                continue
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def normalize(text: str) -> NormalizationResult:
    """Run Pass 1: protect code blocks and math, normalize delimiters.

    Returns a :class:`NormalizationResult` containing the modified text
    and a map from sentinel strings to their original content.
    """
    sentinel_map: dict[str, SentinelEntry] = {}

    # ── Step 0: Repair fragmented tables ──────────────────────────────
    text = repair_broken_tables(text)

    # ── Step 1: Protect fenced code blocks ────────────────────────────
    def _replace_code(match: re.Match[str]) -> str:
        info_string = match.group(2).strip()
        code = match.group(3)
        language = info_string.split()[0] if info_string else None
        sentinel = _make_sentinel("CODE")
        sentinel_map[sentinel] = SentinelEntry(
            sentinel=sentinel,
            kind="code_block",
            content=code,
            language=language,
            info=info_string,
        )
        return f"\n\n{sentinel}\n\n"

    text = _FENCED_CODE_RE.sub(_replace_code, text)

    # ── Step 2: Protect display math blocks ───────────────────────────
    def _replace_display_dollar(match: re.Match[str]) -> str:
        latex = match.group(1).strip()
        sentinel = _make_sentinel("DMATH")
        sentinel_map[sentinel] = SentinelEntry(
            sentinel=sentinel,
            kind="display_math",
            content=latex,
        )
        return sentinel

    text = _DISPLAY_DOLLAR_RE.sub(_replace_display_dollar, text)

    def _replace_display_bracket(match: re.Match[str]) -> str:
        latex = match.group(1).strip()
        sentinel = _make_sentinel("DMATH")
        sentinel_map[sentinel] = SentinelEntry(
            sentinel=sentinel,
            kind="display_math",
            content=latex,
        )
        return sentinel

    text = _DISPLAY_BRACKET_RE.sub(_replace_display_bracket, text)

    # ── Step 3: Scan remaining text for inline math ───────────────────
    # We scan the (already protected) text for remaining $...$ and \(...\)
    math_spans = scan_math(text)

    # Replace inline math spans with sentinels (process in reverse to preserve offsets)
    for span in reversed(math_spans):
        if span.kind == MathKind.INLINE:
            sentinel = _make_sentinel("IMATH")
            sentinel_map[sentinel] = SentinelEntry(
                sentinel=sentinel,
                kind="inline_math",
                content=span.latex,
            )
            text = text[: span.start] + sentinel + text[span.end:]
        elif span.kind == MathKind.DISPLAY:
            # Any remaining display math caught by the scanner (edge cases)
            sentinel = _make_sentinel("DMATH")
            sentinel_map[sentinel] = SentinelEntry(
                sentinel=sentinel,
                kind="display_math",
                content=span.latex,
            )
            text = text[: span.start] + sentinel + text[span.end:]

    return NormalizationResult(text=text, sentinel_map=sentinel_map)
