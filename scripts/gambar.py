"""Buat foto kreatif dari foto master. Provider dicoba berurutan; yang pertama berhasil dipakai.

1. Gemini (model gambar dari daftar model resmi)
2. Cloudflare Workers AI flux-2-klein-4b (akun dari env CF_ACCOUNT_ID atau config/cloudflare-account-id.txt)
3. Manual: status WAITING_FOTO, manusia generate sendiri dari batch/<id>/prompt-foto.md

Kunci API TIDAK pernah ada di sini: proxy jaringan yang menambahkannya. Jangan tambah header Authorization.
Input : <batch>/prompt-foto.md berisi blok "## F01" ... "## F10" + teks prompt.
Output: <batch>/foto/F01.png ..., <batch>/foto/metadata.json (provider tiap foto + percobaan gagal).
"""
import argparse, base64, datetime, json, os, pathlib, re, subprocess, sys, tempfile

GEMINI = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_PILIHAN = ["gemini-3.1-flash-image", "gemini-3-pro-image", "gemini-2.5-flash-image"]
CF_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
AKUN_CF_FILE = pathlib.Path(__file__).resolve().parent.parent / "config" / "cloudflare-account-id.txt"


class Gagal(Exception):
    pass


def _post(args):
    """Satu-satunya pemanggil jaringan (di-mock di tes). Mengembalikan (kode_http, isi)."""
    with tempfile.NamedTemporaryFile() as out:
        r = subprocess.run(["curl", "-sS", "--max-time", "180", "-o", out.name, "-w", "%{http_code}"] + args,
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
        raise Gagal(f"{nama} HTTP {kode}: {isi[:300].decode('utf-8', 'replace')}")


def _gemini_model():
    kode, isi = _post(["-X", "GET", f"{GEMINI}/models?pageSize=200"])
    _cek(kode, isi, "gemini daftar model")
    ada = {m["name"].removeprefix("models/") for m in json.loads(isi).get("models", [])}
    for m in GEMINI_PILIHAN:
        if m in ada:
            return m
    raise Gagal(f"tidak ada model gambar Gemini yang dikenal di daftar model: {sorted(x for x in ada if 'image' in x)}")


def _gemini(model, master, prompt, kerja):
    mime = "image/jpeg" if str(master).lower().endswith((".jpg", ".jpeg")) else "image/png"
    body = {"contents": [{"parts": [
        {"inline_data": {"mime_type": mime, "data": base64.b64encode(pathlib.Path(master).read_bytes()).decode()}},
        {"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"]}}
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
        raise Gagal("cloudflare dilewati: CF_ACCOUNT_ID / config/cloudflare-account-id.txt tidak ada")
    return akun


def _cloudflare(akun, kecil, prompt, ukuran):
    kode, isi = _post(["-X", "POST", "--form-string", f"prompt={prompt}", "-F", f"input_image_0=@{kecil}",
                       "-F", f"width={ukuran}", "-F", f"height={ukuran}",
                       f"https://api.cloudflare.com/client/v4/accounts/{akun}/ai/run/{CF_MODEL}"])
    _cek(kode, isi, "cloudflare")
    if isi[:4] == b"\x89PNG" or isi[:3] == b"\xff\xd8\xff":
        return isi
    j = json.loads(isi)
    if not j.get("success", True) or not j.get("result", {}).get("image"):
        raise Gagal(f"cloudflare: jawaban tanpa gambar: {str(j)[:300]}")
    return base64.b64decode(j["result"]["image"])


def buat(master, batch, akun_cf_file=AKUN_CF_FILE, ukuran=1024):
    batch = pathlib.Path(batch)
    if not pathlib.Path(master).is_file():
        raise Gagal(f"foto master tidak ada: {master}")
    prompts = baca_prompt(batch / "prompt-foto.md")
    if not prompts:
        raise Gagal("prompt-foto.md kosong atau tanpa blok '## Fxx'")
    foto = batch / "foto"
    foto.mkdir(parents=True, exist_ok=True)
    meta = {"master": str(master), "foto": [], "gagal": []}
    kerja = pathlib.Path(tempfile.mkdtemp())

    # provider = (nama, model, fungsi); yang gagal sekali dibuang untuk sisa batch
    provider = []
    try:
        m = _gemini_model()
        provider.append(("gemini", m, lambda p, m=m: _gemini(m, master, p, kerja)))
    except Gagal as e:
        meta["gagal"].append({"id": "-", "provider": "gemini", "alasan": str(e)})
    try:
        akun = _akun_cf(akun_cf_file)
        kecil = kecilkan(master, kerja / "master-kecil.png")
        provider.append(("cloudflare", CF_MODEL, lambda p: _cloudflare(akun, kecil, p, ukuran)))
    except Gagal as e:
        meta["gagal"].append({"id": "-", "provider": "cloudflare", "alasan": str(e)})

    kurang = []
    for fid, prompt in prompts.items():
        while provider:
            nama, model, fn = provider[0]
            try:
                data = fn(prompt)
            except (Gagal, KeyError, IndexError, ValueError) as e:
                meta["gagal"].append({"id": fid, "provider": nama, "alasan": str(e)[:400]})
                provider.pop(0)
                continue
            (foto / f"{fid}.png").write_bytes(data)
            meta["foto"].append({"id": fid, "file": f"{fid}.png", "provider": nama, "model": model,
                                 "prompt": prompt, "waktu": datetime.datetime.now().isoformat(timespec="seconds")})
            break
        else:
            kurang.append(fid)
    meta["kurang"] = kurang
    (foto / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    return {"status": "WAITING_FOTO" if kurang else "SELESAI", "kurang": kurang,
            "dibuat": [f["id"] for f in meta["foto"]]}


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--master", required=True)
    a.add_argument("--batch", required=True, help="folder batch/<id> yang berisi prompt-foto.md")
    x = a.parse_args(argv)
    hasil = buat(x.master, x.batch)
    print(json.dumps(hasil, ensure_ascii=False))
    return 2 if hasil["kurang"] else 0


if __name__ == "__main__":
    sys.exit(main())
