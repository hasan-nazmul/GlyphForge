"""Tests for PDFRenderer."""

from pathlib import Path
from unittest.mock import patch

import pytest

from glyphforge.deps import DependencyStatus
from glyphforge.model.blocks import Heading, Paragraph
from glyphforge.model.document import Document
from glyphforge.model.inlines import Text
from glyphforge.renderers.pdf import DependencyError, PDFRenderer, RenderError


class TestPDFRenderer:
    def test_pdf_generation_live(self, tmp_path: Path):
        doc = Document(
            blocks=[
                Heading(level=1, children=[Text("Test PDF Document")]),
                Paragraph([Text("This is a live test of PDF generation using Pandoc and Tectonic.")]),
            ]
        )
        renderer = PDFRenderer()
        out = tmp_path / "test.pdf"
        result_path = renderer.render(doc, out)
        assert result_path.exists()
        assert result_path.stat().st_size > 1000

    def test_missing_pandoc_raises_dependency_error(self, tmp_path: Path):
        doc = Document(blocks=[Paragraph([Text("test")])])
        renderer = PDFRenderer()
        out = tmp_path / "out.pdf"

        with patch("glyphforge.renderers.pdf.check_pandoc") as mock_check:
            mock_check.return_value = DependencyStatus(
                name="pandoc", found=False, install_hint="Install pandoc hint"
            )
            with pytest.raises(DependencyError) as exc_info:
                renderer.render(doc, out)
            assert "requires Pandoc" in str(exc_info.value)
            assert "Install pandoc hint" in str(exc_info.value)

    def test_missing_tectonic_raises_dependency_error(self, tmp_path: Path):
        doc = Document(blocks=[Paragraph([Text("test")])])
        renderer = PDFRenderer(engine="tectonic")
        out = tmp_path / "out.pdf"

        with patch("glyphforge.renderers.pdf.check_pandoc") as mock_pandoc, \
             patch("glyphforge.renderers.pdf.check_tectonic") as mock_tectonic:
            mock_pandoc.return_value = DependencyStatus(name="pandoc", found=True)
            mock_tectonic.return_value = DependencyStatus(
                name="tectonic", found=False, install_hint="Install tectonic hint"
            )
            with pytest.raises(DependencyError) as exc_info:
                renderer.render(doc, out)
            assert "requires Tectonic" in str(exc_info.value)
            assert "Install tectonic hint" in str(exc_info.value)

    def test_pdf_render_error_handling(self, tmp_path: Path):
        doc = Document(blocks=[Paragraph([Text("test")])])
        renderer = PDFRenderer()
        out = tmp_path / "out.pdf"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "LaTeX Error: File not found."
            with pytest.raises(RenderError) as exc_info:
                renderer.render(doc, out)
            assert "PDF compilation failed" in str(exc_info.value)
