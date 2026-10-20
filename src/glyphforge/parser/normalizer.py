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


def _is_table_delimiter_row(s: str) -> bool:
    clean = re.sub(r"^>\s*", "", s).strip()
    return bool(re.match(r"^\|?\s*:?-+:?\s*(\|(\s*:?-+:?\s*\|?)+)+$", clean))


def _is_row_complete(row: str, expected_cols: int, has_outer_pipes: bool) -> bool:
    s = re.sub(r"^>\s*", "", row).strip()
    if has_outer_pipes and not (s.startswith("|") and s.endswith("|") and len(s) > 1):
        return False
    core = s.strip("|")
    cells = re.split(r"(?<!\\)\|", core)
    return len(cells) >= expected_cols


def repair_broken_tables(text: str) -> str:
    """Repair markdown tables where cells or rows are fragmented across multiple lines with blank lines."""
    lines = text.splitlines()
    result: list[str] = []
    i = 0
    in_table = False
    expected_cols = 0
    has_outer_pipes = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for start of a table (look ahead past blank or solitary pipe lines)
        if not in_table and "|" in stripped:
            k = i + 1
            while k < len(lines) and (not lines[k].strip() or lines[k].strip() in ("|", " |", "\\|")):
                k += 1
            if k < len(lines) and _is_table_delimiter_row(lines[k].strip()):
                in_table = True
                delim_line = lines[k].strip()
                clean_delim = re.sub(r"^>\s*", "", delim_line).strip("|")
                expected_cols = len(re.split(r"(?<!\\)\|", clean_delim))
                norm_header = stripped
                if norm_header.startswith("|") and not norm_header.endswith("|"):
                    norm_header = norm_header + " |"
                has_outer_pipes = norm_header.startswith("|") and norm_header.endswith("|")
                result.append(norm_header)
                result.append(delim_line)
                i = k + 1
                continue

        if in_table:
            # Table ended if line is a thematic break, heading, or code fence
            clean = re.sub(r"^>\s*", "", stripped)
            if (
                clean.startswith("#")
                or re.match(r"^---+$", clean)
                or clean.startswith("```")
                or clean.startswith("~~~")
            ):
                in_table = False
                result.append(line)
                i += 1
                continue

            # If line is completely empty, check if subsequent lines continue the table
            if not stripped:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    next_clean = re.sub(r"^>\s*", "", lines[j].strip())
                    if next_clean.startswith("|") or " |" in next_clean:
                        i += 1
                        continue
                    if result and not _is_row_complete(result[-1], expected_cols, has_outer_pipes):
                        i += 1
                        continue
                in_table = False
                result.append(line)
                i += 1
                continue

            # Check if previous row in result is incomplete and current line is continuation
            if result and not _is_row_complete(result[-1], expected_cols, has_outer_pipes):
                prev = result.pop()
                if prev.rstrip().endswith("|") and clean.startswith("|"):
                    merged = prev.rstrip() + clean.lstrip()[1:]
                else:
                    sep = " " if not prev.endswith(" ") and not prev.endswith("|") and not clean.startswith("|") else ""
                    merged = prev.rstrip() + sep + clean.lstrip()
                result.append(merged)
                i += 1
                continue

            # Complete row or new line
            if "|" in clean:
                result.append(line)
                i += 1
            else:
                in_table = False
                result.append(line)
                i += 1
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


# ── Regex for inline code containing pipe characters ────────────────────────
_INLINE_CODE_PIPE_RE = re.compile(r"(`+)([^`\n]*\|[^`\n]*)\1")


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

    # ── Step 1.5: Protect inline code containing pipes in table rows ────
    def _replace_inline_code_pipe(match: re.Match[str]) -> str:
        code_content = match.group(2)
        sentinel = _make_sentinel("ICODE")
        sentinel_map[sentinel] = SentinelEntry(
            sentinel=sentinel,
            kind="inline_code",
            content=code_content,
        )
        return sentinel

    norm_lines: list[str] = []
    for line in text.splitlines():
        if "|" in line and "`" in line:
            line = _INLINE_CODE_PIPE_RE.sub(_replace_inline_code_pipe, line)
        norm_lines.append(line)
    text = "\n".join(norm_lines)

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
