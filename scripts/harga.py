"""Hitung harga akhir dan harga minimum (aturan: brain/aturan-harga.md).

Harga minimum: harga akhir - biaya admin >= HPP  ->  harga akhir >= HPP / (1 - admin%).
Semua uang dalam rupiah bulat. Pecahan dihitung dengan Fraction agar tidak ada galat float.
"""
import argparse, json, math, sys
from fractions import Fraction


def _persen(p, nama):
    p = Fraction(str(p))
    if not 0 <= p < 100:
        raise ValueError(f"{nama} harus 0..<100, dapat {p}")
    return p / 100


def harga_minimum(hpp, admin_persen):
    if hpp is None or hpp <= 0:
        raise ValueError("HPP kosong atau tidak valid: harga minimum tidak bisa dihitung")
    return math.ceil(Fraction(hpp) / (1 - _persen(admin_persen, "admin_persen")))


def hitung(harga_normal, hpp, admin_persen, diskon_persen=0, voucher_rp=0):
    minimum = harga_minimum(hpp, admin_persen)
    if diskon_persen < 0 or diskon_persen > 100:
        raise ValueError(f"diskon_persen harus 0..100, dapat {diskon_persen}")
    if voucher_rp < 0:
        raise ValueError("voucher_rp tidak boleh negatif")
    # harga dibulatkan ke bawah: pembeli tidak pernah membayar lebih dari hitungan
    akhir = math.floor(Fraction(harga_normal) * (1 - Fraction(str(diskon_persen)) / 100)) - voucher_rp
    if akhir <= 0:
        raise ValueError(f"harga akhir {akhir} <= 0: voucher/diskon terlalu besar")
    admin = round(Fraction(akhir) * _persen(admin_persen, "admin_persen"))
    bersih = akhir - admin
    return {
        "harga_normal": harga_normal, "diskon_persen": diskon_persen, "voucher_rp": voucher_rp,
        "harga_akhir": akhir, "biaya_admin": admin, "terima_bersih": bersih, "hpp": hpp,
        "margin_rp": bersih - hpp,
        "margin_persen": round(float(Fraction(bersih - hpp) / akhir) * 100, 1) if akhir > 0 else None,
        "harga_minimum": minimum, "lulus": akhir >= minimum,
    }


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--harga-normal", type=int, required=True)
    a.add_argument("--hpp", type=int, required=True)
    a.add_argument("--admin-persen", type=float, required=True)
    a.add_argument("--diskon-persen", type=float, default=0)
    a.add_argument("--voucher-rp", type=int, default=0)
    x = a.parse_args(argv)
    try:
        r = hitung(x.harga_normal, x.hpp, x.admin_persen, x.diskon_persen, x.voucher_rp)
    except ValueError as e:  # exit 2 = input salah; exit 1 = dihitung tapi TIDAK LULUS
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["lulus"] else 1


if __name__ == "__main__":
    sys.exit(main())
