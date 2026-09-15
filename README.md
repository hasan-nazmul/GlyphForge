<div align="center">

# ⚡ NoteFlux

### *Local-First Technical Document Preservation & Rendering Engine*

[![PyPI](https://img.shields.io/badge/PyPI-noteflux-blue?style=flat-square&logo=pypi)](https://pypi.org/project/noteflux/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-153%20Passing-brightgreen?style=flat-square)](tests/)
[![Architecture](https://img.shields.io/badge/Architecture-Local--First-orange?style=flat-square)]()
[![Privacy](https://img.shields.io/badge/Cloud%20Dependencies-Zero-red?style=flat-square)]()

<br/>

> **LLM responses make great raw thoughts, but terrible final documents.**  
> NoteFlux restores the equations, tables, code blocks, and structure that copy/paste destroys.

<br/>

```
  ChatGPT / Claude / Gemini / DeepSeek
                   ↓
               NoteFlux
                   ↓
  ┌────────────┬───────────┬────────────┐
  ↓            ↓           ↓            ↓
Markdown     HTML         PDF          DOCX
(Truth)    (Offline    (Tectonic     (Native
 Source)    KaTeX)      LaTeX)        OMML)
```

</div>

---

## 🚀 Quickstart

### 1. Installation

**From PyPI:**
```bash
pip install noteflux
```

**From source:**
```bash
git clone https://github.com/hasan-nazmul/GlyphForge.git && cd GlyphForge
pip install -r requirements.txt
pip install -e .
```

*Optional external tools for PDF & Word rendering:*
```bash
sudo apt install -y pandoc wl-clipboard xclip
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh  # Tectonic
```

---

## 💻 CLI In Action

```bash
# 1. Convert any Markdown or LLM output into all formats
note convert response.md

# 2. Convert directly from your system clipboard
note convert clipboard --format pdf,html --output ./output/

# 3. Clean messy LLM output with deterministic normalization
note clean messy.md --output cleaned.md

# 4. Copy canonical, structured Markdown straight to clipboard
note copy lecture.md

# 5. Inspect document structure and math statistics
note inspect demo/technical_note.md
```

<details>
<summary><b>🔍 Sample Output: <code>note inspect</code></b></summary>

```text
  Document Structure
  ─────────────────────────────
  Headings:        12
  Paragraphs:      28
  Equations:       35 (display: 6, inline: 29)
  Code blocks:     3 (python: 1, cpp: 1, bash: 1)
  Tables:          1
  Lists:           5
  Front matter:    yes (title: "Advanced Machine Learning & Optimization Notes")
```
</details>

---

## 🎯 Target Formats

| Format | Engine | Key Guarantee |
| :--- | :--- | :--- |
| **`.md`** | Canonical Serializer | **Immutable Source of Truth** — always preserved first. |
| **`.html`** | Offline KaTeX + Pygments | Standalone HTML5 with 100% offline bundled math & code styles. |
| **`.pdf`** | Pandoc + Tectonic | Crisp vector LaTeX typesetting, 1-inch margins, TOC, no raster math. |
| **`.docx`** | Pandoc + Reference Template | Genuine editable Word document with native `<m:oMath>` equations. |

---

## 🛡️ Core Principles

- **Zero Math Rasterization**: Math stays mathematical. Never converted to blurry PNGs or lossy screenshots.
- **Fail-Safe Source Preservation**: Even if an external TeX compiler fails, your canonical Markdown source is guaranteed to be saved.
- **Sandboxed Execution**: Runs with `--sandbox` and zero arbitrary LaTeX shell escapes. Safe for untrusted LLM outputs.
- **100% Local**: No API keys, no network calls, zero telemetry.

---

<div align="center">
  <sub>Built with precision for engineers, researchers, and technical writers. MIT Licensed.</sub>
</div>
