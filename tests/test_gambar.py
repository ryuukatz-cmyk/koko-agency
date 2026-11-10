import sys, unittest, pathlib, json, base64, tempfile, os, io
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import gambar
from PIL import Image

PNG = io.BytesIO(); Image.new("RGB", (8, 8), "navy").save(PNG, "PNG"); PNG = PNG.getvalue()
MODELS = json.dumps({"models": [{"name": "models/gemini-3.1-flash-image"}, {"name": "models/gemini-flash-latest"}]}).encode()


class Palsu:
    """Pengganti curl: mencatat argumen dan mengembalikan jawaban yang diatur per provider."""
    def __init__(self, gemini=(429, b'{"error":{"code":429,"message":"limit: 0"}}'), cf=None):
        self.panggilan, self.gemini, self.cf = [], gemini, cf or (200, json.dumps({"success": True, "result": {"image": base64.b64encode(PNG).decode()}}).encode())

    def __call__(self, args):
        self.panggilan.append(args)
        url = args[-1]
        if url.split("?")[0].endswith("/models"):
            return 200, MODELS
        if "generativelanguage" in url:
            return self.gemini
        if "api.cloudflare.com" in url:
            return self.cf
        raise AssertionError(url)

    def hitung(self, kata):
        return sum(1 for a in self.panggilan if kata in a[-1])


def siapkan(n=3):
    d = pathlib.Path(tempfile.mkdtemp())
    Image.new("RGB", (1200, 1600), "white").save(d / "master.png")
    (d / "prompt-foto.md").write_text("".join(f"## F{i:02d}\nfoto koko scene {i}\n\n" for i in range(1, n + 1)))
    return d


class TestGambar(unittest.TestCase):
    def setUp(self):
        self._asli = gambar._post
        os.environ.pop("CF_ACCOUNT_ID", None)

    def tearDown(self):
        gambar._post = self._asli
        os.environ.pop("CF_ACCOUNT_ID", None)

    def test_baca_prompt(self):
        d = siapkan(10)
        p = gambar.baca_prompt(d / "prompt-foto.md")
        self.assertEqual(list(p), [f"F{i:02d}" for i in range(1, 11)])
        self.assertEqual(p["F03"], "foto koko scene 3")

    def test_gemini_429_jatuh_ke_cloudflare(self):
        os.environ["CF_ACCOUNT_ID"] = "akun123"
        palsu = gambar._post = Palsu()
        d = siapkan(3)
        hasil = gambar.buat(d / "master.png", d)
        self.assertEqual(hasil["status"], "SELESAI")
        meta = json.loads((d / "foto" / "metadata.json").read_text())
        self.assertEqual([m["provider"] for m in meta["foto"]], ["cloudflare"] * 3)
        self.assertEqual(meta["foto"][0]["model"], "@cf/black-forest-labs/flux-2-klein-4b")
        self.assertIn("429", meta["gagal"][0]["alasan"])
        self.assertTrue((d / "foto" / "F03.png").stat().st_size > 0)
        # Gemini yang gagal tidak dipanggil lagi untuk foto berikutnya
        self.assertEqual(palsu.hitung(":generateContent"), 1)
        self.assertIn("accounts/akun123/ai/run/@cf/black-forest-labs/flux-2-klein-4b", palsu.panggilan[-1][-1])

    def test_gagal_sementara_tidak_membuang_provider(self):
        ok = json.dumps({"candidates": [{"content": {"parts": [{"inlineData": {"mimeType": "image/png", "data": base64.b64encode(PNG).decode()}}]}}]}).encode()
        palsu = Palsu(gemini=(200, ok))
        jawab = iter([(503, b"sibuk"), (200, ok), (200, ok)])
        asli = palsu.__call__
        gambar._post = lambda a: next(jawab) if ":generateContent" in a[-1] else asli(a)
        d = siapkan(2)
        hasil = gambar.buat(d / "master.png", d)
        # F01: 503 lalu tidak ada provider lain -> kurang; F02 tetap dicoba Gemini
        self.assertEqual(hasil["kurang"], ["F01"])
        self.assertEqual(hasil["dibuat"], ["F02"])

    def test_model_preview_tetap_dikenali(self):
        gambar._post = lambda a: (200, json.dumps({"models": [{"name": "models/gemini-3.1-flash-image-preview"}]}).encode())
        self.assertEqual(gambar._gemini_model(), "gemini-3.1-flash-image-preview")

    def test_jawaban_aneh_tidak_membuat_crash(self):
        os.environ["CF_ACCOUNT_ID"] = "akun123"
        gambar._post = Palsu(cf=(200, b'{"success": true, "result": null}'))
        d = siapkan(1)
        self.assertEqual(gambar.buat(d / "master.png", d)["status"], "WAITING_FOTO")

    def test_foto_lama_dibersihkan_sebelum_buat_ulang(self):
        gambar._post = Palsu()
        d = siapkan(1)
        (d / "foto").mkdir(); (d / "foto" / "F01.png").write_bytes(b"lama")
        gambar.buat(d / "master.png", d, akun_cf_file=d / "x.txt")
        self.assertFalse((d / "foto" / "F01.png").exists())

    def test_curl_tidak_membaca_curlrc(self):
        import subprocess as sp
        tangkap = {}
        asli = sp.run
        def run(args, **kw):
            tangkap["args"] = args
            raise RuntimeError("berhenti")
        gambar.subprocess.run = run
        try:
            with self.assertRaises(RuntimeError):
                self._asli(["https://x"])
        finally:
            gambar.subprocess.run = asli
        self.assertEqual(tangkap["args"][:2], ["curl", "-q"])

    def test_tanpa_akun_cloudflare_jatuh_ke_manual(self):
        gambar._post = Palsu()
        d = siapkan(10)
        hasil = gambar.buat(d / "master.png", d, akun_cf_file=d / "tidak-ada.txt")
        self.assertEqual(hasil["status"], "WAITING_FOTO")
        self.assertEqual(hasil["kurang"], [f"F{i:02d}" for i in range(1, 11)])
        meta = json.loads((d / "foto" / "metadata.json").read_text())
        self.assertTrue(any("CF_ACCOUNT_ID" in g["alasan"] for g in meta["gagal"]))

    def test_gemini_berhasil(self):
        ok = json.dumps({"candidates": [{"content": {"parts": [{"inlineData": {"mimeType": "image/png", "data": base64.b64encode(PNG).decode()}}]}}]}).encode()
        gambar._post = Palsu(gemini=(200, ok))
        d = siapkan(2)
        hasil = gambar.buat(d / "master.png", d)
        self.assertEqual(hasil["status"], "SELESAI")
        meta = json.loads((d / "foto" / "metadata.json").read_text())
        self.assertEqual(meta["foto"][1], {**meta["foto"][1], "id": "F02", "provider": "gemini", "model": "gemini-3.1-flash-image"})

    def test_cloudflare_mengembalikan_gambar_mentah(self):
        os.environ["CF_ACCOUNT_ID"] = "akun123"
        gambar._post = Palsu(cf=(200, PNG))
        d = siapkan(1)
        self.assertEqual(gambar.buat(d / "master.png", d)["status"], "SELESAI")

    def test_tidak_pernah_mengirim_authorization(self):
        os.environ["CF_ACCOUNT_ID"] = "akun123"
        palsu = gambar._post = Palsu()
        d = siapkan(2)
        gambar.buat(d / "master.png", d)
        for a in palsu.panggilan:
            self.assertFalse(any("authorization" in str(x).lower() for x in a), a)

    def test_input_cloudflare_lebih_kecil_dari_512(self):
        d = siapkan(1)
        kecil = gambar.kecilkan(d / "master.png", d / "kecil.png")
        with Image.open(kecil) as im:
            self.assertLess(max(im.size), 512)


if __name__ == "__main__":
    unittest.main()
