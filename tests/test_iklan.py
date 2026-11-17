import sys, unittest, pathlib, tempfile, csv, json, io, contextlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import iklan
from iklan import rencana

ADMIN = {"shopee": 10, "tiktok": 10}
PRODUK = [{"sku": "A", "hpp": "85000"}, {"sku": "B", "hpp": "70000"}, {"sku": "C", "hpp": "100000"},
          {"sku": "D", "hpp": ""}]


def l(sku, harga, platform="shopee"):
    return {"sku": sku, "platform": platform, "harga_akhir": str(harga)}


class TestIklan(unittest.TestCase):
    def test_rumus_dihitung_manual(self):
        r = rencana([l("A", 159000)], PRODUK, ADMIN, 50000)
        b = r["baris"][0]
        # admin 10% = 15.900 -> margin 159.000 - 15.900 - 85.000 = 58.100
        self.assertEqual(b["margin"], 58100)
        self.assertEqual(b["jatah_iklan_per_pesanan"], 29050)
        self.assertEqual(b["roas_impas"], round(159000 / 58100, 2))   # 2.74
        self.assertEqual(b["roas_target"], round(159000 / 29050, 2))  # 5.47
        self.assertEqual(b["bid_maks_per_klik"], 581)                 # 29.050 x 2%
        self.assertEqual(b["batas_klik_tanpa_pesanan"], 100)
        self.assertEqual(b["budget_harian"], 50000)
        self.assertEqual(b["status"], "LAYAK")

    def test_margin_rugi_tidak_diiklankan(self):
        r = rencana([l("C", 105000), l("D", 150000)], PRODUK, ADMIN, 50000)
        self.assertEqual([b["status"] for b in r["baris"]], ["TIDAK_DIIKLANKAN"] * 2)
        self.assertFalse(r["ada_yang_layak"])

    def test_budget_dibagi_sebanding_margin_dan_tidak_lewat_total(self):
        r = rencana([l("A", 159000), l("B", 129000), l("A", 159000, "tiktok")], PRODUK, ADMIN, 100000)
        total = sum(b["budget_harian"] for b in r["baris"])
        self.assertLessEqual(total, 100000)
        self.assertEqual(r["terpakai"], total)
        a, bb = r["baris"][0], r["baris"][1]
        self.assertGreater(a["budget_harian"], bb["budget_harian"])  # margin A > margin B
        self.assertTrue(all(b["budget_harian"] % 1000 == 0 for b in r["baris"]))

    def test_input_salah(self):
        for kw in ({"cr": 0}, {"cr": 1.5}, {"porsi": 0}):
            with self.assertRaises(ValueError):
                rencana([l("A", 159000)], PRODUK, ADMIN, 50000, **kw)
        with self.assertRaises(ValueError):
            rencana([l("A", 159000, "lazada")], PRODUK, ADMIN, 50000)

    def test_cli(self):
        d = pathlib.Path(tempfile.mkdtemp())
        for nama, rows in {"listing.csv": [l("A", 159000)], "produk.csv": PRODUK}.items():
            with open(d / nama, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        args = ["--listing", str(d / "listing.csv"), "--produk", str(d / "produk.csv"), "--admin-persen", "10",
                "--budget-harian", "30000", "--out", str(d / "iklan.csv")]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(iklan.main(args), 0)
            self.assertEqual(iklan.main(args + ["--cr", "2"]), 2)
        with open(d / "iklan.csv", newline="") as f:
            self.assertEqual(next(csv.DictReader(f))["status"], "LAYAK")


if __name__ == "__main__":
    unittest.main()
