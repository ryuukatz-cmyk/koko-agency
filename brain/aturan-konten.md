# Aturan konten (TikTok, Instagram Reels, Shopee Video)

Agent meriset dan menyusun rencana + naskah; **pemilik yang memposting** (atau menyetujui jadwal di alat penjadwal miliknya).
Batch tingkat toko: `batch/<YYYY-MM-DD>-toko-konten`.

## Alur
1. researcher: skill `riset-konten-marketplace` → `riset-konten.csv` + `riset-konten.md` (bukti + tanggal).
2. marketer: skill `social` + `copywriting` → `kalender-konten.csv` (2–4 minggu) + naskah per baris.
3. `python3 scripts/cek_konten.py --kalender .. --produk brain/produk.csv` → exit 0.
4. qc (cek j) → APPROVAL_KONTEN → pemilik memposting → diukur bersama `scripts/ukur.py`.

## kalender-konten.csv
Kolom: `tanggal,platform,format,pilar,sku,hook,naskah,cta,tagar,aset,harga_ditampilkan`
- `platform`: tiktok | instagram | shopee-video. `format`: slideshow | talking-head | close-up | pov | try-on | carousel.
- `pilar` (ASUMSI, pemilik boleh ubah): `produk` (detail & ukuran), `momen` (Jumatan, Ramadan, Lebaran), `cara-pakai`
  (padu padan, perawatan — hanya fakta), `toko` (proses, packing, di balik layar).
- `hook` ≤ 100 karakter, isi 3 detik pertama. `naskah` = urutan adegan + teks layar. `aset` = file yang dipakai/dibutuhkan
  (foto LULUS, video final, atau "rekam: <deskripsi>" untuk pemilik).
- `harga_ditampilkan`: kosong, atau harga yang sudah disetujui pemilik (dicek ke listing.csv).

## Isi
- Klaim sama dengan listing: hanya `fakta_boleh_diklaim`; tanpa "termurah/terbaik/terlaris"; desakan hanya kalau benar.
- Pola dari riset boleh dipakai, naskah/video/musik orang lain tidak. Musik dipilih pemilik dari pustaka resmi aplikasi.
- Frekuensi awal (ASUMSI): TikTok 1/hari, Reels 3–4/minggu, Shopee Video 3/minggu; tinjau tiap 2 minggu dari data.
- Wajah/orang di video: hanya pemilik atau orang yang sudah setuju. Tanpa model AI wajah orang sungguhan.
