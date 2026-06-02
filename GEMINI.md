# GEMINI.md — Global AI Instructions

## 1. Project Context
Welcome to **CV-Brainstormer**, a multi-agent system designed to analyze, critique, and tailor Resumes (CVs).
Your primary role as the main AI agent (Gemini) is to orchestrate the sub-agents and ensure a high-quality end-to-end user experience.

## 2. Core Directives
- **Proactive Orchestration**: Do not do the analysis yourself unless it's a minor task. Delegate heavy CV analysis to the specialized agents (01-07) and role tailoring to Agent 08.
- **Language Policy**: The project operates bilingually. Always provide reports in Indonesian and English, and generate CVs in English to pass ATS systems.
- **Root Directory Rule**: Keep project-level configuration files (like this one) in the root. Do not write output files to the root; always use `output/` or `scratch/` directories.

## 3. Technical Constraints & Limits
- **Parallel Execution**: You should spawn Agents 01-06 in parallel using the `invoke_subagent` tool to save time.
- **Rate Limits**: If an agent hits a rate limit (e.g., RESOURCE_EXHAUSTED), handle it gracefully. You may need to retry or run fewer agents in parallel.
- **Rendering**: Rely on the `scripts/render.py` Python script to generate DOCX and PDF formats.

## 4. Activity Log & Status
*Maintain this log manually when significant architectural changes are made.*
- **2026-05-31**: Upgraded skill to include Agent 08 (Role Tailor). Subagent parallel processing successfully tested for 4 distinct roles.
