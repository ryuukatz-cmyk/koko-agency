import sys, unittest, pathlib, datetime, json, tempfile, csv, io, contextlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import ukur

SEJAK, HARI_INI = datetime.date(2026, 12, 1), datetime.date(2026, 12, 20)
KATALOG = [{"sku": "A", "stok": "40", "hpp": "85000"}, {"sku": "B", "stok": "10", "hpp": ""}]
LISTING = [{"sku": "A", "platform": "shopee", "harga_akhir": "159000"},
           {"sku": "A", "platform": "tiktok", "harga_akhir": "165000"}]


def p(sku, tgl, n=1, status="Selesai"):
    return {"Nomor Referensi SKU": sku, "Waktu Pesanan Dibuat": tgl, "Jumlah": str(n), "Status Pesanan": status,
            "Nama Penerima": "Budi Palsu", "No. Telepon": "0812000"}


class TestUkur(unittest.TestCase):
    def test_hitung_dan_data_pembeli_tidak_bocor(self):
        rows = ukur.ukur([p("A", "2026-12-02 10:00", 2), p("A", "2026-12-09 10:00", 3), p("A", "2026-12-10", 1, "Batal"),
                          p("A", "2026-11-20", 5), p("B", "2026-12-05", 1)], KATALOG, LISTING, 10, SEJAK, HARI_INI)
        a = {r["sku"]: r for r in rows}["A"]
        self.assertEqual(a["unit_terjual"], 5)          # 20 Nov sebelum tayang, batal tidak dihitung
        self.assertEqual(a["unit_batal"], 1)
        self.assertEqual(a["sisa_stok_perkiraan"], 35)
        self.assertEqual(a["harga_akhir"], 159000)      # harga shopee, bukan tiktok
        self.assertEqual(a["uang_masuk_bersih"], 5 * (159000 - 15900))
        self.assertEqual(a["modal_kembali_persen"], 12.5)
        self.assertEqual(json.loads(a["per_minggu"]), {"2026-W49": 2, "2026-W50": 3})
        self.assertNotIn("Budi", json.dumps(rows))
        b = {r["sku"]: r for r in rows}["B"]
        self.assertIsNone(b["uang_masuk_bersih"])
        self.assertIn("HPP kosong", b["catatan"])

    def test_tanggal_rusak_berhenti(self):
        with self.assertRaises(ValueError):
            ukur.ukur([p("A", "kemarin")], KATALOG, LISTING, 10, SEJAK, HARI_INI)

    def test_cli(self):
        d = pathlib.Path(tempfile.mkdtemp())
        for nama, rows in {"pesanan.csv": [p("A", "2026-12-02", 2)], "katalog.csv": KATALOG,
                           "listing.csv": LISTING}.items():
            with open(d / nama, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        args = ["--pesanan", str(d / "pesanan.csv"), "--katalog", str(d / "katalog.csv"), "--listing",
                str(d / "listing.csv"), "--admin-persen", "10", "--sejak", "2026-12-01", "--hari-ini", "2026-12-20",
                "--out", str(d / "hasil.csv")]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(ukur.main(args), 0)
        self.assertEqual(json.loads(out.getvalue())["unit_terjual"], 2)
        self.assertNotIn("Budi", (d / "hasil.csv").read_text())


if __name__ == "__main__":
    unittest.main()
