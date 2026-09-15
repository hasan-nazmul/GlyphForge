"""GlyphForge CLI — the ``note`` command.

Commands
--------
  note convert <file|clipboard>  Convert LLM output to clean technical notes
  note validate <file>           Validate document structure
  note clean <file>              Normalize messy LLM output
  note inspect <file>            Show document structure analysis
  note copy <file>               Copy canonical Markdown to clipboard
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from glyphforge import __version__
from glyphforge.config import ALL_FORMATS, OutputFormat

app = typer.Typer(
    name="note",
    help="GlyphForge — Convert LLM responses into clean, structured technical notes.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"GlyphForge v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """GlyphForge — deterministic document preservation and rendering pipeline."""
    pass


@app.command()
def convert(
    source: str = typer.Argument(help="Path to input file, or 'clipboard' to read from clipboard."),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Comma-separated output formats: md,html,pdf,docx (default: all).",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory (default: ./output/).",
    ),
    clean: bool = typer.Option(
        False,
        "--clean",
        "-c",
        help="Apply deterministic cleaning before conversion.",
    ),
    toc: bool = typer.Option(
        True,
        "--toc/--no-toc",
        help="Generate a Table of Contents where supported.",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output for scripting.",
    ),
) -> None:
    """Convert a Markdown file (or clipboard) into clean technical notes."""
    from glyphforge.pipeline import run_pipeline

    if not quiet:
        console.print()
        console.print("  [bold cyan]GlyphForge[/bold cyan]")
        console.print("  " + "─" * 32)

    # Determine formats
    formats = _parse_formats(format)

    # Read input
    if source.lower() == "clipboard":
        from glyphforge.clipboard.linux import ClipboardError, read_clipboard

        try:
            text = read_clipboard()
        except ClipboardError as e:
            console.print(f"\n  ✗ {e}", style="red")
            raise typer.Exit(code=1)
        source_path = None
        stem = "clipboard"
        if not quiet:
            console.print("  Input: [dim]clipboard[/dim]\n")
    else:
        path = Path(source).expanduser()
        if not path.exists():
            console.print(f"\n  ✗ File not found: {source}", style="red")
            raise typer.Exit(code=1)
        text = path.read_text(encoding="utf-8")
        source_path = str(path)
        stem = path.stem
        if not quiet:
            console.print(f"  Input: [dim]{source}[/dim]\n")

    output_dir = output.expanduser() if output else None

    result = run_pipeline(
        text=text,
        source_path=source_path,
        output_dir=output_dir,
        formats=formats,
        clean=clean,
        stem=stem,
        toc=toc,
        quiet=quiet,
    )

    if not quiet:
        console.print()
        if result.outputs:
            console.print("  Output:", style="bold")
            for fmt, out_path in sorted(result.outputs.items(), key=lambda x: x[0].value):
                console.print(f"    {out_path}")
        console.print()

    if result.success:
        if not quiet:
            console.print("  ✓ Conversion complete", style="bold green")
    else:
        if not quiet:
            console.print("  ⚠ Conversion completed with errors", style="bold yellow")
        raise typer.Exit(code=2)


@app.command()
def copy(
    file: Path = typer.Argument(help="Path to Markdown file to copy as canonical Markdown."),
) -> None:
    """Copy the canonical Markdown representation of a document to the system clipboard."""
    from glyphforge.clipboard.linux import ClipboardError, write_clipboard
    from glyphforge.parser.markdown_parser import parse
    from glyphforge.renderers.markdown import render_markdown

    file = file.expanduser()
    if not file.exists():
        console.print(f"\n  ✗ File not found: {file}", style="red")
        raise typer.Exit(code=1)

    text = file.read_text(encoding="utf-8")
    doc = parse(text, source_path=str(file))
    canonical_md = render_markdown(doc)

    try:
        write_clipboard(canonical_md)
        console.print(f"\n  ✓ Copied canonical Markdown ({len(canonical_md.splitlines())} lines) to clipboard", style="green")
    except ClipboardError as e:
        console.print(f"\n  ✗ {e}", style="red")
        raise typer.Exit(code=1)


@app.command()
def validate(
    file: Path = typer.Argument(help="Path to Markdown file to validate."),
) -> None:
    """Validate the structure and content of a Markdown file."""
    from glyphforge.parser.markdown_parser import parse
    from glyphforge.validation.validator import validate as do_validate

    console.print(Panel.fit("GlyphForge — Validate", style="bold cyan"))

    file = file.expanduser()
    if not file.exists():
        console.print(f"\n  ✗ File not found: {file}", style="red")
        raise typer.Exit(code=1)

    text = file.read_text(encoding="utf-8")
    document = parse(text, source_path=str(file))
    result = do_validate(document)

    console.print()
    console.print(f"  ✓ Markdown parsed ({len(text.splitlines())} lines)", style="green")
    console.print(f"  ✓ {result.heading_count} headings detected", style="green")
    eq_detail = f"{result.display_math_count} display, {result.inline_math_count} inline"
    console.print(f"  ✓ {result.equation_count} equations detected ({eq_detail})", style="green")
    console.print(f"  ✓ {result.code_block_count} code blocks detected", style="green")
    console.print(f"  ✓ {result.table_count} tables detected", style="green")

    for issue in result.issues:
        if issue.severity.value == "warning":
            console.print(f"  {issue.symbol} {issue.message}", style="yellow")
        elif issue.severity.value == "error":
            console.print(f"  {issue.symbol} {issue.message}", style="red")
        else:
            console.print(f"  {issue.symbol} {issue.message}", style="blue")

    console.print()
    if result.is_valid:
        if result.has_warnings:
            console.print("  Valid with warnings", style="bold yellow")
        else:
            console.print("  ✓ Markdown valid", style="bold green")
    else:
        console.print("  ✗ Validation failed", style="bold red")
        raise typer.Exit(code=1)


@app.command()
def clean(
    file: Path = typer.Argument(help="Path to Markdown file to clean."),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: stdout).",
    ),
) -> None:
    """Normalize messy LLM output using deterministic rules."""
    from glyphforge.cleaners.deterministic import DeterministicCleaner

    console.print(Panel.fit("GlyphForge — Clean", style="bold cyan"))

    file = file.expanduser()
    if not file.exists():
        console.print(f"\n  ✗ File not found: {file}", style="red")
        raise typer.Exit(code=1)

    text = file.read_text(encoding="utf-8")
    cleaner = DeterministicCleaner()
    cleaned = cleaner.clean(text)

    if output_file:
        out = output_file.expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(cleaned, encoding="utf-8")
        console.print(f"\n  ✓ Cleaned output written to {out}", style="green")
    else:
        console.print()
        console.print(cleaned)


@app.command()
def inspect(
    file: Path = typer.Argument(help="Path to Markdown file to inspect."),
) -> None:
    """Show document structure analysis (heading counts, equation counts, etc.)."""
    from glyphforge.model.blocks import BlockQuote, CodeBlock, DisplayMath, Heading, List, Paragraph, Table
    from glyphforge.model.inlines import InlineMath, Link
    from glyphforge.parser.markdown_parser import parse
    from glyphforge.validation.validator import validate as do_validate

    console.print(Panel.fit("GlyphForge — Inspect", style="bold cyan"))

    file = file.expanduser()
    if not file.exists():
        console.print(f"\n  ✗ File not found: {file}", style="red")
        raise typer.Exit(code=1)

    text = file.read_text(encoding="utf-8")
    document = parse(text, source_path=str(file))
    result = do_validate(document)

    # Detailed block and inline counting
    paragraphs_count = 0
    lang_counts: dict[str, int] = {}
    link_count = 0

    def _count_inlines(inlines_list: list) -> None:
        nonlocal link_count
        for inl in inlines_list:
            if isinstance(inl, Link):
                link_count += 1
            if hasattr(inl, "children") and isinstance(inl.children, list):
                _count_inlines(inl.children)

    def _walk_blocks(blocks: list) -> None:
        nonlocal paragraphs_count
        for block in blocks:
            if isinstance(block, Paragraph):
                paragraphs_count += 1
                _count_inlines(block.children)
            elif isinstance(block, Heading):
                _count_inlines(block.children)
            elif isinstance(block, CodeBlock):
                lang = block.language or "plain"
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
            elif isinstance(block, Table):
                for cell in block.headers:
                    _count_inlines(cell.children)
                for row in block.rows:
                    for cell in row:
                        _count_inlines(cell.children)
            elif isinstance(block, List):
                for item in block.items:
                    _walk_blocks(item.children)
            elif isinstance(block, BlockQuote):
                _walk_blocks(block.children)

    _walk_blocks(document.blocks)

    console.print()
    console.print("  Document Structure", style="bold")
    console.print("  ─────────────────────────────")
    console.print(f"  Headings:        {result.heading_count}")
    console.print(f"  Paragraphs:      {paragraphs_count}")
    console.print(f"  Equations:       {result.equation_count}")
    console.print(f"  Inline math:     {result.inline_math_count}")
    console.print(f"  Display math:    {result.display_math_count}")

    if lang_counts:
        lang_str = ", ".join(f"{lang}: {count}" for lang, count in sorted(lang_counts.items()))
        console.print(f"  Code blocks:     {result.code_block_count} ({lang_str})")
    else:
        console.print(f"  Code blocks:     {result.code_block_count}")

    console.print(f"  Tables:          {result.table_count}")
    console.print(f"  Lists:           {result.list_count}")
    console.print(f"  Links:           {link_count}")
    console.print(f"  Blockquotes:     {result.blockquote_count}")

    has_fm = "yes" if document.metadata.has_any() else "no"
    if document.metadata.title:
        has_fm += f' (title: "{document.metadata.title}")'
    console.print(f"  Front matter:    {has_fm}")
    console.print(f"  Total lines:     {len(text.splitlines())}")
    console.print()


def _parse_formats(format_str: str | None) -> frozenset[OutputFormat]:
    """Parse comma-separated format string into a frozenset of OutputFormat."""
    if format_str is None:
        return ALL_FORMATS

    result: set[OutputFormat] = set()
    for part in format_str.split(","):
        part = part.strip().lower()
        try:
            result.add(OutputFormat(part))
        except ValueError:
            console.print(f"  ⚠ Unknown format '{part}', skipping", style="yellow")

    if not result:
        return ALL_FORMATS
    return frozenset(result)


if __name__ == "__main__":
    app()
