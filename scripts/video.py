"""Edit video final 9:16 (aturan: brain/format-video.md). Tanpa musik, tanpa model video berbayar.

Mode:
- flow      : kalau folder --flow berisi klip V01.., klip dipotong, digabung, diberi teks.
- slideshow : default. Foto yang LULUS QC diberi zoom pelan + transisi fade + teks.
Teks: nama produk (atas) dan harga akhir yang SUDAH DISETUJUI manusia (bawah).
"""
import argparse, json, pathlib, re, subprocess, sys, tempfile

W, H, FPS = 1080, 1920, 30
MIN_DTK, MAX_DTK = 15, 30
TRANSISI = 0.5
EKSTENSI_KLIP = (".mp4", ".mov", ".webm", ".m4v")


def _font():
    r = subprocess.run(["fc-match", "-f", "%{file}", "DejaVu Sans:bold"], capture_output=True, text=True)
    return r.stdout.strip()


def durasi_per_foto(n):
    """Durasi tiap foto agar total (dikurangi tumpang tindih transisi) ada di 15..30 detik."""
    d = max(3.0, (MIN_DTK + (n - 1) * TRANSISI) / n)
    if n * d - (n - 1) * TRANSISI > MAX_DTK:
        d = (MAX_DTK + (n - 1) * TRANSISI) / n
    return d


def ukuran_font(teks, font, maks, lebar=W - 2 * 60 - 2 * 24):
    """Ukuran font terbesar (<= maks) supaya teks muat selebar video; nama produk panjang tidak terpotong."""
    from PIL import ImageFont
    s = maks
    while s > 28 and ImageFont.truetype(font, s).getlength(teks) > lebar:
        s -= 2
    return s


def _teks(nama, harga, kerja):
    # textfile= menghindari masalah escape karakter khusus di nama produk
    (kerja / "nama.txt").write_text(nama, encoding="utf-8")
    (kerja / "harga.txt").write_text(harga, encoding="utf-8")
    f = _font()
    gaya = f"fontfile='{f}':expansion=none:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=24:x=(w-text_w)/2"
    return (f"drawtext=textfile='{kerja / 'nama.txt'}':{gaya}:fontsize={ukuran_font(nama, f, 64)}:y=220,"
            f"drawtext=textfile='{kerja / 'harga.txt'}':{gaya}:fontsize={ukuran_font(harga, f, 96)}:y=h-420")


def _jalankan(args):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg gagal: {r.stderr.strip()[-800:]}")


KELUARAN = ["-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart"]


def slideshow(fotos, nama, harga, out):
    n, kerja = len(fotos), pathlib.Path(tempfile.mkdtemp())
    d = durasi_per_foto(n)
    frame = round(d * FPS)
    masuk, filt = [], []
    for i, f in enumerate(fotos):
        masuk += ["-i", str(f)]
        filt.append(f"[{i}:v]scale={2*W}:{2*W}:force_original_aspect_ratio=decrease,"
                    f"pad={2*W}:{2*W}:(ow-iw)/2:(oh-ih)/2:white,"
                    f"zoompan=z='min(zoom+0.0006,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frame}:s={W}x{W}:fps={FPS},"
                    f"pad={W}:{H}:0:(oh-ih)/2:white,setsar=1,format=yuv420p[v{i}]")
    akhir = "v0"
    for i in range(1, n):
        filt.append(f"[{akhir}][v{i}]xfade=transition=fade:duration={TRANSISI}:offset={i * (d - TRANSISI):.3f}[x{i}]")
        akhir = f"x{i}"
    filt.append(f"[{akhir}]{_teks(nama, harga, kerja)}[out]")
    _jalankan(masuk + ["-filter_complex", ";".join(filt), "-map", "[out]"] + KELUARAN + [str(out)])


def _durasi(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def dari_flow(klip, nama, harga, out):
    durasi = [_durasi(k) for k in klip]
    rusak = [k.name for k, dur in zip(klip, durasi) if not dur]
    if rusak:
        raise ValueError(f"klip Flow rusak/tidak terbaca: {rusak}")
    jatah = MAX_DTK / len(klip)
    potong = [min(dur, jatah) for dur in durasi]
    if sum(potong) < MIN_DTK:
        raise ValueError(f"klip Flow terlalu pendek: total {sum(potong):.1f} dtk < {MIN_DTK}")
    kerja = pathlib.Path(tempfile.mkdtemp())
    masuk, filt = [], []
    for i, (k, p) in enumerate(zip(klip, potong)):
        masuk += ["-i", str(k)]
        filt.append(f"[{i}:v]trim=0:{p:.3f},setpts=PTS-STARTPTS,scale={W}:{H}:force_original_aspect_ratio=increase,"
                    f"crop={W}:{H},fps={FPS},setsar=1,format=yuv420p[v{i}]")
    filt.append("".join(f"[v{i}]" for i in range(len(klip))) + f"concat=n={len(klip)}:v=1:a=0[g]")
    filt.append(f"[g]{_teks(nama, harga, kerja)}[out]")
    _jalankan(masuk + ["-filter_complex", ";".join(filt), "-map", "[out]"] + KELUARAN + [str(out)])


def _nomor(path, awalan):
    m = re.fullmatch(awalan + r"(\d{2})", pathlib.Path(path).stem.upper())
    return m.group(1) if m else None


def buat(fotos, flow_dir, nama, harga, out):
    """fotos = daftar file foto yang LULUS QC (bukan folder: folder bisa berisi foto yang ditolak)."""
    if not isinstance(fotos, (list, tuple)):
        raise ValueError("berikan daftar file foto yang LULUS QC, bukan folder")
    fotos = [pathlib.Path(f) for f in fotos]
    if not fotos:
        raise ValueError("tidak ada foto LULUS untuk video")
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    klip = []
    if flow_dir and pathlib.Path(flow_dir).is_dir():
        klip = sorted(k for k in pathlib.Path(flow_dir).iterdir()
                      if k.suffix.lower() in EKSTENSI_KLIP and _nomor(k, "V"))
    if klip:  # klip ada: harus berpasangan 1:1 dengan foto LULUS (F01 <-> V01), kalau tidak head yang memutuskan
        nf, nv = {_nomor(f, "F") for f in fotos}, {_nomor(k, "V") for k in klip}
        if nf != nv:
            raise ValueError(f"klip Flow tidak berpasangan 1:1. Foto tanpa klip: {sorted('F' + n for n in nf - nv)}; "
                             f"klip tanpa foto LULUS: {sorted('V' + n for n in nv - nf)}")
        dari_flow(klip, nama, harga, out)
        return {"mode": "flow", "klip": [k.name for k in klip], "catatan": "", "cek": cek(out)}
    slideshow(fotos, nama, harga, out)
    return {"mode": "slideshow", "foto": [f.name for f in fotos], "catatan": "tidak ada klip Flow", "cek": cek(out)}


def cek(path):
    """Bukti untuk head/qc: ukuran, durasi, audio, dan apakah seluruh file bisa didekode."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
        v = next(s for s in j["streams"] if s["codec_type"] == "video")
        dur = float(j["format"]["duration"])
    except (ValueError, KeyError, StopIteration):
        return {"ok": False, "alasan": f"tidak terbaca ffprobe: {r.stderr.strip()[:200]}"}
    dekode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], capture_output=True, text=True)
    hasil = {"lebar": v["width"], "tinggi": v["height"], "durasi": round(dur, 2),
             "ada_audio": any(s["codec_type"] == "audio" for s in j["streams"]),
             "dekode_bersih": dekode.returncode == 0 and not dekode.stderr.strip()}
    hasil["ok"] = ((hasil["lebar"], hasil["tinggi"]) == (W, H) and MIN_DTK <= dur <= MAX_DTK + 0.1
                   and hasil["dekode_bersih"] and not hasil["ada_audio"])
    return hasil


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--foto", nargs="+", help="daftar file foto yang LULUS QC (F01.png F03.png ..)")
    a.add_argument("--flow", help="folder klip Flow (V01.mp4 ..), opsional")
    a.add_argument("--nama", required=True)
    a.add_argument("--harga", required=True, help='harga yang sudah disetujui, mis. "Rp 99.000"')
    a.add_argument("--out", required=True)
    a.add_argument("--cek", action="store_true", help="hanya cek file --out")
    x = a.parse_args(argv)
    if x.cek:
        h = cek(x.out)
    else:
        h = buat(x.foto or [], x.flow, x.nama, x.harga, x.out)
    print(json.dumps(h, ensure_ascii=False))
    return 0 if h.get("ok", h.get("cek", {}).get("ok")) else 1


if __name__ == "__main__":
    sys.exit(main())
