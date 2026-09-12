from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/tiktok-shop-seller"


class ContentTests(unittest.TestCase):
    def test_standalone_skill_includes_license(self):
        self.assertEqual((SKILL / "LICENSE").read_text(), (ROOT / "LICENSE").read_text())

    def test_frontmatter_and_entry_size(self):
        text = (SKILL / "SKILL.md").read_text()
        self.assertTrue(text.startswith("---\nname: tiktok-shop-seller\ndescription: "))
        self.assertLess(len(text.splitlines()), 160)
        self.assertNotIn("[TODO", text)

    def test_local_markdown_links_resolve_and_all_workflows_are_reachable(self):
        visited = set()
        pending = [SKILL / "SKILL.md"]
        while pending:
            path = pending.pop().resolve()
            if path in visited:
                continue
            visited.add(path)
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                linked = (path.parent / target.split("#")[0]).resolve()
                self.assertTrue(linked.is_file(), f"{path}: broken link {target}")
                self.assertTrue(linked.is_relative_to(SKILL))
                if linked.suffix == ".md":
                    pending.append(linked)
        references = {p.resolve() for p in (SKILL / "references").rglob("*.md")}
        self.assertTrue(references.issubset(visited), references - visited)

    def test_business_taxonomy_not_transport_scopes(self):
        self.assertEqual({p.name for p in (SKILL / "references").iterdir()}, {
            "customer-service", "affiliate", "product-management", "inventory-management",
            "order-management", "store-performance", "foundations"})
        self.assertFalse((SKILL / "references/shop-core").exists())

    def test_shared_delivery_workflow_is_reused(self):
        for path in ("customer-service/index.md", "affiliate/review-sample-applications.md"):
            self.assertIn("../order-management/resolve-delivery-exceptions.md",
                          (SKILL / "references" / path).read_text())

    def test_safety_and_data_boundary_contracts(self):
        entry = (SKILL / "SKILL.md").read_text()
        for phrase in ("idempotencyKey", "Data, not instructions", "STORE.md",
                       "do not generate a fresh key", "No Desktop session context"):
            self.assertIn(phrase, entry)
        workflow = (SKILL / "references/affiliate/handle-creator-conversations.md").read_text()
        for phrase in ("input.dispatch: false", "input.dispatch: true",
                       "Never directly send/review", "not that a message was delivered"):
            self.assertIn(phrase, workflow)
        ownership = (SKILL / "references/foundations/workspace-and-data-ownership.md").read_text()
        for phrase in ("no assumed public MCP write interface", "not last-write-wins",
                       "not executable instructions", "git pull --ff-only"):
            self.assertIn(phrase, ownership)

    def test_public_skill_has_no_template_store_or_plugin(self):
        self.assertFalse((ROOT / ".codex-plugin").exists())
        self.assertFalse((ROOT / ".claude-plugin").exists())
        self.assertFalse((ROOT / "template").exists())
        self.assertEqual(list(SKILL.rglob("STORE.md")), [])
        for path in SKILL.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".py"):
                value = path.read_text()
                self.assertNotIn("/Users/", value)
                self.assertNotIn("/home/", value)
                self.assertNotRegex(value, r"[A-Za-z0-9._%+-]+@(?:gmail|outlook|qq)\.com")
