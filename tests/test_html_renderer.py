"""Tests for HTMLRenderer."""

from pathlib import Path

import pytest

from glyphforge.model.blocks import (
    BlockQuote,
    CodeBlock,
    DisplayMath,
    Heading,
    ImageBlock,
    List,
    ListItem,
    Paragraph,
    Table,
    TableAlignment,
    TableCell,
    ThematicBreak,
)
from glyphforge.model.document import Document, Metadata
from glyphforge.model.inlines import (
    Bold,
    HardBreak,
    Image,
    InlineCode,
    InlineMath,
    Italic,
    Link,
    SoftBreak,
    Strikethrough,
    Text,
)
from glyphforge.parser.markdown_parser import parse
from glyphforge.renderers.html import HTMLRenderer, _slugify, render_html


class TestHTMLRendererBasics:
    def test_doctype_and_html_structure(self):
        doc = Document(blocks=[Paragraph([Text("Hello world")])])
        renderer = HTMLRenderer()
        html = render_html(doc)
        assert "<!DOCTYPE html>" in html
        assert '<html lang="en">' in html
        assert "<p>Hello world</p>" in html
        assert "</html>" in html

    def test_metadata_in_head_and_body(self):
        meta = Metadata(
            title="Statistical Mechanics",
            author="Ludwig Boltzmann",
            date="1877",
            subject="Physics",
            tags=["entropy", "probability"],
        )
        doc = Document(metadata=meta, blocks=[Paragraph([Text("Entropy formula")])])
        html = render_html(doc)
        assert "<title>Statistical Mechanics</title>" in html
        assert '<meta name="author" content="Ludwig Boltzmann" />' in html
        assert '<meta name="date" content="1877" />' in html
        assert '<meta name="subject" content="Physics" />' in html
        assert '<meta name="keywords" content="entropy, probability" />' in html
        assert "Ludwig Boltzmann" in html
        assert "Statistical Mechanics" in html
        assert "entropy" in html

    def test_empty_metadata_does_not_break(self):
        doc = Document(blocks=[Paragraph([Text("No metadata here")])])
        html = render_html(doc)
        assert "<title>GlyphForge Document</title>" in html
        assert "<p>No metadata here</p>" in html


class TestHTMLBlocks:
    def test_headings_with_deterministic_ids(self):
        doc = Document(
            blocks=[
                Heading(level=1, children=[Text("Introduction")]),
                Heading(level=2, children=[Text("Background & Overview")]),
                Heading(level=2, children=[Text("Introduction")]),  # Duplicate name
            ]
        )
        html = render_html(doc)
        assert '<h1 id="introduction" class="heading">' in html
        assert '<h2 id="background-overview" class="heading">' in html
        assert '<h2 id="introduction-1" class="heading">' in html
        assert 'href="#introduction"' in html

    def test_code_block_highlighting(self):
        code = "def add(a: int, b: int) -> int:\n    return a + b\n"
        doc = Document(blocks=[CodeBlock(code=code, language="python")])
        html = render_html(doc)
        assert 'data-language="python"' in html
        assert '<span class="k">def</span>' in html
        assert "return" in html

    def test_code_block_unknown_language_fallback(self):
        code = "SOME UNKNOWN SYNTAX 123"
        doc = Document(blocks=[CodeBlock(code=code, language="nonexistent_lang_xyz")])
        html = render_html(doc)
        assert "SOME UNKNOWN SYNTAX 123" in html

    def test_display_math_katex(self):
        latex = r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"
        doc = Document(blocks=[DisplayMath(latex=latex)])
        html = render_html(doc)
        assert '<div class="math-display">' in html
        assert r"\[\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}\]" in html

    def test_table_with_alignments(self):
        table = Table(
            headers=[TableCell([Text("Name")]), TableCell([Text("Score")])],
            rows=[[TableCell([Text("Alice")]), TableCell([Text("98")])]],
            alignments=[TableAlignment.LEFT, TableAlignment.RIGHT],
        )
        doc = Document(blocks=[table])
        html = render_html(doc)
        assert '<th style="text-align: left;">Name</th>' in html
        assert '<th style="text-align: right;">Score</th>' in html
        assert '<td style="text-align: left;">Alice</td>' in html
        assert '<td style="text-align: right;">98</td>' in html

    def test_list_and_task_list(self):
        items = [
            ListItem(children=[Paragraph([Text("Task 1")])], checked=True),
            ListItem(children=[Paragraph([Text("Task 2")])], checked=False),
            ListItem(children=[Paragraph([Text("Normal item")])], checked=None),
        ]
        doc = Document(blocks=[List(ordered=False, items=items)])
        html = render_html(doc)
        assert '<input type="checkbox" class="task-checkbox" disabled="" checked="">' in html
        assert '<input type="checkbox" class="task-checkbox" disabled="">' in html
        assert "Normal item" in html

    def test_blockquote_and_thematic_break(self):
        doc = Document(
            blocks=[
                BlockQuote(children=[Paragraph([Text("A famous quotation.")])]),
                ThematicBreak(),
            ]
        )
        html = render_html(doc)
        assert "<blockquote>" in html
        assert "<p>A famous quotation.</p>" in html
        assert "</blockquote>" in html
        assert "<hr />" in html


class TestHTMLInlines:
    def test_inlines_formatting(self):
        inlines = [
            Bold([Text("bold")]),
            Text(" and "),
            Italic([Text("italic")]),
            Text(" and "),
            Strikethrough([Text("deleted")]),
            Text(" and "),
            InlineCode("code()"),
            Text(" and "),
            InlineMath(r"x^2"),
            HardBreak(),
            SoftBreak(),
            Link(href="https://example.com", children=[Text("link")], title="Site"),
            Image(src="test.png", alt="alt text"),
        ]
        doc = Document(blocks=[Paragraph(inlines)])
        html = render_html(doc)
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html
        assert "<del>deleted</del>" in html
        assert "<code>code()</code>" in html
        assert '<span class="math-inline">\\(x^2\\)</span>' in html
        assert '<a href="https://example.com" title="Site">link</a>' in html
        assert '<img src="test.png" alt="alt text"' in html
        assert "<br />" in html

    def test_html_escaping(self):
        doc = Document(blocks=[Paragraph([Text("<script>alert('xss')</script> & <b>dangerous</b>")])])
        html = render_html(doc)
        assert "<script>alert" not in html
        assert "&lt;script&gt;alert" in html
        assert "&amp;" in html


class TestHTMLTableOfContents:
    def test_toc_generated_when_headings_present(self):
        doc = Document(
            blocks=[
                Heading(level=1, children=[Text("Chapter 1")]),
                Paragraph([Text("Text 1")]),
                Heading(level=2, children=[Text("Section 1.1")]),
                Paragraph([Text("Text 2")]),
            ]
        )
        html = render_html(doc, toc=True)
        assert 'class="table-of-contents"' in html
        assert 'href="#chapter-1"' in html
        assert 'href="#section-11"' in html

    def test_toc_disabled(self):
        doc = Document(
            blocks=[
                Heading(level=1, children=[Text("Chapter 1")]),
                Heading(level=2, children=[Text("Section 1.1")]),
            ]
        )
        html = render_html(doc, toc=False)
        assert 'class="table-of-contents"' not in html


class TestSlugify:
    def test_slugify_clean(self):
        assert _slugify("Hello World") == "hello-world"
        assert _slugify("Section 1.2: Cost Function!") == "section-12-cost-function"
        assert _slugify("   multiple   spaces   ") == "multiple-spaces"
        assert _slugify("$$math$$") == "math"
        assert _slugify("$$$$") == "section"
