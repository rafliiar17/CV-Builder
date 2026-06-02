# CV Brainstormer — Sample Interactions
*Contoh cara memicu dan menggunakan skill ini di berbagai skenario.*
*Examples of how to trigger and use this skill across different scenarios.*

---

## Skenario 1: User paste CV existing, minta review umum

**User:**
> Tolong review CV saya ini dan kasih tau apa yang kurang:
>
> [paste CV text]

**Response flow:**
1. Trigger Agent 00 — normalisasi CV
2. Jalankan Agent 01–06 paralel
3. Trigger Agent 07 — compile report
4. Output: full bilingual report + revised CV draft

**Sample opening response:**
> Oke, gue jalankan 7 agent specialist untuk review CV kamu. Mulai dari normalisasi dulu...
>
> **[Agent 00 — Extractor]**
> CV berhasil dinormalisasi. Ditemukan: 2 roles, 1 pendidikan, 18 skills, 0 sertifikasi aktif.
>
> **Menjalankan analisis paralel...**
> - Agent 01: ATS Scanner ⏳
> - Agent 02: HR First Impression ⏳
> - Agent 03: Tech Stack Reviewer ⏳
> - Agent 04: Achievement Auditor ⏳
> - Agent 05: Industry Analyst ⏳
> - Agent 06: Bias & Inclusion ⏳

---

## Skenario 2: User belum punya CV, minta dibuatkan dari nol

**User:**
> Gue belum punya CV, bisa bantu bikin dari nol? Gue kerja 3 tahun sebagai frontend developer.

**Response flow:**
1. Berikan `templates/cv-input-form.md` untuk diisi
2. Setelah user isi, jalankan Agent 00–07 normal

**Sample opening response:**
> Bisa. Sebelum gue bantu build, gue perlu data dari kamu dulu. Isi form berikut — semakin detail semakin bagus, nanti kita hasilkan CV yang kuat:
>
> [tampilkan cv-input-form.md]

---

## Skenario 3: User punya CV + target JD spesifik

**User:**
> Ini CV gue [paste], dan ini JD yang mau gue lamar [paste JD]. Tolong analisis seberapa match dan apa yang harus diperbaiki.

**Response flow:**
1. Agent 00: normalisasi CV
2. Agent 01–04, 06: analisis standar
3. **Agent 05: jalankan dengan JD sebagai input tambahan** → direct alignment scoring
4. Agent 07: synthesize dengan context JD

**Note untuk Agent 05:**
Sertakan JD secara eksplisit: *"Ini adalah JD target user. Lakukan direct alignment scoring antara CV dan JD ini."*

---

## Skenario 4: User minta focus area tertentu saja

**User:**
> Gue tau CV gue kurang bagus, tapi sekarang mau focus ke bagian achievement dulu aja. Bisa?

**Response flow:**
- Jalankan **hanya Agent 04** (Achievement Auditor)
- Tetap jalankan Agent 00 dulu untuk normalisasi
- Skip Agent 01, 02, 03, 05, 06
- Skip Agent 07 (Synthesizer) — output langsung dari Agent 04

**Sample response:**
> Oke, gue focus ke achievement audit dulu. Jalankan Agent 00 untuk normalisasi, lalu langsung ke Agent 04...

---

## Skenario 5: User minta second pass setelah revisi

**User:**
> Ini CV gue yang sudah gue revisi berdasarkan feedback sebelumnya. Tolong cek lagi apakah sudah lebih baik.

**Response flow:**
- Jalankan semua agent dari awal (full pipeline)
- Di Executive Summary, Agent 07 harus compare skor dengan iterasi pertama jika tersedia
- Highlight: apa yang sudah membaik, apa yang masih perlu perbaikan

---

## Skenario 6: User upload file (PDF/DOCX)

**User:**
> Ini file CV gue [upload file]

**Response flow:**
1. Jalankan `scripts/extract.py` pada file yang diupload
2. Lanjut ke Agent 00–07 normal

**Sample response:**
> File diterima. Mengekstrak teks dari PDF...
>
> Ekstraksi selesai: 487 kata, 2 halaman terdeteksi. Melanjutkan ke normalisasi...

---

## Trigger Phrases / Kalimat Pemicu

Skill ini aktif saat user menyebut salah satu dari:

| Bahasa Indonesia | English |
|-----------------|---------|
| "review CV saya" | "review my CV / resume" |
| "perbaiki CV saya" | "improve my CV" |
| "buat CV dari nol" | "help me build a CV from scratch" |
| "CV saya kurang apa" | "what's wrong with my CV" |
| "ATS CV" | "is my CV ATS-friendly" |
| "CV yang bagus itu gimana" | "what makes a good CV" |
| "bantu tulis CV" | "help me write my resume" |
| "feedback CV" | "give me CV feedback" |
| "CV brainstorm" | "brainstorm my CV" |
| [paste teks CV + pertanyaan apapun] | [paste CV text + any question] |

---

## Output Quality Standards

Setiap output harus memenuhi standar berikut:

**✅ Harus ada:**
- Skor numerik (0–100) + label kategori untuk setiap agent
- Overall score dengan weighted average
- Priority fix list dengan 4 level: Critical / High / Medium / Low
- Minimal 3 bullet rewrite contoh (sebelum/sesudah) dari Agent 04
- CV revised draft yang siap pakai
- Bilingual: setiap section punya versi Indonesia dan English

**❌ Jangan:**
- Memberikan feedback generik tanpa contoh konkret
- Skip salah satu dari 6 agent specialist
- Menghasilkan CV revised tanpa menerapkan semua Critical fixes
- Membuat angka palsu di CV revised — tandai `[VERIFY]` untuk data yang perlu dikonfirmasi user

---

## Edge Cases

| Situasi | Handling |
|---------|----------|
| CV hanya 1 role / fresh grad | Kurangi ekspektasi quantification, focus ke projects dan education |
| CV sangat panjang (5+ halaman) | Flag length issue di Agent 02, rekomendasikan trim ke 2 halaman max |
| CV dalam Bahasa Indonesia sepenuhnya | Output report tetap bilingual, CV revised bisa dalam bahasa yang dipilih user |
| Target role tidak jelas / ambigu | Agent 05 minta klarifikasi sebelum analisis industry fit |
| CV untuk akademisi / researcher | Adjust: publications, research experience lebih penting dari industry achievements |
| CV untuk posisi creative (designer, writer) | Agent 02 dan 03 harus adjust — portfolio link lebih penting dari keyword density |

---

*CV Brainstormer v1.0 — Sample Interactions Reference*
