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


def normalize(text: str) -> NormalizationResult:
    """Run Pass 1: protect code blocks and math, normalize delimiters.

    Returns a :class:`NormalizationResult` containing the modified text
    and a map from sentinel strings to their original content.
    """
    sentinel_map: dict[str, SentinelEntry] = {}

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
        return sentinel

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
