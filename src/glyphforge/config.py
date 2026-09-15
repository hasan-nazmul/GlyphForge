"""Configuration defaults and settings for GlyphForge."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class OutputFormat(str, Enum):
    """Supported output formats."""

    MARKDOWN = "md"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"


class MathEngine(str, Enum):
    """Math rendering engine for HTML output."""

    KATEX = "katex"
    MATHJAX = "mathjax"


class PdfEngine(str, Enum):
    """PDF compilation engine."""

    TECTONIC = "tectonic"
    XELATEX = "xelatex"
    CHROME = "chromium"


class Theme(str, Enum):
    """Visual theme for rendered output."""

    TECHNICAL = "technical"


ALL_FORMATS = frozenset({OutputFormat.MARKDOWN, OutputFormat.HTML, OutputFormat.PDF, OutputFormat.DOCX})
DEFAULT_FORMATS = ALL_FORMATS


@dataclass
class GlyphForgeConfig:
    """Runtime configuration for GlyphForge."""

    # Output
    default_formats: frozenset[OutputFormat] = DEFAULT_FORMATS
    output_dir: Path | None = None

    # Rendering
    theme: Theme = Theme.TECHNICAL
    toc: bool = True
    syntax_highlighting: bool = True
    math_engine: MathEngine = MathEngine.KATEX
    pdf_engine: PdfEngine = PdfEngine.TECTONIC

    # Behavior
    overwrite_source: bool = False
    clean_on_convert: bool = False

    # Paths
    config_dir: Path = field(default_factory=lambda: Path.home() / ".config" / "glyphforge")

    @classmethod
    def default(cls) -> GlyphForgeConfig:
        """Return the default configuration."""
        return cls()
