"""Ukur hasil toko baru (status DIUKUR): export pesanan Shopee sejak tayang vs stok awal di katalog.

Data pembeli dibuang saat dibaca (sama seperti scripts/export.py) dan tidak pernah ditulis.
Uang masuk = unit x harga akhir di listing.csv (platform shopee) - biaya admin. Pesanan "Batal" tidak dihitung.
Nama kolom export = ASUMSI (lihat KOLOM di export.py); TikTok Shop export belum didukung.

  python3 scripts/ukur.py --pesanan data/mentah/pesanan.xlsx --katalog data/katalog.csv \\
      --listing batch/<id>/listing.csv [--listing ..] --admin-persen 10 --sejak YYYY-MM-DD --hari-ini YYYY-MM-DD \\
      --out batch/<id>/hasil.csv
Exit 0 = dihitung, 2 = input salah (kolom tidak ada, tanggal tidak terbaca).
"""
import argparse, csv, datetime, json, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import angka, baca_tabel, buang_data_pembeli, _ambil, _tanggal, _sku, tulis_csv
from harga import hitung

KOLOM_OUTPUT = ["sku", "stok_awal", "unit_terjual", "unit_batal", "sisa_stok_perkiraan", "harga_akhir",
                "uang_masuk_bersih", "modal_kembali_persen", "per_minggu", "catatan"]


def ukur(pesanan, katalog, listing, admin_persen, sejak, hari_ini):
    pesanan = _ambil(buang_data_pembeli(pesanan), "pesanan")
    rusak = [p["tanggal"] for p in pesanan if not _tanggal(p["tanggal"])]
    if rusak:
        raise ValueError(f"{len(rusak)} baris pesanan dengan tanggal tidak terbaca, contoh: {rusak[:3]}")
    harga = {}
    for r in listing:
        if str(r.get("platform", "shopee")).strip().lower() == "shopee":
            harga[_sku(r["sku"])] = angka(r["harga_akhir"])
    out = []
    for k in katalog:
        sku = _sku(k["sku"])
        stok, hpp = angka(k.get("stok")), angka(k.get("hpp"))
        terjual = batal = 0
        minggu = {}
        for p in pesanan:
            t = _tanggal(p["tanggal"])
            if _sku(p["sku"]) != sku or not (sejak <= t <= hari_ini):
                continue
            n = angka(p["jumlah"]) or 0
            if "batal" in str(p.get("status", "")).lower():
                batal += n
                continue
            terjual += n
            th, mg, _ = t.isocalendar()
            kunci = f"{th}-W{mg:02d}"
            minggu[kunci] = minggu.get(kunci, 0) + n
        catatan = []
        h = harga.get(sku)
        bersih = None
        if h and hpp:
            r = hitung(h, hpp, admin_persen)
            bersih = terjual * r["terima_bersih"]
        else:
            catatan.append("harga akhir/HPP kosong: uang masuk tidak dihitung")
        if stok is not None and terjual > stok:
            catatan.append("terjual melebihi stok awal: cek stok gudang/restock")
        out.append({"sku": sku, "stok_awal": stok, "unit_terjual": terjual, "unit_batal": batal,
                    "sisa_stok_perkiraan": None if stok is None else stok - terjual, "harga_akhir": h,
                    "uang_masuk_bersih": bersih,
                    "modal_kembali_persen": round(100 * terjual / stok, 1) if stok else None,
                    "per_minggu": json.dumps(dict(sorted(minggu.items()))), "catatan": ";".join(catatan)})
    return sorted(out, key=lambda r: -r["unit_terjual"])


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--pesanan", required=True)
    a.add_argument("--katalog", required=True)
    a.add_argument("--listing", required=True, action="append")
    a.add_argument("--admin-persen", type=float, required=True)
    a.add_argument("--sejak", required=True, help="tanggal tayang YYYY-MM-DD")
    a.add_argument("--hari-ini", required=True)
    a.add_argument("--out", required=True)
    x = a.parse_args(argv)
    try:
        with open(x.katalog, newline="", encoding="utf-8") as f:
            katalog = list(csv.DictReader(f))
        listing = []
        for p in x.listing:
            with open(p, newline="", encoding="utf-8-sig") as f:
                listing += list(csv.DictReader(f))
        rows = ukur(baca_tabel(x.pesanan), katalog, listing, x.admin_persen,
                    datetime.date.fromisoformat(x.sejak), datetime.date.fromisoformat(x.hari_ini))
    except (ValueError, OSError, KeyError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    tulis_csv(rows, x.out, KOLOM_OUTPUT)
    print(json.dumps({"sku": len(rows), "unit_terjual": sum(r["unit_terjual"] for r in rows),
                      "uang_masuk_bersih": sum(r["uang_masuk_bersih"] or 0 for r in rows), "out": x.out},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
