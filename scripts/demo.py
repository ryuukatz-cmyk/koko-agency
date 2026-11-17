"""Demo alur toko baru ujung ke ujung dengan DATA CONTOH (contoh/). Membuktikan semua alat agent tersambung.

  python3 scripts/demo.py --out demo-out           # offline: latar dibuat lokal (tanpa AI)
  python3 scripts/demo.py --out demo-out --flux    # latar & foto scene dari Cloudflare FLUX nyata (environment koko)

Langkah: stok gudang -> pilih SKU -> harga -> listing Shopee+TikTok -> cek listing -> 10 foto (3 komposit + 7 scene)
-> video 9:16 -> dekorasi toko (3 banner) -> rencana iklan -> paket upload. Ringkasan di <out>/RINGKASAN.md.
Isi copy di demo adalah templat tetap (pengganti tulisan marketer), bukan hasil AI. Folder demo-out/ tidak di-commit.
"""
import argparse, csv, datetime, json, pathlib, shutil, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stok_gudang, harga, cek_listing, gambar, komposit, video, dekorasi, iklan, paket_upload
from export import baca_tabel
from PIL import Image, ImageDraw, ImageFilter

AKAR = pathlib.Path(__file__).resolve().parent.parent
CONTOH = AKAR / "contoh" / "input"
ADMIN = 10
HARI_INI = datetime.date(2026, 11, 17)
PALET = {"utama": "#1F2A44", "kedua": "#F4F1E8", "aksen": "#C9A227", "teks": "#FFFFFF"}
LATAR_WARNA = [(237, 230, 218), (226, 214, 196), (220, 226, 230), (240, 236, 226), (214, 222, 210),
               (232, 220, 206), (225, 225, 220), (238, 228, 214), (219, 210, 198), (230, 232, 236)]
PROMPT_LATAR = ["empty light wooden display table against a cream wall, soft morning side light",
                "empty wooden hanger rail in a calm boutique, warm light, blurred background",
                "plain beige linen backdrop with a small potted plant, soft shadow"]
PROMPT_SCENE = ["hanging on a wooden hanger in front of a cream wall", "folded neatly on a wooden shelf",
                "laid flat on light linen with a wooden prayer bead", "on a mannequin in a calm boutique",
                "close-up of the chest embroidery from image 1, shallow depth of field",
                "on a mannequin near a window with morning light", "next to a plain prayer mat on a wooden floor"]


def rupiah(n):
    return f"Rp {n:,}".replace(",", ".")


def _latar_lokal(warna, path, w=1024, h=1024):
    """Latar pengganti AI untuk demo offline: gradasi lembut + 'meja'."""
    im = Image.new("RGB", (w, h), warna)
    g = ImageDraw.Draw(im)
    gelap = tuple(round(c * 0.86) for c in warna)
    g.rectangle((0, round(h * 0.78), w, h), fill=gelap)
    im = im.filter(ImageFilter.GaussianBlur(3))
    im.save(path)
    return path


def _tulis_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def jalankan(out, flux=False):
    out = pathlib.Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    log = {"mode": "flux" if flux else "offline", "langkah": []}

    # 1. pilih SKU dari stok gudang
    kat = stok_gudang.katalog(baca_tabel(CONTOH / "1-stok-gudang/stok-gudang.csv"), baca_tabel(CONTOH / "2-hpp/hpp.csv"),
                              baca_tabel(CONTOH / "3-info-produk/info-produk.csv"), ADMIN, HARI_INI)
    (out / "data").mkdir()
    stok_gudang.tulis_csv(kat, out / "data/katalog.csv", stok_gudang.KOLOM_OUTPUT)
    siap = [r for r in kat if r["status"] == "SIAP"]
    k = siap[0]
    sku = k["sku"]
    log["langkah"].append({"1_stok_gudang": {"siap": [r["sku"] for r in siap],
                                             "data_kurang": {r["sku"]: r["catatan"] for r in kat if r["status"] != "SIAP"}}})
    batch = out / "batch" / f"{HARI_INI.isoformat()}-{sku}"
    (batch / "master").mkdir(parents=True)
    (out / "brain/product-lock").mkdir(parents=True)
    shutil.copy2(AKAR / "contoh/product-lock" / f"{sku}.md", out / "brain/product-lock" / f"{sku}.md")
    for f in (CONTOH / "4-foto-master" / sku).iterdir():
        shutil.copy2(f, batch / "master" / f.name)
    info = {r["SKU"]: r for r in baca_tabel(CONTOH / "3-info-produk/info-produk.csv")}[sku]
    produk_csv = out / "brain/produk.csv"
    _tulis_csv(produk_csv, [{"sku": sku, "nama": k["nama"], "warna": info["warna"], "ukuran": info["ukuran"],
                             "bahan": info["bahan"], "harga_normal": k["harga_jual_rencana"], "hpp": k["hpp"],
                             "fakta_boleh_diklaim": info["fakta_boleh_diklaim"], "catatan": "CONTOH"}])
    status = {"batch": batch.name, "sku": sku, "mode": "toko-baru", "status": "STRATEGI", "revisi": {}, "riwayat": []}

    # 2. harga (tanpa harga coret di toko baru)
    h = harga.hitung(k["harga_jual_rencana"], k["hpp"], ADMIN)
    log["langkah"].append({"2_harga": h})

    # 3. listing per platform (templat demo; di batch nyata ditulis marketer dari kata-kunci.csv)
    warna = info["warna"]
    fakta = [f.strip() for f in info["fakta_boleh_diklaim"].split(";") if f.strip()]
    lengan = "Lengan Panjang" if "lengan panjang" in fakta else "Lengan Pendek"
    judul_s = f"Baju Koko Pria {lengan} Bordir Dada Kiri {warna.title()} M L XL"
    judul_t = f"Baju Koko Pria {lengan} Bordir Dada Kiri Warna {warna.title()} Cocok Jumatan dan Lebaran M L XL"
    desk = (f"Koko pria {lengan.lower()} warna {warna}.\nDetail: {', '.join(fakta)}.\nUkuran: M, L, XL.\n"
            "Cocok untuk Jumatan, kajian, dan Lebaran.")
    listing = [{"sku": sku, "platform": p, "judul": j, "deskripsi": desk, "harga_normal": h["harga_akhir"],
                "harga_coret": "", "harga_akhir": h["harga_akhir"], "taktik": "harga langsung + voucher toko",
                "kata_kunci": f"baju koko pria;koko bordir;koko {lengan.lower()}",
                "caption_video": f"Koko {warna} bordir dada kiri, siap untuk Lebaran. #bajukoko #kokopria #kokobordir"}
               for p, j in (("shopee", judul_s), ("tiktok", judul_t))]
    _tulis_csv(batch / "listing.csv", listing)
    cl = cek_listing.cek(listing, cek_listing._baca(produk_csv), cek_listing._admin(str(ADMIN)), "toko-baru")
    log["langkah"].append({"3_cek_listing": {"lulus": cl["lulus"],
                                             "masalah": [m for b in cl["baris"] for m in b["masalah"]]}})

    # 4. foto: F01-F03 komposit, F04-F10 scene
    blok = [f"## F{i + 1:02d}\n[komposit] {PROMPT_LATAR[i]}, no people, no clothing, no text\n" for i in range(3)]
    kunci = (f"Keep the shirt from image 0 exactly identical ({'; '.join(fakta)}; embroidery detail in image 1). "
             "Do not change the product.")
    blok += [f"## F{i + 4:02d}\nProduct photo of the koko shirt {s}. {kunci}\n" for i, s in enumerate(PROMPT_SCENE)]
    (batch / "prompt-foto.md").write_text("\n".join(blok), encoding="utf-8")
    masters = [batch / "master/depan.png", batch / "master/detail-bordir.png"]
    if flux:
        hasil_foto = gambar.buat(masters, batch, urutan="cloudflare,gemini")
    else:  # tanpa AI: semua foto = produk asli di atas latar lokal (scene AI butuh --flux)
        (batch / "foto/latar").mkdir(parents=True)
        produk = komposit.potong(masters[0])
        meta = {"master": [str(m) for m in masters], "foto": [], "gagal": [], "kurang": []}
        for i in range(10):
            fid = f"F{i + 1:02d}"
            lt = _latar_lokal(LATAR_WARNA[i], batch / f"foto/latar/{fid}.png")
            komposit.tempel(produk, lt, batch / f"foto/{fid}.png")
            meta["foto"].append({"id": fid, "file": f"{fid}.png", "provider": "demo-offline", "mode": "komposit"})
        (batch / "foto/metadata.json").write_text(json.dumps(meta, indent=2))
        hasil_foto = {"status": "SELESAI", "kurang": [], "dibuat": [f["id"] for f in meta["foto"]]}
    log["langkah"].append({"4_foto": hasil_foto})
    foto_lulus = sorted(p for p in (batch / "foto").glob("F??.*"))  # demo: anggap qc LULUS semua

    # 5. video
    vid, cek_video = None, {"ok": True}
    if foto_lulus:
        vid = batch / f"video/final/{batch.name}_FINAL.mp4"
        hv = video.buat(foto_lulus, None, k["nama"].replace(" (CONTOH)", ""), rupiah(h["harga_akhir"]), vid)
        cek_video = hv["cek"]
        log["langkah"].append({"5_video": cek_video})

    # 6. dekorasi toko (batch tingkat toko)
    dek = out / "batch" / f"{HARI_INI.isoformat()}-toko-dekorasi"
    semua_depan = [str(CONTOH / "4-foto-master" / r["sku"] / "depan.png") for r in siap]
    item = [
        {"id": "D01", "jenis": "banner-carousel", "produk": semua_depan[:3], "label": "Koleksi Ramadan",
         "judul": "Koko Bordir untuk Hari Raya", "subjudul": "Lengan panjang & pendek, M sampai XL", "cta": "Lihat Koleksi"},
        {"id": "D02", "jenis": "banner-carousel", "tata_letak": "teks-kanan", "produk": [semua_depan[0]],
         "label": "Voucher Toko", "judul": "Potongan Rp10.000", "subjudul": "Min. belanja Rp150.000", "cta": "Klaim Voucher"},
        {"id": "D03", "jenis": "kategori", "tata_letak": "tengah", "produk": [semua_depan[0]],
         "judul": f"Koko {lengan}", "harga": rupiah(h["harga_akhir"])},
    ]
    for i, it in enumerate(item):
        it["latar"] = str(dek / f"latar/{it['id']}.png")
        it["latar_prompt"] = PROMPT_LATAR[i] + ", no people, no clothing, no text"
    spec = {"palet": PALET, "item": item}
    dek.mkdir(parents=True)
    (dek / "dekorasi.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2))
    if flux:
        import latar
        lm = latar.buat(spec, urutan="cloudflare,gemini")
        for it in item:  # latar gagal -> pakai gradasi palet
            if it["id"] in lm["kurang"]:
                it["latar"] = None
    else:
        for i, it in enumerate(item):
            (dek / "latar").mkdir(exist_ok=True)
            _latar_lokal((30, 42, 68) if i != 1 else LATAR_WARNA[0], it["latar"], *dekorasi._ukuran(it))
    hd = dekorasi.buat(spec, dek / "hasil")
    log["langkah"].append({"6_dekorasi": {"ok": hd["ok"], "item": [(r["id"], r.get("kb"), r.get("kontras"))
                                                                   for r in hd["item"]]}})

    # 7. rencana iklan
    ri = iklan.rencana(listing, cek_listing._baca(produk_csv), cek_listing._admin(str(ADMIN)), 50000)
    log["langkah"].append({"7_iklan": [{k2: b.get(k2) for k2 in ("platform", "roas_target", "bid_maks_per_klik",
                                                                  "budget_harian", "status")} for b in ri["baris"]]})

    # 8. paket upload
    pk = paket_upload.buat(batch, foto_lulus, vid, batch / "listing.csv", k["stok"], batch / "final")
    log["langkah"].append({"8_paket": {"zip": pk["zip"]}})
    status["status"] = "READY_UPLOAD (demo, tanpa qc & persetujuan manusia)"
    (batch / "status.json").write_text(json.dumps(status, indent=2))

    ringkas = ["# Ringkasan demo", "", f"Mode: {log['mode']}. SKU: {sku}. Data: CONTOH (palsu).", ""]
    for l in log["langkah"]:
        for nama, isi in l.items():
            ringkas += [f"## {nama}", "```", json.dumps(isi, ensure_ascii=False, indent=1, default=str)[:1500], "```", ""]
    (out / "RINGKASAN.md").write_text("\n".join(ringkas), encoding="utf-8")
    log["ok"] = bool(cl["lulus"] and not hasil_foto["kurang"] and cek_video["ok"] and hd["ok"] and ri["ada_yang_layak"])
    return log


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--out", default="demo-out")
    a.add_argument("--flux", action="store_true", help="pakai Cloudflare FLUX nyata (butuh environment koko)")
    x = a.parse_args(argv)
    log = jalankan(x.out, x.flux)
    print(json.dumps({"ok": log["ok"], "mode": log["mode"], "ringkasan": str(pathlib.Path(x.out) / "RINGKASAN.md")},
                     ensure_ascii=False))
    return 0 if log["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
