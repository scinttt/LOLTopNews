import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from crawlers.base import BaseCrawler  # noqa: E402
from crawlers.lol_official import LOLOfficialCrawler  # noqa: E402


class TestBaseCrawler(unittest.TestCase):
    def test_validate_content_rejects_empty(self):
        crawler = BaseCrawler()
        self.assertFalse(crawler.validate_content(""))
        self.assertFalse(crawler.validate_content(None))

    def test_validate_content_rejects_short(self):
        crawler = BaseCrawler()
        self.assertFalse(crawler.validate_content("short", min_length=100))

    def test_validate_content_accepts_valid(self):
        crawler = BaseCrawler()
        self.assertTrue(crawler.validate_content("x" * 1000))


class TestBaseCrawlerRetry(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_with_retry_succeeds_first_try(self):
        crawler = BaseCrawler(max_retries=3, retry_delay=0.01)
        func = AsyncMock(return_value="result")
        result = await crawler.fetch_with_retry(func)
        self.assertEqual(result, "result")
        func.assert_awaited_once()

    async def test_fetch_with_retry_succeeds_after_failures(self):
        crawler = BaseCrawler(max_retries=3, retry_delay=0.01)
        func = AsyncMock(side_effect=[RuntimeError("fail"), RuntimeError("fail"), "ok"])
        result = await crawler.fetch_with_retry(func)
        self.assertEqual(result, "ok")
        self.assertEqual(func.await_count, 3)

    async def test_fetch_with_retry_raises_after_max_retries(self):
        crawler = BaseCrawler(max_retries=2, retry_delay=0.01)
        func = AsyncMock(side_effect=RuntimeError("always fails"))
        with self.assertRaises(RuntimeError):
            await crawler.fetch_with_retry(func)
        self.assertEqual(func.await_count, 2)


class TestLOLOfficialCrawlerInit(unittest.TestCase):
    def test_default_init(self):
        crawler = LOLOfficialCrawler()
        self.assertEqual(crawler.max_retries, 3)
        self.assertIn("User-Agent", crawler.headers)
        self.assertIsNotNone(crawler.news_list_url)


class TestLOLOfficialCrawlerFetch(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_patch_notes_latest_delegates(self):
        crawler = LOLOfficialCrawler()
        with patch.object(
            crawler, "fetch_latest_patch_notes",
            new=AsyncMock(return_value=("content", "26.3")),
        ) as mock:
            result = await crawler.fetch_patch_notes(version="latest")
        self.assertEqual(result, ("content", "26.3"))
        mock.assert_awaited_once()

    async def test_fetch_patch_notes_specific_version(self):
        crawler = LOLOfficialCrawler()
        with (
            patch.object(
                crawler, "_search_version_in_news_list",
                new=AsyncMock(return_value="https://example.com/patch"),
            ),
            patch.object(
                crawler, "_fetch_url_content",
                new=AsyncMock(return_value="patch content"),
            ),
        ):
            content, version = await crawler.fetch_patch_notes(version="26.3")
        self.assertEqual(content, "patch content")
        self.assertEqual(version, "26.3")


if __name__ == "__main__":
    unittest.main()
