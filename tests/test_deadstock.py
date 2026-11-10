import sys, unittest, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from deadstock import pilih


def r(sku, stok, hari, hpp=50000, catatan=""):
    return {"sku": sku, "nama": sku, "stok": stok, "harga": 100000, "hpp": hpp,
            "unit_terjual": 0, "terakhir_terjual": "", "hari_tanpa_jual": hari, "catatan": catatan}


class TestDeadstock(unittest.TestCase):
    def test_batas_aturan(self):
        hasil = pilih([r("STOK0", 0, 200), r("STOK4", 4, 200), r("H59", 10, 59), r("PAS", 5, 60)])
        self.assertEqual([x["sku"] for x in hasil], ["PAS"])

    def test_skor_dihitung_manual(self):
        # modal: A=10*50000=500000 (maks), B=5*40000=200000
        # umur:  A=60, B=120 (maks); stok: A=10 (maks), B=5
        hasil = pilih([r("A", 10, 60), r("B", 5, 120, hpp=40000)])
        skor = {x["sku"]: x["skor"] for x in hasil}
        self.assertEqual(skor["A"], 50 + 15 + 20)        # 85.0
        self.assertEqual(skor["B"], 20 + 30 + 10)        # 60.0
        self.assertEqual([x["sku"] for x in hasil], ["A", "B"])
        self.assertEqual(hasil[0]["modal_tertahan"], 500000)
        self.assertEqual(hasil[0]["status"], "DEADSTOCK")

    def test_hpp_kosong_tidak_diskor_dan_di_akhir(self):
        hasil = pilih([r("X", 50, 300, hpp=None, catatan="HPP_KOSONG"), r("A", 5, 60)])
        self.assertEqual([x["sku"] for x in hasil], ["A", "X"])
        self.assertIsNone(hasil[1]["skor"])
        self.assertIsNone(hasil[1]["modal_tertahan"])
        self.assertEqual(hasil[1]["status"], "DEADSTOCK_DATA_KURANG")

    def test_sku_dobel_tidak_diskor(self):
        hasil = pilih([r("D", 10, 90, catatan="SKU_DOBEL")])
        self.assertEqual(hasil[0]["status"], "DEADSTOCK_DATA_KURANG")
        self.assertIsNone(hasil[0]["skor"])

    def test_kosong(self):
        self.assertEqual(pilih([]), [])


if __name__ == "__main__":
    unittest.main()
