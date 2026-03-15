# Tutorial Push ke GitHub

Panduan ini disesuaikan untuk proyek `Secure Decision` di folder ini.

## 1. File yang Sebaiknya Masuk ke GitHub

Yang penting untuk dipush:

- `README.md`
- `LICENSE`
- `Contributing.md`
- `CHECKLIST.md`
- `docs/`
- `EXAMPLES/`
- `ISSUE_TEMPLATE/`
- `secure_decision/app/`
- `secure_decision/alembic/`
- `secure_decision/alembic.ini`
- `secure_decision/requirements.txt`
- `secure_decision/README.md`
- `secure_decision/knowledge_base/cards/`
- `secure_decision/knowledge_base/schema/`
- `secure_decision/knowledge_base/dist/`
- `secure_decision/knowledge_base/README.md`

## 2. File yang Tidak Perlu Masuk

Sesuai kebutuhan Anda, yang tidak perlu dipush:

- file QA seperti `QA_*.md`
- helper script seperti `scripts/` dan `secure_decision/scripts/`
- script validasi knowledge base di `secure_decision/knowledge_base/scripts/`
- file database lokal `secure_decision/secure_decision.db`
- cache Python seperti `__pycache__/` dan `*.pyc`
- virtual environment seperti `.venv/`

Semua itu sudah dibantu oleh `.gitignore`.

## 3. Rapikan Repo Sebelum Commit

Cek file yang berubah:

```bash
git status
```

Kalau masih ada file yang tidak ingin ikut, pastikan sudah cocok dengan `.gitignore`.

Kalau ada file yang sebelumnya sudah sempat ter-track, lepaskan dari staging/index:

```bash
git rm --cached -r scripts secure_decision/scripts secure_decision/knowledge_base/scripts
git rm --cached secure_decision/secure_decision.db
git rm --cached -r secure_decision/app/__pycache__
```

Kalau ada path yang ternyata belum pernah ter-track, Git akan memberi pesan aman, itu tidak masalah.

## 4. Inisialisasi Git Jika Belum

Kalau folder ini belum menjadi repo Git:

```bash
git init
git branch -M main
```

Kalau sudah pernah `git init`, langkah ini tidak perlu diulang.

## 5. Tambahkan File Penting

Tambahkan isi repo yang sudah dirapikan:

```bash
git add .
```

Cek lagi sebelum commit:

```bash
git status
```

Pastikan yang terlihat hanya file penting aplikasi.

## 6. Commit Pertama

```bash
git commit -m "Initial commit: Secure Decision app"
```

## 7. Buat Repository di GitHub

Di GitHub:

1. Buka `https://github.com/new`
2. Isi nama repo, misalnya `secure-decision`
3. Pilih `Public` atau `Private`
4. Jangan centang `Add a README`, `.gitignore`, atau license jika repo lokal ini sudah punya file tersebut
5. Klik `Create repository`

## 8. Hubungkan Repo Lokal ke GitHub

Setelah repo GitHub dibuat, GitHub akan memberi URL seperti:

```bash
git remote add origin https://github.com/USERNAME/secure-decision.git
```

Verifikasi:

```bash
git remote -v
```

## 9. Push ke GitHub

```bash
git push -u origin main
```

Setelah itu, push berikutnya cukup:

```bash
git push
```

## 10. Alur Update Berikutnya

Kalau nanti Anda mengubah aplikasi:

```bash
git status
git add .
git commit -m "Deskripsi perubahan"
git push
```

## 11. Saran Isi Repo untuk Publik

Agar repo tetap bersih, fokuskan isi GitHub ke:

- source code aplikasi
- template HTML
- model dan service
- migration Alembic
- knowledge base
- dokumentasi utama

Tidak perlu memasukkan:

- hasil QA internal
- script bantu pembuatan data
- script smoke test
- file database lokal
- cache hasil run lokal

## 12. Kalau Muncul Error Umum

Kalau `remote origin already exists`:

```bash
git remote set-url origin https://github.com/USERNAME/secure-decision.git
```

Kalau branch utama Anda masih `master`:

```bash
git branch -M main
git push -u origin main
```

Kalau diminta login, gunakan salah satu:

- GitHub Desktop
- credential manager Git
- personal access token GitHub

## 13. Urutan Praktis Paling Singkat

Kalau mau versi singkatnya:

```bash
git init
git branch -M main
git add .
git commit -m "Initial commit: Secure Decision app"
git remote add origin https://github.com/USERNAME/secure-decision.git
git push -u origin main
```
