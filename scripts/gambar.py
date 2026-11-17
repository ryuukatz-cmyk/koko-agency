"""Buat foto kreatif dari foto master. Provider dicoba berurutan; yang pertama berhasil dipakai.

1. Gemini (model gambar dari daftar model resmi)
2. Cloudflare Workers AI flux-2-klein-4b (akun dari env CF_ACCOUNT_ID atau config/cloudflare-account-id.txt)
3. Manual: status WAITING_FOTO, manusia generate sendiri dari batch/<id>/prompt-foto.md
Urutan 1-2 bisa diubah: --provider cloudflare,gemini (atau env KOKO_PROVIDER).

Master boleh 1-4 foto (--master depan.jpg detail-bordir.jpg belakang.jpg). Semua dikirim sebagai referensi:
Cloudflare input_image_0 = master pertama, input_image_1 = kedua, dst. Di prompt sebut "image 0", "image 1".

Dua mode per foto:
- scene (default): model membuat ulang foto dari referensi. Detail kecil bisa berubah -> qc wajib teliti.
- komposit: blok prompt diawali "[komposit]". Model hanya membuat LATAR (tanpa referensi produk), lalu produk
  asli dari master pertama ditempel (scripts/komposit.py). Produk 100% sama; master harus berlatar polos.

Kunci API TIDAK pernah ada di sini: proxy jaringan yang menambahkannya. Jangan tambah header Authorization.
Input : <batch>/prompt-foto.md berisi blok "## F01" ... "## F10" + teks prompt.
Output: <batch>/foto/F01.png ..., <batch>/foto/metadata.json (provider & mode tiap foto + percobaan gagal).
        Latar mentah mode komposit disimpan terpisah di <batch>/foto/latar/ (bukan foto final).
Exit  : 0 semua jadi, 2 WAITING_FOTO (sebagian gagal, lihat metadata), 3 input salah (master/prompt/--provider).
"""
import argparse, base64, datetime, json, os, pathlib, re, subprocess, sys, tempfile

GEMINI = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_PILIHAN = ["gemini-3.1-flash-image", "gemini-3-pro-image", "gemini-2.5-flash-image"]
CF_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
AKUN_CF_FILE = pathlib.Path(__file__).resolve().parent.parent / "config" / "cloudflare-account-id.txt"
URUTAN_DEFAULT = ("gemini", "cloudflare")
MAKS_MASTER = 4
TANDA_KOMPOSIT = "[komposit]"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import komposit


class Gagal(Exception):
    """fatal=True: masalah tingkat akun/model (kuota, izin) -> provider dilewati untuk sisa batch."""
    def __init__(self, pesan, fatal=False):
        super().__init__(pesan)
        self.fatal = fatal


def _post(args):
    """Satu-satunya pemanggil jaringan (di-mock di tes). Mengembalikan (kode_http, isi)."""
    with tempfile.NamedTemporaryFile() as out:
        r = subprocess.run(["curl", "-q", "-sS", "--max-time", "180", "-o", out.name, "-w", "%{http_code}"] + args,
                           capture_output=True, text=True)
        isi = pathlib.Path(out.name).read_bytes()
    if r.returncode != 0:
        raise Gagal(f"curl error {r.returncode}: {r.stderr.strip()[:300]}")
    return int(r.stdout or 0), isi


def baca_prompt(path):
    blok = re.split(r"^##\s*(F\d{2})\s*$", pathlib.Path(path).read_text(encoding="utf-8"), flags=re.M)
    return {blok[i]: blok[i + 1].strip() for i in range(1, len(blok), 2)}


def kecilkan(master, out, sisi=511):
    from PIL import Image
    with Image.open(master) as asli:
        im = asli.convert("RGB")
    im.thumbnail((sisi, sisi))
    im.save(out, "PNG")
    return out


def _cek(kode, isi, nama):
    if kode != 200:
        raise Gagal(f"{nama} HTTP {kode}: {isi[:300].decode('utf-8', 'replace')}", fatal=kode in (401, 402, 403, 404, 429))


def _gemini_model():
    kode, isi = _post(["-X", "GET", f"{GEMINI}/models?pageSize=200"])
    _cek(kode, isi, "gemini daftar model")
    ada = {m["name"].removeprefix("models/") for m in json.loads(isi).get("models", [])}
    for m in GEMINI_PILIHAN:  # nama persis dulu, lalu varian (mis. -preview)
        cocok = [m] if m in ada else sorted(x for x in ada if x.startswith(m))
        if cocok:
            return cocok[0]
    raise Gagal(f"tidak ada model gambar Gemini yang dikenal di daftar model: {sorted(x for x in ada if 'image' in x)}", fatal=True)


def _gemini(model, masters, prompt, kerja):
    """masters kosong = tanpa referensi (latar mode komposit)."""
    parts = []
    for m in masters:
        mime = "image/jpeg" if str(m).lower().endswith((".jpg", ".jpeg")) else "image/png"
        parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(pathlib.Path(m).read_bytes()).decode()}})
    body = {"contents": [{"parts": parts + [{"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"]}}
    req = kerja / "gemini.json"
    req.write_text(json.dumps(body))
    kode, isi = _post(["-X", "POST", "-H", "Content-Type: application/json", "-d", f"@{req}",
                       f"{GEMINI}/models/{model}:generateContent"])
    _cek(kode, isi, "gemini")
    for p in json.loads(isi)["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            return base64.b64decode(p["inlineData"]["data"])
    raise Gagal("gemini: jawaban tanpa gambar")


def _akun_cf(akun_cf_file):
    akun = os.environ.get("CF_ACCOUNT_ID", "").strip()
    if not akun and pathlib.Path(akun_cf_file).exists():
        akun = pathlib.Path(akun_cf_file).read_text().strip()
    if not akun:
        raise Gagal("cloudflare dilewati: CF_ACCOUNT_ID / config/cloudflare-account-id.txt tidak ada", fatal=True)
    return akun


def _cloudflare(akun, kecil, prompt, ukuran):
    """kecil = daftar master yang sudah < 512 px (kosong = tanpa referensi)."""
    form = []
    for i, k in enumerate(kecil[:MAKS_MASTER]):
        form += ["-F", f"input_image_{i}=@{k}"]
    kode, isi = _post(["-X", "POST", "--form-string", f"prompt={prompt}"] + form +
                      ["-F", f"width={ukuran}", "-F", f"height={ukuran}",
                       f"https://api.cloudflare.com/client/v4/accounts/{akun}/ai/run/{CF_MODEL}"])
    _cek(kode, isi, "cloudflare")
    if isi[:4] == b"\x89PNG" or isi[:3] == b"\xff\xd8\xff":
        return isi
    j = json.loads(isi)
    if not j.get("success", True) or not j.get("result", {}).get("image"):
        raise Gagal(f"cloudflare: jawaban tanpa gambar: {str(j)[:300]}")
    return base64.b64decode(j["result"]["image"])


def _jenis_gambar(data):
    for awal, ext in ((b"\x89PNG", "png"), (b"\xff\xd8\xff", "jpg"), (b"RIFF", "webp")):
        if data[:len(awal)] == awal:
            return ext
    raise Gagal("jawaban bukan file gambar")


def _urutan(urutan):
    if urutan is None:
        urutan = os.environ.get("KOKO_PROVIDER") or ",".join(URUTAN_DEFAULT)
    if isinstance(urutan, str):
        urutan = [u.strip().lower() for u in urutan.split(",") if u.strip()]
    salah = [u for u in urutan if u not in URUTAN_DEFAULT]
    if salah or not urutan or len(set(urutan)) != len(urutan):
        raise Gagal(f"--provider tidak dikenal/dobel: {urutan} (pilihan: {', '.join(URUTAN_DEFAULT)})")
    return list(urutan)


def buat(master, batch, akun_cf_file=AKUN_CF_FILE, ukuran=1024, urutan=None):
    batch = pathlib.Path(batch)
    masters = [pathlib.Path(m) for m in (master if isinstance(master, (list, tuple)) else [master])]
    if not 1 <= len(masters) <= MAKS_MASTER:
        raise Gagal(f"master harus 1-{MAKS_MASTER} foto, dapat {len(masters)}")
    for m in masters:
        if not m.is_file():
            raise Gagal(f"foto master tidak ada: {m}")
    urutan = _urutan(urutan)
    prompts = baca_prompt(batch / "prompt-foto.md")
    if not prompts:
        raise Gagal("prompt-foto.md kosong atau tanpa blok '## Fxx'")
    foto = batch / "foto"
    foto.mkdir(parents=True, exist_ok=True)
    for fid in prompts:  # foto lama dari percobaan sebelumnya tidak boleh ikut terpakai
        for lama in list(foto.glob(f"{fid}.*")) + list(foto.glob(f"latar/{fid}.*")):
            lama.unlink()
    meta = {"master": [str(m) for m in masters], "urutan_provider": urutan, "foto": [], "gagal": []}
    kerja = pathlib.Path(tempfile.mkdtemp())

    # produk untuk mode komposit dipotong sekali; kalau gagal, hanya foto komposit yang terdampak
    produk, alasan_potong = None, None
    if any(p.lower().startswith(TANDA_KOMPOSIT) for p in prompts.values()):
        try:
            produk = komposit.potong(masters[0])
        except (komposit.GagalKomposit, OSError) as e:
            alasan_potong = f"komposit: {e}"

    # provider = (nama, model, fungsi(prompt, pakai_referensi)); yang gagal fatal dibuang untuk sisa batch
    tersedia = {}
    for nama in urutan:
        try:
            if nama == "gemini":
                m = _gemini_model()
                tersedia[nama] = (nama, m, lambda p, ref, m=m: _gemini(m, masters if ref else [], p, kerja))
            else:
                akun = _akun_cf(akun_cf_file)
                kecil = [kecilkan(m, kerja / f"master-{i}.png") for i, m in enumerate(masters)]
                tersedia[nama] = (nama, CF_MODEL, lambda p, ref: _cloudflare(akun, kecil if ref else [], p, ukuran))
        except (Gagal, OSError) as e:  # OSError: master tidak bisa dibuka sebagai gambar
            meta["gagal"].append({"id": "-", "provider": nama, "alasan": str(e)})
    provider = [tersedia[n] for n in urutan if n in tersedia]

    kurang = []
    for fid, prompt in prompts.items():
        mode_komposit = prompt.lower().startswith(TANDA_KOMPOSIT)
        teks = prompt[len(TANDA_KOMPOSIT):].strip() if mode_komposit else prompt
        if mode_komposit and produk is None:
            meta["gagal"].append({"id": fid, "provider": "-", "alasan": alasan_potong})
            kurang.append(fid)
            continue
        for p in list(provider):
            nama, model, fn = p
            try:
                data = fn(teks, not mode_komposit)
                ext = _jenis_gambar(data)
            except (Gagal, KeyError, IndexError, ValueError, TypeError, AttributeError) as e:
                meta["gagal"].append({"id": fid, "provider": nama, "alasan": str(e)[:400]})
                if getattr(e, "fatal", False):
                    provider.remove(p)
                continue
            catatan = {"id": fid, "provider": nama, "model": model, "mode": "komposit" if mode_komposit else "scene",
                       "prompt": prompt, "waktu": datetime.datetime.now().isoformat(timespec="seconds")}
            if mode_komposit:
                latar = foto / "latar" / f"{fid}.{ext}"
                latar.parent.mkdir(exist_ok=True)
                latar.write_bytes(data)
                try:
                    komposit.tempel(produk, latar, foto / f"{fid}.png", ukuran)
                except OSError as e:  # latar rusak: anggap gagal di provider ini
                    meta["gagal"].append({"id": fid, "provider": nama, "alasan": f"komposit: {e}"})
                    latar.unlink()
                    continue
                catatan.update(file=f"{fid}.png", latar=f"latar/{latar.name}")
            else:
                (foto / f"{fid}.{ext}").write_bytes(data)
                catatan["file"] = f"{fid}.{ext}"
            meta["foto"].append(catatan)
            break
        else:
            kurang.append(fid)
    meta["kurang"] = kurang
    (foto / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    return {"status": "WAITING_FOTO" if kurang else "SELESAI", "kurang": kurang,
            "dibuat": [f["id"] for f in meta["foto"]]}


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--master", required=True, nargs="+",
                   help="1-4 foto master; yang pertama = foto depan (dipakai juga untuk komposit)")
    a.add_argument("--batch", required=True, help="folder batch/<id> yang berisi prompt-foto.md")
    a.add_argument("--provider", help="urutan provider, mis. cloudflare,gemini (default gemini,cloudflare)")
    x = a.parse_args(argv)
    try:
        hasil = buat(x.master, x.batch, urutan=x.provider)
    except Gagal as e:  # input salah (master/prompt/provider): bukan WAITING_FOTO
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 3
    print(json.dumps(hasil, ensure_ascii=False))
    return 2 if hasil["kurang"] else 0


if __name__ == "__main__":
    sys.exit(main())
