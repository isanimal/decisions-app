# Secure Decision — MVP Specification
**Decision-Oriented Secure Coding**

## Tujuan Dokumen Ini

Dokumen ini mendefinisikan **Minimum Viable Product (MVP)** Secure Decision.

MVP ini tidak bertujuan:
- menyelesaikan semua masalah keamanan
- menggantikan proses existing
- menjadi tools evaluasi atau audit

MVP ini bertujuan untuk:
> Membantu lead dan tim membuat **keputusan teknis yang lebih sadar, eksplisit, dan dapat diwariskan**.

Jika sebuah fitur tidak mendukung tujuan ini, fitur tersebut **bukan bagian dari MVP**.

---

## Prinsip Desain MVP

MVP Secure Decision dibangun dengan prinsip berikut:

1. **Decision over Automation**  
   MVP membantu manusia berpikir, bukan mengambil alih keputusan.

2. **Explicit over Implicit**  
   Yang tidak ditulis dianggap tidak ada.

3. **Reflection over Verdict**  
   Pertanyaan lebih penting daripada jawaban.

4. **Lightweight over Complete**  
   Mudah dipakai lebih penting daripada lengkap.

---

## Persona Utama (MVP)

MVP hanya melayani **satu persona utama**:

### Lead Developer / Tech Lead

Ciri:
- bertanggung jawab atas keputusan teknis
- perlu menyelaraskan tim
- tidak ingin tooling tambahan yang berat
- butuh kejelasan, bukan kontrol

MVP **tidak dioptimalkan** untuk:
- auditor
- compliance officer
- penilaian performa individu

---

## Konsep Inti MVP

### 1. Decision

**Decision** adalah unit utama dalam sistem.

Decision merepresentasikan:
- satu fitur
- satu sistem
- atau satu perubahan penting

Decision **bukan**:
- ticket
- task
- issue bug
- vulnerability report

---

### 2. Decision Statement (Wajib)

Setiap Decision **harus** memiliki Decision Statement.

Decision Statement berisi jawaban eksplisit atas pertanyaan berikut:

1. **Tujuan Teknis**
   - Apa tujuan operasional dari decision ini?
   - Apa yang ingin dicapai sistem, bukan bisnisnya saja?

2. **Asumsi Utama**
   - Asumsi apa yang dibuat tentang user, data, atau lingkungan?
   - Apa yang dianggap “aman”, “internal”, atau “terpercaya”?

3. **Penyederhanaan yang Disadari**
   - Bagian mana yang sengaja dipercepat atau disederhanakan?
   - Kenapa penyederhanaan ini dianggap dapat diterima?

4. **Batas yang Tidak Boleh Dilanggar**
   - Hal apa yang tidak boleh disederhanakan?
   - Di mana tim harus berhenti dan berpikir ulang?

5. **Risiko yang Diterima**
   - Jika asumsi salah, dampak terburuk apa yang diterima?
   - Risiko mana yang disadari, bukan diabaikan?

Decision Statement **tidak dinilai benar atau salah**.

---

## Fitur MVP (Wajib Ada)

### 1. Create Decision
- Lead dapat membuat Decision baru
- Decision memiliki:
  - judul
  - konteks singkat
  - decision statement (5 bagian)

### 2. View Decision
- Semua anggota tim dapat membaca Decision
- Decision dapat dibaca tanpa login kompleks (opsional)

### 3. Decision History
- Perubahan pada Decision disimpan sebagai riwayat
- Fokus pada:
  - *apa yang berubah*
  - *kapan*
- Tidak fokus pada:
  - siapa yang salah

### 4. Reflection Prompt
- Sistem menampilkan pertanyaan reflektif sederhana, misalnya:
  - “Apakah asumsi ini masih relevan?”
  - “Apa yang berubah sejak decision dibuat?”
- Prompt bersifat pasif, tidak memaksa

---

## Fitur yang Sengaja TIDAK Ada di MVP

Untuk menjaga integritas filosofi, MVP **tidak memiliki**:

- Skor atau nilai keamanan
- Label “secure / insecure”
- KPI, ranking, atau gamifikasi
- Otomatisasi keputusan
- Rekomendasi teknis spesifik
- Integrasi scanner atau tools security

Jika fitur ini muncul, MVP **gagal secara filosofis**.

---

## Alur Penggunaan MVP (High-Level)

1. Lead membuat Decision sebelum atau saat pengembangan
2. Decision dibaca oleh tim sebagai referensi kerja
3. Ketika konteks berubah:
   - Decision diperbarui
   - Riwayat perubahan tersimpan
4. Decision digunakan sebagai:
   - bahan diskusi
   - referensi onboarding
   - refleksi pasca-insiden

Tidak ada tahap “approval”.
Tidak ada tahap “penilaian”.

---

## Kriteria Keberhasilan MVP

MVP dianggap berhasil jika:

- Tim mulai **membicarakan keputusan**, bukan hanya implementasi
- Asumsi mulai ditulis dan dipertanyakan
- Review menjadi lebih kontekstual
- Developer baru lebih cepat memahami konteks sistem

MVP **tidak diukur** dari:
- jumlah decision
- tingkat kepatuhan
- skor keamanan

---

## Batasan MVP

MVP ini:
- tidak menggantikan SDLC
- tidak menggantikan threat modeling
- tidak menggantikan secure coding guideline

Ia **melengkapi cara berpikir**, bukan proses formal.

---

## Hubungan dengan Buku

MVP ini adalah implementasi langsung dari ide buku:

> *Secure Coding: Cara Berpikir Developer di Dunia Nyata*

Bab yang paling terkait:
- Bab 1–3 (keputusan & asumsi)
- Bab 6 (trust & boundary)
- Bab 9 (kebiasaan)
- Bab 13–14 (budaya & keberlanjutan)

Namun, MVP dapat digunakan tanpa membaca buku.

---

## Penutup

Secure Decision MVP bukan tentang membuat sistem lebih aman secara instan.  
Ia tentang membuat **keputusan lebih jujur**.

Jika MVP ini membuat tim:
- lebih sadar
- lebih terbuka
- dan lebih bertanggung jawab

maka MVP ini telah memenuhi tujuannya.
