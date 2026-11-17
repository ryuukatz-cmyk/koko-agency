# Referensi prompt foto & video

Dipakai creative saat menulis `prompt-foto.md` dan `prompt-flow.md`. Hanya poin yang disetujui head (lihat `aturan-belajar.md`).
Format: `- <pola prompt> — kenapa berhasil — contoh hasil/QC (disetujui head YYYY-MM-DD, sumber: ...)`

## Yang terbukti dari uji kita
- Sebut detail produk satu per satu (warna + hex, jumlah kancing, posisi & warna bordir, jenis kerah) dan tutup dengan
  "Do not change the product." — FLUX tetap mengubah detail kecil (kancing 5→4, menambah label leher), jadi qc wajib menghitung.
  (dari uji sistem 2026-11-10, sumber: tests/hasil-uji.md uji nyata FLUX — belum lewat review head)

- Mode komposit untuk foto utama katalog: model hanya membuat latar ("empty ... table/wall, no people, no clothing, no text"),
  produk asli ditempel `scripts/komposit.py`. Kancing/bordir tidak mungkin berubah. Syarat master berlatar polos.
  (dari uji sistem 2026-11-17, tes `test_komposit_produk_asli_tidak_berubah` — belum lewat review head)
- Mode scene: kirim foto detail bordir sebagai referensi kedua (`--master depan.jpg detail-bordir.jpg`) dan sebut
  "image 0"/"image 1" di prompt. (fitur baru 2026-11-17, belum diuji nyata — belum lewat review head)

## Dari riset luar
(belum ada — isi lewat fase belajar)
