"""Buat semua data PALSU untuk uji Fase 3. Jalankan ulang kapan saja: python3 tests/data/buat_data_uji.py

Semua nama/alamat/HP di sini karangan. Tidak ada data pembeli asli.
"""
import csv, json, pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter

D = pathlib.Path(__file__).resolve().parent
NAVY, EMAS, MARUN, HIJAU = "#1F2A44", "#C9A227", "#7A1F2B", "#2E6B3A"


def koko(warna=NAVY, bordir=True, latar="white", sudut=0, skala=1.0, geser=(0, 0), kancing=5):
    im = Image.new("RGB", (1024, 1024), latar)
    g = ImageDraw.Draw(im)
    s = lambda x, y: (512 + (x - 512) * skala + geser[0], 512 + (y - 512) * skala + geser[1])
    g.polygon([s(*p) for p in [(352, 230), (432, 200), (592, 200), (672, 230), (850, 330), (900, 640), (820, 660),
                                (760, 420), (740, 880), (284, 880), (264, 420), (204, 660), (124, 640), (174, 330)]], fill=warna)
    g.rectangle([s(462, 170), s(562, 215)], fill=warna, outline="#0b0f1a", width=4)  # kerah shanghai
    for i in range(kancing):
        x, y = s(512, 250 + i * 55)
        g.ellipse([x - 9 * skala, y - 9 * skala, x + 9 * skala, y + 9 * skala], fill="white")
    if bordir:
        g.rectangle([s(570, 300), s(660, 360)], outline=EMAS, width=int(8 * skala))
        g.line([s(575, 330), s(655, 330)], fill=EMAS, width=int(5 * skala))
    return im.rotate(sudut, fillcolor=latar) if sudut else im


LATAR = ["white", "#EDE6DA", "#D9E4EC", "#F4E9D8", "#E3E3E3", "#DCEBDD", "#F2DCDC", "#E8E0F0", "#FFF6E0", "#E0F0F0"]


def foto_batch(folder, cacat_f04=False):
    folder.mkdir(parents=True, exist_ok=True)
    meta = {"master": "tests/data/master-CONTOH-KOKO-01.png", "foto": [], "gagal": [], "kurang": []}
    for i in range(10):
        fid = f"F{i + 1:02d}"
        warna = MARUN if (cacat_f04 and fid == "F04") else NAVY
        koko(warna, latar=LATAR[i], sudut=(-8, 0, 6, 0, -4, 10, 0, -10, 4, 0)[i], skala=(1, .85, .9, 1, .8, .95, .75, .9, 1, .85)[i],
             geser=((0, 0), (-60, 40), (50, 0), (0, 30), (80, -30), (0, 0), (-40, -40), (30, 60), (0, -20), (-70, 0))[i]).save(folder / f"{fid}.png")
        meta["foto"].append({"id": fid, "file": f"{fid}.png", "provider": "uji-palsu", "model": "PIL", "prompt": f"scene {i + 1}", "waktu": "2026-11-10T08:00:00"})
    (folder / "metadata.json").write_text(json.dumps(meta, indent=2))


def tulis(path, kolom, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(kolom); w.writerows(rows)


def export_palsu():
    m = D / "mentah"; m.mkdir(exist_ok=True)
    pembeli = ["budi_palsu", "Budi Palsu", "081200000000", "Jl. Karangan No. 1", "Kota Fiktif", "Provinsi Fiktif", "00000", "tolong cepat"]
    kolom = ["No. Pesanan", "Status Pesanan", "Waktu Pesanan Dibuat", "Nomor Referensi SKU", "Nama Produk", "Jumlah",
             "Harga Setelah Diskon", "Username (Pembeli)", "Nama Penerima", "No. Telepon", "Alamat Pengiriman",
             "Kota/Kabupaten", "Provinsi", "Kode Pos", "Catatan dari Pembeli"]
    p = [("KOKO-A", "2026-05-01 10:00", 3, "Selesai"), ("KOKO-A", "2026-06-13 10:00", 1, "Selesai"),
         ("KOKO-B", "2026-08-27 09:00", 2, "Selesai"), ("KOKO-B", "2026-10-30 09:00", 4, "Batal"),
         ("KOKO-D", "2026-04-01 09:00", 1, "Selesai"), ("KOKO-F", "2026-10-31 09:00", 5, "Selesai"),
         ("KOKO-G", "2026-04-26 09:00", 1, "Selesai"), ("KOKO-H", "2026-07-01 09:00", 1, "Selesai")]
    tulis(m / "export-pesanan.csv", kolom,
          [[f"2600{i}", s, t, sku, "Koko", j, "Rp 150.000"] + pembeli for i, (sku, t, j, s) in enumerate(p)])
    tulis(m / "export-stok.csv", ["Kode Produk", "Nama Produk", "SKU", "Harga", "Stok"],
          [["1", "Koko Navy Bordir", "KOKO-A", "Rp 150.000", 40], ["2", "Koko Putih", "KOKO-B", "Rp 120.000", 12],
           ["3", "Koko Hijau", "KOKO-C", "Rp 110.000", 25], ["4", "Koko Abu", "KOKO-D", "Rp 100.000", 3],
           ["5", "Koko Hitam", "KOKO-E", "Rp 130.000", 0], ["6", "Koko Laris", "KOKO-F", "Rp 140.000", 50],
           ["7", "Koko Cokelat", "KOKO-G", "Rp 125.000", 30], ["8", "Koko Krem", "KOKO-H", "Rp 115.000", 10],
           ["9", "Koko Krem", "KOKO-H", "Rp 115.000", 6]])
    tulis(m / "hpp.csv", ["SKU", "HPP"],
          [["KOKO-A", "90.000"], ["KOKO-B", "70.000"], ["KOKO-C", "60.000"], ["KOKO-D", "55.000"],
           ["KOKO-E", "75.000"], ["KOKO-F", "80.000"], ["KOKO-G", ""], ["KOKO-H", "65.000"]])


def status(sku, st):
    return json.dumps({"batch": None, "sku": sku, "status": st, "revisi": {}, "riwayat": []}, indent=2)


def batch(nama, diskon, judul, deskripsi, caption, cacat):
    b = D / nama
    foto_batch(b / "foto", cacat_f04=cacat)
    s = json.loads(status("CONTOH-KOKO-01", "QC_FINAL")); s["batch"] = nama
    (b / "status.json").write_text(json.dumps(s, indent=2))
    akhir = int(150000 * (100 - diskon) / 100)
    (b / "strategi.md").write_text(
        f"# Strategi {nama}\n\nSKU CONTOH-KOKO-01. Taktik: diskon {diskon}%.\n"
        f"Alasan: stok 40, tidak terjual 150 hari, modal tertahan Rp 3.600.000.\n\n"
        f"Harga normal Rp 150.000, HPP Rp 90.000, admin 10%. Harga akhir Rp {akhir:,}. (laporan marketer)\n".replace(",", "."))
    tulis(b / "listing.csv", ["sku", "judul", "deskripsi", "harga_normal", "harga_akhir", "taktik", "caption_video"],
          [["CONTOH-KOKO-01", judul, deskripsi, 150000, akhir, f"diskon {diskon}%", caption]])
    return b, akhir


def main():
    export_palsu()
    koko().save(D / "master-CONTOH-KOKO-01.png")
    koko().filter(ImageFilter.GaussianBlur(28)).save(D / "master-buram-CONTOH-KOKO-02.png")
    koko(HIJAU, bordir=False, kancing=3).save(D / "produk-lain-KOKO-C.png")

    b1, h1 = batch("batch-uji-lulus", 20, "Koko Lengan Panjang Navy Kerah Shanghai Bordir Dada",
                   "Koko lengan panjang warna navy. Kerah shanghai. Bordir di dada kiri.",
                   "Koko navy kerah shanghai, bordir dada kiri. Cek keranjang ya Kak!", cacat=False)
    b2, h2 = batch("batch-uji-cacat", 35, "Koko Premium Best Seller Navy Anti Luntur",
                   "Bahan katun premium, best seller, anti luntur, garansi uang kembali.",
                   "Best seller! Bahan premium adem seharian.", cacat=True)

    # batch cacat memakai Flow: P01..P10 tapi klip hanya V01..V09, dan V05 adalah produk lain (SKU salah)
    (b2 / "prompt-flow.md").write_text("".join(f"## P{i:02d}\nslow camera push-in on F{i:02d}, product unchanged\n\n" for i in range(1, 11)))
    flow = b2 / "video" / "flow"; flow.mkdir(parents=True, exist_ok=True)
    for i in range(1, 10):
        src = D / "produk-lain-KOKO-C.png" if i == 5 else b2 / "foto" / f"F{i:02d}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(src), "-t", "4", "-vf",
                        "scale=1080:-2,pad=1080:1920:0:(oh-ih)/2:white,format=yuv420p", "-r", "30", str(flow / f"V{i:02d}.mp4")], check=True)

    # video final: batch lulus = slideshow; batch cacat = dari klip Flow (berisi V05 produk lain)
    sys.path.insert(0, str(D.parent.parent / "scripts"))
    import video
    for b, harga, fl in ((b1, h1, None), (b2, h2, flow)):
        out = b / "video" / "final" / f"{b.name}_FINAL.mp4"
        r = video.buat(b / "foto", fl, "Koko Navy Bordir", f"Rp {harga:,}".replace(",", "."), out)
        print(b.name, json.dumps(r))


if __name__ == "__main__":
    main()
