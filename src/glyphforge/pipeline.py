"""Pipeline orchestrator.

Sequences the full conversion pipeline:
  1. Read input → raw text
  2. (Optional) Clean with DeterministicCleaner
  3. Parse → Document IR
  4. Validate → report issues
  5. Render canonical Markdown (always, first — the immutable safety net)
  6. Render other requested formats (HTML, PDF, DOCX) via RendererRegistry

Error recovery: if any renderer fails, the pipeline continues with remaining
formats and reports failures. The canonical Markdown is always preserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console

from glyphforge.cleaners.deterministic import DeterministicCleaner
from glyphforge.config import ALL_FORMATS, OutputFormat
from glyphforge.model.document import Document
from glyphforge.parser.markdown_parser import parse
from glyphforge.renderers import MarkdownRenderer, RendererRegistry
from glyphforge.validation.validator import ValidationResult, validate

console = Console()


@dataclass
class PipelineResult:
    """Result of running the conversion pipeline."""

    document: Document
    validation: ValidationResult
    outputs: dict[OutputFormat, Path] = field(default_factory=dict)
    errors: dict[OutputFormat, str] = field(default_factory=dict)
    safety_net_path: Path | None = None

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def run_pipeline(
    text: str,
    source_path: str | None = None,
    output_dir: Path | None = None,
    formats: frozenset[OutputFormat] | None = None,
    clean: bool = False,
    stem: str | None = None,
    toc: bool = True,
    quiet: bool = False,
) -> PipelineResult:
    """Run the full conversion pipeline.

    Parameters
    ----------
    text
        Raw input text (Markdown, possibly messy).
    source_path
        Path to the original file, for diagnostics.
    output_dir
        Directory to write outputs into. Defaults to ``./output/``.
    formats
        Set of output formats to produce. Defaults to all.
    clean
        If True, apply DeterministicCleaner before parsing.
    stem
        Base filename (without extension) for outputs.
    toc
        Whether to generate a Table of Contents where supported.
    quiet
        If True, suppress standard progress messages.
    """
    if formats is None:
        formats = ALL_FORMATS
    if stem is None:
        stem = Path(source_path).stem if source_path else "note"
    if output_dir is None:
        output_dir = Path.cwd() / "output"

    output_dir.mkdir(parents=True, exist_ok=True)

    def _log(message: str, style: str = "") -> None:
        if not quiet:
            if style:
                console.print(message, style=style)
            else:
                console.print(message)

    # ── Step 1: Clean (optional) ──────────────────────────────────────
    if clean:
        cleaner = DeterministicCleaner()
        text = cleaner.clean(text)
        _log("  ✓ Cleaned document", style="green")

    # ── Step 2: Parse ─────────────────────────────────────────────────
    document = parse(text, source_path=source_path)
    _log(f"  ✓ Parsed Markdown ({len(text.splitlines())} lines)", style="green")

    # ── Step 3: Validate ──────────────────────────────────────────────
    validation = validate(document)
    if not quiet:
        _report_validation(validation)

    # ── Step 4: Render ────────────────────────────────────────────────
    result = PipelineResult(document=document, validation=validation)

    # Always render canonical Markdown first as immutable safety net
    md_path = output_dir / f"{stem}.md"
    try:
        md_renderer = MarkdownRenderer()
        md_renderer.render(document, md_path)
        result.safety_net_path = md_path
        if OutputFormat.MARKDOWN in formats:
            result.outputs[OutputFormat.MARKDOWN] = md_path
            _log(f"  ✓ Generated Markdown  → {md_path}", style="green")
        else:
            _log(f"  ✓ Preserved source    → {md_path}", style="dim")
    except Exception as e:
        if OutputFormat.MARKDOWN in formats:
            result.errors[OutputFormat.MARKDOWN] = str(e)
        _log(f"  ✗ Markdown preservation failed: {e}", style="red")

    # Render remaining requested formats via RendererRegistry
    for fmt in sorted(formats, key=lambda f: f.value):
        if fmt == OutputFormat.MARKDOWN:
            continue

        try:
            renderer = RendererRegistry.get(fmt)
            out_file = output_dir / f"{stem}{renderer.file_extension}"
            renderer.render(document, out_file, toc=toc)
            result.outputs[fmt] = out_file
            _log(f"  ✓ Generated {renderer.format_name:<8}  → {out_file}", style="green")
        except Exception as e:
            result.errors[fmt] = str(e)
            _log(f"  ✗ {fmt.value.upper()} rendering failed: {e}", style="red")
            if result.safety_net_path and result.safety_net_path.exists():
                _log(f"    Source preserved at: {result.safety_net_path}", style="yellow")

    return result


def _report_validation(validation: ValidationResult) -> None:
    """Print validation statistics and issues."""
    console.print(f"  ✓ Detected {validation.heading_count} headings", style="green")
    eq_detail = f"{validation.display_math_count} display, {validation.inline_math_count} inline"
    console.print(f"  ✓ Detected {validation.equation_count} equations ({eq_detail})", style="green")
    console.print(f"  ✓ Detected {validation.code_block_count} code blocks", style="green")
    console.print(f"  ✓ Detected {validation.table_count} tables", style="green")

    for issue in validation.issues:
        if issue.severity.value == "warning":
            console.print(f"  {issue.symbol} {issue.message}", style="yellow")
        elif issue.severity.value == "error":
            console.print(f"  {issue.symbol} {issue.message}", style="red")
        else:
            console.print(f"  {issue.symbol} {issue.message}", style="blue")
