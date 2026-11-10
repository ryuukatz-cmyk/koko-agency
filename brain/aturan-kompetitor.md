# Aturan riset kompetitor

- **Tujuan:** harga pembanding untuk SKU deadstock, supaya marketer memilih taktik dan harga yang masuk akal. Bukan untuk meniru klaim kompetitor.
- **Produk mirip** = jenis sama (koko), lengan sama, ada bordir/motif serupa, warna sama atau mirip. Minimal **5** pembanding terverifikasi.
- **Sumber** (kolom `sumber`):
  - `cuplikan` — potongan hasil pencarian web. **Tidak dihitung**, hanya petunjuk ke halaman mana yang perlu dibuka.
  - `halaman` — halaman produk dibuka langsung (WebFetch). Tokopedia & Blibli diizinkan di environment.
  - `chrome` — dibaca lewat Claude in Chrome di komputer pemilik (Shopee, TikTok Shop, IG, Meta Ad Library).
- **Wajib per baris:** link, sumber, tanggal dicek (YYYY-MM-DD), harga lengkap ("Rp125.000", bukan "125rb").
- **Hitungan** hanya lewat `scripts/kompetitor.py` (termurah, tengah, termahal dari baris terverifikasi).
- **Batas sopan:** hanya halaman publik, baca saja, maksimal ±15 halaman per SKU. Tidak login ke akun kompetitor, tidak memalsukan identitas
  browser, tidak mengakali pemblokir bot. Halaman yang menolak → catat "tidak bisa dibuka", jangan diakali.
- **Shopee/Seller Centre:** boleh dibaca lewat Chrome pemilik; **tidak boleh mengubah apa pun** (harga, listing, iklan, chat).
- Harga minimum (`aturan-harga.md`) **selalu menang** atas harga kompetitor.
- Tidak menyimpan data pribadi pembeli/pengulas (nama, foto profil, isi ulasan dengan nama).
