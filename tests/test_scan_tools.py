import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scan_tools  # noqa: E402


class ScanToolsTest(unittest.TestCase):
    def test_parse_yaml_frontmatter_accepts_utf8_bom(self):
        metadata = scan_tools.parse_yaml_frontmatter(
            "\ufeff---\n"
            "name: tool-lister\n"
            "description: Lists tools\n"
            "---\n"
            "# Body\n"
        )

        self.assertEqual(metadata["name"], "tool-lister")
        self.assertEqual(metadata["description"], "Lists tools")

    def test_parse_yaml_frontmatter_accepts_folded_description(self):
        metadata = scan_tools.parse_yaml_frontmatter(
            "---\n"
            "name: folded-skill\n"
            "description: >\n"
            "  First line\n"
            "  second line\n"
            "version: 1.2.3\n"
            "---\n"
        )

        self.assertEqual(metadata["description"], "First line second line")
        self.assertEqual(metadata["version"], "1.2.3")

    def test_scan_all_skills_includes_claude_and_agents_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude_skill = root / ".claude" / "skills" / "claude-only"
            agents_skill = root / ".agents" / "skills" / "agents-only"
            claude_skill.mkdir(parents=True)
            agents_skill.mkdir(parents=True)
            (claude_skill / "SKILL.md").write_text(
                "---\nname: claude-only\ndescription: Claude skill\n---\n",
                encoding="utf-8",
            )
            (agents_skill / "SKILL.md").write_text(
                "---\nname: agents-only\ndescription: Agents skill\n---\n",
                encoding="utf-8",
            )

            skills = scan_tools.scan_all_skills(
                [
                    (root / ".claude" / "skills", "~/.claude/skills"),
                    (root / ".agents" / "skills", "~/.agents/skills"),
                ]
            )

        self.assertEqual([skill["name"] for skill in skills], ["agents-only", "claude-only"])
        self.assertEqual(
            {skill["name"]: skill["source"] for skill in skills},
            {
                "agents-only": "~/.agents/skills",
                "claude-only": "~/.claude/skills",
            },
        )


if __name__ == "__main__":
    unittest.main()
