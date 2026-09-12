"""Project-only configuration helpers; no credentials or network access."""
import json
import os
import tempfile
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

BASE_URLS = {
    "production": "https://api.rivonclaw.com",
    "staging": "https://api-stg.rivonclaw.com",
}
ENDPOINTS = {
    "tkcopilot_core": "/mcp/shop-core",
    "tkcopilot_customer_service": "/mcp/customer-service",
    "tkcopilot_affiliate": "/mcp/affiliate",
}
CONFIG_PATHS = {
    "codex": ".codex/config.toml",
    "claude": ".mcp.json",
    "workbuddy": ".workbuddy/mcp.json",
}


def validate_base_url(value):
    parts = urlsplit(value)
    if (
        parts.scheme != "https" or not parts.hostname or parts.username or parts.password
        or "?" in value or "#" in value or parts.path not in ("", "/")
        or any(c.isspace() or ord(c) < 32 for c in value)
    ):
        raise ValueError("Base URL must be an HTTPS origin without credentials, path, or query.")
    _ = parts.port  # Also reject malformed ports.
    return value.rstrip("/")


def project_path(value):
    project = Path(value).expanduser().resolve()
    if not project.is_dir():
        raise ValueError("Project directory must already exist.")
    return project


def safe_target(project, relative):
    target = project / relative
    current = target
    while current != project:
        if current.is_symlink():
            raise ValueError("Refusing a symlink in the configuration destination.")
        current = current.parent
    return target


def entries(agent, base_url):
    base_url = validate_base_url(base_url)
    if agent == "codex":
        return {name: {"url": base_url + path,
                       "oauth_resource": base_url + "/mcp/shop-core",
                       "scopes": ["mcp:shop"]} for name, path in ENDPOINTS.items()}
    return {name: {"type": "http", "url": base_url + path}
            for name, path in ENDPOINTS.items()}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON keys; resolve them before setup.")
        result[key] = value
    return result


def merge_config(agent, original, base_url):
    """Return merged text. Refuse collisions; preserve unrelated values."""
    wanted = entries(agent, base_url)
    if agent == "codex":
        document = tomllib.loads(original)
        key = "mcp_servers"
    else:
        document = json.loads(original, object_pairs_hook=unique_object) if original.strip() else {}
        key = "mcpServers"
    if not isinstance(document, dict) or not isinstance(document.get(key, {}), dict):
        raise ValueError("MCP configuration must be an object/table.")
    servers = document.get(key, {})
    missing = {}
    for name, value in wanted.items():
        if name in servers and servers[name] != value:
            raise ValueError(f"Existing {name} differs. Review it manually; nothing was overwritten.")
        if name not in servers:
            missing[name] = value
    if not missing:
        return original
    if agent == "codex":
        sections = []
        for name, value in missing.items():
            rows = [f"[mcp_servers.{name}]"]
            rows.extend(f"{k} = {json.dumps(v)}" for k, v in value.items())
            sections.append("\n".join(rows))
        merged = original + ("\n" if original else "") + "\n\n".join(sections) + "\n"
        parsed = tomllib.loads(merged)
        expected = dict(document)
        expected[key] = {**servers, **missing}
        if parsed != expected:
            raise ValueError("Cannot safely append to this TOML layout.")
        return merged
    document[key] = {**servers, **missing}
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def write_config(target, original, merged):
    """Back up an existing file, then atomically replace it; never print its contents."""
    if merged == original:
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink() or (target.exists() and target.read_bytes() != original.encode("utf-8")):
        raise ValueError("Configuration changed during setup; retry after reviewing it.")
    backup = None
    if target.exists():
        fd, name = tempfile.mkstemp(prefix=target.name + ".tkcopilot-", suffix=".bak", dir=target.parent)
        backup = Path(name)
        with os.fdopen(fd, "wb") as handle:
            handle.write(original.encode("utf-8"))
    fd, name = tempfile.mkstemp(prefix=target.name + ".tkcopilot-", suffix=".tmp", dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(merged.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return backup
