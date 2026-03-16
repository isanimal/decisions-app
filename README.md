# Secure Decision

Secure Decision adalah aplikasi open source untuk membantu tim engineering membuat keputusan teknis yang lebih sadar, eksplisit, dan dapat diwariskan.

Proyek ini bukan vulnerability scanner, bukan compliance engine, dan bukan alat scoring keamanan. Fokusnya adalah membuat keputusan teknis, asumsi, penyederhanaan, dan trade-off menjadi terlihat.

## Apa yang Dibantu Secure Decision

Secure Decision membantu tim untuk:

- menulis decision statement secara eksplisit
- mencatat asumsi dan penyederhanaan yang disadari
- menyimpan riwayat perubahan keputusan
- memicu diskusi yang lebih sehat dalam review dan perencanaan

Secure Decision tidak bertujuan untuk:

- memberi label "aman" atau "tidak aman"
- memberi skor atau ranking
- membandingkan tim atau individu
- menggantikan penilaian profesional

## Mulai dari Sini

Jika ini pertama kali Anda membuka proyek ini, urutan baca yang disarankan:

1. [How to Read a Decision](docs/HOW_TO_READ_DECISION.md)
2. [How to Write a Good Decision](docs/HOW_TO_WRITE_A_GOOD_DECISION.md)
3. [Documentation Index](docs/README.md)
4. [Examples](EXAMPLES/README.md)

## Dokumentasi

Dokumentasi dibagi menjadi beberapa bagian:

- [docs/README.md](docs/README.md) untuk indeks dokumentasi utama
- [secure_decision/README.md](secure_decision/README.md) untuk setup dan menjalankan aplikasi
- [Contributing.md](Contributing.md) untuk panduan kontribusi

## Struktur Repo

Struktur inti repo ini:

- `secure_decision/app/` source code aplikasi
- `secure_decision/alembic/` migration database
- `secure_decision/knowledge_base/` knowledge base dan skema
- `docs/` dokumentasi konsep, alur, dan referensi
- `EXAMPLES/` contoh decision

## Filosofi Proyek

Secure Decision dibangun di atas prinsip berikut:

- keamanan lahir dari keputusan, bukan dari alat
- asumsi yang tidak ditulis adalah sumber risiko
- checklist tanpa konteks tidak membangun budaya
- pengukuran harus mendukung pembelajaran, bukan menghukum

Jika suatu fitur bertentangan dengan prinsip-prinsip di atas, maka fitur tersebut salah arah.

## Status Dokumen

`README.md` ini adalah pintu masuk utama untuk publik.

Dokumen seperti `IMPLEMENTATION_COMPLETE.md`, `SETUP_FIX_REPORT.md`, dan `ISSUE_LOG.md` adalah catatan kerja/internal, bukan titik mulai yang disarankan untuk pengguna baru.

> Secure Decision works when it is read thoughtfully.
> Tools are secondary. Decisions are primary.
