"""Pilih deadstock dan beri skor prioritas (aturan: brain/aturan-deadstock.md).

Deadstock: hari_tanpa_jual >= 60 dan stok >= 5 (ASUMSI, bisa diubah lewat argumen).
Skor 0-100 = 50*modal/modal_maks + 30*umur/umur_maks + 20*stok/stok_maks; modal = stok x HPP.
SKU dengan data kurang (HPP kosong/dobel, SKU dobel, tidak pernah terjual di data) tetap didaftar tapi tidak diskor.
"""
import argparse, csv, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import angka, tulis_csv, KOLOM_OUTPUT

# TIDAK_TERJUAL_SEPANJANG_DATA: bisa produk baru di-listing, umur sebenarnya belum diketahui -> manusia cek
TANDA_DATA_KURANG = ("HPP_KOSONG", "HPP_DOBEL", "SKU_DOBEL", "STOK_KOSONG", "TIDAK_TERJUAL_SEPANJANG_DATA")


def pilih(rows, min_hari=60, min_stok=5):
    dead = [dict(r) for r in rows
            if r["stok"] is not None and r["stok"] >= min_stok
            and r["hari_tanpa_jual"] is not None and r["hari_tanpa_jual"] >= min_hari]
    lengkap = []
    for r in dead:
        kurang = r["hpp"] is None or any(t in (r.get("catatan") or "") for t in TANDA_DATA_KURANG)
        r["modal_tertahan"] = None if kurang else r["stok"] * r["hpp"]
        r["skor"] = None
        r["status"] = "DEADSTOCK_DATA_KURANG" if kurang else "DEADSTOCK"
        if not kurang:
            lengkap.append(r)
    if lengkap:
        mm = max(r["modal_tertahan"] for r in lengkap) or 1
        um = max(r["hari_tanpa_jual"] for r in lengkap) or 1
        sm = max(r["stok"] for r in lengkap) or 1
        for r in lengkap:
            r["skor"] = round(50 * r["modal_tertahan"] / mm + 30 * r["hari_tanpa_jual"] / um
                              + 20 * r["stok"] / sm, 1)
    return sorted(dead, key=lambda r: (r["skor"] is None, -(r["skor"] or 0), r["sku"]))


def baca_ringkas(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("stok", "harga", "hpp", "unit_terjual", "hari_tanpa_jual"):
            r[k] = angka(r[k])
    return rows


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ringkas", required=True)
    a.add_argument("--out", required=True)
    a.add_argument("--min-hari", type=int, default=60)
    a.add_argument("--min-stok", type=int, default=5)
    x = a.parse_args(argv)
    hasil = pilih(baca_ringkas(x.ringkas), x.min_hari, x.min_stok)
    tulis_csv(hasil, x.out, KOLOM_OUTPUT + ["modal_tertahan", "skor", "status"])
    print(f"{len(hasil)} deadstock ditulis ke {x.out}")


if __name__ == "__main__":
    sys.exit(main())
