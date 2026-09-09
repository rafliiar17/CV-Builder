# CV Brainstormer

[![CI](https://github.com/rafliiar17/CV-Builder/actions/workflows/ci.yml/badge.svg)](https://github.com/rafliiar17/CV-Builder/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

CV Brainstormer is an open-source, multi-agent workflow for reviewing, improving, and generating professional CVs. It is designed for candidates who need role-specific, ATS-friendly, and interview-defensible CV outputs in English and Indonesian.

The project turns a raw CV and target-role brief into structured analysis, market salary intelligence, tailored CV variants, portfolio mapping, STAR interview preparation, and global job application packages. It is especially useful when a candidate's job title, actual work, target role, and available evidence do not line up cleanly.

## Why This Exists

Many CV generators produce generic, inflated, or keyword-stuffed resumes. CV Brainstormer takes a stricter approach:

- It separates evidence-backed claims from weak or risky claims.
- It challenges unclear target roles before writing final CVs.
- It applies ATS, HR, technical, achievement, bias, and industry checks.
- It produces bilingual outputs for different hiring contexts.
- It keeps candidate outputs organized by candidate and run to avoid overwrites.

The goal is not to make a CV sound bigger than the candidate's experience. The goal is to make real experience clearer, more relevant, and easier for recruiters and hiring managers to evaluate.

## Workflow

The workflow orchestrates an 18-agent roster (Agents 00–11 plus strategic gate agents) stored in `.agents/skills/cv-brainstormer/agents/`.

Core phases:

1. **Extraction (Agent 00)**: Normalize raw CV text (PDF/DOCX) into structured Markdown.
2. **Role Discovery Interview (Agent 00.25)**: Classify real role family and level when official titles, actual work, or targets mismatch.
3. **Target Decision Gate (Agent 00.5)**: Lock primary/secondary targets, market, language, and single/dual-track strategy.
4. **Deep Specialist Analysis (Agents 01–06)**: Parallel review covering ATS compliance, HR 6-second scan, tech stack credibility, achievement auditing, industry/JD fit with original role match percentage, and bias checking.
5. **Evidence Gate (Agent 04.5)**: Classify claims as proven, project-backed, exposure, learning, risky, or remove.
6. **Adjacent Role Strategy (Agent 05.5)**: Recommend closest realistic roles and transition paths based on achievements and market needs.
7. **Salary Market Analysis (Agent 05.75)**: Deep-dive current compensation ranges with verified fresh sources, SGD/USD/IDR conversions, and negotiation positioning.
8. **Synthesis & Baseline CV (Agent 07)**: Synthesize findings into a bilingual report and write an evidence-safe, human baseline CV.
9. **Role Tailoring & Copywriting (Agent 08)**: Craft role-specific, interview-defensible CV variants in English and Indonesian.
10. **Portfolio Mapping (Agent 08.5)**: Map real projects to target roles and identify missing proof (code, READMEs, SQL snippets, demos).
11. **Verification (Agent 09)**: Re-run ATS & achievement audits, compute role match delta, and enforce the Harvard Resume Standard gate.
12. **STAR Interview Preparation (Agent 10)**: Create role-specific STAR story banks with situational prep and overclaim guardrails.
13. **Application Package & Platform Profiles (Agent 11)**: Generate targeted cover letters, application emails, follow-up emails, and consolidated profiles for Upwork, LinkedIn, and Glints.

## Output Structure

Outputs are grouped by candidate and run:

```text
output/
  candidates/
    <candidate-slug>/
      LATEST.md
      <run-id>/
        input/
          original-cv.pdf
          extracted.txt
          projects-list.md
          target-brief.md
        scratch/
        reports/
          final-report-bilingual.*
        salary/
          <target-role>/
            salary-market-<target-role>.*
        cv/
          <target-role>/
            cv-<candidate_file_slug>-<target-role>-en.*
            cv-<candidate_file_slug>-<target-role>-id.*
        portfolio/
          projects-from-list.*
        interview/
          <target-role>/
            star-<target-role>-en.*
            star-<target-role>-id.*
        application/
          <target-role>/
            cover-letter-<target-role>-en.*
            email-application-<target-role>-en.*
            email-follow-up-<target-role>-en.*
        platform/
          <target-role>/
            upwork.md
            linkedin.md
            glints.md
            threads.md
```

Generated candidate inputs and outputs are ignored by Git by default.

## Installation & Prerequisites

### 1. System Dependencies
PDF rendering requires WeasyPrint's underlying graphical libraries:
- **Ubuntu / Debian**:
  ```bash
  sudo apt-get update && sudo apt-get install -y libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libjpeg-dev libopenjp2-7-dev
  ```
- **Arch Linux / CachyOS**:
  ```bash
  sudo pacman -S pango harfbuzz cairo libjpeg-turbo openjpeg2
  ```
- **macOS**:
  ```bash
  brew install pango harfbuzz cairo libjpeg openjpeg
  ```

### 2. Python Environment
```bash
# Clone the repository
git clone https://github.com/rafliiar17/CV-Builder.git
cd CV-Builder

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### 1. Initialize a review run
Using the unified CLI:
```bash
python3 scripts/cli.py init "Candidate Name" /path/to/cv.pdf --roles "Data Analyst, Application Support" --projects /path/to/projects-list.md
```
Or via the classic shell script:
```bash
scripts/review-cv "Candidate Name" /path/to/cv.pdf --roles "Data Analyst, Application Support" --projects /path/to/projects-list.md
```

The CLI creates the candidate run folder, extracts CV text & links, copies templates, and prepares the input directory.

### 2. Compile Documents to DOCX & PDF
Render all deliverable documents (CVs, reports, salary analysis, interview prep, cover letters, platforms) using MarkForge:
```bash
# Compile entire candidate run directory
python3 scripts/cli.py render output/candidates/<candidate-slug>/<run-id>/

# Or compile a single document
python3 scripts/cli.py render output/candidates/<candidate-slug>/<run-id>/cv/<role>/cv-<candidate_file_slug>-<role>-en.md
```

### 3. Audit ATS Compliance
```bash
python3 scripts/cli.py audit output/candidates/<candidate-slug>/<run-id>/cv/<role>/cv-<candidate_file_slug>-<role>-en.md
```

## Quality Standard

CV Brainstormer uses a Harvard-inspired resume quality layer as a light gate. The final verifier must label each final CV with:

- `Pass`
- `Minor Issues`
- `Needs Revision`

The standard checks whether the CV is tailored, specific, active, factual, scan-friendly, ATS-safe, and free from unsupported overclaims.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, development setup, test execution, and pull request process.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Repository Status

This repository is maintained as a practical workflow project, not a packaged library. Before applying to Codex for Open Source, make sure the GitHub repository is public and add accurate adoption signals if available, such as stars, forks, issues, external users, or real usage examples.

