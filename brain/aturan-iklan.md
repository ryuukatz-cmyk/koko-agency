# Aturan iklan

Agent **mengusulkan**; pemilik yang memasang, mengatur, dan membayar iklan di dashboard Shopee Ads / TikTok Shop Ads.
Sistem tidak pernah login dan tidak pernah mengeluarkan uang. Batch tingkat toko: `batch/<YYYY-MM-DD>-toko-iklan`.

## Kapan boleh iklan
- SKU sudah LIVE (atau READY_UPLOAD dan pemilik akan upload hari itu), foto & listing LULUS qc.
- Margin > 0 setelah admin (dihitung `scripts/iklan.py`). Margin ≤ 0 = TIDAK_DIIKLANKAN.
- Toko baru tanpa ulasan: mulai kecil, kumpulkan data 7 hari, baru naikkan.

## Angka (selalu dari `scripts/iklan.py`, tidak dihitung di kepala)
- ROAS impas = harga akhir ÷ margin. ROAS target = harga akhir ÷ (margin × porsi). Porsi default 50% margin (ASUMSI).
- Bid maks per klik = jatah iklan per pesanan × CR. CR default 2% (ASUMSI toko baru; ganti dengan angka nyata setelah 2 minggu).
- Budget harian total dari **pemilik**, dibagi ke SKU sebanding margin. Agent tidak menebak budget.

## Kata kunci
- Dari `batch/<id>/kata-kunci.csv` (sumber bukan `dugaan`). Mulai 5–10 kata kunci spesifik per SKU ("koko bordir lengan panjang")
  sebelum kata umum ("baju koko").
- Kata kunci merek toko lain tidak dipakai.

## Aturan berhenti (ditulis di rencana, dijalankan pemilik)
- Setelah `batas_klik_tanpa_pesanan` klik tanpa pesanan → jeda kata kunci/SKU itu.
- ROAS 7 hari < ROAS impas → turunkan bid atau jeda.
- ROAS 7 hari ≥ ROAS target → boleh naikkan budget SKU itu ±20%.
- Semua perubahan dicatat di `hasil.md` minggu itu; pelajaran yang terbukti masuk `pelajaran.md`.
