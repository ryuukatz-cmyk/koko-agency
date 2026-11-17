# ROADMAP

Fase 1 (sekarang): head, researcher, marketer, creative, qc — toko baru Shopee + TikTok Shop (mode `toko-baru`); mode `deadstock` tetap ada.

## Rencana menuju Ramadan 2027 (usulan 2026-11-10, pemilik: "sipp" — konfirmasi lagi saat lanjut)
Tujuan: koko ludes terjual di toko baru (Shopee + TikTok Shop). 1 Ramadan ±8 Feb 2027, Lebaran ±9–10 Mar 2027 (perkiraan, tunggu isbat).
Toko baru belum punya ulasan → kejar penjualan & ulasan pertama sebelum Ramadan (12.12, lalu Januari).

| Kapan | Proyek | Hasil |
|---|---|---|
| Sekarang – akhir Nov | 1. Listing siap jual Shopee + TikTok Shop: lembar stok gudang (umur stok dari tanggal masuk), riset kata kunci & kompetitor, judul/deskripsi/kata kunci, 10 foto + video per SKU, desain toko dasar | Paket upload per SKU, siap 12.12 |
| Desember | 2. Landing page + admin + rekap ke WA | Tujuan iklan IG/FB |
| Des – Jan | 3. Rencana iklan (Shopee Ads, TikTok, Meta): agent menyiapkan, owner memasang & membayar | Iklan jalan sebelum puasa |
| Jan – Mar | 4. Kampanye Ramadan: ukur mingguan → ubah harga/promo/konten | Stok habis sebelum Lebaran |

Keputusan tertunda (proyek 1):
- Deadstock belum pernah dijual online → `input/1-stok-gudang` (SKU, nama, stok, harga_jual_rencana, tanggal_masuk, catatan); export Shopee jadi `5-export-shopee` untuk mengukur toko baru. Aturan 60 hari & stok ≥5 = ASUMSI, dikoreksi owner.
- Barang belum pernah dijual → jangan pakai harga coret; pakai harga langsung, voucher toko, bundling, grosir.
- Konfirmasi owner: biaya admin toko baru (Shopee & TikTok Shop).

Sudah ada (2026-11-10): riset kompetitor, fase belajar (`brain/aturan-belajar.md`), skill per agent.

Tahap 1 toko baru (2026-11-17, branch `toko-baru-tahap-1`):
- head = sesi utama (CLAUDE.md), mode `toko-baru` (`scripts/stok_gudang.py`, `brain/aturan-toko-baru.md`), tanpa harga coret.
- Listing per platform (Shopee + TikTok) dengan kata kunci riset: skill `riset-kata-kunci-marketplace`, `listing-seo-marketplace`,
  `brain/aturan-listing.md`, `brain/aturan-tiktokshop.md` (ASUMSI), `scripts/cek_listing.py`.
- Foto: banyak master sebagai referensi FLUX, urutan provider bisa diatur, mode komposit (produk asli + latar AI, `scripts/komposit.py`),
  `scripts/cek_cloudflare.py` untuk uji nyata di environment koko.
- `brain/brand-visual.md` (templat, diisi pemilik), `brain/kalender.md`.
- Keputusan tertunda di atas: input `1-stok-gudang` dan "tanpa harga coret" sudah dipakai. Masih ASUMSI: biaya admin toko baru (10%),
  batas judul Shopee 100 / TikTok 255, urutan skor 60/40.

Berikutnya:
- Tahap 2: file upload massal Shopee (menunggu template Excel kategori koko dari Seller Centre milik pemilik).
- Tahap 3: produksi dekorasi toko — `scripts/dekorasi.py` (latar AI + produk asli + teks lewat kode, ukuran persis),
  skill `dekorasi-toko` untuk creative, status DEKORASI → QC_DEKORASI → APPROVAL_DEKORASI, cek qc baru, `brain/aturan-dekorasi.md`
  (ukuran banner/etalase dicek researcher di Seller Centre).
- Tahap 4: rencana iklan (marketer menyusun kata kunci & budget Shopee Ads; pemilik memasang & membayar) + ukur mingguan.

NANTI (belum dibangun):
- **landing page + halaman admin** (IG/FB ads → pilih produk → rekap → WA admin). Desain menunggu bahan.
- **produksi dekorasi toko** (banner/etalase dibuat creative, dipasang pemilik).
- **jadwal otomatis** (cek Drive tiap minggu, berhenti di titik persetujuan).

Fase 2 (NANTI, jangan dibangun sebelum Fase 1 terbukti di batch nyata):
- **ops** — cek stok harian, pengingat restock/stop restock SKU lambat.
- **cs** — draft balasan chat pembeli (manusia yang mengirim).
- **ads** — usulan iklan Shopee; tidak boleh mengeluarkan uang tanpa persetujuan manusia.
