---
name: listing-seo-marketplace
description: "Menulis judul, deskripsi, dan caption listing Shopee dan TikTok Shop yang mudah ditemukan pencarian, dari kata kunci yang sudah diriset dan fakta produk saja. Dipakai marketer; hasilnya dicek dengan scripts/cek_listing.py."
---

# Listing SEO marketplace

Aturan proyek menang: `brain/aturan-listing.md`, `brain/aturan-shopee.md`, `brain/aturan-tiktokshop.md`,
`brain/brand-voice.md`. Skill ini hanya cara kerja.

## Prinsip
- Pembeli marketplace mencari dengan kata pendek ("koko pria", "baju koko bordir"). Judul yang memuat kata itu di depan
  lebih mudah muncul. Judul bukan tempat slogan.
- Setiap kata di judul harus benar untuk produk ini. Kata kunci yang populer tapi tidak sesuai produk = klaim palsu.
- Satu SKU, dua platform, dua baris: Shopee lebih pendek, TikTok boleh lebih panjang dan lebih bercerita.

## Langkah
1. Baca `batch/<id>/kata-kunci.csv`. Pilih **1 kata kunci utama** per platform (prioritas: `saran-pencarian` yang juga
   muncul di `judul-kompetitor`), lalu 3–6 kata kunci pendukung. Abaikan baris `dugaan` untuk kata kunci utama dan baris
   yang ditandai tidak cocok.
2. **Judul** = kata kunci utama + jenis/potongan + detail pembeda + bahan + warna/ukuran.
   - Shopee: padat, ≤ 100 karakter (ASUMSI). TikTok: boleh sampai batas di `cek_listing.py`, tetap mudah dibaca.
   - Kata pendukung masuk kalau masih muat dan benar. Jangan mengulang kata.
3. **Deskripsi** (urutan dari `aturan-listing.md`): pembuka manfaat nyata → detail dari fakta → ukuran → perawatan
   (hanya kalau ada data) → ajakan. Sisipkan kata kunci pendukung secara wajar, bukan ditumpuk.
4. **Caption video**: ≤ 2 kalimat + 3–5 tagar dari kata kunci.
5. Isi `kata_kunci` di listing.csv dengan kata kunci utama di posisi pertama, dipisah `;`.
6. Jalankan `python3 scripts/cek_listing.py --listing batch/<id>/listing.csv --produk brain/produk.csv
   --admin-persen <dari aturan> --mode <mode dari status.json>`. Perbaiki sampai exit 0, tempel JSON-nya di `strategi.md`.

## Contoh pola (bukan untuk disalin mentah)
- Shopee: `Baju Koko Pria Lengan Panjang Bordir Dada Kiri Katun Navy M L XL`
- TikTok: `Baju Koko Pria Lengan Panjang Bordir Dada Kiri Bahan Katun Warna Navy Cocok Jumatan Lebaran M L XL`
  ("cocok Jumatan/Lebaran" boleh karena itu kegunaan, bukan klaim kualitas.)

## Jangan
Klaim di luar `fakta_boleh_diklaim`, harga coret di mode toko baru, kata "termurah/terbaik/terlaris",
huruf kapital semua, emoji di judul, nama merek toko lain.
