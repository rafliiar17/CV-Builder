# CV Brainstormer — Runner Guide
*How to run this system on different AI platforms.*
*Cara menjalankan sistem ini di berbagai platform AI.*

---

## Overview / Gambaran Umum

CV Brainstormer uses 8 sequential agents. The general flow is:

```
Input → Agent 00 → [Agent 01–06 in parallel] → Agent 07 → Output
```

Each agent is a `.md` file in the `/agents/` folder. You run them by:
1. Opening the agent's `.md` file
2. Copying the full contents as a **system prompt** or **instruction**
3. Providing the input (CV or previous agent's output)
4. Saving the output for the next agent

---

## Input Preparation / Persiapan Input

### Option A — You have an existing CV file
1. Place your PDF or DOCX in the `/input/` folder
2. Run the extractor script:
   ```bash
   python scripts/extract.py input/your-cv.pdf
   # Output: input/extracted.txt
   ```
3. Use `input/extracted.txt` as input for Agent 00

### Option B — Building from scratch
1. Open `/templates/cv-input-form.md`
2. Fill in all fields
3. Use the filled form directly as input for Agent 00

---

## Platform Instructions / Instruksi per Platform

---

### 🤖 Claude (claude.ai)

**Recommended: Use Claude Projects**

1. Create a new Project in Claude
2. Upload all agent `.md` files as Project Knowledge
3. In each conversation, tell Claude which agent to use:
   > "Act as Agent 00 — Extractor. Here is my CV: [paste CV text]"
4. Save each agent's output in a text file
5. Pass the output to the next agent

**Running agents 01–06 in parallel:**
- Open 6 separate Claude conversations
- Use the same normalized CV (Agent 00 output) in each
- Collect all 6 outputs, then run Agent 07

---

### 💻 Claude Code (Terminal)

```bash
# Install dependencies
pip install anthropic --break-system-packages

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run Agent 00
cat agents/00-extractor.md input/extracted.txt | \
  claude -p "$(cat agents/00-extractor.md)" < input/extracted.txt \
  > output/step-00-normalized.txt

# Run Agents 01-06 (one at a time or parallel)
for i in 01 02 03 04 05 06; do
  claude -p "$(cat agents/${i}-*.md)" < output/step-00-normalized.txt \
    > output/step-${i}-report.txt
done

# Run Agent 07 (Synthesizer)
cat output/step-0*.txt | \
  claude -p "$(cat agents/07-synthesizer.md)" \
  > output/final-report.md
```

---

### 🔲 Codex (OpenAI)

1. Create a new Codex task
2. Set the system prompt to the agent's `.md` file contents
3. Provide CV text as user message
4. Save output, repeat for each agent
5. Final synthesis with Agent 07

**Task file format for Codex:**
```
SYSTEM: [paste agent .md content]
USER: [paste CV or previous output]
```

---

### ⚡ Kiro

1. Create a new spec file referencing each agent:
```yaml
# kiro-spec.yaml
name: cv-brainstormer
steps:
  - name: extract
    prompt_file: agents/00-extractor.md
    input: input/extracted.txt
    output: output/step-00.txt
  - name: ats-scan
    prompt_file: agents/01-ats-scanner.md
    input: output/step-00.txt
    output: output/step-01.txt
  # ... repeat for each agent
  - name: synthesize
    prompt_file: agents/07-synthesizer.md
    input: output/step-*.txt
    output: output/final-report.md
```

---

### 🌌 Antigravity

1. Import each agent `.md` as an Agent definition
2. Set up pipeline:
   ```
   extractor → [ats_scanner, hr_impression, tech_reviewer, achievement_auditor, industry_analyst, bias_checker] → synthesizer
   ```
3. Configure fan-out for parallel execution of agents 01–06
4. Configure fan-in for Agent 07 (wait for all 6 before running)

---

## Output Rendering / Render Output

After Agent 07 produces `output/final-report.md`:

```bash
# Render to DOCX and PDF
python scripts/render.py output/final-report.md

# Output files:
# output/final-report.docx
# output/final-report.pdf
# output/cv-revised.docx  (extracted from report)
# output/cv-revised.pdf
```

---

## Quick Reference / Referensi Cepat

| Agent | File | Input | Output |
|-------|------|-------|--------|
| 00 Extractor | `00-extractor.md` | Raw CV text | Normalized CV |
| 01 ATS Scanner | `01-ats-scanner.md` | Normalized CV | ATS Report |
| 02 HR Impression | `02-hr-first-impression.md` | Normalized CV | HR Report |
| 03 Tech Reviewer | `03-tech-stack-reviewer.md` | Normalized CV | Tech Report |
| 04 Achievement | `04-achievement-auditor.md` | Normalized CV | Achievement Report |
| 05 Industry | `05-industry-analyst.md` | Normalized CV + optional JD | Industry Report |
| 06 Bias Checker | `06-bias-checker.md` | Normalized CV | Bias Report |
| 07 Synthesizer | `07-synthesizer.md` | Normalized CV + all 6 reports | Final Report + Revised CV |

---

## Tips / Tips

- **Don't skip Agent 00.** The normalization step ensures all specialist agents work from consistent data.
- **Run 01–06 in parallel** when possible to save time. They don't depend on each other.
- **Agent 07 needs all 6 reports.** Don't run it until you have outputs from all previous agents.
- **Iterate.** After getting the revised CV from Agent 07, you can re-run it through all agents again for a second pass.
- **Provide target JD to Agent 05** whenever possible — it dramatically improves accuracy of the Industry Fit analysis.
