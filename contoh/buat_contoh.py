"""Buat data CONTOH toko koko (palsu) untuk latihan agent dan demo. Jalankan ulang: python3 contoh/buat_contoh.py

Struktur meniru folder Drive `Koko Agency/input/`. Semua angka, nama, dan foto di sini karangan.
Ganti dengan data asli di Drive; folder contoh/ tidak pernah dibaca saat batch nyata.
"""
import csv, pathlib
from PIL import Image, ImageChops, ImageDraw, ImageFilter

D = pathlib.Path(__file__).resolve().parent
INPUT = D / "input"

# sku: (nama, warna badan, warna bordir, kancing (jumlah, warna), lengan, latar master, stok, harga, hpp, tgl masuk, fakta)
PRODUK = {
    "CONTOH-KOKO-NAVY": ("Koko Lengan Panjang Bordir Navy", "#1F2A44", "#C9A227", (5, "#F5F5F0"), "panjang", "#F2F1EE",
                         40, 159000, 85000, "2026-08-15",
                         "lengan panjang;kerah shanghai;bordir dada kiri warna emas;5 kancing putih;warna navy"),
    "CONTOH-KOKO-PUTIH": ("Koko Lengan Panjang Putih Bordir Emas", "#F4F1E8", "#B8962E", (6, "#E2DCCB"), "panjang",
                          "#9AA3AB", 60, 149000, 80000, "2026-09-01",
                          "lengan panjang;kerah shanghai;bordir dada kiri warna emas;6 kancing;warna putih gading"),
    "CONTOH-KOKO-SAGE": ("Koko Lengan Pendek Hijau Sage", "#8FA58A", "#F4F1E8", (4, "#7A4E2D"), "pendek", "#F2F1EE",
                         25, 129000, 70000, "2026-10-01",
                         "lengan pendek;kerah shanghai;bordir dada kiri warna putih;4 kancing cokelat;warna hijau sage"),
    # sengaja tidak lengkap: HPP kosong -> DATA_KURANG (latihan agent menolak menebak)
    "CONTOH-KOKO-MARUN": ("Koko Lengan Panjang Marun", "#7A1F2B", "#C9A227", (5, "#F5F5F0"), "panjang", "#F2F1EE",
                          15, 155000, None, "2026-07-20", "lengan panjang;kerah shanghai;warna marun"),
}


WARNA = {"CONTOH-KOKO-NAVY": "navy", "CONTOH-KOKO-PUTIH": "putih gading", "CONTOH-KOKO-SAGE": "hijau sage",
         "CONTOH-KOKO-MARUN": "marun"}


def _gelap(hexwarna, f):
    r, g, b = (int(hexwarna[i:i + 2], 16) for i in (1, 3, 5))
    return tuple(max(0, min(255, round(c * f))) for c in (r, g, b))


def gambar_koko(badan, bordir, kancing, lengan, latar, w=1200, h=1500):
    """Ilustrasi koko tampak depan di latar polos (bukan foto asli; cukup untuk latihan potong & Product Lock)."""
    im = Image.new("RGB", (w, h), latar)
    g = ImageDraw.Draw(im)
    cx = w // 2
    bahu_y, bawah_y = 330, 1330
    badan_poly = [(cx - 150, 250), (cx + 150, 250), (cx + 330, 330), (cx + 345, bawah_y), (cx - 345, bawah_y),
                  (cx - 330, 330)]
    if lengan == "panjang":
        kiri = [(cx - 330, 330), (cx - 470, 420), (cx - 560, 1180), (cx - 440, 1200), (cx - 345, 640)]
        manset = [(cx - 562, 1130), (cx - 438, 1150), (cx - 440, 1200), (cx - 560, 1180)]
    else:
        kiri = [(cx - 330, 330), (cx - 470, 420), (cx - 520, 660), (cx - 360, 690), (cx - 345, 560)]
        manset = None
    cermin = lambda poly: [(2 * cx - x, y) for (x, y) in poly]
    kanan = cermin(kiri)
    for poly in (kiri, kanan):
        g.polygon(poly, fill=_gelap(badan, 0.92))
    g.polygon(badan_poly, fill=badan)
    # bayangan lipatan lembut di sisi badan
    sisi = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sisi).polygon([(cx - 345, 400), (cx - 280, 400), (cx - 290, bawah_y), (cx - 345, bawah_y)], fill=60)
    ImageDraw.Draw(sisi).polygon([(cx + 345, 400), (cx + 280, 400), (cx + 290, bawah_y), (cx + 345, bawah_y)], fill=60)
    badan_mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(badan_mask).polygon(badan_poly, fill=255)
    sisi = ImageChops.multiply(sisi.filter(ImageFilter.GaussianBlur(25)), badan_mask)  # bayangan tidak keluar dari badan
    im.paste(Image.new("RGB", (w, h), _gelap(badan, 0.75)), (0, 0), sisi)
    g = ImageDraw.Draw(im)
    if manset:
        for poly in (manset, cermin(manset)):
            g.polygon(poly, fill=_gelap(badan, 0.8))
    # kerah shanghai (berdiri)
    g.rounded_rectangle([cx - 120, 190, cx + 120, 262], radius=18, fill=_gelap(badan, 0.9), outline=_gelap(badan, 0.6),
                        width=4)
    # plaket kancing
    g.rectangle([cx - 28, 262, cx + 28, 760], fill=_gelap(badan, 0.94), outline=_gelap(badan, 0.75), width=3)
    n, warna_k = kancing
    for i in range(n):
        y = 310 + i * (420 // max(n - 1, 1))
        g.ellipse([cx - 13, y - 13, cx + 13, y + 13], fill=warna_k, outline=_gelap(warna_k, 0.7), width=2)
    # bordir dada kiri pemakai = kanan gambar
    bx, by = cx + 120, 400
    g.rounded_rectangle([bx, by, bx + 150, by + 110], radius=10, outline=bordir, width=6)
    for k in range(4):
        x = bx + 15 + k * 31
        g.polygon([(x, by + 55), (x + 15, by + 30), (x + 30, by + 55), (x + 15, by + 80)], outline=bordir, width=4)
    g.line([(bx + 12, by + 55), (bx + 138, by + 55)], fill=bordir, width=3)
    return im


def detail_bordir(depan, w=1200):
    cx = w // 2
    return depan.crop((cx + 80, 360, cx + 310, 550)).resize((920, 760), Image.LANCZOS)


def tulis(path, kolom, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")  # LF: sama dengan yang tersimpan di git
        w.writerow(kolom)
        w.writerows(rows)


def product_lock(sku, p):
    nama, badan, bordir, (n, warna_k), lengan, *_ = p
    return f"""# Product Lock — {sku} (CONTOH, data palsu untuk latihan)

- SKU: {sku}
- Foto master: contoh/input/4-foto-master/{sku}/depan.png (+ detail-bordir.png)
- Warna utama: {WARNA[sku]} ({badan})
- Bentuk/potongan: kemeja koko lengan {lengan}
- Kerah: shanghai (berdiri), warna sedikit lebih gelap dari badan
- Kancing: {n} kancing ({warna_k}) di plaket tengah depan
- Bordir/motif: kotak bordir {bordir} berisi 4 belah ketupat dan garis tengah, di dada kiri pemakai (kanan foto)
- Logo/label: tidak ada
- Saku: tidak ada
- Boleh berubah: latar, properti, pencahayaan, sudut kamera, model/manekin
- TIDAK boleh berubah: warna badan, jumlah & warna kancing, bentuk & posisi bordir, kerah shanghai, panjang lengan
"""


def main():
    stok, hpp, info = [], [], []
    for sku, p in PRODUK.items():
        nama, badan, bordir, kancing, lengan, latar, n_stok, harga, nilai_hpp, tgl, fakta = p
        folder = INPUT / "4-foto-master" / sku
        folder.mkdir(parents=True, exist_ok=True)
        depan = gambar_koko(badan, bordir, kancing, lengan, latar)
        depan.save(folder / "depan.png", optimize=True)
        detail_bordir(depan).save(folder / "detail-bordir.png", optimize=True)
        stok.append([sku, f"{nama} (CONTOH)", n_stok, harga, tgl, "CONTOH"])
        hpp.append([sku, "" if nilai_hpp is None else nilai_hpp])
        info.append([sku, nama, WARNA[sku], "M;L;XL", "CONTOH-isi dari data asli", fakta, "CONTOH"])
        (D / "product-lock").mkdir(exist_ok=True)
        (D / "product-lock" / f"{sku}.md").write_text(product_lock(sku, p), encoding="utf-8")
    tulis(INPUT / "1-stok-gudang" / "stok-gudang.csv",
          ["SKU", "nama", "stok", "harga_jual_rencana", "tanggal_masuk", "catatan"], stok)
    tulis(INPUT / "2-hpp" / "hpp.csv", ["SKU", "HPP"], hpp)
    tulis(INPUT / "3-info-produk" / "info-produk.csv",
          ["SKU", "nama", "warna", "ukuran", "bahan", "fakta_boleh_diklaim", "catatan"], info)
    print(f"{len(PRODUK)} SKU contoh ditulis ke {INPUT}")


if __name__ == "__main__":
    main()
