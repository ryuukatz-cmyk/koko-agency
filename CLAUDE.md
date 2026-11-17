# Koko Agency — aturan singkat

Tujuan: menjalankan toko koko baru di Shopee + TikTok Shop dengan tim agent AI (listing, foto, video, dekorasi, rencana iklan),
tanpa menambah karyawan. Mode lama untuk menghabiskan deadstock tetap ada.
Desain: `docs/desain.md`. Rencana: `docs/rencana.md`, `ROADMAP.md`. Mode: `brain/aturan-toko-baru.md`, `brain/aturan-deadstock.md`.

## Sesi utama = head
Di awal setiap sesi, sesi utama membaca `.claude/agents/head.md` dan **berperan sebagai head**: memilih langkah, menulis brief,
memanggil researcher/marketer/creative/qc lewat Agent tool, memeriksa bukti. Jangan memanggil `head` sebagai subagent
(subagent belum tentu bisa memanggil subagent lain).

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
- Harga akhir tidak boleh di bawah harga minimum (`scripts/harga.py`). Mode toko-baru: tanpa harga coret.
- Produk di foto/video harus sama dengan `brain/product-lock/<sku>.md`. Foto utama katalog pakai mode komposit (produk asli).
- Tidak memakai model video berbayar.

## Belajar
Pengetahuan baru masuk `brain/` hanya lewat alur di `brain/aturan-belajar.md` (draf di `belajar/`, disetujui head).
Pinterest/IG/toko lain = inspirasi pola, tidak disalin. Dekorasi toko dibuat agent, dipasang pemilik.

## Bukti, bukan laporan
Cek file benar-benar ada, hitung ulang angka dengan script, cek video dengan `ffprobe`.
Revisi maksimal 2 kali per tahap, setelah itu OPER KE MANUSIA.

## Perintah
- Tes: `python3 -m unittest discover -s tests -v`
- Cek Cloudflare FLUX nyata (environment koko): `python3 scripts/cek_cloudflare.py` (exit 0 = jalan)
- Toko baru, pilih SKU (exit 0 ada SIAP, 1 tidak ada, 2 input salah): `python3 scripts/stok_gudang.py --stok .. --hpp .. --info .. --admin-persen 10 --hari-ini YYYY-MM-DD --out data/katalog.csv`
- Cek listing (exit 0 LULUS, 1 ada masalah, 2 input salah): `python3 scripts/cek_listing.py --listing batch/<id>/listing.csv --produk brain/produk.csv --admin-persen 10 --mode toko-baru`
- Ringkas export: `python3 scripts/export.py --pesanan .. --stok .. --hpp .. --hari-ini YYYY-MM-DD --out data/ringkas-sku.csv`
- Deadstock: `python3 scripts/deadstock.py --ringkas data/ringkas-sku.csv --out batch/<id>/riset.csv`
- Harga (exit 0 lulus, 1 TIDAK LULUS, 2 input salah): `python3 scripts/harga.py --harga-normal .. --hpp .. --admin-persen 10 [--diskon-persen ..] [--voucher-rp ..]`
- Kompetitor (exit 0 CUKUP, 1 DATA_KURANG, 2 input salah): `python3 scripts/kompetitor.py --csv batch/<id>/kompetitor.csv --hari-ini YYYY-MM-DD [--harga-kita ..]`
- Gambar (prompt dari `batch/<id>/prompt-foto.md`; blok `[komposit]` = produk asli + latar AI; exit 2 = WAITING_FOTO, 3 = input salah): `python3 scripts/gambar.py --master depan.jpg [detail.jpg ..] --batch batch/<id> [--provider cloudflare,gemini]`
- Komposit manual (latar buatan manusia): `python3 scripts/komposit.py --master depan.jpg --latar latar.png --out batch/<id>/foto/F01.png`
- Video: `python3 scripts/video.py --foto <file foto LULUS: batch/<id>/foto/F01.png ..> --nama ".." --harga "Rp .." --out batch/<id>/video/final/<id>_FINAL.mp4 [--flow ..]`
