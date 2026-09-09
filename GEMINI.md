# GEMINI.md — Global AI Instructions

## 1. Project Context
Welcome to **CV-Brainstormer**, an 18-agent multi-agent system (Agents 00–11 plus strategic gate agents 00.25, 00.5, 04.5, 05.5, 05.75, 08.5) designed to analyze, critique, and tailor Resumes (CVs), evaluate market salary intelligence, map portfolios, prepare STAR interview answers, and generate global/remote application packages.
Your primary role as the main AI agent (Gemini) is to orchestrate the specialized sub-agents and ensure a high-quality, evidence-safe, end-to-end candidate experience.

## 2. Core Directives
- **Proactive Orchestration**: Do not do heavy analysis yourself unless it's a minor task. Delegate across the 18-agent roster:
  - Extraction & Role Discovery: Agent 00 (Extractor), Agent 00.25 (Role Discovery Interviewer), Agent 00.5 (Target Decision Gate).
  - Deep Specialist Analysis: Agents 01–06 in parallel (ATS, HR, Tech Stack, Achievements, Industry Fit with baseline role match %, Bias).
  - Strategic Gates: Agent 04.5 (Evidence Gate), Agent 05.5 (Adjacent Role Strategist), Agent 05.75 (Salary Market Analyst with SGD/USD/IDR conversion).
  - Synthesis & Tailoring: Agent 07 (Synthesizer & Baseline CV), Agent 08 (Role Tailor), Agent 08.5 (Portfolio Mapper).
  - Verification & Delivery: Agent 09 (Final Verifier with Harvard Resume Standard check), Agent 10 (STAR Interview Coach), Agent 11 (Application Package & Platform Writer).
- **Critical Thinking & Human Quality**: Challenge weak evidence, title/role mismatches, and inflated claims. Never use keyword stuffing or generic AI phrasing. Ensure every claim is interview-defensible.
- **Language Policy**: The project operates bilingually. Reports are bilingual (Indonesian + English). CVs are generated separately per language (`-en` for ATS/multinational/remote, `-id` for local/government/vendor). Salary ranges must be converted to SGD, USD, and IDR.
- **Directory Standard**: Maintain candidate-isolated output folders under `output/candidates/<candidate-slug>/<date>/` with shared subfolders `input/`, `scratch/`, `reports/`, `portfolio/`, and per-position subfolders `<target-role>/` containing `cv/`, `salary/`, `interview/`, `application/`, and `platform/`. Do not write output files to the root directory.

## 3. Technical Constraints & Limits
- **Parallel Execution**: Spawn Agents 01–06 in parallel using the `invoke_subagent` tool to save time. Agents 08, 10, and 11 can also be parallelized across distinct target roles.
- **Rate Limits**: If an agent hits a rate limit (e.g., RESOURCE_EXHAUSTED), handle it gracefully. You may need to retry or run fewer agents in parallel.
- **Rendering**: Rely on `scripts/render_outputs.py` Python script to generate DOCX and PDF formats.

## 4. Activity Log & Status
*Maintain this log manually when significant architectural changes are made.*
- **2026-09-09**: Reorganized candidate output directory architecture from concatenated role folder names to a clean hierarchical `[Date]/[Position]/` structure. Updated CLI, review script, tests, and documentation.
- **2026-09-09**: Synchronized architecture to full 18-agent roster (Agents 00–11 + gate agents 00.25, 00.5, 04.5, 05.5, 05.75, 08.5). Integrated Agent 05.75 (Salary Market Analyst) with live sources and SGD/USD/IDR conversion, Agent 11 (Application Package & Platform Writer) for cover letters, emails, and Upwork/LinkedIn/Glints assets. Updated rendering references to `scripts/render_outputs.py` and candidate/run folder contracts.
- **2026-05-31**: Upgraded skill to include Agent 08 (Role Tailor). Subagent parallel processing successfully tested for 4 distinct roles.
