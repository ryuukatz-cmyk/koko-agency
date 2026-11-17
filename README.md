# Koko Agency — Cara pakai

Ini "kantor kecil" berisi 5 pegawai AI yang menyiapkan toko koko baru di Shopee + TikTok Shop: memilih SKU dari stok gudang,
riset kompetitor & kata kunci, harga, judul/deskripsi per platform, 10 foto + 1 video per SKU. Dekorasi toko dan rencana iklan
menyusul (lihat `ROADMAP.md`). Mode lama untuk menghabiskan deadstock toko yang sudah jalan tetap ada.
Kamu tetap bosnya: kamu yang menyetujui harga dan menyetujui hasil akhir.

## Siapa saja pegawainya
- **head** — ketua. Membagi tugas, memeriksa bukti, memutuskan lanjut atau berhenti. Head = sesi utama (otomatis lewat `CLAUDE.md`).
- **researcher** — memilih SKU yang siap dari stok gudang, mengecek harga toko lain, mencari kata kunci yang diketik pembeli, dan mencatat pelajaran.
- **marketer** — memilih promo (voucher, paket, grosir) dan menulis judul serta deskripsi untuk Shopee dan TikTok Shop.
- **creative** — membuat 10 foto (3 foto utama = produk asli di atas latar AI, 7 foto scene AI) dan 1 video pendek.
- **qc** — pemeriksa. Hanya menilai: LULUS, REVISI, atau TOLAK.

## Dua tempat kerja
1. **Cloud** (claude.ai/code, repo `koko-agency`, environment **koko**): untuk hampir semua pekerjaan.
   Kunci Gemini dan Cloudflare sudah tersimpan di sana, jadi pembuatan foto jalan.
2. **Komputermu** (aplikasi Claude Desktop + ekstensi Claude in Chrome): untuk riset yang perlu membuka Shopee, Pinterest, IG, dan toko lain.
   Setelah selesai, hasilnya disimpan (commit) ke GitHub supaya bisa dipakai di cloud.

## Folder Google Drive (jangan dicampur)
Aturan gampangnya: **kamu mengisi `input/`, agent mengisi `output/`.** Agent hanya membaca folder bernomor; file lain di luar itu diabaikan.

```
Koko Agency/
├── input/                      ← KAMU yang isi
│   ├── 1-stok-gudang/stok-gudang   TOKO BARU: satu lembar SKU | nama | stok | harga_jual_rencana | tanggal_masuk | catatan
│   ├── 1-export-shopee/        (mode deadstock) export pesanan + export stok dari Seller Centre (file asli, jangan diedit)
│   ├── 2-hpp/hpp               satu lembar: SKU | HPP  (angka polos, mis. 90000)
│   ├── 3-info-produk/info-produk   satu lembar: SKU | nama | warna | ukuran | bahan | fakta_boleh_diklaim | catatan
│   ├── 4-foto-master/<SKU>/    satu folder per SKU, nama folder = SKU persis
│   └── 5-export-shopee/        nanti, setelah toko jalan: export pesanan untuk mengukur hasil
└── output/                     ← AGENT yang isi
    └── <batch>/                mis. 2026-11-15-KOKO-A
        ├── foto/               10 foto hasil agent (kalau FLUX gagal, KAMU taruh foto buatanmu di sini)
        ├── flow/               (opsional) klip Google Flow buatanmu: V01.mp4, V02.mp4 …
        └── final/              video final, listing.csv, checklist upload
```

**Isi tiap folder**
| Folder | Isi | Nama file | Catatan |
|---|---|---|---|
| `1-export-shopee` | Export **pesanan** minimal 90 hari terakhir + export **stok/produk** | `pesanan-YYYY-MM-DD.xlsx`, `stok-YYYY-MM-DD.xlsx` (tanggal export) | Kolom pesanan: `Nomor Referensi SKU`, `Waktu Pesanan Dibuat`, `Jumlah`, `Status Pesanan`. Kolom stok: `SKU`, `Nama Produk`, `Stok`, `Harga`. Data pembeli di dalamnya dibuang otomatis, tidak pernah disimpan agent. |
| `2-hpp` | Lembar `hpp` (sudah disiapkan) | — | Satu baris per SKU. SKU harus sama persis dengan di Shopee. HPP kosong = SKU itu tidak diproses harganya. |
| `3-info-produk` | Lembar `info-produk` (sudah disiapkan) | — | `fakta_boleh_diklaim` = hal yang **benar** tentang produk, pisahkan dengan `;` (mis. `katun;bordir dada kiri;kerah shanghai`). Agent tidak boleh menulis klaim di luar kolom ini. |
| `1-stok-gudang` | Lembar `stok-gudang` (toko baru) | — | Satu baris per SKU. `harga_jual_rencana` angka polos (mis. 150000), `tanggal_masuk` format `2026-11-01`. Harga di bawah HPP + admin akan ditandai. |
| `4-foto-master/<SKU>/` | 1–4 foto asli produk | `depan.jpg` (wajib), `detail-bordir.jpg`, `belakang.jpg` | Tajam, cahaya terang, produk penuh terlihat, **latar polos satu warna** dan produk tidak menyentuh tepi foto (wajib untuk foto komposit). Foto buram akan ditolak qc. |

File lama tidak perlu dihapus; agent memakai export dengan tanggal **terbaru**.

## Sekali di awal: sambungkan alat
| Alat | Untuk | Cara |
|---|---|---|
| Google Drive (connector claude.ai) | head membaca `input/` dan menulis `output/` | claude.ai → Settings → Connectors → Google Drive |
| Claude in Chrome (ekstensi, di komputermu) | riset Shopee/TikTok/Pinterest, saran kata kunci, cek ukuran di Seller Centre | pasang ekstensi, jalankan riset dari aplikasi desktop |
| Cloudflare Workers AI (token di environment koko) | foto & latar FLUX gratis ±10.000 neurons/hari | network environment izinkan `api.cloudflare.com`, token dipasang sebagai secret proxy |
| Gemini (opsional, perlu billing) | provider gambar cadangan | key di proxy environment |
Lalu di sesi cloud jalankan `bash scripts/setup.sh` (cek ffmpeg/Pillow/openpyxl + tes cepat).

## Perintah cepat (ketik di sesi Claude Code)
| Perintah | Hasil |
|---|---|
| `/status` | apa yang menunggu keputusanmu |
| `/batch-baru [SKU]` | mulai 1 SKU sampai tabel persetujuan harga |
| `/lanjut [batch] [catatan]` | lanjutkan setelah kamu setuju / menaruh file |
| `/dekorasi [kampanye]` | banner carousel, voucher, kategori untuk toko |
| `/iklan [budget harian]` | rencana iklan dari margin (kamu yang pasang & bayar) |
| `/ukur [tanggal tayang]` | hasil mingguan dari export pesanan baru |
| `/belajar <pertanyaan>` | riset satu pertanyaan → pengetahuan baru di `brain/` |
| `/cek-cloudflare` | uji FLUX nyata |
| `/demo [--flux]` | latihan alur lengkap dengan data `contoh/` |

## Sekali di awal: cek Cloudflare FLUX
Di sesi cloud environment **koko**, tulis: **"jalankan python3 scripts/cek_cloudflare.py"**.
Hasilnya 3 gambar uji di `tests/out/cek-cloudflare/` dan `"ok": true`. Kalau `false`, ikuti isi `saran`
(mis. izinkan `api.cloudflare.com` di network environment, atau pasang token Cloudflare).
Jatah gratis Cloudflare ±10.000 neurons/hari (reset 07.00 WIB) ≈ ±90 foto 1024×1024 ≈ ±9 SKU per hari.

## Cara memulai batch baru
1. Isi folder `input/` seperti tabel di atas (toko baru: `1-stok-gudang`, `2-hpp`, `3-info-produk`, `4-foto-master`).
2. Isi `brain/brand-visual.md` (nama toko, palet, gaya foto) — atau minta creative membuat 2–3 usulan untuk kamu pilih.
3. Buka sesi baru di cloud dan tulis: **"mulai batch toko baru dari bahan di Drive."**

## Latihan tanpa data asli
`contoh/` berisi 4 SKU palsu (foto, stok, HPP, info produk). Jalankan `/demo` untuk melihat hasil tiap langkah:
katalog → harga → listing Shopee & TikTok → 10 foto → video → 3 banner → rencana iklan → paket upload (zip + checklist).

## Kapan kamu dipanggil
| Saat | Yang kamu lakukan |
|---|---|
| **Persetujuan harga** | Baca tabel harga, lalu jawab "setuju" atau beri koreksi |
| Foto gagal dibuat otomatis | Buat foto sendiri dari daftar prompt, taruh di Drive `output/<batch>/foto/` |
| (Opsional) video Flow | Kalau mau video lebih hidup, buat klip di Google Flow dan taruh di Drive `output/<batch>/flow/` |
| **Persetujuan akhir** | Lihat foto, video, dan laporan qc, lalu jawab "setuju" |
| Dekorasi | Lihat banner, jawab "setuju", lalu pasang di Seller Centre > Dekorasi Toko |
| Iklan | Beri budget harian, setujui rencana, lalu pasang & bayar sendiri di dashboard iklan |
| Upload | Kamu sendiri yang upload ke Seller Centre (sistem tidak pernah login ke Shopee) |
| Ada masalah | Head menulis: masalahnya apa, buktinya apa, dan apa yang dibutuhkan darimu |

## Supaya pegawai makin pintar (fase belajar)
- Minta riset dengan satu pertanyaan, misalnya: *"researcher, cari tahu banner toko koko yang laris seperti apa"*.
  Lakukan di komputermu supaya Chrome bisa dipakai.
- Hasilnya ditulis dulu sebagai draf di folder `belajar/`, lalu head memilih mana yang boleh masuk ke `brain/` (buku pintar kantor).
- Pelajaran paling berharga datang dari hasil penjualanmu sendiri. Setelah promo jalan, minta researcher mengukurnya.

## Aturan yang tidak boleh dilanggar
- Tidak jual rugi: harga akhir tidak boleh di bawah HPP ditambah biaya admin. Toko baru: tanpa harga coret.
- Produk di foto dan video harus sama persis dengan aslinya.
- Tidak login ke Shopee, tidak mengubah harga live, tidak memakai uang iklan.
- Data pembeli tidak pernah disimpan.
- Gambar dan desain toko lain hanya untuk inspirasi, tidak disalin.

Detail teknis untuk pengembang ada di `CLAUDE.md` dan `docs/`.
