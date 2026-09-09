---
name: cv-brainstormer
description: >
  Multi-agent system to analyze, improve, and generate professional ATS-friendly CVs.
  Use when user wants to: create, review, fix, or analyze a CV; check ATS compliance;
  get HR feedback; improve achievement bullets; check bias; or tailor CV for a target role.
  Triggers: "review CV", "perbaiki CV", "buat CV", "CV saya kurang apa", "ATS CV",
  "HR suka CV yang gimana", "CV yang bagus", "bikin CV dari nol", "CV brainstorm",
  or when user pastes CV content and asks for feedback.
  Runs multi-agent workflow (agents 00-11 + gate agents 00.25, 00.5, 04.5, 05.75, 08.5).
  Outputs: bilingual report (ID+EN), role-tailored CVs per language, portfolio mapping,
  STAR interview prep, application package, and platform packages (LinkedIn, Upwork, Glints)
  in .md, .docx, and .pdf.
---

# CV Brainstormer — Multi-Agent CV Analysis System

## Overview

This system analyzes CVs from multiple specialist perspectives, producing a comprehensive report with scores, a priority fix list, evidence checks, role match percentages from the original CV, portfolio mapping, a revised CV, STAR interview prep, application packages for global/remote job applications, and platform packages for LinkedIn/Upwork. Reports are bilingual (Indonesian + English). Final CVs are generated separately per language (`-en` and `-id`) so that ATS-optimized English and local market needs don't get mixed.

Agents in this workflow must think critically. They must not simply agree with the user's framing if the target role is unclear, evidence is weak, claims are inflated, or the role context is off. CV-writing agents must produce human-quality copywriting: natural, specific, not stiff, no keyword stuffing, and always interview-defensible.

This workflow also applies a Harvard-inspired resume quality layer from `references/harvard-resume-standard.md`. This layer requires CVs to be tailored, specific, action-oriented, factual, easy to scan by humans and ATS, consistently formatted, and free of overclaims. Agent 09 must assign a status of `Pass`, `Minor Issues`, or `Needs Revision` for this standard before a CV can be called ready to send.

**Flow:**
```
Input CV / Form → Agent 00 (Extractor) → Agent 00.25 (Role Discovery Interviewer) → Agent 00.5 (Target Decision Gate) → Agent 01–06 (parallel, including Previous CV Role Match in Agent 05) → Agent 04.5 (Evidence Gate) → Agent 05.5 (Adjacent Role Strategist) → Agent 05.75 (Salary Market Analyst) → Agent 07 (Synthesizer) → Agent 08 (Role Tailor) → Agent 08.5 (Portfolio Mapper) → Agent 09 (Final Verifier + post-rewrite match check) → Agent 10 (STAR Interview Coach) → Agent 11 (Application Package Writer) → Verified Output
```

**Output Root:**

All outputs must go into the candidate and run folder so the workflow can be used by multiple people without overwriting each other:

```text
output/candidates/<candidate-slug>/<run-id>/
```

Example:

```text
output/candidates/rafli-arraafi/2026-06-01-data-analyst-application-support/
```

---

## How to Run

### Quick Start — Initialize a Candidate Run

Use the following script to create the candidate/run folder, copy inputs, generate `target-brief.md`, and print a short prompt for the agent:

```bash
scripts/review-cv "Candidate Name" /path/to/cv.pdf --roles "Data Analyst, Application Support" --projects /path/to/projects-list.md
```

Example:

```bash
scripts/review-cv "Rafli Arraafi" CV_Rafli_Arraafi_ID.pdf --roles "Data Analyst, Application Support" --projects input/projects-list.md
```

### Step 1 — Determine the Input Path

**Path A: Has an existing CV**
- Ask the user to paste their CV text, or
- Run `scripts/extract.py` to convert PDF/DOCX → text
- Proceed to Step 2

**Path B: No existing CV / starting from scratch**
- Ask the user to fill out `templates/cv-input-form.md`
- Proceed to Step 2

### Step 2 — Run Agent 00 (Extractor)
Read `agents/00-extractor.md` and normalize the input CV into a structured format.

### Step 2.25 — Run Agent 00.25 (Role Discovery Interviewer)
Read `agents/00-role-discovery-interviewer.md`. Start from the CV: first classify the candidate's general domain, initial role family, level, and any mismatch between their official title and actual work. Then ask universal and domain-specific diagnostic questions as appropriate.

This agent must work for both general and tech candidates. Do not force tech-specific questions on non-tech candidates. For tech/support candidates, the agent must differentiate L1, L2, L3, Production Support, Application Support, SQL/Data Support, Manual QA, SysAdmin, and DevOps based on actual work evidence, not company-assigned titles.

### Step 2.5 — Run Agent 00.5 (Target Decision Gate)
Read `agents/00-target-decision-gate.md`. Determine the primary target, secondary target, market, output language, single/dual-track strategy, and what should be downplayed or removed from the CV.

Use Agent 00.25 output as the primary source of truth when there is a conflict between title and actual work.

If the target role is conflicting or too broad, ask the user to choose before proceeding.

### Step 3 — Run Agents 01–06 (parallel)
Use Agent 00's output as input for all of the following agents simultaneously:
- `agents/01-ats-scanner.md` — ATS compliance
- `agents/02-hr-first-impression.md` — HR first impression
- `agents/03-tech-stack-reviewer.md` — Tech stack relevance (web search allowed)
- `agents/04-achievement-auditor.md` — Achievement vs responsibility
- `agents/05-industry-analyst.md` — Industry fit & JD alignment
- `agents/06-bias-checker.md` — Bias & inclusion check

Also use the Harvard checklist from `input/harvard-resume-checklist.md` if available, or fall back to `references/harvard-resume-standard.md`.

Agent 05 must calculate a `Previous CV Role Match` for each target role from the original/pre-rewrite CV. This is the baseline match percentage of the old CV against the target role/JD, not the final CV score.

### Step 3.5 — Run Agent 04.5 (Evidence Gate)
Read `agents/04-evidence-gate.md`. Classify claims, skills, projects, and metrics as:
- Proven
- Project-backed
- Exposure
- Learning
- Risky
- Remove

Claims with a Risky/Remove status must not appear as strong claims in the final CV.

### Step 3.75 — Run Agent 05.5 (Adjacent Role Strategist)
Read `agents/05-adjacent-role-strategist.md`. This agent recommends the closest realistic positions based on:
- Target title and the candidate's title history
- Job description if available, or current market requirements if no JD is provided
- The candidate's genuinely proven achievements
- Evidence strength and missing proof

This agent may reject or downgrade the user's target role if evidence is insufficient, and then provide a more realistic alternative path.

### Step 3.875 — Run Agent 05.75 (Salary Market Analyst)
Read `agents/05-salary-market-analyst.md`. For each target role that survives Agent 05.5, analyze current compensation ranges by market, level, and work model.

This agent must:
- Use live/current salary references at generation time.
- Cite each salary source with URL/source name and access date.
- Record the generated date and FX date.
- Convert salary ranges into SGD, USD, and IDR using current exchange rates.
- Separate monthly, annual, hourly, contract, and freelance ranges.
- State confidence level and data quality.
- Refuse to present stale or unverified ranges as current.

Output must go in:

```text
output/candidates/<candidate-slug>/<run-id>/salary/<target-role>/salary-market-<target-role>.md
```

This salary report is advisory, not a legal/financial guarantee. It exists to help the user understand what the market can plausibly pay for the role and how to negotiate without underpricing themselves.

### Step 4 — Run Agent 07 (Synthesizer)
Read `agents/07-synthesizer.md`. Provide all outputs from Agents 00–06 as input.
Output: Full bilingual report + revised CV draft. This agent must resolve inter-agent conflicts, maintain role context, write CV copy with natural and defensible human copywriting, and include a Harvard Resume Quality Check.

### Step 5 — Run Agent 08 (Role Tailor)
Use insights from Agent 05 (Industry Analyst) about relevant roles, or ask the *user* to specify their target positions.
Spawn parallel subagents if available, or run locally, to read instructions in `agents/08-role-tailor.md` and adapt the CV output from Agent 07 to align with each target role. Generate *separate files* per role and language using the candidate file slug with underscores, e.g. `cv-rafli_arraafi-data-analyst-en.md` and `cv-rafli_arraafi-data-analyst-id.md`.

### Step 5.5 — Run Agent 08.5 (Portfolio Mapper)
Read `agents/08-portfolio-mapper.md`. Map the user's real projects to target roles, determine which projects to feature, which to downplay, and what portfolio artifacts are missing (README, screenshot, SQL snippet, demo, or mockup).

### Step 6 — Render Output (optional, requires Python)
```bash
python scripts/render_outputs.py output/candidates/<candidate-slug>/<run-id>/reports/final-report-bilingual.md
python scripts/render_outputs.py output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-<candidate_file_slug>-data-analyst-en.md output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-<candidate_file_slug>-data-analyst-id.md
```
Generates `.docx` and `.pdf` from the report and various CV variants.

### Step 7 — Run Agent 09 (Final Verifier)
Read `agents/09-delta-verifier.md`. Run **two parallel subagents** (re-run Agent 01 + Agent 04) against the CV variant to verify, e.g. `output/candidates/<candidate-slug>/<run-id>/cv/general/cv-<candidate_file_slug>-revised-en.md` or `output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-<candidate_file_slug>-data-analyst-en.md`, then run the Delta Synthesizer which reads:
- Original scores from Agent 07
- Re-run results from Agent 01 & 04
- Priority Fix List from Agent 07 (to verify which items have been applied)
- Target Decision Gate output
- Evidence Gate output
- Portfolio Mapper output

Output is saved in the candidate/run reports folder, e.g. `output/candidates/<candidate-slug>/<run-id>/reports/delta-report-bilingual.md` (+ `.docx` + `.pdf`) if delta verification is needed.

Agent 09 must include a `Harvard Resume Standard Check` with a status of `Pass`, `Minor Issues`, or `Needs Revision`. A status of `Needs Revision` means the CV may still be rendered, but must not be called ready to send.

Agent 09 must also include a `Role Match Delta`:
- `Previous CV Role Match`: score from Agent 05 against the original CV
- `Revised CV Role Match`: score against the final role variant CV
- `Delta`: percentage change and primary reasons for increase/decrease

**Variant Mode:** If the user wants to check a specific role variant (e.g. `output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-<candidate_file_slug>-data-analyst-en.md`), call Agent 09 again with that file as input. Output: `output/candidates/<candidate-slug>/<run-id>/reports/delta-report-{role}-bilingual.md`

### Step 8 — Run Agent 10 (STAR Interview Coach)
Read `agents/10-star-interview-coach.md`. Create a STAR interview story bank based on the final CV, evidence gate, role discovery, portfolio mapping, verification report, and user clarifications.

Output must go in the interview folder per role:

```text
output/candidates/<candidate-slug>/<run-id>/interview/<target-role>/
```

Each role must have English and Indonesian versions if the role's CV was also generated in both languages.

### Step 9 — Run Agent 11 (Application Package Writer)
Read `agents/11-application-package-writer.md`. Create application packages and platform profiles for global/remote targets based on the verified final CV, target roles, JD/company context if available, portfolio mapper, and STAR story bank.

Output must go in the application folder per role:

```text
output/candidates/<candidate-slug>/<run-id>/application/<target-role>/
```

Minimum output for global/remote targets:
- `cover-letter-<target-role>-en.md`
- `email-application-<target-role>-en.md`
- `email-follow-up-<target-role>-en.md`

If a local/Indonesian target is also requested, create `-id.md` versions with a natural tone for the local market. Do not produce raw translations from English.

For platform profiles such as Upwork, LinkedIn, Glints, JobStreet, or other marketplaces/job boards, output must be one file per platform:

```text
output/candidates/<candidate-slug>/<run-id>/platform/<target-role>/
```

Example platform output:
- `upwork.md`
- `linkedin.md`
- `glints.md`

Each platform file must include:
- `Platform Opportunity Analysis`: candidate's prospects on the platform, estimated match percentage, main obstacles, and best strategy.
- `Recommended Positioning`: the most promising angle for that platform.
- `Profile Copy`: headline/title, summary/about/overview, and skills/tags as needed by the platform.
- `Application Assets`: proposal, message, pitch, or apply note as relevant.

Upwork packages must include `Upwork Service Match` as an estimated percentage of how well the candidate's CV/proof matches the service offered on Upwork. This differs from `Previous CV Role Match` because Upwork evaluates service-market fit, proof of work, niche clarity, and proposal strength.

---

## Agent Reference

| File | Agent | Domain |
|------|-------|--------|
| `agents/00-extractor.md` | Extractor | Normalizes CV into a structured format |
| `agents/00-role-discovery-interviewer.md` | Role Discovery Interviewer | Determines actual role family and level via diagnostic questions when title/target role are misaligned |
| `agents/00-target-decision-gate.md` | Target Decision Gate | Determines target role, market, language, and strategy before analysis |
| `agents/01-ats-scanner.md` | ATS Scanner | ATS compliance, keyword density, formatting |
| `agents/02-hr-first-impression.md` | HR First Impression | 6-second scan, tone, red flags |
| `agents/03-tech-stack-reviewer.md` | Tech Stack Reviewer | Skill credibility, market relevance, web search |
| `agents/04-achievement-auditor.md` | Achievement Auditor | STAR method, action verbs, quantification |
| `agents/04-evidence-gate.md` | Evidence Gate | Verifies claim evidence for skills, projects, and metrics to prevent overclaiming |
| `agents/05-industry-analyst.md` | Industry Analyst | JD alignment, gap analysis, competitive positioning |
| `agents/05-adjacent-role-strategist.md` | Adjacent Role Strategist | Recommends closest positions based on title, JD/market requirements, and achievements |
| `agents/05-salary-market-analyst.md` | Salary Market Analyst | Current salary range research, source validation, SGD/USD/IDR conversion, and negotiation positioning |
| `agents/06-bias-checker.md` | Bias & Inclusion Checker | Unnecessary personal info, privacy, inclusive language |
| `agents/07-synthesizer.md` | Synthesizer / Human CV Writer | Compiles all outputs → priority list + revised CV with human copywriting |
| `agents/08-role-tailor.md` | Role Tailor / Copywriter | Adapts CV content for specific roles/positions naturally and defensibly |
| `agents/08-portfolio-mapper.md` | Portfolio Mapper | Maps real projects to roles and identifies portfolio gaps |
| `agents/09-delta-verifier.md` | Final Verifier | Re-runs ATS + Achievement, checks role fit, evidence risk, interview defensibility, portfolio completeness |
| `agents/10-star-interview-coach.md` | STAR Interview Coach | Creates role-specific STAR interview story bank from verified CV claims |
| `agents/11-application-package-writer.md` | Application Package Writer | Creates cover letters, application emails, follow-up emails, and one platform file per channel (Upwork, LinkedIn, Glints) |

---

## Scoring System

Each agent produces a score of **0–100** with a category label:
- **0–40:** Poor
- **41–60:** Fair
- **61–80:** Good
- **81–100:** Excellent

Agent 07 combines all scores with the following weights:

| Agent | Weight |
|-------|--------|
| Achievement Quality | 25% |
| ATS Compliance | 20% |
| HR First Impression | 20% |
| Industry Fit | 15% |
| Tech Stack | 15% |
| Bias & Inclusion | 5% |

---

## Priority Fix System

All findings are classified as:
- 🔴 **Critical** — fix before sending any application
- 🟠 **High** — fix this week
- 🟡 **Medium** — fix this month
- 🟢 **Low** — polish, nice to have

---

## Generated Output

1. **Full Report** (`output/candidates/<candidate-slug>/<run-id>/reports/final-report-bilingual.md` / `.docx` / `.pdf`) — comprehensive bilingual report with per-agent scores, priority fix list, and detailed findings
2. **Salary Market Report** (`output/candidates/<candidate-slug>/<run-id>/salary/<role>/salary-market-<role>.md`) — current salary range analysis with reliable references, SGD/USD/IDR conversion, confidence level, and negotiation guidance
3. **CV Role Variants** (`output/candidates/<candidate-slug>/<run-id>/cv/<role>/cv-<candidate_file_slug>-<role>-en.md` and `cv-<candidate_file_slug>-<role>-id.md`) — ready-to-use CV versions per role and language
4. **Portfolio Summary** (`output/candidates/<candidate-slug>/<run-id>/portfolio/projects-from-list.md`) — portfolio summary from the user's project list, if available
5. **STAR Interview Story Bank** (`output/candidates/<candidate-slug>/<run-id>/interview/<role>/star-<role>-en.md` and `star-<role>-id.md`) — role-specific, interview-defensible STAR interview answers
6. **Application Package** (`output/candidates/<candidate-slug>/<run-id>/application/<role>/`) — cover letter, application email, and follow-up email for global/remote roles
7. **Platform Packages** (`output/candidates/<candidate-slug>/<run-id>/platform/<role>/upwork.md`, `linkedin.md`, `glints.md`) — per-platform opportunity analysis, recommended positioning, profile copy, skills/tags, and application/proposal assets as needed

---

## Design Decisions

| Parameter | Value |
|-----------|-------|
| Output language | Reports bilingual; CVs split into English (`-en`) and Indonesian (`-id`) |
| Target industry | Generalist — all industries |
| Input | File upload (PDF/DOCX) OR fill out form from scratch |
| Target JD | Optional — agents infer if absent, request clarification if ambiguous |
| Web search | Required for Agent 05.75 salary research; allowed for Agent 03 (Tech Stack Reviewer) |
| Scoring | Numeric 0–100 + category labels |

---

## Usage Tips

- **Provide a target JD** to Agent 05 if available — significantly improves industry fit analysis accuracy
- **Run Agents 01–06 in parallel** to save time — they do not depend on each other
- **Iterate** — after the CV is revised, re-run all agents for second-pass improvement
- **Agent 03 can search** — validates skill market demand more accurately with current data

---

## Scripts

| Script | Function |
|--------|----------|
| `scripts/review-cv` | Initializes the candidate/run folder and prints a short agent prompt |
| `scripts/extract.py` | Extracts text from PDF or DOCX to plain text if available |
| `scripts/render_outputs.py` | Converts `.md` reports/CVs to `.docx` and `.pdf` |

**Install dependencies:**
```bash
pip install pdfplumber python-docx markdown weasyprint --break-system-packages
```

---

## Platform Support

This skill can be run on: **Claude** (Projects), **Claude Code** (terminal), **Codex**, **Kiro**, **Antigravity**, or any other AI agent runner.
See `references/runner-guide.md` for per-platform instructions.

---

## References

| File | Contents |
|------|----------|
| `references/runner-guide.md` | Instructions for running on Claude, Codex, Kiro, Antigravity, Claude Code |
| `references/sample-report-output.md` | Full example of Agent 07 output — standard format and analysis depth |
| `references/sample-cv-before-after.md` | Example CV transformation before and after processing — quality benchmark |
| `references/sample-interactions.md` | Example trigger phrases, usage scenarios, and edge cases |
| `references/design-spec.md` | Complete architecture design document for this system |
