# Aturan harga

- Biaya admin Shopee: **10%** dari harga akhir yang dibayar pembeli. (ASUMSI — cek di Seller Centre: admin + layanan + program yang diikuti)
- Harga akhir = harga normal × (1 − diskon%) − voucher toko. Voucher toko ditanggung penjual. (ASUMSI)
- **Harga minimum** = HPP ÷ (1 − admin%), dibulatkan ke atas. Artinya setelah dipotong admin, uang yang diterima ≥ HPP.
- Harga akhir **tidak boleh** di bawah harga minimum. Tidak ada pengecualian tanpa keputusan tertulis pemilik.
- Margin = (harga akhir − biaya admin) − HPP.
- Bundling: HPP = jumlah HPP semua barang di paket. Grosir: cek per tingkat harga, per unit.
- Semua harga dihitung dengan `scripts/harga.py --admin-persen 10 ...`, bukan dihitung di kepala.
- Harga baru dipakai di konten (teks video, listing) **setelah** pemilik menyetujui di APPROVAL_HARGA.
