# Harvard Resume Quality Layer Design

Date: 2026-06-03

## Purpose

Upgrade CV Brainstormer so the Harvard resume guidance becomes an explicit quality layer across analysis, writing, tailoring, and verification. The layer is advisory during writing and a light gate during final verification: it should flag major quality issues, but it should not block output automatically when candidate evidence is incomplete.

## Source Standard

The workflow will adapt the Harvard FAS Mignone Center for Career Success resume guidance into repo-native rules:

- Tailor the resume to the target role and employer-valued skills.
- Use specific, active, factual language.
- Quantify or qualify claims where evidence supports it.
- Write for fast human scanning and ATS/system scanning.
- Avoid personal pronouns, narrative style, slang, flowery language, photos, age, gender, and references.
- Keep formatting consistent, reverse chronological, easy to skim, and PDF-safe.
- Treat AI as an editing aid, not the primary author; the CV must stay authentic and interview-defensible.

The workflow will paraphrase the source principles rather than copying the Harvard page into prompts.

## Scope

### Add Reference

Create:

```text
.agents/skills/cv-brainstormer/references/harvard-resume-standard.md
```

This file will define:

- The Harvard-inspired quality principles.
- A compact checklist for agents.
- Light gate labels: `Pass`, `Minor Issues`, `Needs Revision`.
- Examples of safe downgrades when evidence is weak.

### Update Agent Prompts

Update these prompts:

- `01-ats-scanner.md`: add scan-friendly, PDF-safe, recognizable sections, abbreviation clarity, and contact visibility checks.
- `02-hr-first-impression.md`: add "express, not impress" tone checks, anti-flowery language, anti-generic AI phrasing, and fast-scan readability.
- `04-achievement-auditor.md`: add bullet quality standard: action, context, qualified or quantified result, defensible scope.
- `04-evidence-gate.md`: connect factual language to evidence level and require downgrade wording for unsupported claims.
- `07-synthesizer.md`: require the Harvard layer in final report, priority fixes, and revised CV writing.
- `08-role-tailor.md`: require tailoring without keyword stuffing, overclaiming, or making the candidate sound like a different person.
- `09-delta-verifier.md`: add a `Harvard Resume Standard Check` section with `Pass / Minor Issues / Needs Revision`.

### Update Orchestration Docs

Update:

- `AGENTS.md`
- `SUB-AGENTS.md`
- `.agents/skills/cv-brainstormer/SKILL.md`

These docs will state that the Harvard layer applies throughout the workflow and is checked explicitly before a CV is called ready to send.

### Update Run Initialization Script

Update:

```text
scripts/review-cv
```

The script will create:

```text
output/candidates/<candidate-slug>/<run-id>/input/harvard-resume-checklist.md
```

The generated start prompt will include that checklist and instruct the workflow to use it during synthesis, role tailoring, and final verification.

## Non-Goals

- Do not add a new agent in this change.
- Do not rewrite the entire workflow.
- Do not change output folder naming conventions.
- Do not add external dependencies.
- Do not automate live web fetching of the Harvard page during normal CV runs.
- Do not hard-fail CV generation solely because some metrics are missing.

## Data Flow

1. `scripts/review-cv` initializes the run and writes `input/harvard-resume-checklist.md`.
2. Early agents use the standard as a shared lens for ATS, HR, achievement, and evidence review.
3. Agent 07 applies the standard while writing the final report and revised baseline CV.
4. Agent 08 applies the standard when creating role-specific variants.
5. Agent 09 checks the revised or role-specific CV against the standard and reports one of:
   - `Pass`: no major violations.
   - `Minor Issues`: usable, but polish remains.
   - `Needs Revision`: major issues remain, such as generic claims, overclaiming, poor scannability, or unsupported strong claims.

## Acceptance Criteria

- A new Harvard standard reference file exists and is linked from the workflow docs.
- `scripts/review-cv` creates `input/harvard-resume-checklist.md` for new runs.
- Agent 07 output format includes a Harvard-informed quality summary or quality check.
- Agent 09 output format includes `Harvard Resume Standard Check`.
- Existing workflow order and output folder contract remain unchanged.
- Existing shell script behavior remains backward-compatible for current arguments.

## Testing

- Run `scripts/review-cv --help` to verify usage still works.
- Run `scripts/review-cv` with a temporary sample CV file to verify the checklist is created and prompt includes it.
- Inspect modified Markdown prompts for clear, non-contradictory instructions.

## Risks

- The standard could duplicate existing ATS, HR, and Achievement rubrics. Mitigation: present it as a shared quality layer and only add explicit final verification status in Agent 09.
- The workflow could become too strict for candidates without metrics. Mitigation: keep gatekeeping light and allow qualified wording instead of invented numbers.
- Prompts could become verbose. Mitigation: add compact sections and link to the reference file.
