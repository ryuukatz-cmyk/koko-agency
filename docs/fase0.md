# Fase 0 — Cek kesiapan (2026-11-10)

| Cek | Hasil |
|---|---|
| ffmpeg / ffprobe / python3 | Ada (`/usr/bin/ffmpeg`, `/usr/bin/ffprobe`, Python 3.13.18) |
| Google Drive `Koko Agency/input/` | Tersambung. Isi: 1 file `Workbook-Peserta-Workshop-DIMENSI-Labs_ISI_AI_Content_Agent.docx` (sudah dibaca). Belum ada: export Shopee, file HPP, foto master. Folder `Koko Agency/output/` belum ada. |
| Dokumentasi Gemini | `ai.google.dev/gemini-api/docs/*` dialihkan (301) ke `aistudio.google.com`, yang **diblokir** proxy (403). Nama model diambil dari endpoint resmi `GET /v1beta/models`. |
| Model gambar tersedia | `gemini-3.1-flash-image` (Nano Banana 2, stabil, terbaru), `gemini-3.1-flash-lite-image`, `gemini-3-pro-image`, `gemini-2.5-flash-image`, + versi preview |
| Uji generate 1 gambar | **GAGAL** — HTTP 429 `RESOURCE_EXHAUSTED`: "Quota exceeded for metric generate_content_free_tier_requests, limit: 0, model: gemini-3.1-flash-image". Sama untuk semua model gambar. |
| Key Gemini | Berfungsi: model teks `gemini-flash-lite-latest` menjawab HTTP 200. |

Arti: model gambar tidak punya kuota gratis (limit 0). Perlu billing aktif di project Google Cloud pemilik API key.
