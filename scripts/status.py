"""Ringkasan kondisi kantor: batch yang berjalan, yang menunggu pemilik, dan pengingat brain/.
Dipanggil otomatis di awal sesi (hook SessionStart di .claude/settings.json) dan lewat /status.

  python3 scripts/status.py [--singkat] [--akar .]
"""
import argparse, json, pathlib, sys

MENUNGGU_PEMILIK = {
    "APPROVAL_HARGA": "setujui harga & judul",
    "WAITING_FOTO": "buat foto manual dari prompt-foto.md lalu taruh di Drive",
    "WAITING_FLOW": "buat klip Flow atau bilang lanjut tanpa Flow",
    "APPROVAL_FINAL": "lihat foto, video, laporan qc lalu setujui",
    "READY_UPLOAD": "upload paket ke Seller Centre / TikTok Shop, lalu kabari link-nya",
    "OPER_KE_MANUSIA": "baca pesan head: ada masalah yang butuh keputusanmu",
    "WAITING_LATAR": "buat latar dekorasi manual atau izinkan latar warna palet",
    "APPROVAL_DEKORASI": "lihat banner/etalase lalu setujui",
    "APPROVAL_IKLAN": "setujui rencana iklan, lalu pasang & bayar sendiri di dashboard iklan",
    "APPROVAL_KONTEN": "setujui kalender konten, lalu posting/jadwalkan sendiri",
}
SELESAI = {"LIVE", "DIUKUR", "DIPASANG", "DIJADWALKAN", "STOP"}


def baca(akar):
    akar = pathlib.Path(akar)
    batch = []
    for f in sorted(akar.glob("batch/*/status.json")):
        try:
            s = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            batch.append({"batch": f.parent.name, "status": "STATUS_RUSAK", "catatan": str(e)[:100]})
            continue
        riw = s.get("riwayat") or [{}]
        batch.append({"batch": s.get("batch", f.parent.name), "sku": s.get("sku", "-"),
                      "mode": s.get("mode", "deadstock"), "status": s.get("status", "?"),
                      "terakhir": riw[-1].get("waktu", "-"), "revisi": s.get("revisi", {})})
    ingat = []
    bv = akar / "brain/brand-visual.md"
    if bv.is_file() and "- Nama toko:\n" in bv.read_text(encoding="utf-8"):
        ingat.append("brain/brand-visual.md belum diisi (nama toko, palet, gaya foto)")
    pr = akar / "brain/produk.csv"
    if pr.is_file() and "CONTOH" in pr.read_text(encoding="utf-8"):
        ingat.append("brain/produk.csv masih berisi baris CONTOH: ganti dengan data asli dari Drive")
    tunggu = [b for b in batch if b["status"] in MENUNGGU_PEMILIK or b["status"] == "STATUS_RUSAK"]
    return {"batch": batch, "menunggu_pemilik": tunggu, "pengingat": ingat}


def teks(r, singkat=False):
    baris = []
    if not r["batch"]:
        baris.append("Belum ada batch. Mulai dengan: \"mulai batch toko baru dari bahan di Drive\" atau /demo untuk latihan.")
    else:
        jalan = [b for b in r["batch"] if b["status"] not in SELESAI]
        baris.append(f"Batch: {len(r['batch'])} total, {len(jalan)} berjalan, {len(r['menunggu_pemilik'])} menunggu pemilik.")
        for b in r["menunggu_pemilik"]:
            baris.append(f"- MENUNGGU PEMILIK {b['batch']} [{b['status']}]: {MENUNGGU_PEMILIK.get(b['status'], b.get('catatan', ''))}")
        if not singkat:
            for b in jalan:
                if b not in r["menunggu_pemilik"]:
                    baris.append(f"- {b['batch']} ({b['mode']}) [{b['status']}] terakhir {b['terakhir']} revisi {b['revisi']}")
    for i in r["pengingat"]:
        baris.append(f"- Pengingat: {i}")
    return "\n".join(baris)


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--singkat", action="store_true")
    a.add_argument("--json", action="store_true")
    a.add_argument("--akar", default=str(pathlib.Path(__file__).resolve().parent.parent))
    x = a.parse_args(argv)
    r = baca(x.akar)
    print(json.dumps(r, ensure_ascii=False) if x.json else teks(r, x.singkat))
    return 0


if __name__ == "__main__":
    sys.exit(main())
