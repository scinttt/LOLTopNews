import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import api  # noqa: E402


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(api.app)

    def setUp(self):
        # 默认不命中缓存
        self.cache_get_patcher = patch("api.get_cached_analysis", return_value=None)
        self.cache_save_patcher = patch("api.save_analysis_to_cache")
        self.cache_get_patcher.start()
        self.cache_save_patcher.start()

    def tearDown(self):
        self.cache_get_patcher.stop()
        self.cache_save_patcher.stop()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_analyze_get_success(self):
        fake_content = "patch notes"
        fake_result = {"version": "14.24", "top_lane_changes": []}

        with (
            patch.object(api.LOLOfficialCrawler, "fetch_patch_notes", new=AsyncMock(return_value=(fake_content, "14.24"))),
            patch.object(api, "run_workflow", new=AsyncMock(return_value=fake_result)) as workflow_mock,
        ):
            response = self.client.get("/api/analyze", params={"version": "14.24"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), fake_result)
        workflow_mock.assert_awaited_once_with(fake_content, version="14.24")

    def test_analyze_post_uses_provided_content(self):
        fake_result = {"version": "14.24", "top_lane_changes": ["x"]}

        with (
            patch.object(api.LOLOfficialCrawler, "fetch_patch_notes", new=AsyncMock()) as fetch_mock,
            patch.object(api, "run_workflow", new=AsyncMock(return_value=fake_result)) as workflow_mock,
        ):
            response = self.client.post(
                "/api/analyze",
                json={"version": "14.24", "raw_content": "provided content"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), fake_result)
        fetch_mock.assert_not_awaited()
        workflow_mock.assert_awaited_once_with("provided content", version="14.24")

    def test_analyze_post_fetches_when_missing_content(self):
        fake_result = {"version": "latest", "top_lane_changes": []}

        with (
            patch.object(api.LOLOfficialCrawler, "fetch_patch_notes", new=AsyncMock(return_value=("fetched content", "latest"))) as fetch_mock,
            patch.object(api, "run_workflow", new=AsyncMock(return_value=fake_result)) as workflow_mock,
        ):
            response = self.client.post("/api/analyze", json={"version": "latest"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), fake_result)
        fetch_mock.assert_awaited_once_with(version="latest")
        workflow_mock.assert_awaited_once_with("fetched content", version="latest")

    def test_analyze_returns_500_on_failure(self):
        with patch.object(api, "run_workflow", new=AsyncMock(side_effect=RuntimeError("boom"))):
            response = self.client.post(
                "/api/analyze",
                json={"version": "14.24", "raw_content": "provided content"},
            )

        self.assertEqual(response.status_code, 500)
        self.assertIn("分析失败: boom", response.json()["detail"])
