"""Foto komposit: produk ASLI dari foto master ditempel di atas latar buatan AI.

Dipakai untuk foto yang produknya harus 100% sama (F01-F03, foto utama katalog). Model gambar hanya membuat
latar; piksel produk diambil langsung dari master, jadi kancing/bordir/kerah tidak mungkin berubah.

Syarat master: latar polos (putih/abu/satu warna), produk tidak menyentuh tepi foto. Kalau latar tidak polos,
script berhenti dengan pesan error (tidak ditebak): pakai scene AI biasa atau minta master yang lebih bersih.

  python3 scripts/komposit.py --master depan.jpg --latar latar.png --out F01.png
Exit 0 = selesai, 2 = master/latar tidak bisa dipakai.
"""
import argparse, json, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

SISI_MASK = 600      # mask dihitung di ukuran kecil supaya cepat (floodfill PIL berjalan di Python)
AMBANG = 40          # beda warna dari latar (0-255) yang masih dianggap latar
AREA_MIN, AREA_MAX = 0.05, 0.92


class GagalKomposit(Exception):
    pass


def _warna_latar(im):
    """Median warna piksel tepi foto."""
    w, h = im.size
    px = im.load()
    tepi = [px[x, y] for x in range(w) for y in (0, h - 1)] + [px[x, y] for y in range(h) for x in (0, w - 1)]
    return tuple(sorted(c[i] for c in tepi)[len(tepi) // 2] for i in range(3)), tepi


def potong(master):
    """Kembalikan gambar RGBA produk (latar transparan), dipotong rapat ke batas produk."""
    with Image.open(master) as asli:
        im = asli.convert("RGB")
    kecil = im.copy()
    kecil.thumbnail((SISI_MASK, SISI_MASK))
    latar, tepi = _warna_latar(kecil)
    beda_tepi = sorted(max(abs(c[i] - latar[i]) for i in range(3)) for c in tepi)
    if beda_tepi[int(len(beda_tepi) * 0.9)] > AMBANG:
        raise GagalKomposit("latar master tidak polos (tepi foto berwarna-warni): potong otomatis tidak aman")

    r, g, b = ImageChops.difference(kecil, Image.new("RGB", kecil.size, latar)).split()
    beda = ImageChops.lighter(ImageChops.lighter(r, g), b)
    biner = beda.point(lambda v: 255 if v > AMBANG else 0)
    # latar = area mirip warna latar yang TERSAMBUNG ke tepi; warna mirip di dalam produk (kancing putih) tetap produk
    w, h = biner.size
    px = biner.load()
    for x, y in [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + \
                [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]:
        if px[x, y] == 0:
            ImageDraw.floodfill(biner, (x, y), 128, thresh=0)
    mask = biner.point(lambda v: 0 if v == 128 else 255)

    area = sum(mask.histogram()[255:]) / (w * h)
    if not AREA_MIN <= area <= AREA_MAX:
        raise GagalKomposit(f"produk terdeteksi {area:.0%} dari foto (wajar {AREA_MIN:.0%}-{AREA_MAX:.0%}): "
                            "cek master (produk terpotong, terlalu kecil, atau menyatu dengan latar)")
    # kecilkan tepi 1 px supaya sisa warna latar tidak terlihat, lalu haluskan
    mask = mask.filter(ImageFilter.MinFilter(3)).resize(im.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(1))
    produk = im.convert("RGBA")
    produk.putalpha(mask)
    kotak = mask.point(lambda v: 255 if v > 128 else 0).getbbox()
    if not kotak:
        raise GagalKomposit("produk tidak terdeteksi di master")
    return produk.crop(kotak)


def _kotak_latar(latar_path, ukuran):
    with Image.open(latar_path) as asli:
        im = asli.convert("RGB")
    s = min(im.size)  # potong tengah jadi persegi
    kiri, atas = (im.width - s) // 2, (im.height - s) // 2
    return im.crop((kiri, atas, kiri + s, atas + s)).resize((ukuran, ukuran), Image.LANCZOS)


def tempel(produk, latar_path, out, ukuran=1024, tinggi=0.84, lebar=0.86):
    """Tempel produk RGBA di tengah-bawah latar persegi, dengan bayangan lembut."""
    kanvas = _kotak_latar(latar_path, ukuran).convert("RGBA")
    skala = min(tinggi * ukuran / produk.height, lebar * ukuran / produk.width)
    p = produk.resize((max(1, round(produk.width * skala)), max(1, round(produk.height * skala))), Image.LANCZOS)
    x = (ukuran - p.width) // 2
    y = ukuran - p.height - round(0.05 * ukuran)

    bayangan = Image.new("L", (ukuran, ukuran), 0)
    lebar_b = round(p.width * 0.8)
    ImageDraw.Draw(bayangan).ellipse((x + (p.width - lebar_b) // 2, y + p.height - round(0.025 * ukuran),
                                      x + (p.width + lebar_b) // 2, y + p.height + round(0.025 * ukuran)), fill=90)
    bayangan = bayangan.filter(ImageFilter.GaussianBlur(round(0.02 * ukuran)))
    kanvas = Image.composite(Image.new("RGBA", kanvas.size, (0, 0, 0, 255)), kanvas, bayangan)
    kanvas.alpha_composite(p, (x, y))
    kanvas.convert("RGB").save(out, "PNG")
    return {"ukuran": ukuran, "posisi": [x, y], "ukuran_produk": [p.width, p.height]}


def buat(master, latar, out, ukuran=1024):
    return tempel(potong(master), latar, out, ukuran)


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--master", required=True, help="foto master depan, latar polos")
    a.add_argument("--latar", required=True, help="gambar latar (dari gambar.py atau buatan manusia)")
    a.add_argument("--out", required=True)
    a.add_argument("--ukuran", type=int, default=1024)
    x = a.parse_args(argv)
    try:
        hasil = buat(x.master, x.latar, x.out, x.ukuran)
    except (GagalKomposit, OSError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"status": "SELESAI", "out": x.out, **hasil}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
