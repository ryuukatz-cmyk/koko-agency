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

## Folder Google Drive (jangan dicampur)
Aturan gampangnya: **kamu mengisi `input/`, agent mengisi `output/`.** Agent hanya membaca folder bernomor; file lain di luar itu diabaikan.

```
Koko Agency/
├── input/                      ← KAMU yang isi
│   ├── 1-export-shopee/        export pesanan + export stok dari Seller Centre (file asli, jangan diedit)
│   ├── 2-hpp/hpp               satu lembar: SKU | HPP  (angka polos, mis. 90000)
│   ├── 3-info-produk/info-produk   satu lembar: SKU | nama | warna | ukuran | bahan | fakta_boleh_diklaim | catatan
│   └── 4-foto-master/<SKU>/    satu folder per SKU, nama folder = SKU persis
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
| `4-foto-master/<SKU>/` | 1–3 foto asli produk | `depan.jpg` (wajib), `detail-bordir.jpg`, `belakang.jpg` | Tajam, cahaya terang, produk penuh terlihat, latar polos. Foto buram akan ditolak qc. |

File lama tidak perlu dihapus; agent memakai export dengan tanggal **terbaru**.

## Cara memulai batch baru
1. Isi folder `input/` seperti tabel di atas.
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
