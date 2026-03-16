# Project Checklist

Checklist ringkas ini dipakai untuk menjaga repo tetap rapi sebelum dibagikan atau dipublikasikan.

## Dokumentasi

- [ ] `README.md` menggambarkan proyek dengan benar
- [ ] link ke `docs/` dan `EXAMPLES/` valid
- [ ] `secure_decision/README.md` masih sesuai dengan cara menjalankan aplikasi
- [ ] dokumen internal tidak tampil sebagai titik masuk utama

## Source Code

- [ ] source code utama ada di `secure_decision/app/`
- [ ] migration ada di `secure_decision/alembic/`
- [ ] knowledge base dan schema konsisten

## Repo Hygiene

- [ ] file lokal seperti database dan cache tidak ikut ter-track
- [ ] helper script yang tidak perlu untuk publik tidak ikut dipush
- [ ] tidak ada link mati atau path yang salah di dokumentasi

## Sebelum Push

- [ ] `git status` bersih atau hanya berisi perubahan yang memang ingin dipush
- [ ] commit message menjelaskan perubahan secara singkat
- [ ] branch sudah sinkron dengan remote yang benar
