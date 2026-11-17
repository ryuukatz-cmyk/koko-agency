"""Integritas: setiap skill yang dimuat agent ada di .claude/skills, punya frontmatter, dan tercatat di SUMBER.md."""
import unittest, pathlib, re

AKAR = pathlib.Path(__file__).resolve().parent.parent
SKILLS = AKAR / ".claude" / "skills"


def frontmatter(path):
    teks = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", teks, re.S)
    return m.group(1) if m else ""


class TestSkillAgent(unittest.TestCase):
    def test_skill_yang_dimuat_agent_ada(self):
        sumber = (SKILLS / "SUMBER.md").read_text(encoding="utf-8")
        for agent in sorted((AKAR / ".claude" / "agents").glob("*.md")):
            fm = frontmatter(agent)
            blok = re.search(r"^skills:\n((?:  - .+\n?)+)", fm + "\n", re.M)
            for s in re.findall(r"  - (\S+)", blok.group(1)) if blok else []:
                with self.subTest(agent=agent.name, skill=s):
                    f = SKILLS / s / "SKILL.md"
                    self.assertTrue(f.is_file(), f"{agent.name} memuat {s} tapi {f} tidak ada")
                    self.assertRegex(frontmatter(f), rf"(?m)^name: {re.escape(s)}$")
                    self.assertIn(f"{s}", sumber, f"{s} belum tercatat di SUMBER.md")
                    # agent harus menyebut skill itu di catatan "Skill yang dimuat"
                    self.assertIn(s, agent.read_text(encoding="utf-8").split("---", 2)[2])

    def test_skill_yang_dirujuk_di_teks_agent_ada(self):
        for agent in sorted((AKAR / ".claude" / "agents").glob("*.md")):
            for rujukan in re.findall(r"\.claude/skills/([\w-]+)/SKILL\.md", agent.read_text(encoding="utf-8")):
                with self.subTest(agent=agent.name, skill=rujukan):
                    self.assertTrue((SKILLS / rujukan / "SKILL.md").is_file())

    def test_skill_luar_punya_lisensi(self):
        buatan_sendiri = {"riset-kata-kunci-marketplace", "listing-seo-marketplace", "dekorasi-toko",
                          "rencana-iklan-marketplace", "riset-konten-marketplace"}
        for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
            if d.name not in buatan_sendiri:
                with self.subTest(skill=d.name):
                    self.assertTrue((d / "LICENSE").is_file(), f"{d.name} tanpa LICENSE")

    def test_skill_social_tanpa_resep_curl_user_agent(self):
        # listening.md (resep curl dengan user-agent) sengaja tidak disalin: bertentangan dengan penjaga & aturan-kompetitor
        self.assertFalse((SKILLS / "social" / "references" / "listening.md").exists())


if __name__ == "__main__":
    unittest.main()
