"""Output renderers and registry for GlyphForge."""

from __future__ import annotations

from glyphforge.config import OutputFormat
from glyphforge.renderers.base import BaseRenderer
from glyphforge.renderers.docx import DOCXRenderer
from glyphforge.renderers.html import HTMLRenderer
from glyphforge.renderers.markdown import MarkdownRenderer
from glyphforge.renderers.pdf import PDFRenderer
from glyphforge.renderers.registry import RendererRegistry

# Register all built-in format renderers
RendererRegistry.register(OutputFormat.MARKDOWN, MarkdownRenderer)
RendererRegistry.register(OutputFormat.HTML, HTMLRenderer)
RendererRegistry.register(OutputFormat.PDF, PDFRenderer)
RendererRegistry.register(OutputFormat.DOCX, DOCXRenderer)

# Also register standard string aliases
RendererRegistry.register("md", MarkdownRenderer)
RendererRegistry.register("markdown", MarkdownRenderer)
RendererRegistry.register("html", HTMLRenderer)
RendererRegistry.register("pdf", PDFRenderer)
RendererRegistry.register("docx", DOCXRenderer)

__all__ = [
    "BaseRenderer",
    "MarkdownRenderer",
    "HTMLRenderer",
    "PDFRenderer",
    "DOCXRenderer",
    "RendererRegistry",
]
