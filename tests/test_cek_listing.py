import sys, unittest, pathlib, tempfile, csv, json, io, contextlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import cek_listing
from cek_listing import cek, _admin

PRODUK = [{"sku": "KOKO-A", "hpp": "90000", "fakta_boleh_diklaim": "lengan panjang;bordir dada kiri;katun"}]
ADMIN = {"shopee": 10, "tiktok": 10}


def baris(**ubah):
    r = {"sku": "KOKO-A", "platform": "shopee",
         "judul": "Baju Koko Pria Lengan Panjang Bordir Dada Kiri Katun Navy M L XL",
         "deskripsi": "Koko lengan panjang, bordir dada kiri, bahan katun.", "harga_normal": "150000",
         "harga_coret": "", "harga_akhir": "150000", "taktik": "voucher toko", "kata_kunci": "baju koko pria;koko bordir",
         "caption_video": "Koko navy bordir dada kiri"}
    r.update(ubah)
    return r


def masalah(hasil):
    return " | ".join(m for b in hasil["baris"] for m in b["masalah"])


class TestCekListing(unittest.TestCase):
    def test_listing_benar_lulus(self):
        r = cek([baris(), baris(platform="tiktok")], PRODUK, ADMIN, "toko-baru")
        self.assertTrue(r["lulus"], masalah(r))

    def test_judul_terlalu_panjang_untuk_shopee(self):
        r = cek([baris(judul="baju koko pria " + "x" * 100)], PRODUK, ADMIN, "toko-baru")
        self.assertIn("panjang judul", masalah(r))
        # judul yang sama masih muat untuk tiktok (batas lebih panjang, ASUMSI)
        self.assertTrue(cek([baris(platform="tiktok", judul="baju koko pria " + "x" * 100)], PRODUK, ADMIN,
                            "toko-baru")["lulus"])

    def test_kata_kunci_utama_wajib_di_judul(self):
        r = cek([baris(kata_kunci="kemeja muslim;koko")], PRODUK, ADMIN, "toko-baru")
        self.assertIn("kata kunci utama 'kemeja muslim'", masalah(r))

    def test_klaim_palsu_ditolak_kecuali_ada_di_fakta(self):
        r = cek([baris(deskripsi="Bahan premium anti luntur, best seller!")], PRODUK, ADMIN, "toko-baru")
        for k in ("premium", "anti luntur", "best seller"):
            self.assertIn(repr(k), masalah(r))
        produk = [{**PRODUK[0], "fakta_boleh_diklaim": PRODUK[0]["fakta_boleh_diklaim"] + ";premium"}]
        self.assertNotIn("'premium'", masalah(cek([baris(deskripsi="Bahan premium")], produk, ADMIN, "toko-baru")))

    def test_kata_mirip_tidak_salah_tangkap(self):
        # "palingkan" bukan "paling"
        self.assertTrue(cek([baris(deskripsi="Jangan palingkan pandangan, koko katun.")], PRODUK, ADMIN,
                            "toko-baru")["lulus"])

    def test_harga_di_bawah_minimum(self):
        r = cek([baris(harga_akhir="99000")], PRODUK, ADMIN, "toko-baru")
        self.assertIn("di bawah harga minimum 100000", masalah(r))

    def test_toko_baru_tanpa_harga_coret(self):
        r = cek([baris(harga_coret="200000", harga_normal="200000", harga_akhir="150000")], PRODUK, ADMIN, "toko-baru")
        self.assertIn("harga coret dilarang", masalah(r))
        self.assertTrue(cek([baris(harga_coret="200000", harga_normal="200000", harga_akhir="150000")], PRODUK,
                            ADMIN, "deadstock")["lulus"])

    def test_admin_per_platform(self):
        self.assertEqual(_admin("shopee=10,tiktok=8"), {"shopee": 10.0, "tiktok": 8.0})
        self.assertEqual(_admin("10"), {"shopee": 10.0, "tiktok": 10.0})
        with self.assertRaises(ValueError):
            _admin("shopee=10")
        # admin tiktok 8% -> minimum 97827, jadi 98000 lulus di tiktok (di shopee minimum 100000)
        r = cek([baris(platform="tiktok", harga_akhir="98000")], PRODUK, _admin("shopee=10,tiktok=8"), "toko-baru")
        self.assertTrue(r["lulus"], masalah(r))

    def test_sku_tidak_dikenal_dan_platform_salah(self):
        r = cek([baris(sku="X"), baris(platform="lazada")], PRODUK, ADMIN, "toko-baru")
        self.assertIn("tidak ada di produk.csv", masalah(r))
        self.assertIn("platform harus", masalah(r))

    def test_baris_dobel(self):
        self.assertIn("dobel", masalah(cek([baris(), baris()], PRODUK, ADMIN, "toko-baru")))

    def test_cli_exit_code(self):
        d = pathlib.Path(tempfile.mkdtemp())
        for nama, rows in {"listing.csv": [baris()], "produk.csv": PRODUK}.items():
            with open(d / nama, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        args = ["--listing", str(d / "listing.csv"), "--produk", str(d / "produk.csv"), "--admin-persen", "10",
                "--mode", "toko-baru"]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cek_listing.main(args), 0)
            self.assertEqual(cek_listing.main(args[:-1] + ["deadstock"]), 0)
            self.assertEqual(cek_listing.main(["--listing", str(d / "x.csv")] + args[2:]), 2)


if __name__ == "__main__":
    unittest.main()
