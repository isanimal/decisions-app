# Secure Decision — Decision Lifecycle Specification

## Tujuan Dokumen

Dokumen ini mendefinisikan **siklus hidup (lifecycle)** sebuah *Decision* di Secure Decision.
Lifecycle ini memastikan bahwa keputusan:
- dibuat secara sadar
- berevolusi ketika konteks berubah
- tetap dapat dibaca dan diwariskan
- tidak pernah “menghilang” atau dinilai secara kaku

Lifecycle ini **bukan workflow approval**, **bukan SDLC**, dan **bukan kontrol keamanan**.

---

## Prinsip Lifecycle

1. **Decision is Living**
   Keputusan dianggap hidup dan dapat berubah seiring konteks.

2. **No Forced Perfection**
   Decision tidak harus lengkap sejak awal.

3. **Evolution over Replacement**
   Keputusan lama tidak dihapus; ia digantikan dengan sadar.

4. **History Matters**
   Perubahan adalah bagian dari nilai decision.

---

## Status Decision (Lifecycle States)

Secure Decision menggunakan **empat status ringan**:

### 1. `draft`
Decision masih dalam proses perumusan.

Karakteristik:
- decision statement boleh belum lengkap
- digunakan untuk eksplorasi awal
- belum dijadikan referensi utama tim

Aturan:
- Draft boleh diedit bebas
- Draft belum memerlukan history eksplisit

---

### 2. `active`
Decision telah cukup jelas untuk dijadikan acuan kerja.

Karakteristik:
- decision statement terisi secara sadar
- dibaca oleh tim
- menjadi referensi diskusi dan review

Aturan:
- Setiap perubahan bermakna pada decision `active` **harus menghasilkan history**
- Tidak ada approval atau penilaian otomatis

---

### 3. `superseded`
Decision tidak lagi relevan karena digantikan oleh decision baru.

Karakteristik:
- decision lama tetap dapat dibaca
- decision baru merujuk atau menggantikan konteksnya

Aturan:
- Decision `superseded` **tidak boleh diedit**
- Status ini menjaga jejak keputusan lama tanpa menghapusnya

---

### 4. `archived`
Decision tidak lagi digunakan, tetapi disimpan untuk referensi historis.

Karakteristik:
- sistem sudah berubah jauh
- decision jarang dirujuk, tapi masih bernilai pembelajaran

Aturan:
- Archived bersifat read-only
- Tidak ada kewajiban migrasi ke decision baru

---

## Transisi Antar Status

Transisi yang diperbolehkan:

- `draft` → `active`
- `active` → `superseded`
- `active` → `archived`
- `superseded` → `archived`

Transisi yang **tidak diperbolehkan**:
- `archived` → `active`
- `superseded` → `active`

Alasan:
> Keputusan lama tidak “dihidupkan kembali” tanpa konteks baru.

---

## Event Lifecycle (Konseptual)

### 1. Decision Created
- Decision dibuat sebagai `draft`
- Tujuan: eksplorasi dan perumusan awal

---

### 2. Decision Activated
- Draft dianggap cukup jelas untuk digunakan
- Tidak ada validasi otomatis
- Aktivasi adalah keputusan manusia

---

### 3. Decision Updated
- Konteks berubah
- Asumsi tidak lagi valid
- Trade-off bergeser

Aturan:
- Update pada decision `active` menghasilkan **history entry**
- Update memicu **prompt reflektif ringan** (opsional)

---

### 4. Decision Superseded
- Decision baru dibuat untuk konteks yang sama
- Decision lama ditandai sebagai `superseded`

Aturan:
- Superseding adalah tindakan sadar
- Decision lama tidak dihapus

---

### 5. Decision Archived
- Decision tidak lagi relevan
- Disimpan untuk pembelajaran

---

## Hubungan dengan History & Reflection

- **History**
  - Mencatat *apa yang berubah*, bukan *siapa yang salah*
  - Setiap update bermakna pada decision `active` menciptakan history

- **Reflection**
  - Muncul sebagai prompt saat update atau secara manual
  - Tidak mempengaruhi status
  - Tidak menghasilkan penilaian

---

## Anti-Pattern Lifecycle (Yang Dihindari)

Secure Decision **secara sadar menghindari**:

- lifecycle berbasis approval
- gate “secure / insecure”
- decision auto-expired
- decision scored atau diberi ranking
- forcing update berbasis waktu

Jika lifecycle berubah ke arah ini, arah proyek melenceng.

---

## Kriteria Lifecycle Berhasil

Lifecycle dianggap berhasil jika:
- decision lama masih bisa dibaca dan dipahami
- perubahan konteks memicu update, bukan blame
- tim terbiasa mengganti decision, bukan menambal asumsi
- knowledge transfer terjadi alami

---

## Penutup

Decision Lifecycle ini tidak dibuat untuk mengendalikan kerja tim.
Ia dibuat untuk **menjaga ingatan kolektif** dan **kejujuran keputusan**.

Jika lifecycle ini terasa ringan namun bermakna,
maka Secure Decision berjalan sesuai tujuan awalnya.
