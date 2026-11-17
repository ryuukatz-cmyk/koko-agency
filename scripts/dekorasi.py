"""Render dekorasi toko (banner, etalase, kategori) dari spesifikasi JSON. Aturan: brain/aturan-dekorasi.md.

Teks dan harga ditulis oleh KODE (bukan model gambar), jadi ejaan dan angka pasti benar.
Produk diambil dari foto master asli (scripts/komposit.py), latar dari gambar AI (scripts/latar.py) atau warna palet.

  python3 scripts/dekorasi.py --spec batch/<id>/dekorasi.json --out batch/<id>/dekorasi
Spec:
{
  "palet": {"utama": "#1F2A44", "kedua": "#F4F1E8", "aksen": "#C9A227", "teks": "#FFFFFF"},
  "font": {"judul": "aset/font/Poppins-Bold.ttf", "isi": "aset/font/Poppins-Medium.ttf"},   (opsional)
  "item": [{"id": "D01", "jenis": "banner-carousel", "tata_letak": "teks-kiri",
            "latar": "batch/<id>/dekorasi/latar/D01.png" atau null,
            "produk": ["batch/<id>/master/depan.png"], "label": "Koleksi Ramadan", "judul": "...",
            "subjudul": "...", "harga": "Rp 149.000" atau null, "cta": "Cek Etalase"}]
}
jenis: lihat UKURAN (ASUMSI) atau "ukuran": "1200x600". tata_letak: teks-kiri | teks-kanan | tengah.
Exit 0 = semua item jadi dan lolos cek, 1 = ada item yang gagal cek (lihat laporan), 2 = spec salah.
"""
import argparse, json, pathlib, sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import komposit

AKAR = pathlib.Path(__file__).resolve().parent.parent
# ASUMSI dari panduan pihak ketiga; cek di Seller Centre > Dekorasi Toko lalu ubah di sini dan di brain/aturan-dekorasi.md
UKURAN = {"banner-carousel": (1200, 600), "banner-tinggi": (1200, 900), "gambar-tunggal": (1200, 1200),
          "kategori": (800, 800), "banner-kampanye": (1200, 628)}
MAKS_KB = 2000
MAKS_SISI = 2000
KONTRAS_MIN = 4.5
FONT_DEFAULT = {"judul": AKAR / "aset/font/Poppins-Bold.ttf", "isi": AKAR / "aset/font/Poppins-Medium.ttf"}
TATA_LETAK = ("teks-kiri", "teks-kanan", "tengah")
MAKS_JUDUL = 60  # karakter: banner bukan tempat paragraf


class SpecSalah(Exception):
    pass


def _rgb(h):
    h = str(h).strip()
    if not (h.startswith("#") and len(h) == 7):
        raise SpecSalah(f"warna harus #RRGGBB, dapat {h!r}")
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _luminans(c):
    def kanal(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (kanal(x) for x in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontras(a, b):
    """Rasio kontras WCAG antara dua warna RGB (1-21)."""
    la, lb = sorted((_luminans(a), _luminans(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def _ukuran(item):
    if item.get("ukuran"):
        try:
            w, h = (int(v) for v in str(item["ukuran"]).lower().split("x"))
        except ValueError:
            raise SpecSalah(f"{item.get('id')}: ukuran harus LxT, mis. 1200x600") from None
    elif item.get("jenis") in UKURAN:
        w, h = UKURAN[item["jenis"]]
    else:
        raise SpecSalah(f"{item.get('id')}: jenis {item.get('jenis')!r} tidak dikenal ({', '.join(UKURAN)}) dan tanpa 'ukuran'")
    if not (200 <= w <= MAKS_SISI and 100 <= h <= MAKS_SISI):
        raise SpecSalah(f"{item.get('id')}: ukuran {w}x{h} di luar batas (maks {MAKS_SISI} px per sisi)")
    return w, h


def _latar(item, w, h, palet):
    if item.get("latar"):
        p = pathlib.Path(item["latar"])
        if not p.is_file():
            raise SpecSalah(f"{item['id']}: latar tidak ada: {p}")
        with Image.open(p) as asli:
            im = asli.convert("RGB")
        skala = max(w / im.width, h / im.height)  # cover: isi penuh, potong tengah
        im = im.resize((round(im.width * skala) + 1, round(im.height * skala) + 1), Image.LANCZOS)
        kiri, atas = (im.width - w) // 2, (im.height - h) // 2
        return im.crop((kiri, atas, kiri + w, atas + h))
    a, b = _rgb(palet["utama"]), tuple(round(c * 0.72) for c in _rgb(palet["utama"]))
    grad = Image.linear_gradient("L").rotate(90, expand=True).resize((w, h))
    return Image.composite(Image.new("RGB", (w, h), b), Image.new("RGB", (w, h), a), grad)


def _font(path, size):
    return ImageFont.truetype(str(path), max(8, int(size)))


def _bungkus(teks, font, lebar, maks_baris):
    """Bungkus kata ke beberapa baris; None kalau tidak muat dalam maks_baris."""
    kata, baris, kini = teks.split(), [], ""
    for k in kata:
        coba = f"{kini} {k}".strip()
        if font.getlength(coba) <= lebar:
            kini = coba
        else:
            if not kini:
                return None  # satu kata lebih lebar dari kotak
            baris.append(kini)
            kini = k
    baris.append(kini)
    return baris if len(baris) <= maks_baris else None


def _pas(teks, path_font, lebar, ukuran_awal, maks_baris, minimal):
    s = ukuran_awal
    while s >= minimal:
        f = _font(path_font, s)
        b = _bungkus(teks, f, lebar, maks_baris)
        if b:
            return f, b
        s *= 0.92
    raise SpecSalah(f"teks terlalu panjang untuk kotaknya: {teks!r}")


def _tempel_produk(kanvas, paths, kotak, cache):
    """Tempel 1-3 produk asli di dalam kotak (x0, y0, x1, y1), rata bawah, dengan bayangan."""
    x0, y0, x1, y1 = kotak
    n = len(paths)
    lebar_slot = (x1 - x0) / (1 + 0.55 * (n - 1))
    for i, p in reversed(list(enumerate(paths))):  # belakang dulu, produk pertama paling depan
        if p not in cache:
            cache[p] = komposit.potong(p)
        prod = cache[p]
        skala_i = 1 - 0.12 * i  # produk belakang sedikit lebih kecil
        sk = min((y1 - y0) * skala_i / prod.height, lebar_slot * skala_i / prod.width)
        im = prod.resize((max(1, round(prod.width * sk)), max(1, round(prod.height * sk))), Image.LANCZOS)
        x = round(x0 + i * lebar_slot * 0.55 + (lebar_slot - im.width) / 2)
        y = y1 - im.height
        bay = Image.new("L", kanvas.size, 0)
        ImageDraw.Draw(bay).ellipse((x + im.width * 0.12, y1 - im.height * 0.03, x + im.width * 0.88,
                                     y1 + im.height * 0.03), fill=80)
        bay = bay.filter(ImageFilter.GaussianBlur(max(2, im.height // 40)))
        kanvas.paste(Image.new("RGBA", kanvas.size, (0, 0, 0, 255)), (0, 0), bay)
        kanvas.alpha_composite(im, (x, y))
    return kanvas


def render(item, palet, font, out_dir, cache):
    w, h = _ukuran(item)
    tata = item.get("tata_letak", "teks-kiri")
    if tata not in TATA_LETAK:
        raise SpecSalah(f"{item['id']}: tata_letak harus salah satu {TATA_LETAK}")
    judul = str(item.get("judul") or "").strip()
    if not judul:
        raise SpecSalah(f"{item['id']}: judul wajib diisi")
    if len(judul) > MAKS_JUDUL:
        raise SpecSalah(f"{item['id']}: judul {len(judul)} karakter (maks {MAKS_JUDUL})")
    produk = [str(p) for p in item.get("produk") or []]
    if len(produk) > 3:
        raise SpecSalah(f"{item['id']}: maksimal 3 produk per item")
    for p in produk:
        if not pathlib.Path(p).is_file():
            raise SpecSalah(f"{item['id']}: foto produk tidak ada: {p}")

    kanvas = _latar(item, w, h, palet).convert("RGBA")
    pad = round(min(w, h) * 0.07)
    if tata == "tengah":
        area_teks = (pad, pad, w - pad, round(h * 0.42))
        area_prod = (round(w * 0.18), round(h * 0.44), round(w * 0.82), h - round(pad * 0.4))
    else:
        teks_kiri = tata == "teks-kiri"
        bagi = round(w * 0.56)
        area_teks = (pad, pad, bagi - pad // 2, h - pad) if teks_kiri else (w - bagi + pad // 2, pad, w - pad, h - pad)
        area_prod = (bagi, round(h * 0.06), w - pad // 2, h - round(pad * 0.3)) if teks_kiri else \
                    (pad // 2, round(h * 0.06), w - bagi, h - round(pad * 0.3))
    if produk:
        kanvas = _tempel_produk(kanvas, produk, area_prod, cache)

    # susun blok teks dari atas ke bawah
    ax0, ay0, ax1, ay1 = area_teks
    lebar = ax1 - ax0
    unit = min(w, h)
    warna_teks = _rgb(palet.get("teks", "#FFFFFF"))
    aksen = _rgb(palet["aksen"])
    def rencana(sk):
        plan = []  # (jenis, font, baris, warna)
        if item.get("label"):
            plan.append(("label", _font(font["isi"], unit * 0.045 * sk), [str(item["label"])], _rgb(palet["utama"])))
        fj, bj = _pas(judul, font["judul"], lebar, unit * (0.11 if tata != "tengah" else 0.085) * sk, 2, unit * 0.04)
        plan.append(("judul", fj, bj, warna_teks))
        if item.get("subjudul"):
            fs, bs = _pas(str(item["subjudul"]), font["isi"], lebar, unit * 0.05 * sk, 2, unit * 0.028)
            plan.append(("subjudul", fs, bs, warna_teks))
        if item.get("harga"):
            fh, bh = _pas(str(item["harga"]), font["judul"], lebar, unit * 0.09 * sk, 1, unit * 0.04)
            plan.append(("harga", fh, bh, aksen))
        if item.get("cta"):
            plan.append(("cta", _font(font["judul"], unit * 0.042 * sk), [str(item["cta"])], _rgb(palet["utama"])))
        jarak = round(unit * 0.025 * sk)
        tinggi = []
        for jenis, f, bs, _ in plan:
            t = sum(f.getbbox("Ag")[3] for _ in bs) + (len(bs) - 1) * round(f.size * 0.15)
            tinggi.append(t + (round(f.size * 0.9) if jenis in ("label", "cta") else 0))
        return plan, tinggi, jarak, sum(tinggi) + jarak * (len(tinggi) - 1)

    for sk in (1.0, 0.9, 0.8, 0.7, 0.6):  # kecilkan semua teks bersama sampai muat
        baris_plan, tinggi, jarak, total = rencana(sk)
        if total <= ay1 - ay0:
            break
    else:
        raise SpecSalah(f"{item['id']}: teks terlalu banyak untuk ukuran {w}x{h}; kurangi subjudul/label")
    y = ay0 + ((ay1 - ay0) - total) // 2 if tata != "tengah" else ay0

    # kontras: warna teks vs rata-rata latar di area teks; kalau kurang, tambah panel
    kotak_teks = (ax0, y, ax1, y + total)
    rata = kanvas.convert("RGB").crop(kotak_teks).resize((1, 1), Image.BOX).getpixel((0, 0))
    k_awal = kontras(warna_teks, rata)
    panel = k_awal < KONTRAS_MIN
    if panel:
        lapis = Image.new("RGBA", kanvas.size, (0, 0, 0, 0))
        m = round(unit * 0.03)
        ImageDraw.Draw(lapis).rounded_rectangle((ax0 - m, y - m, ax1 + m, y + total + m), radius=m,
                                                fill=_rgb(palet["utama"]) + (225,))
        kanvas.alpha_composite(lapis)
    g = ImageDraw.Draw(kanvas)
    rata_x = (lambda tw: ax0 + (lebar - tw) // 2) if tata == "tengah" else (
        (lambda tw: ax0) if tata == "teks-kiri" else (lambda tw: ax1 - tw))
    teks_tertulis = []
    for (jenis, f, bs, warna), t in zip(baris_plan, tinggi):
        if jenis in ("label", "cta"):
            s = bs[0]
            tw, th = f.getlength(s), f.getbbox("Ag")[3]
            px, py = round(f.size * 0.7), round(f.size * 0.45)
            x = rata_x(tw + 2 * px)
            isi = aksen if jenis == "cta" else _rgb(palet.get("kedua", "#FFFFFF"))
            g.rounded_rectangle((x, y, x + tw + 2 * px, y + th + 2 * py), radius=(th + 2 * py) // 2, fill=isi)
            g.text((x + px, y + py), s, font=f, fill=warna)
        else:
            yy = y
            for s in bs:
                g.text((rata_x(f.getlength(s)), yy), s, font=f, fill=warna)
                yy += f.getbbox("Ag")[3] + round(f.size * 0.15)
        teks_tertulis.append({"jenis": jenis, "teks": " ".join(bs), "px": f.size})
        y += t + jarak

    out_dir.mkdir(parents=True, exist_ok=True)
    hasil = kanvas.convert("RGB")
    f_out = out_dir / f"{item['id']}.png"
    hasil.save(f_out, "PNG", optimize=True)
    if f_out.stat().st_size > MAKS_KB * 1024:  # terlalu besar: JPEG
        f_out.unlink()
        f_out = out_dir / f"{item['id']}.jpg"
        for q in (92, 85, 78, 70):
            hasil.save(f_out, "JPEG", quality=q, optimize=True)
            if f_out.stat().st_size <= MAKS_KB * 1024:
                break
    kb = round(f_out.stat().st_size / 1024)
    kontras_akhir = kontras(warna_teks, _rgb(palet["utama"])) if panel else k_awal
    cek = {"ukuran_ok": hasil.size == (w, h), "kb_ok": kb <= MAKS_KB, "kontras_ok": kontras_akhir >= KONTRAS_MIN}
    return {"id": item["id"], "file": str(f_out), "ukuran": f"{w}x{h}", "kb": kb, "kontras": kontras_akhir,
            "panel_ditambah": panel, "teks": teks_tertulis, "produk": produk, "latar": item.get("latar"),
            "cek": cek, "ok": all(cek.values())}


def buat(spec, out_dir):
    palet = spec.get("palet") or {}
    for k in ("utama", "aksen"):
        if k not in palet:
            raise SpecSalah(f"palet.{k} wajib (ambil dari brain/brand-visual.md)")
        _rgb(palet[k])
    font = {**FONT_DEFAULT, **{k: AKAR / v if not pathlib.Path(v).is_absolute() else pathlib.Path(v)
                               for k, v in (spec.get("font") or {}).items()}}
    for k, p in font.items():
        if not pathlib.Path(p).is_file():
            raise SpecSalah(f"font {k} tidak ada: {p}")
    item = spec.get("item") or []
    if not item:
        raise SpecSalah("spec tanpa item")
    ids = [i.get("id") for i in item]
    if len(set(ids)) != len(ids) or not all(ids):
        raise SpecSalah(f"id item kosong/dobel: {ids}")
    cache, laporan = {}, []
    for i in item:
        try:
            laporan.append(render(i, palet, font, pathlib.Path(out_dir), cache))
        except komposit.GagalKomposit as e:
            laporan.append({"id": i["id"], "ok": False, "error": f"potong produk: {e}"})
    hasil = {"ok": all(r["ok"] for r in laporan), "item": laporan}
    (pathlib.Path(out_dir) / "laporan.json").write_text(json.dumps(hasil, ensure_ascii=False, indent=2))
    return hasil


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--spec", required=True)
    a.add_argument("--out", required=True)
    x = a.parse_args(argv)
    try:
        spec = json.loads(pathlib.Path(x.spec).read_text(encoding="utf-8"))
        hasil = buat(spec, x.out)
    except (SpecSalah, OSError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": hasil["ok"], "item": [{k: r.get(k) for k in ("id", "file", "kb", "kontras", "ok", "error")}
                                                   for r in hasil["item"]]}, ensure_ascii=False))
    return 0 if hasil["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
