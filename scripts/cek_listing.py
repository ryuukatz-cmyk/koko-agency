"""Cek listing.csv sebelum qc: panjang judul, kata kunci di judul, klaim terlarang, harga minimum, harga coret.

Aturan: brain/aturan-listing.md, brain/aturan-shopee.md, brain/aturan-tiktokshop.md, brain/aturan-harga.md.
Kolom listing.csv: sku,platform,judul,deskripsi,harga_normal,harga_coret,harga_akhir,taktik,kata_kunci,caption_video
  platform    shopee | tiktok (satu baris per SKU per platform)
  harga_coret harga coret yang tampil di toko; KOSONG kalau tidak ada. Mode toko-baru wajib kosong.
  kata_kunci  dipisah ";" — kata kunci pertama = kata kunci utama, wajib ada di judul.

  python3 scripts/cek_listing.py --listing batch/<id>/listing.csv --produk brain/produk.csv \\
      --admin-persen 10 --mode toko-baru
  --admin-persen boleh per platform: shopee=10,tiktok=8
Exit 0 = LULUS, 1 = ada masalah (lihat JSON), 2 = input salah.
"""
import argparse, csv, json, re, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import angka, _sku
from harga import harga_minimum

PLATFORM = ("shopee", "tiktok")
# ASUMSI — cek batas terbaru di Seller Centre / TikTok Shop Seller Center, lalu ubah di sini dan di aturan-listing.md
MAKS_JUDUL = {"shopee": 100, "tiktok": 255}
MIN_JUDUL = 25
# klaim yang hanya boleh muncul kalau tertulis di fakta_boleh_diklaim produk itu
KLAIM_TERLARANG = ["termurah", "terbaik", "terlaris", "best seller", "bestseller", "original 100%", "100% original",
                   "premium", "anti luntur", "tidak luntur", "garansi", "stok terakhir", "limited", "paling",
                   "no.1", "nomor 1", "adem seharian", "pasti adem"]
KOLOM_WAJIB = ["sku", "platform", "judul", "deskripsi", "harga_normal", "harga_akhir", "kata_kunci"]


def _admin(teks):
    teks = str(teks).strip()
    if "=" not in teks:
        return {p: float(teks) for p in PLATFORM}
    hasil = {}
    for bagian in teks.split(","):
        p, _, v = bagian.partition("=")
        if p.strip().lower() not in PLATFORM:
            raise ValueError(f"--admin-persen: platform tidak dikenal {p!r}")
        hasil[p.strip().lower()] = float(v)
    kurang = [p for p in PLATFORM if p not in hasil]
    if kurang:
        raise ValueError(f"--admin-persen: belum ada nilai untuk {kurang}")
    return hasil


def _baca(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def cek(listing, produk, admin, mode):
    if not listing:
        raise ValueError("listing.csv kosong")
    kurang = [k for k in KOLOM_WAJIB if k not in listing[0]]
    if kurang:
        raise ValueError(f"listing.csv: kolom wajib tidak ada: {kurang}")
    data = {_sku(p["sku"]): p for p in produk}
    hasil, dilihat = [], set()
    for i, r in enumerate(listing, start=2):  # baris 1 = header
        sku, platform = _sku(r["sku"]), str(r["platform"]).strip().lower()
        masalah = []
        if (sku, platform) in dilihat:
            masalah.append("baris dobel untuk SKU+platform ini")
        dilihat.add((sku, platform))
        if platform not in PLATFORM:
            hasil.append({"baris": i, "sku": sku, "platform": platform, "masalah": [f"platform harus {PLATFORM}"]})
            continue
        p = data.get(sku)
        if not p:
            hasil.append({"baris": i, "sku": sku, "platform": platform, "masalah": ["SKU tidak ada di produk.csv"]})
            continue

        judul = re.sub(r"\s+", " ", str(r["judul"])).strip()
        if not MIN_JUDUL <= len(judul) <= MAKS_JUDUL[platform]:
            masalah.append(f"panjang judul {len(judul)} (harus {MIN_JUDUL}-{MAKS_JUDUL[platform]})")
        if judul.isupper():
            masalah.append("judul huruf kapital semua")
        kunci = [k.strip().lower() for k in str(r["kata_kunci"]).split(";") if k.strip()]
        if not kunci:
            masalah.append("kata_kunci kosong")
        elif kunci[0] not in judul.lower():
            masalah.append(f"kata kunci utama {kunci[0]!r} tidak ada di judul")
        if not str(r["deskripsi"]).strip():
            masalah.append("deskripsi kosong")

        fakta = str(p.get("fakta_boleh_diklaim", "")).lower()
        teks = " ".join(str(r.get(k, "")) for k in ("judul", "deskripsi", "caption_video")).lower()
        for k in KLAIM_TERLARANG:
            if re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", teks) and k not in fakta:
                masalah.append(f"klaim tidak ada di fakta produk: {k!r}")

        normal, akhir, coret = angka(r["harga_normal"]), angka(r["harga_akhir"]), angka(r.get("harga_coret"))
        hpp = angka(p.get("hpp"))
        if not akhir or not normal:
            masalah.append("harga_normal/harga_akhir kosong")
        elif not hpp:
            masalah.append("HPP kosong di produk.csv: harga minimum tidak bisa dicek")
        else:
            minimum = harga_minimum(hpp, admin[platform])
            if akhir < minimum:
                masalah.append(f"harga_akhir {akhir} di bawah harga minimum {minimum}")
            if akhir > normal:
                masalah.append("harga_akhir lebih besar dari harga_normal")
        if coret is not None:
            if mode == "toko-baru":
                masalah.append("mode toko-baru: harga coret dilarang (barang belum pernah dijual dengan harga itu)")
            elif normal and coret != normal:
                masalah.append(f"harga_coret {coret} harus sama dengan harga_normal {normal} yang benar-benar berlaku")
        hasil.append({"baris": i, "sku": sku, "platform": platform, "masalah": masalah})
    return {"lulus": all(not h["masalah"] for h in hasil), "mode": mode, "baris": hasil}


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--listing", required=True)
    a.add_argument("--produk", required=True, help="brain/produk.csv (hpp, fakta_boleh_diklaim)")
    a.add_argument("--admin-persen", required=True)
    a.add_argument("--mode", choices=["toko-baru", "deadstock"], required=True)
    x = a.parse_args(argv)
    try:
        r = cek(_baca(x.listing), _baca(x.produk), _admin(x.admin_persen), x.mode)
    except (ValueError, OSError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r["lulus"] else 1


if __name__ == "__main__":
    sys.exit(main())
