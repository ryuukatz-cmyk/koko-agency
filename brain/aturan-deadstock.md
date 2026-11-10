# Aturan deadstock

- Deadstock = **tidak terjual ≥ 60 hari DAN stok ≥ 5**. (ASUMSI — default aman, belum dikonfirmasi pemilik)
- "Hari tanpa jual" = hari ini − tanggal pesanan terakhir yang tidak batal. Kalau SKU tidak pernah terjual di data,
  dipakai hari sejak pesanan tertua di export, dan ditandai `TIDAK_TERJUAL_SEPANJANG_DATA`.
- Angka/tanggal export yang ambigu atau tidak terbaca → script berhenti dengan pesan error (tidak ditebak).
- Pesanan berstatus "Batal"/"Dibatalkan" tidak dihitung terjual. (ASUMSI)
- Skor prioritas 0–100: `50·modal/modal_maks + 30·umur/umur_maks + 20·stok/stok_maks`, modal = stok × HPP.
- Data kurang (`HPP_KOSONG`, `HPP_DOBEL`, `SKU_DOBEL`, `STOK_KOSONG`, `TIDAK_TERJUAL_SEPANJANG_DATA` — bisa jadi produk baru) → tetap didaftar sebagai `DEADSTOCK_DATA_KURANG`, tidak diskor,
  diserahkan ke manusia. Angka yang kosong tidak boleh diisi tebakan.
- Script: `scripts/export.py` lalu `scripts/deadstock.py`.
