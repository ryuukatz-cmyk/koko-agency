import sys, unittest, pathlib, datetime, tempfile, csv, json, io, contextlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import stok_gudang
from stok_gudang import katalog

HARI_INI = datetime.date(2026, 11, 17)


def stok(sku, n, harga, tgl="2026-08-01", nama="Koko", catatan=""):
    return {"SKU": sku, "Nama": nama, "Stok": str(n), "Harga_Jual_Rencana": harga, "Tanggal_Masuk": tgl,
            "Catatan": catatan}


def hpp(sku, n):
    return {"SKU": sku, "HPP": n}


def info(sku, fakta="lengan panjang;bordir dada kiri"):
    return {"SKU": sku, "fakta_boleh_diklaim": fakta}


class TestStokGudang(unittest.TestCase):
    def test_lengkap_siap_dan_diskor(self):
        rows = katalog([stok("A", 20, "150.000", "2026-05-01"), stok("B", 10, "Rp 175.000", "2026-10-01")],
                       [hpp("A", "90000"), hpp("B", "100000")], [info("A"), info("B")], 10, HARI_INI)
        a = {r["sku"]: r for r in rows}
        self.assertEqual(a["A"]["status"], "SIAP")
        self.assertEqual(a["A"]["harga_minimum"], 100000)
        self.assertEqual(a["A"]["margin_rencana"], 150000 - 15000 - 90000)
        self.assertEqual(a["A"]["umur_stok_hari"], 200)
        # A: modal 1.800.000 (maks), umur 200 (maks) -> 100. B: 60*1.000.000/1.800.000 + 40*47/200
        self.assertEqual(a["A"]["skor"], 100.0)
        self.assertEqual(a["B"]["skor"], round(60 * 1_000_000 / 1_800_000 + 40 * 47 / 200, 1))
        self.assertEqual([r["sku"] for r in rows], ["A", "B"])

    def test_harga_rencana_rugi_tidak_siap(self):
        rows = katalog([stok("A", 5, "95000")], [hpp("A", 90000)], [info("A")], 10, HARI_INI)
        self.assertEqual(rows[0]["status"], "DATA_KURANG")
        self.assertIn("HARGA_RENCANA_DI_BAWAH_MINIMUM", rows[0]["catatan"])
        self.assertIsNone(rows[0]["skor"])

    def test_data_kurang_ditandai_tidak_ditebak(self):
        rows = katalog([stok("A", 5, "150000"), stok("B", "", "150000"), stok("C", 5, "", tgl=""),
                        stok("D", 5, "150000")],
                       [hpp("A", ""), hpp("B", 90000), hpp("C", 90000), hpp("D", 90000)],
                       [info("A"), info("B"), info("C"), info("D", "")], 10, HARI_INI)
        c = {r["sku"]: r["catatan"] for r in rows}
        self.assertIn("HPP_KOSONG", c["A"])
        self.assertIn("STOK_KOSONG", c["B"])
        self.assertIn("HARGA_KOSONG", c["C"])
        self.assertIn("TANGGAL_MASUK_KOSONG", c["C"])
        self.assertIn("FAKTA_PRODUK_KOSONG", c["D"])
        self.assertTrue(all(r["status"] == "DATA_KURANG" for r in rows))

    def test_hpp_dobel_dan_sku_dobel(self):
        rows = katalog([stok("A", 5, "150000"), stok("a", 3, "150000")], [hpp("A", 90000), hpp("A", 95000)],
                       [info("A")], 10, HARI_INI)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["stok"], 8)
        self.assertIn("SKU_DOBEL", rows[0]["catatan"])
        self.assertIn("HPP_DOBEL", rows[0]["catatan"])

    def test_tanggal_tidak_terbaca_berhenti(self):
        with self.assertRaises(ValueError):
            katalog([stok("A", 5, "150000", "kemarin")], [hpp("A", 90000)], [info("A")], 10, HARI_INI)

    def test_kolom_wajib_tidak_ada(self):
        with self.assertRaisesRegex(ValueError, "tanggal"):
            katalog([{"SKU": "A", "Nama": "x", "Stok": 1, "Harga": 1}], [hpp("A", 1)], [info("A")], 10, HARI_INI)

    def test_catatan_pemilik_ikut(self):
        rows = katalog([stok("A", 5, "150000", catatan="warna agak pudar")], [hpp("A", 90000)], [info("A")], 10,
                       HARI_INI)
        self.assertEqual(rows[0]["status"], "SIAP")
        self.assertIn("pemilik: warna agak pudar", rows[0]["catatan"])

    def test_cli(self):
        d = pathlib.Path(tempfile.mkdtemp())
        for nama, rows in {"stok.csv": [stok("A", 5, "150000")], "hpp.csv": [hpp("A", 90000)],
                           "info.csv": [info("A")]}.items():
            with open(d / nama, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        args = ["--stok", str(d / "stok.csv"), "--hpp", str(d / "hpp.csv"), "--info", str(d / "info.csv"),
                "--admin-persen", "10", "--hari-ini", "2026-11-17", "--out", str(d / "katalog.csv")]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(stok_gudang.main(args), 0)
        self.assertEqual(json.loads(out.getvalue())["siap"], ["A"])
        with open(d / "katalog.csv", newline="") as f:
            self.assertEqual(next(csv.DictReader(f))["status"], "SIAP")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(stok_gudang.main(args[:1] + [str(d / "tidak-ada.csv")] + args[2:]), 2)


if __name__ == "__main__":
    unittest.main()
