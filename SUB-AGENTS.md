# SUB-AGENTS.md - Orchestration & Output Workflow

This document defines how the main agent should orchestrate the CV Brainstormer workflow and manage outputs.

## 1. Orchestration Flow

### Phase 1 - Pre-processing

- Run Agent 00 instructions yourself, or delegate only when an explicit subagent workflow is available.
- Normalize raw CV text into structured Markdown.
- Recommended intermediate output: `scratch/00-structured-cv.md` if scratch space is used.

### Phase 2 - Role Discovery Interview

- Run Agent 00.25 when the candidate's official title, target role, and actual work are mixed or unclear.
- This gate asks diagnostic questions about:
  - ticket ownership
  - RCA ownership
  - SQL depth
  - production data responsibility
  - log/service debugging
  - developer escalation
  - workaround authority
  - client communication
  - SLA responsibility
  - deployment and infrastructure exposure
  - monitoring
  - backup/restore
  - code ownership boundary
  - documentation
  - decision authority
  - scale
  - daily tools
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

### Phase 7 - Synthesis

- Run Agent 07 to synthesize findings into a bilingual report and baseline CV.
- Agent 07 must write like a human CV strategist, not a template generator.
- Agent 07 must resolve conflicts and challenge unsupported framing.
- Output:
  - `output/candidates/<candidate-slug>/<run-id>/reports/final-report-bilingual.md`
  - `output/candidates/<candidate-slug>/<run-id>/reports/final-report-bilingual.docx`
  - `output/candidates/<candidate-slug>/<run-id>/reports/final-report-bilingual.pdf`

### Phase 8 - Role Tailoring

- Run Agent 08 for each user-approved target role.
- Current target role folders:
  - `output/candidates/<candidate-slug>/<run-id>/cv/application-support/`
  - `output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/`
  - `output/candidates/<candidate-slug>/<run-id>/cv/general/`
- For each target role, create both language variants:
  - `*-en.md`
  - `*-id.md`
- Render each Markdown file to `.docx` and `.pdf`.

### Phase 9 - Portfolio Alignment

- Portfolio material must come from real user-provided project context when available.
- Current portfolio source:
  - `output/candidates/<candidate-slug>/<run-id>/input/projects-list.md`
- Current curated output:
  - `output/candidates/<candidate-slug>/<run-id>/portfolio/projects-from-list.md`
- Do not invent unrelated dummy portfolio projects unless the user explicitly asks for synthetic examples.
- Run Agent 08.5 to decide which projects support which role and what proof is missing.

### Phase 10 - Verification

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

## 2. Output Folder Contract

The workflow should keep `output/` organized by candidate and run:

```text
output/
  candidates/
    <candidate-slug>/
      LATEST.md
      <run-id>/
        input/
        scratch/
        reports/
        cv/
          <target-role>/
        portfolio/
```

Do not leave root-level CV/report files in `output/`. Never overwrite another candidate's run.

### Candidate Slug

Use a lowercase ASCII slug derived from the candidate name:

- `Rafli Arraafi Albaasith` -> `rafli-arraafi`
- Remove titles, punctuation, and duplicate spaces.
- If two candidates share the same slug, append a short suffix such as `-2` or a date.

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

## 7. Tooling

- Use `scripts/review-cv` to initialize a new candidate run:

```bash
scripts/review-cv "Candidate Name" /path/to/cv.pdf --roles "Data Analyst, Application Support" --projects /path/to/projects-list.md
```

This creates `output/candidates/<candidate-slug>/<run-id>/`, copies input files, writes `target-brief.md`, updates `LATEST.md`, and prints the short prompt to start the agent workflow.

- Use `scripts/render_outputs.py` to render Markdown into DOCX/PDF:

```bash
python scripts/render_outputs.py path/to/file.md
```

- For multiple files:

```bash
python scripts/render_outputs.py output/candidates/rafli-arraafi/2026-06-01-data-analyst-application-support/cv/data-analyst/cv-data-analyst-en.md output/candidates/rafli-arraafi/2026-06-01-data-analyst-application-support/cv/data-analyst/cv-data-analyst-id.md
```

## 8. Failure Handling

- If PDF/DOCX rendering fails, leave Markdown complete and report the rendering failure clearly.
- If old files cannot be removed, list stale files explicitly in the final response.
- If a target role is ambiguous, ask the user for the target role before tailoring.
