# Aturan listing (judul, deskripsi, kata kunci)

Dipakai marketer (menulis) dan qc (menilai). Dicek otomatis oleh `scripts/cek_listing.py`.

## listing.csv
Satu baris per SKU **per platform**. Kolom:
`sku,platform,judul,deskripsi,harga_normal,harga_coret,harga_akhir,taktik,kata_kunci,caption_video`
- `platform`: `shopee` atau `tiktok`.
- `harga_coret`: kosong kalau tidak ada. Mode toko baru: wajib kosong.
- `kata_kunci`: dipisah `;`, urut dari yang paling penting. Kata kunci pertama = kata kunci utama, wajib ada di judul.

## Judul
- Batas panjang (ASUMSI, cek Seller Centre): Shopee 25–100 karakter, TikTok Shop 25–255 karakter.
- Rumus: **kata kunci utama + jenis/potongan + detail pembeda + bahan + warna/ukuran**.
  Contoh pola: `Baju Koko Pria Lengan Panjang Bordir Dada Kiri Katun Navy M L XL`.
- Kata kunci utama di depan. Tidak huruf kapital semua. Tidak mengulang kata yang sama berkali-kali.
- Hanya fakta dari `produk.csv` (fakta_boleh_diklaim) dan Product Lock.

## Kata kunci
- Sumbernya `batch/<id>/kata-kunci.csv` dari researcher (bukti + tanggal). Kata kunci tanpa bukti tidak dipakai.
- Pilih yang cocok dengan produk. Kata kunci yang tidak sesuai produk (mis. "koko anak" untuk koko dewasa) dilarang.

## Deskripsi
Urutan: 1 kalimat pembuka (manfaat nyata) → detail produk (dari fakta) → ukuran (kalau ada data) → cara perawatan
(hanya kalau ada di data) → ajakan singkat. Kalimat pendek, sapaan "Kak" (`brand-voice.md`).
Klaim yang dilarang ada di `cek_listing.py` (KLAIM_TERLARANG) dan `aturan-shopee.md`.

## Caption video
Maksimal 2 kalimat + 3–5 tagar dari kata kunci. Tidak ada harga selain harga akhir yang sudah disetujui.
