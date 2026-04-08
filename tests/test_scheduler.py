import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import scheduler  # noqa: E402


class TestCheckForNewVersion(unittest.IsolatedAsyncioTestCase):
    async def test_new_version_triggers_workflow(self):
        fake_index = {"latest": "26.3", "versions": []}
        fake_result = {"version": "26.4", "top_lane_changes": []}

        with (
            patch.object(
                scheduler.LOLOfficialCrawler, "fetch_latest_patch_notes",
                new=AsyncMock(return_value=("raw patch", "26.4")),
            ),
            patch("api.load_versions_index", return_value=fake_index),
            patch("agents.workflow.run_workflow", new=AsyncMock(return_value=fake_result)) as wf_mock,
            patch("api.save_analysis_to_cache") as cache_mock,
        ):
            result = await scheduler.check_for_new_version()

        self.assertEqual(result["status"], "new")
        self.assertEqual(result["version"], "26.4")
        wf_mock.assert_awaited_once_with("raw patch", version="26.4")
        cache_mock.assert_called_once_with("26.4", fake_result)

    async def test_same_version_is_noop(self):
        fake_index = {"latest": "26.3", "versions": []}

        with (
            patch.object(
                scheduler.LOLOfficialCrawler, "fetch_latest_patch_notes",
                new=AsyncMock(return_value=("raw patch", "26.3")),
            ),
            patch("api.load_versions_index", return_value=fake_index),
            patch("agents.workflow.run_workflow", new=AsyncMock()) as wf_mock,
        ):
            result = await scheduler.check_for_new_version()

        self.assertEqual(result["status"], "unchanged")
        wf_mock.assert_not_awaited()

    async def test_crawler_error_returns_error_status(self):
        with patch.object(
            scheduler.LOLOfficialCrawler, "fetch_latest_patch_notes",
            new=AsyncMock(side_effect=RuntimeError("network error")),
        ):
            result = await scheduler.check_for_new_version()

        self.assertEqual(result["status"], "error")
        self.assertIn("network error", result["error"])


class TestSchedulerLifecycle(unittest.TestCase):
    def test_start_and_stop(self):
        with patch("scheduler.AsyncIOScheduler") as MockSched:
            mock_instance = MagicMock()
            MockSched.return_value = mock_instance

            scheduler._scheduler = None
            scheduler.start_scheduler()
            mock_instance.add_job.assert_called_once()
            mock_instance.start.assert_called_once()

            scheduler.stop_scheduler()
            mock_instance.shutdown.assert_called_once()
            self.assertIsNone(scheduler._scheduler)


if __name__ == "__main__":
    unittest.main()
