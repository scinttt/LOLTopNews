import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import subscribers  # noqa: E402


class TestSubscribers(unittest.TestCase):
    def setUp(self):
        self.original_file = subscribers.SUBSCRIBERS_FILE
        self.test_file = Path("data/_test_subscribers.json")
        subscribers.SUBSCRIBERS_FILE = self.test_file
        if self.test_file.exists():
            self.test_file.unlink()

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()
        subscribers.SUBSCRIBERS_FILE = self.original_file

    def test_upsert_creates_new_subscriber(self):
        sub, action = subscribers.upsert_active("test@example.com")
        self.assertEqual(action, "created")
        self.assertEqual(sub["email"], "test@example.com")
        self.assertEqual(sub["status"], "active")
        self.assertIn("unsubscribe_token", sub)

    def test_upsert_already_active_is_idempotent(self):
        subscribers.upsert_active("test@example.com")
        sub, action = subscribers.upsert_active("test@example.com")
        self.assertEqual(action, "already_active")

    def test_unsubscribe_by_token(self):
        sub, _ = subscribers.upsert_active("test@example.com")
        token = sub["unsubscribe_token"]

        result = subscribers.unsubscribe_by_token(token)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "unsubscribed")

    def test_unsubscribe_invalid_token_returns_none(self):
        result = subscribers.unsubscribe_by_token("invalid-token")
        self.assertIsNone(result)

    def test_reactivate_after_unsubscribe(self):
        sub, _ = subscribers.upsert_active("test@example.com")
        subscribers.unsubscribe_by_token(sub["unsubscribe_token"])

        sub2, action = subscribers.upsert_active("test@example.com")
        self.assertEqual(action, "reactivated")
        self.assertEqual(sub2["status"], "active")

    def test_list_active_filters_unsubscribed(self):
        subscribers.upsert_active("active@example.com")
        sub2, _ = subscribers.upsert_active("gone@example.com")
        subscribers.unsubscribe_by_token(sub2["unsubscribe_token"])

        active = subscribers.list_active()
        emails = [s["email"] for s in active]
        self.assertIn("active@example.com", emails)
        self.assertNotIn("gone@example.com", emails)


if __name__ == "__main__":
    unittest.main()
