import sys, unittest, pathlib, csv, tempfile, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from export import angka, buang_data_pembeli, ringkas_per_sku, baca_tabel

PEMBELI = ["Username (Pembeli)", "Nama Penerima", "No. Telepon", "Alamat Pengiriman",
           "Kota/Kabupaten", "Provinsi", "Kode Pos", "Catatan dari Pembeli"]
HARI_INI = datetime.date(2026, 11, 10)


def pesanan(sku, tgl, jumlah=1, status="Selesai"):
    r = {"No. Pesanan": "X", "Status Pesanan": status, "Waktu Pesanan Dibuat": tgl,
         "Nomor Referensi SKU": sku, "Jumlah": str(jumlah)}
    r.update({k: "rahasia" for k in PEMBELI})
    return r


def stok(sku, n, harga="Rp 150.000", nama="Koko"):
    return {"SKU": sku, "Nama Produk": nama, "Stok": str(n), "Harga": harga}


class TestAngka(unittest.TestCase):
    def test_format_indonesia(self):
        self.assertEqual(angka("Rp 125.000"), 125000)
        self.assertEqual(angka("125.000,00"), 125000)
        self.assertEqual(angka("7"), 7)

    def test_kosong_tetap_kosong(self):
        self.assertIsNone(angka(""))
        self.assertIsNone(angka(None))
        self.assertIsNone(angka("-"))


class TestBuangDataPembeli(unittest.TestCase):
    def test_semua_kolom_pembeli_hilang(self):
        hasil = buang_data_pembeli([pesanan("A", "2026-01-01 10:00")])
        for k in PEMBELI:
            self.assertNotIn(k, hasil[0])
        self.assertEqual(hasil[0]["Nomor Referensi SKU"], "A")

    def test_nama_kolom_beda_huruf_dan_spasi_tetap_dibuang(self):
        hasil = buang_data_pembeli([{" no. TELEPON ": "08123", "SKU": "A"}])
        self.assertEqual(list(hasil[0]), ["SKU"])

    def test_tidak_ada_isi_pembeli_di_ringkasan(self):
        rows = ringkas_per_sku([pesanan("A", "2026-01-01 10:00")], [stok("A", 10)], [], HARI_INI)
        teks = repr(rows)
        self.assertNotIn("rahasia", teks)


class TestRingkas(unittest.TestCase):
    def test_hitung_terjual_dan_hari(self):
        rows = ringkas_per_sku(
            [pesanan("A", "2026-09-01 10:00", 2), pesanan("A", "2026-10-11 09:00", 1),
             pesanan("A", "2026-11-01 09:00", 5, status="Batal")],
            [stok("A", 10)], [{"SKU": "A", "HPP": "90.000"}], HARI_INI)
        r = rows[0]
        self.assertEqual(r["unit_terjual"], 3)
        self.assertEqual(r["terakhir_terjual"], "2026-10-11")
        self.assertEqual(r["hari_tanpa_jual"], 30)
        self.assertEqual(r["hpp"], 90000)
        self.assertEqual(r["harga"], 150000)
        self.assertEqual(r["catatan"], "")

    def test_tidak_pernah_terjual(self):
        rows = ringkas_per_sku([pesanan("A", "2026-05-14 10:00")],
                               [stok("A", 10), stok("B", 8)], [], HARI_INI)
        b = [r for r in rows if r["sku"] == "B"][0]
        self.assertEqual(b["unit_terjual"], 0)
        self.assertEqual(b["terakhir_terjual"], "")
        self.assertEqual(b["hari_tanpa_jual"], 180)
        self.assertIn("TIDAK_TERJUAL_SEPANJANG_DATA", b["catatan"])

    def test_hpp_kosong_ditandai_bukan_diisi(self):
        rows = ringkas_per_sku([], [stok("A", 10)], [{"SKU": "A", "HPP": ""}], HARI_INI)
        self.assertIsNone(rows[0]["hpp"])
        self.assertIn("HPP_KOSONG", rows[0]["catatan"])

    def test_sku_dobel_ditandai(self):
        rows = ringkas_per_sku([], [stok("A", 10), stok("A", 3)], [], HARI_INI)
        self.assertEqual(len(rows), 1)
        self.assertIn("SKU_DOBEL", rows[0]["catatan"])

    def test_kolom_wajib_hilang_menyebut_namanya(self):
        with self.assertRaisesRegex(ValueError, "Stok"):
            ringkas_per_sku([], [{"SKU": "A", "Nama Produk": "K", "Harga": "1"}], [], HARI_INI)


class TestBacaTabel(unittest.TestCase):
    def test_baca_csv(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:
            w = csv.writer(f); w.writerow(["SKU", "Stok"]); w.writerow(["A", "5"])
        self.assertEqual(baca_tabel(f.name), [{"SKU": "A", "Stok": "5"}])

    def test_baca_xlsx(self):
        import openpyxl
        wb = openpyxl.Workbook(); ws = wb.active
        ws.append(["SKU", "Stok"]); ws.append(["A", 5])
        p = tempfile.mktemp(suffix=".xlsx"); wb.save(p)
        self.assertEqual(baca_tabel(p), [{"SKU": "A", "Stok": "5"}])


if __name__ == "__main__":
    unittest.main()
