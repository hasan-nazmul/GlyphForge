"""Pass 2 — Markdown parsing & AST construction.

Uses ``markdown-it-py`` to parse the sentinel-protected text from Pass 1,
then walks the token stream and builds the typed Document IR.  Sentinel
placeholders are resolved back into their original AST node types (code
blocks, display math, inline math).
"""

from __future__ import annotations

from markdown_it import MarkdownIt
from markdown_it.token import Token

from glyphforge.model.blocks import (
    Block,
    BlockQuote,
    CodeBlock,
    DisplayMath,
    Heading,
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
    Inline,
    InlineCode,
    InlineMath,
    Italic,
    Link,
    SoftBreak,
    Strikethrough,
    Text,
)
from glyphforge.parser.frontmatter import extract_frontmatter
from glyphforge.parser.normalizer import NormalizationResult, SentinelEntry, normalize

# ── markdown-it-py instance (GFM tables enabled) ────────────────────────────

_MD = MarkdownIt("commonmark").enable("table")


def parse(text: str, source_path: str | None = None) -> Document:
    """Parse raw Markdown *text* into a :class:`Document` IR.

    This is the main entry point for the parser pipeline.  It runs:

    1. Front matter extraction
    2. Pass 1: Protection & normalization (sentinels)
    3. Pass 2: markdown-it-py parsing + AST construction
    """
    # ── Front matter ──────────────────────────────────────────────────
    metadata, body = extract_frontmatter(text)

    # ── Pass 1: Normalize ─────────────────────────────────────────────
    norm = normalize(body)

    # ── Pass 2: Parse with markdown-it-py ─────────────────────────────
    tokens = _MD.parse(norm.text)
    blocks = _build_blocks(tokens, norm)

    return Document(metadata=metadata, blocks=blocks, source_path=source_path)


# ── Block-level token → AST node ─────────────────────────────────────────────


def _build_blocks(tokens: list[Token], norm: NormalizationResult) -> list[Block]:
    """Walk the markdown-it token list and produce a list of Block nodes."""
    blocks: list[Block] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]

        # ── Heading ───────────────────────────────────────────────────
        if tok.type == "heading_open":
            level = int(tok.tag[1])  # h1 → 1, h2 → 2, etc.
            i += 1  # move to inline content token
            children = _build_inlines(tokens[i], norm) if tokens[i].type == "inline" else []
            blocks.append(Heading(level=level, children=children))
            i += 2  # skip inline + heading_close
            continue

        # ── Paragraph ─────────────────────────────────────────────────
        if tok.type == "paragraph_open":
            i += 1
            if i < len(tokens) and tokens[i].type == "inline":
                inline_tok = tokens[i]
                resolved_blocks = _split_inline_token_to_blocks(inline_tok, norm)
                blocks.extend(resolved_blocks)
                i += 1
            if i < len(tokens) and tokens[i].type == "paragraph_close":
                i += 1
            continue

        # ── Fenced code block ─────────────────────────────────────────
        if tok.type == "fence":
            # Check for sentinel in content
            resolved = _try_resolve_sentinel(tok.content.strip(), norm)
            if resolved is not None and isinstance(resolved, SentinelEntry) and resolved.kind == "code_block":
                blocks.append(CodeBlock(code=resolved.content, language=resolved.language, info=resolved.info))
            else:
                lang = tok.info.strip().split()[0] if tok.info.strip() else None
                blocks.append(CodeBlock(code=tok.content.rstrip("\n"), language=lang, info=tok.info.strip()))
            i += 1
            continue

        # ── Code block (indented) ─────────────────────────────────────
        if tok.type == "code_block":
            blocks.append(CodeBlock(code=tok.content.rstrip("\n"), language=None))
            i += 1
            continue

        # ── Table ─────────────────────────────────────────────────────
        if tok.type == "table_open":
            table, consumed = _parse_table_tokens(tokens, i, norm)
            blocks.append(table)
            i += consumed
            continue

        # ── Bullet / ordered list ─────────────────────────────────────
        if tok.type in ("bullet_list_open", "ordered_list_open"):
            list_node, consumed = _parse_list_tokens(tokens, i, norm)
            blocks.append(list_node)
            i += consumed
            continue

        # ── Block quote ───────────────────────────────────────────────
        if tok.type == "blockquote_open":
            bq, consumed = _parse_blockquote_tokens(tokens, i, norm)
            blocks.append(bq)
            i += consumed
            continue

        # ── Thematic break ────────────────────────────────────────────
        if tok.type == "hr":
            blocks.append(ThematicBreak())
            i += 1
            continue

        # ── Fallback: skip unrecognised tokens ────────────────────────
        i += 1

    return blocks


# ── Inline token → AST node ──────────────────────────────────────────────────


def _build_inlines(token: Token, norm: NormalizationResult) -> list[Inline]:
    """Convert an ``inline`` token's children into a list of Inline nodes."""
    if token.children is None:
        # No children — the content itself might contain sentinels
        return _resolve_inline_text(token.content, norm)

    result: list[Inline] = []
    i = 0
    children = token.children

    while i < len(children):
        child = children[i]

        if child.type == "text":
            result.extend(_resolve_inline_text(child.content, norm))
            i += 1
        elif child.type == "code_inline":
            result.append(InlineCode(code=child.content))
            i += 1
        elif child.type == "softbreak":
            result.append(SoftBreak())
            i += 1
        elif child.type == "hardbreak":
            result.append(HardBreak())
            i += 1
        elif child.type == "strong_open":
            inner, consumed = _collect_until(children, i + 1, "strong_close", norm)
            result.append(Bold(children=inner))
            i += consumed + 2  # skip open + inner + close
        elif child.type == "em_open":
            inner, consumed = _collect_until(children, i + 1, "em_close", norm)
            result.append(Italic(children=inner))
            i += consumed + 2
        elif child.type == "s_open":
            inner, consumed = _collect_until(children, i + 1, "s_close", norm)
            result.append(Strikethrough(children=inner))
            i += consumed + 2
        elif child.type == "link_open":
            href = child.attrGet("href") or ""
            title = child.attrGet("title")
            inner, consumed = _collect_until(children, i + 1, "link_close", norm)
            result.append(Link(href=href, children=inner, title=title))
            i += consumed + 2
        elif child.type == "html_inline":
            if child.content.strip() == "<br>" or child.content.strip() == "<br/>":
                result.append(HardBreak())
            else:
                result.append(Text(content=child.content))
            i += 1
        else:
            # Fallback: treat as text
            if child.content:
                result.extend(_resolve_inline_text(child.content, norm))
            i += 1

    return result


def _collect_until(
    children: list[Token], start: int, close_type: str, norm: NormalizationResult
) -> tuple[list[Inline], int]:
    """Collect inline children from *start* until a token of *close_type* is found."""
    inlines: list[Inline] = []
    count = 0
    i = start
    while i < len(children):
        if children[i].type == close_type:
            break
        if children[i].type == "text":
            inlines.extend(_resolve_inline_text(children[i].content, norm))
        elif children[i].type == "code_inline":
            inlines.append(InlineCode(code=children[i].content))
        elif children[i].type == "softbreak":
            inlines.append(SoftBreak())
        elif children[i].type == "hardbreak":
            inlines.append(HardBreak())
        elif children[i].type == "strong_open":
            inner, consumed = _collect_until(children, i + 1, "strong_close", norm)
            inlines.append(Bold(children=inner))
            i += consumed + 1
        elif children[i].type == "em_open":
            inner, consumed = _collect_until(children, i + 1, "em_close", norm)
            inlines.append(Italic(children=inner))
            i += consumed + 1
        elif children[i].type == "link_open":
            href = children[i].attrGet("href") or ""
            title = children[i].attrGet("title")
            inner, consumed = _collect_until(children, i + 1, "link_close", norm)
            inlines.append(Link(href=href, children=inner, title=title))
            i += consumed + 1
        else:
            if children[i].content:
                inlines.extend(_resolve_inline_text(children[i].content, norm))
        count += 1
        i += 1
    return inlines, count


# ── Sentinel resolution ──────────────────────────────────────────────────────

def _try_resolve_sentinel(text: str, norm: NormalizationResult) -> SentinelEntry | None:
    """If *text* is exactly a sentinel string, return its entry."""
    text = text.strip()
    return norm.sentinel_map.get(text)


def _try_resolve_block_sentinel(text: str, norm: NormalizationResult) -> Block | None:
    """If *text* (trimmed) is a single block-level sentinel, return the AST node."""
    stripped = text.strip()
    entry = norm.sentinel_map.get(stripped)
    if entry is None:
        return None
    if entry.kind == "code_block":
        return CodeBlock(code=entry.content, language=entry.language, info=entry.info)
    if entry.kind == "display_math":
        return DisplayMath(latex=entry.content)
    return None


def _split_inline_token_to_blocks(token: Token, norm: NormalizationResult) -> list[Block]:
    """If an inline token contains embedded block sentinels (e.g. code blocks or display math
    that markdown-it merged into a paragraph), split them into separate Block nodes.
    """
    import re
    from glyphforge.parser.normalizer import SENTINEL_PREFIX, SENTINEL_SUFFIX

    content = token.content
    single = _try_resolve_block_sentinel(content, norm)
    if single is not None:
        return [single]

    # Quick check: if no block sentinels are embedded, build inlines as normal
    if f"{SENTINEL_PREFIX}:CODE:" not in content and f"{SENTINEL_PREFIX}:DMATH:" not in content:
        inlines = _build_inlines(token, norm)
        return [Paragraph(children=inlines)] if inlines else []

    # Contains embedded block sentinel: split content around block sentinels
    pattern = f"({re.escape(SENTINEL_PREFIX)}:(?:CODE|DMATH):[a-f0-9]+{re.escape(SENTINEL_SUFFIX)})"
    parts = re.split(pattern, content)
    from markdown_it import MarkdownIt
    md = MarkdownIt("commonmark")
    blocks: list[Block] = []

    for part in parts:
        part_strip = part.strip()
        if not part_strip:
            continue
        entry = norm.sentinel_map.get(part_strip)
        if entry is not None and entry.kind == "code_block":
            blocks.append(CodeBlock(code=entry.content, language=entry.language, info=entry.info))
        elif entry is not None and entry.kind == "display_math":
            blocks.append(DisplayMath(latex=entry.content))
        else:
            sub_tokens = md.parse(part_strip)
            for st in sub_tokens:
                if st.type == "inline":
                    sub_inlines = _build_inlines(st, norm)
                    if sub_inlines:
                        blocks.append(Paragraph(children=sub_inlines))

    return blocks


def _resolve_inline_text(text: str, norm: NormalizationResult) -> list[Inline]:
    """Split *text* around embedded sentinel placeholders and return Inline nodes.

    Non-sentinel text becomes :class:`Text` nodes; inline math sentinels become
    :class:`InlineMath` nodes; display math sentinels that somehow ended up
    inline are also resolved (though this should be rare).
    """
    if not text:
        return []

    from glyphforge.parser.normalizer import SENTINEL_PREFIX, SENTINEL_SUFFIX

    result: list[Inline] = []
    remaining = text

    while remaining:
        start_idx = remaining.find(SENTINEL_PREFIX)
        if start_idx == -1:
            result.append(Text(content=remaining))
            break

        # Text before the sentinel
        if start_idx > 0:
            result.append(Text(content=remaining[:start_idx]))

        # Find sentinel end
        end_idx = remaining.find(SENTINEL_SUFFIX, start_idx + len(SENTINEL_PREFIX))
        if end_idx == -1:
            # Malformed sentinel — treat rest as text
            result.append(Text(content=remaining[start_idx:]))
            break

        sentinel = remaining[start_idx: end_idx + len(SENTINEL_SUFFIX)]
        entry = norm.sentinel_map.get(sentinel)
        if entry is not None:
            if entry.kind == "inline_math":
                result.append(InlineMath(latex=entry.content))
            elif entry.kind == "display_math":
                # Display math appearing inline — still create InlineMath
                # (the renderer will decide how to handle it)
                result.append(InlineMath(latex=entry.content))
            elif entry.kind == "code_block":
                result.append(InlineCode(code=entry.content))
            else:
                result.append(Text(content=sentinel))
        else:
            result.append(Text(content=sentinel))

        remaining = remaining[end_idx + len(SENTINEL_SUFFIX):]

    return result


# ── Table token parsing ──────────────────────────────────────────────────────

def _parse_table_tokens(
    tokens: list[Token], start: int, norm: NormalizationResult
) -> tuple[Table, int]:
    """Parse a table from the token stream starting at ``table_open``."""
    headers: list[TableCell] = []
    rows: list[list[TableCell]] = []
    alignments: list[TableAlignment] = []
    i = start + 1  # skip table_open
    in_head = False
    in_body = False
    current_row: list[TableCell] = []

    while i < len(tokens):
        tok = tokens[i]

        if tok.type == "table_close":
            i += 1
            break
        elif tok.type == "thead_open":
            in_head = True
            i += 1
        elif tok.type == "thead_close":
            in_head = False
            i += 1
        elif tok.type == "tbody_open":
            in_body = True
            i += 1
        elif tok.type == "tbody_close":
            in_body = False
            i += 1
        elif tok.type == "tr_open":
            current_row = []
            i += 1
        elif tok.type == "tr_close":
            if in_head:
                headers = current_row
            else:
                rows.append(current_row)
            i += 1
        elif tok.type in ("th_open", "td_open"):
            # Extract alignment from style attribute
            style = tok.attrGet("style") or ""
            if "text-align:center" in style:
                al = TableAlignment.CENTER
            elif "text-align:right" in style:
                al = TableAlignment.RIGHT
            elif "text-align:left" in style:
                al = TableAlignment.LEFT
            else:
                al = TableAlignment.NONE
            if in_head and tok.type == "th_open":
                alignments.append(al)
            i += 1
        elif tok.type in ("th_close", "td_close"):
            i += 1
        elif tok.type == "inline":
            children = _build_inlines(tok, norm)
            current_row.append(TableCell(children=children))
            i += 1
        else:
            i += 1

    return Table(headers=headers, rows=rows, alignments=alignments), i - start


# ── List token parsing ───────────────────────────────────────────────────────

def _parse_list_tokens(
    tokens: list[Token], start: int, norm: NormalizationResult
) -> tuple[List, int]:
    """Parse an ordered or unordered list from the token stream."""
    tok = tokens[start]
    ordered = tok.type == "ordered_list_open"
    list_start = int(tok.attrGet("start") or 1) if ordered else 1
    items: list[ListItem] = []
    i = start + 1
    close_type = "ordered_list_close" if ordered else "bullet_list_close"

    while i < len(tokens):
        if tokens[i].type == close_type:
            i += 1
            break
        if tokens[i].type == "list_item_open":
            item, consumed = _parse_list_item_tokens(tokens, i, norm)
            items.append(item)
            i += consumed
        else:
            i += 1

    return List(ordered=ordered, start=list_start, items=items), i - start


def _parse_list_item_tokens(
    tokens: list[Token], start: int, norm: NormalizationResult
) -> tuple[ListItem, int]:
    """Parse a single list item and its nested content."""
    i = start + 1  # skip list_item_open
    children: list[Block] = []

    while i < len(tokens):
        if tokens[i].type == "list_item_close":
            i += 1
            break

        if tokens[i].type == "paragraph_open":
            i += 1
            if i < len(tokens) and tokens[i].type == "inline":
                resolved_blocks = _split_inline_token_to_blocks(tokens[i], norm)
                children.extend(resolved_blocks)
                i += 1
            if i < len(tokens) and tokens[i].type == "paragraph_close":
                i += 1
        elif tokens[i].type in ("bullet_list_open", "ordered_list_open"):
            nested_list, consumed = _parse_list_tokens(tokens, i, norm)
            children.append(nested_list)
            i += consumed
        elif tokens[i].type == "blockquote_open":
            bq, consumed = _parse_blockquote_tokens(tokens, i, norm)
            children.append(bq)
            i += consumed
        else:
            i += 1

    return ListItem(children=children), i - start


# ── Blockquote token parsing ─────────────────────────────────────────────────

def _parse_blockquote_tokens(
    tokens: list[Token], start: int, norm: NormalizationResult
) -> tuple[BlockQuote, int]:
    """Parse a blockquote and its nested content."""
    i = start + 1  # skip blockquote_open
    inner_tokens: list[Token] = []

    depth = 1
    while i < len(tokens):
        if tokens[i].type == "blockquote_open":
            depth += 1
        elif tokens[i].type == "blockquote_close":
            depth -= 1
            if depth == 0:
                i += 1
                break
        inner_tokens.append(tokens[i])
        i += 1

    children = _build_blocks(inner_tokens, norm)
    return BlockQuote(children=children), i - start
