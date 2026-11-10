# Agency Deadstock Koko — Rencana Implementasi

> **Untuk agent pelaksana:** dikerjakan langsung (native) di sesi ini, tugas demi tugas, sesuai instruksi pemilik "kerjakan sendiri sampai selesai". Langkah memakai checkbox (`- [ ]`).

**Goal:** Tim agent Claude Code + script Python kecil yang memilih deadstock, menghitung harga aman, membuat foto/video, dan memeriksa semuanya, berhenti di titik keputusan manusia.

**Architecture:** Agent di `.claude/agents/`, aturan di `brain/`, hitungan pasti di `scripts/` (Python stdlib + openpyxl, HTTP lewat `curl`). Satu batch = satu folder `batch/<id>/` dengan `status.json` yang hanya diubah head.

**Tech Stack:** Python 3.13, unittest, openpyxl, Pillow (hanya untuk mengecilkan master & data uji), ffmpeg/ffprobe, curl.

**Spec:** `docs/desain.md`

## Global Constraints

- Harga akhir ≥ HPP ÷ (1 − admin%), dibulatkan ke atas ke rupiah penuh. Admin default 10% (ASUMSI). Semua uang dalam bilangan bulat rupiah.
- Deadstock: hari tanpa penjualan ≥ 60 **dan** stok ≥ 5 (ASUMSI).
- Skor = 50·modal/modal_maks + 30·umur/umur_maks + 20·stok/stok_maks, dibulatkan 1 desimal.
- Video: 1080×1920, 15–30 detik, tanpa audio.
- Tidak ada header Authorization di kode. Tidak ada API key di file.
- Kolom data pembeli tidak boleh ditulis ke file apa pun.

## Review Focus

1. Export dengan nama kolom sedikit berbeda (spasi, huruf besar) → tetap dikenali lewat normalisasi nama kolom.
2. Angka rupiah bergaya Indonesia ("Rp 125.000", "125.000,00") → dibaca sebagai 125000.
3. Kolom pembeli yang namanya tidak ada di daftar → tetap tidak lolos (ringkasan hanya menulis kolom yang diizinkan).
4. Pesanan batal → tidak dihitung terjual.
5. Provider gambar mati di tengah batch → provider itu tidak dipanggil lagi untuk foto berikutnya.

Masing-masing punya tes di tugas pemiliknya.

---

### Task 1: Pondasi repo
**Files:** `.gitignore`, `CLAUDE.md`, `ROADMAP.md`
- [ ] `.gitignore`: `data/mentah/`, `*.mp4`, `*.mov`, `batch/*/video/`, `__pycache__/`, `.env`; kecuali `tests/data/**` kecil.
- [ ] CLAUDE.md ≤ 40 baris: aturan inti. ROADMAP.md: ops, cs, ads (tidak dibangun).
- [ ] Commit.

### Task 2: `scripts/harga.py` (TDD)
**Produces:** `harga_minimum(hpp:int, admin_persen:float)->int`, `hitung(harga_normal:int, hpp:int, admin_persen:float, diskon_persen:float=0, voucher_rp:int=0)->dict` dengan kunci `harga_akhir, biaya_admin, terima_bersih, margin_rp, margin_persen, harga_minimum, lulus`. CLI: `python3 scripts/harga.py --harga-normal --hpp --admin-persen [--diskon-persen] [--voucher-rp]` mencetak JSON; exit 1 bila tidak lulus.
- [ ] Tes `tests/test_harga.py`: `harga_minimum(90000,10)==100000`; `harga_minimum(100001,10)==111113`; pas di batas (`hitung(125000,90000,10,20)` → harga_akhir 100000, lulus True, margin_rp 0); di bawah (`diskon 21%` → lulus False); voucher mengurangi harga; HPP None → ValueError; diskon >100 atau negatif → ValueError.
- [ ] Jalankan → gagal. Implementasi dengan `math.ceil` pada pecahan `Fraction` (hindari float). Jalankan → lulus. Commit.

### Task 3: `scripts/export.py` (TDD)
**Produces:** `baca_tabel(path)->list[dict]` (csv/xlsx), `buang_data_pembeli(rows)->list[dict]`, `angka(s)->int|None`, `ringkas_per_sku(pesanan, stok, hpp, hari_ini:date)->list[dict]` kolom `sku,nama,stok,harga,hpp,unit_terjual,terakhir_terjual,hari_tanpa_jual,catatan`. CLI: `--pesanan --stok --hpp --hari-ini --out`.
- [ ] Tes: kolom `Username (Pembeli)`, `Nama Penerima`, `No. Telepon`, `Alamat Pengiriman`, `Kota/Kabupaten`, `Provinsi`, `Kode Pos`, `Catatan dari Pembeli` hilang; kolom asing tidak ikut ke ringkasan; `angka("Rp 125.000")==125000`, `angka("")is None`; pesanan batal tidak dihitung; SKU tanpa penjualan → `hari_tanpa_jual` = hari sejak pesanan tertua + catatan `TIDAK_TERJUAL_SEPANJANG_DATA`; HPP kosong → `hpp` kosong + `HPP_KOSONG`; SKU dobel di stok → `SKU_DOBEL`; kolom wajib hilang → ValueError yang menyebut nama kolom.
- [ ] Merah → implementasi → hijau. Commit.

### Task 4: `scripts/deadstock.py` (TDD)
**Consumes:** CSV dari Task 3. **Produces:** `pilih(rows, min_hari=60, min_stok=5)->list[dict]` diurutkan skor menurun; tambah kolom `modal_tertahan, skor, status` (`DEADSTOCK`, `DEADSTOCK_DATA_KURANG`). CLI `--ringkas --out`.
- [ ] Tes: stok 0 / stok 4 / 59 hari → tidak masuk; 60 hari & stok 5 → masuk; HPP kosong → masuk dengan skor kosong, status `DEADSTOCK_DATA_KURANG`, di urutan akhir; SKU_DOBEL → `DEADSTOCK_DATA_KURANG`; contoh skor 3 SKU dihitung manual.
- [ ] Merah → hijau. Commit.

### Task 5: `scripts/gambar.py`
**Produces:** `buat(master, prompts:list[str], out_dir, batch_dir)->dict` (`{"status": "SELESAI"|"WAITING_FOTO", "foto":[...]}`), `_post(args)->bytes` (satu-satunya pemanggil `curl`, di-mock di tes). Menulis `foto/F01.png…`, `foto/metadata.json`; kalau jatuh ke manual → `prompt-foto.md`.
- [ ] Tes `tests/test_gambar.py` dengan mock: Gemini 429 → Cloudflare dipakai, metadata `provider=cloudflare`; Gemini dipanggil sekali saja walau 3 prompt; tanpa `CF_ACCOUNT_ID` → manual, `prompt-foto.md` berisi 10 prompt, status WAITING_FOTO; argumen curl tidak mengandung "Authorization".
- [ ] Implementasi. Hijau. Commit.

### Task 6: `scripts/video.py`
**Produces:** `slideshow(fotos, nama, harga_teks, out)`, `dari_flow(klip, nama, harga_teks, out)`, `buat(foto_dir, flow_dir|None, nama, harga_teks, out)` (pilih Flow kalau ada klip, kalau tidak slideshow), `cek(path)->dict` (lebar, tinggi, durasi, ok).
- [ ] Tes: slideshow 3 foto → durasi 15–30 dtk, 1080×1920; 12 foto → ≤30 dtk; flow dir kosong → slideshow; `cek` file rusak → ok False.
- [ ] Implementasi. Hijau. Commit.

### Task 7: Brain + agent
**Files:** `brain/*`, `.claude/agents/{head,researcher,marketer,creative,qc}.md`
- [ ] Brain diisi asumsi bertanda "ASUMSI". `produk.csv` dan product-lock berisi template + contoh palsu `CONTOH-KOKO-01` (ditandai CONTOH).
- [ ] Agent sesuai tabel peran di desain; frontmatter `name, description, model, tools`. Commit.

### Task 8: Uji (Fase 3)
- [ ] `tests/kasus-uji.md` 20 kasus + 3 kasus provider/video.
- [ ] `tests/data/`: export palsu, HPP palsu, gambar produk palsu (master, versi warna berubah, versi buram, produk lain), batch uji dengan cacat tertanam.
- [ ] Jalankan tes script + QC independen (subagent dengan instruksi `qc.md`) + head untuk kasus intake.
- [ ] Satu video slideshow nyata + ffprobe. `tests/hasil-uji.md`.
- [ ] Review kode oleh `agent-skills:code-reviewer`; perbaiki temuan serius. Verifikasi akhir. Commit, push, berhenti.

---

## Tambahan: Riset kompetitor (desain §13)

**Goal:** researcher menghasilkan tabel harga pembanding per SKU yang angkanya bisa dicek; marketer & qc memakainya.

**Review Focus**
1. Harga ditulis "125rb" → terbaca 125 → harus ditolak (harga < Rp1.000 tidak masuk akal).
2. Link sama dicatat dua kali → dihitung sekali.
3. Baris tanpa link/sumber/tanggal, atau tanggal di masa depan → ditolak dengan alasan, bukan diam-diam dipakai.
4. Jumlah terverifikasi genap → median memakai harga nyata (median bawah), bukan rata-rata dua harga.
5. File tanpa kolom wajib → exit 2 dengan nama kolom.

### Task 9: `scripts/kompetitor.py` (TDD)
**Produces:** `ringkas(rows:list[dict], hari_ini:date, min_pembanding=5, harga_kita:int|None=None) -> dict` dengan kunci
`jumlah_baris, terverifikasi, cuplikan, ditolak:[{baris,alasan}], harga_min, harga_median, harga_max, lebih_murah_dari_kita, status ("CUKUP"|"DATA_KURANG")`.
CLI `--csv --hari-ini [--harga-kita]`, cetak JSON; exit 0 CUKUP, 1 DATA_KURANG, 2 input salah. Pakai `export.angka`, `export.baca_tabel`.
- [ ] Tes `tests/test_kompetitor.py`: 5 terverifikasi [100k,120k,150k,180k,200k] + 2 cuplikan [50k,300k] → min 100000, median 150000, max 200000, CUKUP;
  4 terverifikasi → DATA_KURANG; tanpa link / sumber asing / tanggal kosong / tanggal masa depan / "125rb" → ditolak; link dobel dihitung sekali;
  6 harga → median bawah; harga_kita 130000 → lebih_murah_dari_kita 2; CLI exit 0/1/2.
- [ ] Merah → implementasi → hijau. Commit.

### Task 10: Aturan & agent
- [ ] `brain/aturan-kompetitor.md`; CLAUDE.md (aturan baca-saja + perintah); researcher (bagian riset kompetitor, tools WebSearch, WebFetch, Claude in Chrome);
  head (syarat RISET→STRATEGI); marketer (pakai kompetitor.md); qc (cek f). Commit.

### Task 11: Uji
- [ ] Kasus K1–K5 di `tests/kasus-uji.md`; satu riset nyata oleh researcher (proses Claude baru) untuk CONTOH-KOKO-01; cek hasilnya dengan script; catat di `tests/hasil-uji.md`. Commit, push.
