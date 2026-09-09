# CV Brainstormer — Runner Guide
*How to run this system on different AI platforms.*
*Cara menjalankan sistem ini di berbagai platform AI.*

---

## Overview / Gambaran Umum

CV Brainstormer uses an 18-agent roster (Agents 00–11 plus strategic gate agents 00.25, 00.5, 04.5, 05.5, 05.75, and 08.5). The end-to-end execution flow is:

```text
Input CV/Form 
  → Agent 00 (Extractor)
  → Agent 00.25 (Role Discovery Interviewer)
  → Agent 00.5 (Target Decision Gate)
  → [Agents 01–06 in parallel: ATS, HR, Tech, Achievement, Industry Fit, Bias]
  → Agent 04.5 (Evidence Gate)
  → Agent 05.5 (Adjacent Role Strategist)
  → Agent 05.75 (Salary Market Analyst: SGD/USD/IDR)
  → Agent 07 (Synthesizer & Baseline CV)
  → Agent 08 (Role Tailor: -en & -id per role)
  → Agent 08.5 (Portfolio Mapper)
  → Agent 09 (Final Verifier + Harvard Resume Gate)
  → Agent 10 (STAR Interview Coach)
  → Agent 11 (Application Package & Platform Writer)
  → Verified Output & Rendering
```

All agent prompt files are located in `.agents/skills/cv-brainstormer/agents/`. You can run them by:
1. Providing the agent's markdown prompt as the **system prompt** or **instruction**.
2. Supplying the structured input (CV, candidate brief, or outputs from preceding agents).
3. Storing outputs in the isolated candidate run directory.

---

## Output Structure & Folder Contract / Struktur Output

Outputs are strictly isolated per candidate and per run to support multiple candidates without data collisions:

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
```

- **`<candidate-slug>`**: Lowercase ASCII kebab-case name (e.g., `rafli-arraafi`).
- **`<candidate_file_slug>`**: Lowercase underscore name for CV filenames (e.g., `rafli_arraafi`).
- **`<run-id>`**: `YYYY-MM-DD-<primary-target-slug>` (e.g., `2026-06-01-data-analyst-application-support`).

---

## Input Preparation & Initialization / Persiapan Input

### Option A — Existing CV File (Recommended)
Initialize the run folder and prepare inputs with `scripts/review-cv`:

```bash
scripts/review-cv "Candidate Name" /path/to/cv.pdf --roles "Data Analyst, Application Support" --projects /path/to/projects-list.md
```

This automated script:
1. Creates `output/candidates/<candidate-slug>/<run-id>/` and subdirectories.
2. Extracts plain text from the PDF/DOCX into `input/extracted.txt`.
3. Copies `projects-list.md` and generates `input/target-brief.md`.
4. Updates `LATEST.md` to point to this newest run.
5. Prints the exact prompt to paste into your agent runner.

### Option B — Building from Scratch (No Existing CV)
1. Open `templates/cv-input-form.md`.
2. Fill in all background, experience, skills, and target fields.
3. Save to `output/candidates/<candidate-slug>/<run-id>/input/extracted.txt` and run Agent 00.

---

## Platform Instructions / Instruksi per Platform

### 🤖 Claude (claude.ai)

**Using Claude Projects:**
1. Create a new Project in Claude for the candidate.
2. Upload all files from `.agents/skills/cv-brainstormer/agents/` as Project Knowledge.
3. Add `references/harvard-resume-standard.md` to Project Knowledge.
4. Execute phases sequentially:
   > "Act as Agent 00 — Extractor. Normalize the following raw CV text: [paste text from input/extracted.txt]"
5. Run Agent 00.25 (Role Discovery) and Agent 00.5 (Target Decision Gate) to confirm target roles.
6. Run Agents 01–06 (in separate chats or sequentially), then Agent 04.5 (Evidence Gate), Agent 05.5 (Adjacent Roles), and Agent 05.75 (Salary Market Analyst).
7. Synthesize with Agent 07, tailor CV variants with Agent 08, verify with Agent 09, prep STAR answers with Agent 10, and draft application packages with Agent 11.

---

### 💻 Claude Code (Terminal)

```bash
RUN_DIR="output/candidates/rafli-arraafi/2026-06-01-data-analyst-application-support"
AGENTS_DIR=".agents/skills/cv-brainstormer/agents"

# Step 00: Extractor
claude -p "$(cat ${AGENTS_DIR}/00-extractor.md)" < "${RUN_DIR}/input/extracted.txt" \
  > "${RUN_DIR}/scratch/00-structured-cv.md"

# Step 00.25 & 00.5: Role Discovery & Target Decision Gate
claude -p "$(cat ${AGENTS_DIR}/00.25-role-discovery-interviewer.md)" < "${RUN_DIR}/scratch/00-structured-cv.md" \
  > "${RUN_DIR}/scratch/00-role-discovery.md"
claude -p "$(cat ${AGENTS_DIR}/00.5-target-decision-gate.md)" < "${RUN_DIR}/scratch/00-role-discovery.md" \
  > "${RUN_DIR}/scratch/00-target-decision.md"

# Steps 01–06: Parallel specialist reviews
for i in 01 02 03 04 05 06; do
  claude -p "$(cat ${AGENTS_DIR}/${i}-*.md)" < "${RUN_DIR}/scratch/00-structured-cv.md" \
    > "${RUN_DIR}/scratch/step-${i}-report.md" &
done
wait

# Step 04.5, 05.5, 05.75: Evidence, Adjacent Roles, Salary Intelligence
claude -p "$(cat ${AGENTS_DIR}/04.5-evidence-gate.md)" < "${RUN_DIR}/scratch/step-04-report.md" \
  > "${RUN_DIR}/scratch/step-04.5-evidence.md"
claude -p "$(cat ${AGENTS_DIR}/05.5-adjacent-role-strategist.md)" < "${RUN_DIR}/scratch/step-05-report.md" \
  > "${RUN_DIR}/scratch/step-05.5-adjacent.md"
claude -p "$(cat ${AGENTS_DIR}/05.75-salary-market-analyst.md)" < "${RUN_DIR}/scratch/step-05.5-adjacent.md" \
  > "${RUN_DIR}/salary/data-analyst/salary-market-data-analyst.md"

# Step 07: Synthesizer
claude -p "$(cat ${AGENTS_DIR}/07-synthesizer.md)" < "${RUN_DIR}/scratch/00-structured-cv.md" \
  > "${RUN_DIR}/reports/final-report-bilingual.md"

# Step 08: Role Tailor
claude -p "$(cat ${AGENTS_DIR}/08-role-tailor.md)" < "${RUN_DIR}/reports/final-report-bilingual.md" \
  > "${RUN_DIR}/cv/data-analyst/cv-rafli_arraafi-data-analyst-en.md"

# Step 08.5: Portfolio Mapper
claude -p "$(cat ${AGENTS_DIR}/08.5-portfolio-mapper.md)" < "${RUN_DIR}/input/projects-list.md" \
  > "${RUN_DIR}/portfolio/projects-from-list.md"

# Step 09: Final Verifier (Harvard Check)
claude -p "$(cat ${AGENTS_DIR}/09-final-verifier.md)" < "${RUN_DIR}/cv/data-analyst/cv-rafli_arraafi-data-analyst-en.md" \
  > "${RUN_DIR}/reports/delta-report-bilingual.md"

# Step 10: STAR Interview Coach
claude -p "$(cat ${AGENTS_DIR}/10-star-interview-coach.md)" < "${RUN_DIR}/cv/data-analyst/cv-rafli_arraafi-data-analyst-en.md" \
  > "${RUN_DIR}/interview/data-analyst/star-data-analyst-en.md"

# Step 11: Application Package Writer
claude -p "$(cat ${AGENTS_DIR}/11-application-package-writer.md)" < "${RUN_DIR}/cv/data-analyst/cv-rafli_arraafi-data-analyst-en.md" \
  > "${RUN_DIR}/application/data-analyst/cover-letter-data-analyst-en.md"
```

---

### 🔲 Codex (OpenAI)

1. Set candidate run context from `output/candidates/<candidate-slug>/<run-id>/input/target-brief.md`.
2. Supply agent `.md` content as System Instruction.
3. Pass structured input to Agent 00 → 00.25 → 00.5.
4. Run Agents 01–06, 04.5, 05.5, and 05.75.
5. Synthesize (07), tailor roles (08), verify (09), prep STAR (10), and generate application/platform packages (11).

---

### 🌌 Antigravity

1. Import `.agents/skills/cv-brainstormer/agents/` into Antigravity subagent registry.
2. Configure pipeline fan-out:
   - Extractor (00) → Role Discovery (00.25) → Target Gate (00.5)
   - Fan-out to Agents 01–06 concurrently.
   - Fan-in to Evidence Gate (04.5) → Adjacent Role Strategist (05.5) → Salary Market Analyst (05.75).
   - Synthesizer (07) produces bilingual baseline.
   - Fan-out to Role Tailor (08) per role/language.
   - Portfolio Mapper (08.5) aligns evidence.
   - Final Verifier (09) performs Harvard gate check.
   - STAR Interview Coach (10) and Application Package Writer (11) generate candidate delivery assets.

---

## Output Rendering / Render Output

Convert Markdown files into professional `.docx` and `.pdf` documents using `scripts/render_outputs.py`:

```bash
# Render bilingual final report
python scripts/render_outputs.py output/candidates/<candidate-slug>/<run-id>/reports/final-report-bilingual.md

# Render CV variants (English & Indonesian)
python scripts/render_outputs.py output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-<candidate_file_slug>-data-analyst-en.md \
                                output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-<candidate_file_slug>-data-analyst-id.md

# Render salary market analysis
python scripts/render_outputs.py output/candidates/<candidate-slug>/<run-id>/salary/data-analyst/salary-market-data-analyst.md

# Render STAR interview prep
python scripts/render_outputs.py output/candidates/<candidate-slug>/<run-id>/interview/data-analyst/star-data-analyst-en.md

# Render application package documents
python scripts/render_outputs.py output/candidates/<candidate-slug>/<run-id>/application/data-analyst/cover-letter-data-analyst-en.md
```

---

## Quick Reference / Referensi Cepat (18-Agent Roster)

| Agent | Prompt File | Input | Output Deliverables |
|---|---|---|---|
| **00 Extractor** | `00-extractor.md` | Raw CV (PDF/DOCX/text) | `scratch/00-structured-cv.md` |
| **00.25 Role Discovery** | `00.25-role-discovery-interviewer.md` | Structured CV + history | Diagnostic role classification & true level |
| **00.5 Target Gate** | `00.5-target-decision-gate.md` | Discovery output + target brief | Locked target roles, market, single/dual track |
| **01 ATS Scanner** | `01-ats-scanner.md` | Structured CV | ATS score, formatting errors, keyword density |
| **02 HR Impression** | `02-hr-first-impression.md` | Structured CV | 6-second scan, tone, red flags |
| **03 Tech Reviewer** | `03-tech-stack-reviewer.md` | Structured CV | Stack credibility, outdated tech, market demand |
| **04 Achievement Auditor** | `04-achievement-auditor.md` | Structured CV | Responsibility vs Achievement ratio, STAR quantification |
| **04.5 Evidence Gate** | `04.5-evidence-gate.md` | Tech & Achievement reports | Claim classification (proven/project/risky/remove) |
| **05 Industry Analyst** | `05-industry-analyst.md` | Structured CV + target JD | Industry fit, previous CV role match % |
| **05.5 Adjacent Roles** | `05.5-adjacent-role-strategist.md` | Industry & Evidence outputs | Recommended adjacent roles & feasibility bands |
| **05.75 Salary Analyst** | `05.75-salary-market-analyst.md` | Decision, Strategy & Market data | `salary/<role>/salary-market-<role>.md` (SGD/USD/IDR) |
| **06 Bias Checker** | `06-bias-checker.md` | Structured CV | Privacy scan, bias signals, inclusive language |
| **07 Synthesizer** | `07-synthesizer.md` | All 00–06.x outputs | `reports/final-report-bilingual.md` + baseline CV |
| **08 Role Tailor** | `08-role-tailor.md` | Baseline CV + Target role | `cv/<role>/cv-<slug>-<role>-en.md` & `-id.md` |
| **08.5 Portfolio Mapper** | `08.5-portfolio-mapper.md` | `input/projects-list.md` + Roles | `portfolio/projects-from-list.md` (proof & gaps) |
| **09 Final Verifier** | `09-final-verifier.md` | Tailored CV + previous scores | `reports/delta-report-bilingual.md` (Harvard Gate) |
| **10 STAR Coach** | `10-star-interview-coach.md` | Verified CV + Evidence Gate | `interview/<role>/star-<role>-en.md` & `-id.md` |
| **11 Application Writer** | `11-application-package-writer.md` | Verified CV + Target context | `application/<role>/` (cover letters, emails) & `platform/<role>/` (Upwork, LinkedIn, Glints) |

---

## Pro Tips / Tips Penting

- **Never skip Agent 00 & 00.25**: If official title (e.g., "Staff IT") does not match actual daily work (e.g., SQL query fixes, bug triage, SLA tracking), Agent 00.25's diagnostic classification is the single source of truth.
- **Enforce the Evidence Gate (04.5)**: Any skill or achievement marked `Risky` or `Remove` must never be written as a strong claim in the final CV.
- **Live Salary & FX Verification (05.75)**: Compensation ranges must always cite fresh reputable sources (Hays, Michael Page, Levels.fyi, NodeFlair) with access dates and explicit SGD, USD, and IDR currency conversions.
- **Harvard Resume Standard Gate (09)**: Agent 09 must rate the final CV as `Pass`, `Minor Issues`, or `Needs Revision`. A status of `Needs Revision` blocks declaring the CV ready to submit.
- **Service-Positioning for Upwork (11)**: Upwork assets in `platform/<role>/upwork.md` must focus on client problems, deliverables, scope, turnaround, and proof of work, rather than a resume dump.

