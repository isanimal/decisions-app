# Secure Decision
**Decision-Oriented Secure Coding**

## Tentang Proyek Ini

Secure Decision adalah proyek open source yang dibuat untuk membantu **lead developer, tech lead, dan tim engineering** membuat keputusan teknis yang lebih sadar, eksplisit, dan dapat diwariskan.

Proyek ini **bukan** vulnerability scanner.  
Proyek ini **bukan** alat penilaian keamanan.  
Proyek ini **bukan** pengganti penilaian profesional.

Secure Decision hadir untuk menjawab satu pertanyaan mendasar:

> *Bagaimana kita memastikan bahwa keputusan teknis yang kita ambil hari ini dapat dipahami, dipertanggungjawabkan, dan dievaluasi di masa depan?*

---

## Getting Started

Secure Decision bukan alat yang perlu “dipelajari fiturnya”,  
tetapi cara berpikir yang perlu **dibaca dan dipahami**.

Jika ini pertama kali Anda menggunakan Secure Decision,  
kami sangat menyarankan urutan berikut:

1. **[How to Read a Decision](HOW_TO_READ_A_DECISION.md)**  
   Pelajari cara membaca sebuah decision tanpa menghakimi atau mencari verdict.

2. **[How to Write a Good Decision](HOW_TO_WRITE_A_GOOD_DECISION.md)**  
   Panduan praktis menulis decision yang jujur, kontekstual, dan berguna.

3. **[Examples](examples/)**  
   Lihat contoh decision nyata untuk memahami bagaimana trade-off ditulis secara eksplisit.

Dokumen-dokumen ini dirancang untuk membantu Anda masuk ke mindset Secure Decision  
sebelum menggunakan tools atau menulis decision Anda sendiri.
> Secure Decision works when it is read thoughtfully.
> Tools are secondary. Decisions are primary.

## local dev
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows PowerShell

pip install -r requirements.txt
uvicorn app.main:app --reload

---

## Masalah yang Kami Sasar

Dalam praktik pengembangan perangkat lunak, banyak keputusan penting terjadi secara implisit:
- asumsi tidak ditulis
- penyederhanaan dilakukan karena tekanan waktu
- ekspektasi hanya hidup di kepala lead atau senior developer

Ketika sistem berkembang, konteks berubah, atau tim berganti, keputusan-keputusan ini sering hilang.  
Masalah keamanan yang muncul kemudian diperlakukan sebagai kegagalan teknis, padahal akarnya adalah **keputusan yang tidak pernah dibuat eksplisit**.

Secure Decision dibuat untuk membantu mengatasi masalah ini.

---

## Prinsip Dasar

Proyek ini dibangun di atas prinsip-prinsip berikut:

- **Keamanan lahir dari keputusan, bukan dari alat**
- **Asumsi yang tidak ditulis adalah sumber risiko**
- **Checklist tanpa konteks tidak membangun budaya**
- **Pengukuran harus mendukung pembelajaran, bukan menghukum**

Karena itu, Secure Decision secara sadar **tidak**:
- memberikan skor keamanan
- memberi label “aman” atau “tidak aman”
- membandingkan tim atau individu
- memaksakan kepatuhan formal

---

## Apa yang Dilakukan Secure Decision

Secure Decision membantu tim untuk:

- Menuliskan **decision statement** secara eksplisit  
- Mendefinisikan asumsi, batas kepercayaan, dan penyederhanaan yang disadari  
- Menyimpan sejarah keputusan untuk keperluan refleksi dan transfer pengetahuan  
- Memicu diskusi yang lebih sehat dalam review dan perencanaan  

Tools ini berfokus pada **membuat keputusan terlihat**, bukan menilai hasilnya.

---

## Untuk Siapa Proyek Ini Dibuat

Secure Decision ditujukan untuk:

- **Tech Lead / Lead Developer**  
  yang perlu menyelaraskan ekspektasi tim tanpa micro-management

- **Engineering Manager**  
  yang ingin meningkatkan efektivitas tim tanpa menambah beban administratif

- **Tim Developer Kecil hingga Menengah**  
  yang membutuhkan kejelasan keputusan, bukan kontrol tambahan

Proyek ini **bukan** ditujukan untuk:
- organisasi yang mencari compliance otomatis
- tim yang membutuhkan laporan audit instan
- penggunaan sebagai alat evaluasi kinerja individu

---

## Filosofi Open Source

Secure Decision bersifat **open source secara sadar dan etis**.

Kami percaya bahwa:
- transparansi membangun kepercayaan
- logika pengambilan keputusan harus dapat dibaca manusia
- komunitas berhak menjaga arah filosofis proyek

Kontribusi yang bertentangan dengan prinsip inti proyek—seperti penambahan scoring, ranking, atau KPI—akan **ditolak**, meskipun secara teknis baik.

Ini bukan soal membatasi inovasi, tetapi menjaga integritas tujuan proyek.

---

## Struktur Proyek (High-Level)

Proyek ini berfokus pada konsep inti berikut:

- **Decision**  
  Pernyataan tujuan, asumsi, penyederhanaan, dan risiko

- **History**  
  Riwayat perubahan keputusan dari waktu ke waktu

- **Reflection**  
  Pertanyaan yang membantu tim mengevaluasi relevansi keputusan

Detail implementasi bersifat minimal dan dapat berkembang secara bertahap.

---

## Hubungan dengan Buku

Secure Decision terinspirasi langsung dari buku:

> **Secure Coding: Cara Berpikir Developer di Dunia Nyata**

Proyek ini adalah **perpanjangan praktis** dari ide-ide dalam buku tersebut, khususnya:
- keputusan sehari-hari
- asumsi desain
- budaya kerja
- keberlanjutan praktik secure coding

Namun, Secure Decision **dapat digunakan secara mandiri** tanpa membaca buku.

---

## Kontribusi

Jika Anda ingin berkontribusi:
- pahami prinsip inti proyek
- jelaskan **keputusan apa yang dibantu** oleh kontribusi Anda
- hormati bahwa proyek ini adalah **decision-support**, bukan security scoring engine

Diskusi lebih dihargai daripada fitur.

---

## Penutup

Secure Decision tidak bertujuan membuat developer lebih takut.  
Ia bertujuan membuat keputusan lebih sadar.

Jika tools ini membantu tim Anda:
- berdiskusi lebih jujur
- memahami konteks keputusan lama
- dan bekerja lebih efektif tanpa menambah tekanan

maka proyek ini telah menjalankan fungsinya.

---

### Status

README ini adalah **dokumen filosofis utama** proyek.  
Jika suatu hari fitur bertentangan dengan isi dokumen ini, **fitur tersebut salah arah**.
