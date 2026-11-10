# Riset kompetitor CONTOH-KOKO-01 (uji sistem) — siap dicek

Dicek: 2026-11-10. Harga normal kita: Rp150.000. Status: **DATA_KURANG** (0 dari minimal 5 pembanding terverifikasi).

## Perintah
`python3 scripts/kompetitor.py --csv tests/data/batch-uji-kompetitor/kompetitor.csv --hari-ini 2026-11-10 --harga-kita 150000` (exit 1)

## Output script
```json
{"jumlah_baris": 1, "terverifikasi": 0, "cuplikan": 1, "ditolak": [], "harga_min": null, "harga_median": null, "harga_max": null, "lebih_murah_dari_kita": 0, "status": "DATA_KURANG"}
```
Catatan: `lebih_murah_dari_kita: 0` karena tidak ada baris terverifikasi, bukan karena tidak ada yang lebih murah.

## Temuan
**Fakta yang terlihat (hanya dari cuplikan pencarian, belum dibuka langsung, tidak dihitung):**
1. Pencarian 2 kali (WebSearch) tidak menemukan listing yang cocok di ketiga ciri sekaligus (navy, kerah shanghai, bordir emas di dada). Dicari: "navy, bordir emas, kerah shanghai" dan "biru dongker bordir emas dada".
2. Koko navy lengan panjang berbordir yang muncul di cuplikan: AMK "Bordir KK ZAKI L/S NAVY" Rp125.000 (coret Rp469.000, 27 terjual, rating 5.0); DGM Navy Bordir Motif Hexagonal Rp186.000; DGM Premium Biru Navy Motif Jaring Segi Enam Rp194.000 (3 terjual); PAKAJI Deep Blue Rp194.000. Warna bordir tidak disebut di cuplikan.
3. Koko shanghai navy polos (Platini) disebut kisaran Rp99.000–Rp180.000 di cuplikan, tanpa harga per produk.
4. "Light Gold" milik PAKAJI adalah nama warna kain, bukan bordir emas.

**Dugaan (belum terbukti):**
- Harga Rp125.000–Rp194.000 untuk koko navy berbordir mungkin menjadi kisaran pasar, jadi Rp150.000 kita kemungkinan di tengah. Belum boleh dipakai marketer sampai ada 5 halaman terverifikasi.
- Kombinasi navy + bordir emas dada + kerah shanghai mungkin cukup jarang. Itu bisa jadi pembeda, tapi belum terbukti: "tidak ditemukan" tidak sama dengan "tidak ada".
- Harga coret AMK (Rp469.000 jadi Rp125.000) tampak seperti coret besar, bukan harga acuan nyata. Ini dugaan.

## Halaman yang tidak bisa dibuka (dicatat, tidak diakali)
- Tokopedia, WebFetch gagal "socket hang up" (percobaan 1 kali per halaman, ditambah 1 halaman daftar pencarian):
  - https://www.tokopedia.com/platini-official-store/platini-kemeja-pria-koko-shanghai-lengan-panjang-katun-961310-1730879801381192937
  - https://www.tokopedia.com/platini-official-store/last-call-platini-kemeja-koko-bordir-timbul-pria-lengan-panjang-polyester-96949-1729756468454787305
  - https://www.tokopedia.com/kemejadancus/dancus-baju-muslim-pria-baju-koko-motif-bordir-lengan-panjang-warna-coklat-olrm318-1734222286579992366
  - https://www.tokopedia.com/bombboogie/bombboogie-kemeja-pria-long-pragma-dark-blue-koko-regular-24650b2dl-s
  - https://www.tokopedia.com/vanfiveofficial/vanfive-kemeja-pria-koko-kemko-salur-stripe-lengan-panjang-arhan-putih-1731531973344987006
  - https://www.tokopedia.com/find/baju-koko-warna-navy
- Blibli, HTTP 403: https://www.blibli.com/p/baju-koko-lengan-panjang-baju-kok-batik-baju-muslim-pria-baju-atasan-pria-baju-lebaran/ps--STF-70009-00038
- Shopee/TikTok Shop/IG: tidak dicoba, karena Claude in Chrome tidak tersedia di sesi ini.
- AMK dan DGM: cuplikan tidak memberi link produk, jadi tidak dimasukkan ke CSV.

## Langkah lanjut
Ulangi saat Tokopedia/Blibli bisa dibuka, atau jalankan lewat Claude in Chrome di komputer pemilik. Jalur ini perlu dicek oleh head: apakah "socket hang up" masalah proxy environment.
