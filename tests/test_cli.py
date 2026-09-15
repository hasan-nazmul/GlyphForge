"""CLI integration tests using Typer's CliRunner."""

from pathlib import Path

from typer.testing import CliRunner

from glyphforge.cli import app

runner = CliRunner()


class TestVersion:
    def test_version_flag(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "NoteFlux" in result.stdout


class TestConvert:
    def test_convert_demo(self, tmp_path: Path):
        demo = Path(__file__).parent.parent / "demo" / "logistic_regression.md"
        output_dir = tmp_path / "output"
        result = runner.invoke(app, ["convert", str(demo), "--output", str(output_dir), "--format", "md"])
        assert result.exit_code == 0
        assert (output_dir / "logistic_regression.md").exists()

    def test_convert_nonexistent_file(self):
        result = runner.invoke(app, ["convert", "/nonexistent/file.md", "--format", "md"])
        assert result.exit_code == 1

    def test_convert_with_clean(self, tmp_path: Path):
        demo = Path(__file__).parent.parent / "demo" / "logistic_regression.md"
        output_dir = tmp_path / "output"
        result = runner.invoke(app, ["convert", str(demo), "--output", str(output_dir), "--format", "md", "--clean"])
        assert result.exit_code == 0


class TestValidate:
    def test_validate_demo(self):
        demo = Path(__file__).parent.parent / "demo" / "logistic_regression.md"
        result = runner.invoke(app, ["validate", str(demo)])
        assert result.exit_code == 0

    def test_validate_nonexistent(self):
        result = runner.invoke(app, ["validate", "/nonexistent/file.md"])
        assert result.exit_code == 1


class TestClean:
    def test_clean_to_file(self, tmp_path: Path):
        demo = Path(__file__).parent.parent / "demo" / "logistic_regression.md"
        output = tmp_path / "cleaned.md"
        result = runner.invoke(app, ["clean", str(demo), "--output", str(output)])
        assert result.exit_code == 0
        assert output.exists()


class TestInspect:
    def test_inspect_demo(self):
        demo = Path(__file__).parent.parent / "demo" / "logistic_regression.md"
        result = runner.invoke(app, ["inspect", str(demo)])
        assert result.exit_code == 0
        assert "Headings" in result.stdout
        assert "Equations" in result.stdout

    def test_inspect_nonexistent(self):
        result = runner.invoke(app, ["inspect", "/nonexistent/file.md"])
        assert result.exit_code == 1
