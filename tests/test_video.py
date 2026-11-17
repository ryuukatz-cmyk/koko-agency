import sys, unittest, pathlib, tempfile, subprocess
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import video
from PIL import Image


def foto(d, n, warna="navy"):
    p = []
    for i in range(1, n + 1):
        f = d / f"F{i:02d}.png"
        Image.new("RGB", (640, 640), warna).save(f)
        p.append(f)
    return p


def klip(path, detik, ukuran="1280x720"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc=size={ukuran}:rate=30:duration={detik}",
                    "-pix_fmt", "yuv420p", str(path)], check=True)


class TestVideo(unittest.TestCase):
    def setUp(self):
        self.d = pathlib.Path(tempfile.mkdtemp())

    def test_durasi_per_foto(self):
        self.assertAlmostEqual(video.durasi_per_foto(10) * 10 - 9 * video.TRANSISI, 25.5)
        self.assertAlmostEqual(video.durasi_per_foto(1), 15)
        total12 = video.durasi_per_foto(12) * 12 - 11 * video.TRANSISI
        self.assertLessEqual(total12, 30)
        total3 = video.durasi_per_foto(3) * 3 - 2 * video.TRANSISI
        self.assertGreaterEqual(total3, 15)

    def test_slideshow_3_foto_9x16(self):
        out = self.d / "a.mp4"
        hasil = video.buat(foto(self.d, 3), None, "Koko Navy", "Rp 99.000", out)
        self.assertEqual(hasil["mode"], "slideshow")
        c = video.cek(out)
        self.assertTrue(c["ok"], c)
        self.assertEqual((c["lebar"], c["tinggi"]), (1080, 1920))
        self.assertFalse(c["ada_audio"])

    def test_folder_flow_kosong_pakai_slideshow(self):
        (self.d / "flow").mkdir()
        hasil = video.buat(foto(self.d, 2), self.d / "flow", "Koko", "Rp 1", self.d / "b.mp4")
        self.assertEqual(hasil["mode"], "slideshow")

    def test_klip_flow_dipotong_dan_9x16(self):
        fl = self.d / "flow"; fl.mkdir()
        for i in range(1, 5):
            klip(fl / f"V{i:02d}.mp4", 8)
        hasil = video.buat(foto(self.d, 4), fl, "Koko", "Rp 99.000", self.d / "c.mp4")
        self.assertEqual(hasil["mode"], "flow")
        c = video.cek(self.d / "c.mp4")
        self.assertTrue(c["ok"], c)

    def test_klip_flow_terlalu_pendek_ditolak(self):
        fl = self.d / "flow"; fl.mkdir()
        klip(fl / "V01.mp4", 3)
        with self.assertRaisesRegex(ValueError, "pendek"):
            video.buat(foto(self.d, 1), fl, "Koko", "Rp 1", self.d / "d.mp4")

    def test_klip_flow_tidak_berpasangan_ditolak(self):
        fl = self.d / "flow"; fl.mkdir()
        for i in (1, 2):
            klip(fl / f"V{i:02d}.mp4", 8)
        with self.assertRaisesRegex(ValueError, "F03"):
            video.buat(foto(self.d, 3), fl, "Koko", "Rp 1", self.d / "f.mp4")

    def test_folder_foto_ditolak_harus_daftar_lulus(self):
        foto(self.d, 2)
        with self.assertRaisesRegex(ValueError, "LULUS"):
            video.buat(self.d, None, "Koko", "Rp 1", self.d / "g.mp4")

    def test_cek_video_beraudio_tidak_ok(self):
        p = self.d / "audio.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=white:s=1080x1920:d=16:r=30",
                        "-f", "lavfi", "-i", "sine=d=16", "-shortest", "-pix_fmt", "yuv420p", str(p)], check=True)
        c = video.cek(p)
        self.assertTrue(c["ada_audio"])
        self.assertFalse(c["ok"])

    def test_cek_file_rusak(self):
        rusak = self.d / "rusak.mp4"
        rusak.write_bytes(b"bukan video")
        self.assertFalse(video.cek(rusak)["ok"])

    def test_tanpa_foto_ditolak(self):
        with self.assertRaises(ValueError):
            video.buat([], None, "K", "Rp 1", self.d / "e.mp4")


class TestUkuranFont(unittest.TestCase):
    def test_nama_panjang_dikecilkan_supaya_muat(self):
        import video
        from PIL import ImageFont
        f = video._font()
        nama = "Koko Lengan Panjang Putih Bordir Emas Kerah Shanghai"
        s = video.ukuran_font(nama, f, 64)
        self.assertLess(s, 64)
        self.assertLessEqual(ImageFont.truetype(f, s).getlength(nama), video.W - 2 * 60 - 2 * 24)
        self.assertEqual(video.ukuran_font("Koko Navy", f, 64), 64)


if __name__ == "__main__":
    unittest.main()
