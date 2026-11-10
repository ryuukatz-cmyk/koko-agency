# Hasil uji Fase 3 — 2026-11-10

Ringkas: **25 dari 25 kasus LULUS** (20 kasus wajib + 3 provider/video + 2 head). 56 tes unit lulus.
Semua dengan data palsu. Uji nyata Cloudflare **menunggu**: `api.cloudflare.com` masih diblokir di sesi ini dan belum ada ACCOUNT_ID.

Bukti bisa diulang:
```
python3 tests/data/buat_data_uji.py          # buat ulang data & video uji
python3 -m unittest discover -s tests -v     # 56 tes, ~30 dtk
```

## Cara uji
- **Script**: tes unit (`tests/test_*.py`) + CLI dijalankan pada `tests/data/export-palsu/`.
- **Agent qc dan head**: dijalankan sebagai agent terpisah, hanya diberi brief, **tanpa diberi tahu cacat apa yang ditanam**.
  Hasil tertulis oleh agent itu sendiri di `tests/data/batch-uji-*/qc.md` dan `tests/data/batch-uji-head-*/keputusan.md` + `status.json`.

## A. Normal

| # | Hasil | Bukti |
|---|---|---|
| N1 | LULUS | `export.py` → `tests/out/ringkas.csv`; `grep -ciE "budi\|0812\|karangan\|fiktif\|cepat"` = **0**. Tes `TestBuangDataPembeli` (3 tes) lulus |
| N2 | LULUS | `riset.csv`: A, B = DEADSTOCK; C, G, H = DEADSTOCK_DATA_KURANG; D (stok 3), E (stok 0), F (terjual 10 hari lalu) tidak masuk |
| N3 | LULUS | Skor A 100,0; B 32,7 (= 50×840.000/3.600.000 + 30×75/150 + 20×12/40). Tes `test_skor_dihitung_manual` lulus |
| N4 | LULUS | `harga.py ... --diskon-persen 20` → harga_akhir 120000, minimum 100000, margin 18000, exit 0 |
| N5 | LULUS | bundling 290.000/HPP 170.000/diskon 25% → 217500 ≥ 188889, exit 0 |
| N6 | LULUS | diskon 10% + voucher 5.000 → 130000, exit 0 |
| N7 | LULUS | `gambar.py` panggilan **Gemini asli**: model dipilih dari daftar resmi (`gemini-3.1-flash-image`), HTTP 429 tercatat di `foto/metadata.json` bagian `gagal` |
| N8 | LULUS | `ffprobe batch-uji-lulus_FINAL.mp4`: h264, **1080×1920, 30 fps, 25,5 dtk**, tanpa stream audio, 1,7 MB. `video.cek` → ok true, dekode bersih. Frame dtk 12 menampilkan "Koko Navy Bordir" + "Rp 120.000" |
| N9 | LULUS | `batch-uji-lulus/qc.md`: F01–F10 LULUS, harga dihitung ulang LULUS, copy LULUS, video LULUS. Putusan batch **LULUS** |
| N10 | LULUS | `batch-uji-head-2/status.json`: STRATEGI → **APPROVAL_HARGA**. Head menolak saran marketer "pemilik pasti setuju, langsung KONTEN_FOTO", menghitung ulang harga sendiri, menulis tabel untuk pemilik di `keputusan.md` |

## B. Pinggiran

| # | Hasil | Bukti |
|---|---|---|
| P1 | LULUS | KOKO-G: hpp kosong + `HPP_KOSONG`, status DATA_KURANG tanpa skor; `harga.py --hpp 0` → exit 2 + pesan error |
| P2 | LULUS | KOKO-E (stok 0) tidak ada di `riset.csv`; tes `test_batas_aturan` |
| P3 | LULUS | KOKO-H: `SKU_DOBEL`, stok dijumlah 16, tidak diskor |
| P4 | LULUS | `batch-uji-buram/qc.md`: master **TOLAK**, "kancing tidak bisa dihitung, bordir hanya bercak", oper ke manusia minta master jelas, Product Lock jangan dibuat |
| P5 | LULUS | `hitung(125000, 90000, 10, 20)` → harga akhir 100000 = minimum, margin 0, lulus (tes `test_diskon_pas_di_batas_lulus`) |
| P6 | LULUS | `batch-uji-cacat/qc.md`: **V05 TOLAK** "produk lain — badan hijau, 3 kancing, tanpa bordir"; video final TOLAK (dtk 14–17 produk hijau) |

## C. Wajib ditolak

| # | Hasil | Bukti |
|---|---|---|
| T1 | LULUS | `harga.py --diskon-persen 35` → 97500 < 100000, exit 1. qc: Harga **TOLAK**, margin −2.250 |
| T2 | LULUS | qc: **F04 TOLAK** "badan + kerah merah marun, master navy"; V04 juga TOLAK |
| T3 | LULUS | qc: pasangan F10/P10/V10 **REVISI** (V10 tidak ada). Setelah perbaikan code review, `video.py` juga menolak sendiri: "klip Flow tidak berpasangan 1:1. Foto tanpa klip: ['F10']" |
| T4 | LULUS | qc: Copy **TOLAK** — "Premium", "Best Seller", "Anti Luntur", "garansi uang kembali", "adem seharian" tidak ada di produk.csv |

## D. Provider dan video

| # | Hasil | Bukti |
|---|---|---|
| X1 | LULUS (mock) | `test_gemini_429_jatuh_ke_cloudflare`: 3 foto via Cloudflare, `metadata.json` provider=cloudflare, model `@cf/black-forest-labs/flux-2-klein-4b`, Gemini dipanggil 1×; argumen curl tanpa "Authorization" |
| X2 | LULUS (mock + nyata) | Nyata: Gemini 429 asli → Cloudflare dilewati ("CF_ACCOUNT_ID / config/cloudflare-account-id.txt tidak ada") → `{"status": "WAITING_FOTO"}`, exit 2 |
| X3 | LULUS | `test_folder_flow_kosong_pakai_slideshow`; batch-uji-lulus tanpa klip → mode slideshow |

## E. Head

| # | Hasil | Bukti |
|---|---|---|
| H1 | LULUS | `batch-uji-head-1`: head menghitung sendiri, folder hanya 9 foto, F10 dan `metadata.json` tidak ada → tetap KONTEN_FOTO, `revisi.KONTEN_FOTO = 1`, brief ulang ke creative |
| H2 | LULUS | `batch-uji-head-3`: revisi ke-3 → **OPER_KE_MANUSIA** dengan kalimat oper baku dan 3 pilihan untuk pemilik |

## Code review (agent-skills:code-reviewer)

18 temuan. Yang serius sudah diperbaiki, masing-masing dengan tes yang gagal dulu lalu lulus:

| Temuan | Perbaikan |
|---|---|
| KRITIS: `"90,000"` terbaca 90 → harga minimum ambruk | koma/titik ribuan dibaca benar; format ambigu → error |
| KRITIS: desimal xlsx `83333.333…` terbaca 8 miliar | angka xlsx tidak diubah ke teks |
| Tanggal tak terbaca dilewati diam-diam | proses berhenti dengan contoh baris; format `1/11/2026` didukung |
| Folder foto ikut memasukkan foto yang ditolak QC | `video.py` wajib daftar foto LULUS |
| Klip Flow tidak dicek pasangan 1:1 | dicek; tidak cocok → berhenti, head memutuskan |
| Tidak pernah terjual tetap diskor penuh | jadi DATA_KURANG (bisa produk baru) |
| Satu gagal sementara membuang provider | hanya gagal tingkat akun (401/402/403/404/429) yang membuang |
| Model `-preview` tidak dikenali | dicocokkan prefiks |
| `cek` tidak menolak audio | ditolak |
| Kecil: `%{}` di teks video, `~/.curlrc`, JSON aneh crash, foto lama tertinggal, exit code harga, SKU beda huruf, `mentah/` di tests | semua diperbaiki |

Tidak diperbaiki (kecil): teks `--harga` di video tidak otomatis dicocokkan dengan listing.csv (dicek qc & head), judul prompt `## F01 - studio` tidak dikenali (format ditetapkan di creative.md).

## Uji nyata Cloudflare FLUX (2026-11-10, setelah token dipasang)

- Perintah: `gambar.py --master tests/data/master-CONTOH-KOKO-01.png` dengan 1 prompt.
- Hasil: Gemini HTTP 429 (tercatat) → **Cloudflare `@cf/black-forest-labs/flux-2-klein-4b` berhasil**, 8 dtk, JPEG 1024×1024, 483 KB, `metadata.json` provider=cloudflare. Exit 0.
- Penilaian visual (pembanding, bukan putusan qc): warna navy, kerah shanghai, bordir emas dada kiri **terjaga**; tetapi kancing **4, bukan 5**, dan muncul **label putih di leher** yang tidak ada di master → akan **TOLAK** menurut Product Lock.
- Pelajaran: FLUX menjaga warna & bordir besar, tapi menambah/mengurangi detail kecil. qc wajib menghitung kancing dan mencari tambahan (label, logo, saku).

## Yang belum teruji
- Gemini gambar nyata (kuota free tier 0, perlu billing).
- Nama kolom export Shopee & file HPP asli (Fase 4).
- QC visual pada foto AI sungguhan (data uji berupa gambar sederhana; cacatnya mencolok).
