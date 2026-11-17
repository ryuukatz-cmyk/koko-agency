import sys, unittest, pathlib, tempfile, csv, io, contextlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import cek_konten
from cek_konten import cek

PRODUK = [{"sku": "KOKO-A", "fakta_boleh_diklaim": "lengan panjang;bordir dada kiri;katun"}]
LISTING = [{"sku": "KOKO-A", "platform": "shopee", "harga_akhir": "159000"}]


def b(**ubah):
    r = {"tanggal": "2026-12-01", "platform": "tiktok", "format": "close-up", "pilar": "produk", "sku": "KOKO-A",
         "hook": "Bordir dada kiri ini dijahit rapi, lihat dari dekat", "naskah": "1) close-up bordir 2) badan penuh 3) harga",
         "cta": "Cek keranjang kuning", "tagar": "#bajukoko #kokopria", "aset": "F05.png", "harga_ditampilkan": ""}
    r.update(ubah)
    return r


def masalah(r):
    return " | ".join(m for x in r["baris"] for m in x["masalah"])


class TestCekKonten(unittest.TestCase):
    def test_kalender_benar_lulus(self):
        r = cek([b(), b(tanggal="2026-12-02", platform="instagram", format="carousel", pilar="momen",
                       harga_ditampilkan="159000")], PRODUK, LISTING)
        self.assertTrue(r["lulus"], masalah(r))

    def test_nilai_tidak_sah(self):
        r = cek([b(tanggal="1 Des", platform="youtube", format="vlog", pilar="random", hook="", naskah="")], PRODUK)
        for kata in ("tanggal tidak valid", "platform", "format", "pilar", "hook kosong", "naskah kosong"):
            self.assertIn(kata, masalah(r))

    def test_hook_terlalu_panjang_dan_tagar_kebanyakan(self):
        r = cek([b(hook="x" * 101, tagar=" ".join(f"#t{i}" for i in range(9)))], PRODUK)
        self.assertIn("hook 101", masalah(r))
        self.assertIn("tagar 9", masalah(r))

    def test_klaim_palsu_ditolak(self):
        r = cek([b(naskah="Koko terlaris, bahan premium anti luntur")], PRODUK)
        for k in ("terlaris", "premium", "anti luntur"):
            self.assertIn(repr(k), masalah(r))

    def test_harga_harus_sama_dengan_listing(self):
        self.assertIn("tidak sama dengan harga akhir", masalah(cek([b(harga_ditampilkan="149000")], PRODUK, LISTING)))
        self.assertIn("tidak ada", masalah(cek([b(harga_ditampilkan="159000")], PRODUK)))  # tanpa listing

    def test_sku_tidak_dikenal_dan_terlalu_padat(self):
        r = cek([b(sku="X")] + [b() for _ in range(2)], PRODUK)
        self.assertIn("SKU X", masalah(r))
        self.assertIn("lebih dari 2 konten", masalah(r))

    def test_cli(self):
        d = pathlib.Path(tempfile.mkdtemp())
        for nama, rows in {"k.csv": [b()], "p.csv": PRODUK}.items():
            with open(d / nama, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cek_konten.main(["--kalender", str(d / "k.csv"), "--produk", str(d / "p.csv")]), 0)
            self.assertEqual(cek_konten.main(["--kalender", str(d / "x.csv"), "--produk", str(d / "p.csv")]), 2)


if __name__ == "__main__":
    unittest.main()
