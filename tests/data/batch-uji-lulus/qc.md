# QC batch batch-uji-lulus — QC_FINAL — 2026-11-10
SKU CONTOH-KOKO-01. Acuan: brain/product-lock/CONTOH-KOKO-01.md + tests/data/master-CONTOH-KOKO-01.png (navy, kerah shanghai, 5 kancing putih, kotak bordir emas dada kiri, lengan panjang, tanpa saku/logo).

| Item | Putusan | Bukti | Tindakan berikutnya |
|---|---|---|---|
| F01 | LULUS | dilihat: navy, kerah shanghai, 5 kancing putih, bordir emas dada kiri, lengan panjang; latar putih, diputar | - |
| F02 | LULUS | sama dengan master; latar krem | - |
| F03 | LULUS | sama dengan master; latar biru muda, diputar | - |
| F04 | LULUS | sama dengan master; latar krem | - |
| F05 | LULUS | sama dengan master; latar abu, diputar | - |
| F06 | LULUS | sama dengan master; latar hijau muda, diputar | - |
| F07 | LULUS | sama dengan master; latar pink muda | - |
| F08 | LULUS | sama dengan master; latar lila, diputar | - |
| F09 | LULUS | sama dengan master; latar krem muda, diputar | - |
| F10 | LULUS | sama dengan master; latar biru-hijau muda | - |
| Video (Product Lock) | LULUS | frame dtk 1/8/15/22 dilihat: produk sama dengan master; sampel 1 frame/dtk (26 frame) warna badan navy semua | - |
| Pasangan 1:1 | LULUS | Flow tidak dipakai (tidak ada prompt-flow.md / video/flow); foto F01–F10 lengkap, metadata.json gagal=[] kurang=[] | - |
| Harga | LULUS | `harga.py --harga-normal 150000 --hpp 90000 (produk.csv) --admin-persen 10 --diskon-persen 20` → harga_akhir 120000, minimum 100000, margin 18000, lulus=true. Sama dengan strategi.md (Rp 120.000) dan listing.csv (120000) | - |
| Copy | LULUS | judul/deskripsi/caption: lengan panjang, kerah shanghai, bordir dada kiri (fakta_boleh_diklaim) + navy (Product Lock). "Cek keranjang ya Kak!" ajakan, bukan klaim. Tidak ada klaim palsu | - |
| File final | LULUS | `video.py --cek`: 1080×1920, 25,5 dtk, tanpa audio, dekode_bersih=true, ok=true. Teks "Koko Navy Bordir" + "Rp 120.000" = harga hitung ulang | - |

Catatan: persetujuan pemilik di APPROVAL_HARGA tidak dicek (status.json riwayat kosong) — head pastikan sebelum APPROVAL_FINAL.

Putusan batch: LULUS
