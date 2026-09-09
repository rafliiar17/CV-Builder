# Contributing to CV Brainstormer

Thank you for your interest in contributing to **CV Brainstormer**! This project is an open-source, multi-agent AI system designed to analyze, critique, tailor, and compile high-impact, ATS-compliant, and interview-defensible resumes and application packages.

We welcome contributions of all kinds: bug fixes, prompt improvements, documentation, new test cases, and tool integrations.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for all contributors. Please be respectful, professional, and collaborative in all discussions, pull requests, and issues.

---

## Getting Started

### 1. Prerequisites

- **Python 3.10+** (tested on 3.10, 3.11, 3.12)
- **Git**
- **System Libraries for WeasyPrint** (needed for PDF rendering):
  - **Ubuntu / Debian:**
    ```bash
    sudo apt-get update && sudo apt-get install -y libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libjpeg-dev libopenjp2-7-dev
    ```
  - **Arch Linux / CachyOS:**
    ```bash
    sudo pacman -S pango harfbuzz cairo libjpeg-turbo openjpeg2
    ```
  - **macOS:**
    ```bash
    brew install pango harfbuzz cairo libjpeg openjpeg
    ```

### 2. Local Environment Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/rafliiar17/CV-Builder.git
   cd CV-Builder
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies in editable mode:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .
   pip install ruff pytest
   ```

---

## Development Workflow

### Branching Convention

Always branch off `master`:
- `feature/<feature-name>` for new features or prompt upgrades
- `fix/<bug-name>` for bug fixes
- `docs/<topic>` for documentation improvements

### Running Tests & Linter

Before submitting a Pull Request, ensure all tests and linter checks pass locally:

```bash
# Run Ruff linter
ruff check .

# Automatically fix simple lint errors
ruff check . --fix

# Run Pytest suite
pytest -v
```

---

## Contributing to Agents & Prompts

The core intelligence of CV Brainstormer is structured across specialized agent prompts in `.agents/skills/cv-brainstormer/agents/`.

When modifying or adding agent prompts:
1. **Preserve Invariants:**
   - Title must follow `# Agent XX — <Name>` with an em-dash (`—`).
   - Every agent prompt must maintain:
     - `## When NOT to Run`
     - `## Dependencies`
     - `## Quality Checklist`
     - `## Changelog`
2. **Defensibility & Anti-Hallucination:**
   - Never encourage fabrications, exaggerated ownership verbs, or artificial metrics.
   - Always apply the Harvard-inspired resume standard (`references/harvard-resume-standard.md`).
3. **Anti-Slop Standard:**
   - Platform and application copy must follow `.agents/skills/no-ai-slop/` principles (no banned AI clichés or buzzwords).

---

## Submitting a Pull Request

1. Push your branch to your fork:
   ```bash
   git push -u origin feature/<feature-name>
   ```
2. Open a Pull Request on GitHub against `master`.
3. Provide a clear title and description explaining:
   - What changed
   - Why it was changed
   - Verification steps taken
4. Ensure all GitHub Actions CI checks are green.

Thank you for helping make CV Brainstormer better for everyone!
