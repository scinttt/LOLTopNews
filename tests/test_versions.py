import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import api  # noqa: E402


class TestVersionsIndex(unittest.TestCase):
    """Test the version index management logic."""

    def setUp(self):
        self.original_index = api.VERSIONS_INDEX
        self.original_max = api.MAX_CACHED_VERSIONS
        # Use a temp path for versions.json
        self.test_dir = Path("data/cache/_test_versions")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        api.VERSIONS_INDEX = self.test_dir / "versions.json"
        api.CACHE_DIR = self.test_dir
        api.MAX_CACHED_VERSIONS = 3

    def tearDown(self):
        # Cleanup
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        api.VERSIONS_INDEX = self.original_index
        api.CACHE_DIR = Path("data/cache")
        api.MAX_CACHED_VERSIONS = self.original_max

    def test_load_empty_index(self):
        index = api.load_versions_index()
        self.assertIsNone(index["latest"])
        self.assertEqual(index["versions"], [])

    def test_update_versions_index_adds_version(self):
        api.update_versions_index("26.3")
        index = api.load_versions_index()
        self.assertEqual(index["latest"], "26.3")
        self.assertEqual(len(index["versions"]), 1)
        self.assertEqual(index["versions"][0]["version"], "26.3")

    def test_update_versions_index_latest_is_newest(self):
        api.update_versions_index("26.1")
        api.update_versions_index("26.2")
        api.update_versions_index("26.3")
        index = api.load_versions_index()
        self.assertEqual(index["latest"], "26.3")
        self.assertEqual(index["versions"][0]["version"], "26.3")
        self.assertEqual(index["versions"][2]["version"], "26.1")

    def test_update_versions_index_evicts_oldest(self):
        # MAX_CACHED_VERSIONS = 3
        for v in ["26.1", "26.2", "26.3"]:
            # Create cache file so eviction can delete it
            (self.test_dir / f"{v}.json").write_text("{}")
            api.update_versions_index(v)

        # Now add a 4th — should evict 26.1
        (self.test_dir / "26.4.json").write_text("{}")
        api.update_versions_index("26.4")

        index = api.load_versions_index()
        self.assertEqual(len(index["versions"]), 3)
        self.assertEqual(index["latest"], "26.4")
        versions = [v["version"] for v in index["versions"]]
        self.assertNotIn("26.1", versions)
        self.assertFalse((self.test_dir / "26.1.json").exists())

    def test_update_versions_index_deduplicates_reanalysis(self):
        api.update_versions_index("26.3")
        api.update_versions_index("26.3")
        index = api.load_versions_index()
        self.assertEqual(len(index["versions"]), 1)


class TestVersionsEndpoints(unittest.TestCase):
    """Test /api/versions and /api/versions/{version} endpoints."""

    def setUp(self):
        self.client = TestClient(api.app)

    def test_list_versions_empty(self):
        with patch.object(api, "load_versions_index", return_value={"latest": None, "versions": []}):
            resp = self.client.get("/api/versions")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.json()["latest"])

    def test_list_versions_with_data(self):
        fake_index = {
            "latest": "26.3",
            "versions": [{"version": "26.3", "analyzed_at": "2026-04-06T00:00:00Z"}],
        }
        with patch.object(api, "load_versions_index", return_value=fake_index):
            resp = self.client.get("/api/versions")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["latest"], "26.3")

    def test_get_version_cache_hit(self):
        fake_data = {"version": "26.3", "top_lane_changes": []}
        with patch.object(api, "get_cached_analysis", return_value=fake_data):
            resp = self.client.get("/api/versions/26.3")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["version"], "26.3")

    def test_get_version_not_found(self):
        with patch.object(api, "get_cached_analysis", return_value=None):
            resp = self.client.get("/api/versions/99.99")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
