# SUB-AGENTS.md - Orchestration & Output Workflow

This document defines how the main agent should orchestrate the CV Brainstormer workflow and manage outputs.

## 1. Orchestration Flow

### Phase 1 - Pre-processing

- Run Agent 00 instructions yourself, or delegate only when an explicit subagent workflow is available.
- Normalize raw CV text into structured Markdown.
- Recommended intermediate output: `scratch/00-structured-cv.md` if scratch space is used.

### Phase 2 - Role Discovery Interview

- Run Agent 00.25 when the candidate's official title, target role, and actual work are mixed or unclear.
- This gate must read the CV first and classify the candidate's broad domain before asking questions.
- Start with universal diagnostics:
  - actual day-to-day role
  - main deliverables
  - ownership level
  - stakeholders
  - decision authority
  - complexity
  - scale
  - daily tools
  - measurable outcomes
  - risk/compliance
  - documentation
  - escalation
  - collaboration
  - process improvement
  - target-role evidence
- Then choose the relevant domain-specific question bank:
  - operations/administration
  - customer service/support
  - sales/business development
  - finance/accounting
  - marketing/content/creative
  - HR/people operations
  - project/product/business analysis
  - data/analytics
  - tech/IT/engineering/application support
  - QA/testing
- Output: `scratch/00-role-discovery-interview.md`
- If the CV and existing context already answer the questions, summarize the evidence instead of asking the user again.

### Phase 3 - Target Decision Gate

- Run Agent 00.5 before deep analysis.
- Consume Agent 00.25 output when available.
- Decide:
  - primary target role
  - secondary target role
  - single-track, dual-track, or multi-track strategy
  - target market
  - output languages
  - what to exclude or downplay
- If the target is unclear or conflicting, stop and ask the user before writing CV variants.

### Phase 4 - Deep Analysis

- Run Agents 01 through 06 independently:
  - 01 ATS Scanner
  - 02 HR First Impression
  - 03 Tech Stack Reviewer
  - 04 Achievement Auditor
  - 05 Industry Analyst
  - 06 Bias Checker
- Parallelize only when the runtime supports actual subagents. In Codex, use available multi-agent tools only when the user explicitly asks for subagents/delegation or when the environment authorizes it.
- If no subagent tool is available, run the rubrics locally and clearly label each agent section.
- Apply the Harvard-inspired quality layer from `input/harvard-resume-checklist.md` or `.agents/skills/cv-brainstormer/references/harvard-resume-standard.md` during ATS, HR, achievement, and evidence analysis.

### Phase 5 - Evidence Gate

- Run Agent 04.5 after Agent 03 and Agent 04.
- Classify major claims and skills:
  - Proven
  - Project-backed
  - Exposure
  - Learning
  - Risky
  - Remove
- Claims marked Risky or Remove must not appear as strong claims in final CVs.

### Phase 6 - Adjacent Role Strategy

- Run Agent 05.5 after Industry Analyst and Evidence Gate.
- It must recommend nearby roles by analyzing:
  - target title
  - JD or current market requirements
  - candidate achievements
  - evidence strength
  - missing proof
- It must classify each role as:
  - Apply Now
  - Apply With Minor CV Tailoring
  - Apply After Portfolio Proof
  - Long-Term Path
  - Do Not Target Yet
- It may disagree with the user's desired role if the evidence is weak.

### Phase 7 - Salary Market Analysis

- Run Agent 05.75 after Agent 05.5 and before Agent 07 for each target role that survives the decision and strategy gates.
- Inputs:
  - Target Decision Gate output (Agent 00.5)
  - Role Discovery Interview output (Agent 00.25)
  - Industry Analyst output (Agent 05)
  - Adjacent Role Strategist output (Agent 05.5)
  - Evidence Gate output (Agent 04.5)
  - Target market (Indonesia local, Singapore/SEA, Global Remote, US Remote, Freelance/Upwork)
  - Target role and JD context
- Currency Conversion:
  - Every final compensation range must be converted into **SGD, USD, and IDR** using live FX rates at generation time.
  - Record the `Generated date`, `Research date`, and `FX rate date`.
- Source Citation Requirements:
  - Deep-review current compensation ranges using at least 3 reputable sources (e.g., Hays, Michael Page, Robert Walters, Levels.fyi, NodeFlair, Glassdoor, Payscale).
  - Explicitly cite source names/URLs, access date, target market, role title, experience level, and data confidence rating.
  - Anti-hallucination mandate: if fresh references or FX rates cannot be verified, state clearly that current salary range cannot be verified with sufficient confidence and provide a research checklist instead of unverified figures.
- Negotiation Positioning:
  - Clearly state candidate's realistic ask, stretch ask, minimum walk-away number, and freelance/contract rates (hourly/monthly) to prevent underpricing.
- Output:
  - `output/candidates/<candidate-slug>/<date>/<target-role>/salary/salary-market-<target-role>.md`
  - Render to `.docx` and `.pdf` via `scripts/render_outputs.py`.

### Phase 8 - Synthesis

- Run Agent 07 to synthesize findings into a bilingual report and baseline CV.
- Agent 07 must write like a human CV strategist, not a template generator.
- Agent 07 must resolve conflicts and challenge unsupported framing.
- Agent 07 must include a Harvard-informed quality check covering target tailoring, specific/active/factual language, scanability, evidence-safe claims, and ATS-safe formatting.
- Output:
  - `output/candidates/<candidate-slug>/<date>/reports/final-report-bilingual.md`
  - `output/candidates/<candidate-slug>/<date>/reports/final-report-bilingual.docx`
  - `output/candidates/<candidate-slug>/<date>/reports/final-report-bilingual.pdf`

### Phase 9 - Role Tailoring

- Run Agent 08 for each user-approved target role.
- Current target role folders:
  - `output/candidates/<candidate-slug>/<date>/application-support/cv/`
  - `output/candidates/<candidate-slug>/<date>/data-analyst/cv/`
  - `output/candidates/<candidate-slug>/<date>/general/cv/`
- For each target role, create both language variants:
  - `*-en.md`
  - `*-id.md`
- Render each Markdown file to `.docx` and `.pdf`.

### Phase 10 - Portfolio Alignment

- Portfolio material must come from real user-provided project context when available.
- Current portfolio source:
  - `output/candidates/<candidate-slug>/<run-id>/input/projects-list.md`
- Current curated output:
  - `output/candidates/<candidate-slug>/<run-id>/portfolio/projects-from-list.md`
- Do not invent unrelated dummy portfolio projects unless the user explicitly asks for synthetic examples.
- Run Agent 08.5 to decide which projects support which role and what proof is missing.

### Phase 11 - Verification

- Run Agent 09 after major revisions and before declaring outputs ready.
- Verify at minimum:
  - ATS safety
  - target-role alignment
  - achievement quality
  - evidence risk
  - interview defensibility
  - portfolio completeness
  - language separation
  - folder structure completeness
  - stale output removal
- Agent 09 must include `Harvard Resume Standard Check` with `Pass`, `Minor Issues`, or `Needs Revision`. Treat this as a light gate: files can still be generated, but a CV with `Needs Revision` cannot be called ready to send.

### Phase 12 - STAR Interview Preparation

- Run Agent 10 after Final Verifier.
- Create role-specific STAR story banks from verified CV evidence, role discovery, evidence gate, adjacent role strategy, portfolio mapping, and user clarifications.
- STAR stories must include:
  - Situation
  - Task
  - Action
  - Result
  - likely interview questions
  - follow-up prep
  - what not to overclaim
- Output:
  - `output/candidates/<candidate-slug>/<date>/<target-role>/interview/star-<target-role>-en.md`
  - `output/candidates/<candidate-slug>/<date>/<target-role>/interview/star-<target-role>-id.md`
- Render each Markdown file to `.docx` and `.pdf`.

### Phase 13 - Application Package & Platform Writer

- Run Agent 11 after Agent 10 (STAR Interview Coach).
- Inputs:
  - Verified CV role variant from Agent 08 + Agent 09
  - Target role and market from Agent 00.5
  - Target alignment and Previous CV Role Match from Agent 05
  - Evidence Gate output from Agent 04.5
  - Portfolio Mapper output from Agent 08.5
  - STAR Interview Coach output from Agent 10
  - Optional company/JD context and target platform
- Core deliverables:
  - **Cover Letters**: 180-260 words, tailored, evidence-backed, connecting strongest proof to employer problems.
  - **Application Emails**: 5-8 concise sentences with clear subject line options.
  - **Follow-up Emails**: Polite, direct, low-pressure follow-up template.
  - Generates `-en.md` for global/remote and `-id.md` for local Indonesian markets when requested.
- Consolidated Platform Files (one single file per platform channel under `<target-role>/platform/`):
  - `upwork.md`: Service-positioned (client problems, deliverables, tools, scope, turnaround, proof of work, proposal hooks, and Upwork Service Match score; avoid resume-dump or unverified expert claims).
  - `linkedin.md`: Keyword-aware headline, about section, featured highlights, and outreach messaging.
  - `glints.md`: Regional/local recruiter-friendly summary, practical skills, expected role fit, and application pitch.
- Outputs:
  - `output/candidates/<candidate-slug>/<date>/<target-role>/application/cover-letter-<target-role>-en.md`
  - `output/candidates/<candidate-slug>/<date>/<target-role>/application/email-application-<target-role>-en.md`
  - `output/candidates/<candidate-slug>/<date>/<target-role>/application/email-follow-up-<target-role>-en.md`
  - `output/candidates/<candidate-slug>/<date>/<target-role>/platform/upwork.md`
  - `output/candidates/<candidate-slug>/<date>/<target-role>/platform/linkedin.md`
  - `output/candidates/<candidate-slug>/<date>/<target-role>/platform/glints.md`
  - `output/candidates/<candidate-slug>/<date>/<target-role>/platform/threads.md`
- Render Markdown files to `.docx` and `.pdf` via `scripts/render_outputs.py`.

## 2. Output Folder Contract

The workflow should keep `output/` organized by candidate, run date, and position:

```text
output/
  candidates/
    <candidate-slug>/
      LATEST.md
      <date>/
        input/
          original-cv.pdf
          extracted.txt
          projects-list.md
          target-brief.md
        scratch/
        reports/
          final-report-bilingual.*
        portfolio/
          projects-from-list.*
        <target-role>/
          cv/
            cv-<candidate_file_slug>-<target-role>-en.*
            cv-<candidate_file_slug>-<target-role>-id.*
          salary/
            salary-market-<target-role>.*
          interview/
            star-<target-role>-en.*
            star-<target-role>-id.*
          application/
            cover-letter-<target-role>-en.*
            email-application-<target-role>-en.*
            email-follow-up-<target-role>-en.*
          platform/
            upwork.md
            linkedin.md
            glints.md
            threads.md
```

Do not leave root-level CV/report files in `output/`. Never overwrite another candidate's run.

### Candidate Slug

Use a lowercase ASCII slug derived from the candidate name:

- `Rafli Arraafi Albaasith` -> `rafli-arraafi`
- Remove titles, punctuation, and duplicate spaces.
- If two candidates share the same slug, append a short suffix such as `-2` or a date.

### CV Filename Slug

Use an underscore slug derived from the candidate name for CV filenames:

- `Rafli Arraafi Albaasith` -> `rafli_arraafi`
- CV files must use `cv-<candidate_file_slug>-<target-role>-<language>.md`.
- Example: `cv-rafli_arraafi-application-support-en.md`.
- Keep role folders kebab-case, for example `cv/application-support/`.

### Run ID

Use:

```text
YYYY-MM-DD-<primary-target-slug>
```

For multi-track runs, include the major targets:

```text
2026-06-01-data-analyst-application-support
```

Keep previous runs. Update `LATEST.md` to point to the newest run instead of deleting history.

## 3. Language Policy

- Reports: bilingual English + Indonesia.
- CVs: separate files per language.
- English CVs: ATS-first, standard English role keywords, standard date names such as `Oct 2025-Present`.
- Indonesian CVs: local-market friendly, but still professional and ATS-readable.

## 4. Role-Specific Guidance

### Application Support L1/L2/L3

Lead with:

- SLA tracking or SLA compliance support
- incident handling
- escalation ownership
- SQL troubleshooting
- bug lifecycle
- UAT support
- runbook documentation
- client communication
- database backup/recovery support

### Data Analyst

Lead with:

- SQL
- reporting
- data validation
- import/export workflows
- operational dashboards
- PBB/BPHTB domain knowledge
- PostgreSQL/MySQL/MariaDB exposure
- portfolio projects from `input/projects-list.md`

## 5. Critical Thinking Policy

Agents must not be passive executors. They should challenge:

- unclear target roles
- official titles that do not match actual work
- unsupported role level claims such as L3, DevOps, SysAdmin, or Data Analyst
- QA/Manual Tester claims without test case, UAT, defect tracking, or bug evidence context
- conflicting role combinations
- unsupported skills
- inflated ownership claims
- private projects described as public
- metrics without source
- portfolio projects that sound impressive but do not support the target role
- CV bullets that the candidate cannot defend in interview
- adjacent role suggestions that are not backed by title fit, JD/market fit, and achievement evidence

## 6. Human CV Writing Policy

Agents responsible for CV writing must:

- write naturally, not like a template
- avoid keyword stuffing
- use role-native vocabulary without sounding robotic
- keep bullets specific, contextual, and readable
- downgrade wording when evidence is partial
- preserve the candidate's real career narrative
- follow the Harvard-inspired standard: tailored, active, factual, scan-friendly, and free from narrative style, personal pronouns, slang, photos, age, gender, and references unless a local-market exception is explicitly chosen.

## 7. Tooling

- Use `scripts/review-cv` to initialize a new candidate run:

```bash
scripts/review-cv "Candidate Name" /path/to/cv.pdf --roles "Data Analyst, Application Support" --projects /path/to/projects-list.md
```

This creates `output/candidates/<candidate-slug>/<date>/`, copies input files, writes `target-brief.md`, updates `LATEST.md`, and prints the short prompt to start the agent workflow.

- Use `scripts/render_outputs.py` to render Markdown into DOCX/PDF:

```bash
python scripts/render_outputs.py path/to/file.md
```

- For multiple files:

```bash
python scripts/render_outputs.py output/candidates/rafli-arraafi/2026-09-09/data-analyst/cv/cv-rafli_arraafi-data-analyst-en.md output/candidates/rafli-arraafi/2026-09-09/data-analyst/cv/cv-rafli_arraafi-data-analyst-id.md
```

- STAR interview, salary reports, and application packages should also be rendered to DOCX/PDF:

```bash
python scripts/render_outputs.py output/candidates/<candidate-slug>/<date>/<role>/interview/star-<role>-en.md
python scripts/render_outputs.py output/candidates/<candidate-slug>/<date>/<role>/salary/salary-market-<role>.md
python scripts/render_outputs.py output/candidates/<candidate-slug>/<date>/<role>/application/cover-letter-<role>-en.md
```

## 8. Failure Handling

- If PDF/DOCX rendering fails, leave Markdown complete and report the rendering failure clearly.
- If old files cannot be removed, list stale files explicitly in the final response.
- If a target role is ambiguous, ask the user for the target role before tailoring.
