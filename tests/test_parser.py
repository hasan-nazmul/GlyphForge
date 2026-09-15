"""Tests for the Markdown parser (AST construction)."""

from glyphforge.model.blocks import (
    BlockQuote,
    CodeBlock,
    DisplayMath,
    Heading,
    List,
    Paragraph,
    Table,
    ThematicBreak,
)
from glyphforge.model.inlines import Bold, InlineCode, InlineMath, Italic, Text
from glyphforge.parser.markdown_parser import parse


class TestHeadings:
    def test_h1(self):
        doc = parse("# Hello World")
        assert len(doc.blocks) == 1
        h = doc.blocks[0]
        assert isinstance(h, Heading)
        assert h.level == 1

    def test_h2(self):
        doc = parse("## Section")
        h = doc.blocks[0]
        assert isinstance(h, Heading)
        assert h.level == 2

    def test_heading_with_inline_math(self):
        doc = parse("# Cost Function $J(\\theta)$")
        h = doc.blocks[0]
        assert isinstance(h, Heading)
        # Should contain Text and InlineMath
        has_math = any(isinstance(c, InlineMath) for c in h.children)
        assert has_math


class TestParagraphs:
    def test_simple_paragraph(self):
        doc = parse("Hello world.")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], Paragraph)

    def test_bold_text(self):
        doc = parse("This is **bold** text.")
        p = doc.blocks[0]
        assert isinstance(p, Paragraph)
        has_bold = any(isinstance(c, Bold) for c in p.children)
        assert has_bold

    def test_italic_text(self):
        doc = parse("This is *italic* text.")
        p = doc.blocks[0]
        has_italic = any(isinstance(c, Italic) for c in p.children)
        assert has_italic

    def test_inline_code(self):
        doc = parse("Use `print()` here.")
        p = doc.blocks[0]
        has_code = any(isinstance(c, InlineCode) for c in p.children)
        assert has_code


class TestCodeBlocks:
    def test_fenced_code(self):
        doc = parse('```python\nprint("hello")\n```')
        assert len(doc.blocks) == 1
        cb = doc.blocks[0]
        assert isinstance(cb, CodeBlock)
        assert cb.language == "python"
        assert 'print("hello")' in cb.code

    def test_no_language(self):
        doc = parse("```\nsome code\n```")
        cb = doc.blocks[0]
        assert isinstance(cb, CodeBlock)
        assert cb.language is None


class TestDisplayMathBlocks:
    def test_dollar_display(self):
        doc = parse("$$\nE = mc^2\n$$")
        assert len(doc.blocks) == 1
        dm = doc.blocks[0]
        assert isinstance(dm, DisplayMath)
        assert "E = mc^2" in dm.latex

    def test_bracket_display(self):
        doc = parse("\\[\nx^2 + y^2\n\\]")
        assert len(doc.blocks) == 1
        dm = doc.blocks[0]
        assert isinstance(dm, DisplayMath)
        assert "x^2 + y^2" in dm.latex


class TestInlineMath:
    def test_inline_dollar(self):
        doc = parse("The value $x^2$ is important.")
        p = doc.blocks[0]
        assert isinstance(p, Paragraph)
        math_nodes = [c for c in p.children if isinstance(c, InlineMath)]
        assert len(math_nodes) == 1
        assert math_nodes[0].latex == "x^2"


class TestTables:
    def test_basic_table(self):
        text = "| A | B |\n|---|---|\n| 1 | 2 |"
        doc = parse(text)
        tables = [b for b in doc.blocks if isinstance(b, Table)]
        assert len(tables) == 1
        t = tables[0]
        assert len(t.headers) == 2
        assert len(t.rows) == 1


class TestLists:
    def test_unordered_list(self):
        doc = parse("- Item 1\n- Item 2\n- Item 3")
        lists = [b for b in doc.blocks if isinstance(b, List)]
        assert len(lists) == 1
        assert not lists[0].ordered
        assert len(lists[0].items) == 3

    def test_ordered_list(self):
        doc = parse("1. First\n2. Second\n3. Third")
        lists = [b for b in doc.blocks if isinstance(b, List)]
        assert len(lists) == 1
        assert lists[0].ordered
        assert len(lists[0].items) == 3


class TestBlockquotes:
    def test_blockquote(self):
        doc = parse("> Important note.")
        bqs = [b for b in doc.blocks if isinstance(b, BlockQuote)]
        assert len(bqs) == 1


class TestThematicBreaks:
    def test_hr(self):
        doc = parse("---")
        assert any(isinstance(b, ThematicBreak) for b in doc.blocks)


class TestFrontMatter:
    def test_yaml_frontmatter(self):
        text = "---\ntitle: Test\nauthor: User\n---\n\n# Hello"
        doc = parse(text)
        assert doc.metadata.title == "Test"
        assert doc.metadata.author == "User"
        assert len(doc.blocks) >= 1

    def test_no_frontmatter(self):
        doc = parse("# Hello")
        assert doc.metadata.title is None


class TestComplexDocument:
    def test_demo_parses(self, demo_md):
        """The demo document should parse without errors."""
        doc = parse(demo_md)
        assert len(doc.blocks) > 0
        assert doc.metadata.title == "Logistic Regression"
        # Should have multiple block types
        block_types = {type(b).__name__ for b in doc.blocks}
        assert "Heading" in block_types
        assert "Paragraph" in block_types
        assert "DisplayMath" in block_types
        assert "CodeBlock" in block_types
        assert "Table" in block_types
