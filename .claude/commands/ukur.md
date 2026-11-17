---
description: Ukur hasil mingguan toko (export pesanan baru) dan usulkan perubahan harga/promo/konten
argument-hint: "[tanggal tayang YYYY-MM-DD opsional]"
---
Kamu head. Ambil export pesanan terbaru dari Drive `input/5-export-shopee/` ke `data/mentah/`, lalu brief researcher:
`python3 scripts/ukur.py --pesanan .. --katalog data/katalog.csv --listing batch/*/listing.csv --admin-persen .. --sejak $ARGUMENTS --hari-ini <hari ini> --out ..`
Hasil per SKU (unit terjual, sisa stok, uang masuk, per minggu) + usulan satu baris untuk `brain/pelajaran.md`.
Usulan perubahan harga tetap lewat APPROVAL_HARGA. Data pembeli tidak pernah ditulis.
