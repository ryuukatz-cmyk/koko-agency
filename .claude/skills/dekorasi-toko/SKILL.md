---
name: dekorasi-toko
description: "Merancang dekorasi toko marketplace (banner carousel, voucher, kampanye, gambar kategori) untuk toko koko: menulis dekorasi.json dari brand visual dan pesan kampanye, lalu merender lewat scripts/latar.py dan scripts/dekorasi.py. Dipakai creative."
---

# Dekorasi toko

Aturan proyek menang: `brain/aturan-dekorasi.md`, `brain/brand-visual.md`, `brain/kalender.md`, `brain/referensi-dekorasi.md`.
Gambar dibuat oleh script, bukan dengan menggambar teks lewat model AI.

## Prinsip desain banner marketplace
- **Dilihat di HP, sekilas.** Satu banner = satu pesan. Judul 2–6 kata, subjudul ≤ 8 kata, satu ajakan (CTA).
- **Hierarki:** label kecil (konteks: "Koleksi Ramadan") → judul besar (pesan) → subjudul (detail) → harga/CTA.
- **Produk asli yang jadi bintang.** Foto master dipotong dan ditempel (komposit); 1–3 produk per banner. Lebih banyak = kecil dan ramai.
- **Konsisten.** Semua banner satu palet & font dari `brand-visual.md`. Satu warna aksen untuk harga/CTA saja.
- **Kontras cukup.** Latar terang → teks gelap (`"teks": "#1F2A44"`) atau biarkan script menambah panel. Latar gelap → teks putih.
- **Latar tenang.** Prompt latar: ruang kosong, tekstur lembut, sesuai gaya foto toko; selalu akhiri dengan
  "no people, no clothing, no text, no logo". Sisi tempat teks dibuat lebih polos.
- **Pola, bukan salinan.** Boleh meniru pola umum (harga besar di kanan bawah, produk di kanan), tidak meniru desain toko tertentu.

## Langkah
1. Baca brief head: kampanye, SKU yang ditampilkan, angka yang sudah disetujui (harga/voucher), jumlah banner.
   Kalau `brain/brand-visual.md` kosong: buat 2–3 usulan palet + gaya di `belajar/<tanggal>-usulan-brand.md` dan berhenti.
2. Tulis `batch/<id>/dekorasi.json`:
   - `palet` dari brand-visual (utama, kedua, aksen, teks).
   - Item per banner: `id` D01.., `jenis` (lihat aturan), `tata_letak` (teks-kiri / teks-kanan / tengah untuk persegi),
     `produk` (path foto master depan), `label`, `judul`, `subjudul`, `harga` (hanya angka disetujui, format "Rp 149.000"), `cta`,
     `latar` = `batch/<id>/latar/Dxx.png`, `latar_prompt`.
   - Variasikan tata letak antar slide carousel supaya tidak monoton.
3. `python3 scripts/latar.py --spec batch/<id>/dekorasi.json` (exit 2 = WAITING_LATAR → lapor head, jangan mengarang).
4. `python3 scripts/dekorasi.py --spec batch/<id>/dekorasi.json --out batch/<id>/hasil`.
   Exit 2 = spec salah (perbaiki); exit 1 = cek gagal (lihat `laporan.json`).
5. Buka setiap hasil dengan Read. Kalau produk terlalu kecil/teks terasa sesak, ubah spec (bukan gambar) dan render ulang.
6. Lapor ke head: daftar file, isi `laporan.json` (ukuran, KB, kontras, teks tertulis), dan alasan pilihan desain singkat.
   Jangan menilai "lulus" — itu tugas qc.

## Jangan
Teks di dalam latar AI, produk buatan AI di banner, angka yang belum disetujui, harga coret di mode toko-baru,
logo/nama toko lain, foto orang tanpa izin, warna di luar palet.
