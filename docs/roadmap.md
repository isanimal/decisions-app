# Secure Decision — Roadmap (v0.1 → v0.3)

Roadmap ini dirancang untuk memastikan Secure Decision:
- tumbuh perlahan tapi tepat arah
- tidak berubah menjadi security tool generik
- tetap setia pada filosofi *decision-oriented secure coding*

Setiap versi harus:
- usable secara nyata
- bisa diuji di tim kecil
- membawa pembelajaran baru

Jika sebuah fitur tidak meningkatkan kualitas keputusan atau diskusi,
fitur tersebut **tidak masuk roadmap**.

---

## Prinsip Roadmap

1. **Small, Composable Features**
   Tidak ada lonjakan fitur besar.

2. **Reflection First**
   Fitur baru harus memicu refleksi, bukan automasi.

3. **No Scoring, No Verdict**
   Tidak ada fitur yang memberi nilai atau status keamanan.

4. **Adoption > Completeness**
   Lebih penting dipakai daripada lengkap.

---

## v0.1 — Make Decisions Visible

### Tujuan Utama
Membuat keputusan teknis **tertulis, terbaca, dan dapat dibagikan**.

Versi ini harus:
- bisa dipakai secara nyata
- bahkan jika hanya oleh 1 lead dan 1 tim kecil

### Fitur Inti

#### 1. Create Decision
- Membuat Decision dengan:
  - title
  - context
  - decision statement (5 bagian)
- Mendukung status:
  - `draft`
  - `active`

#### 2. View Decision
- Membaca Decision secara lengkap
- Tampilan fokus ke narasi, bukan metadata

#### 3. Edit Decision
- Update decision statement
- Tidak ada approval flow

#### 4. Minimal History (Implicit)
- Perubahan disimpan (walau belum ditampilkan kompleks)
- Fokus: jangan kehilangan keputusan lama

### Out of Scope (v0.1)
- Reflection prompt
- Advanced history diff
- User role kompleks
- Integrasi apa pun

### Kriteria Sukses v0.1
- Lead bisa menulis decision < 10 menit
- Decision dibaca oleh anggota tim
- Decision dipakai sebagai referensi diskusi

---

## v0.2 — Track Decision Evolution

### Tujuan Utama
Membuat **perubahan keputusan terlihat dan bermakna**.

Versi ini memperkenalkan konsep:
> keputusan berevolusi seiring konteks

### Fitur Tambahan

#### 1. Decision History (Explicit)
- Menampilkan daftar revisi decision
- Setiap revisi berisi:
  - waktu perubahan
  - ringkasan perubahan
  - bagian yang berubah

#### 2. Update Prompt (Light Reflection)
- Saat update decision, tampil prompt:
  - “Apa yang berubah sejak decision ini dibuat?”
- Prompt opsional, tidak wajib diisi

#### 3. Lifecycle Extension
- Tambahan status:
  - `superseded`
  - `archived`
- Untuk menjaga decision lama tetap terbaca, bukan dihapus

### Out of Scope (v0.2)
- Analitik
- Reminder otomatis
- Notification system
- Penilaian kualitas decision

### Kriteria Sukses v0.2
- Tim bisa melihat *kenapa* decision berubah
- Decision lama masih dirujuk saat diskusi
- Onboarding developer baru jadi lebih cepat

---

## v0.3 — Encourage Reflection Without Forcing It

### Tujuan Utama
Mendorong **refleksi berkelanjutan** tanpa tekanan atau ritual berat.

Versi ini memperhalus perilaku pengguna,
bukan menambah kontrol.

### Fitur Tambahan

#### 1. Reflection Prompt Bank
- Kumpulan pertanyaan reflektif, misalnya:
  - “Apakah asumsi ini masih relevan?”
  - “Apa trade-off terbesar dari decision ini?”
- Prompt:
  - dapat dipilih manual
  - tidak muncul agresif

#### 2. Optional Reflection Response
- Pengguna boleh menulis refleksi singkat
- Refleksi tersimpan, tapi:
  - tidak wajib
  - tidak dinilai

#### 3. Readability & Sharing Improvement
- Decision mudah dibaca sebagai dokumen
- Cocok untuk:
  - review
  - diskusi
  - onboarding

### Out of Scope (v0.3)
- Reminder berbasis waktu
- KPI atau maturity scoring
- Role-based access kompleks
- Automation atau recommendation engine

### Kriteria Sukses v0.3
- Tim mulai terbiasa mempertanyakan asumsi
- Refleksi muncul alami dalam diskusi
- Tools tidak terasa “mengawasi”

---

## Fitur yang Sengaja Ditunda (Post v0.3)

Fitur-fitur berikut **sengaja ditunda** untuk menjaga arah:

- Reminder otomatis
- Integrasi CI/CD
- Dashboard metrik
- Analitik usage
- Multi-team comparison
- “Best practice suggestion”

Fitur ini **hanya dipertimbangkan** jika:
- filosofi tetap terjaga
- tidak mengubah tools menjadi compliance engine

---

## Evaluasi Antar Versi

Setiap rilis **harus** menjawab pertanyaan berikut:

1. Apakah tools ini membantu keputusan jadi lebih eksplisit?
2. Apakah diskusi tim menjadi lebih kontekstual?
3. Apakah ada kecenderungan misuse (scoring, judging)?

Jika jawaban ke-3 adalah “ya”, roadmap harus dikoreksi.

---

## Penutup

Secure Decision tidak dibangun untuk:
- tumbuh cepat
- menang kompetisi fitur
- mengejar adopsi massal

Ia dibangun untuk:
> tumbuh pelan,  
> menjaga makna,  
> dan membantu manusia berpikir lebih jujur.

Roadmap ini adalah pagar, bukan peta harta karun.
