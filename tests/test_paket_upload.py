import sys, unittest, pathlib, tempfile, csv, json, zipfile, io, contextlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import paket_upload
from paket_upload import buat, Salah
from PIL import Image


def siapkan(n_foto=3, platform=("shopee", "tiktok")):
    d = pathlib.Path(tempfile.mkdtemp()) / "2026-12-01-KOKO-A"
    (d / "foto").mkdir(parents=True)
    foto = []
    for i in range(1, n_foto + 1):
        f = d / "foto" / f"F{i:02d}.png"; Image.new("RGB", (64, 64), (i * 20, 40, 80)).save(f); foto.append(f)
    (d / "video.mp4").write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"0" * 100)
    with open(d / "listing.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["sku", "platform", "judul", "deskripsi", "harga_normal", "harga_coret",
                                            "harga_akhir", "taktik", "kata_kunci", "caption_video"])
        w.writeheader()
        for p in platform:
            w.writerow({"sku": "KOKO-A", "platform": p, "judul": f"Baju Koko Pria {p}", "deskripsi": "Desk",
                        "harga_normal": "159000", "harga_coret": "", "harga_akhir": "159000", "taktik": "voucher",
                        "kata_kunci": "baju koko pria", "caption_video": "cap"})
    return d, foto


class TestPaket(unittest.TestCase):
    def test_paket_lengkap(self):
        d, foto = siapkan(3)
        m = buat(d, [foto[2], foto[0], foto[1]], d / "video.mp4", d / "listing.csv", 40, d / "final")
        self.assertEqual(m["sku"], "KOKO-A")
        s = d / "final" / "paket" / "shopee"
        self.assertEqual(sorted(x.name for x in s.iterdir()), ["foto-01.png", "foto-02.png", "foto-03.png",
                                                              "listing.txt", "video.mp4"])
        # urutan argumen = urutan di toko: foto-01 = F03
        self.assertEqual(m["platform"]["shopee"]["foto"][0]["asal"], str(foto[2]))
        self.assertIn("JUDUL\nBaju Koko Pria shopee", (s / "listing.txt").read_text())
        ck = (d / "final" / "CHECKLIST-UPLOAD.md").read_text()
        self.assertIn("Tanpa harga coret", ck)
        self.assertIn("Stok: 40", ck)
        with zipfile.ZipFile(m["zip"]) as z:
            self.assertIn("paket/tiktok/video.mp4", z.namelist())
            self.assertIn("CHECKLIST-UPLOAD.md", z.namelist())

    def test_foto_lebih_dari_batas_tidak_masuk_dan_dicatat(self):
        d, foto = siapkan(11)
        m = buat(d, foto, None, d / "listing.csv", None, d / "final")
        self.assertEqual(len(m["platform"]["shopee"]["foto"]), 9)
        self.assertEqual(len(m["platform"]["shopee"]["foto_tidak_masuk"]), 2)

    def test_paket_lama_dibersihkan(self):
        d, foto = siapkan(3)
        buat(d, foto, None, d / "listing.csv", 5, d / "final")
        buat(d, foto[:1], None, d / "listing.csv", 5, d / "final")
        self.assertEqual(len(list((d / "final" / "paket" / "shopee").glob("foto-*"))), 1)

    def test_input_salah(self):
        d, foto = siapkan(2)
        with self.assertRaises(Salah):
            buat(d, [], None, d / "listing.csv", 1, d / "final")
        with self.assertRaises(Salah):
            buat(d, [d / "tidak-ada.png"], None, d / "listing.csv", 1, d / "final")
        with self.assertRaises(Salah):
            buat(d, [foto[0], foto[0]], None, d / "listing.csv", 1, d / "final")
        d2, f2 = siapkan(1, platform=("shopee", "shopee"))
        with self.assertRaises(Salah):
            buat(d2, f2, None, d2 / "listing.csv", 1, d2 / "final")

    def test_cli(self):
        d, foto = siapkan(2)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(paket_upload.main(["--batch", str(d), "--foto", *map(str, foto), "--listing",
                                                str(d / "listing.csv"), "--out", str(d / "final")]), 0)
            self.assertEqual(paket_upload.main(["--batch", str(d), "--foto", "x.png", "--listing",
                                                str(d / "listing.csv"), "--out", str(d / "final")]), 2)


if __name__ == "__main__":
    unittest.main()
