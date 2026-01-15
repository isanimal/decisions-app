# Secure Decision — UX Flow (MVP)
**Decision-Oriented Secure Coding**

## Tujuan UX Flow Ini

UX Secure Decision dirancang untuk:
- mendorong refleksi, bukan kecepatan
- membuat keputusan terlihat, bukan tersembunyi
- meminimalkan friksi, tanpa menghilangkan makna

UX ini **tidak dirancang untuk optimasi klik**,  
tetapi untuk **kualitas interaksi berpikir**.

---

## Prinsip UX Dasar

1. **Write Less, Think More**  
   Input singkat, pertanyaan tajam.

2. **No Verdict UI**  
   Tidak ada status “aman / tidak aman”.

3. **Context First**  
   Pengguna selalu diingatkan *kenapa* decision ini ada.

4. **History Is a Feature**  
   Riwayat perubahan sama pentingnya dengan versi terbaru.

---

## Flow 0 — Entry Point

### Kondisi Awal
Pengguna membuka Secure Decision.

### Yang Ditampilkan
- Daftar Decision yang ada (jika ada)
- CTA utama:  
  **“Create a new decision”**

Tidak ada:
- dashboard statistik
- grafik
- skor
- notifikasi agresif

---

## Flow 1 — Create Decision

### Step 1: Naming the Decision
Pengguna diminta mengisi:
- **Judul Decision**
  - Contoh:  
    “Authentication flow for internal admin panel”

- **Konteks Singkat**
  - 1–2 kalimat
  - Fokus pada *apa yang sedang diputuskan*, bukan solusi

Tujuan step ini:
- memastikan decision *nyata*, bukan abstrak

---

### Step 2: Decision Statement (Inti UX)

Pengguna menjawab **5 pertanyaan inti**, satu per satu.

Setiap pertanyaan:
- ditampilkan sendiri (tidak sekaligus)
- tidak ada validasi “benar / salah”
- boleh kosong sementara (draft)

#### 1. Tujuan Teknis
> “Apa tujuan operasional dari decision ini?”

UX cue:
- placeholder berisi contoh kalimat
- penekanan pada *fungsi sistem*

---

#### 2. Asumsi Utama
> “Asumsi apa yang sedang kita buat?”

UX cue:
- teks bantuan:  
  “Asumsi tentang user, data, lingkungan, atau trust boundary”

---

#### 3. Penyederhanaan yang Disadari
> “Bagian mana yang sengaja kita sederhanakan atau percepat?”

UX cue:
- pengingat halus:  
  “Penyederhanaan bukan kesalahan, selama disadari”

---

#### 4. Batas yang Tidak Boleh Dilanggar
> “Hal apa yang tidak boleh disederhanakan?”

UX cue:
- dorongan berpikir:  
  “Di titik mana tim harus berhenti dan berpikir ulang?”

---

#### 5. Risiko yang Diterima
> “Jika asumsi salah, dampak terburuk apa yang kita terima?”

UX cue:
- tidak ada wording menakutkan
- fokus pada kesadaran, bukan paranoia

---

### Step 3: Save Decision

Saat menyimpan:
- tidak ada “approval”
- tidak ada skor
- hanya konfirmasi:  
  **“Decision saved. This decision can evolve over time.”**

---

## Flow 2 — View Decision

### Tampilan Decision
Decision ditampilkan sebagai:
- ringkasan konteks
- decision statement (5 bagian)
- tanggal dibuat & terakhir diubah

Penekanan UX:
- **mudah dibaca**
- **mudah dibagikan**
- cocok untuk onboarding & diskusi

---

## Flow 3 — Decision History

### Akses History
Pengguna dapat membuka:
- “View decision history”

### Isi History
- daftar perubahan
- setiap perubahan menunjukkan:
  - bagian apa yang berubah
  - kapan perubahan terjadi

Tidak ada:
- blame
- highlight “kesalahan”
- perbandingan skor

Tujuan UX:
> Melihat **bagaimana keputusan berevolusi**, bukan siapa yang salah.

---

## Flow 4 — Update Decision

### Trigger Update
Decision diperbarui ketika:
- konteks berubah
- asumsi tidak lagi valid
- sistem berkembang

### UX saat Update
- sistem menampilkan decision lama
- pengguna mengedit bagian relevan
- sebelum menyimpan, muncul prompt reflektif:

> “Apa yang berubah sejak decision ini dibuat?”

Prompt ini:
- opsional
- tidak wajib dijawab
- berfungsi sebagai *pause for thinking*

---

## Flow 5 — Reflection Prompt (Pasif)

Secure Decision secara berkala (atau manual) menampilkan pertanyaan seperti:
- “Apakah asumsi ini masih relevan?”
- “Apa konsekuensi jika decision ini diterapkan hari ini?”

Catatan penting:
- tidak ada notifikasi agresif
- tidak ada deadline
- refleksi adalah undangan, bukan perintah

---

## Flow 6 — Sharing & Discussion (Non-Technical)

Decision dapat:
- dibaca oleh tim
- dibagikan sebagai link
- dijadikan referensi diskusi

Tidak ada:
- komentar inline panjang
- thread debat di tools

Diskusi **didorong terjadi di luar tools**:
- code review
- meeting
- pairing

Tools ini **memicu**, bukan menampung semua diskusi.

---

## Anti-Pattern UX (Yang Sengaja Dihindari)

UX Secure Decision **secara sadar menghindari**:

- indikator warna merah / hijau
- progress bar keamanan
- gamifikasi
- notifikasi “decision overdue”
- “best practice suggestion”

Jika UX mengarah ke ini, berarti **arah proyek melenceng**.

---

## Kriteria UX Berhasil

UX dianggap berhasil jika:
- pengguna merasa “dipaksa berpikir” dengan cara yang wajar
- diskusi teknis menjadi lebih kontekstual
- decision lama masih dibaca, bukan dilupakan
- tools tidak terasa seperti beban tambahan

---

## Penutup

UX Secure Decision tidak dirancang untuk:
- membuat pekerjaan lebih cepat
- membuat sistem terlihat lebih aman

UX ini dirancang untuk:
> membuat keputusan lebih jujur,  
> dan percakapan lebih bermakna.
