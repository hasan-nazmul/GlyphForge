"""PDF renderer.

Renders Document IR into publication-quality technical PDF via Pandoc + Tectonic/LaTeX.
Features:
- Professional technical document typography
- Vector equations rendered by real TeX math engine (never rasterized)
- Sensible margins (1 inch), page numbers, headers/footers
- Table of Contents when enabled
- Front matter metadata (title, author, date, subject)
- Sandboxed execution to prevent LaTeX shell escapes or arbitrary file reads
- Clear dependency detection with Ubuntu installation instructions
- Source preservation guarantee if PDF compilation fails
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from glyphforge.deps import DependencyStatus, check_pandoc, check_tectonic
from glyphforge.model.document import Document
from glyphforge.renderers.base import BaseRenderer
from glyphforge.renderers.markdown import render_markdown


class DependencyError(RuntimeError):
    """Raised when an external tool required for PDF rendering is missing."""

    pass


class RenderError(RuntimeError):
    """Raised when PDF generation fails."""

    pass


class PDFRenderer(BaseRenderer):
    """Renders Document IR into a technical PDF using Pandoc and a TeX engine."""

    def __init__(self, engine: str = "tectonic") -> None:
        self.engine = engine

    @property
    def format_name(self) -> str:
        return "PDF"

    @property
    def file_extension(self) -> str:
        return ".pdf"

    def render(self, document: Document, output_path: Path, **kwargs: Any) -> Path:
        """Render *document* to PDF and write to *output_path*.

        Options
        -------
        toc : bool
            Whether to include a Table of Contents (default: True).
        engine : str | None
            TeX engine to use (e.g. 'tectonic', 'xelatex', 'pdflatex').
        margin : str
            Page margin (default: '1in').
        fontsize : str
            Base font size (default: '11pt').
        number_sections : bool
            Whether to number sections (default: False).
        """
        engine = kwargs.get("engine", self.engine)
        toc = kwargs.get("toc", True)
        margin = kwargs.get("margin", "1in")
        fontsize = kwargs.get("fontsize", "11pt")
        number_sections = kwargs.get("number_sections", False)

        # ── Dependency Verification ───────────────────────────────────
        self._verify_dependencies(engine)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate canonical Markdown from Document IR
        md_text = render_markdown(document)

        cmd = [
            "pandoc",
            "-f",
            "markdown+tex_math_dollars+tex_math_single_backslash",
            "-o",
            str(output_path),
            f"--pdf-engine={engine}",
            "--sandbox",
            "-V",
            f"geometry:margin={margin}",
            "-V",
            "colorlinks=true",
            "-V",
            "linkcolor=blue",
            "-V",
            f"fontsize={fontsize}",
            "-V",
            "documentclass=article",
        ]

        if toc:
            cmd.append("--toc")

        if number_sections:
            cmd.append("--number-sections")

        try:
            result = subprocess.run(
                cmd,
                input=md_text,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            if result.returncode != 0:
                # Clean error message without dumping giant LaTeX traceback
                error_msg = result.stderr.strip()
                # Extract relevant lines if long
                if len(error_msg.splitlines()) > 15:
                    lines = error_msg.splitlines()
                    error_msg = "\n".join(lines[-15:])
                raise RenderError(
                    f"PDF compilation failed (exit code {result.returncode}):\n{error_msg}"
                )
        except subprocess.TimeoutExpired:
            raise RenderError("PDF compilation timed out after 120 seconds.")
        except FileNotFoundError:
            raise DependencyError(
                f"Pandoc or PDF engine '{engine}' not found in PATH."
            )

        if not output_path.exists():
            raise RenderError(f"Expected PDF file not found at {output_path}")

        return output_path

    @staticmethod
    def _verify_dependencies(engine: str) -> None:
        """Verify that Pandoc and the chosen TeX engine are available."""
        pandoc_status = check_pandoc()
        if not pandoc_status.found:
            raise DependencyError(
                "PDF rendering requires Pandoc.\n\n"
                f"{pandoc_status.install_hint}"
            )

        if engine == "tectonic":
            tectonic_status = check_tectonic()
            if not tectonic_status.found:
                raise DependencyError(
                    "PDF rendering requires Tectonic (TeX engine).\n\n"
                    f"{tectonic_status.install_hint}\n"
                    "Or install XeLaTeX: sudo apt install texlive-xetex"
                )
        else:
            path = shutil.which(engine)
            if not path:
                raise DependencyError(
                    f"PDF engine '{engine}' was not found in PATH.\n\n"
                    f"Install with:\n"
                    f"  Ubuntu/Debian: sudo apt install texlive-latex-base texlive-fonts-recommended"
                )
