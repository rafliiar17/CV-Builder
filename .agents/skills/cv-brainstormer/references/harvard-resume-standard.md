# Harvard-Inspired Resume Quality Standard

Use this as a shared quality layer for CV Brainstormer. It adapts Harvard FAS Mignone Center for Career Success resume guidance into concise workflow rules.

## Core Principles

- Tailor the CV to the target role. Not every experience must directly match, but the selected evidence should reflect skills the employer values.
- Prefer specific language over general claims.
- Prefer active language over passive wording.
- Write to express, not impress. Avoid flowery, inflated, or generic AI-sounding phrasing.
- Keep claims fact-based. Quantify when evidence supports numbers; qualify when numbers are unavailable.
- Write for people and systems that scan quickly.
- Keep formatting consistent, clean, reverse chronological, and PDF-safe.
- Use recognizable section headers such as `Experience`, `Education`, `Skills`, `Projects`, and `Certifications`.
- Avoid personal pronouns, narrative style, slang, photos, age, gender, and references.
- Use AI as an editing aid. The final CV must authentically represent the candidate and remain interview-defensible.

## Agent Checklist

Before marking a CV or role variant as ready, check:

- Target role is clear and the CV is tailored to it.
- Summary is specific, factual, and 3-5 lines.
- Key information is easy to find in a 6-second scan.
- Experience bullets start with action verbs and show context plus result where possible.
- Metrics are supported by source CV, project notes, user confirmation, or clearly safe estimates.
- Skills are grouped honestly by strength: production, project-backed, exposure, or learning.
- Unsupported ownership claims are downgraded.
- Private/internal projects are described safely.
- Formatting uses simple Markdown, no tables for layout, no columns, and no hidden contact details.
- Output language is separated correctly between English and Indonesian variants.

## Light Gate Labels

- `Pass`: No major issue remains. Minor wording polish may still be possible.
- `Minor Issues`: CV is usable, but has small issues such as a few generic bullets, missing optional metrics, or light scannability improvements.
- `Needs Revision`: CV should not be called ready yet because it has major generic claims, unsupported strong claims, poor scanability, role mismatch, overclaiming, or formatting that can break ATS/human review.

## Safe Wording Downgrades

Use stronger verbs only when evidence supports ownership. Otherwise downgrade:

- `Led migration` -> `Supported migration` or `Contributed to migration`
- `Owned SLA governance` -> `Handled tickets within SLA process`
- `Built analytics platform` -> `Created reporting workbook/dashboard for operational tracking`
- `Expert in Kubernetes` -> `Learning Kubernetes` or `Project exposure to Kubernetes`
- `Automated QA` -> `Performed manual/UAT validation` unless automation scripts are evidenced

## Verification Rule

Agent 09 must include a `Harvard Resume Standard Check` with one light gate label and concrete remaining issues. This check is not a hard blocker for generating files, but it is required before saying a CV is ready to send.
