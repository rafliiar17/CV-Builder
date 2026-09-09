# CV Brainstormer — Design Spec
**Date:** 2026-09-09  
**Status:** Active Architecture Reference  
**Author:** CV Brainstormer Core Architecture Team

---

## 1. Overview

CV Brainstormer adalah sistem multi-agent (18 specialist & gate agents: Agents 00–11 beserta 00.25, 00.5, 04.5, 05.5, 05.75, dan 08.5) yang menganalisis, mengkritisi, menyempurnakan, dan men-tailor Curriculum Vitae (CV) secara mendalam dari berbagai perspektif profesional.

Sistem ini tidak sekadar membuat resume terdengar bombastis. Sebaliknya, sistem ini menegakkan verifikasi bukti (*evidence gate*), menyelaraskan peran nyata vs judul resmi (*role discovery*), menganalisis kompensasi pasar terkini (*salary intelligence* dalam SGD, USD, dan IDR), memetakan portofolio teknis, menyiapkan bank cerita wawancara STAR, serta memproduksi paket aplikasi kerja global (cover letter, application email, follow-up) dan profil platform terpadu (Upwork, LinkedIn, Glints).

Sistem ini bersifat **platform-agnostic** — setiap agent didefinisikan sebagai file instruksi Markdown mandiri di `.agents/skills/cv-brainstormer/agents/` dan dapat dijalankan di berbagai runtime (Claude, Claude Code, Codex, Antigravity, Kiro).

---

## 2. Goals

- **18-Agent Comprehensive Pipeline**: Menganalisis CV secara holistik dari sudut pandang ATS, HR, stack teknis, pencapaian STAR, kesesuaian industri, bias/inklusivitas, riset gaji, strategi peran terdekat, dan verifikasi kualitas.
- **Evidence-Safe & Defensible**: Mengklasifikasikan klaim kandidat (proven, project-backed, exposure, learning, risky, remove) agar semua klaim pada CV final dapat dipertanggungjawabkan saat wawancara teknis.
- **Role Discovery & Conflict Resolution**: Mendiagnosis peran dan level sebenarnya kandidat ketika jabatan resmi perusahaan tidak mencerminkan pekerjaan riil sehari-hari.
- **Bilingual & Language Separation**: Laporan analitis dwibahasa (Indonesia + English), sementara berkas CV dipisahkan per bahasa (`-en` untuk ATS/multinasional/remote, `-id` untuk pasar lokal/BUMN/vendor).
- **Salary Market Intelligence**: Menyediakan estimasi rentang gaji pasar yang akurat dengan sitasi sumber terpercaya terkini dan konversi wajib ke SGD, USD, dan IDR.
- **Application & Freelance Packaging**: Menghasilkan materi lamaran siap pakai (cover letter, email aplikasi, email follow-up) serta strategi platform terpadu untuk LinkedIn, Glints, dan Upwork (berbasis pemecahan masalah klien, bukan CV dump).
- **Candidate & Run Isolation**: Mengelompokkan input dan seluruh artefak output per kandidat dan per run (`output/candidates/<candidate-slug>/<run-id>/`) untuk mencegah tabrakan data.
- **Harvard Resume Standard Gate**: Menerapkan standar Harvard sebagai *light gate* verifikasi (`Pass`, `Minor Issues`, `Needs Revision`).

---

## 3. Non-Goals

- Bukan platform auto-apply atau automated job scraper.
- Bukan database penyimpanan permanen kredensial kandidat (stateless per candidate run folder).
- Tidak memalsukan atau menggelembungkan (*inflate*) pencapaian, angka metrik, atau teknologi yang tidak pernah disentuh kandidat.

---

## 4. Project Structure

```text
CV-Brainstormer/
├── AGENTS.md                    # Master agent orchestrator & specialist roster reference
├── GEMINI.md                    # AI runtime instructions & global directives
├── README.md                    # Public project documentation & quick start
├── SUB-AGENTS.md                # Orchestration workflow & output contracts
├── .agents/
│   └── skills/
│       └── cv-brainstormer/
│           ├── SKILL.md         # Skill definition & invocation steps
│           ├── agents/          # 18 specialist agent prompt files
│           │   ├── 00-extractor.md
│           │   ├── 00.25-role-discovery-interviewer.md
│           │   ├── 00.5-target-decision-gate.md
│           │   ├── 01-ats-scanner.md
│           │   ├── 02-hr-first-impression.md
│           │   ├── 03-tech-stack-reviewer.md
│           │   ├── 04-achievement-auditor.md
│           │   ├── 04.5-evidence-gate.md
│           │   ├── 05-industry-analyst.md
│           │   ├── 05.5-adjacent-role-strategist.md
│           │   ├── 05.75-salary-market-analyst.md
│           │   ├── 06-bias-checker.md
│           │   ├── 07-synthesizer.md
│           │   ├── 08-role-tailor.md
│           │   ├── 08.5-portfolio-mapper.md
│           │   ├── 09-final-verifier.md
│           │   ├── 10-star-interview-coach.md
│           │   └── 11-application-package-writer.md
│           └── references/      # Architecture, runner guide & Harvard standards
│               ├── design-spec.md
│               ├── runner-guide.md
│               └── harvard-resume-standard.md
├── templates/
│   ├── cv-input-form.md         # Form input dari nol
│   └── report-template.md       # Skeleton laporan output
├── scripts/
│   ├── review-cv                # Bash runner untuk inisialisasi candidate run
│   └── render_outputs.py        # Markdown → DOCX & PDF renderer
└── output/
    └── candidates/
        └── <candidate-slug>/
            ├── LATEST.md
            └── <run-id>/        # Direktori artefak run terisolasi
```

---

## 5. Agent Definitions (18-Agent Roster)

### Agent 00 — Extractor
- **Role**: Normalisasi input teks mentah (dari file PDF/DOCX atau form) menjadi Markdown terstruktur standar (`[PERSONAL INFO]`, `[SUMMARY]`, `[EXPERIENCE]`, `[EDUCATION]`, `[SKILLS]`, `[PROJECTS]`).
- **File**: `agents/00-extractor.md`

### Agent 00.25 — Role Discovery Interviewer
- **Role**: Mengidentifikasi kesenjangan antara judul resmi, target peran, dan pekerjaan riil sehari-hari melalui pertanyaan diagnostik universal dan domain-spesifik.
- **File**: `agents/00.25-role-discovery-interviewer.md`

### Agent 00.5 — Target Decision Gate
- **Role**: Menentukan dan mengunci target peran primer, target sekunder, pasar geografis sasaran, bahasa output, serta strategi single/dual-track sebelum analisis mendalam dimulai.
- **File**: `agents/00.5-target-decision-gate.md`

### Agent 01 — ATS Scanner
- **Role**: Mengevaluasi keterbacaan mesin Applicant Tracking System, kepadatan kata kunci, tata letak, format tanggal, dan section headers yang kompatibel.
- **File**: `agents/01-ats-scanner.md`

### Agent 02 — HR First Impression
- **Role**: Mensimulasikan pemindaian 6 detik pertama oleh HR/recruiter, mengevaluasi hierarki visual, nada profesional, dan mendeteksi red flags.
- **File**: `agents/02-hr-first-impression.md`

### Agent 03 — Tech Stack Reviewer
- **Role**: Memvalidasi kredibilitas teknologi, mendeteksi teknologi usang (misal CentOS EOL), memverifikasi versi tools, dan mengecek permintaan pasar terkini via web search.
- **File**: `agents/03-tech-stack-reviewer.md`

### Agent 04 — Achievement Auditor
- **Role**: Mengaudit rasio tanggung jawab vs pencapaian (*Responsibility vs Achievement ratio*), kekuatan kata kerja tindakan (*action verbs*), dan kuantifikasi dampak menggunakan metode STAR.
- **File**: `agents/04-achievement-auditor.md`

### Agent 04.5 — Evidence Gate
- **Role**: Mengklasifikasikan setiap klaim keterampilan dan pencapaian ke dalam 6 tingkat bukti: `Proven`, `Project-backed`, `Exposure`, `Learning`, `Risky`, atau `Remove`. Klaim berisiko wajib diturunkan atau dihapus dari CV final.
- **File**: `agents/04.5-evidence-gate.md`

### Agent 05 — Industry Analyst
- **Role**: Menganalisis kesesuaian target role/JD, menghitung persentase `Previous CV Role Match` dari CV orisinal, serta memetakan kesenjangan kompetensi kandidat.
- **File**: `agents/05-industry-analyst.md`

### Agent 05.5 — Adjacent Role Strategist
- **Role**: Merekomendasikan alternatif peran paling realistis berdasarkan riwayat karier, kebutuhan pasar/JD, dan bukti pencapaian nyata (mengklasifikasikan ke dalam: Apply Now, Minor Tailoring, After Portfolio Proof, Long-Term, Do Not Target).
- **File**: `agents/05.5-adjacent-role-strategist.md`

### Agent 05.75 — Salary Market Analyst
- **Role**: Melakukan riset mendalam terhadap rentang kompensasi pasar terkini untuk target peran dan geografi. Wajib mengonversi rentang gaji ke SGD, USD, dan IDR menggunakan kurs terkini, mencantumkan sitasi sumber terpercaya (Hays, Michael Page, Levels.fyi, NodeFlair) dengan tanggal akses, serta merumuskan posisi negosiasi (realistic, stretch, walk-away).
- **File**: `agents/05.75-salary-market-analyst.md`

### Agent 06 — Bias & Inclusion Checker
- **Role**: Memeriksa data pribadi yang tidak perlu (usia, agama, status pernikahan, foto) dan menegakkan bahasa inklusif serta perlindungan privasi kandidat.
- **File**: `agents/06-bias-checker.md`

### Agent 07 — Synthesizer / Human CV Writer
- **Role**: Mengompilasi laporan dwibahasa komprehensif, menyelesaikan konflik antar-agent, dan menulis draf CV baseline dengan gaya copywriting manusiawi, aktif, faktual, dan aman dari overclaiming.
- **File**: `agents/07-synthesizer.md`

### Agent 08 — Role Tailor / Copywriter
- **Role**: Mengadaptasi CV baseline untuk setiap peran spesifik yang disetujui, menghasilkan berkas terpisah untuk versi bahasa Inggris (`-en.md`) dan bahasa Indonesia (`-id.md`).
- **File**: `agents/08-role-tailor.md`

### Agent 08.5 — Portfolio Mapper
- **Role**: Memetakan proyek nyata kandidat dari `projects-list.md` ke target peran dan mengidentifikasi bukti yang masih kurang (README, skrinsut UI, cuplikan query SQL, demo interaktif).
- **File**: `agents/08.5-portfolio-mapper.md`

### Agent 09 — Final Verifier
- **Role**: Memvalidasi ulang skor ATS & pencapaian, menghitung `Role Match Delta`, dan mengevaluasi kepatuhan terhadap Harvard Resume Standard (`Pass`, `Minor Issues`, `Needs Revision`).
- **File**: `agents/09-final-verifier.md`

### Agent 10 — STAR Interview Coach
- **Role**: Menyusun bank cerita wawancara STAR (Situation, Task, Action, Result) per peran target berdasarkan bukti nyata CV, dilengkapi antisipasi pertanyaan sulit dan batasan klaim (*what not to overclaim*).
- **File**: `agents/10-star-interview-coach.md`

### Agent 11 — Application Package Writer
- **Role**: Menghasilkan materi lamaran pekerjaan global/remote (cover letter, email aplikasi, email follow-up) serta satu file profil terpadu per saluran platform (`upwork.md`, `linkedin.md`, `glints.md`). Pada Upwork, fokus pada positioning jasa, pemecahan masalah klien, deliverable, dan proposal hooks.
- **File**: `agents/11-application-package-writer.md`

---

## 6. End-to-End Orchestration Flow

```text
Input CV (PDF/DOCX/Form)
  │
  ▼
[Agent 00: Extractor] ──► scratch/00-structured-cv.md
  │
  ▼
[Agent 00.25: Role Discovery] ──► Klasifikasi peran riil & level
  │
  ▼
[Agent 00.5: Target Decision Gate] ──► Kunci target role, market & strategi
  │
  ├──────────────────────────────────────────────────────┐
  │ Parallel Execution                                   │
  ▼                                                      ▼
[Agents 01-06: ATS, HR, Tech, Achievement, Industry, Bias]
  │
  ▼
[Agent 04.5: Evidence Gate] ──► Filter klaim Risky/Remove
  │
  ▼
[Agent 05.5: Adjacent Role Strategist] ──► Rekomendasi peran terdekat
  │
  ▼
[Agent 05.75: Salary Market Analyst] ──► salary/<role>/salary-market-<role>.md (SGD/USD/IDR)
  │
  ▼
[Agent 07: Synthesizer] ──► reports/final-report-bilingual.md + Baseline CV
  │
  ▼
[Agent 08: Role Tailor] ──► cv/<role>/cv-<slug>-<role>-en.md & -id.md
  │
  ▼
[Agent 08.5: Portfolio Mapper] ──► portfolio/projects-from-list.md
  │
  ▼
[Agent 09: Final Verifier] ──► reports/delta-report-bilingual.md (Harvard Gate)
  │
  ▼
[Agent 10: STAR Coach] ──► interview/<role>/star-<role>-en.md & -id.md
  │
  ▼
[Agent 11: Application Writer] ──► application/<role>/ & platform/<role>/ (Upwork/LinkedIn/Glints)
  │
  ▼
[scripts/render_outputs.py] ──► Dokumen cetak .docx & .pdf
```

---

## 7. Output Folder Contract

Setiap run kandidat diisolasi secara ketat dalam hirarki berikut:

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

---

## 8. Quality & Formatting Mandates

1. **Harvard Resume Standard**: Semua output CV harus memenuhi prinsip ringkas, terfokus, berbasis hasil/fakta terukur, bebas dari kata ganti orang pertama (I, me, my), tanpa grafik/tabel kompleks, dan diformat ATS-safe.
2. **Bilingual Separation**: Laporan hasil review dwibahasa; file CV dibuat terpisah per bahasa. Tidak mencampur bahasa Inggris dan Indonesia dalam satu CV.
3. **Salary Data Freshness**: Sitasi wajib menyertakan URL/sumber resmi, tanggal riset, dan tanggal kurs valuta asing (SGD, USD, IDR).
4. **Upwork Positioning**: Khusus profil Upwork (`platform/<target-role>/upwork.md`), gunakan penawaran berbasis jasa/solusi bisnis klien, bukan ringkasan resume formal.

---

## 9. Automation Scripts

- **`scripts/review-cv`**: Menginisialisasi folder run baru, menyalin file input, mengekstrak teks, membuat `target-brief.md`, memperbarui `LATEST.md`, dan menampilkan prompt eksekusi awal.
- **`scripts/render_outputs.py`**: Mengonversi file Markdown artefak menjadi berkas dokumen Word (`.docx`) dan Adobe PDF (`.pdf`) berkualitas tinggi dengan penanganan styling ATS profesional.
