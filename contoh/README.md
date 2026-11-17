# Data CONTOH (palsu)

Untuk latihan agent dan demo, bukan data toko asli. Dibuat ulang dengan `python3 contoh/buat_contoh.py`.

| Isi | Path | Catatan |
|---|---|---|
| Stok gudang | `input/1-stok-gudang/stok-gudang.csv` | 4 SKU; format sama dengan lembar di Drive |
| HPP | `input/2-hpp/hpp.csv` | `CONTOH-KOKO-MARUN` sengaja kosong → harus jadi DATA_KURANG |
| Info produk | `input/3-info-produk/info-produk.csv` | kolom `fakta_boleh_diklaim` = batas klaim copy |
| Foto master | `input/4-foto-master/<SKU>/depan.png`, `detail-bordir.png` | ilustrasi, latar polos (putih → latar abu supaya bisa dipotong) |
| Product Lock | `product-lock/<SKU>.md` | contoh isian lengkap |
| Brand visual | `brand-visual.md` | contoh isian `brain/brand-visual.md` |

Coba: `python3 scripts/demo.py --out demo-out` (offline) atau `--flux` di environment koko (latar & foto scene dari FLUX nyata).
