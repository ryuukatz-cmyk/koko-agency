#!/usr/bin/env bash
# Siapkan environment (cloud koko atau komputer sendiri): cek alat, pasang pustaka Python, jalankan tes cepat.
#   bash scripts/setup.sh
set -u
cd "$(dirname "$0")/.."
ok=1
for alat in python3 ffmpeg ffprobe fc-match curl git; do
  if command -v "$alat" >/dev/null 2>&1; then echo "ada   : $alat"; else echo "KURANG: $alat"; ok=0; fi
done
python3 - <<'PY' || pip install -r requirements.txt 2>/dev/null || pip install --break-system-packages -r requirements.txt
import PIL, openpyxl
print("ada   : Pillow", PIL.__version__, "/ openpyxl", openpyxl.__version__)
PY
if python3 -m unittest tests.test_harga tests.test_cek_listing tests.test_stok_gudang tests.test_dekorasi >/dev/null 2>&1; then
  echo "tes cepat: LULUS"
else
  echo "tes cepat: GAGAL (jalankan: python3 -m unittest discover -s tests -v)"; ok=0
fi
[ "$ok" = 1 ] && echo "SIAP. Berikutnya: python3 scripts/cek_cloudflare.py (uji FLUX nyata)" || echo "Belum siap: lengkapi yang KURANG di atas."
