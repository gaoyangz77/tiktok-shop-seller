import json
import ssl
import urllib.error
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/tiktok-shop-seller/scripts"))
from doctor import fetch, inspect, metadata, NoRedirects
from mcp_config import ENDPOINTS

BASE = "https://shop.example.com"
DISCOVERY = BASE + "/.well-known/oauth-protected-resource/mcp/shop-core"


def healthy(url, timeout):
    if url == DISCOVERY:
        data = {"resource": BASE + "/mcp/shop-core", "authorization_servers": [BASE],
                "scopes_supported": ["mcp:shop"]}
    elif url.endswith("/.well-known/oauth-authorization-server"):
        data = {"issuer": BASE, "authorization_endpoint": BASE + "/oauth/authorize",
                "token_endpoint": BASE + "/oauth/token", "registration_endpoint": BASE + "/oauth/register",
                "code_challenge_methods_supported": ["S256"], "grant_types_supported": ["authorization_code"]}
    else:
        return 401, {"WWW-Authenticate": f'Bearer resource_metadata="{DISCOVERY}"'}, b""
    return 200, {}, json.dumps(data).encode()


class DoctorTests(unittest.TestCase):
    def test_healthy_preflight_is_not_authentication(self):
        seen = []
        def fetcher(url, timeout):
            seen.append(url)
            return healthy(url, timeout)
        report = inspect(BASE, fetcher)
        self.assertTrue(report["preflight_ok"])
        self.assertFalse(report["authenticated"])
        self.assertEqual(len(report["checks"]), 5)
        self.assertEqual(len(seen), 5)
        self.assertFalse(any(url.endswith(("/oauth/authorize", "/oauth/register", "/oauth/token")) for url in seen))

    def test_404_never_passes(self):
        report = inspect(BASE, lambda url, timeout: (404, {}, b"nginx"))
        self.assertFalse(report["preflight_ok"])
        self.assertTrue(all(c["http_status"] == 404 for c in report["checks"]))

    def test_html_null_and_wrong_metadata_fail_closed(self):
        for body in (b"<html>login</html>", b"null", b"[]", b'{"resource":null}', b"x" * 65537,
                     json.dumps({"resource": BASE + "/mcp/shop-core", "authorization_servers": None}).encode()):
            with self.subTest(body=body[:40]):
                report = inspect(BASE, lambda url, timeout: (200, {}, body))
                self.assertFalse(report["preflight_ok"])

    def test_wrong_audience_or_issuer_fails(self):
        for field, wrong in (("resource", BASE + "/mcp/affiliate"),
                             ("authorization_servers", ["https://wrong.example.com"])):
            def fetcher(url, timeout):
                status, headers, body = healthy(url, timeout)
                if url == DISCOVERY:
                    value = json.loads(body)
                    value[field] = wrong
                    body = json.dumps(value).encode()
                return status, headers, body
            with self.subTest(field=field):
                self.assertFalse(inspect(BASE, fetcher)["preflight_ok"])

    def test_endpoint_challenges_must_reference_canonical_metadata(self):
        for status, challenge in ((403, ""), (200, ""), (401, "Bearer"),
                                  (401, 'Bearer resource_metadata="https://wrong.example.com/metadata"')):
            def fetcher(url, timeout):
                if "/.well-known/" not in url:
                    return status, {"www-authenticate": challenge}, b""
                return healthy(url, timeout)
            with self.subTest(status=status, challenge=challenge):
                self.assertFalse(inspect(BASE, fetcher)["preflight_ok"])

    def test_redirects_are_not_followed(self):
        self.assertIsNone(NoRedirects().redirect_request(None, None, 302, "", {}, "https://elsewhere.example"))

    def test_tls_failure_is_reported_without_bypassing_verification(self):
        with patch("urllib.request.build_opener") as builder:
            builder.return_value.open.side_effect = urllib.error.URLError(
                ssl.SSLCertVerificationError("private error detail"))
            status, headers, body = fetch(BASE, 1)
        self.assertEqual(status, 0)
        self.assertEqual(headers["_preflight_error"], "tls_certificate_error")
        self.assertNotIn("private error detail", str((headers, body)))
        report = inspect(BASE, lambda url, timeout: (status, headers, body))
        self.assertFalse(report["preflight_ok"])
        self.assertEqual(set(report["network_errors"].values()), {"tls_certificate_error"})
