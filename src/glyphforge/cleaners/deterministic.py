"""Deterministic text cleaner for messy LLM output.

Applies a series of rule-based transformations without requiring any LLM API.
All transformations are safe, reversible in spirit (no information is destroyed),
and focused on normalizing formatting inconsistencies.
"""

from __future__ import annotations

import re

from glyphforge.cleaners.base import Cleaner


class DeterministicCleaner(Cleaner):
    """Rule-based cleaner for common LLM output issues."""

    @property
    def name(self) -> str:
        return "DeterministicCleaner"

    def clean(self, text: str) -> str:
        """Apply all deterministic cleaning rules to *text*."""
        text = self._normalize_line_endings(text)
        text = self._strip_trailing_whitespace(text)
        text = self._normalize_blank_lines(text)
        text = self._normalize_heading_spacing(text)
        text = self._normalize_code_fence_style(text)
        text = self._normalize_list_markers(text)
        text = self._strip_trailing_newlines(text)
        # Ensure exactly one trailing newline
        text = text.rstrip("\n") + "\n"
        return text

    @staticmethod
    def _normalize_line_endings(text: str) -> str:
        """Convert \\r\\n and \\r to \\n."""
        return text.replace("\r\n", "\n").replace("\r", "\n")

    @staticmethod
    def _strip_trailing_whitespace(text: str) -> str:
        """Remove trailing spaces/tabs from each line (but keep intentional hard breaks)."""
        lines = text.split("\n")
        result: list[str] = []
        for line in lines:
            stripped = line.rstrip(" \t")
            # Preserve hard breaks (two trailing spaces before newline)
            if line.endswith("  ") and stripped:
                result.append(stripped + "  ")
            else:
                result.append(stripped)
        return "\n".join(result)

    @staticmethod
    def _normalize_blank_lines(text: str) -> str:
        """Collapse sequences of 3+ blank lines into 2 (one visual blank line)."""
        return re.sub(r"\n{3,}", "\n\n", text)

    @staticmethod
    def _normalize_heading_spacing(text: str) -> str:
        """Ensure blank line before headings (unless at document start)."""
        lines = text.split("\n")
        result: list[str] = []
        for i, line in enumerate(lines):
            if re.match(r"^#{1,6}\s", line) and i > 0 and result and result[-1].strip():
                result.append("")
            result.append(line)
        return "\n".join(result)

    @staticmethod
    def _normalize_code_fence_style(text: str) -> str:
        """Normalize tilde fences (~~~) to backtick fences (```) unless content has backticks."""
        # Only replace ~~~ that are used as fences (start of line, 3+ tildes)
        lines = text.split("\n")
        result: list[str] = []
        in_tilde_block = False
        for line in lines:
            if re.match(r"^~{3,}", line) and not in_tilde_block:
                in_tilde_block = True
                result.append(re.sub(r"^~{3,}", "```", line))
            elif re.match(r"^~{3,}\s*$", line) and in_tilde_block:
                in_tilde_block = False
                result.append("```")
            else:
                result.append(line)
        return "\n".join(result)

    @staticmethod
    def _normalize_list_markers(text: str) -> str:
        """Normalize * and + list markers to - for consistency."""
        return re.sub(r"^(\s*)[*+]\s", r"\1- ", text, flags=re.MULTILINE)

    @staticmethod
    def _strip_trailing_newlines(text: str) -> str:
        """Remove excessive trailing newlines."""
        return text.rstrip("\n")
