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

Full build tanpa data asli (2026-11-17, branch `toko-baru`):
- Dekorasi: `scripts/latar.py` + `scripts/dekorasi.py` (produk asli, teks lewat kode, cek ukuran/KB/kontras), skill `dekorasi-toko`,
  `brain/aturan-dekorasi.md` (ukuran ASUMSI), batch tingkat toko DEKORASI → QC_DEKORASI → APPROVAL_DEKORASI → DIPASANG, qc cek h.
- Iklan: `scripts/iklan.py` (ROAS impas/target, bid maks, budget per SKU), skill `rencana-iklan-marketplace`, `brain/aturan-iklan.md`, qc cek i.
- Ukur toko baru: `scripts/ukur.py`. Paket upload: `scripts/paket_upload.py` (foto urut, video, listing per platform, checklist, zip).
- Data contoh `contoh/` (4 SKU palsu) + `scripts/demo.py` + tes integrasi alur lengkap.
- Tooling: `.claude/settings.json` (izin, hook status & penjaga), `.claude/commands/` (9 perintah), `scripts/setup.sh`, `requirements.txt`,
  font Poppins (OFL) di `aset/font/`.

Riset lebih kuat (2026-11-17): skill market-research (ECC ±229 rb bintang), competitive-brief (resmi Anthropic),
customer-research & social (coreyhaines31 ±59 rb), skill buatan sendiri riset-konten-marketplace, alur `/konten`
(KONTEN_RISET → KONTEN_RENCANA → QC_KONTEN → APPROVAL_KONTEN → DIJADWALKAN), `scripts/cek_konten.py`, tool Karyawan AI opsional.

Menunggu data/aksi pemilik:
- Data asli di Drive, isi `brain/brand-visual.md`, konfirmasi biaya admin & batas platform (masih ASUMSI).
- Uji FLUX nyata (`/cek-cloudflare`), lalu `/demo --flux`.
- File upload massal Shopee: menunggu template Excel kategori koko dari Seller Centre milik pemilik.
- Landing page + admin (IG/FB ads → WA) — desain menunggu bahan; skill `ui-ux-pro-max` sudah tersedia.

NANTI (belum dibangun):
- **landing page + halaman admin** (IG/FB ads → pilih produk → rekap → WA admin). Desain menunggu bahan.
- ~~produksi dekorasi toko~~ — sudah dibangun 2026-11-17 (`scripts/dekorasi.py`).
- **jadwal otomatis** (cek Drive tiap minggu, berhenti di titik persetujuan).

Fase 2 (NANTI, jangan dibangun sebelum Fase 1 terbukti di batch nyata):
- **ops** — cek stok harian, pengingat restock/stop restock SKU lambat.
- **cs** — draft balasan chat pembeli (manusia yang mengirim).
- **ads** — usulan iklan Shopee; tidak boleh mengeluarkan uang tanpa persetujuan manusia.
