# How to Write a Good Decision
**Practical Guide — Secure Decision**

Dokumen ini membantu Anda **menulis Decision yang berguna**,  
bukan yang terdengar pintar, bukan yang terlihat “secure”,  
dan bukan yang mencoba menutup semua risiko.

Decision yang baik bukan yang sempurna.  
Decision yang baik adalah yang **jujur dan dapat dipahami orang lain**.

---

## Apa Tujuan Menulis Decision?

Menulis Decision bukan untuk:
- membuktikan bahwa Anda benar
- menunjukkan kepatuhan terhadap standar
- menghindari tanggung jawab

Menulis Decision bertujuan untuk:
- membuat asumsi terlihat
- menjelaskan trade-off yang dipilih
- membantu orang lain memahami *kenapa* keputusan ini diambil

Jika orang lain bisa membaca decision Anda dan berkata  
“oh, masuk akal di konteks itu”, maka decision Anda berhasil.

---

## Kapan Sebuah Decision Perlu Ditulis?

Tulislah Decision ketika:
- Anda membuat trade-off (keamanan vs waktu, kompleksitas vs kecepatan)
- Anda menyederhanakan sesuatu “untuk sementara”
- Anda mengandalkan asumsi tertentu (internal-only, trusted user, dll)
- Anda tahu keputusan ini akan dipertanyakan di masa depan

Jika tidak ada trade-off, biasanya tidak perlu Decision.

---

## Cara Menulis Decision (Langkah demi Langkah)

### 1. Tulis Konteks dengan Jujur

Mulai dari **Context**, bukan solusi.

Tulis:
- sistem atau fitur apa yang sedang dibahas
- batasan nyata (waktu, tim, infrastruktur)

Hindari:
- justifikasi panjang
- bahasa defensif

Contoh baik:
> “Fitur ini dibuat untuk internal admin panel dengan tim kecil dan deadline ketat.”

---

### 2. Rumuskan Tujuan Teknis (Bukan Janji)

Di **Technical Goal**, tulis apa yang ingin dicapai sistem secara operasional.

Fokus pada:
- fungsi sistem
- bukan klaim keamanan

Contoh:
> “Membatasi akses ke admin panel agar hanya user internal yang dapat masuk.”

Hindari:
> “Membuat sistem yang aman dari semua serangan.”

---

### 3. Tuliskan Asumsi yang Anda Percaya Hari Ini

Bagian **Assumptions** adalah inti dari Decision.

Tulis asumsi yang Anda:
- percaya
- andalkan
- belum diverifikasi sepenuhnya

Contoh:
> “Admin panel hanya diakses melalui VPN internal.”

Catatan penting:
> Asumsi bukan kesalahan.  
> Asumsi yang tidak ditulis adalah masalah.

---

### 4. Akui Penyederhanaan yang Anda Ambil

Di **Conscious Simplifications**, tulis apa yang Anda sengaja tidak lakukan.

Ini bukan pengakuan dosa.  
Ini catatan trade-off.

Contoh:
> “MFA belum diterapkan untuk mengurangi friksi operasional.”

Decision yang baik **tidak berpura-pura sempurna**.

---

### 5. Tetapkan Batas yang Tidak Boleh Dilanggar

Di **Non-Negotiables**, tulis garis merah Anda.

Ini adalah titik di mana tim harus berhenti dan berpikir ulang.

Contoh:
> “Credential tidak boleh disimpan dalam kode atau config publik.”

Bagian ini membantu tim memahami:
> “Di sini kita kompromi, di sini tidak.”

---

### 6. Tulis Risiko Terburuk Tanpa Drama

Di **Accepted Worst-Case**, jawab satu pertanyaan:
> “Jika asumsi salah, apa dampak terburuk yang kita terima?”

Tulis dengan tenang, bukan menakut-nakuti.

Contoh:
> “Jika VPN bocor, admin panel bisa diakses sampai credential di-rotate.”

Ini bukan tanda menyerah,  
ini tanda kedewasaan.

---

## Apa yang Tidak Perlu Anda Lakukan

Saat menulis Decision, Anda **tidak perlu**:
- menyebutkan CVE
- menulis checklist panjang
- membuktikan compliance
- membandingkan diri dengan best practice

Decision bukan laporan audit.

---

## Ciri Decision yang Baik

Decision yang baik biasanya:
- singkat tapi padat
- bisa dibaca dalam 3–5 menit
- terasa “manusiawi”
- masih masuk akal meski dibaca 6 bulan kemudian

Jika decision Anda perlu banyak penjelasan lisan tambahan,  
biasanya konteksnya belum cukup jelas.

---

## Ciri Decision yang Buruk

Waspadai Decision yang:
- terlalu umum
- penuh jargon
- tidak punya asumsi
- tidak mengakui penyederhanaan
- terdengar seperti pembelaan diri

Decision bukan tempat untuk terlihat pintar.

---

## Penutup

Menulis Decision adalah latihan kejujuran profesional.

Anda tidak sedang menulis untuk hari ini saja,  
tetapi untuk:
- diri Anda di masa depan
- rekan tim baru
- orang yang harus merawat sistem ini setelah Anda pergi

Jika Decision Anda membantu mereka memahami *kenapa* sesuatu dibuat seperti itu,  
maka Anda telah menulis Decision yang baik.

Secure Decision bekerja bukan karena formatnya,  
tetapi karena keberanian Anda menulis dengan jujur.
