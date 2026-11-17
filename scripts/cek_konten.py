"""Cek kalender konten sebelum qc (aturan: brain/aturan-konten.md).

  python3 scripts/cek_konten.py --kalender batch/<id>/kalender-konten.csv --produk brain/produk.csv \\
      [--listing batch/*/listing.csv ...]
Cek: kolom & nilai sah, tanggal valid dan berurutan wajar, hook ≤ 100 karakter, naskah tidak kosong, SKU dikenal,
klaim terlarang (sama dengan cek_listing.py) kecuali tertulis di fakta produk, harga yang ditampilkan = harga akhir
di listing (kalau --listing diberikan; tanpa listing, harga apa pun ditandai).
Exit 0 = LULUS, 1 = ada masalah (JSON), 2 = input salah.
"""
import argparse, csv, datetime, json, re, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import angka, _sku
from cek_listing import KLAIM_TERLARANG, _baca

KOLOM = ["tanggal", "platform", "format", "pilar", "sku", "hook", "naskah", "cta", "tagar", "aset", "harga_ditampilkan"]
PLATFORM = {"tiktok", "instagram", "shopee-video"}
FORMAT = {"slideshow", "talking-head", "close-up", "pov", "try-on", "carousel"}
PILAR = {"produk", "momen", "cara-pakai", "toko"}
MAKS_HOOK = 100
MAKS_TAGAR = 8


def cek(kalender, produk, listing=None):
    if not kalender:
        raise ValueError("kalender-konten.csv kosong")
    kurang = [k for k in KOLOM if k not in kalender[0]]
    if kurang:
        raise ValueError(f"kolom wajib tidak ada: {kurang}")
    fakta = {_sku(p["sku"]): str(p.get("fakta_boleh_diklaim", "")).lower() for p in produk}
    harga_ok = {}
    for r in listing or []:
        harga_ok.setdefault(_sku(r["sku"]), set()).add(angka(r["harga_akhir"]))
    hasil, per_hari = [], {}
    for i, r in enumerate(kalender, start=2):
        m = []
        try:
            tgl = datetime.date.fromisoformat(str(r["tanggal"]).strip())
            kunci = (tgl, r["platform"].strip().lower())
            per_hari[kunci] = per_hari.get(kunci, 0) + 1
            if per_hari[kunci] == 3:
                m.append(f"lebih dari 2 konten di {r['platform']} pada {tgl}")
        except ValueError:
            m.append(f"tanggal tidak valid (YYYY-MM-DD): {r['tanggal']!r}")
        for kolom, sah in (("platform", PLATFORM), ("format", FORMAT), ("pilar", PILAR)):
            if str(r[kolom]).strip().lower() not in sah:
                m.append(f"{kolom} {r[kolom]!r} tidak dikenal ({', '.join(sorted(sah))})")
        hook = str(r["hook"]).strip()
        if not hook:
            m.append("hook kosong")
        elif len(hook) > MAKS_HOOK:
            m.append(f"hook {len(hook)} karakter (maks {MAKS_HOOK})")
        if not str(r["naskah"]).strip():
            m.append("naskah kosong")
        tagar = re.findall(r"#\w+", str(r["tagar"]))
        if len(tagar) > MAKS_TAGAR:
            m.append(f"tagar {len(tagar)} (maks {MAKS_TAGAR})")
        skus = [_sku(s) for s in str(r["sku"]).split(";") if s.strip()]
        for s in skus:
            if s not in fakta:
                m.append(f"SKU {s} tidak ada di produk.csv")
        boleh = " ".join(fakta.get(s, "") for s in skus)
        teks = " ".join(str(r[k]) for k in ("hook", "naskah", "cta", "tagar")).lower()
        for k in KLAIM_TERLARANG:
            if re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", teks) and k not in boleh:
                m.append(f"klaim tidak ada di fakta produk: {k!r}")
        harga = angka(r.get("harga_ditampilkan"))
        if harga is not None:
            sah = set().union(*(harga_ok.get(s, set()) for s in skus)) if skus else set()
            if harga not in sah:
                m.append(f"harga {harga} tidak sama dengan harga akhir di listing yang disetujui ({sorted(sah) or 'tidak ada'})")
        hasil.append({"baris": i, "tanggal": r["tanggal"], "platform": r["platform"], "masalah": m})
    return {"lulus": all(not h["masalah"] for h in hasil), "jumlah": len(hasil), "baris": hasil}


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--kalender", required=True)
    a.add_argument("--produk", required=True)
    a.add_argument("--listing", action="append", default=[])
    x = a.parse_args(argv)
    try:
        listing = [r for f in x.listing for r in _baca(f)]
        r = cek(_baca(x.kalender), _baca(x.produk), listing)
    except (ValueError, OSError, KeyError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r["lulus"] else 1


if __name__ == "__main__":
    sys.exit(main())
