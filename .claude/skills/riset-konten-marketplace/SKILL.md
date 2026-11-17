---
name: riset-konten-marketplace
description: "Riset konten untuk toko koko di TikTok, Instagram Reels, dan Shopee Video: konten organik dan iklan kompetitor yang sedang jalan, pola hook/format/durasi/sudut jual, bahasa pembeli dari ulasan, dan momen musiman. Menulis riset-konten.csv + riset-konten.md dengan bukti dan tanggal. Dipakai researcher sebelum marketer menyusun kalender konten."
---

# Riset konten marketplace

Aturan proyek menang: `CLAUDE.md`, `brain/aturan-konten.md`, `brain/aturan-belajar.md`, `brain/aturan-kompetitor.md`.
Skill pendukung yang boleh dipakai bersama: `social` (hook & format video pendek), `customer-research` (bahasa pembeli dari ulasan),
`competitive-brief` dan `market-research` (posisi & celah). Untuk koko, terapkan ke toko marketplace, bukan SaaS.

## Pertanyaan yang dijawab (pilih yang ada di brief head)
1. Konten seperti apa yang sedang ramai untuk "baju koko" (format, hook 3 detik pertama, durasi, gaya, CTA)?
2. Iklan apa yang sedang dijalankan toko/brand koko (Meta & TikTok Ads Library)? Berapa lama sudah tayang (iklan lama = kemungkinan untung)?
3. Apa kata pembeli di ulasan produk koko laris: yang dipuji, yang dikeluhkan, kata yang mereka pakai?
4. Celah: sudut jual yang belum dipakai kompetitor dan benar untuk produk kita (`fakta_boleh_diklaim`).

## Sumber dan alat (pakai yang tersedia, catat yang tidak bisa dibuka)
| Sumber | Alat | Catatan |
|---|---|---|
| TikTok / IG Reels / Shopee Video organik | Claude in Chrome (komputer pemilik) | baca saja; catat link, tanggal, angka yang terlihat (views/likes) |
| TikTok Ads Library | `mcp__Karyawan_AI__karyawan_tiktok_search` → `karyawan_tiktok_ad_detail` | hanya kalau tool tersedia di sesi; cari nama toko/brand, bukan kata umum |
| Meta Ad Library (FB/IG) | `mcp__Karyawan_AI__karyawan_meta_search` → `karyawan_meta_library` (country `ID`) | iklan aktif + tanggal mulai |
| Ide kata kunci Google | `mcp__Karyawan_AI__karyawan_googlead_keyword_idea` | pendukung, bukan penentu |
| Ulasan produk Shopee/TikTok | Chrome | ambil POLA keluhan/pujian; tidak menyimpan nama/foto pengulas |
| Artikel/tren umum | WebSearch / WebFetch | sebut tanggal artikel |
Tool berbayar/kuota (mis. Karyawan AI): pakai seperlunya, maksimal ±20 panggilan per riset, dan sebutkan jumlahnya di laporan.

## Yang dicatat per konten/iklan
`platform, akun, link, tanggal_dicek, tanggal_tayang (kalau terlihat), format (talking head / slideshow / POV / try-on / detail close-up / unboxing),
durasi_detik, hook (parafrase singkat, bukan salinan naskah), sudut_jual (harga / bahan / momen Lebaran / kerapian / ukuran),
cta, angka_terlihat (views/likes/terjual), sumber (chrome / ads-library / websearch)`.
Hanya angka yang benar-benar terlihat. Kosong = kosong, bukan perkiraan.

## Output
1. `batch/<id>/riset-konten.csv` — kolom persis seperti di atas.
2. `batch/<id>/riset-konten.md`:
   - **Fakta yang terlihat** (dengan link + tanggal), **Dugaan** (dipisah dan diberi alasan),
   - 3–5 pola yang berulang (mis. "close-up bordir + harga di 3 detik pertama muncul di 6 dari 10 video teratas"),
   - bahasa pembeli dari ulasan (kata/frasa umum, tanpa nama), keluhan yang bisa kita jawab dengan fakta produk kita,
   - celah sudut jual yang benar untuk produk kita, dan halaman/alat yang gagal dibuka.
3. Usulan poin untuk `brain/referensi-konten.md` lewat draf `belajar/` (head yang memutuskan).

## Batas
- Pola boleh ditiru, isinya tidak: jangan menyalin naskah, video, foto, musik, atau caption orang lain.
- Tidak login ke akun orang lain, tidak klik beli/follow/komentar, tidak mengakali pemblokir bot.
- Tidak menyimpan data pribadi (nama/username pengulas atau penonton, foto wajah).
- Riset konten basi setelah ±1 bulan; wajib diulang menjelang Ramadan (`brain/kalender.md`).
