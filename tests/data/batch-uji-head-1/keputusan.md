# Keputusan head — batch-uji-head-1

Status: KONTEN_FOTO → KONTEN_FOTO. Keputusan: **REVISI** (revisi KONTEN_FOTO ke-1 dari maks 2).

## Bukti yang saya cek sendiri
- `laporan-creative.md` mengklaim 10 foto (F01–F10). Faktanya `foto/` berisi **9 file** (F01–F09). F10 tidak ada.
- Semua foto **< 10 KB** (7.365–9.656 byte). Header PNG valid, 1024×1024, tetapi ukuran segini terlalu kecil untuk foto produk.
- `foto/metadata.json` **tidak ada**.
- Belum dikirim ke qc: syarat KONTEN_FOTO → QC_FOTO (10 foto + metadata.json) belum terpenuhi.

## Brief untuk creative
- **Area:** hanya `batch/batch-uji-head-1/foto/` (F01–F10 + `metadata.json`). Jangan sentuh `status.json`, `qc.md`, atau `scripts/`.
- **Batas:** buat dengan `python3 scripts/gambar.py --master .. --prompts prompts.txt --batch batch/batch-uji-head-1`. Produk harus sama dengan `brain/product-lock/CONTOH-KOKO-01.md` (navy, lengan panjang, kerah shanghai, bordir dada kiri). Tanpa teks harga. Tidak memakai model berbayar. Kalau semua provider gagal, biarkan `gambar.py` keluar dengan WAITING_FOTO dan laporkan apa adanya.
- **Syarat lulus:**
  1. `ls foto/` menunjukkan tepat 10 foto F01–F10, masing-masing > 10 KB.
  2. F01–F09 yang sekarang < 10 KB dibuat ulang atau diganti.
  3. `foto/metadata.json` ada, satu entri per foto (id, provider, model, prompt, waktu), termasuk percobaan gagal.
  4. Laporan menyebut jumlah file dan ukuran yang benar-benar ada, bukan perkiraan.
