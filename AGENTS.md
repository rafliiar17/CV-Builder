# AGENTS.md - Specialist Agents Reference

This project utilizes a multi-agent CV workflow with core agents (00-09) plus strategic gate agents (00.25, 00.5, 04.5, 08.5) to prevent generic, overclaimed, or role-misaligned CVs.

## Main Orchestrator (You)
You are the master agent. Your job is to extract the input, orchestrate the specialists below, tailor outputs to the user's target roles, and render final documents in a manageable folder structure.

## Current Output Standard

Outputs are stored per candidate and per run so multiple people can use the workflow without overwriting each other. Reports are bilingual (English + Indonesia). CVs are split by language and target role:

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
            cv-<target-role>-en.*
            cv-<target-role>-id.*
        portfolio/
          projects-from-list.*
```

Use English CVs for ATS-heavy portals, startups, multinational companies, and LinkedIn/JobStreet applications. Use Indonesian CVs for local/government/vendor roles that expect Bahasa Indonesia.

Current example run:

`output/candidates/rafli-arraafi/2026-06-01-data-analyst-application-support/`

## Specialist Roster

| Agent ID | Role / Name | Core Responsibility |
|----------|-------------|---------------------|
| **00** | **Extractor** | Normalizes raw CV text (from PDF/DOCX) into a structured markdown format. |
| **00.25** | **Role Discovery Interviewer** | Asks diagnostic questions to classify the candidate's real role family and level when title, actual work, or target role conflict. |
| **00.5** | **Target Decision Gate** | Forces target role, market, language, and single/dual-track strategy decisions before analysis. |
| **01** | **ATS Scanner** | Checks ATS compliance, keyword density, and formatting issues. |
| **02** | **HR First Impression** | Performs a 6-second scan, evaluating tone and identifying HR red flags. |
| **03** | **Tech Stack Reviewer** | Evaluates skill credibility, market relevance, and checks for outdated tech (e.g., CentOS EOL). |
| **04** | **Achievement Auditor** | Audits the Responsibility vs. Achievement ratio, action verbs, and quantification (STAR method). |
| **04.5** | **Evidence Gate** | Classifies claims as proven, project-backed, exposure, learning, risky, or remove before writing. |
| **05** | **Industry Analyst** | Assesses JD alignment, gap analysis, and identifies alternative career paths/roles. |
| **05.5** | **Adjacent Role Strategist** | Recommends closest realistic roles by analyzing target title, JD/market requirements, and candidate achievements. |
| **06** | **Bias Checker** | Scans for unnecessary personal info (age, religion, photo) and inclusive language. |
| **07** | **Synthesizer / Human CV Writer** | Compiles reports, resolves conflicts, and writes a human, role-aware, evidence-safe baseline CV. |
| **08** | **Role Tailor / Copywriter** | Tailors the baseline CV to specific target roles with natural human copywriting and interview-defensible wording. |
| **08.5** | **Portfolio Mapper** | Maps real projects to target roles and identifies portfolio gaps, screenshots, READMEs, demos, or SQL proof needed. |
| **09** | **Final Verifier** | Re-runs ATS + achievement scoring and checks role fit, evidence risk, interview defensibility, portfolio completeness, and output structure. |

## Critical Standards

- Agents must not simply agree with user framing. They should challenge unclear targets, unsupported claims, missing context, and weak evidence.
- When official title and real work conflict, agents must use Agent 00.25 output as the source of truth for role family and level.
- CV writing must be human-readable, specific, and role-native. Avoid generic AI-sounding phrasing and keyword stuffing.
- Every strong claim must be interview-defensible.
- Adjacent role recommendations must be based on target title, job description or market requirements, and candidate achievements.
- Private/internal projects must be described safely without implying public repository access or exposing confidential data.
- If evidence is weak, downgrade wording instead of inflating the candidate.

## Instructions Location
The specific prompts and detailed rubrics for each agent are stored in `.agents/skills/cv-brainstormer/agents/`. Do not duplicate them here.
