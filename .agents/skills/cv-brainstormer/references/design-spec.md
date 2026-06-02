# CV Brainstormer — Design Spec
**Date:** 2026-05-31  
**Status:** Draft — Pending User Review  
**Author:** Brainstorming Session (Rafzz × Claude)

---

## 1. Overview

CV Brainstormer adalah sistem multi-subagent yang menganalisis CV secara mendalam dari berbagai perspektif profesional, menghasilkan laporan komprehensif, dan memproduksi versi CV yang sudah diperbaiki dalam format `.md`, `.docx`, dan `.pdf`.

Sistem ini bersifat **platform-agnostic** — dapat dijalankan di Claude, Codex, Kiro, Antigravity, atau AI agent runner lainnya karena semua agent didefinisikan sebagai prompt file Markdown.

---

## 2. Goals

- Menganalisis CV dari 6 perspektif specialist secara mendalam
- Menghasilkan report yang actionable, bukan sekadar generic feedback
- Memproduksi CV revised draft yang siap dipakai
- Generalis — bisa handle semua industri, bukan hanya IT
- Dua jalur input: upload file existing CV atau isi dari nol via form

---

## 3. Non-Goals

- Bukan job board / job matching platform
- Tidak menyimpan data user (stateless per run)
- Tidak auto-apply ke lowongan

---

## 4. Project Structure

```
cv-brainstormer/
├── agents/
│   ├── 00-extractor.md          # Normalize input → plain structured text
│   ├── 01-ats-scanner.md        # ATS compliance specialist
│   ├── 02-hr-first-impression.md # HR 6-second rule specialist
│   ├── 03-tech-stack-reviewer.md # Tech relevance specialist
│   ├── 04-achievement-auditor.md # STAR/quantifiable achievement specialist
│   ├── 05-industry-analyst.md   # Market fit & JD alignment specialist
│   ├── 06-bias-checker.md       # Inclusive language specialist
│   └── 07-synthesizer.md        # Compile all → final report + revised CV
├── templates/
│   ├── cv-input-form.md         # Form terstruktur untuk input dari nol
│   └── report-template.md       # Skeleton output report
├── input/
│   └── .gitkeep                 # User taruh CV di sini (PDF/DOCX/MD)
├── output/
│   └── .gitkeep                 # Report hasil (.md, .docx, .pdf)
├── scripts/
│   ├── extract.py               # PDF/DOCX → plain text extractor
│   └── render.py                # .md → .docx + .pdf converter
├── runner.md                    # Instruksi cara jalanin di berbagai platform
└── README.md
```

---

## 5. Agent Definitions

### Agent 00 — Extractor
**Role:** Normalisasi input CV menjadi format terstruktur yang konsisten sebelum dilempar ke agent lain.

**Input:** Raw CV text (dari file extract atau form isian)  
**Output:** Structured CV dalam format standar:
```
[PERSONAL INFO] [SUMMARY] [EXPERIENCE] [EDUCATION] [SKILLS] [CERTIFICATIONS] [PROJECTS] [OTHERS]
```
**Knowledge domain:** Text parsing, CV section identification, deduplication, encoding cleanup.

---

### Agent 01 — ATS Scanner
**Role:** Mengevaluasi CV dari perspektif Applicant Tracking System.

**Knowledge domain:**
- ATS parsing rules (section headers yang dikenali, format yang aman)
- Keyword density analysis — apakah skills dan role keywords muncul cukup
- Format compliance: bullet points, date format, file encoding
- Hal-hal yang merusak ATS: tabel, kolom multi-kolom, header/footer, gambar, ikon
- Section order yang optimal untuk ATS

**Output section:** `## ATS Compliance` dengan skor 0-100 + temuan spesifik

---

### Agent 02 — HR First Impression
**Role:** Mensimulasikan HR yang membaca CV dalam 6 detik pertama.

**Knowledge domain:**
- Visual hierarchy dan scannability
- Tone profesional vs terlalu kaku / terlalu casual
- Personal branding — apakah ada "hook" yang bikin penasaran
- Summary/objective quality — apakah langsung to the point
- Red flags yang bikin HR langsung skip
- Length appropriateness (fresh grad vs senior berbeda)

**Output section:** `## First Impression Analysis` dengan temuan + saran konkret

---

### Agent 03 — Tech Stack Reviewer
**Role:** Menilai relevansi dan kredibilitas skills yang tercantum.

**Knowledge domain:**
- Validasi skills berdasarkan konteks pengalaman (jangan claim sesuatu yang tidak ada proyeknya)
- Skills yang outdated vs in-demand di market saat ini
- Perbedaan "familiar with" vs "proficient in" vs "expert in" — framing yang tepat
- Stack consistency — apakah skills yang disebutkan koheren dengan role dan pengalaman
- Missing skills yang seharusnya ada untuk target role
- Versi tools yang sebaiknya disebutkan (misal "Docker" vs "Docker + Compose + Swarm")

**Output section:** `## Tech Stack Assessment` dengan gap analysis + rekomendasi

---

### Agent 04 — Achievement Auditor
**Role:** Mengaudit kualitas penulisan pengalaman kerja.

**Knowledge domain:**
- STAR method (Situation, Task, Action, Result)
- Action verbs yang kuat vs lemah (misal "helped with" vs "architected", "led", "reduced")
- Quantifiable results — angka, persentase, skala, dampak bisnis
- Responsibility framing vs Achievement framing (mayoritas CV terjebak di responsibility)
- Bullet point structure yang optimal
- Tense consistency (past role = past tense, current = present)

**Output section:** `## Achievement Quality` dengan contoh sebelum/sesudah per bullet point

---

### Agent 05 — Industry Analyst
**Role:** Menganalisis kesesuaian CV dengan demand pasar dan target role.

**Knowledge domain:**
- Trend hiring di berbagai industri
- Keyword alignment dengan job description umum di target role
- Gap analysis — apa yang kurang untuk bisa lolos screening
- Competitive positioning — apa yang membedakan kandidat ini
- Jika user provide target JD: direct alignment scoring
- Jika tidak: analisis berdasarkan current role dan implied target

**Output section:** `## Industry Fit Analysis` dengan alignment score + gap list

---

### Agent 06 — Bias & Inclusion Checker
**Role:** Mendeteksi elemen yang bisa memicu unconscious bias atau dinilai tidak profesional.

**Knowledge domain:**
- Sinyal usia (tahun lulus, tahun pengalaman pertama)
- Sinyal gender dari bahasa yang digunakan
- Foto di CV — konteks regional (beberapa negara tidak prefer foto)
- Informasi yang tidak perlu: agama, status pernikahan, nomor KTP, dll
- Bahasa yang eksklusif vs inklusif
- Nama & cultural markers — relevansi untuk target market (lokal vs internasional)

**Output section:** `## Bias & Inclusion Check` dengan flag list + alasan

---

### Agent 07 — Synthesizer
**Role:** Mengompilasi semua output agent, membuat priority ranking, dan menghasilkan CV revised draft.

**Knowledge domain:**
- Weighting feedback berdasarkan severity (blocker vs nice-to-have)
- Conflict resolution antar agent (jika ada saran yang bertentangan)
- CV rewriting berdasarkan semua feedback
- Menjaga voice/tone asli user saat rewriting

**Output:**
1. Executive Summary (3-5 poin paling kritis)
2. Priority Fix List (ranked: Critical → High → Medium → Low)
3. Full revised CV draft siap pakai

---

## 6. Input Flow

### Jalur A — Upload File Existing CV
```
User taruh file di /input/
→ scripts/extract.py jalankan ekstraksi
→ Output: /input/extracted.txt
→ Lempar ke Agent 00 (Extractor) untuk normalisasi
→ Lanjut ke 6 specialist agents
```

### Jalur B — Form Terstruktur (dari nol)
```
User isi /templates/cv-input-form.md
→ Langsung ke Agent 00 (Extractor) untuk normalisasi
→ Lanjut ke 6 specialist agents
```

### Paralel Processing
Setelah Agent 00 selesai, Agent 01-06 bisa dijalankan **paralel** (tidak ada dependency antar agent). Agent 07 (Synthesizer) hanya jalan setelah semua agent 01-06 selesai.

---

## 7. Output Flow

```
Agent 07 Synthesizer output → /output/report-YYYY-MM-DD.md
→ scripts/render.py → /output/report-YYYY-MM-DD.docx
→ scripts/render.py → /output/report-YYYY-MM-DD.pdf

CV Revised Draft → /output/cv-revised-YYYY-MM-DD.md
→ scripts/render.py → /output/cv-revised-YYYY-MM-DD.docx
→ scripts/render.py → /output/cv-revised-YYYY-MM-DD.pdf
```

---

## 8. Report Template Structure

```markdown
# CV Brainstormer Report
**Generated:** {date}
**CV Owner:** {name}
**Target Role:** {role atau "General"}

---

## Executive Summary
> 3-5 poin paling kritis yang harus difix sekarang

## Priority Fix List
### 🔴 Critical
### 🟠 High  
### 🟡 Medium
### 🟢 Low (Nice to have)

---

## Detailed Analysis

### 1. ATS Compliance [Score: XX/100]
### 2. First Impression Analysis
### 3. Tech Stack Assessment
### 4. Achievement Quality
### 5. Industry Fit Analysis [Score: XX/100]
### 6. Bias & Inclusion Check

---

## CV Revised Draft
> Versi CV yang sudah diperbaiki berdasarkan semua feedback di atas
```

---

## 9. Runner Instructions (Multi-Platform)

File `runner.md` akan berisi instruksi cara menjalankan sistem ini di:
- **Claude:** copy-paste agent prompt satu per satu, atau gunakan Projects
- **Codex:** instruksi sebagai task file
- **Kiro:** sebagai spec/task definition
- **Antigravity:** sebagai agent pipeline config
- **Manual/Custom:** urutan eksekusi dan cara passing output antar agent

---

## 10. Scripts

### `extract.py`
- Library: `pdfplumber` (PDF) + `python-docx` (DOCX)
- Input: file path
- Output: `/input/extracted.txt`

### `render.py`
- Library: `markdown` + `weasyprint` (PDF) + `python-docx` (DOCX)
- Input: `.md` file path
- Output: `.docx` dan `.pdf` di `/output/`

---

## 11. Decisions (Resolved)

- [x] **Target JD:** Optional input. Agent 05 inferensi dari CV terlebih dahulu; minta klarifikasi dari user hanya jika target role ambigu atau tidak dapat disimpulkan.
- [x] **Bahasa report:** Bilingual — Indonesia + English (section terpisah per bahasa, atau label dual-language per temuan).
- [x] **Web search:** Agent 03 (Tech Stack Reviewer) diizinkan melakukan web search untuk validasi market demand dan relevansi skills terkini.
- [x] **Scoring:** Numerik (0–100) + label kategori: Poor (0–40) / Fair (41–60) / Good (61–80) / Excellent (81–100).

---

## 12. Future Enhancements (Out of Scope v1)

- Web UI / artifact interaktif
- Integrasi langsung dengan job board (LinkedIn, Jobstreet, Glints)
- Version history CV
- Multi-language CV generation
- Cover letter generator

---

*Spec ini subject to revision setelah user review.*
