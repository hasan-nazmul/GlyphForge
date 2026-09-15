"""Phase 2 CLI integration tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from glyphforge.cli import app
from glyphforge.clipboard.linux import ClipboardError

runner = CliRunner()


class TestPhase2Convert:
    def test_convert_all_formats(self, tmp_path: Path):
        demo = Path(__file__).parent.parent / "demo" / "technical_note.md"
        output_dir = tmp_path / "output"
        result = runner.invoke(
            app,
            ["convert", str(demo), "--output", str(output_dir), "--format", "md,html,pdf,docx"],
        )
        assert result.exit_code == 0
        assert (output_dir / "technical_note.md").exists()
        assert (output_dir / "technical_note.html").exists()
        assert (output_dir / "technical_note.pdf").exists()
        assert (output_dir / "technical_note.docx").exists()

    def test_convert_html_only(self, tmp_path: Path):
        demo = Path(__file__).parent.parent / "demo" / "technical_note.md"
        output_dir = tmp_path / "output"
        result = runner.invoke(
            app,
            ["convert", str(demo), "--output", str(output_dir), "--format", "html"],
        )
        assert result.exit_code == 0
        assert (output_dir / "technical_note.html").exists()

    def test_convert_pdf_only_preserves_canonical_source(self, tmp_path: Path):
        demo = Path(__file__).parent.parent / "demo" / "technical_note.md"
        output_dir = tmp_path / "output"
        result = runner.invoke(
            app,
            ["convert", str(demo), "--output", str(output_dir), "--format", "pdf"],
        )
        assert result.exit_code == 0
        assert (output_dir / "technical_note.pdf").exists()
        # Immutable safety net: canonical markdown is always preserved
        assert (output_dir / "technical_note.md").exists()

    def test_convert_pdf_failure_preserves_source(self, tmp_path: Path):
        demo = Path(__file__).parent.parent / "demo" / "technical_note.md"
        output_dir = tmp_path / "output"

        with patch("glyphforge.renderers.pdf.PDFRenderer.render", side_effect=RuntimeError("Simulated TeX crash")):
            result = runner.invoke(
                app,
                ["convert", str(demo), "--output", str(output_dir), "--format", "pdf"],
            )
            # Exit code 2 for renderer error
            assert result.exit_code == 2
            # Canonical markdown source MUST still be preserved!
            assert (output_dir / "technical_note.md").exists()
            assert "Source preserved at:" in result.stdout

    def test_convert_quiet_mode(self, tmp_path: Path):
        demo = Path(__file__).parent.parent / "demo" / "technical_note.md"
        output_dir = tmp_path / "output"
        result = runner.invoke(
            app,
            ["convert", str(demo), "--output", str(output_dir), "--format", "html", "--quiet"],
        )
        assert result.exit_code == 0
        assert (output_dir / "technical_note.html").exists()
        # In quiet mode, standard verbose banners are suppressed
        assert "NoteFlux" not in result.stdout

    def test_convert_from_clipboard(self, tmp_path: Path):
        output_dir = tmp_path / "output"
        with patch("glyphforge.clipboard.linux.read_clipboard", return_value="# Title\n\nContent from clipboard"):
            result = runner.invoke(
                app,
                ["convert", "clipboard", "--output", str(output_dir), "--format", "html"],
            )
            assert result.exit_code == 0
            assert (output_dir / "clipboard.html").exists()

    def test_convert_from_clipboard_error(self):
        with patch("glyphforge.clipboard.linux.read_clipboard", side_effect=ClipboardError("No clipboard provider")):
            result = runner.invoke(app, ["convert", "clipboard", "--format", "html"])
            assert result.exit_code == 1
            assert "No clipboard provider" in result.stdout


class TestPhase2Copy:
    def test_copy_file_to_clipboard(self):
        demo = Path(__file__).parent.parent / "demo" / "technical_note.md"
        with patch("glyphforge.clipboard.linux.write_clipboard") as mock_write:
            result = runner.invoke(app, ["copy", str(demo)])
            assert result.exit_code == 0
            assert "Copied canonical Markdown" in result.stdout
            assert mock_write.called
            copied_text = mock_write.call_args[0][0]
            assert "Advanced Machine Learning" in copied_text

    def test_copy_nonexistent_file(self):
        result = runner.invoke(app, ["copy", "/nonexistent.md"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_copy_no_clipboard_provider(self):
        demo = Path(__file__).parent.parent / "demo" / "technical_note.md"
        with patch("glyphforge.clipboard.linux.write_clipboard", side_effect=ClipboardError("No provider found")):
            result = runner.invoke(app, ["copy", str(demo)])
            assert result.exit_code == 1
            assert "No provider found" in result.stdout


class TestMathDisambiguation:
    def test_dollar_amounts_and_shell_vars_not_math(self, tmp_path: Path):
        content = """# Financial & System Notes

Server cost was $100 and hosting is $5.99/mo.
Environment variables include $PATH and $HOME.

Actual equation:
$x + y = z$
"""
        test_file = tmp_path / "test_disambiguation.md"
        test_file.write_text(content, encoding="utf-8")

        result = runner.invoke(app, ["inspect", str(test_file)])
        assert result.exit_code == 0
        # Exactly 1 inline equation should be detected ($x + y = z$)
        assert "Inline math:     1" in result.stdout


class TestMalformedAndStressInput:
    def test_malformed_input(self, tmp_path: Path):
        malformed = """---
title: Malformed Doc
---
# Unclosed math
$$\\frac{1}{2}
Some text | with | partial table
```python
unclosed code fence
"""
        test_file = tmp_path / "malformed.md"
        test_file.write_text(malformed, encoding="utf-8")
        out_dir = tmp_path / "out"
        result = runner.invoke(app, ["convert", str(test_file), "--output", str(out_dir), "--format", "html,md"])
        assert result.exit_code == 0
        assert (out_dir / "malformed.html").exists()
        assert (out_dir / "malformed.md").exists()

    def test_large_input(self, tmp_path: Path):
        large_parts = ["# Large Document Benchmark\n\n"]
        for i in range(200):
            large_parts.append(f"## Section {i}\n\nEquation: $x_{i}^2 + y_{i}^2 = z_{i}^2$\n\n")
            large_parts.append(f"```python\ndef func_{i}():\n    return {i} * 2\n```\n\n")
        large_text = "".join(large_parts)
        test_file = tmp_path / "large.md"
        test_file.write_text(large_text, encoding="utf-8")
        out_dir = tmp_path / "out_large"
        result = runner.invoke(app, ["convert", str(test_file), "--output", str(out_dir), "--format", "html,md", "--quiet"])
        assert result.exit_code == 0
        assert (out_dir / "large.html").exists()

    def test_repair_broken_table(self, tmp_path: Path):
        broken_table = """# Table Test

| Col A | Col B |
| --- | --- |
| Cell 1

 | Cell 2

 |
| Cell 3 | Cell 4 |
"""
        test_file = tmp_path / "broken_table.md"
        test_file.write_text(broken_table, encoding="utf-8")
        out_dir = tmp_path / "out_tbl"
        result = runner.invoke(app, ["convert", str(test_file), "--output", str(out_dir), "--format", "md"])
        assert result.exit_code == 0
        rendered_md = (out_dir / "broken_table.md").read_text()
        assert "| Cell 1 | Cell 2 |" in rendered_md
        assert "| Cell 3 | Cell 4 |" in rendered_md

    def test_code_block_in_list_item(self, tmp_path: Path):
        content = """1. Item with code:
```bash
echo hello
```
"""
        test_file = tmp_path / "list_code.md"
        test_file.write_text(content, encoding="utf-8")
        out_dir = tmp_path / "out_list_code"
        result = runner.invoke(app, ["convert", str(test_file), "--output", str(out_dir), "--format", "md"])
        assert result.exit_code == 0
        rendered_md = (out_dir / "list_code.md").read_text()
        assert "```bash" in rendered_md
        assert "echo hello" in rendered_md

