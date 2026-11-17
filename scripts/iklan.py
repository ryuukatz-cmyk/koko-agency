"""Rencana iklan (Shopee Ads / TikTok Shop Ads): batas aman biaya iklan dihitung dari margin. Aturan: brain/aturan-iklan.md.

Agent hanya MENGUSULKAN. Pemilik yang memasang dan membayar iklan. Script tidak menghubungi platform mana pun.

Rumus per SKU per platform (uang dalam rupiah):
  margin          = harga akhir - biaya admin - HPP                       (sebelum iklan)
  jatah_iklan     = margin x porsi_margin                                 (bagian margin yang rela dipakai iklan)
  ROAS impas      = harga akhir / margin           (di bawah ini iklan pasti rugi)
  ROAS target     = harga akhir / jatah_iklan      (target minimal di dashboard iklan)
  bid maks / klik = jatah_iklan x CR               (CR = konversi klik->pesanan, ASUMSI toko baru 2%)
  batas klik tanpa pesanan = ceil(2 / CR)          (setelah itu jeda/ganti kata kunci)
Budget harian total dibagi ke SKU sebanding margin, dibulatkan ke bawah per Rp1.000.

  python3 scripts/iklan.py --listing batch/<id>/listing.csv [--listing ...] --produk brain/produk.csv \\
      --admin-persen shopee=10,tiktok=10 --budget-harian 50000 [--cr 0.02] [--porsi-margin 0.5] --out iklan.csv
Exit 0 = rencana dibuat, 1 = tidak ada SKU yang layak diiklankan, 2 = input salah.
"""
import argparse, csv, json, math, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import angka, _sku
from harga import hitung
from cek_listing import _admin, _baca, PLATFORM

KOLOM = ["sku", "platform", "harga_akhir", "hpp", "margin", "jatah_iklan_per_pesanan", "roas_impas", "roas_target",
         "acos_maks_persen", "bid_maks_per_klik", "budget_harian", "batas_klik_tanpa_pesanan", "status", "catatan"]


def rencana(listing, produk, admin, budget_harian, cr=0.02, porsi=0.5):
    if not 0 < cr < 1:
        raise ValueError("cr harus 0..1 (mis. 0.02 = 2%)")
    if not 0 < porsi <= 1:
        raise ValueError("porsi_margin harus 0..1")
    if budget_harian < 0:
        raise ValueError("budget harian tidak boleh negatif")
    hpp = {_sku(p["sku"]): angka(p.get("hpp")) for p in produk}
    baris = []
    for r in listing:
        sku, platform = _sku(r["sku"]), str(r["platform"]).strip().lower()
        if platform not in PLATFORM:
            raise ValueError(f"platform tidak dikenal: {platform!r}")
        akhir = angka(r["harga_akhir"])
        b = {"sku": sku, "platform": platform, "harga_akhir": akhir, "hpp": hpp.get(sku), "catatan": ""}
        if not akhir or not hpp.get(sku):
            b.update(status="TIDAK_DIIKLANKAN", catatan="harga akhir / HPP kosong")
            baris.append(b)
            continue
        h = hitung(akhir, hpp[sku], admin[platform])
        margin = h["margin_rp"]
        b["margin"] = margin
        if margin <= 0:
            b.update(status="TIDAK_DIIKLANKAN", catatan="margin <= 0: setiap pesanan dari iklan pasti rugi")
            baris.append(b)
            continue
        jatah = math.floor(margin * porsi)
        b.update(jatah_iklan_per_pesanan=jatah, roas_impas=round(akhir / margin, 2),
                 roas_target=round(akhir / jatah, 2) if jatah else None,
                 acos_maks_persen=round(100 * jatah / akhir, 1),
                 bid_maks_per_klik=math.floor(jatah * cr), batas_klik_tanpa_pesanan=math.ceil(2 / cr),
                 status="LAYAK")
        if b["bid_maks_per_klik"] < 100:  # ASUMSI: bid di bawah ~Rp100 hampir tidak dapat tayang
            b.update(status="LAYAK_TERBATAS", catatan="bid maks sangat kecil; utamakan voucher/organik")
        baris.append(b)

    layak = [b for b in baris if b["status"].startswith("LAYAK")]
    total_margin = sum(b["margin"] for b in layak)
    for b in layak:
        b["budget_harian"] = (budget_harian * b["margin"] // total_margin) // 1000 * 1000 if total_margin else 0
        if b["budget_harian"] < b["bid_maks_per_klik"] * 10:
            b["catatan"] = (b["catatan"] + "; " if b["catatan"] else "") + "budget < 10 klik/hari: data lambat terkumpul"
    return {"asumsi": {"cr": cr, "porsi_margin": porsi, "budget_harian_total": budget_harian},
            "terpakai": sum(b.get("budget_harian", 0) for b in layak), "baris": baris,
            "ada_yang_layak": bool(layak)}


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--listing", required=True, action="append", help="boleh diulang untuk beberapa batch")
    a.add_argument("--produk", required=True)
    a.add_argument("--admin-persen", required=True)
    a.add_argument("--budget-harian", type=int, required=True, help="total rupiah per hari untuk semua SKU")
    a.add_argument("--cr", type=float, default=0.02)
    a.add_argument("--porsi-margin", type=float, default=0.5)
    a.add_argument("--out", required=True)
    x = a.parse_args(argv)
    try:
        listing = [r for f in x.listing for r in _baca(f)]
        r = rencana(listing, _baca(x.produk), _admin(x.admin_persen), x.budget_harian, x.cr, x.porsi_margin)
    except (ValueError, OSError, KeyError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    with open(x.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KOLOM, extrasaction="ignore")
        w.writeheader()
        for b in r["baris"]:
            w.writerow({k: "" if b.get(k) is None else b.get(k) for k in KOLOM})
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["ada_yang_layak"] else 1


if __name__ == "__main__":
    sys.exit(main())
