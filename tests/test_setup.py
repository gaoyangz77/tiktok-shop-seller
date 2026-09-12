import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/tiktok-shop-seller/scripts"
sys.path.insert(0, str(SCRIPTS))
from mcp_config import BASE_URLS, CONFIG_PATHS, ENDPOINTS, entries, merge_config, safe_target, validate_base_url, write_config
from install_skill import install


class ConfigurationTests(unittest.TestCase):
    def test_codex_preserves_text_and_values(self):
        original = '# keep this comment\nmodel = "example"\n[mcp_servers.other]\ncommand = "other"\n'
        merged = merge_config("codex", original, BASE_URLS["production"])
        self.assertTrue(merged.startswith(original))
        data = tomllib.loads(merged)
        self.assertEqual(data["model"], "example")
        self.assertEqual(data["mcp_servers"]["other"], {"command": "other"})
        for name in ENDPOINTS:
            self.assertEqual(data["mcp_servers"][name]["oauth_resource"], BASE_URLS["production"] + "/mcp/shop-core")
            self.assertEqual(data["mcp_servers"][name]["scopes"], ["mcp:shop"])
        self.assertEqual(merge_config("codex", merged, BASE_URLS["production"]), merged)

    def test_json_preserves_other_configuration(self):
        for agent in ("claude", "workbuddy"):
            with self.subTest(agent=agent):
                original = json.dumps({"unrelated": [1], "mcpServers": {"other": {"command": "safe"}}})
                merged = merge_config(agent, original, BASE_URLS["staging"])
                data = json.loads(merged)
                self.assertEqual(data["unrelated"], [1])
                self.assertEqual(data["mcpServers"]["other"], {"command": "safe"})
                self.assertEqual(len(data["mcpServers"]), 4)
                self.assertEqual(data["mcpServers"]["tkcopilot_core"]["type"], "http")
                self.assertEqual(merge_config(agent, merged, BASE_URLS["staging"]), merged)

    def test_environment_conflict_never_overwrites(self):
        for agent in CONFIG_PATHS:
            current = merge_config(agent, "", BASE_URLS["production"])
            with self.subTest(agent=agent), self.assertRaises(ValueError):
                merge_config(agent, current, BASE_URLS["staging"])

    def test_malformed_or_duplicate_keys_refused(self):
        for value in ('[]', '{"mcpServers":[]}', '{"mcpServers":{},"mcpServers":{}}', '{"bad"'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                merge_config("claude", value, BASE_URLS["production"])
        with self.assertRaises(ValueError):
            merge_config("codex", 'mcp_servers = []', BASE_URLS["production"])

    def test_https_origin_validation(self):
        self.assertEqual(validate_base_url("https://example.com/"), "https://example.com")
        for value in ("http://example.com", "https://u:p@example.com", "https://example.com/mcp",
                      "https://example.com?key=x", "https://example.com?", "https://example.com/#",
                      "https://example.com/#x", "https://",
                      "https://example.com\n", "https://example.com:bad"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_base_url(value)

    def test_no_secrets_or_approval_overrides_generated(self):
        for agent in CONFIG_PATHS:
            data = entries(agent, BASE_URLS["production"])
            for item in data.values():
                self.assertNotIn("headers", item)
                self.assertNotIn("http_headers", item)
                self.assertNotIn("bearer_token_env_var", item)
                self.assertNotIn("default_tools_approval_mode", item)

    def test_backup_atomic_update_and_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / ".mcp.json"
            target.write_text('{"unrelated": true}\n')
            original = target.read_text()
            merged = merge_config("claude", original, BASE_URLS["production"])
            backup = write_config(target, original, merged)
            self.assertEqual(backup.read_text(), original)
            self.assertEqual(target.read_text(), merged)
            if os.name != "nt":
                self.assertEqual(target.stat().st_mode & 0o777, 0o600)
                self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
            self.assertIsNone(write_config(target, merged, merged))
            self.assertEqual(len(list(Path(directory).glob("*.bak"))), 1)
            with self.assertRaises(ValueError):
                write_config(target, original, merged)
            self.assertEqual(target.read_text(), merged)

    def test_symlink_config_or_parent_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "outside").mkdir()
            (root / ".codex").symlink_to(root / "outside", target_is_directory=True)
            with self.assertRaises(ValueError):
                safe_target(root, ".codex/config.toml")
            (root / ".mcp.json").symlink_to(root / "absent")
            with self.assertRaises(ValueError):
                safe_target(root, ".mcp.json")

    def test_dry_run_and_project_only_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "shop"
            project.mkdir()
            fake_home = root / "user"
            fake_home.mkdir()
            env = dict(os.environ, HOME=str(fake_home), PYTHONDONTWRITEBYTECODE="1")
            command = [sys.executable, str(SCRIPTS / "setup_mcp.py"), "--agent", "codex",
                       "--project-dir", str(project), "--environment", "staging"]
            result = subprocess.run(command + ["--dry-run"], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(project.iterdir()), [])
            result = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / ".codex/config.toml").exists())
            self.assertEqual(list(fake_home.iterdir()), [])
            repeat = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertEqual(repeat.returncode, 0)
            self.assertEqual(list(project.rglob("*.bak")), [])

    def test_parse_failure_does_not_print_private_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".mcp.json").write_text('{"private": "SENSITIVE_SENTINEL", bad}')
            result = subprocess.run([sys.executable, str(SCRIPTS / "setup_mcp.py"),
                                     "--agent", "claude", "--project-dir", str(root)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("SENSITIVE_SENTINEL", result.stdout + result.stderr)

    def test_install_is_project_local_idempotent_and_updates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "official"
            source.mkdir()
            (source / "SKILL.md").write_text("version 1")
            project = root / "shop"
            project.mkdir()
            target, changed = install(project, "codex", source, dry_run=True)
            self.assertTrue(changed)
            self.assertFalse(target.exists())
            target, changed = install(project, "codex", source)
            self.assertTrue(changed)
            self.assertEqual((target / "SKILL.md").read_text(), "version 1")
            (source / "SKILL.md").write_text("version 2")
            self.assertEqual((target / "SKILL.md").read_text(), "version 2")
            self.assertFalse(install(project, "codex", source)[1])
            with self.assertRaises(ValueError):
                install(project, "codex", root / "different-source")

    def test_install_preserves_existing_custom_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / ".claude/skills/tiktok-shop-seller"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("custom")
            with self.assertRaises(ValueError):
                install(root, "claude", SCRIPTS.parent)
            self.assertEqual((target / "SKILL.md").read_text(), "custom")
