# Secure Decision — Conceptual Data Model (MVP)

## Tujuan Model Ini

Model ini mendefinisikan tiga konsep inti:
- **Decision**
- **History**
- **Reflection**

Tujuan utamanya adalah menjaga konsistensi filosofi:
- keputusan dibuat eksplisit
- perubahan terdokumentasi sebagai evolusi keputusan
- refleksi dipakai sebagai prompt, bukan verdict

Model ini sengaja menghindari:
- skor
- status “secure/insecure”
- KPI, ranking, gamifikasi

---

## 1) Entity: Decision

### Definisi
Decision adalah unit utama yang mewakili **satu keputusan teknis yang disadari**, terkait fitur/sistem/perubahan penting.

Decision bukan task, bukan ticket, bukan vulnerability report.

### Atribut Inti (MVP)
- `decision_id`
  - Identitas unik (string/UUID)
- `title`
  - Judul decision (singkat, jelas)
- `context`
  - Konteks singkat (1–2 paragraf) tentang ruang lingkup keputusan
- `statement`
  - Objek Decision Statement (lihat sub-entity)
- `created_at`
- `updated_at`

### Atribut Opsional (disarankan, tetap ringan)
- `tags`
  - Misal: `auth`, `payments`, `internal-tool`, `api`
- `status`
  - **Bukan status keamanan**
  - Hanya lifecycle ringan: `draft` / `active` / `superseded` / `archived`
  - Tujuan: menjaga keterbacaan repositori decision (bukan penilaian)

### Invariants (Aturan Domain)
- Decision **harus** punya `title`.
- Decision boleh `draft` tanpa statement lengkap, tetapi:
  - Decision yang `active` **harus** punya statement minimal terisi.
- Decision **tidak boleh** punya atribut seperti:
  - `security_score`
  - `risk_score`
  - `pass/fail`

---

### Sub-Entity: DecisionStatement (Wajib)

DecisionStatement adalah inti makna decision.

Atribut minimal:
- `technical_goal`
  - Tujuan operasional teknis
- `assumptions`
  - Daftar asumsi utama (array string)
- `conscious_simplifications`
  - Penyederhanaan yang disadari (array string)
- `non_negotiables`
  - Batas yang tidak boleh dilanggar (array string)
- `accepted_worst_case`
  - Dampak terburuk yang diterima (string atau array)

Invariants:
- Tidak ada field yang memaksa “jawaban benar”.
- Semua field adalah naratif/teks, bukan checklist compliance.

---

## 2) Entity: History (DecisionHistory)

### Definisi
History adalah catatan evolusi Decision dari waktu ke waktu.

History dibuat untuk:
- knowledge transfer
- refleksi setelah perubahan konteks
- pembelajaran kolektif

History bukan log audit untuk mencari salah.

### Struktur Konseptual
History adalah kumpulan `DecisionRevision` yang terikat pada satu `Decision`.

Relasi:
- Decision `1..n` DecisionRevision

---

### Sub-Entity: DecisionRevision (MVP)

Atribut inti:
- `revision_id`
- `decision_id`
- `changed_at`
- `change_summary`
  - Ringkasan perubahan (singkat, human-readable)
- `changed_fields`
  - Daftar bagian yang berubah (misal: `assumptions`, `non_negotiables`)
- `before_snapshot` (opsional)
- `after_snapshot` (opsional)

Catatan:
- Snapshot dapat berupa teks ringkas, bukan full object.
- MVP boleh simpan snapshot penuh jika sederhana, tapi konsepnya:
  - yang penting adalah *cerita perubahan*, bukan detail teknis.

Invariants:
- Setiap update Decision yang meaningful **menciptakan** satu revision.
- History tidak menampilkan “penyebab” dalam bentuk blame.
- Tidak ada atribut seperti `fault_owner` atau `severity`.

---

## 3) Entity: Reflection

### Definisi
Reflection adalah mekanisme prompt pertanyaan yang membantu tim:
- mengevaluasi relevansi decision
- menyadari perubahan konteks
- menghindari asumsi menjadi blind spot

Reflection bukan rekomendasi otomatis.
Reflection tidak memberi verdict.

Ada dua jenis Reflection dalam MVP:
1. **ReflectionPrompt (template)**: bank pertanyaan
2. **ReflectionResponse (opsional)**: jawaban/refleksi yang disimpan

Relasi:
- Decision `0..n` ReflectionResponse
- ReflectionPrompt `1..n` digunakan oleh Decision/Update flow

---

### Sub-Entity: ReflectionPrompt (Template Bank)

Atribut inti:
- `prompt_id`
- `prompt_text`
  - Contoh: “Apakah asumsi ini masih relevan?”
- `category` (opsional)
  - Misal: `assumptions`, `boundary`, `failure`, `tradeoff`
- `trigger` (opsional)
  - Kapan prompt muncul: `on_create`, `on_update`, `manual`

Invariants:
- Prompt harus berupa pertanyaan reflektif.
- Prompt tidak boleh berupa perintah compliance seperti:
  - “Pastikan X sesuai standar Y”
- Prompt tidak boleh menghasilkan status/score.

---

### Sub-Entity: ReflectionResponse (Opsional, tapi powerful)

Atribut inti:
- `response_id`
- `decision_id`
- `prompt_id` (optional: kalau berasal dari template)
- `response_text`
- `created_at`

Opsional:
- `context_change_note`
  - “Apa yang berubah sejak decision dibuat?”

Invariants:
- Response bersifat naratif.
- Response tidak dipakai untuk scoring.

---

## Relasi Antar Entitas (Ringkas)

- Decision `1` — `n` DecisionRevision
- Decision `0` — `n` ReflectionResponse
- ReflectionPrompt `0` — `n` ReflectionResponse (opsional)

---

## Domain Events (Konsep, bukan implementasi)

Event ini membantu membangun flow tanpa teknis berat:

1. `DecisionCreated`
   - menghasilkan Decision baru
   - dapat memicu prompt reflektif ringan

2. `DecisionUpdated`
   - menghasilkan DecisionRevision
   - dapat memicu prompt “apa yang berubah?”

3. `DecisionSuperseded`
   - menandai decision lama sebagai tidak lagi aktif
   - menjaga sejarah tanpa menghapus

4. `ReflectionCaptured`
   - menyimpan response (opsional)

---

## Anti-Entities (Yang Tidak Ada)

Model ini secara sadar tidak memasukkan:
- `SecurityScore`
- `ComplianceChecklist`
- `TeamRanking`
- `DeveloperPerformanceMetric`
- `AutomatedRecommendationEngine`

Jika entitas semacam ini muncul, arah proyek melenceng dari manifesto.

---

## Kriteria Model Berhasil

Model ini dianggap berhasil jika:
- keputusan bisa dibaca dan dipahami oleh anggota baru
- perubahan konteks menghasilkan update decision yang “terlihat”
- tim berdiskusi lebih kontekstual tanpa merasa diaudit
- tidak ada tekanan untuk mengejar angka

---

## Penutup

Secure Decision bukan sistem untuk menentukan siapa benar.
Ia adalah sistem untuk memastikan keputusan tidak menghilang.

Data model ini menjaga agar:
- keputusan menjadi eksplisit
- evolusi keputusan terdokumentasi
- refleksi menjadi kebiasaan, bukan ritual compliance
