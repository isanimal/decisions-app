# How to Read a Decision
**Onboarding Guide — Secure Decision**

Dokumen ini membantu Anda membaca sebuah *Decision* dengan cara yang benar.  
Bukan untuk menilai apakah keputusan itu “aman” atau “benar”,  
tetapi untuk memahami **cara berpikir** di baliknya.

Secure Decision tidak dibuat untuk memberi verdict.  
Ia dibuat untuk membuat keputusan **terlihat dan dapat dipahami**.

---

## Apa Itu Decision?

Decision adalah artefak berpikir.

Ia menangkap:
- apa yang ingin dicapai secara teknis
- asumsi yang dibuat
- penyederhanaan yang disadari
- batas yang tidak boleh dilanggar
- risiko yang diterima

Decision **bukan**:
- spesifikasi lengkap
- best practice
- audit report
- janji keamanan

---

## Cara Membaca Decision (Urutan yang Disarankan)

### 1. Baca Konteks, Bukan Solusi

Mulailah dari **Context**.

Tanyakan:
- Dalam situasi apa keputusan ini dibuat?
- Tekanan apa yang mungkin ada? (waktu, tim, kompleksitas)

Kesalahan umum:
> Langsung mencari “apa yang salah” tanpa memahami situasi.

---

### 2. Pahami Tujuan Teknisnya

Lanjutkan ke **Technical Goal**.

Tanyakan:
- Masalah operasional apa yang ingin diselesaikan?
- Apakah tujuannya realistis untuk konteks saat itu?

Ingat:
> Tujuan teknis sering lebih sempit dari tujuan bisnis.

---

### 3. Cari Asumsi yang Paling Kritis

Bagian **Assumptions** adalah kunci.

Tanyakan:
- Hal apa yang dianggap benar tanpa diverifikasi?
- Apa yang dipercaya tentang user, data, atau lingkungan?

Asumsi bukan kesalahan.
Asumsi yang **tidak disadari** adalah masalah.

---

### 4. Perhatikan Penyederhanaan yang Disadari

Baca **Conscious Simplifications** dengan tenang.

Tanyakan:
- Bagian mana yang sengaja dipercepat?
- Apa trade-off yang diterima?

Kesalahan umum:
> Menganggap penyederhanaan sebagai kelalaian.

Dalam Secure Decision:
> Penyederhanaan yang ditulis adalah tanda kedewasaan.

---

### 5. Hormati Batas yang Tidak Boleh Dilanggar

Bagian **Non-Negotiables** menunjukkan nilai inti.

Tanyakan:
- Di titik mana tim memilih untuk berhenti?
- Apa yang dianggap terlalu berisiko untuk disederhanakan?

Ini adalah “garis merah” dari decision tersebut.

---

### 6. Baca Risiko Tanpa Panik

Terakhir, baca **Accepted Worst-Case**.

Tanyakan:
- Jika asumsi salah, apa dampak terburuk yang diterima?
- Apakah risiko ini masih dapat diterima hari ini?

Catatan penting:
> Menulis worst-case ≠ menyerah pada risiko  
> Ini adalah bentuk kejujuran.

---

## Cara Membaca History (Jika Ada)

History menunjukkan **evolusi keputusan**, bukan kesalahan masa lalu.

Saat membaca history:
- fokus pada *apa yang berubah*
- pahami *kenapa* decision diperbarui
- jangan mencari siapa yang salah

Jika decision berubah:
> itu tanda sistem hidup, bukan gagal.

---

## Pertanyaan Reflektif untuk Pembaca

Setelah membaca sebuah decision, tanyakan pada diri Anda:

- Apakah konteks hari ini masih sama?
- Asumsi mana yang paling rapuh?
- Jika decision ini dibuat hari ini, apa yang berbeda?

Pertanyaan ini **tidak harus dijawab di tools**.
Diskusi sering lebih baik terjadi di:
- code review
- meeting
- pairing session

---

## Kesalahan Umum Saat Membaca Decision

Hindari:
- mencari “secure / insecure”
- membandingkan decision satu tim dengan tim lain
- menggunakan decision sebagai alat menyalahkan

Decision adalah **catatan berpikir**, bukan senjata evaluasi.

---

## Penutup

Membaca decision dengan benar berarti:
- memahami konteks
- menghargai trade-off
- dan menjaga ingatan kolektif tim

Jika Anda bisa menjelaskan kembali decision ini kepada orang lain  
tanpa menghakimi atau menyederhanakan secara berlebihan,  
berarti Anda telah membacanya dengan benar.

Secure Decision bekerja bukan karena fiturnya,  
tetapi karena cara Anda membacanya.
