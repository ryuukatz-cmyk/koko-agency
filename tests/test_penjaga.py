import sys, unittest, pathlib, json, subprocess, tempfile
AKAR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AKAR / ".claude" / "hooks"))
sys.path.insert(0, str(AKAR / "scripts"))
import penjaga, status

KUNCI_PALSU = "AIza" + "B" * 35  # dirakit supaya file tes sendiri tidak memuat pola kunci utuh
BERSIH = {"files": [], "diff": ""}


def bash(cmd, staged=BERSIH):
    return penjaga.periksa({"tool_name": "Bash", "tool_input": {"command": cmd}}, staged)


class TestPenjaga(unittest.TestCase):
    def test_header_authorization_ditolak(self):
        self.assertIn("Authorization", bash('curl -H "Author' + 'ization: Bearer abc" https://api.cloudflare.com/x'))

    def test_identitas_browser_palsu_ditolak(self):
        self.assertIsNotNone(bash("curl -A 'Mozilla/5.0' https://shopee.co.id"))
        self.assertIsNotNone(bash("wget --user-agent=x https://tokopedia.com"))

    def test_perintah_biasa_lolos(self):
        for cmd in ("python3 scripts/gambar.py --master a.png --batch batch/x", "git status", "ls -la foto/",
                    "curl -sS https://example.com", "git commit -m 'tambah listing'"):
            self.assertIsNone(bash(cmd), cmd)

    def test_git_data_mentah_dan_env_ditolak(self):
        self.assertIsNotNone(bash("git add data/mentah/pesanan.xlsx"))
        self.assertIsNotNone(bash("git add .env"))
        self.assertIsNotNone(bash("git commit -m x", {"files": ["data/mentah/pesanan.csv"], "diff": ""}))
        self.assertIsNotNone(bash("git commit -m x", {"files": ["scripts/a.py"], "diff": "+k = '" + KUNCI_PALSU + "'"}))
        self.assertIsNone(bash("git commit -m x", {"files": ["data/katalog.csv", "brain/produk.csv"], "diff": "+a"}))

    def test_tulis_kunci_ke_file_ditolak(self):
        r = penjaga.periksa({"tool_name": "Write", "tool_input": {"file_path": "config/x.txt", "content": KUNCI_PALSU}})
        self.assertIsNotNone(r)
        r = penjaga.periksa({"tool_name": "Edit", "tool_input": {"file_path": "a.md", "new_string": "akun ba68056379f1"}})
        self.assertIsNone(r)  # account ID Cloudflare bukan rahasia

    def test_lewat_stdin_exit_code(self):
        p = AKAR / ".claude/hooks/penjaga.py"
        ditolak = subprocess.run([sys.executable, str(p)], input=json.dumps(
            {"tool_name": "Bash", "tool_input": {"command": "git add data/mentah/x.csv"}}), capture_output=True, text=True)
        self.assertEqual(ditolak.returncode, 2)
        self.assertIn("data pembeli", ditolak.stderr)
        lolos = subprocess.run([sys.executable, str(p)], input=json.dumps(
            {"tool_name": "Read", "tool_input": {"file_path": "README.md"}}), capture_output=True, text=True)
        self.assertEqual(lolos.returncode, 0)
        aneh = subprocess.run([sys.executable, str(p)], input="bukan json", capture_output=True, text=True)
        self.assertEqual(aneh.returncode, 0)

    def test_settings_valid_dan_hook_terdaftar(self):
        s = json.loads((AKAR / ".claude/settings.json").read_text())
        perintah = [h["command"] for g in s["hooks"]["PreToolUse"] for h in g["hooks"]]
        self.assertTrue(any("penjaga.py" in c for c in perintah))
        self.assertIn("Read(./data/mentah/**)", s["permissions"]["deny"])


class TestStatus(unittest.TestCase):
    def test_batch_menunggu_pemilik_terdeteksi(self):
        d = pathlib.Path(tempfile.mkdtemp())
        for nama, st in (("2026-12-01-A", "APPROVAL_HARGA"), ("2026-12-01-B", "KONTEN_FOTO"), ("2026-12-01-C", "LIVE")):
            (d / "batch" / nama).mkdir(parents=True)
            (d / "batch" / nama / "status.json").write_text(json.dumps(
                {"batch": nama, "sku": nama[-1], "mode": "toko-baru", "status": st, "riwayat": []}))
        (d / "batch/rusak").mkdir()
        (d / "batch/rusak/status.json").write_text("{")
        r = status.baca(d)
        self.assertEqual({b["batch"] for b in r["menunggu_pemilik"]}, {"2026-12-01-A", "rusak"})
        t = status.teks(r)
        self.assertIn("MENUNGGU PEMILIK 2026-12-01-A [APPROVAL_HARGA]: setujui harga", t)
        self.assertIn("2026-12-01-B", t)
        self.assertNotIn("2026-12-01-B", status.teks(r, singkat=True))

    def test_tanpa_batch(self):
        self.assertIn("Belum ada batch", status.teks(status.baca(tempfile.mkdtemp())))


if __name__ == "__main__":
    unittest.main()
