"""Tests for DOCXRenderer."""

from pathlib import Path
from unittest.mock import patch

import pytest

from glyphforge.deps import DependencyStatus
from glyphforge.model.blocks import CodeBlock, Heading, Paragraph, Table, TableCell
from glyphforge.model.document import Document
from glyphforge.model.inlines import InlineMath, Text
from glyphforge.renderers.docx import DependencyError, DOCXRenderer, RenderError


class TestDOCXRenderer:
    def test_docx_generation_live(self, tmp_path: Path):
        doc = Document(
            blocks=[
                Heading(level=1, children=[Text("Test Word Document")]),
                Paragraph([Text("Inline math: "), InlineMath("E = mc^2")]),
                CodeBlock(code="x = 42\nprint(x)", language="python"),
                Table(
                    headers=[TableCell([Text("Col A")]), TableCell([Text("Col B")])],
                    rows=[[TableCell([Text("1")]), TableCell([Text("2")])]],
                ),
            ]
        )
        renderer = DOCXRenderer()
        out = tmp_path / "test.docx"
        result_path = renderer.render(doc, out)
        assert result_path.exists()
        assert result_path.stat().st_size > 5000

    def test_missing_pandoc_raises_dependency_error(self, tmp_path: Path):
        doc = Document(blocks=[Paragraph([Text("test")])])
        renderer = DOCXRenderer()
        out = tmp_path / "out.docx"

        with patch("glyphforge.renderers.docx.check_pandoc") as mock_check:
            mock_check.return_value = DependencyStatus(
                name="pandoc", found=False, install_hint="Install pandoc hint"
            )
            with pytest.raises(DependencyError) as exc_info:
                renderer.render(doc, out)
            assert "requires Pandoc" in str(exc_info.value)

    def test_docx_render_failure(self, tmp_path: Path):
        doc = Document(blocks=[Paragraph([Text("test")])])
        renderer = DOCXRenderer()
        out = tmp_path / "out.docx"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Pandoc error"
            with pytest.raises(RenderError) as exc_info:
                renderer.render(doc, out)
            assert "Pandoc DOCX generation failed" in str(exc_info.value)
