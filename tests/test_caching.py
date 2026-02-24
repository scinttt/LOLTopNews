import os
import sys
import json
import unittest
from unittest.mock import AsyncMock, patch
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import api

class TestCaching(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)
        self.test_version = "99.99_test"
        self.cache_file = Path("data/cache") / f"{self.test_version}.json"
        # 确保开始前没有缓存
        if self.cache_file.exists():
            self.cache_file.unlink()

    def tearDown(self):
        # 清理测试产生的缓存
        if self.cache_file.exists():
            self.cache_file.unlink()

    def test_cache_creation_and_hit(self):
        fake_content = "patch notes content"
        fake_result = {
            "version": self.test_version,
            "top_lane_changes": [{"champion": "Garen", "change": "buff"}],
            "impact_analyses": "Big buff",
            "summary_report": "Summary",
            "metadata": {}
        }

        # 1. 模拟第一次调用：不命中缓存，执行工作流
        with (
            patch.object(api.LOLOfficialCrawler, "fetch_patch_notes", new=AsyncMock(return_value=(fake_content, self.test_version))),
            patch.object(api, "run_workflow", new=AsyncMock(return_value=fake_result)) as workflow_mock,
        ):
            response = self.client.get("/api/analyze", params={"version": self.test_version})
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["version"], self.test_version)
            self.assertTrue(self.cache_file.exists(), "Cache file should be created")
            workflow_mock.assert_awaited_once()

        # 2. 模拟第二次调用：命中缓存，不应再次执行工作流
        with (
            patch.object(api.LOLOfficialCrawler, "fetch_patch_notes", new=AsyncMock(return_value=(fake_content, self.test_version))),
            patch.object(api, "run_workflow", new=AsyncMock()) as workflow_mock_hit,
        ):
            response = self.client.get("/api/analyze", params={"version": self.test_version})
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["version"], self.test_version)
            workflow_mock_hit.assert_not_awaited()
            print(f"✅ 成功验证缓存命中: {self.test_version}")

if __name__ == "__main__":
    unittest.main()
