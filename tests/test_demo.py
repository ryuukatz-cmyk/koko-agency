"""Tes integrasi: seluruh alur toko baru pada data contoh (offline). Membuktikan semua script tersambung."""
import sys, unittest, pathlib, tempfile, json, zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import demo


class TestDemoAlurLengkap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = pathlib.Path(tempfile.mkdtemp()) / "demo"
        cls.log = demo.jalankan(cls.out)

    def test_alur_lulus(self):
        self.assertTrue(self.log["ok"], json.dumps(self.log, default=str)[:2000])

    def test_sku_data_kurang_tidak_diproses(self):
        langkah = self.log["langkah"][0]["1_stok_gudang"]
        self.assertIn("CONTOH-KOKO-MARUN", langkah["data_kurang"])
        self.assertNotIn("CONTOH-KOKO-MARUN", langkah["siap"])

    def test_hasil_lengkap_di_folder(self):
        batch = next(p for p in (self.out / "batch").iterdir() if not p.name.endswith("toko-dekorasi"))
        self.assertEqual(len(list((batch / "foto").glob("F??.png"))), 10)
        self.assertTrue(next((batch / "video/final").glob("*_FINAL.mp4")).stat().st_size > 10_000)
        z = next((batch / "final").glob("paket-*.zip"))
        with zipfile.ZipFile(z) as zf:
            nama = zf.namelist()
        self.assertIn("paket/shopee/foto-01.png", nama)
        self.assertIn("paket/tiktok/listing.txt", nama)
        dek = self.out / "batch" / next(p.name for p in (self.out / "batch").iterdir() if p.name.endswith("toko-dekorasi"))
        self.assertEqual(sorted(p.name for p in (dek / "hasil").glob("D*.png")), ["D01.png", "D02.png", "D03.png"])
        self.assertTrue((self.out / "RINGKASAN.md").is_file())


if __name__ == "__main__":
    unittest.main()
