#!/usr/bin/env python3
"""Link this official skill into one Codex or Claude Code project; do not copy store data."""
import argparse
import sys
from pathlib import Path

from mcp_config import project_path, safe_target

SKILL_DIRS = {"codex": ".agents/skills", "claude": ".claude/skills"}


def install(project, agent, source, dry_run=False):
    target = project / SKILL_DIRS[agent] / "tiktok-shop-seller"
    safe_target(project, SKILL_DIRS[agent])
    if target.is_symlink() and target.resolve() == source.resolve():
        return target, False
    if target.exists() or target.is_symlink():
        raise ValueError("A different skill already exists here; nothing was replaced.")
    if not (source / "SKILL.md").is_file():
        raise ValueError("Source skill is incomplete.")
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source.resolve(), target_is_directory=True)
    return target, True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, choices=SKILL_DIRS)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        target, changed = install(project_path(args.project_dir), args.agent,
                                  Path(__file__).resolve().parent.parent, args.dry_run)
        print(f"{'Would link' if args.dry_run and changed else 'Linked' if changed else 'Already linked'}: {target}")
        print("Keep the official source directory in place; reload the host to discover the Skill.")
        print("Ignore this machine-local link in Git. Store customizations belong in STORE.md and knowledge/.")
        return 0
    except (OSError, ValueError) as error:
        print(f"Installation stopped: {error}. Import/copy the skill manually if symlinks are unavailable.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
