---
name: rencana-iklan-marketplace
description: "Menyusun rencana iklan Shopee Ads / TikTok Shop Ads untuk toko kecil: SKU mana, kata kunci, budget, batas bid, target ROAS, dan aturan berhenti — dihitung dari margin dengan scripts/iklan.py. Hanya usulan; pemilik yang memasang dan membayar. Dipakai marketer."
---

# Rencana iklan marketplace

Aturan proyek menang: `brain/aturan-iklan.md`, `brain/aturan-harga.md`, `brain/kalender.md`, `brain/pelajaran.md`.

## Prinsip
- Iklan hanya mempercepat produk yang sudah layak: listing & foto LULUS, harga tidak rugi, stok cukup.
- Uang iklan per pesanan tidak boleh melebihi jatah dari margin. Angka dari script, bukan perkiraan.
- Toko baru: mulai kecil di kata kunci spesifik (niat beli tinggi), ukur 7 hari, baru tambah.
- Musim koko (`kalender.md`): naikkan budget bertahap 2–3 minggu sebelum puncak, bukan di hari puncak.

## Langkah
1. Kumpulkan: `listing.csv` semua SKU yang LIVE/READY_UPLOAD, `brain/produk.csv`, `kata-kunci.csv`, budget harian dari pemilik
   (tidak ada budget = minta ke head, jangan menebak), CR nyata kalau sudah ada data (`hasil.md`), kalau belum pakai default.
2. `python3 scripts/iklan.py --listing batch/<id>/listing.csv [--listing ..] --produk brain/produk.csv --admin-persen <aturan>
   --budget-harian <dari pemilik> [--cr ..] --out batch/<toko-iklan>/iklan.csv`
3. Tulis `batch/<toko-iklan>/rencana-iklan.md`:
   - tabel per SKU & platform: budget harian, bid maks, ROAS target, ROAS impas, status (dari script),
   - 5–10 kata kunci per SKU dari `kata-kunci.csv` (spesifik dulu), kata kunci negatif yang jelas tidak cocok,
   - aturan berhenti/naik dari `aturan-iklan.md` dengan angka SKU itu (mis. "jeda setelah 100 klik tanpa pesanan"),
   - tanggal tinjau (7 hari), dan risiko (stok tipis, toko belum ada ulasan).
4. Tempel JSON output script. Status kerjamu "siap dicek" — qc menghitung ulang.

## Jangan
Mengusulkan budget di luar angka pemilik, mengiklankan SKU berstatus TIDAK_DIIKLANKAN, kata kunci merek toko lain,
klaim di materi iklan yang tidak ada di `fakta_boleh_diklaim`, atau login/memasang iklan sendiri.
