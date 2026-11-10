# Format video

(ASUMSI — default aman)

- 9:16, 1080×1920, H.264, 30 fps, **15–30 detik**, tanpa musik/audio.
- Mode default (gratis, otomatis): slideshow dari foto yang LULUS QC — zoom pelan, transisi fade 0,5 dtk, latar putih.
- Mode opsional: klip Google Flow dari Drive `Koko Agency/output/<batch>/flow/` (V01..V10), dipotong dan digabung.
  Klip harus berpasangan dengan foto dan prompt: F01 ↔ P01 ↔ V01.
- Teks: nama produk (atas), harga akhir yang SUDAH DISETUJUI (bawah). Tidak ada teks lain tanpa persetujuan.
- Nama file final: `batch/<id>/video/final/<id>_FINAL.mp4`.
- Script: `scripts/video.py` (sudah termasuk `--cek` dengan ffprobe).
