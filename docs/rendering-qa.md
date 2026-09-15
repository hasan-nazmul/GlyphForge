# GlyphForge — Visual QA & Rendering Quality Checklist

This document specifies the manual and visual quality assurance checklist for rendered technical documents (HTML, PDF, DOCX). Run this checklist against any new document template or renderer changes.

---

## 1. Mathematics & Typography

- [ ] **Equation Centering & Margins**: Display equations ($\$\$\dots\$\$$ and `\[...\]`) must be properly centered with adequate top/bottom margins.
- [ ] **No Math Clipping**: Long equations must not clip or overflow page boundaries (in PDF) or screen boundaries (in HTML horizontal scroll).
- [ ] **Symbol Typography**: Greek symbols ($\alpha, \beta, \theta, \sigma, \lambda$), operators ($\sum, \int, \prod$), and relations ($\le, \ge, \approx, \in$) render as true mathematical vector glyphs, not raster images.
- [ ] **Subscripts & Superscripts**: Expressions like $x_i^{(k)}$, $\hat{y}_i$, and $e^{-z}$ maintain baseline alignment and correct font scaling.
- [ ] **Matrix Formatting**: Multi-row matrices (e.g. `\begin{bmatrix} ... \end{bmatrix}`) align properly across rows and columns.
- [ ] **Inline Math Baseline**: Inline math like $J(\theta)$ or $\mathbf{w} \in \mathbb{R}^d$ matches the surrounding body font height and baseline.

---

## 2. Code Blocks & Syntax Highlighting

- [ ] **Language Lexer**: Code blocks specify correct languages (`python`, `cpp`, `bash`, `sql`, `json`, etc.) with appropriate token colors.
- [ ] **Content Preservation**: Indentation, quotes, backticks, comments, and empty lines inside code blocks match the source verbatim.
- [ ] **No Unintended Line Wrapping**: Code blocks in HTML use `overflow-x: auto` rather than wrapping lines unpredictably.
- [ ] **Fallbacks**: Unrecognized language identifiers gracefully fall back to clean monospaced plain text without error.

---

## 3. Tables & Alignment

- [ ] **Header Distinctions**: Table headers (`<th>`) have distinct background styling or bold font weights.
- [ ] **Column Alignment**: Left (`:---`), center (`:---:`), and right (`---:`) alignments are honored in both HTML and PDF.
- [ ] **Math in Tables**: Formulas embedded inside table cells render with full mathematical typesetting.
- [ ] **Borders & Striping**: Clean, subtle borders and alternating row stripes for readability.

---

## 4. Headings & Hierarchy

- [ ] **Logical Sizing**: H1 through H6 have proportional font sizes and clear separation from preceding text.
- [ ] **Orphan Control / Page Breaks**: In PDF, headings must not appear as orphans at the very bottom of a page without at least 2 lines of subsequent text (`page-break-after: avoid`).
- [ ] **Heading IDs & Anchors**: In HTML, hovering over headings exposes anchor links (`#`), enabling direct linking.
- [ ] **Table of Contents**: When `--toc` is enabled, the TOC reflects the exact document heading hierarchy.

---

## 5. Metadata & Layout

- [ ] **Front Matter Header**: Title, author, date, and subject metadata render cleanly at the top of the document.
- [ ] **Tags & Keywords**: Topic tags render as subtle, pill-style badges.
- [ ] **Sensible Margins**: Standard 1-inch (72pt) margins on all sides in PDF and DOCX; maximum 860px reading column in HTML.
- [ ] **Print Styles**: HTML print preview (`Ctrl+P` or `@media print`) produces clean monochrome/grayscale pages without dark backgrounds or interactive anchors.

---

## 6. Word / DOCX Editability

- [ ] **Native Paragraphs & Headings**: Text opens as genuine Word styles (`Heading 1`, `Heading 2`, `Normal`).
- [ ] **Native OMML Equations**: Math expressions are editable using Word's built-in Equation Tools (`<m:oMath>`).
- [ ] **Native Tables**: Tables are editable Word tables with resizable columns.
