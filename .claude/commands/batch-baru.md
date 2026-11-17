---
description: Mulai batch toko baru (1 SKU) dari bahan di Drive — head memimpin sampai titik persetujuan harga
argument-hint: "[SKU opsional]"
---
Kamu head (baca `.claude/agents/head.md`). Mulai batch mode `toko-baru` dari bahan di Drive `Koko Agency/input/`.
SKU yang diminta pemilik: $ARGUMENTS (kosong = pilih SKU SIAP dengan skor tertinggi dari `scripts/stok_gudang.py`).

Urutan: unduh bahan ke `data/mentah/` → researcher menjalankan `stok_gudang.py` → pilih SKU → buat `batch/<YYYY-MM-DD>-<SKU>/status.json`
(status NEW, mode toko-baru) → Product Lock dari foto master (TIDAK JELAS kalau tidak terlihat) → researcher: kompetitor + kata kunci
→ marketer: strategi + listing.csv (Shopee & TikTok) → cek bukti sendiri (`harga.py`, `cek_listing.py`) → qc → APPROVAL_HARGA.
Berhenti di APPROVAL_HARGA dan kirim tabel persetujuan ke pemilik. Kalau bahan kurang, pakai kalimat "Oper ke manusia".
