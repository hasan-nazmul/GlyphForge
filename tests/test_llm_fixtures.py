"""Automated regression tests for real LLM outputs and complex table fixtures.

Tests real Gemini samples and table edge cases:
- Pipes inside inline code within table cells
- `<br>` inside table cells not causing row splits
- Multi-line table cell wrapping
- Round-trip stability for real LLM technical notes
"""

import re
from pathlib import Path
import pytest

from glyphforge.parser.markdown_parser import parse
from glyphforge.renderers.markdown import render_markdown
from glyphforge.renderers.html import HTMLRenderer
from glyphforge.model.blocks import Table
from glyphforge.model.inlines import InlineCode

INPUT_DIR = Path(__file__).parent / "fixtures" / "input"


class TestGeminiRealFixtures:
    """Test all real gemini-sample fixtures against the parser and renderers."""

    @pytest.mark.parametrize("sample_name", [
        "gemini-sample-1.md",
        "gemini-sample-2.md",
        "gemini-sample-3.md",
        "gemini-sample-4.md",
        "gemini-sample-5.md",
    ])
    def test_fixture_parse_and_markdown_render(self, sample_name: str):
        path = INPUT_DIR / sample_name
        assert path.exists(), f"Fixture {sample_name} missing"
        content = path.read_text(encoding="utf-8")

        # Pass 1 & 2: Parse
        doc = parse(content)
        assert doc is not None

        # Pass 3: Render markdown
        md_out = render_markdown(doc)
        assert isinstance(md_out, str)

        # Verify no table row is severed by a raw newline (excluding code fences)
        lines = md_out.splitlines()
        in_code_fence = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue

            if stripped.startswith("|") and not re.match(r"^\|?\s*:?-+:?", stripped):
                assert stripped.endswith("|"), (
                    f"Line {i + 1} in rendered markdown is an unclosed/broken table row:\n{line}"
                )

    @pytest.mark.parametrize("sample_name", [
        "gemini-sample-1.md",
        "gemini-sample-2.md",
        "gemini-sample-3.md",
        "gemini-sample-4.md",
        "gemini-sample-5.md",
    ])
    def test_fixture_html_render(self, sample_name: str, tmp_path: Path):
        path = INPUT_DIR / sample_name
        content = path.read_text(encoding="utf-8")
        doc = parse(content)

        renderer = HTMLRenderer()
        out_file = tmp_path / f"{sample_name}.html"
        renderer.render(doc, out_file)
        assert out_file.exists()
        assert out_file.stat().st_size > 0


class TestTableEdgeCases:
    """Specific tests for table corruption patterns produced by LLMs."""

    def test_pipe_inside_inline_code_in_table(self):
        """Unescaped pipes inside backticks must not split the table column."""
        md = (
            "| Command | Description |\n"
            "| :--- | :--- |\n"
            "| `ps aux | grep python` | Find python processes |\n"
            "| `a || b` | Logical OR |\n"
        )
        doc = parse(md)
        tables = [b for b in doc.blocks if isinstance(b, Table)]
        assert len(tables) == 1
        t = tables[0]
        assert len(t.headers) == 2
        assert len(t.rows) == 2

        # Check column 1 of row 0 contains the full command
        cell0 = t.rows[0][0]
        code_nodes = [n for n in cell0.children if isinstance(n, InlineCode)]
        assert len(code_nodes) == 1
        assert code_nodes[0].code == "ps aux | grep python"

        # Check column 2 of row 0 is "Find python processes"
        cell1 = t.rows[0][1]
        text = "".join(getattr(n, "content", "") for n in cell1.children)
        assert "Find python processes" in text

    def test_break_in_cell_does_not_break_row(self):
        """Hard breaks or <br> inside cells must not emit a literal newline into the pipe table row."""
        md = (
            "| Col 1 | Col 2 |\n"
            "| :--- | :--- |\n"
            "| Line 1<br>Line 2 | Other cell |\n"
        )
        doc = parse(md)
        rendered = render_markdown(doc)

        lines = [l for l in rendered.splitlines() if l.strip().startswith("|")]
        # Must have header, separator, and exactly one row
        assert len(lines) == 3
        # The data row must be on a single line with <br>
        assert "<br>" in lines[2]
        assert lines[2].strip().endswith("|")

    def test_multiline_cell_wrap_repaired(self):
        """Tables where an LLM wrapped a cell across multiple lines must be repaired."""
        md = (
            "| Step | Description |\n"
            "| :--- | :--- |\n"
            "| 1 | This is a long cell that wraps\n"
            "onto the second line |\n"
            "| 2 | Step 2 |\n"
        )
        doc = parse(md)
        tables = [b for b in doc.blocks if isinstance(b, Table)]
        assert len(tables) == 1
        t = tables[0]
        assert len(t.rows) == 2
