# Agency Deadstock Koko — aturan singkat

Tujuan: menghabiskan deadstock toko Shopee koko tanpa menambah karyawan.
Desain: `docs/desain.md`. Rencana: `docs/rencana.md`.

## Peran (yang mengarahkan, membuat, dan mengecek dipisah)
- head mengarahkan dan satu-satunya yang mengubah `batch/<id>/status.json`.
- researcher, marketer, creative membuat. Tidak menilai kerjaan sendiri.
- qc menilai saja (LULUS / REVISI / TOLAK), tidak memperbaiki, hanya menulis `qc.md`.
- Manusia memutuskan harga (APPROVAL_HARGA) dan publikasi (APPROVAL_FINAL).

## Larangan keras
- Tidak login ke Shopee, tidak mengubah harga live, tidak mengeluarkan uang iklan.
- Riset kompetitor hanya membaca halaman publik (lihat `brain/aturan-kompetitor.md`). Tidak mengubah apa pun di Shopee/Seller Centre, tidak mengakali pemblokir bot.
- Tidak menulis API key ke file/commit. Gemini & Cloudflare dipanggil tanpa key; proxy menambahkannya. Jangan kirim header Authorization.
- Tidak commit data pembeli. Export mentah hanya di `data/mentah/` (di-.gitignore). Repo hanya menyimpan ringkasan per SKU.
- Harga akhir tidak boleh di bawah harga minimum (`scripts/harga.py`).
- Produk di foto/video harus sama dengan `brain/product-lock/<sku>.md`.
- Tidak memakai model video berbayar.

## Belajar
Pengetahuan baru masuk `brain/` hanya lewat alur di `brain/aturan-belajar.md` (draf di `belajar/`, disetujui head).
Pinterest/IG/toko lain = inspirasi pola, tidak disalin. Dekorasi toko dibuat agent, dipasang pemilik.

## Bukti, bukan laporan
Cek file benar-benar ada, hitung ulang angka dengan script, cek video dengan `ffprobe`.
Revisi maksimal 2 kali per tahap, setelah itu OPER KE MANUSIA.

## Perintah
- Tes: `python3 -m unittest discover -s tests -v`
- Ringkas export: `python3 scripts/export.py --pesanan .. --stok .. --hpp .. --hari-ini YYYY-MM-DD --out data/ringkas-sku.csv`
- Deadstock: `python3 scripts/deadstock.py --ringkas data/ringkas-sku.csv --out batch/<id>/riset.csv`
- Harga (exit 0 lulus, 1 TIDAK LULUS, 2 input salah): `python3 scripts/harga.py --harga-normal .. --hpp .. --admin-persen 10 [--diskon-persen ..] [--voucher-rp ..]`
- Kompetitor (exit 0 CUKUP, 1 DATA_KURANG, 2 input salah): `python3 scripts/kompetitor.py --csv batch/<id>/kompetitor.csv --hari-ini YYYY-MM-DD [--harga-kita ..]`
- Gambar (prompt dibaca dari `batch/<id>/prompt-foto.md`; exit 2 = WAITING_FOTO): `python3 scripts/gambar.py --master .. --batch batch/<id>`
- Video: `python3 scripts/video.py --foto <file foto LULUS: batch/<id>/foto/F01.png ..> --nama ".." --harga "Rp .." --out batch/<id>/video/final/<id>_FINAL.mp4 [--flow ..]`
