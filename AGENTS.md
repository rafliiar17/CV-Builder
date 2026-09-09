# AGENTS.md - Specialist Agents Reference

This project utilizes a multi-agent CV workflow with core agents (00-11) plus strategic gate agents (00.25, 00.5, 04.5, 05.75, 08.5) to prevent generic, overclaimed, underpriced, or role-misaligned CVs.

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

Use English CVs for ATS-heavy portals, startups, multinational companies, and LinkedIn/JobStreet applications. Use Indonesian CVs for local/government/vendor roles that expect Bahasa Indonesia.

For CV filenames, use a candidate file slug with underscores derived from the candidate name, followed by the target role slug. Example: `cv-rafli_arraafi-application-support-en.md`.

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
| **05.75** | **Salary Market Analyst** | Deep-reviews current salary ranges for the target role/market, cites reliable fresh sources, converts ranges to SGD, USD, and IDR, and states negotiation positioning. |
| **06** | **Bias Checker** | Scans for unnecessary personal info (age, religion, photo) and inclusive language. |
| **07** | **Synthesizer / Human CV Writer** | Compiles reports, resolves conflicts, and writes a human, role-aware, evidence-safe baseline CV. |
| **08** | **Role Tailor / Copywriter** | Tailors the baseline CV to specific target roles with natural human copywriting, interview-defensible wording, and anti-slop principles. |
| **08.5** | **Portfolio Mapper** | Maps real projects to target roles and identifies portfolio gaps, screenshots, READMEs, demos, or SQL proof needed. |
| **09** | **Final Verifier** | Re-runs ATS + achievement scoring and checks role fit, evidence risk, interview defensibility, portfolio completeness, and output structure. |
| **10** | **STAR Interview Coach** | Converts verified CV claims, metrics, and evidence into role-specific STAR interview story banks. |
| **11** | **Application Package Writer** | Creates short, role/company-aware cover letters, application emails, and consolidated platform content (LinkedIn, Upwork, Glints) using structured writing and anti-slop guidelines. |

## Critical Standards

- Agents must not simply agree with user framing. They should challenge unclear targets, unsupported claims, missing context, and weak evidence.
- All CV analysis, writing, tailoring, and verification must apply the Harvard-inspired quality layer from `.agents/skills/cv-brainstormer/references/harvard-resume-standard.md`.
- The Harvard layer is a light gate: it flags major quality issues before a CV is called ready, but it does not block file generation when evidence is incomplete.
- When official title and real work conflict, agents must use Agent 00.25 output as the source of truth for role family and level.
- If QA/testing work exists, agents must distinguish Manual QA / Application Support QA from Automation QA and only claim automation when evidence exists.
- CV writing must be human-readable, specific, and role-native. Avoid generic AI-sounding phrasing and keyword stuffing.
- Every strong claim must be interview-defensible.
- STAR interview answers must be based on verified CV evidence and must include safe boundaries for what not to overclaim.
- Adjacent role recommendations must be based on target title, job description or market requirements, and candidate achievements.
- Agent 05 must include a `Previous CV Role Match` percentage for each target role before rewrite, so the candidate can see how close the original CV was to the target market.
- Agent 05.75 must use current sources at generation time for salary ranges and FX conversion. It must cite source names/URLs, access date, market, role title, level, and confidence. If fresh references or exchange rates cannot be verified, it must say so and avoid presenting the salary range as current.
- Private/internal projects must be described safely without implying public repository access or exposing confidential data.
- If evidence is weak, downgrade wording instead of inflating the candidate.
- Agent 09 must include a `Harvard Resume Standard Check` with `Pass`, `Minor Issues`, or `Needs Revision` before declaring a CV ready to send.
- Agent 11 must not invent company research. If no company/JD context is provided, generate reusable but non-generic drafts with placeholders and clear customization notes.
- Platform outputs must be consolidated into one file per platform, for example `upwork.md`, `linkedin.md`, and `glints.md`. Each platform file must include opportunity analysis, recommended positioning, profile copy, and platform-specific application/proposal content.
- Upwork outputs must be service-positioned, not CV-positioned: focus on client problems, deliverables, proof, scope, turnaround, and proposal hooks. Do not use inflated expert claims unless evidence supports them.
- **Anti-Slop Quality Gate (`no-ai-slop`)**: All platform copy (LinkedIn posts, profile intros, Threads), cover letters, and email outreach must pass the Peter Yang `no-ai-slop` standard (`.agents/skills/no-ai-slop/SKILL.md`). Strip banned buzzwords (*delve, foster, leverage, robust, cutting-edge, paradigm shift, tapestry, supercharge*), faux-insight openers (*"Here's the thing..."*, *"What nobody tells you..."*), binary contrasts (*"It's not X. It's Y."*), and decorative emoji/bold formatting.
- **Proper Content Writing Pipeline (Matt Pocock)**: For thought-leadership posts, case studies, and long-form portfolio stories, use the two-stage writing pipeline:
  1. `writing-fragments` (Explore): Interview and mine raw personal insights, unfiltered opinions, and real project vignettes without imposing early structure.
  2. `writing-shape` / `writing-beats` (Exploit): Structure the draft paragraph-by-paragraph with grounded concepts, deliberate format choices (prose vs. list vs. table), and zero filler before final anti-slop verification.

## Content Creation & Writing Skills

The repository includes localized writing skills under `.agents/skills/` to guarantee authentic, high-impact copy for candidate content and applications:

| Skill | Author | Path | Purpose |
|---|---|---|---|
| **`no-ai-slop`** | Peter Yang | `.agents/skills/no-ai-slop/` | Removes 20+ AI slop patterns, buzzwords, and robotic cadence while preserving author voice. |
| **`writing-fragments`** | Matt Pocock | `.agents/skills/writing-fragments/` | Explore phase: Mines raw observations, punchy lines, and vignettes via intensive interviewing. |
| **`writing-shape`** | Matt Pocock | `.agents/skills/writing-shape/` | Exploit phase: Shapes raw material into disciplined articles/posts paragraph-by-paragraph. |
| **`writing-beats`** | Matt Pocock | `.agents/skills/writing-beats/` | Exploit variant: Assembles content into a narrative journey of beats with progressive grounding. |

## Instructions Location
The specific prompts and detailed rubrics for each agent are stored in `.agents/skills/cv-brainstormer/agents/`. Do not duplicate them here.
