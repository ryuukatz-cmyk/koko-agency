# Aturan Shopee (untuk agency ini)

- Sistem TIDAK login ke Shopee, TIDAK mengubah harga live, TIDAK mengeluarkan uang iklan.
  Hasil akhir = paket READY_UPLOAD yang diupload manusia lewat Seller Centre.
- Taktik yang boleh diusulkan: diskon produk, bundling (paket dengan produk laris), voucher toko, flash sale toko, harga grosir.
  Mode toko-baru: tanpa diskon produk/harga coret (lihat `aturan-toko-baru.md`).
- Judul listing: maksimal 100 karakter (ASUMSI, cek batas terbaru di Seller Centre). Tanpa kata "termurah", "terbaik", "original 100%" kecuali terbukti.
  Rumus judul, kata kunci, dan deskripsi: `aturan-listing.md`. Dicek `scripts/cek_listing.py`.
- Deskripsi: hanya fakta dari `brain/produk.csv` (kolom fakta_boleh_diklaim) dan Product Lock.
- Video produk: lihat `format-video.md`.
- Dilarang: klaim palsu (bahan, ukuran, "garansi", "best seller", "stok terakhir" bila tidak benar), harga coret palsu
  (harga normal harus harga yang memang berlaku sebelumnya).
