# MarkForge Integration Guide

This guide details the integration between **CV-Brainstormer** and the **MarkForge** universal document compilation engine and AST-based ATS compliance analyzer.

---

## 1. Overview & Architecture

MarkForge (`/home/archy/Projects/markforge`) is a high-performance document compiler and AST analyzer written in TypeScript and executed via [Bun](https://bun.sh). It solves two critical challenges in automated CV generation:

1. **Deterministic ATS Parsing & Quality Audits**: Replaces fuzzy LLM impressions with deterministic AST parsing that inspects heading structures, detects 95+ high-impact action verbs, quantifies metric density (#s, %s, currency, multipliers), and computes an objective ATS compliance score (0–100).
2. **100% Visual Parity (DOCX & PDF)**: Directly generates clean OpenXML `.docx` files and compiles them to `.pdf` via headless LibreOffice (`soffice`), ensuring that the printed PDF is an exact 1:1 match of the editable DOCX without table distortion, line wraps, or margin discrepancies.

### Architecture Diagram

```
CV-Brainstormer Markdown Outputs
  ├── cv/role/cv-*.md
  ├── reports/final-report-bilingual.md
  ├── salary/salary-market-*.md
  ├── interview/star-*.md
  └── portfolio/projects-from-list.md
          │
          ├── [scripts/render-markforge.sh]  ──┐
          ├── [scripts/markforge_bridge.py]  ──┼──> MarkForge CLI (Bun)
          └── [markforge-mcp] (stdio MCP)    ──┘       │
                                                       ├── AST Parser & ATS Heuristics
                                                       ├── OpenXML DOCX Generator
                                                       └── LibreOffice Headless PDF Renderer
                                                               │
                                                               ▼
                                                  Compiled .pdf & .docx
```

---

## 2. Document-to-Template Mapping Matrix

CV-Brainstormer outputs different document families. MarkForge provides specialized typographic presets tailored to each document's purpose:

| Document Pattern | Example Files | MarkForge Template | ATS Compliant? | Layout Characteristics |
| :--- | :--- | :--- | :---: | :--- |
| **CVs & Resumes** | `cv-*.md`, `cv.md`, `*/cv/*.md` | `ats-classic` | **Yes (100%)** | Single-column, standard headings, Calibri/Arial, no tables/graphics, parser-safe layout. |
| **Reports & Benchmarks** | `final-report-bilingual.md`, `verification-report-bilingual.md` | `tech-spec` | Internal Report | RFC-style headers, metadata tables, executive callouts, structured grids. |
| **Salary Benchmarks** | `salary-market-*.md`, `salary-market-summary.md` | `tech-spec` | Internal Report | Multi-currency tables (SGD, USD, IDR), negotiation callout blocks. |
| **STAR Interview Banks** | `star-*.md`, `star-story-bank-*.md` | `tech-spec` | Prep Guide | Situation-Task-Action-Result colored callouts, question prompts, metric tags. |
| **Portfolios & Showcases** | `projects-from-list.md`, `*/portfolio/*.md` | `modern-accent` | Human Eye | Accent colored headers, badge-styled tech stack items, clean project cards. |
| **Applications & Platforms** | `cover-letter-*.md` | `ats-classic` | **Yes (100%)** | Formal letterhead, clean spacing. |
| **Platform Copy** | `linkedin.md`, `upwork.md`, `glints.md` | `tech-spec` | Internal Guide | Sectioned proposal templates, headline variants, profile hooks. |

---

## 3. CLI Tools & Helper Scripts

Three companion scripts in `scripts/` provide full compilation and auditing capabilities:

### A. `scripts/render-markforge.sh` (Shell Wrapper)

Fast shell wrapper for compiling individual files or batch-processing entire candidate run directories.

```bash
# Render a single CV (automatically selects 'ats-classic' template)
./scripts/render-markforge.sh output/candidates/rafli-arraafi/2026-06-01-data-analyst/cv/data-analyst/cv-rafli_arraafi-data-analyst-en.md

# Render an entire candidate run folder (batch compiles CVs, reports, salary, portfolio)
./scripts/render-markforge.sh output/candidates/rafli-arraafi/2026-06-01-data-analyst/

# Override template or specify format (both, pdf, docx, html, all)
./scripts/render-markforge.sh path/to/report.md --template tech-spec --format pdf

# Enable file watcher for live editing
./scripts/render-markforge.sh path/to/cv.md --watch
```

### B. `scripts/markforge_bridge.py` (Python Engine Bridge)

Python CLI and importable module for programmatic document compilation and AST analysis.

```bash
# Doctor: verify installed rendering engines (LibreOffice, Bun, Weasyprint, Pandoc)
python scripts/markforge_bridge.py doctor

# Build a file or directory with telemetry
python scripts/markforge_bridge.py build path/to/cv.md --telemetry

# Output machine-readable JSON for automated workflows
python scripts/markforge_bridge.py build path/to/cv.md --json

# Run ATS audit
python scripts/markforge_bridge.py audit path/to/cv.md
```

#### Python API Usage

```python
from pathlib import Path
from scripts.markforge_bridge import compile_document, audit_document, detect_template

# Detect preset
template = detect_template("cv-john_doe-data-analyst-en.md") # -> "ats-classic"

# Compile to PDF and DOCX
result = compile_document(
    file_path=Path("output/candidates/john/cv/cv-john-en.md"),
    template="ats-classic",
    fmt="both",
)
print("Generated files:", result.output_files)

# Run deterministic AST audit
audit = audit_document("output/candidates/john/cv/cv-john-en.md", json_output=True)
print(f"ATS Score: {audit['score']}/100, Verbs: {audit['actionVerbsCount']}")
```

### C. `scripts/ats-audit.sh` (Deterministic ATS & Metrics Auditor)

Runs MarkForge's AST analyzer to verify ATS compatibility, power action verbs, and quantified metric density.

```bash
# Audit a single CV
./scripts/ats-audit.sh path/to/cv-rafli_arraafi-data-analyst-en.md

# Audit all English CVs in a candidate run folder with an enforced minimum score
./scripts/ats-audit.sh output/candidates/rafli-arraafi/2026-06-01-data-analyst/cv --en-only --min-score 90

# Output structured JSON for Agent 09 (Delta / Final Verifier)
./scripts/ats-audit.sh path/to/cv.md --json
```

#### Sample Audit Scoreboard Output

```text
╔═════════════════════════════════════════════════════════════════════════════════╗
║                    MARKFORGE ATS AUDIT SCOREBOARD                               ║
╚═════════════════════════════════════════════════════════════════════════════════╝

CV Document                                ATS Score  Grade    Verbs      Metrics    Status  
------------------------------------------ ---------- -------  ---------- ---------- ------- 
cv-rafli_arraafi-application-support-...   100/100    A+       10         46         PASS    
cv-rafli_arraafi-business-analyst-en.md    100/100    A+       11         26         PASS    
cv-rafli_arraafi-data-analyst-en.md        100/100    A+       8          26         PASS    
cv-rafli_arraafi-data-support-analyst...   100/100    A+       7          26         PASS    
cv-rafli_arraafi-devops-en.md              100/100    A+       8          21         PASS    
cv-rafli_arraafi-revised-en.md             100/100    A+       8          28         PASS    
cv-rafli_arraafi-manual-qa-en.md           100/100    A+       10         21         PASS    
cv-rafli_arraafi-system-analyst-en.md      100/100    A+       11         27         PASS    

Total documents audited: 8
Enforced minimum ATS threshold: 90/100

✔ All CVs passed ATS quality audit successfully!
```

---

## 4. AST Deterministic Scoring Rules

Unlike LLM-based evaluations that vary between runs, MarkForge uses deterministic AST evaluation rules defined in `packages/core/src/analyzer/`:

1. **Required Section Detection (90 points)**:
   - **Summary / Profile** (15 pts): Evaluated via `/(summary|profile|about\s*me|objective)/i`.
   - **Work Experience** (30 pts): Evaluated via `/(experience|employment|work\s*history|career)/i`.
   - **Education** (15 pts): Evaluated via `/(education|academic|qualifications|degrees)/i`.
   - **Skills** (20 pts): Evaluated via `/(skills|competencies|technical\s*skills|tech\s*stack)/i`.
   - **Projects / Achievements** (10 pts): Evaluated via `/(projects|portfolio|achievements|certifications)/i`.
2. **Contact Information (10 points)**:
   - Detects presence of valid email addresses, phone numbers, and professional links (LinkedIn, GitHub).
3. **Power Action Verbs Check**:
   - Matches words against a curated dictionary of 95+ active verbs (`spearheaded`, `engineered`, `optimized`, `automated`, `resolved`, `architected`, etc.).
4. **Quantified Metrics Density**:
   - Regex matches quantifiable impact points (`(\b\d+([.,]\d+)?\s*(%|\$|x|ms|s|k|m|users|requests|tps|clients)\b|\$\d+)`).
   - CVs should aim for at least 15+ quantifiable metrics across experience bullets.

> **Note on Indonesian CVs (`*-id.md`)**:
> As established in `AGENTS.md`, English CVs are tailored for ATS portals, international firms, and multinational recruiters. Indonesian CVs are tailored for domestic Indonesian firms, state-owned enterprises (BUMN), and local HR screening. For ATS scoring gates, always use `--en-only`.

---

## 5. Connecting MarkForge MCP Server to AI Agent Runners

MarkForge provides a first-class Model Context Protocol (MCP) server located in `/home/archy/Projects/markforge/packages/mcp`.

### Available MCP Tools

| MCP Tool | Description | Key Parameters |
| :--- | :--- | :--- |
| `convert_markdown` | Compiles markdown text into DOCX, PDF, or HTML. | `markdown` (string), `template` (enum), `format` (both/pdf/docx), `outputPath` (string) |
| `analyze_document` | Audits markdown CV for deterministic ATS score and metrics. | `markdown` (string) |
| `list_templates` | Lists all template designs, categories, and typography specs. | None |
| `get_template_skeleton` | Retrieves starting Markdown template skeletons. | `template` (ats-classic, tech-spec, modern-accent, academic, executive) |
| `doctor` | Checks host rendering engines (soffice, weasyprint, pandoc). | None |

---

### Configuration for AI Clients

#### A. Antigravity / Gemini CLI (`mcp_servers`)
Add the MarkForge MCP entry to your workspace configuration or `~/.gemini/antigravity-cli/mcp/markforge.json`:

```json
{
  "mcpServers": {
    "markforge": {
      "command": "bun",
      "args": [
        "run",
        "/home/archy/Projects/markforge/packages/mcp/src/index.ts"
      ],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

#### B. Claude Desktop (`claude_desktop_config.json`)
Location: `~/.config/Claude/claude_desktop_config.json` (Linux) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "markforge": {
      "command": "/home/archy/.bun/bin/bun",
      "args": [
        "run",
        "/home/archy/Projects/markforge/packages/mcp/src/index.ts"
      ]
    }
  }
}
```

#### C. Cursor (`.cursor/mcp.json`)
Location: `/home/archy/Projects/CV-Brainstormer/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "markforge": {
      "command": "bun",
      "args": [
        "run",
        "/home/archy/Projects/markforge/packages/mcp/src/index.ts"
      ]
    }
  }
}
```

#### D. Windsurf / Codeium (`~/.codeium/windsurf/mcp_config.json`)

```json
{
  "mcpServers": {
    "markforge": {
      "command": "bun",
      "args": [
        "run",
        "/home/archy/Projects/markforge/packages/mcp/src/index.ts"
      ]
    }
  }
}
```

---

## 6. Verification and Troubleshooting

### Verifying System Prerequisites

Run the MarkForge doctor:
```bash
python scripts/markforge_bridge.py doctor
# Or via shell:
bun run /home/archy/Projects/markforge/packages/cli/src/index.ts doctor
```

Required dependencies:
- **Bun** (`>= 1.3.8`): Powers MarkForge CLI and MCP server.
- **LibreOffice** (`soffice`): Headless engine for 100% DOCX→PDF rendering parity.
  - Install on Arch/CachyOS: `sudo pacman -S libreoffice-still`
  - Install on Debian/Ubuntu: `sudo apt install libreoffice`

### Custom Path Overrides

If MarkForge is cloned in an unusual directory, specify either environment variable:
```bash
export MARKFORGE_DIR="/path/to/markforge"
# Or point directly to the binary:
export MARKFORGE_BIN="/path/to/markforge-cli"
```
