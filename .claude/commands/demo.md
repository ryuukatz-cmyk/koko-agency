---
description: Jalankan demo alur lengkap dengan data CONTOH (latihan, tanpa data asli)
argument-hint: "[--flux untuk pakai Cloudflare nyata]"
---
Jalankan `python3 scripts/demo.py --out demo-out $ARGUMENTS`. Baca `demo-out/RINGKASAN.md`, lalu buka dengan Read beberapa hasil:
satu foto `F01`, banner `D01`, dan satu frame video (`ffmpeg -v error -ss 12 -i <video> -frames:v 1 /tmp/frame.png`).
Jelaskan ke pemilik apa yang dihasilkan tiap langkah dan apa yang akan berbeda saat memakai data asli. Ingatkan: demo melewati qc dan persetujuan.
