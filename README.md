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

## End-to-End User Guide (How to Create or Review a CV)

Follow this complete step-by-step guide after cloning this repository to review an existing CV or generate an ATS-ready CV from scratch.

### Step 1: Initialize Your Candidate Workspace

You have two ways to prepare your input data:

#### Option A — You have an existing CV (PDF / DOCX) `[Recommended]`
Run the unified CLI to initialize your run directory and automatically extract text & links:
```bash
python3 scripts/cli.py init "Your Full Name" /path/to/your-cv.pdf --roles "Target Role 1, Target Role 2" --projects /path/to/projects-list.md
```
*(Or use the shell helper: `scripts/review-cv "Your Full Name" /path/to/your-cv.pdf --roles "Target Role 1, Target Role 2"`)*

This automated command:
1. Creates an isolated candidate directory: `output/candidates/<candidate-slug>/<date>/`.
2. Extracts plain text and links from your PDF/DOCX into `input/extracted.txt`.
3. Prepares `input/target-brief.md` with your chosen target roles and market strategy.
4. Sets up `input/projects-list.md` to link project portfolio evidence.
5. Sets up per-position folders `<target-role>/` with `cv/`, `salary/`, `interview/`, `application/`, and `platform/`.
6. Updates `LATEST.md` to point to this newest run.

#### Option B — Building from Scratch (No Existing CV)
If you don't have an existing CV file:
1. Create your candidate folder manually:
   ```bash
   mkdir -p output/candidates/your-name/$(date +%Y-%m-%d)/input
   ```
2. Copy the standardized input template:
   ```bash
   cp templates/cv-input-form.md output/candidates/your-name/$(date +%Y-%m-%d)/input/extracted.txt
   ```
3. Open `extracted.txt` and fill in your education, work history, tech skills, and projects.
4. Create `input/target-brief.md` specifying your target roles (e.g. `Data Analyst, Application Support`).

---

### Step 2: Run the Multi-Agent Pipeline

CV Brainstormer uses an 18-agent roster defined under `.agents/skills/cv-brainstormer/agents/`. You can execute the workflow using your preferred AI environment:

#### 🤖 Method 1: AI Coding Assistant (Antigravity, Claude Code, Cursor, Codex) — Recommended
Open this repository in your AI agent and prompt it:
> *"Run the CV-Brainstormer workflow for candidate directory `output/candidates/<candidate-slug>/<date>/` targeting the role `[Target Role]`. Execute Agent 00 through Agent 11, enforcing the Evidence Gate (04.5), Harvard Resume Standard (09), and Anti-Slop writing rules (`no-ai-slop`)."*

The agent will read `.agents/skills/cv-brainstormer/SKILL.md` and orchestrate the full pipeline:
- **Phase 1 (Diagnosis & Target Gate)**: Agents 00, 00.25, and 00.5 normalize text, diagnose true role level, and lock targets.
- **Phase 2 (Specialist Deep Audit)**: Agents 01–06 run parallel checks (ATS score, HR 6s scan, tech stack, achievements, JD match %, bias).
- **Phase 3 (Evidence & Strategy Gates)**: Agent 04.5 filters overclaims, Agent 05.5 suggests adjacent career paths, and Agent 05.75 analyzes live market salaries (SGD, USD, IDR).
- **Phase 4 (Human CV Tailoring)**: Agent 07 writes a baseline CV, Agent 08 tailors role variants (`-en` and `-id`), and Agent 08.5 maps portfolio proof.
- **Phase 5 (Verification & Delivery)**: Agent 09 runs the Harvard Standard Gate (`Pass`/`Minor Issues`/`Needs Revision`), Agent 10 builds STAR interview banks, and Agent 11 writes application packages (cover letters, emails, Upwork/LinkedIn copy).

#### 💻 Method 2: Terminal Scripting (Claude Code CLI)
You can pipe commands directly via Claude Code in terminal:
```bash
RUN_DIR="output/candidates/<candidate-slug>/<date>"
AGENTS_DIR=".agents/skills/cv-brainstormer/agents"

# Step 00: Extract & Normalize
claude -p "$(cat ${AGENTS_DIR}/00-extractor.md)" < "${RUN_DIR}/input/extracted.txt" > "${RUN_DIR}/scratch/00-structured-cv.md"

# (See references/runner-guide.md for the complete script across all 18 agents)
```

#### 🌐 Method 3: Web UI (Claude.ai Projects / ChatGPT)
1. Create a Project in Claude or Custom GPT in ChatGPT.
2. Upload `.agents/skills/cv-brainstormer/agents/` and `references/harvard-resume-standard.md` as Knowledge.
3. Paste the contents of `input/extracted.txt` and run step-by-step following `references/runner-guide.md`.

---

### Step 3: Review Your Deliverables

Once the pipeline completes, your results are saved in `output/candidates/<candidate-slug>/<date>/`:
- 📊 **`reports/final-report-bilingual.md`**: Full diagnostic review, ATS score breakdown, and recruiter impressions (ID + EN).
- 📁 **`<target-role>/`**:
  - 📄 **`cv/`**:
    - `cv-<candidate_file_slug>-<target-role>-en.md` (English CV for global/multinational/remote jobs).
    - `cv-<candidate_file_slug>-<target-role>-id.md` (Indonesian CV for local companies/government/vendors).
  - 💰 **`salary/salary-market-<target-role>.md`**: Real-time salary benchmark with mathematical calculation breakdown converted to SGD, USD, and IDR.
  - 🎯 **`interview/star-<target-role>-en.md`**: Role-specific STAR interview answers with strict boundaries against overclaiming.
  - ✉️ **`application/`**: Tailored cover letter, application email, and follow-up email.
  - 🌐 **`platform/`**: Platform-optimized profiles and proposals for LinkedIn, Upwork, and Glints.

> [!IMPORTANT]
> **Check the Harvard Gate in `reports/delta-report-bilingual.md`**:
> Confirm that Agent 09 marked the CV as **`Pass`** or **`Minor Issues`**. If it marked **`Needs Revision`**, review the unverified claims flagged before sending the CV to recruiters.

---

### Step 4: Compile to PDF & DOCX

Convert the verified Markdown documents into beautifully styled, ATS-safe PDF and DOCX files using MarkForge:

```bash
# Compile all generated files in the candidate run folder:
python3 scripts/cli.py render output/candidates/<candidate-slug>/<date>/

# Or compile an individual CV:
python3 scripts/cli.py render output/candidates/<candidate-slug>/<date>/<role>/cv/cv-<candidate_file_slug>-<role>-en.md
```

### Step 5: Run Final ATS Audit

Verify keyword compliance and layout safety directly from your terminal:
```bash
python3 scripts/cli.py audit output/candidates/<candidate-slug>/<date>/<role>/cv/cv-<candidate_file_slug>-<role>-en.md
```

### Step 6: Sync to Web Portfolio (Optional)

If you maintain a web portfolio (e.g. `profile-new`), you can automatically sync verified PDF and DOCX files into your portfolio repository and update download metadata:
```bash
# Preview sync changes:
python3 scripts/sync_to_profile.py --dry-run

# Execute sync:
python3 scripts/sync_to_profile.py

# Execute sync and trigger Cloudflare R2 upload:
python3 scripts/sync_to_profile.py --upload-r2
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

