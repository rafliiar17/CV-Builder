---
name: cv-brainstormer
description: >
  Sistem multi-agent untuk menganalisis, memperbaiki, dan menghasilkan CV profesional
  yang ATS-friendly dan mengundang HR untuk membaca. Gunakan skill ini SETIAP KALI
  pengguna ingin: membuat CV dari nol, memperbaiki CV yang sudah ada, menganalisis
  CV mereka, meminta review CV, ingin tahu apakah CV mereka ATS-friendly, ingin
  mendapat feedback HR, ingin meningkatkan achievement bullets, ingin cek bias di CV,
  atau ingin CV yang lebih kompetitif untuk target role tertentu.
  Trigger juga jika pengguna menyebut: "review CV", "perbaiki CV", "buat CV",
  "CV saya kurang apa", "ATS CV", "HR suka CV yang gimana", "CV yang bagus",
  "bikin CV dari nol", "CV brainstorm", atau menempel isi CV dan meminta feedback.
  Skill ini menjalankan workflow multi-agent dengan core agents (00-10) plus
  strategic gate agents (00.25, 00.5, 04.5, 08.5). Output berupa report bilingual
  (Indonesia + English), CV siap pakai per role dan bahasa, serta portfolio
  mapping dalam format .md, .docx, dan .pdf.
---

# CV Brainstormer — Multi-Agent CV Analysis System

## Overview

Sistem ini menganalisis CV dari perspektif specialist berbeda, menghasilkan laporan komprehensif dengan skor, priority fix list, evidence check, portfolio mapping, dan CV yang sudah direvisi. Report bersifat bilingual (Indonesia + English). CV final dibuat terpisah per bahasa (`-en` dan `-id`) agar ATS English dan kebutuhan pasar lokal tidak bercampur.

Agents dalam workflow ini harus berpikir kritis. Mereka tidak boleh sekadar menyetujui framing user jika target role tidak jelas, bukti lemah, klaim terlalu tinggi, atau konteks role meleset. Agent penulis CV wajib menulis dengan kualitas copywriting human: natural, spesifik, tidak kaku, tidak keyword stuffing, dan tetap interview-defensible.

**Flow:**
```
Input CV / Form → Agent 00 (Extractor) → Agent 00.25 (Role Discovery Interviewer) → Agent 00.5 (Target Decision Gate) → Agent 01–06 (paralel) → Agent 04.5 (Evidence Gate) → Agent 05.5 (Adjacent Role Strategist) → Agent 07 (Synthesizer) → Agent 08 (Role Tailor) → Agent 08.5 (Portfolio Mapper) → Agent 09 (Final Verifier) → Agent 10 (STAR Interview Coach) → Verified Output
```

**Output Root:**

Semua output harus masuk ke folder kandidat dan run agar workflow bisa dipakai banyak orang tanpa saling menimpa:

```text
output/candidates/<candidate-slug>/<run-id>/
```

Contoh:

```text
output/candidates/rafli-arraafi/2026-06-01-data-analyst-application-support/
```

---

## Cara Menjalankan

### Quick Start — Inisialisasi Run Kandidat

Gunakan script berikut untuk membuat folder kandidat/run, menyalin input, membuat `target-brief.md`, dan mencetak prompt singkat untuk agent:

```bash
scripts/review-cv "Candidate Name" /path/to/cv.pdf --roles "Data Analyst, Application Support" --projects /path/to/projects-list.md
```

Contoh:

```bash
scripts/review-cv "Rafli Arraafi" CV_Rafli_Arraafi_ID.pdf --roles "Data Analyst, Application Support" --projects input/projects-list.md
```

### Step 1 — Tentukan jalur input

**Jalur A: Punya CV existing**
- Minta user paste teks CV-nya, atau
- Jalankan `scripts/extract.py` untuk PDF/DOCX → text
- Lanjut ke Step 2

**Jalur B: Belum punya CV / dari nol**
- Minta user isi `templates/cv-input-form.md`
- Lanjut ke Step 2

### Step 2 — Jalankan Agent 00 (Extractor)
Baca `agents/00-extractor.md` dan normalisasi input CV menjadi format terstruktur.

### Step 2.25 — Jalankan Agent 00.25 (Role Discovery Interviewer)
Baca `agents/00-role-discovery-interviewer.md`. Mulai dari CV: klasifikasikan dulu domain umum kandidat, role family awal, level, dan mismatch antara title resmi dengan pekerjaan nyata. Setelah itu baru ajukan pertanyaan diagnostik universal dan domain-specific yang relevan.

Agent ini harus bisa bekerja untuk kandidat general maupun tech. Jangan memaksakan pertanyaan tech untuk kandidat non-tech. Untuk kandidat tech/support, agent wajib membedakan L1, L2, L3, Production Support, Application Support, SQL/Data Support, Manual QA, SysAdmin, dan DevOps berdasarkan bukti kerja, bukan berdasarkan title perusahaan.

### Step 2.5 — Jalankan Agent 00.5 (Target Decision Gate)
Baca `agents/00-target-decision-gate.md`. Tentukan target utama, target sekunder, market, bahasa output, strategi single/dual-track, dan hal yang harus dikecilkan atau dikeluarkan dari CV.

Gunakan output Agent 00.25 sebagai sumber utama jika ada konflik antara title dan pekerjaan nyata.

Jika target role konflik atau terlalu luas, minta user memilih sebelum lanjut.

### Step 3 — Jalankan Agent 01–06 (paralel)
Gunakan output Agent 00 sebagai input untuk semua agent berikut secara bersamaan:
- `agents/01-ats-scanner.md` — ATS compliance
- `agents/02-hr-first-impression.md` — HR first impression
- `agents/03-tech-stack-reviewer.md` — Tech stack relevance (boleh web search)
- `agents/04-achievement-auditor.md` — Achievement vs responsibility
- `agents/05-industry-analyst.md` — Industry fit & JD alignment
- `agents/06-bias-checker.md` — Bias & inclusion check

### Step 3.5 — Jalankan Agent 04.5 (Evidence Gate)
Baca `agents/04-evidence-gate.md`. Klasifikasikan klaim, skill, project, dan metrik menjadi:
- Proven
- Project-backed
- Exposure
- Learning
- Risky
- Remove

Klaim dengan status Risky/Remove tidak boleh muncul sebagai klaim kuat di CV final.

### Step 3.75 — Jalankan Agent 05.5 (Adjacent Role Strategist)
Baca `agents/05-adjacent-role-strategist.md`. Agent ini memberi rekomendasi posisi terdekat berdasarkan:
- Title target dan title history kandidat
- Job description jika ada, atau market requirement saat ini jika JD tidak tersedia
- Achievement kandidat yang benar-benar terbukti
- Evidence strength dan missing proof

Agent ini boleh menolak atau menurunkan target role user jika bukti belum cukup, lalu memberi jalur alternatif yang lebih realistis.

### Step 4 — Jalankan Agent 07 (Synthesizer)
Baca `agents/07-synthesizer.md`. Berikan semua output dari Agent 00–06 sebagai input.
Output: Full report bilingual + CV revised draft. Agent ini wajib menyelesaikan konflik antar-agent, menjaga konteks role, dan menulis CV dengan copywriting human yang natural serta defensible.

### Step 5 — Jalankan Agent 08 (Role Tailor)
Gunakan insight dari Agent 05 (Industry Analyst) tentang role relevan atau minta *user* menyebutkan posisi yang diincarnya.
Spawn subagent paralel jika tersedia, atau jalankan secara lokal, untuk membaca instruksi di `agents/08-role-tailor.md` dan mengadaptasi output CV dari Agent 07 agar selaras dengan masing-masing role target. Hasilkan *file* terpisah per role dan bahasa, misalnya `cv-data-analyst-en.md` dan `cv-data-analyst-id.md`.

### Step 5.5 — Jalankan Agent 08.5 (Portfolio Mapper)
Baca `agents/08-portfolio-mapper.md`. Petakan project nyata dari user ke target role, tentukan project mana yang dipakai, mana yang harus dikecilkan, dan artefak portfolio apa yang kurang (README, screenshot, SQL snippet, demo, atau mockup).

### Step 6 — Render output (opsional, butuh Python)
```bash
python scripts/render_outputs.py output/candidates/<candidate-slug>/<run-id>/reports/final-report-bilingual.md
python scripts/render_outputs.py output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-data-analyst-en.md output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-data-analyst-id.md
```
Menghasilkan `.docx` dan `.pdf` dari report dan berbagai varian CV.

### Step 7 — Jalankan Agent 09 (Final Verifier)
Baca `agents/09-delta-verifier.md`. Jalankan **dua subagent paralel** (re-run Agent 01 + Agent 04) terhadap varian CV yang ingin diverifikasi, misalnya `output/candidates/<candidate-slug>/<run-id>/cv/general/cv-revised-en.md` atau `output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-data-analyst-en.md`, lalu jalankan Delta Synthesizer yang membaca:
- Skor original dari Agent 07
- Hasil re-run Agent 01 & 04
- Priority Fix List dari Agent 07 (untuk verifikasi item mana yang sudah diterapkan)
- Target Decision Gate output
- Evidence Gate output
- Portfolio Mapper output

Output disimpan di folder report kandidat/run, misalnya `output/candidates/<candidate-slug>/<run-id>/reports/delta-report-bilingual.md` (+ `.docx` + `.pdf`) jika verifikasi delta diperlukan.

**Mode Varian:** Jika user ingin cek varian role tertentu (misal `output/candidates/<candidate-slug>/<run-id>/cv/data-analyst/cv-data-analyst-en.md`), panggil Agent 09 lagi dengan file tersebut sebagai input. Output: `output/candidates/<candidate-slug>/<run-id>/reports/delta-report-{role}-bilingual.md`

### Step 8 — Jalankan Agent 10 (STAR Interview Coach)
Baca `agents/10-star-interview-coach.md`. Buat STAR interview story bank berdasarkan CV final, evidence gate, role discovery, portfolio mapping, verification report, dan klarifikasi user.

Output wajib masuk ke folder interview per role:

```text
output/candidates/<candidate-slug>/<run-id>/interview/<target-role>/
```

Setiap role harus punya versi English dan Indonesia jika CV role tersebut juga dibuat dalam dua bahasa.

---

## Agent Reference

| File | Agent | Domain |
|------|-------|--------|
| `agents/00-extractor.md` | Extractor | Normalisasi CV menjadi format terstruktur |
| `agents/00-role-discovery-interviewer.md` | Role Discovery Interviewer | Menentukan role family dan level aktual lewat pertanyaan diagnostik saat title/target role tidak sinkron |
| `agents/00-target-decision-gate.md` | Target Decision Gate | Menentukan target role, market, bahasa, dan strategi sebelum analisis |
| `agents/01-ats-scanner.md` | ATS Scanner | ATS compliance, keyword density, format |
| `agents/02-hr-first-impression.md` | HR First Impression | 6-second scan, tone, red flags |
| `agents/03-tech-stack-reviewer.md` | Tech Stack Reviewer | Skill credibility, market relevance, web search |
| `agents/04-achievement-auditor.md` | Achievement Auditor | STAR method, action verbs, quantification |
| `agents/04-evidence-gate.md` | Evidence Gate | Cek bukti klaim, skill, project, dan metrik agar tidak overclaim |
| `agents/05-industry-analyst.md` | Industry Analyst | JD alignment, gap analysis, competitive positioning |
| `agents/05-adjacent-role-strategist.md` | Adjacent Role Strategist | Rekomendasi posisi terdekat berdasarkan title, JD/market requirement, dan achievement |
| `agents/06-bias-checker.md` | Bias & Inclusion Checker | Unnecessary personal info, privacy, inclusive language |
| `agents/07-synthesizer.md` | Synthesizer / Human CV Writer | Compile semua → priority list + revised CV dengan copywriting human |
| `agents/08-role-tailor.md` | Role Tailor / Copywriter | Menyesuaikan isi CV untuk spesifik role / posisi baru secara natural dan defensible |
| `agents/08-portfolio-mapper.md` | Portfolio Mapper | Memetakan project nyata ke role dan gap portfolio |
| `agents/09-delta-verifier.md` | Final Verifier | Re-run ATS + Achievement, cek role fit, evidence risk, interview defensibility, portfolio completeness |
| `agents/10-star-interview-coach.md` | STAR Interview Coach | Membuat story bank STAR interview per role dari klaim CV yang sudah diverifikasi |

---

## Scoring System

Setiap agent menghasilkan skor **0–100** dengan label kategori:
- **0–40:** Poor / Buruk
- **41–60:** Fair / Cukup
- **61–80:** Good / Baik
- **81–100:** Excellent / Sangat Baik

Agent 07 menggabungkan semua skor dengan weighting:

| Agent | Bobot |
|-------|-------|
| Achievement Quality | 25% |
| ATS Compliance | 20% |
| HR First Impression | 20% |
| Industry Fit | 15% |
| Tech Stack | 15% |
| Bias & Inclusion | 5% |

---

## Priority Fix System

Semua temuan diklasifikasikan:
- 🔴 **Critical** — perbaiki sebelum kirim lamaran apapun
- 🟠 **High** — perbaiki minggu ini
- 🟡 **Medium** — perbaiki bulan ini
- 🟢 **Low** — polish, nice to have

---

## Output yang Dihasilkan

1. **Full Report** (`output/candidates/<candidate-slug>/<run-id>/reports/final-report-bilingual.md` / `.docx` / `.pdf`) — laporan lengkap bilingual dengan skor per agent, priority fix list, dan detail temuan
2. **CV Role Variants** (`output/candidates/<candidate-slug>/<run-id>/cv/<role>/cv-<role>-en.md` dan `cv-<role>-id.md`) — versi CV siap pakai per role dan bahasa
3. **Portfolio Summary** (`output/candidates/<candidate-slug>/<run-id>/portfolio/projects-from-list.md`) — ringkasan portfolio dari project list user, jika tersedia
4. **STAR Interview Story Bank** (`output/candidates/<candidate-slug>/<run-id>/interview/<role>/star-<role>-en.md` dan `star-<role>-id.md`) — jawaban interview berbasis STAR yang role-specific dan interview-defensible

---

## Keputusan Design

| Parameter | Nilai |
|-----------|-------|
| Bahasa output | Report bilingual; CV dipisah English (`-en`) dan Indonesia (`-id`) |
| Target industri | Generalis — semua industri |
| Input | Upload file (PDF/DOCX) ATAU isi form dari nol |
| Target JD | Opsional — agent inferensi jika tidak ada, minta klarifikasi jika ambigu |
| Web search | Diizinkan untuk Agent 03 (Tech Stack Reviewer) |
| Scoring | Numerik 0–100 + label kategori |

---

## Tips Penggunaan

- **Sediakan target JD** ke Agent 05 jika ada — meningkatkan akurasi industry fit analysis secara signifikan
- **Jalankan Agent 01–06 paralel** untuk menghemat waktu — mereka tidak bergantung satu sama lain
- **Iterasi** — setelah CV direvisi, jalankan ulang semua agent untuk second-pass improvement
- **Agent 03 boleh search** — validasi market demand skills lebih akurat dengan data terkini

---

## File Scripts

| Script | Fungsi |
|--------|--------|
| `scripts/review-cv` | Inisialisasi folder kandidat/run dan cetak prompt agent singkat |
| `scripts/extract.py` | Ekstrak teks dari PDF atau DOCX ke plain text jika tersedia |
| `scripts/render_outputs.py` | Konversi `.md` report/CV ke `.docx` dan `.pdf` |

**Install dependencies:**
```bash
pip install pdfplumber python-docx markdown weasyprint --break-system-packages
```

---

## Platform Support

Skill ini bisa dijalankan di: **Claude** (Projects), **Claude Code** (terminal), **Codex**, **Kiro**, **Antigravity**, atau AI agent runner lainnya.
Lihat `references/runner-guide.md` untuk instruksi per platform.

---

## References / Referensi

| File | Isi |
|------|-----|
| `references/runner-guide.md` | Instruksi menjalankan di Claude, Codex, Kiro, Antigravity, Claude Code |
| `references/sample-report-output.md` | Contoh output lengkap Agent 07 — standar format dan kedalaman analisis |
| `references/sample-cv-before-after.md` | Contoh transformasi CV sebelum dan sesudah diproses — benchmark kualitas |
| `references/sample-interactions.md` | Contoh trigger phrases, skenario penggunaan, dan edge cases |
| `references/design-spec.md` | Dokumen desain arsitektur lengkap sistem ini |
