# Aturan fase belajar

Tujuan: agent makin ahli dengan mencatat pengetahuan yang **sudah dicek** ke `brain/`. Agent tidak ingat apa pun antar sesi;
yang tidak tertulis di `brain/` dianggap tidak diketahui.

## Dua sumber pengetahuan
1. **Luar** — riset lewat Claude in Chrome di komputer pemilik (e-commerce, web, Pinterest, IG, TikTok, Meta Ad Library), atau WebSearch di cloud.
2. **Dalam** — hasil batch kita sendiri (unit terjual, rupiah kembali). Ini yang paling berharga: dicatat di `brain/pelajaran.md`.

## Alur
1. **Pertanyaan dulu.** Head menulis brief berisi satu pertanyaan yang jelas, mis. "banner toko koko seperti apa yang dipakai toko dengan >1.000 terjual?".
   Tanpa pertanyaan, tidak ada browsing.
2. **Researcher mencari** dan menulis draf `belajar/<YYYY-MM-DD>-<topik>.md` (templat di bawah).
3. **Head memeriksa draf.** Poin tanpa link/tanggal, atau dugaan yang ditulis seperti fakta, dibuang. Poin yang lolos disalin ke file
   `brain/referensi-*.md` atau `brain/pelajaran.md` dengan tanda `(disetujui head YYYY-MM-DD, sumber: belajar/...)`.
4. **Agent memakai** `brain/` saat bekerja. qc mengecek bahwa yang dipakai tidak melanggar aturan.

## Batas
- Hanya halaman publik, baca saja. Tidak login ke akun orang lain, tidak klik beli/chat/follow, tidak mengakali pemblokir bot.
- Maksimal ±20 halaman per pertanyaan. Halaman yang menolak dicatat, tidak diakali.
- **Pinterest/IG/toko lain = inspirasi saja.** Gambar, desain, dan teks orang lain tidak disalin (hak cipta). Yang dicatat adalah **pola**
  (mis. "banner atas memakai foto model + harga besar"), bukan file gambarnya. Produk di konten tetap foto koko kita sendiri.
- Tidak menyimpan data pribadi (nama/foto pengulas, nomor HP, username pembeli).
- Seller Centre/Shopee milik sendiri: boleh dibaca; **tidak mengubah apa pun**. Dekorasi toko dibuat agent, **dipasang pemilik**.

## Kapan diperbarui (pengetahuan bisa basi)
- Harga kompetitor: tiap batch, dan riset ulang **sebulan sekali** + **sebelum Ramadan/Lebaran** (musim koko).
- Prompt & dekorasi: saat hasil QC sering gagal, atau tiap 3 bulan.
- Setiap poin di `brain/referensi-*.md` punya tanggal; poin > 6 bulan dianggap perlu dicek ulang.

## Templat draf `belajar/<YYYY-MM-DD>-<topik>.md`
```
# <topik> — <YYYY-MM-DD>
Pertanyaan: <dari brief head>
Alat: Claude in Chrome / WebSearch. Halaman dibuka: <n>
## Fakta yang terlihat
- <poin> — <link> (dicek <YYYY-MM-DD>)
## Dugaan (belum terbukti)
- <poin> — alasannya
## Usulan untuk brain/
- <file tujuan>: <poin singkat>
## Halaman yang gagal dibuka
- <link> — <alasan>
```
