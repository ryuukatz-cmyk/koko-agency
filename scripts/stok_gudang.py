"""Mode toko baru: baca lembar stok gudang + HPP + info produk, tentukan SKU mana yang siap dibuatkan listing.

Toko baru belum punya pesanan, jadi tidak ada skor deadstock. Yang dicek:
- data lengkap (stok, HPP, harga rencana, fakta produk untuk copy),
- harga jual rencana tidak di bawah harga minimum (scripts/harga.py),
- urutan kerja: skor = 60*modal/modal_maks + 40*umur/umur_maks (ASUMSI, lihat brain/aturan-toko-baru.md),
  modal = stok x HPP, umur = hari sejak tanggal_masuk.

  python3 scripts/stok_gudang.py --stok data/mentah/stok-gudang.csv --hpp data/mentah/hpp.csv \\
      --info data/mentah/info-produk.csv --admin-persen 10 --hari-ini YYYY-MM-DD --out data/katalog.csv
Exit 0 = minimal 1 SKU SIAP, 1 = tidak ada yang SIAP, 2 = input salah (kolom wajib tidak ada, angka ambigu).
"""
import argparse, datetime, json, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import angka, baca_tabel, tulis_csv, _norm, _sku, _tanggal
from harga import harga_minimum, hitung

KOLOM = {
    "stok": {"sku": ["sku", "kode sku"], "nama": ["nama", "nama produk"], "stok": ["stok", "jumlah stok", "qty"],
             "harga": ["harga_jual_rencana", "harga jual rencana", "harga jual", "harga"],
             "tanggal": ["tanggal_masuk", "tanggal masuk", "tgl masuk"], "catatan": ["catatan"]},
    "hpp": {"sku": ["sku", "kode sku"], "hpp": ["hpp", "harga pokok", "modal"]},
    "info": {"sku": ["sku", "kode sku"], "fakta": ["fakta_boleh_diklaim", "fakta boleh diklaim", "fakta"]},
}
WAJIB = {"stok": ["sku", "nama", "stok", "harga", "tanggal"], "hpp": ["sku", "hpp"], "info": ["sku", "fakta"]}
KOLOM_OUTPUT = ["sku", "nama", "stok", "hpp", "harga_jual_rencana", "harga_minimum", "margin_rencana",
                "tanggal_masuk", "umur_stok_hari", "modal_tertahan", "skor", "status", "catatan"]


def _petakan(rows, jenis):
    if not rows:
        raise ValueError(f"lembar {jenis} kosong")
    ada = {_norm(k): k for k in rows[0]}
    peta = {i: next((ada[a] for a in alias if a in ada), None) for i, alias in KOLOM[jenis].items()}
    kurang = [k for k in WAJIB[jenis] if not peta[k]]
    if kurang:
        raise ValueError(f"lembar {jenis}: kolom wajib tidak ada: {kurang}. Kolom yang ada: {list(rows[0])}")
    return [{i: (r.get(a, "") if a else "") for i, a in peta.items()} for r in rows]


def katalog(stok, hpp, info, admin_persen, hari_ini):
    stok, hpp, info = _petakan(stok, "stok"), _petakan(hpp, "hpp"), _petakan(info, "info")

    peta_hpp, hpp_dobel = {}, set()
    for h in hpp:
        sku, nilai = _sku(h["sku"]), angka(h["hpp"])
        if sku in peta_hpp and peta_hpp[sku] != nilai:
            hpp_dobel.add(sku)
        peta_hpp[sku] = nilai
    fakta = {_sku(i["sku"]): str(i["fakta"]).strip() for i in info if _sku(i["sku"])}

    hasil, dobel = {}, set()
    for s in stok:
        sku = _sku(s["sku"])
        if not sku:
            continue
        if sku in hasil:
            dobel.add(sku)
            hasil[sku]["stok"] = (hasil[sku]["stok"] or 0) + (angka(s["stok"]) or 0)
            continue
        t = _tanggal(s["tanggal"]) if str(s["tanggal"]).strip() else None
        if str(s["tanggal"]).strip() and t is None:
            raise ValueError(f"tanggal_masuk tidak terbaca untuk {sku}: {s['tanggal']!r} (pakai YYYY-MM-DD)")
        hasil[sku] = {"sku": sku, "nama": str(s["nama"]).strip(), "stok": angka(s["stok"]),
                      "harga_jual_rencana": angka(s["harga"]), "tanggal_masuk": t.isoformat() if t else "",
                      "umur_stok_hari": (hari_ini - t).days if t else None,
                      "_catatan_pemilik": str(s.get("catatan") or "").strip()}

    out = []
    for sku, r in hasil.items():
        kurang = []
        r["hpp"] = None if sku in hpp_dobel else peta_hpp.get(sku)
        if sku in hpp_dobel:
            kurang.append("HPP_DOBEL")
        elif not r["hpp"]:
            kurang.append("HPP_KOSONG")
        if sku in dobel:
            kurang.append("SKU_DOBEL")
        if not r["stok"]:
            kurang.append("STOK_KOSONG")
        if not r["harga_jual_rencana"]:
            kurang.append("HARGA_KOSONG")
        if r["umur_stok_hari"] is None:
            kurang.append("TANGGAL_MASUK_KOSONG")
        if not fakta.get(sku):
            kurang.append("FAKTA_PRODUK_KOSONG")

        r["harga_minimum"] = r["margin_rencana"] = None
        if r["hpp"] and sku not in hpp_dobel:
            r["harga_minimum"] = harga_minimum(r["hpp"], admin_persen)
            if r["harga_jual_rencana"]:
                h = hitung(r["harga_jual_rencana"], r["hpp"], admin_persen)  # rumus sama persis dengan harga.py
                r["margin_rencana"] = h["margin_rp"]
                if not h["lulus"]:
                    kurang.append("HARGA_RENCANA_DI_BAWAH_MINIMUM")
        r["modal_tertahan"] = r["stok"] * r["hpp"] if r["stok"] and r["hpp"] and sku not in hpp_dobel else None
        r["status"] = "DATA_KURANG" if kurang else "SIAP"
        r["catatan"] = ";".join(kurang + ([f"pemilik: {r['_catatan_pemilik']}"] if r["_catatan_pemilik"] else []))
        r["skor"] = None
        out.append(r)

    siap = [r for r in out if r["status"] == "SIAP"]
    if siap:
        mm = max(r["modal_tertahan"] for r in siap) or 1
        um = max(r["umur_stok_hari"] for r in siap) or 1
        for r in siap:
            r["skor"] = round(60 * r["modal_tertahan"] / mm + 40 * max(r["umur_stok_hari"], 0) / um, 1)
    return sorted(out, key=lambda r: (r["skor"] is None, -(r["skor"] or 0), r["sku"]))


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--stok", required=True, help="lembar stok gudang (csv/xlsx)")
    a.add_argument("--hpp", required=True)
    a.add_argument("--info", required=True, help="lembar info produk (kolom fakta_boleh_diklaim)")
    a.add_argument("--admin-persen", type=float, required=True)
    a.add_argument("--hari-ini", required=True, help="YYYY-MM-DD")
    a.add_argument("--out", required=True)
    x = a.parse_args(argv)
    try:
        rows = katalog(baca_tabel(x.stok), baca_tabel(x.hpp), baca_tabel(x.info), x.admin_persen,
                       datetime.date.fromisoformat(x.hari_ini))
    except (ValueError, OSError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    tulis_csv(rows, x.out, KOLOM_OUTPUT)
    siap = [r["sku"] for r in rows if r["status"] == "SIAP"]
    print(json.dumps({"total": len(rows), "siap": siap,
                      "data_kurang": {r["sku"]: r["catatan"] for r in rows if r["status"] != "SIAP"},
                      "out": x.out}, ensure_ascii=False))
    return 0 if siap else 1


if __name__ == "__main__":
    sys.exit(main())
