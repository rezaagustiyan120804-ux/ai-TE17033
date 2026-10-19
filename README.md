# KELOMPOK AI-TE17033 PENJADWALAN KULIAH / RUANGAN (CONSTRAIN SEARCH)

**Tugas - Kecerdasan Buatan (AI)** Constraint Satisfaction Problem (CSP) dan Constraint Search
Kelompok/Kelas: AI-TE-17033

## Anggota

| Peran | Nama | Branch |
| ----- | ---- | ------ |
| Ketua / Pembuat | Reza Agustiyan | `main` |
| Dev 1 | Adryan Syarif | Dev1 |

## Deskripsi

Program ini membuat jadwal kuliah dan penempatan ruangan secara otomatis tanpa bentrok
(data disederhanakan, hanya untuk keperluan tugas).

Masalah dimodelkan sebagai **Constraint Satisfaction Problem (CSP)**:

| Komponen | Isi |
| -------- | --- |
| Variabel | Setiap sesi mata kuliah yang harus dijadwalkan |
| Domain | Kombinasi (hari, jam, ruangan) yang tersedia |
| Constraint | Aturan yang tidak boleh dilanggar (lihat tabel di bawah) |

Solusi dicari dengan **Constraint Search**. Beberapa strategi dijalankan dan dibandingkan:

| Algoritma | Jenis | Keterangan |
| --------- | ----- | ---------- |
| Backtracking | Dasar | Menetapkan nilai satu per satu, mundur jika melanggar constraint |
| Backtracking + Forward Checking | Pemangkasan domain | Setelah memilih nilai, domain variabel lain dipangkas |
| Backtracking + MRV | Heuristik variabel | Pilih variabel dengan sisa domain paling sedikit lebih dulu |

## Constraint

| ID | Jenis | Aturan |
| -- | ----- | ------ |
| C1 | Hard | Satu ruangan tidak boleh dipakai dua kelas pada hari dan jam yang sama |
| C2 | Hard | Satu dosen tidak boleh mengajar dua kelas pada hari dan jam yang sama |
| C3 | Hard | Kelas satu angkatan/semester tidak boleh bentrok jadwalnya |
| C4 | Hard | Kapasitas ruangan harus lebih besar atau sama dengan jumlah mahasiswa |
| C5 | Hard | Jenis ruangan harus sesuai (kelas teori di ruang kelas, praktikum di laboratorium) |
| C6 | Soft | Hindari jadwal terlalu sore atau jeda kosong terlalu panjang (opsional) |

## Struktur Folder

```
ai-TE17033/
├── README.md
└── penjadwalan/
    ├── data.py          # data mata kuliah, dosen, ruangan, slot waktu
    ├── csp.py           # definisi variabel, domain, constraint
    ├── search.py        # Backtracking, Forward Checking, MRV
    └── main.py          # program utama
```

> Sesuaikan nama file dan folder dengan isi repository kamu.

## Requirements

- Python 3.8 atau lebih baru
- Tidak ada library tambahan (hanya library standar, misalnya `itertools`, `collections`, `time`)

## Cara Pakai

1. Clone repository:

```
git clone https://github.com/rezaagustiyan120804-ux/ai-TE17033.git
cd ai-TE17033/penjadwalan
```

2. Jalankan program utama (lihat bagian Running).
3. Pilih algoritma yang ingin dipakai, atau jalankan semuanya untuk dibandingkan.
4. Program menampilkan jadwal hasil dan tabel perbandingan algoritma.

## Running

```
cd penjadwalan
python main.py
```

Tes tiap modul secara terpisah:

```
python data.py       # cek data mata kuliah, dosen, ruangan
python csp.py        # cek constraint
python search.py     # contoh perbandingan algoritma
```

### Contoh Output

Contoh format hasil (ganti dengan output asli programmu):

```
Hari    Jam          Mata Kuliah          Dosen        Ruangan
--------------------------------------------------------------
Senin   08.00-09.40  Kecerdasan Buatan    Pak A        R101
Senin   10.00-11.40  Basis Data           Bu B         Lab 2
Selasa  08.00-09.40  Jaringan Komputer    Pak C        R102

Algoritma         Waktu (ms)   Node Dikunjungi   Backtrack
-----------------------------------------------------------
Backtracking            120             5400          2100
Forward Checking         35              900           210
FC + MRV                 12              240            30
```

## Catatan

- Data mata kuliah, dosen, dan ruangan hanya contoh untuk keperluan tugas, bukan data resmi kampus.
- Constraint bertipe hard wajib terpenuhi; constraint soft hanya preferensi.
- Jika tidak ada solusi yang memenuhi semua constraint, program melaporkan bahwa jadwal tidak dapat dibuat.

## Keterbatasan

- Jumlah mata kuliah, dosen, dan ruangan masih terbatas.
- Preferensi dosen (misalnya hari tidak bisa mengajar) belum semuanya dimodelkan.
- Backtracking murni bisa lambat jika jumlah variabel bertambah banyak.

## Pengembangan Selanjutnya

- Menambah algoritma lain (misalnya AC-3 atau Min-Conflicts).
- Menambah antarmuka sederhana untuk input data.
- Ekspor jadwal ke file CSV atau Excel.
