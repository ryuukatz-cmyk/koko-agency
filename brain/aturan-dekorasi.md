# Aturan dekorasi toko

Dekorasi = banner carousel, banner voucher/kampanye, gambar kategori/etalase di halaman toko Shopee dan TikTok Shop.
Agent membuat; **pemilik yang memasang** di Seller Centre. Satu batch tingkat toko: `batch/<YYYY-MM-DD>-toko-dekorasi`.

## Ukuran (ASUMSI — researcher cek di Seller Centre > Dekorasi Toko, lalu perbarui di sini dan `scripts/dekorasi.py`)
| jenis | ukuran | dipakai untuk |
|---|---|---|
| banner-carousel | 1200×600 | slide atas halaman toko (maks ±6 slide) |
| banner-tinggi | 1200×900 | banner tunggal yang lebih tinggi |
| gambar-tunggal | 1200×1200 | blok gambar persegi |
| kategori | 800×800 | ikon/etalase kategori |
| banner-kampanye | 1200×628 | banner promo kampanye (12.12, Ramadan) |
Batas file 2 MB, sisi maks 2000 px (dicek otomatis). Ukuran lain: `"ukuran": "LxT"` di spec.

## Cara membuat (wajib lewat script)
1. Creative menulis `dekorasi.json` (format di `scripts/dekorasi.py`): palet dari `brain/brand-visual.md`, produk = foto master
   asli (`batch/*/master/depan.*`), teks pendek, `latar_prompt` untuk latar AI.
2. `python3 scripts/latar.py --spec .../dekorasi.json` → latar tanpa orang, tanpa baju, tanpa teks. Gagal = WAITING_LATAR
   (pemilik membuat latar sendiri ke path yang sama, atau head mengizinkan `"latar": null` = gradasi warna palet).
3. `python3 scripts/dekorasi.py --spec .../dekorasi.json --out .../hasil` → gambar + `laporan.json` (ukuran, KB, kontras, teks tertulis).

## Isi
- Teks hanya lewat script, bukan digambar AI. Judul ≤ 60 karakter, satu pesan per banner.
- Harga, voucher, dan potongan hanya angka yang **sudah disetujui pemilik** (riwayat `status.json`). Mode toko-baru: tanpa harga coret.
- Klaim sama dengan listing: hanya `fakta_boleh_diklaim`. Tidak ada "termurah/terbaik/terlaris".
- Kontras teks ≥ 4,5 (WCAG). Script menambah panel otomatis kalau kurang; qc tetap melihat gambarnya.
- Produk di banner = foto master asli (komposit), jadi Product Lock otomatis terjaga. Tidak boleh produk buatan AI di banner.
- Pola dari toko lain/Pinterest boleh (lihat `referensi-dekorasi.md`), gambar/desain/teks mereka tidak disalin.

## Paket minimal toko baru
1. 3 banner carousel: koleksi utama, voucher toko, kampanye terdekat (`kalender.md`).
2. 1 gambar kategori per jenis (lengan panjang / lengan pendek / warna).
3. Banner kampanye diganti sebelum tiap kampanye; banner lama diarsipkan, tidak dihapus.
