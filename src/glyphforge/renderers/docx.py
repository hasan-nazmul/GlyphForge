"""DOCX renderer.

Converts Document IR into an editable Microsoft Word document (.docx) via Pandoc.
Features:
- Produces native, editable Word documents (not rasterized or embedded PDFs)
- Native Word equations (OMML) from LaTeX math
- True Word heading styles (Heading 1, Heading 2, Heading 3)
- True Word tables, bulleted/numbered lists, and code blocks
- Applies custom reference template if available
- Sandboxed execution to prevent unsafe file access or macros
- Clear dependency errors with Ubuntu installation instructions
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from glyphforge.deps import check_pandoc
from glyphforge.model.document import Document
from glyphforge.renderers.base import BaseRenderer
from glyphforge.renderers.markdown import render_markdown


class DependencyError(RuntimeError):
    """Raised when an external tool required for rendering is missing."""

    pass


class RenderError(RuntimeError):
    """Raised when rendering fails."""

    pass


class DOCXRenderer(BaseRenderer):
    """Renders Document IR into an editable DOCX file using Pandoc."""

    @property
    def format_name(self) -> str:
        return "DOCX"

    @property
    def file_extension(self) -> str:
        return ".docx"

    def render(self, document: Document, output_path: Path, **kwargs: Any) -> Path:
        """Render *document* to DOCX and write to *output_path*.

        Options
        -------
        reference_doc : Path | None
            Custom reference DOCX style template.
        toc : bool
            Whether to include a Table of Contents (default: False for Word, or user choice).
        """
        pandoc_status = check_pandoc()
        if not pandoc_status.found:
            raise DependencyError(
                "DOCX rendering requires Pandoc.\n\n"
                f"{pandoc_status.install_hint}"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Locate reference template
        ref_doc = kwargs.get("reference_doc")
        if ref_doc is None:
            # Check project templates/ first, then package templates/
            candidates = [
                Path.cwd() / "templates" / "reference.docx",
                Path(__file__).parent.parent / "templates" / "reference.docx",
            ]
            for candidate in candidates:
                if candidate.is_file():
                    ref_doc = candidate
                    break

        # Generate canonical Markdown as pandoc source
        md_text = render_markdown(document)

        cmd = [
            "pandoc",
            "-f",
            "markdown+tex_math_dollars+tex_math_single_backslash",
            "-t",
            "docx",
            "--sandbox",
            "-o",
            str(output_path),
        ]

        if ref_doc and Path(ref_doc).exists():
            cmd.extend(["--reference-doc", str(ref_doc)])

        if kwargs.get("toc", False):
            cmd.append("--toc")

        try:
            result = subprocess.run(
                cmd,
                input=md_text,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if result.returncode != 0:
                raise RenderError(
                    f"Pandoc DOCX generation failed (exit code {result.returncode}):\n"
                    f"{result.stderr.strip()}"
                )
        except subprocess.TimeoutExpired:
            raise RenderError("DOCX generation timed out after 60 seconds.")
        except FileNotFoundError:
            raise DependencyError(
                "Pandoc was not found in PATH.\n\n"
                f"{pandoc_status.install_hint}"
            )

        if not output_path.exists():
            raise RenderError(f"Expected DOCX file not found at {output_path}")

        return output_path
