"""Cek nyata: apakah Cloudflare FLUX bisa dipakai dari environment ini. Jalankan di environment koko.

  python3 scripts/cek_cloudflare.py

Membuat 3 file di tests/out/cek-cloudflare/ (memakai master uji, bukan produk asli):
  1-latar.png     latar tanpa referensi produk (dipakai mode komposit)
  2-referensi.png foto dari master uji (mode scene)
  3-komposit.png  produk master uji ditempel di atas latar 1
Biaya: 2 gambar dari jatah gratis harian Cloudflare (±220 neurons dari 10.000).
Exit 0 = Cloudflare berfungsi, 1 = gagal (lihat "saran").
"""
import json, pathlib, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import gambar, komposit

AKAR = pathlib.Path(__file__).resolve().parent.parent
MASTER_UJI = AKAR / "tests" / "data" / "master-CONTOH-KOKO-01.png"


def _saran(pesan):
    p = pesan.lower()
    if "curl error 56" in p or "connect" in p or ("403" in p and "tunnel" in p):
        return "api.cloudflare.com belum diizinkan di jaringan environment ini (Settings environment > network)."
    if "401" in p or "403" in p or "authentication" in p:
        return "Token Cloudflare belum dipasang/tidak valid di proxy environment ini, atau izin Workers AI belum dicentang."
    if "429" in p:
        return "Jatah gratis harian habis (reset 07.00 WIB). Coba lagi besok."
    if "cf_account_id" in p:
        return "Isi config/cloudflare-account-id.txt atau env CF_ACCOUNT_ID."
    return "Lihat pesan error di atas."


def cek(out=AKAR / "tests" / "out" / "cek-cloudflare"):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    hasil = {"model": gambar.CF_MODEL, "langkah": []}
    try:
        akun = gambar._akun_cf(gambar.AKUN_CF_FILE)
        kecil = [gambar.kecilkan(MASTER_UJI, out / "master-kecil.png")]
        for nama, ref, prompt in [
            ("1-latar.png", [], "empty light wooden display table in a calm modern muslim menswear boutique, "
                               "soft warm daylight, cream wall, no people, no clothing, no text"),
            ("2-referensi.png", kecil, "Product photo of the shirt from image 0 hanging on a wooden hanger in front of a "
                                       "cream wall, soft daylight. Keep the shirt exactly identical: navy color, "
                                       "5 white buttons, gold embroidery on left chest. Do not change the product."),
        ]:
            t = time.time()
            data = gambar._cloudflare(akun, ref, prompt, 1024)
            ext = gambar._jenis_gambar(data)
            f = out / nama.replace(".png", f".{ext}")
            f.write_bytes(data)
            hasil["langkah"].append({"file": str(f.relative_to(AKAR)), "kb": round(len(data) / 1024),
                                     "detik": round(time.time() - t, 1), "referensi": len(ref)})
        latar = out / hasil["langkah"][0]["file"].split("/")[-1]
        komposit.buat(MASTER_UJI, latar, out / "3-komposit.png")
        hasil["langkah"].append({"file": str((out / "3-komposit.png").relative_to(AKAR)), "mode": "komposit"})
    except (gambar.Gagal, komposit.GagalKomposit, OSError) as e:
        hasil.update(ok=False, error=str(e)[:500], saran=_saran(str(e)))
        return hasil
    hasil.update(ok=True, catatan="Buka 2-referensi.png: hitung kancing (harus 5). 3-komposit.png: produk harus persis master.")
    return hasil


def main():
    hasil = cek()
    print(json.dumps(hasil, ensure_ascii=False, indent=2))
    return 0 if hasil["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
