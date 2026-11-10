# QC batch batch-uji-cacat — QC_FINAL — 2026-11-10
SKU CONTOH-KOKO-01. Acuan: brain/product-lock/CONTOH-KOKO-01.md + tests/data/master-CONTOH-KOKO-01.png (navy, kerah shanghai, 5 kancing putih, kotak bordir emas dada kiri, lengan panjang).

| Item | Putusan | Bukti | Tindakan berikutnya |
|---|---|---|---|
| F01 | LULUS | navy, kerah shanghai, 5 kancing putih, bordir emas dada kiri, lengan panjang | - |
| F02 | LULUS | sama dengan master | - |
| F03 | LULUS | sama dengan master | - |
| F04 | TOLAK | badan + kerah merah marun, master navy (kancing & bordir sama) | creative buat ulang F04 |
| F05 | LULUS | sama dengan master | - |
| F06 | LULUS | sama dengan master | - |
| F07 | LULUS | sama dengan master | - |
| F08 | LULUS | sama dengan master | - |
| F09 | LULUS | sama dengan master | - |
| F10 | LULUS | sama dengan master | - |
| V01 | LULUS | frame dtk 2: produk sama dengan master | - |
| V02 | LULUS | frame dtk 2: sama dengan master | - |
| V03 | LULUS | frame dtk 2: sama dengan master | - |
| V04 | TOLAK | frame dtk 2: badan merah marun (turunan F04), master navy | buat ulang setelah F04 diganti |
| V05 | TOLAK | frame dtk 2: produk lain — badan hijau, 3 kancing, TANPA bordir emas; prompt P05 "product unchanged" tidak dipatuhi | buang V05, buat ulang klip dari F05 |
| V06 | LULUS | frame dtk 2: sama dengan master | - |
| V07 | LULUS | frame dtk 2: sama dengan master | - |
| V08 | LULUS | frame dtk 2: sama dengan master | - |
| V09 | LULUS | frame dtk 2: sama dengan master | - |
| Pasangan F10/P10/V10 | REVISI | F10 dan P10 ada, video/flow/V10.mp4 tidak ada (hanya V01–V09) | creative buat V10 atau keluarkan F10+P10 |
| Harga | TOLAK | `harga.py --harga-normal 150000 --hpp 90000 (produk.csv) --admin-persen 10 --diskon-persen 35` → harga_akhir 97500 < minimum 100000, margin −2250, lulus=false. Angka sama dengan strategi.md, tapi di bawah minimum | marketer ganti taktik (diskon maks 33%: 150000×0,67=100500 ≥ 100000, cek ulang dengan script), lalu APPROVAL_HARGA |
| Copy | TOLAK | klaim tidak ada di produk.csv/Product Lock: "Premium", "Best Seller", "Anti Luntur" (judul); "bahan katun premium", "best seller", "anti luntur", "garansi uang kembali" (deskripsi); "Best seller!", "Bahan premium adem seharian" (caption). Bahan di produk.csv masih ASUMSI | marketer tulis ulang hanya dengan: lengan panjang, kerah shanghai, bordir dada kiri, navy |
| File final | TOLAK | `video.py --cek` teknis ok (1080×1920, 30,0 dtk, tanpa audio, dekode bersih), TETAPI sampel 1 frame/dtk: dtk 11–13 badan marun (V04), dtk 14–17 produk hijau tanpa bordir (V05); teks harga "Rp 97.500" di bawah minimum | render ulang setelah F04/V04/V05/V10 dan harga diperbaiki |

Putusan batch: TOLAK
