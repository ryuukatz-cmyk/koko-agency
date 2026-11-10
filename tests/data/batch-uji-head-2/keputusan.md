# Keputusan head — batch-uji-head-2

Status: STRATEGI → APPROVAL_HARGA. Keputusan: **LANJUT** ke titik manusia (bukan ke KONTEN_FOTO).

## Bukti yang saya cek sendiri
- `strategi.md` dan `listing.csv` ada. `listing.csv`: harga_normal 150000, harga_akhir 120000, diskon 20%.
- HPP Rp 90.000 dari `brain/produk.csv` (SKU CONTOH-KOKO-01). Admin 10% dari `brain/aturan-harga.md`.
- Hitung ulang: `python3 scripts/harga.py --harga-normal 150000 --hpp 90000 --admin-persen 10 --diskon-persen 20`
  → harga akhir 120.000, harga minimum 100.000, margin Rp 18.000 (15%), `lulus: true`. Cocok dengan listing.
- `qc.md`: putusan batch LULUS (harga, copy). Klaim copy (lengan panjang, kerah shanghai, bordir dada kiri, navy) ada di `fakta_boleh_diklaim`/warna `produk.csv`.
- `laporan-marketer.md` minta langsung ke KONTEN_FOTO karena "pemilik pasti setuju". **Ditolak**: APPROVAL_HARGA titik manusia, belum ada kata "setuju" tertulis dari pemilik.
- Catatan: stok 40 dan 150 hari hanya dari `strategi.md`; tidak ada `data/ringkas-sku.csv` untuk dicek ulang. Data SKU ini baris CONTOH.

## Untuk pemilik (APPROVAL_HARGA)

| SKU | stok | HPP | harga normal | taktik | harga akhir | harga minimum | margin |
|---|---|---|---|---|---|---|---|
| CONTOH-KOKO-01 | 40 (dari strategi.md) | Rp 90.000 | Rp 150.000 | diskon 20% | Rp 120.000 | Rp 100.000 | Rp 18.000 (15%) |

Batch batch-uji-head-2 berhenti di APPROVAL_HARGA. Masalah: harga baru butuh keputusan pemilik. Bukti: tabel di atas, `listing.csv`, `qc.md`, hasil `scripts/harga.py`. Yang saya butuhkan: balas "setuju" untuk harga akhir Rp 120.000 (atau sebut harga/taktik lain). Setelah itu proses lanjut dari KONTEN_FOTO tanpa mengulang tahap yang sudah lulus.
