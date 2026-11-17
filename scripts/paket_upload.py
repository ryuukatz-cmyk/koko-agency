"""Susun paket siap upload (status READY_UPLOAD) untuk satu SKU: foto urut, video, teks listing per platform,
dan checklist upload manual. Sistem tidak pernah login ke Shopee/TikTok: pemilik yang mengunggah.

  python3 scripts/paket_upload.py --batch batch/<id> --foto batch/<id>/foto/F01.png .. --video batch/<id>/video/final/<id>_FINAL.mp4 \\
      --listing batch/<id>/listing.csv --stok 40 --out batch/<id>/final
Hanya foto yang LULUS QC yang boleh dimasukkan (urutan argumen = urutan di toko; foto pertama = foto sampul).
Hasil: <out>/paket/{shopee,tiktok}/..., <out>/CHECKLIST-UPLOAD.md, <out>/manifest.json, <out>/paket-<id>.zip
Exit 0 = paket jadi, 2 = input salah.
"""
import argparse, csv, hashlib, json, pathlib, shutil, sys, zipfile

MAKS_FOTO = {"shopee": 9, "tiktok": 9}  # ASUMSI, cek di Seller Centre / TikTok Shop Seller Center


class Salah(Exception):
    pass


def _sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()[:16]


def _teks_listing(r):
    return (f"JUDUL\n{r['judul']}\n\nHARGA\n{r['harga_akhir']}\n\nKATA KUNCI\n{r.get('kata_kunci', '')}\n\n"
            f"DESKRIPSI\n{r['deskripsi']}\n\nCAPTION VIDEO\n{r.get('caption_video', '')}\n")


def _checklist(batch_id, sku, baris, foto, video, stok):
    bagian = [f"# Checklist upload — {batch_id} ({sku})", "",
              "Upload dilakukan PEMILIK. Centang satu per satu. Jangan mengubah harga/judul tanpa kembali ke head.", ""]
    for platform, r in baris.items():
        nama = "Shopee Seller Centre" if platform == "shopee" else "TikTok Shop Seller Center"
        n = min(len(foto), MAKS_FOTO[platform])
        bagian += [f"## {nama}", "",
                   f"- [ ] Tambah produk baru, pilih kategori yang paling sesuai (koko / baju muslim pria).",
                   f"- [ ] Nama produk: salin dari `paket/{platform}/listing.txt` (bagian JUDUL), persis.",
                   f"- [ ] Deskripsi: salin bagian DESKRIPSI, persis.",
                   f"- [ ] Foto: unggah `paket/{platform}/foto-01..{n:02d}` berurutan; foto-01 = foto sampul.",
                   f"- [ ] Video: unggah `paket/{platform}/video.mp4`." if video else "- [ ] (tidak ada video)",
                   f"- [ ] Harga: {r['harga_akhir']} — harga yang sudah disetujui. "
                   + ("Tanpa harga coret." if not str(r.get("harga_coret", "")).strip() else f"Harga coret {r['harga_coret']}."),
                   f"- [ ] Stok: {stok if stok is not None else 'isi dari stok gudang'}; SKU induk: `{sku}`.",
                   "- [ ] Variasi ukuran, berat, dan dimensi paket: isi dari data gudang (tidak dibuat agent).",
                   "- [ ] Simpan & tampilkan. Kirim link produk ke head untuk dicatat (status LIVE).", ""]
    return "\n".join(bagian)


def buat(batch, foto, video, listing, stok, out):
    batch, out = pathlib.Path(batch), pathlib.Path(out)
    batch_id = batch.name
    foto = [pathlib.Path(f) for f in foto]
    if not foto:
        raise Salah("minimal 1 foto LULUS")
    for f in foto + ([pathlib.Path(video)] if video else []):
        if not f.is_file() or f.stat().st_size == 0:
            raise Salah(f"file tidak ada / kosong: {f}")
    if len({f.name for f in foto}) != len(foto):
        raise Salah("foto dobel di daftar")
    with open(listing, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    sku = {r["sku"].strip().upper() for r in rows}
    if len(sku) != 1:
        raise Salah(f"listing.csv harus berisi tepat 1 SKU (satu batch = satu SKU), dapat {sorted(sku)}")
    baris = {}
    for r in rows:
        p = r["platform"].strip().lower()
        if p not in MAKS_FOTO:
            raise Salah(f"platform tidak dikenal di listing: {p!r}")
        if p in baris:
            raise Salah(f"baris {p} dobel di listing.csv")
        baris[p] = r
    sku = sku.pop()

    paket = out / "paket"
    if paket.exists():
        shutil.rmtree(paket)  # paket lama tidak boleh tercampur foto yang sudah tidak LULUS
    manifest = {"batch": batch_id, "sku": sku, "platform": {}}
    for p, r in baris.items():
        d = paket / p
        d.mkdir(parents=True)
        daftar = []
        for i, f in enumerate(foto[:MAKS_FOTO[p]], start=1):
            tujuan = d / f"foto-{i:02d}{f.suffix.lower()}"
            shutil.copy2(f, tujuan)
            daftar.append({"file": tujuan.name, "asal": str(f), "sha": _sha(f)})
        if video:
            shutil.copy2(video, d / "video.mp4")
        (d / "listing.txt").write_text(_teks_listing(r), encoding="utf-8")
        manifest["platform"][p] = {"foto": daftar, "video": "video.mp4" if video else None,
                                   "harga_akhir": r["harga_akhir"], "judul": r["judul"],
                                   "foto_tidak_masuk": [str(f) for f in foto[MAKS_FOTO[p]:]]}
    (out / "CHECKLIST-UPLOAD.md").write_text(_checklist(batch_id, sku, baris, foto, video, stok), encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    z = out / f"paket-{batch_id}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(paket.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(out))
        zf.write(out / "CHECKLIST-UPLOAD.md", "CHECKLIST-UPLOAD.md")
    manifest["zip"] = str(z)
    return manifest


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--batch", required=True)
    a.add_argument("--foto", required=True, nargs="+")
    a.add_argument("--video")
    a.add_argument("--listing", required=True)
    a.add_argument("--stok", type=int)
    a.add_argument("--out", required=True)
    x = a.parse_args(argv)
    try:
        m = buat(x.batch, x.foto, x.video, x.listing, x.stok, x.out)
    except (Salah, OSError, KeyError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"sku": m["sku"], "platform": list(m["platform"]), "zip": m["zip"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
