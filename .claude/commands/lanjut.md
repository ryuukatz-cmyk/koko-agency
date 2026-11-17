---
description: Lanjutkan batch dari status terakhirnya (setelah pemilik menyetujui / menaruh file)
argument-hint: "[id batch opsional] [catatan pemilik]"
---
Kamu head (baca `.claude/agents/head.md`). Batch dan catatan pemilik: $ARGUMENTS
Kalau id batch kosong, pilih batch yang menunggu pemilik dari `python3 scripts/status.py --json`.
Baca `status.json` + bukti di folder batch, catat persetujuan pemilik (kutip kalimatnya) di riwayat, lalu lanjutkan alur
sampai titik manusia berikutnya. Jangan mengulang tahap yang sudah LULUS.
