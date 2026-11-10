# Desain — Agency Deadstock Koko

Tanggal: 2026-11-10. Status: disetujui pemilik ("lanjut, pakai semua default aman") + keputusan media tambahan.

## 1. Tujuan dan alasan

Toko Shopee baju koko punya stok yang tidak laku (deadstock). Modal tertahan di gudang.
Tujuan: tim AI agent yang membantu menghabiskan deadstock **tanpa menambah karyawan**.
Pemilik hanya dipanggil di titik keputusan berisiko (harga, publikasi).

Sukses = deadstock terjual, rupiah kembali, tanpa jual rugi dan tanpa produk "berubah" di konten.

## 2. Prinsip (dari workbook DIMENSI Labs)

- Yang memberi arah (**head**), yang membuat (**researcher, marketer, creative**), dan yang mengecek (**qc**) dipisah. Pembuat tidak menilai kerjaannya sendiri.
- Laporan agent hanya petunjuk. Yang menentukan adalah bukti: file ada, angka dihitung ulang, `ffprobe`, hasil tes.
- Manusia memegang keputusan berisiko: harga (APPROVAL_HARGA) dan publikasi (APPROVAL_FINAL).
- Yang gagal kembali ke pembuatnya. Maksimal 2 revisi, lalu OPER KE MANUSIA.
- Template oper ke manusia (dari workbook): "Batch {ID} berhenti di {STATUS}. Masalah: {TEMUAN}. Bukti: {FILE/ID}. Yang saya butuhkan: {AKSI}. Setelah itu proses lanjut dari {LANGKAH} tanpa mengulang tahap yang sudah lulus."

## 3. Tujuan, bukan tujuan, anti-tujuan

**Tujuan:** daftar deadstock berskor, strategi + harga per SKU, 10 foto kreatif, 1 video 9:16 siap upload, listing.csv, checklist upload manual, pengukuran hasil.

**Bukan tujuan (sekarang):** ops, CS, iklan (lihat ROADMAP.md). Upload otomatis.

**Anti-tujuan (gagal walau "jalan"):**
- Sistem login ke Shopee, mengubah harga live, atau mengeluarkan uang iklan.
- Harga akhir di bawah harga minimum.
- Warna/bentuk/logo/bordir produk berubah di foto atau video.
- Data pembeli (nama, alamat, HP, username) masuk repo.
- API key tertulis di file atau commit.
- Batch dinyatakan READY_UPLOAD tanpa QC_FINAL LULUS dan persetujuan manusia.

## 4. Batasan

- Jaringan "Terbatas": generativelanguage.googleapis.com, ai.google.dev, manajer paket. `api.cloudflare.com` dan `aistudio.google.com` sedang ditambahkan pemilik; per 2026-11-10 masih diblokir di sesi ini.
- Gemini: key berfungsi, tapi semua model gambar 429 "limit: 0" (free tier tanpa billing).
- Kunci API hanya lewat proxy (network secret). Script **tidak pernah** mengirim header Authorization sendiri.
- Tidak ada model video berbayar.

## 5. Asumsi (semua bisa dikoreksi pemilik)

| Hal | Nilai | Sumber |
|---|---|---|
| Deadstock | tidak terjual ≥ 60 hari **dan** stok ≥ 5 | ASUMSI (default aman) |
| Harga minimum | harga akhir − biaya admin ≥ HPP, yaitu harga akhir ≥ HPP ÷ (1 − admin%) | ASUMSI |
| Biaya admin Shopee | 10% dari harga akhir yang dibayar pembeli | ASUMSI |
| Voucher toko | ditanggung penjual, mengurangi harga akhir | ASUMSI |
| Bahasa | santai-sopan, tanpa klaim yang tidak ada di data produk | ASUMSI |
| Video | 9:16 (1080×1920), 15–30 detik, tanpa musik | ASUMSI |
| Nama kolom export Shopee | lihat `scripts/export.py` (daftar alias) | ASUMSI, dicek di Fase 4 |
| Pesanan "Batal"/"Dibatalkan" | tidak dihitung terjual | ASUMSI |

## 6. Pendekatan yang dipertimbangkan

1. **Agent Claude Code + script Python kecil (DIPILIH).** Agent di `.claude/agents/`, aturan di `brain/`, hitungan pasti (harga, skor, buang data pembeli) di script ber-tes. Alasan: angka uang tidak boleh ditebak model; script bisa dites dan dihitung ulang oleh qc.
2. Semua dikerjakan agent tanpa script. Ditolak: hitungan harga tidak bisa dibuktikan, tidak bisa TDD.
3. Aplikasi/server sendiri (web app, database). Ditolak: lebih berat dari kebutuhan; satu batch = satu folder sudah cukup.

## 7. Peran

| Agent | Model | Membuat | Tidak boleh |
|---|---|---|---|
| head | opus | brief, keputusan LANJUT/REVISI/STOP/OPER KE MANUSIA, `status.json` | membuat konten, menulis kode, percaya laporan tanpa cek bukti |
| researcher | sonnet | `riset.md`, `riset.csv`; nanti `hasil.md` (pengukuran) | menebak angka; data kosong ditandai |
| marketer | sonnet | `strategi.md`, `listing.csv` | harga di bawah minimum; klaim di luar data produk |
| creative | sonnet | `foto/`, `prompt-foto.md`, `prompt-flow.md`, `video/final/` | mengubah produk; menilai hasil sendiri |
| qc | opus | `qc.md` saja | memperbaiki apa pun |

Hanya **head** yang mengubah `status.json`.

## 8. Alur status (satu batch = satu SKU)

```
NEW → RISET → STRATEGI → APPROVAL_HARGA (manusia)
    → KONTEN_FOTO → [WAITING_FOTO (manusia), hanya jika provider gambar jatuh ke manual]
    → QC_FOTO → [WAITING_FLOW (manusia), opsional]
    → EDIT_VIDEO → QC_FINAL → APPROVAL_FINAL (manusia)
    → READY_UPLOAD → LIVE → DIUKUR
```

- Dari QC_FOTO: LULUS → EDIT_VIDEO (default) atau WAITING_FLOW (jika pemilik mau klip Flow). REVISI → KONTEN_FOTO.
- Dari QC_FINAL: LULUS → APPROVAL_FINAL. REVISI → EDIT_VIDEO (atau KONTEN_FOTO jika fotonya yang salah).
- Setiap status boleh ke `OPER_KE_MANUSIA` atau `STOP`.
- `status.json`: `{"batch","sku","status","revisi":{"<tahap>":n},"riwayat":[{"waktu","dari","ke","oleh":"head","alasan","bukti"}]}`.
- Revisi ke-3 pada tahap yang sama → OPER_KE_MANUSIA.
- LIVE diisi head setelah pemilik bilang sudah upload. DIUKUR setelah researcher membandingkan export baru.

## 9. Media (keputusan pemilik, final)

### Gambar — `scripts/gambar.py`, satu script, provider berurutan

1. **Gemini**: model gambar dipilih dari `GET /v1beta/models` (urutan pilihan: `gemini-3.1-flash-image`, `gemini-3-pro-image`, `gemini-2.5-flash-image`). Foto master dikirim sebagai referensi. Gagal (mis. 429) → catat, lewati untuk sisa batch.
2. **Cloudflare Workers AI** `@cf/black-forest-labs/flux-2-klein-4b`: multipart `prompt`, `input_image_0` (master dikecilkan < 512×512), `width`, `height`. Akun dari env `CF_ACCOUNT_ID` atau `config/cloudflare-account-id.txt`; kalau tidak ada → lewati. Token dipasang proxy.
3. **Manual**: tulis 10 prompt ke `batch/<id>/prompt-foto.md`, status WAITING_FOTO. Pemilik generate sendiri (Flow / aplikasi Gemini) dan menaruh hasil di Drive `Koko Agency/output/<batch>/foto/`.

Provider hanya dilewati untuk sisa batch bila gagal tingkat akun (HTTP 401/402/403/404/429, model tidak ada, akun tidak diatur). Gagal sementara (5xx, timeout, jawaban tanpa gambar) hanya berlaku untuk foto itu.
Setiap foto punya catatan di `foto/metadata.json`: id, provider, model, prompt, waktu. Percobaan yang gagal juga dicatat.
QC Product Lock wajib untuk semua provider; FLUX rawan kehilangan bordir/logo → QC ketat.

### Video — `scripts/video.py`

1. **Default (otomatis, gratis):** slideshow ffmpeg dari foto LULUS QC: zoom pelan, transisi fade, teks nama produk + harga akhir yang **sudah disetujui**, tanpa musik, 1080×1920, 15–30 detik.
2. **Opsional:** kalau ada klip Flow di Drive `.../<batch>/flow/`, ffmpeg memotong, menggabung, dan memberi teks harga. Kalau tidak ada klip → otomatis pakai slideshow. Klip yang tidak berpasangan 1:1 dengan foto LULUS, rusak, atau total < 15 dtk → script berhenti dan head memutuskan (perbaikan setelah code review).

Output: satu video final per batch (`video/final/<batch>_FINAL.mp4`). Kalau Flow dipakai, klip harus berpasangan 1:1: `F01 ↔ P01 ↔ V01`.

## 10. Data

- Input mentah (export pesanan, export stok, HPP) dibaca dari folder sementara `data/mentah/` (di-.gitignore).
- `scripts/export.py` membuang kolom data pembeli **sebelum** apa pun disimpan, lalu meringkas per SKU ke `data/ringkas-sku.csv` (boleh di-commit: tidak ada data pembeli).
- `scripts/deadstock.py` → daftar deadstock + skor.
- `scripts/harga.py` → harga minimum, harga akhir, margin, LULUS/TIDAK.

Skor prioritas (0–100), hanya untuk SKU yang lolos aturan deadstock dan datanya lengkap:
`skor = 50·modal/modal_maks + 30·umur/umur_maks + 20·stok/stok_maks`, modal = stok × HPP.
HPP kosong → ditandai `HPP_KOSONG`, tidak diberi skor. SKU dobel → `SKU_DOBEL`, tidak diberi skor sampai manusia memilih.
Tidak pernah terjual di data → `TIDAK_TERJUAL_SEPANJANG_DATA`, tidak diberi skor (bisa produk baru; manusia cek tanggal listing).

## 11. Struktur repo

```
.claude/agents/{head,researcher,marketer,creative,qc}.md
brain/ produk.csv, product-lock/<sku>.md, aturan-deadstock.md, aturan-harga.md,
       aturan-shopee.md, brand-voice.md, format-video.md
scripts/ export.py, deadstock.py, harga.py, gambar.py, video.py
tests/ test_*.py, kasus-uji.md, hasil-uji.md, data/
batch/<id>/ status.json, riset.*, strategi.md, listing.csv, foto/, prompt-*.md, video/, qc.md
config/cloudflare-account-id.txt (opsional, bukan rahasia)
CLAUDE.md, ROADMAP.md, .gitignore
```

## 12. Diserahkan ke pembangun (keputusan pembangun)

- Bahasa script: Python 3 + library yang sudah ada (openpyxl untuk .xlsx). Tes: `unittest` bawaan.
- HTTP lewat `curl` (sudah ikut proxy dan CA), dibungkus satu fungsi agar bisa di-mock.
- Ukuran foto default 1024×1024; video menaruh foto persegi di kanvas 9:16 berlatar putih.
- Durasi slideshow: 3 detik per foto, dibatasi 15–30 detik total.

## 13. Riset kompetitor (disetujui pemilik 2026-11-10)

- **Kapan:** setelah RISET memilih SKU, sebelum STRATEGI. Brief dari head ke researcher.
- **Hasil:** `batch/<id>/kompetitor.csv` + `kompetitor.md`, minimal 5 produk mirip (jenis, lengan, bordir/motif, warna).
  Kolom: `sku_kita,platform,toko,judul,harga,harga_coret,terjual,rating,link,sumber,dicek_pada`.
- **Sumber (gratis saja):**
  - `cuplikan` — hasil pencarian web (WebSearch). Tidak dihitung, hanya petunjuk.
  - `halaman` — halaman produk dibuka langsung (WebFetch; Tokopedia/Blibli diizinkan di environment).
  - `chrome` — dibaca lewat Claude in Chrome di komputer pemilik (Shopee, TikTok Shop, IG, Meta Ad Library).
- **Hitungan:** `scripts/kompetitor.py` menghitung harga termurah, tengah (median), termahal **hanya dari `halaman`/`chrome`**.
  Kurang dari 5 terverifikasi → `DATA_KURANG` (tidak memblokir, tapi marketer & pemilik diberi tahu).
- **Aturan:** hanya membaca halaman publik; tidak login, tidak mengubah apa pun di Shopee/Seller Centre; tidak memalsukan identitas browser
  atau mengakali pemblokir bot; maksimal ±15 halaman per SKU. Harga minimum tetap menang atas harga kompetitor.
- **qc:** setiap baris punya link, sumber, tanggal; angka dihitung ulang dengan script.
- **Tidak termasuk:** Apify, Agent-Reach, scraping massal, pengumpulan contoh iklan/konten IG.

## 14. Fase belajar (disetujui pemilik 2026-11-10)

- Di awal, pengetahuan dikumpulkan lewat Claude in Chrome (e-commerce, web, Pinterest, IG, TikTok, Meta Ad Library) di komputer pemilik;
  setelah matang, agent bekerja dari `brain/` tanpa browsing, kecuali pembaruan berkala (harga bulanan, sebelum Ramadan/Lebaran).
- Alur: pertanyaan dari head → researcher menulis draf `belajar/<tanggal>-<topik>.md` → head menyaring → poin lolos masuk
  `brain/referensi-prompt.md`, `brain/referensi-dekorasi.md`, `brain/aturan-kompetitor.md`, atau `brain/pelajaran.md`.
- Hasil toko sendiri (`brain/pelajaran.md`) diutamakan atas riset luar.
- Dekorasi toko: agent membuat usulan, pemilik memasang. Karya orang lain hanya inspirasi pola (qc cek g).
- Pembagian tempat: komputer pemilik = riset lewat Chrome; cloud = deadstock, harga, foto (token ada di environment cloud), video, qc.
  Penghubungnya repo GitHub yang sama.
- Tidak termasuk: produksi banner, jadwal otomatis, landing page (ROADMAP).
