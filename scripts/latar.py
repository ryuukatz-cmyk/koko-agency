"""Buat gambar LATAR untuk dekorasi toko (tanpa produk, tanpa teks) dari dekorasi.json.

Item yang punya "latar_prompt" dibuatkan latarnya ke path di "latar". Produk dan teks ditambahkan kemudian oleh
scripts/dekorasi.py, jadi prompt latar wajib meminta: tanpa orang, tanpa baju, tanpa teks/huruf/logo.
Provider dan aturan kunci API sama dengan scripts/gambar.py (Gemini/Cloudflare, tanpa header Authorization).

  python3 scripts/latar.py --spec batch/<id>/dekorasi.json [--provider cloudflare,gemini] [--ulang]
Latar yang sudah ada tidak dibuat ulang kecuali --ulang.
Exit 0 = semua latar ada, 2 = sebagian gagal (manusia bisa membuat latar sendiri ke path yang sama), 3 = spec salah.
"""
import argparse, datetime, json, pathlib, sys, tempfile, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gambar, dekorasi

SISI_MAKS_AI = 1024


def ukuran_ai(w, h):
    """Ukuran permintaan ke model: sisi terpanjang 1024, kelipatan 16, rasio sama dengan dekorasi."""
    sk = SISI_MAKS_AI / max(w, h)
    return max(256, round(w * sk / 16) * 16), max(256, round(h * sk / 16) * 16)


def buat(spec, akun_cf_file=gambar.AKUN_CF_FILE, urutan=None, ulang=False):
    item = [i for i in spec.get("item") or [] if i.get("latar_prompt")]
    for i in item:
        if not i.get("latar"):
            raise dekorasi.SpecSalah(f"{i.get('id')}: ada latar_prompt tapi path 'latar' kosong")
        dekorasi._ukuran(i)
    urutan = gambar._urutan(urutan)
    kerja = pathlib.Path(tempfile.mkdtemp())
    meta = {"urutan_provider": urutan, "latar": [], "gagal": []}
    tersedia = {}
    for nama in urutan:
        try:
            if nama == "gemini":
                m = gambar._gemini_model()
                tersedia[nama] = (m, lambda p, w, h, m=m: gambar._gemini(m, [], p, kerja))
            else:
                akun = gambar._akun_cf(akun_cf_file)
                tersedia[nama] = (gambar.CF_MODEL, lambda p, w, h: gambar._cloudflare(akun, [], p, w, h))
        except gambar.Gagal as e:
            meta["gagal"].append({"id": "-", "provider": nama, "alasan": str(e)})
    provider = [(n, *tersedia[n]) for n in urutan if n in tersedia]

    kurang = []
    for i in item:
        target = pathlib.Path(i["latar"])
        if target.is_file() and not ulang:
            meta["latar"].append({"id": i["id"], "file": str(target), "provider": "sudah-ada"})
            continue
        w, h = ukuran_ai(*dekorasi._ukuran(i))
        prompt = i["latar_prompt"]
        for p in list(provider):
            nama, model, fn = p
            try:
                data = fn(prompt, w, h)
                gambar._jenis_gambar(data)
            except (gambar.Gagal, KeyError, IndexError, ValueError, TypeError, AttributeError) as e:
                meta["gagal"].append({"id": i["id"], "provider": nama, "alasan": str(e)[:400]})
                if getattr(e, "fatal", False):
                    provider.remove(p)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            meta["latar"].append({"id": i["id"], "file": str(target), "provider": nama, "model": model,
                                  "prompt": prompt, "ukuran_minta": f"{w}x{h}",
                                  "waktu": datetime.datetime.now().isoformat(timespec="seconds")})
            break
        else:
            kurang.append(i["id"])
    meta["kurang"] = kurang
    return meta


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--spec", required=True)
    a.add_argument("--provider")
    a.add_argument("--ulang", action="store_true")
    x = a.parse_args(argv)
    try:
        spec = json.loads(pathlib.Path(x.spec).read_text(encoding="utf-8"))
        meta = buat(spec, urutan=x.provider, ulang=x.ulang)
    except (dekorasi.SpecSalah, gambar.Gagal, OSError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 3
    (pathlib.Path(x.spec).parent / "latar-metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(json.dumps({"status": "WAITING_LATAR" if meta["kurang"] else "SELESAI", "kurang": meta["kurang"]},
                     ensure_ascii=False))
    return 2 if meta["kurang"] else 0


if __name__ == "__main__":
    sys.exit(main())
