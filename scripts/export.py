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
        return [{h: ("" if v is None else str(v)) for h, v in zip(head, r)} for r in it
                if any(v is not None for v in r)]
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def buang_data_pembeli(rows):
    return [{k: v for k, v in r.items() if not any(w in _norm(k) for w in KATA_PEMBELI)} for r in rows]


def angka(s):
    """'Rp 125.000' / '125.000,00' / '7' -> int. Kosong atau '-' -> None (tidak ditebak)."""
    if s is None:
        return None
    s = re.sub(r"[^\d,.\-]", "", str(s)).strip()
    if s in ("", "-"):
        return None
    if re.fullmatch(r"-?\d+\.\d{1,2}", s):  # gaya Excel: 125000.0
        return round(float(s))
    s = s.split(",")[0].replace(".", "")  # gaya Indonesia: titik ribuan, koma desimal
    return int(s) if s not in ("", "-") else None


def _tanggal(s):
    s = str(s).strip()
    for f, n in (("%Y-%m-%d", 10), ("%d-%m-%Y", 10), ("%d/%m/%Y", 10)):
        try:
            return datetime.datetime.strptime(s[:n], f).date()
        except ValueError:
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


def ringkas_per_sku(pesanan, stok, hpp, hari_ini):
    pesanan = _ambil(buang_data_pembeli(pesanan), "pesanan")
    stok = _ambil(buang_data_pembeli(stok), "stok")
    hpp = _ambil(hpp, "hpp")

    terjual, terakhir, tgl_semua = {}, {}, []
    for p in pesanan:
        t = _tanggal(p["tanggal"])
        if t:
            tgl_semua.append(t)
        if "batal" in p.get("status", "").lower() or not t:
            continue
        sku = p["sku"].strip()
        terjual[sku] = terjual.get(sku, 0) + (angka(p["jumlah"]) or 0)
        terakhir[sku] = max(terakhir.get(sku, t), t)
    awal_data = min(tgl_semua) if tgl_semua else None

    peta_hpp, hpp_dobel = {}, set()
    for h in hpp:
        sku, nilai = h["sku"].strip(), angka(h["hpp"])
        if sku in peta_hpp and peta_hpp[sku] != nilai:
            hpp_dobel.add(sku)
        peta_hpp[sku] = nilai

    hasil = {}
    for s in stok:
        sku = s["sku"].strip()
        if not sku:
            continue
        if sku in hasil:  # SKU dobel: dijumlah, tapi ditandai dan tidak diskor sampai manusia cek
            hasil[sku]["stok"] = (hasil[sku]["stok"] or 0) + (angka(s["stok"]) or 0)
            hasil[sku]["_dobel"] = True
            continue
        hasil[sku] = {"sku": sku, "nama": s["nama"].strip(), "stok": angka(s["stok"]),
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
