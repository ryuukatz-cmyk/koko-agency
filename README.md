# Agency Deadstock Koko — Cara pakai

Ini "kantor kecil" berisi 5 pegawai AI yang membantu menghabiskan stok koko yang tidak laku.
Kamu tetap bosnya: kamu yang menyetujui harga dan menyetujui hasil akhir.

## Siapa saja pegawainya
- **head** — ketua. Membagi tugas, memeriksa bukti, memutuskan lanjut atau berhenti.
- **researcher** — mencari stok mana yang paling lama tidak laku, mengecek harga toko lain, dan mencatat pelajaran.
- **marketer** — memilih promo (diskon, paket, voucher) dan menulis judul serta deskripsi produk.
- **creative** — membuat 10 foto dan 1 video pendek dari foto asli produk.
- **qc** — pemeriksa. Hanya menilai: LULUS, REVISI, atau TOLAK.

## Dua tempat kerja
1. **Cloud** (claude.ai/code, repo `koko-agency`, environment **koko**): untuk hampir semua pekerjaan.
   Kunci Gemini dan Cloudflare sudah tersimpan di sana, jadi pembuatan foto jalan.
2. **Komputermu** (aplikasi Claude Desktop + ekstensi Claude in Chrome): untuk riset yang perlu membuka Shopee, Pinterest, IG, dan toko lain.
   Setelah selesai, hasilnya disimpan (commit) ke GitHub supaya bisa dipakai di cloud.

## Cara memulai batch baru
1. Taruh bahan di Google Drive `Koko Agency/input/`:
   - export pesanan Shopee (kolom: `Nomor Referensi SKU`, `Waktu Pesanan Dibuat`, `Jumlah`, `Status Pesanan`)
   - export stok (kolom: `SKU`, `Nama Produk`, `Stok`, `Harga`)
   - file HPP (kolom: `SKU`, `HPP`, tulis angka polos seperti `90000`)
   - foto master produk yang tajam (kerah, kancing, bordir terlihat jelas)
2. Buka sesi baru di cloud dan tulis: **"head, mulai batch baru dari bahan di Drive."**

## Kapan kamu dipanggil
| Saat | Yang kamu lakukan |
|---|---|
| **Persetujuan harga** | Baca tabel harga, lalu jawab "setuju" atau beri koreksi |
| Foto gagal dibuat otomatis | Buat foto sendiri dari daftar prompt, taruh di Drive `output/<batch>/foto/` |
| (Opsional) video Flow | Kalau mau video lebih hidup, buat klip di Google Flow dan taruh di Drive `output/<batch>/flow/` |
| **Persetujuan akhir** | Lihat foto, video, dan laporan qc, lalu jawab "setuju" |
| Upload | Kamu sendiri yang upload ke Seller Centre (sistem tidak pernah login ke Shopee) |
| Ada masalah | Head menulis: masalahnya apa, buktinya apa, dan apa yang dibutuhkan darimu |

## Supaya pegawai makin pintar (fase belajar)
- Minta riset dengan satu pertanyaan, misalnya: *"researcher, cari tahu banner toko koko yang laris seperti apa"*.
  Lakukan di komputermu supaya Chrome bisa dipakai.
- Hasilnya ditulis dulu sebagai draf di folder `belajar/`, lalu head memilih mana yang boleh masuk ke `brain/` (buku pintar kantor).
- Pelajaran paling berharga datang dari hasil penjualanmu sendiri. Setelah promo jalan, minta researcher mengukurnya.

## Aturan yang tidak boleh dilanggar
- Tidak jual rugi: harga akhir tidak boleh di bawah HPP ditambah biaya admin.
- Produk di foto dan video harus sama persis dengan aslinya.
- Tidak login ke Shopee, tidak mengubah harga live, tidak memakai uang iklan.
- Data pembeli tidak pernah disimpan.
- Gambar dan desain toko lain hanya untuk inspirasi, tidak disalin.

Detail teknis untuk pengembang ada di `CLAUDE.md` dan `docs/`.
