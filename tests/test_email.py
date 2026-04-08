import os
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from email_template import render_patch_email  # noqa: E402


class TestEmailTemplate(unittest.TestCase):
    def test_render_patch_email_structure(self):
        result = render_patch_email(
            version="26.5",
            summary="Major top lane changes this patch.",
            tier_highlights=["S-tier: Fiora", "A-tier: Darius"],
            app_base_url="https://example.com",
            unsubscribe_url="https://example.com/api/unsubscribe?token=abc",
        )

        self.assertIn("subject", result)
        self.assertIn("html", result)
        self.assertIn("text", result)
        self.assertIn("headers", result)
        self.assertIn("26.5", result["subject"])
        self.assertIn("Fiora", result["html"])
        self.assertIn("Darius", result["text"])
        self.assertIn("List-Unsubscribe", result["headers"])

    def test_render_escapes_html(self):
        result = render_patch_email(
            version="26.5",
            summary='<script>alert("xss")</script>',
            tier_highlights=["S-tier: <b>Fiora</b>"],
            app_base_url="https://example.com",
            unsubscribe_url="https://example.com/unsub",
        )
        self.assertNotIn("<script>", result["html"])
        self.assertIn("&lt;script&gt;", result["html"])


class TestEmailEndpoints(unittest.TestCase):
    def setUp(self):
        import api
        from fastapi.testclient import TestClient
        self.client = TestClient(api.app)

    def test_subscribe_success(self):
        with patch("subscribers.upsert_active", return_value=(
            {"email": "a@b.com", "status": "active", "unsubscribe_token": "tok"},
            "created",
        )):
            resp = self.client.post("/api/subscribe", json={"email": "a@b.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["ok"])
        self.assertEqual(resp.json()["action"], "created")

    def test_subscribe_invalid_email(self):
        resp = self.client.post("/api/subscribe", json={"email": "not-an-email"})
        self.assertEqual(resp.status_code, 400)

    def test_unsubscribe_valid_token(self):
        with patch("subscribers.unsubscribe_by_token", return_value={"email": "a@b.com"}):
            resp = self.client.get("/api/unsubscribe?token=valid-token")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("unsubscribed", resp.text.lower())

    def test_unsubscribe_invalid_token(self):
        with patch("subscribers.unsubscribe_by_token", return_value=None):
            resp = self.client.get("/api/unsubscribe?token=bad")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
