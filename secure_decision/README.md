# Secure Decision App

Dokumen ini khusus untuk setup dan menjalankan aplikasi di folder `secure_decision/`.

Untuk memahami filosofi dan dokumentasi proyek, mulai dari [README.md](../README.md).

## Struktur Folder

- `app/` source code FastAPI
- `alembic/` migration database
- `knowledge_base/` kartu knowledge base dan skema
- `requirements.txt` dependency aplikasi
- `alembic.ini` konfigurasi Alembic

## Menjalankan Aplikasi

### 1. Buat virtual environment

```bash
python -m venv .venv
```

### 2. Aktifkan virtual environment

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\activate
```

### 3. Install dependency

```bash
pip install -r requirements.txt
```

### 4. Jalankan server

Dari folder `secure_decision/`:

```bash
uvicorn app.main:app --reload
```

Secara default aplikasi akan berjalan di `http://127.0.0.1:8000`.

## Database dan Migration

Project ini menggunakan SQLite untuk pengembangan lokal dan Alembic untuk migration schema.

Contoh perintah:

```bash
alembic upgrade head
```

Jika Anda perlu meninjau knowledge base, lihat:

- [knowledge_base/README.md](knowledge_base/README.md)

## Catatan

Database lokal seperti `secure_decision.db`, cache Python, dan script bantu tidak ditujukan sebagai bagian dokumentasi publik utama repo.
