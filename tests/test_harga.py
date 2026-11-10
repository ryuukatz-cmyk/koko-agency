import sys, unittest, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from harga import harga_minimum, hitung


class TestHarga(unittest.TestCase):
    def test_minimum_bulat(self):
        self.assertEqual(harga_minimum(90000, 10), 100000)

    def test_minimum_dibulatkan_ke_atas(self):
        # 100001 / 0.9 = 111112.22 -> 111113
        self.assertEqual(harga_minimum(100001, 10), 111113)

    def test_diskon_pas_di_batas_lulus(self):
        r = hitung(125000, 90000, 10, diskon_persen=20)
        self.assertEqual(r["harga_akhir"], 100000)
        self.assertEqual(r["biaya_admin"], 10000)
        self.assertEqual(r["terima_bersih"], 90000)
        self.assertEqual(r["margin_rp"], 0)
        self.assertTrue(r["lulus"])

    def test_diskon_lewat_batas_ditolak(self):
        r = hitung(125000, 90000, 10, diskon_persen=21)
        self.assertEqual(r["harga_akhir"], 98750)
        self.assertFalse(r["lulus"])
        self.assertLess(r["margin_rp"], 0)

    def test_voucher_mengurangi_harga(self):
        r = hitung(150000, 90000, 10, diskon_persen=10, voucher_rp=5000)
        self.assertEqual(r["harga_akhir"], 130000)
        self.assertTrue(r["lulus"])

    def test_hpp_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            hitung(150000, None, 10)

    def test_diskon_tidak_masuk_akal_ditolak(self):
        for d in (-1, 101):
            with self.assertRaises(ValueError):
                hitung(150000, 90000, 10, diskon_persen=d)

    def test_voucher_melebihi_harga_ditolak(self):
        with self.assertRaises(ValueError):
            hitung(50000, 30000, 10, voucher_rp=60000)

    def test_cli_error_input_exit_2_beda_dengan_tidak_lulus(self):
        import subprocess
        skrip = str(pathlib.Path(__file__).resolve().parent.parent / "scripts" / "harga.py")
        jalan = lambda *a: subprocess.run([sys.executable, skrip, "--harga-normal", "150000", "--admin-persen", "10", *a], capture_output=True).returncode
        self.assertEqual(jalan("--hpp", "90000", "--diskon-persen", "35"), 1)
        self.assertEqual(jalan("--hpp", "0"), 2)

    def test_admin_100_persen_ditolak(self):
        with self.assertRaises(ValueError):
            harga_minimum(90000, 100)


if __name__ == "__main__":
    unittest.main()
