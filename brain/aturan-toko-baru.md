# Aturan mode toko baru

Dipakai saat toko (Shopee/TikTok Shop) belum punya riwayat penjualan. `status.json` berisi `"mode": "toko-baru"`.
Mode lama (`"mode": "deadstock"`) tetap ada untuk toko yang sudah punya export pesanan.

## Bahan dari pemilik (Drive `Koko Agency/input/`)
- `1-stok-gudang/stok-gudang` — satu lembar: `SKU | nama | stok | harga_jual_rencana | tanggal_masuk | catatan`
  (tanggal `YYYY-MM-DD`, harga angka polos). Ini pengganti export Shopee.
- `2-hpp/hpp`, `3-info-produk/info-produk`, `4-foto-master/<SKU>/` — sama seperti mode deadstock.
- `5-export-shopee/` — diisi nanti setelah toko jalan, untuk mengukur hasil (status DIUKUR).

## Memilih SKU
- `scripts/stok_gudang.py` menandai SKU `SIAP` atau `DATA_KURANG` (HPP/stok/harga/tanggal/fakta kosong, dobel,
  atau harga rencana di bawah harga minimum). Data kurang tidak ditebak, diserahkan ke pemilik.
- Urutan kerja: skor = 60·modal/modal_maks + 40·umur/umur_maks (ASUMSI: modal tertahan terbesar dulu). Pemilik
  boleh menentukan urutan lain (mis. model yang paling dicari menjelang Ramadan).

## Harga
- Barang belum pernah dijual di toko ini → **tidak ada harga coret**. Harga normal = harga yang dipasang.
- Taktik yang boleh: harga langsung, voucher toko, bundling, harga grosir, gratis ongkir program platform.
- Harga minimum tetap dari `aturan-harga.md` dan tetap menang atas harga kompetitor.
- Biaya admin toko baru Shopee & TikTok Shop: **ASUMSI 10%**, konfirmasi pemilik dari Seller Centre (bisa beda per platform:
  `cek_listing.py --admin-persen shopee=..,tiktok=..`).

## Fokus toko baru
- Toko belum punya ulasan: kejar penjualan dan ulasan pertama sebelum musim (12.12, Januari, lalu Ramadan; lihat `kalender.md`).
- Listing harus mudah ditemukan: judul dan kata kunci dari riset (`aturan-listing.md`), bukan dari tebakan.
- Dekorasi toko dan iklan dibuat agent sebagai usulan; **pemilik yang memasang dan membayar**.
