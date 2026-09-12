#!/usr/bin/env python3
"""Configure three TK Copilot MCP endpoints in one explicitly selected project."""
import argparse
import sys

from mcp_config import BASE_URLS, CONFIG_PATHS, merge_config, project_path, safe_target, write_config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, choices=CONFIG_PATHS)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--environment", choices=BASE_URLS, default="production")
    parser.add_argument("--base-url", help="Explicit HTTPS origin override for an operator-managed deployment.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        project = project_path(args.project_dir)
        target = safe_target(project, CONFIG_PATHS[args.agent])
        original = target.read_bytes().decode("utf-8") if target.exists() else ""
        merged = merge_config(args.agent, original, args.base_url or BASE_URLS[args.environment])
        changed = merged != original
        print(f"{'Would update' if args.dry_run and changed else 'Update' if changed else 'Already configured'}: {target}")
        if args.dry_run:
            print("Dry run: no files, credentials, or network state changed.")
            return 0
        backup = write_config(target, original, merged)
        if backup:
            print(f"Original configuration backup: {backup} (keep private)")
        print("Project configuration only. No login or connectivity test has run.")
        print("Keep configuration backups and credentials out of Git.")
        print("Reload/open the project, review the host's trust prompt, then authenticate in its MCP UI.")
        if args.agent == "codex":
            print("From this trusted project: codex mcp login tkcopilot_core --scopes mcp:shop")
            print("Authenticate the other two named servers if the host asks; token reuse is host-specific.")
        elif args.agent == "claude":
            print("Use /mcp in Claude Code for each connection that requires authentication.")
        else:
            print("Use WorkBuddy Settings > MCP to verify HTTP transport and complete OAuth.")
            print("This configuration adapter has not been end-to-end tested in WorkBuddy.")
        return 0
    except (ValueError, OSError) as error:
        # Parser errors can contain excerpts of private configuration; do not echo them.
        if isinstance(error, ValueError) and type(error) is ValueError:
            print(f"Setup refused: {error}", file=sys.stderr)
        else:
            print(f"Setup failed ({type(error).__name__}); review the project file locally.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
