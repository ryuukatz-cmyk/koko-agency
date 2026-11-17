# Sumber skill (diambil 2026-11-10, isinya sudah dibaca dan dicek)

| Skill | Dipakai agent | Sumber | Commit | Bintang | Lisensi |
|---|---|---|---|---|---|
| campaign-plan | head | anthropics/knowledge-work-plugins (resmi Anthropic, plugin Marketing) | e605d8d | resmi | Apache-2.0 |
| brand-review | qc | anthropics/knowledge-work-plugins (resmi Anthropic, plugin Marketing) | e605d8d | resmi | Apache-2.0 |
| competitor-profiling | researcher | coreyhaines31/marketingskills | 9d6d7ce | ±59 rb | MIT |
| copywriting, marketing-psychology | marketer | coreyhaines31/marketingskills | 9d6d7ce | ±59 rb | MIT |
| image | creative | coreyhaines31/marketingskills | 9d6d7ce | ±59 rb | MIT |
| riset-kata-kunci-marketplace | researcher | buatan sendiri untuk proyek ini (2026-11-17) | - | - | milik pemilik |
| listing-seo-marketplace | marketer | buatan sendiri untuk proyek ini (2026-11-17) | - | - | milik pemilik |
| rencana-iklan-marketplace | marketer | buatan sendiri untuk proyek ini (2026-11-17) | - | - | milik pemilik |
| dekorasi-toko | creative | buatan sendiri untuk proyek ini (2026-11-17) | - | - | milik pemilik |
| market-research | researcher | affaan-m/everything-claude-code (`skills/market-research`) | 3f14a10 | ±229 rb | MIT |
| competitive-brief | researcher (dibaca saat perlu) | anthropics/knowledge-work-plugins (resmi Anthropic, plugin Marketing) | e91a134 | resmi | Apache-2.0 |
| customer-research | researcher (dibaca saat perlu) | coreyhaines31/marketingskills | 1f83744 | ±59 rb | MIT |
| social | marketer & researcher (dibaca saat perlu) | coreyhaines31/marketingskills | 1f83744 | ±59 rb | MIT |
| riset-konten-marketplace | researcher | buatan sendiri untuk proyek ini (2026-11-17) | - | - | milik pemilik |
| ui-ux-pro-max | (untuk landing page nanti) | nextlevelbuilder/ui-ux-pro-max-skill | 4f2dbb6 | ±147 rb | MIT |

Pemeriksaan keamanan:
- Yang dicari: perintah jaringan (curl/wget/requests/urllib/subprocess), permintaan API key/password, "abaikan instruksi", eval/exec, symlink.
- Hasil: skill marketing berupa teks Markdown saja. Script ui-ux-pro-max hanya memakai pustaka bawaan Python dan membaca CSV lokal, tanpa akses internet. Folder tes dan evals tidak ikut disalin.
- Konflik dengan aturan proyek: skill `image` menanyakan API key dan menyebut alat berbayar; skill marketing umumnya ditulis untuk SaaS/jasa.
  Karena itu tiap agent diberi aturan: CLAUDE.md dan brain/ menang atas skill.
- Tambahan 2026-11-17 (riset lebih kuat): market-research, competitive-brief, customer-research, social diperiksa dengan cara yang sama.
  Semua teks Markdown tanpa script. Dari `social`, `references/listening.md` TIDAK disalin (resep curl ke Reddit/HN/Bluesky dengan
  user-agent sendiri: bertentangan dengan aturan-kompetitor dan hook penjaga); bagian "Publishing From Your Agent" tidak berlaku
  (agent tidak memposting). `evals/` tidak disalin.
- Dipertimbangkan, tidak dipakai: deep-research (ECC) — butuh MCP firecrawl/exa berbayar; skill riset sosial ScrapeCreators — butuh
  API berbayar; review-reputation & social-content-engine (Anthropic small-business) — dirancang untuk Google/Yelp/Shopify/Canva,
  disimpan untuk fase CS nanti.
- Tidak dipakai: ad-creative (contohnya mengirim API key sendiri dan memakai model video berbayar), offers & pricing (untuk SaaS/jasa mahal, bukan toko baju).
