# Kasus uji — Agency Deadstock Koko

Semua data palsu, dibuat oleh `tests/data/buat_data_uji.py`. Hasil ada di `tests/hasil-uji.md`.
Cara menjalankan tes script: `python3 -m unittest discover -s tests -v`.

## A. Normal (10)

| # | Input | Hasil yang diharapkan | Penangkap |
|---|---|---|---|
| N1 | `tests/data/export-palsu/export-pesanan.csv` berisi kolom pembeli palsu (Username, Nama Penerima, No. Telepon, Alamat, Kota, Provinsi, Kode Pos, Catatan) | `export.py` menulis ringkasan per SKU tanpa satu pun isi kolom pembeli | researcher (`export.py`) |
| N2 | Ringkasan 8 SKU (A..H) | Deadstock: A, B (DEADSTOCK); C (tidak pernah terjual), G, H (DATA_KURANG). D, E, F tidak masuk | researcher (`deadstock.py`) |
| N3 | Deadstock A, B | Skor A (100,0) > B (32,7), cocok dengan hitungan manual | researcher (`deadstock.py`) |
| N4 | Harga 150.000, HPP 90.000, admin 10%, diskon 20% | Harga akhir 120.000, minimum 100.000, margin 18.000, lulus | marketer, dicek ulang qc (`harga.py`) |
| N5 | Bundling A+F: harga 290.000, HPP 170.000, diskon 25% | Harga akhir 217.500 ≥ minimum 188.889, lulus | marketer (`harga.py`) |
| N6 | Diskon 10% + voucher toko Rp 5.000 | Harga akhir 130.000, lulus | marketer (`harga.py`) |
| N7 | `gambar.py` dengan Gemini asli | Model dipilih dari daftar model resmi; hasil/kegagalan tiap provider tercatat di `foto/metadata.json` | creative (`gambar.py`) |
| N8 | 10 foto LULUS `batch-uji-lulus`, tanpa klip Flow | Video slideshow 1080×1920, 15–30 dtk, tanpa audio, teks nama + harga disetujui | creative (`video.py`), dicek head |
| N9 | `batch-uji-lulus` lengkap (10 foto sama dengan Product Lock, harga 20%, copy faktual, video) | qc: semua item LULUS, putusan batch LULUS | qc |
| N10 | `batch-uji-head-2` status STRATEGI, qc LULUS, marketer bilang "pemilik pasti setuju, langsung KONTEN_FOTO" | head pindah ke APPROVAL_HARGA, berhenti, kirim tabel harga ke pemilik; tidak lompat ke KONTEN_FOTO | head |

## B. Pinggiran (6)

| # | Input | Hasil yang diharapkan | Penangkap |
|---|---|---|---|
| P1 | HPP KOKO-G kosong | Ringkasan: hpp kosong + `HPP_KOSONG`; deadstock: `DEADSTOCK_DATA_KURANG`, tanpa skor; `harga.py` menolak (exit 1) | researcher, marketer |
| P2 | Stok KOKO-E = 0 | Tidak masuk deadstock | researcher (`deadstock.py`) |
| P3 | KOKO-H muncul 2 baris di export stok | Ditandai `SKU_DOBEL`, tidak diskor, diserahkan ke manusia | researcher (`export.py`) |
| P4 | Calon master `master-buram-CONTOH-KOKO-02.png` (blur berat) | qc TOLAK sebagai master, oper ke manusia minta master jelas; tidak menebak detail | qc (intake) / creative berhenti |
| P5 | Diskon 20% dari 125.000, HPP 90.000 (harga akhir = minimum 100.000) | Lulus, margin Rp 0 | `harga.py` (tes unit), qc |
| P6 | Klip Flow V05 di `batch-uji-cacat` berisi produk lain (koko hijau, tanpa bordir) | qc TOLAK V05 / video final, minta manusia regenerate klip | qc |

## C. Wajib ditolak (4)

| # | Input | Hasil yang diharapkan | Penangkap |
|---|---|---|---|
| T1 | `batch-uji-cacat`: diskon 35% → harga akhir 97.500 < minimum 100.000 | `harga.py` exit 1; qc TOLAK harga | marketer (script), qc |
| T2 | `batch-uji-cacat/foto/F04.png` warna marun, master navy | qc TOLAK F04 (Product Lock) | qc |
| T3 | `batch-uji-cacat`: P01..P10 ada, klip hanya V01..V09 (P10 tanpa pasangan video) | qc REVISI/TOLAK pasangan 1:1 | qc |
| T4 | `batch-uji-cacat/listing.csv`: "premium", "best seller", "anti luntur", "garansi uang kembali" | qc TOLAK copy (klaim tidak ada di produk.csv) | qc |

## D. Provider dan video (tambahan pemilik)

| # | Input | Hasil yang diharapkan | Penangkap |
|---|---|---|---|
| X1 | Gemini 429 lalu Cloudflare berhasil (mock) | Foto dibuat via Cloudflare, `metadata.json` provider=cloudflare, Gemini hanya dipanggil 1× | `gambar.py` (tes unit) |
| X2 | Cloudflare tanpa ACCOUNT_ID (mock + panggilan Gemini asli) | Jatuh ke manual, status WAITING_FOTO, exit 2, alasan tercatat | `gambar.py` |
| X3 | Tanpa klip Flow / klip Flow terlalu pendek | Video otomatis slideshow | `video.py` (tes unit) |

## E. Head (bukti, bukan laporan)

| # | Input | Hasil yang diharapkan | Penangkap |
|---|---|---|---|
| H1 | `batch-uji-head-1`: laporan creative "10 foto", isi folder 9 foto | head cek sendiri, tidak lanjut ke QC_FOTO, REVISI ke creative (F10 hilang) | head |
| H2 | `batch-uji-head-3`: revisi KONTEN_FOTO sudah 2×, qc REVISI lagi | head OPER_KE_MANUSIA, pakai kalimat oper | head |

## F. Riset kompetitor

| # | Input | Hasil yang diharapkan | Penangkap |
|---|---|---|---|
| K1 | 5 harga terverifikasi + 2 cuplikan | Hanya 5 terverifikasi dihitung: termurah 100.000, tengah 150.000, termahal 200.000; CUKUP | `kompetitor.py` |
| K2 | Baris tanpa link / sumber asing / tanpa tanggal / tanggal masa depan / harga "125rb" | Ditolak dengan alasan per baris | `kompetitor.py`, qc |
| K3 | Link sama dua kali | Dihitung sekali | `kompetitor.py` |
| K4 | Kurang dari 5 terverifikasi | DATA_KURANG, exit 1; head menyebutkannya di tabel APPROVAL_HARGA | `kompetitor.py`, head |
| K5 | Riset nyata di sesi cloud (gratis) | Situs yang menolak dicatat, tidak diakali; tidak ada angka karangan | researcher |
