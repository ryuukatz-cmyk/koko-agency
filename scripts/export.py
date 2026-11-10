"""Baca export Shopee (csv/xlsx), buang kolom data pembeli, ringkas per SKU.

Data mentah hanya dibaca dari data/mentah/ (di-.gitignore). Output hanya berisi kolom per SKU,
tidak pernah berisi data pembeli.
Nama kolom Shopee di bawah adalah ASUMSI dan dicek dengan export asli di Fase 4.
"""
import argparse, csv, datetime, re, sys

# kolom yang mengandung salah satu kata ini dianggap data pembeli dan dibuang
KATA_PEMBELI = ["pembeli", "penerima", "telepon", "no. hp", "nomor hp", "handphone", "alamat",
                "kota", "kabupaten", "kecamatan", "provinsi", "kode pos", "email", "username"]

# alias nama kolom (ASUMSI dari format export Shopee Indonesia)
KOLOM = {
    "pesanan": {"sku": ["nomor referensi sku", "sku", "sku induk"],
                "tanggal": ["waktu pesanan dibuat", "tanggal pesanan"],
                "jumlah": ["jumlah", "jumlah produk"],
                "status": ["status pesanan"]},
    "stok": {"sku": ["sku", "nomor referensi sku", "sku variasi"],
             "nama": ["nama produk"],
             "stok": ["stok"],
             "harga": ["harga", "harga awal"]},
    "hpp": {"sku": ["sku", "nomor referensi sku"], "hpp": ["hpp", "harga pokok", "modal"]},
}
WAJIB = {"pesanan": ["sku", "tanggal", "jumlah"], "stok": ["sku", "nama", "stok", "harga"], "hpp": ["sku", "hpp"]}
CONTOH_NAMA = {"sku": "SKU", "tanggal": "Waktu Pesanan Dibuat", "jumlah": "Jumlah", "nama": "Nama Produk",
               "stok": "Stok", "harga": "Harga", "hpp": "HPP"}
KOLOM_OUTPUT = ["sku", "nama", "stok", "harga", "hpp", "unit_terjual", "terakhir_terjual",
                "hari_tanpa_jual", "catatan"]


def _norm(k):
    return re.sub(r"\s+", " ", str(k)).strip().lower()


def baca_tabel(path):
    if str(path).lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True).active
        it = ws.iter_rows(values_only=True)
        head = [str(h) if h is not None else "" for h in next(it)]
        # angka dibiarkan angka: mengubahnya ke teks dulu bisa merusak desimal (83333.333 -> 83333333)
        return [{h: ("" if v is None else v) for h, v in zip(head, r)} for r in it
                if any(v is not None for v in r)]
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def buang_data_pembeli(rows):
    return [{k: v for k, v in r.items() if not any(w in _norm(k) for w in KATA_PEMBELI)} for r in rows]


def angka(s):
    """Rupiah/jumlah -> int. 'Rp 125.000', '125.000,00', '90,000', 83333.3 (xlsx) -> int. Kosong/'-' -> None.

    Rupiah tidak punya 3 angka desimal, jadi kelompok 3 digit setelah pemisah = ribuan.
    Format yang tetap ambigu -> ValueError (tidak ditebak).
    """
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return round(s)
    asli, s = s, re.sub(r"[^\d,.\-]", "", str(s)).strip()
    if s in ("", "-"):
        return None
    if "," in s and "." in s:  # pemisah yang muncul terakhir = desimal
        des = "," if s.rfind(",") > s.rfind(".") else "."
        bulat, pecahan = s.rsplit(des, 1)
        s = bulat.replace("," if des == "." else ".", "") + "." + pecahan
    elif "," in s or "." in s:
        sep = "," if "," in s else "."
        bagian = s.split(sep)
        if len(bagian) > 1 and all(len(b) == 3 for b in bagian[1:]) and 1 <= len(bagian[0].lstrip("-")) <= 3:
            s = "".join(bagian)
        elif len(bagian) == 2:
            s = bagian[0] + "." + bagian[1]
        else:
            raise ValueError(f"angka ambigu, cek manual: {asli!r}")
    try:
        return round(float(s))
    except ValueError:
        raise ValueError(f"angka ambigu, cek manual: {asli!r}") from None


def _tanggal(s):
    if isinstance(s, datetime.datetime):
        return s.date()
    if isinstance(s, datetime.date):
        return s
    bagian = str(s).strip().split()
    for f in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"):  # ASUMSI: hari sebelum bulan
        try:
            return datetime.datetime.strptime(bagian[0], f).date()
        except (ValueError, IndexError):
            pass
    return None


def _ambil(rows, jenis):
    """Petakan nama kolom asli -> nama internal. Error yang jelas kalau kolom wajib tidak ada."""
    if not rows:
        return []
    ada = {_norm(k): k for k in rows[0]}
    peta = {}
    for internal, alias in KOLOM[jenis].items():
        asli = next((ada[a] for a in alias if a in ada), None)
        if asli:
            peta[internal] = asli
    kurang = [k for k in WAJIB[jenis] if k not in peta]
    if kurang:
        raise ValueError(f"Export {jenis}: kolom wajib tidak ditemukan: "
                         + ", ".join(f"{CONTOH_NAMA[k]} ({k})" for k in kurang)
                         + f". Kolom yang ada: {list(rows[0])}")
    return [{i: r.get(a, "") for i, a in peta.items()} for r in rows]


def _sku(v):
    return str(v).strip().upper()


def ringkas_per_sku(pesanan, stok, hpp, hari_ini):
    pesanan = _ambil(buang_data_pembeli(pesanan), "pesanan")
    stok = _ambil(buang_data_pembeli(stok), "stok")
    hpp = _ambil(hpp, "hpp")

    rusak = [p["tanggal"] for p in pesanan if not _tanggal(p["tanggal"])]
    if rusak:  # pesanan yang dilewati diam-diam bisa membuat SKU laku tampak deadstock
        raise ValueError(f"{len(rusak)} baris pesanan dengan tanggal tidak terbaca, contoh: {rusak[:3]}")
    terjual, terakhir, tgl_semua = {}, {}, []
    for p in pesanan:
        t = _tanggal(p["tanggal"])
        tgl_semua.append(t)
        if "batal" in str(p.get("status", "")).lower():
            continue
        sku = _sku(p["sku"])
        terjual[sku] = terjual.get(sku, 0) + (angka(p["jumlah"]) or 0)
        terakhir[sku] = max(terakhir.get(sku, t), t)
    awal_data = min(tgl_semua) if tgl_semua else None

    peta_hpp, hpp_dobel = {}, set()
    for h in hpp:
        sku, nilai = _sku(h["sku"]), angka(h["hpp"])
        if sku in peta_hpp and peta_hpp[sku] != nilai:
            hpp_dobel.add(sku)
        peta_hpp[sku] = nilai

    hasil = {}
    for s in stok:
        sku = _sku(s["sku"])
        if not sku:
            continue
        if sku in hasil:  # SKU dobel: dijumlah, tapi ditandai dan tidak diskor sampai manusia cek
            hasil[sku]["stok"] = (hasil[sku]["stok"] or 0) + (angka(s["stok"]) or 0)
            hasil[sku]["_dobel"] = True
            continue
        hasil[sku] = {"sku": sku, "nama": str(s["nama"]).strip(), "stok": angka(s["stok"]),
                      "harga": angka(s["harga"]), "_dobel": False}

    out = []
    for sku, r in hasil.items():
        catatan = []
        nilai_hpp = None if sku in hpp_dobel else peta_hpp.get(sku)
        if sku in hpp_dobel:
            catatan.append("HPP_DOBEL")
        elif nilai_hpp is None:
            catatan.append("HPP_KOSONG")
        if r.pop("_dobel"):
            catatan.append("SKU_DOBEL")
        if r["stok"] is None:
            catatan.append("STOK_KOSONG")
        if sku in terakhir:
            hari = (hari_ini - terakhir[sku]).days
        elif awal_data:
            hari = (hari_ini - awal_data).days
            catatan.append("TIDAK_TERJUAL_SEPANJANG_DATA")
        else:
            hari = None
            catatan.append("TANPA_DATA_PESANAN")
        out.append({**r, "hpp": nilai_hpp, "unit_terjual": terjual.get(sku, 0),
                    "terakhir_terjual": terakhir[sku].isoformat() if sku in terakhir else "",
                    "hari_tanpa_jual": hari, "catatan": ";".join(catatan)})
    return out


def tulis_csv(rows, path, kolom):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=kolom, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: "" if r.get(k) is None else r.get(k) for k in kolom})


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--pesanan", required=True)
    a.add_argument("--stok", required=True)
    a.add_argument("--hpp", required=True)
    a.add_argument("--hari-ini", required=True, help="YYYY-MM-DD")
    a.add_argument("--out", required=True)
    x = a.parse_args(argv)
    rows = ringkas_per_sku(baca_tabel(x.pesanan), baca_tabel(x.stok), baca_tabel(x.hpp),
                           datetime.date.fromisoformat(x.hari_ini))
    tulis_csv(rows, x.out, KOLOM_OUTPUT)
    print(f"{len(rows)} SKU ditulis ke {x.out}")


if __name__ == "__main__":
    sys.exit(main())
