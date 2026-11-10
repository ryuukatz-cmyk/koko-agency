"""Ringkas harga kompetitor (aturan: brain/aturan-kompetitor.md).

Hanya baris bersumber 'halaman' (dibuka langsung) atau 'chrome' (Claude in Chrome) yang dihitung.
'cuplikan' (potongan hasil pencarian) hanya dicatat. Baris tanpa bukti ditolak dengan alasan.
"""
import argparse, datetime, json, os, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import angka, baca_tabel

KOLOM = ["sku_kita", "platform", "toko", "judul", "harga", "harga_coret", "terjual", "rating", "link", "sumber", "dicek_pada"]
TERVERIFIKASI = {"halaman", "chrome"}
SUMBER = TERVERIFIKASI | {"cuplikan"}
HARGA_MIN_MASUK_AKAL = 1000  # "125rb" terbaca 125: bukan harga baju


def _alasan_tolak(r, hari_ini):
    if not str(r.get("link", "")).strip().startswith(("http://", "https://")):
        return "link kosong/tidak valid"
    if str(r.get("sumber", "")).strip() not in SUMBER:
        return f"sumber '{r.get('sumber')}' tidak dikenal (pakai: {', '.join(sorted(SUMBER))})"
    try:
        tgl = datetime.date.fromisoformat(str(r.get("dicek_pada", "")).strip()[:10])
    except ValueError:
        return "tanggal dicek_pada kosong/tidak valid (YYYY-MM-DD)"
    if tgl > hari_ini:
        return "tanggal dicek_pada di masa depan"
    try:
        h = angka(r.get("harga"))
    except ValueError as e:
        return f"harga ambigu: {e}"
    if h is None or h < HARGA_MIN_MASUK_AKAL:
        return f"harga tidak masuk akal: {r.get('harga')!r} (tulis lengkap, mis. Rp125.000)"
    return None


def ringkas(rows, hari_ini, min_pembanding=5, harga_kita=None):
    ditolak, harga, cuplikan, link_ada = [], [], 0, set()
    for i, r in enumerate(rows, 1):
        alasan = _alasan_tolak(r, hari_ini)
        link = str(r.get("link", "")).strip()
        if not alasan and link in link_ada:
            alasan = "link dobel (sudah dicatat)"
        if alasan:
            ditolak.append({"baris": i, "alasan": alasan})
            continue
        link_ada.add(link)
        if str(r["sumber"]).strip() in TERVERIFIKASI:
            harga.append(angka(r["harga"]))
        else:
            cuplikan += 1
    harga.sort()
    return {
        "jumlah_baris": len(rows), "terverifikasi": len(harga), "cuplikan": cuplikan, "ditolak": ditolak,
        "harga_min": harga[0] if harga else None,
        "harga_median": statistics.median_low(harga) if harga else None,  # median_low: selalu harga yang benar-benar ada
        "harga_max": harga[-1] if harga else None,
        "lebih_murah_dari_kita": sum(h < harga_kita for h in harga) if harga_kita is not None else None,
        "status": "CUKUP" if len(harga) >= min_pembanding else "DATA_KURANG",
    }


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--csv", required=True, help="batch/<id>/kompetitor.csv")
    a.add_argument("--hari-ini", required=True, help="YYYY-MM-DD")
    a.add_argument("--harga-kita", type=int, help="harga akhir kita, untuk posisi")
    x = a.parse_args(argv)
    try:
        rows = baca_tabel(x.csv)
        kurang = [k for k in KOLOM if rows and k not in rows[0]]
        if kurang:
            raise ValueError(f"kolom wajib tidak ada: {kurang}")
        r = ringkas(rows, datetime.date.fromisoformat(x.hari_ini), harga_kita=x.harga_kita)
    except (OSError, ValueError) as e:  # exit 2 = input salah
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["status"] == "CUKUP" else 1


if __name__ == "__main__":
    sys.exit(main())
