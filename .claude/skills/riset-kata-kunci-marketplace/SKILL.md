---
name: riset-kata-kunci-marketplace
description: "Riset kata kunci yang benar-benar diketik pembeli di Shopee dan TikTok Shop untuk satu produk (koko). Mengumpulkan saran pencarian marketplace, pola judul kompetitor, dan (opsional) ide kata kunci Google, lalu menulis batch/<id>/kata-kunci.csv dengan bukti dan tanggal. Dipakai researcher sebelum marketer menulis judul."
---

# Riset kata kunci marketplace

Tujuan: daftar kata kunci yang **terbukti** dipakai pembeli, supaya judul listing mudah ditemukan.
Aturan proyek (`CLAUDE.md`, `brain/`) selalu menang atas skill ini.

## Bahan
- `brain/produk.csv` dan `brain/product-lock/<sku>.md`: jenis, lengan, kerah, bordir, warna, bahan.
- `batch/<id>/kompetitor.csv` kalau sudah ada (judul kompetitor terverifikasi).

## Langkah
1. **Kata dasar** (3–5): gabungan jenis + ciri utama dari fakta produk.
   Contoh: `baju koko`, `koko pria lengan panjang`, `koko bordir`, `kemeja koko`, `koko kurta`. Hanya ciri yang benar.
2. **Saran pencarian Shopee** (butuh Claude in Chrome di komputer pemilik): buka shopee.co.id, ketik tiap kata dasar
   di kotak cari **tanpa menekan enter**, catat saran yang muncul persis seperti tertulis. Baca saja.
   Sumber = `saran-pencarian`, platform = `shopee`, bukti = kata dasar yang diketik.
3. **Saran pencarian TikTok** (Chrome): sama, di kotak cari TikTok / TikTok Shop. Platform = `tiktok`.
4. **Pola judul kompetitor**: dari 5–10 judul produk mirip yang terlaris (halaman yang sudah dibuka untuk riset kompetitor),
   catat frasa 2–4 kata yang muncul di ≥ 3 judul. Sumber = `judul-kompetitor`, bukti = link salah satu judul.
   Yang dicatat frasa umumnya, bukan menyalin judul utuh.
5. **(Opsional) ide kata kunci Google**: hanya kalau alat ide kata kunci tersedia di sesi. Sumber = `google-ads`.
   Volume Google ≠ volume Shopee: dipakai sebagai pendukung, bukan penentu.
6. Tidak bisa membuka marketplace (cloud tanpa Chrome)? Jangan menebak. Tulis kata dasar dengan sumber `dugaan`
   dan laporkan ke head bahwa riset Chrome dibutuhkan. Marketer tidak memakai baris `dugaan` sebagai kata kunci utama.

## Output `batch/<id>/kata-kunci.csv`
Kolom persis: `kata_kunci,platform,sumber,bukti,dicek_pada,catatan`
- `kata_kunci` huruf kecil, apa adanya seperti diketik pembeli.
- `sumber`: `saran-pencarian` | `judul-kompetitor` | `google-ads` | `dugaan`.
- `dicek_pada`: YYYY-MM-DD.
- `catatan`: mis. "tidak cocok: untuk anak" — kata kunci yang tidak sesuai produk tetap dicatat tapi ditandai.

Lalu tulis 3–5 baris ringkas di laporan ke head: **kata kunci utama yang diusulkan** per platform (yang muncul di
saran pencarian DAN pola judul kompetitor lebih kuat), plus kata kunci yang sengaja dibuang dan alasannya.

## Batas
- Hanya halaman publik, baca saja, maksimal ±15 halaman per SKU. Tidak login ke akun lain, tidak mengakali pemblokir bot.
- Tidak menyimpan data pribadi (nama/username pembeli, isi ulasan dengan nama).
- Kata kunci basi setelah ±1 bulan dan wajib dicek ulang menjelang Ramadan (`brain/kalender.md`).
