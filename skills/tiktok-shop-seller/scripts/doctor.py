#!/usr/bin/env python3
"""Read-only, unauthenticated deployment preflight. Never sends email or merchant API writes."""
import argparse
import concurrent.futures
import json
import re
import ssl
import sys
import urllib.error
import urllib.request

from mcp_config import BASE_URLS, ENDPOINTS, validate_base_url

MAX_METADATA_BYTES = 65536


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url, timeout):
    request = urllib.request.Request(url, headers={"Accept": "application/json, text/event-stream",
                                                  "User-Agent": "tiktok-shop-seller-doctor/0.1"})
    opener = urllib.request.build_opener(NoRedirects())
    try:
        with opener.open(request, timeout=timeout) as response:
            # A 200 MCP GET may be a long-lived SSE stream; do not consume it.
            body = response.read(MAX_METADATA_BYTES + 1) if "/.well-known/" in url else b""
            return response.status, dict(response.headers.items()), body
    except urllib.error.HTTPError as error:
        try:
            return error.code, dict(error.headers.items()), b""
        finally:
            error.close()
    except urllib.error.URLError as error:
        reason = error.reason
        kind = ("tls_certificate_error" if isinstance(reason, ssl.SSLCertVerificationError)
                else "timeout" if isinstance(reason, TimeoutError) else "network_error")
        return 0, {"_preflight_error": kind}, b""
    except (TimeoutError, OSError):
        return 0, {"_preflight_error": "network_error_or_timeout"}, b""


def metadata(body):
    if len(body) > MAX_METADATA_BYTES:
        return {}
    try:
        value = json.loads(body)
        return value if isinstance(value, dict) else {}
    except (ValueError, UnicodeError):
        return {}


def includes(data, key, value):
    items = data.get(key)
    return isinstance(items, list) and value in items


def inspect(base_url, fetcher=fetch, timeout=8):
    base = validate_base_url(base_url)
    resource = base + "/mcp/shop-core"
    discovery = base + "/.well-known/oauth-protected-resource/mcp/shop-core"
    issuer_url = base + "/.well-known/oauth-authorization-server"
    targets = {"resource_metadata": discovery, "authorization_metadata": issuer_url,
               **{name: base + path for name, path in ENDPOINTS.items()}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(targets)) as pool:
        results = dict(zip(targets, pool.map(lambda url: fetcher(url, timeout), targets.values())))
    checks = []
    status, _, body = results["resource_metadata"]
    data = metadata(body)
    resource_ok = (
        status == 200 and data.get("resource") == resource
        and includes(data, "authorization_servers", base)
        and includes(data, "scopes_supported", "mcp:shop")
    )
    checks.append({"check": "resource_metadata", "ok": resource_ok, "http_status": status})
    status, _, body = results["authorization_metadata"]
    data = metadata(body)
    issuer_ok = (
        status == 200 and data.get("issuer") == base
        and data.get("authorization_endpoint") == base + "/oauth/authorize"
        and data.get("token_endpoint") == base + "/oauth/token"
        and data.get("registration_endpoint") == base + "/oauth/register"
        and includes(data, "code_challenge_methods_supported", "S256")
        and includes(data, "grant_types_supported", "authorization_code")
    )
    checks.append({"check": "authorization_metadata", "ok": issuer_ok, "http_status": status})
    for name in ENDPOINTS:
        status, headers, _ = results[name]
        challenge = next((v for k, v in headers.items() if k.lower() == "www-authenticate"), "")
        advertised = re.search(r'resource_metadata="([^"]+)"', challenge)
        ok = status == 401 and "bearer" in challenge.lower() and advertised is not None and advertised[1] == discovery
        checks.append({"check": name, "ok": ok, "http_status": status})
    return {
        "base_url": base, "preflight_ok": all(c["ok"] for c in checks), "checks": checks,
        "network_errors": {name: headers.get("_preflight_error", "network_error")
                           for name, (status, headers, _) in results.items() if status == 0},
        "authenticated": False,
        "note": "Preflight only: OAuth login, tool discovery, shop access and writes are NOT tested.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", choices=BASE_URLS, default="production")
    parser.add_argument("--base-url")
    parser.add_argument("--timeout", type=float, default=8)
    args = parser.parse_args()
    try:
        if not 0 < args.timeout <= 30:
            raise ValueError("Timeout must be between 0 and 30 seconds.")
        report = inspect(args.base_url or BASE_URLS[args.environment], timeout=args.timeout)
        print(json.dumps(report, indent=2))
        return 0 if report["preflight_ok"] else 1
    except (ValueError, OSError):
        print("Invalid preflight configuration; no login attempted.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
