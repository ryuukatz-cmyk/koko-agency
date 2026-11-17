"""Hook PreToolUse: penjaga aturan keras proyek (CLAUDE.md) sebelum alat dijalankan.

Menolak (exit 2, alasan dikirim ke agent):
- perintah yang mengirim header Authorization sendiri (kunci API hanya lewat proxy),
- curl/wget dengan identitas browser palsu (dilarang mengakali pemblokir bot),
- git add / git commit yang memasukkan data mentah (data pembeli), .env, atau teks yang mirip kunci API,
- menulis teks yang mirip kunci API ke file mana pun.
Selain itu diizinkan (exit 0). Hook ini lapisan kedua; aturan utamanya tetap di CLAUDE.md.
"""
import json, re, subprocess, sys

POLA_KUNCI = [r"AIza[0-9A-Za-z_\-]{35}", r"\bsk-[A-Za-z0-9]{20,}", r"\bghp_[A-Za-z0-9]{30,}", r"\bxox[abp]-[A-Za-z0-9-]{10,}",
              r"(?i)bearer\s+[A-Za-z0-9_\-\.]{30,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
              r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"][A-Za-z0-9_\-]{24,}['\"]"]
TERLARANG_GIT = re.compile(r"(^|/)(data/mentah/|\.env$|\.env\.)")


def _kunci(teks):
    return next((p for p in POLA_KUNCI if re.search(p, teks or "")), None)


def periksa(data, git_staged=None):
    """Kembalikan alasan penolakan atau None."""
    alat, inp = data.get("tool_name", ""), data.get("tool_input") or {}
    if alat == "Bash":
        cmd = inp.get("command", "")
        if re.search(r"(?i)authorization\s*:", cmd):
            return "Jangan mengirim header Authorization sendiri: kunci API ditambahkan proxy (CLAUDE.md)."
        if re.search(r"\b(curl|wget)\b", cmd) and re.search(r"(-A\s|--user-agent|-U\s|Mozilla/)", cmd):
            return "Dilarang memalsukan identitas browser / mengakali pemblokir bot (brain/aturan-kompetitor.md)."
        if re.search(r"\bgit\s+add\b", cmd) and re.search(r"data/mentah|\.env\b", cmd):
            return "data/mentah/ (data pembeli) dan .env tidak boleh di-commit."
        if re.search(r"\bgit\s+commit\b", cmd):
            staged = git_staged if git_staged is not None else _staged()
            buruk = [f for f in staged["files"] if TERLARANG_GIT.search(f)]
            if buruk:
                return f"File terlarang ikut di-stage: {buruk[:5]}. Keluarkan dengan git restore --staged."
            if _kunci(staged["diff"]):
                return "Ada teks yang mirip kunci API di perubahan yang di-stage. Hapus sebelum commit."
        if _kunci(cmd):
            return "Perintah memuat teks yang mirip kunci API."
    elif alat in ("Write", "Edit", "MultiEdit"):
        isi = inp.get("content") or inp.get("new_string") or ""
        isi += "".join(e.get("new_string", "") for e in inp.get("edits") or [])
        if _kunci(isi):
            return f"Teks yang mirip kunci API tidak boleh ditulis ke file ({inp.get('file_path')})."
    return None


def _staged():
    def run(args):
        r = subprocess.run(["git"] + args, capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else ""
    return {"files": run(["diff", "--cached", "--name-only"]).split(), "diff": run(["diff", "--cached", "-U0"])}


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # input aneh: jangan menghalangi kerja
    alasan = periksa(data)
    if alasan:
        print(f"Ditolak penjaga proyek: {alasan}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
