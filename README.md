# CV Brainstormer

CV Brainstormer is an open-source, multi-agent workflow for reviewing, improving, and generating professional CVs. It is designed for candidates who need role-specific, ATS-friendly, and interview-defensible CV outputs in English and Indonesian.

The project turns a raw CV and target-role brief into structured analysis, tailored CV variants, portfolio mapping, and STAR interview preparation. It is especially useful when a candidate's job title, actual work, target role, and available evidence do not line up cleanly.

## Why This Exists

Many CV generators produce generic, inflated, or keyword-stuffed resumes. CV Brainstormer takes a stricter approach:

- It separates evidence-backed claims from weak or risky claims.
- It challenges unclear target roles before writing final CVs.
- It applies ATS, HR, technical, achievement, bias, and industry checks.
- It produces bilingual outputs for different hiring contexts.
- It keeps candidate outputs organized by candidate and run to avoid overwrites.

The goal is not to make a CV sound bigger than the candidate's experience. The goal is to make real experience clearer, more relevant, and easier for recruiters and hiring managers to evaluate.

## Workflow

The workflow uses specialist agent instructions stored in `.agents/skills/cv-brainstormer/agents/`.

Core phases:

1. Extract and normalize the original CV.
2. Discover the candidate's real role family and level when titles or targets conflict.
3. Decide target role, market, language, and single-track or dual-track strategy.
4. Run ATS, HR, tech stack, achievement, industry, and bias reviews.
5. Classify evidence strength before writing.
6. Recommend adjacent roles when the requested target is not yet well supported.
7. Write role-aware CV variants in English and Indonesian.
8. Map portfolio projects to target roles.
9. Verify output quality and interview defensibility.
10. Generate STAR interview story banks.

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
```

Generated candidate inputs and outputs are ignored by Git by default.

## Quick Start

Initialize a review run:

```bash
scripts/review-cv "Candidate Name" /path/to/cv.pdf --roles "Data Analyst, Application Support" --projects /path/to/projects-list.md
```

The script creates a candidate run folder and prints a prompt that can be pasted back into Codex or another compatible agent runner.

Render Markdown outputs to DOCX and PDF:

```bash
python scripts/render_outputs.py output/candidates/<candidate>/<run-id>/cv/<role>/cv-<candidate>-<role>-en.md
```

## Quality Standard

CV Brainstormer uses a Harvard-inspired resume quality layer as a light gate. The final verifier must label each final CV with:

- `Pass`
- `Minor Issues`
- `Needs Revision`

The standard checks whether the CV is tailored, specific, active, factual, scan-friendly, ATS-safe, and free from unsupported overclaims.

## OpenAI Codex For OSS Application Notes

Suggested answer for "Why does this repository qualify?" under 500 characters:

```text
CV Brainstormer is an active OSS workflow for maintainers and job seekers who need evidence-safe, ATS-friendly CV reviews. It combines specialist agent rubrics for extraction, ATS, HR, tech, achievements, bias, portfolio mapping, verification, and STAR interview prep, with structured outputs that can be reused and improved by the ecosystem.
```

Suggested answer for "How will you use API credits for your project?" under 500 characters:

```text
API credits will be used to run and test the multi-agent CV review workflow: extracting CV text, evaluating ATS and HR quality, checking evidence strength, tailoring bilingual CV variants, mapping portfolios, and generating STAR interview prep. Credits will also support regression tests, prompt iteration, and maintainer automation for releases and documentation.
```

Suggested answer for "Anything else we should know?" under 500 characters:

```text
The project is built to avoid inflated or generic AI resumes. Its core standard is interview-defensible writing: claims are downgraded or removed when evidence is weak. Candidate files are kept out of Git by default, while the reusable workflow, agent rubrics, templates, and scripts remain open for community use.
```

## Repository Status

This repository is maintained as a practical workflow project, not a packaged library. Before applying to Codex for Open Source, make sure the GitHub repository is public and add accurate adoption signals if available, such as stars, forks, issues, external users, or real usage examples.

