---
description: Buat dekorasi toko (banner carousel, voucher, etalase/kategori) untuk satu kampanye
argument-hint: "[kampanye, mis. 12.12 / Ramadan] [catatan]"
---
Kamu head. Buat batch tingkat toko `batch/<YYYY-MM-DD>-toko-dekorasi` (mode toko-baru, status DEKORASI) untuk: $ARGUMENTS
Aturan: `brain/aturan-dekorasi.md`, `brain/brand-visual.md` (wajib terisi; kalau kosong minta creative membuat 2–3 usulan dulu),
`brain/kalender.md`. Brief creative dengan skill dekorasi-toko: tulis `dekorasi.json` → `scripts/latar.py` → `scripts/dekorasi.py`.
Harga/voucher di banner hanya angka yang sudah disetujui pemilik. Cek bukti (`laporan.json`), kirim ke qc (cek h), lalu
APPROVAL_DEKORASI: tunjukkan gambarnya ke pemilik. Pemilik yang memasang di Seller Centre.
