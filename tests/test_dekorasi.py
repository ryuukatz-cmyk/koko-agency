import sys, unittest, pathlib, tempfile, json, io, contextlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import dekorasi
from dekorasi import buat, kontras, SpecSalah
from PIL import Image

AKAR = pathlib.Path(__file__).resolve().parent.parent
NAVY = str(AKAR / "contoh/input/4-foto-master/CONTOH-KOKO-NAVY/depan.png")
PUTIH = str(AKAR / "contoh/input/4-foto-master/CONTOH-KOKO-PUTIH/depan.png")
PALET = {"utama": "#1F2A44", "kedua": "#F4F1E8", "aksen": "#C9A227", "teks": "#FFFFFF"}


def spec(*item, palet=PALET):
    return {"palet": palet, "item": list(item)}


class TestDekorasi(unittest.TestCase):
    def setUp(self):
        self.d = pathlib.Path(tempfile.mkdtemp())

    def test_kontras_wcag(self):
        self.assertEqual(kontras((255, 255, 255), (0, 0, 0)), 21.0)
        self.assertEqual(kontras((10, 10, 10), (10, 10, 10)), 1.0)

    def test_banner_ukuran_pas_dan_teks_dari_kode(self):
        r = buat(spec({"id": "D01", "jenis": "banner-carousel", "produk": [NAVY], "label": "Koleksi Ramadan",
                       "judul": "Koko Bordir Navy", "harga": "Rp 159.000", "cta": "Beli"}), self.d)
        self.assertTrue(r["ok"], r)
        it = r["item"][0]
        with Image.open(it["file"]) as im:
            self.assertEqual(im.size, (1200, 600))
        self.assertLessEqual(it["kb"], dekorasi.MAKS_KB)
        # teks yang tertulis tercatat persis -> qc bisa membandingkan dengan harga yang disetujui
        self.assertIn({"jenis": "harga", "teks": "Rp 159.000"}, [{k: t[k] for k in ("jenis", "teks")} for t in it["teks"]])
        self.assertTrue(json.loads((self.d / "laporan.json").read_text())["ok"])

    def test_produk_asli_ditempel(self):
        r = buat(spec({"id": "D02", "jenis": "kategori", "tata_letak": "tengah", "produk": [NAVY],
                       "judul": "Koko Navy"}, palet={**PALET, "utama": "#F4F1E8", "teks": "#1F2A44"}), self.d)
        with Image.open(r["item"][0]["file"]) as im:
            px = im.convert("RGB")
            # badan navy master (#1F2A44) muncul di area produk (bawah tengah)
            navy = sum(1 for x in range(250, 550, 10) for y in range(450, 780, 10)
                       if max(abs(a - b) for a, b in zip(px.getpixel((x, y)), (31, 42, 68))) < 25)
        self.assertGreater(navy, 50)

    def test_latar_terang_dapat_panel_kontras(self):
        Image.new("RGB", (1600, 900), (240, 235, 225)).save(self.d / "latar.png")
        r = buat(spec({"id": "D03", "jenis": "banner-carousel", "latar": str(self.d / "latar.png"),
                       "produk": [PUTIH], "judul": "Voucher Rp10.000"}), self.d / "out")
        it = r["item"][0]
        self.assertTrue(it["panel_ditambah"])
        self.assertGreaterEqual(it["kontras"], dekorasi.KONTRAS_MIN)
        self.assertTrue(it["ok"])

    def test_teks_panjang_dikecilkan_bukan_dipotong(self):
        r = buat(spec({"id": "D04", "jenis": "kategori", "tata_letak": "tengah", "judul": "Koko Lengan Panjang Bordir",
                       "subjudul": "Ukuran M sampai XL", "harga": "Rp 159.000"}), self.d)
        self.assertTrue(r["ok"])
        self.assertEqual([t["teks"] for t in r["item"][0]["teks"]][0], "Koko Lengan Panjang Bordir")

    def test_spec_salah_ditolak(self):
        salah = [
            {"id": "X", "jenis": "spanduk", "judul": "a"},                         # jenis tidak dikenal
            {"id": "X", "jenis": "kategori", "judul": "a" * 61},                    # judul terlalu panjang
            {"id": "X", "jenis": "kategori", "judul": "a", "latar": "tidak/ada.png"},
            {"id": "X", "jenis": "kategori", "judul": "a", "produk": [NAVY] * 4},
            {"id": "X", "ukuran": "5000x600", "judul": "a"},
            {"id": "X", "jenis": "kategori", "judul": ""},
        ]
        for item in salah:
            with self.assertRaises(SpecSalah, msg=item):
                buat(spec(item), self.d)
        with self.assertRaises(SpecSalah):
            buat({"palet": {"utama": "biru"}, "item": [{"id": "X", "jenis": "kategori", "judul": "a"}]}, self.d)
        with self.assertRaises(SpecSalah):
            buat(spec({"id": "X", "jenis": "kategori", "judul": "a"}, {"id": "X", "jenis": "kategori", "judul": "b"}), self.d)

    def test_ukuran_kustom(self):
        r = buat(spec({"id": "D05", "ukuran": "1200x400", "judul": "Gratis Ongkir"}), self.d)
        with Image.open(r["item"][0]["file"]) as im:
            self.assertEqual(im.size, (1200, 400))

    def test_cli(self):
        (self.d / "spec.json").write_text(json.dumps(spec({"id": "D01", "jenis": "kategori", "judul": "Koko"})))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(dekorasi.main(["--spec", str(self.d / "spec.json"), "--out", str(self.d / "o")]), 0)
            (self.d / "rusak.json").write_text("{")
            self.assertEqual(dekorasi.main(["--spec", str(self.d / "rusak.json"), "--out", str(self.d / "o")]), 2)


if __name__ == "__main__":
    unittest.main()


class TestLatar(unittest.TestCase):
    def setUp(self):
        import gambar, latar
        self.gambar, self.latar = gambar, latar
        self._asli = gambar._post
        self.d = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        self.gambar._post = self._asli

    def test_ukuran_ai_kelipatan_16_rasio_sama(self):
        self.assertEqual(self.latar.ukuran_ai(1200, 600), (1024, 512))
        self.assertEqual(self.latar.ukuran_ai(800, 800), (1024, 1024))
        w, h = self.latar.ukuran_ai(1200, 628)
        self.assertEqual((w % 16, h % 16), (0, 0))

    def test_latar_dibuat_tanpa_referensi_dan_dilewati_kalau_ada(self):
        png = io.BytesIO(); Image.new("RGB", (8, 8), "beige").save(png, "PNG")
        panggilan = []
        def palsu(args):
            panggilan.append(args)
            return (429, b"limit 0") if "generativelanguage" in args[-1] else (200, png.getvalue())
        self.gambar._post = palsu
        (self.d / "ada.png").write_bytes(png.getvalue())
        s = spec({"id": "D01", "jenis": "banner-carousel", "judul": "a", "latar": str(self.d / "baru.png"),
                  "latar_prompt": "empty wooden shelf, no people, no text"},
                 {"id": "D02", "jenis": "kategori", "judul": "b", "latar": str(self.d / "ada.png"),
                  "latar_prompt": "x"})
        akun = self.d / "akun.txt"; akun.write_text("akun123")
        meta = self.latar.buat(s, akun_cf_file=akun, urutan="cloudflare")
        self.assertEqual(meta["kurang"], [])
        self.assertTrue((self.d / "baru.png").is_file())
        cf = [a for a in panggilan if "api.cloudflare.com" in a[-1]]
        self.assertEqual(len(cf), 1)  # D02 sudah ada -> tidak dibuat ulang
        self.assertIn("width=1024", cf[0]); self.assertIn("height=512", cf[0])
        self.assertFalse(any(x.startswith("input_image_") for x in cf[0]))

    def test_latar_prompt_tanpa_path_ditolak(self):
        with self.assertRaises(SpecSalah):
            self.latar.buat(spec({"id": "D01", "jenis": "kategori", "judul": "a", "latar_prompt": "x"}))
