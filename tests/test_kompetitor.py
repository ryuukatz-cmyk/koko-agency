import sys, unittest, pathlib, datetime, tempfile, subprocess, csv
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from kompetitor import ringkas, KOLOM

HARI_INI = datetime.date(2026, 11, 10)
SKRIP = str(pathlib.Path(__file__).resolve().parent.parent / "scripts" / "kompetitor.py")


def baris(harga, sumber="halaman", link=None, dicek="2026-11-10", n=[0]):
    n[0] += 1
    return {"sku_kita": "KOKO-A", "platform": "tokopedia", "toko": f"toko{n[0]}", "judul": "Koko navy bordir",
            "harga": harga, "harga_coret": "", "terjual": "", "rating": "",
            "link": link if link is not None else f"https://www.tokopedia.com/toko/p{n[0]}",
            "sumber": sumber, "dicek_pada": dicek}


LIMA = [baris(h) for h in ("Rp100.000", "Rp120.000", "Rp150.000", "Rp180.000", "Rp200.000")]


class TestKompetitor(unittest.TestCase):
    def test_hanya_terverifikasi_dihitung(self):
        r = ringkas(LIMA + [baris("Rp50.000", "cuplikan"), baris("Rp300.000", "cuplikan")], HARI_INI)
        self.assertEqual((r["harga_min"], r["harga_median"], r["harga_max"]), (100000, 150000, 200000))
        self.assertEqual((r["terverifikasi"], r["cuplikan"], r["status"]), (5, 2, "CUKUP"))
        self.assertEqual(r["ditolak"], [])

    def test_chrome_juga_terverifikasi(self):
        r = ringkas(LIMA[:4] + [baris("Rp110.000", "chrome")], HARI_INI)
        self.assertEqual(r["status"], "CUKUP")

    def test_kurang_dari_lima_data_kurang(self):
        r = ringkas(LIMA[:4] + [baris("Rp90.000", "cuplikan")], HARI_INI)
        self.assertEqual((r["terverifikasi"], r["status"]), (4, "DATA_KURANG"))

    def test_kosong_data_kurang_tanpa_angka(self):
        r = ringkas([], HARI_INI)
        self.assertEqual(r["status"], "DATA_KURANG")
        self.assertIsNone(r["harga_median"])

    def test_baris_bermasalah_ditolak_dengan_alasan(self):
        buruk = [baris("Rp100.000", link=""), baris("Rp100.000", sumber="kira-kira"),
                 baris("Rp100.000", dicek=""), baris("Rp100.000", dicek="2026-12-01"), baris("125rb")]
        r = ringkas(LIMA + buruk, HARI_INI)
        self.assertEqual(r["terverifikasi"], 5)
        self.assertEqual([d["baris"] for d in r["ditolak"]], [6, 7, 8, 9, 10])
        alasan = " ".join(d["alasan"] for d in r["ditolak"])
        for kata in ("link", "sumber", "tanggal", "masa depan", "harga"):
            self.assertIn(kata, alasan)

    def test_link_dobel_dihitung_sekali(self):
        r = ringkas(LIMA + [baris("Rp999.000", link=LIMA[0]["link"])], HARI_INI)
        self.assertEqual(r["terverifikasi"], 5)
        self.assertEqual(r["harga_max"], 200000)
        self.assertIn("dobel", r["ditolak"][0]["alasan"])

    def test_median_genap_pakai_harga_nyata(self):
        r = ringkas(LIMA + [baris("Rp210.000")], HARI_INI)
        self.assertEqual(r["harga_median"], 150000)

    def test_posisi_harga_kita(self):
        r = ringkas(LIMA, HARI_INI, harga_kita=130000)
        self.assertEqual(r["lebih_murah_dari_kita"], 2)

    def test_cli_exit_code(self):
        d = pathlib.Path(tempfile.mkdtemp())
        def tulis(nama, rows, kolom=KOLOM):
            p = d / nama
            with open(p, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=kolom, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
            return str(p)
        jalan = lambda p: subprocess.run([sys.executable, SKRIP, "--csv", p, "--hari-ini", "2026-11-10"], capture_output=True).returncode
        self.assertEqual(jalan(tulis("a.csv", LIMA)), 0)
        self.assertEqual(jalan(tulis("b.csv", LIMA[:2])), 1)
        self.assertEqual(jalan(tulis("c.csv", LIMA, kolom=["sku_kita", "harga"])), 2)


if __name__ == "__main__":
    unittest.main()
