import argparse
import os
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, patch


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import main as app_main  # noqa: E402


class TestMainHelpers(unittest.TestCase):
    def test_get_change_symbol(self):
        self.assertEqual(app_main.get_change_symbol("buff"), "⬆️")
        self.assertEqual(app_main.get_change_symbol("nerf"), "⬇️")
        self.assertEqual(app_main.get_change_symbol("adjust"), "🔄")

    def test_split_changes_by_type(self):
        changes = [
            {"type": "champion", "champion": "Aatrox"},
            {"type": "item", "item": "Black Cleaver"},
            {"type": "system", "category": "Runes"},
        ]
        champions, items, systems = app_main.split_changes_by_type(changes)

        self.assertEqual(len(champions), 1)
        self.assertEqual(len(items), 1)
        self.assertEqual(len(systems), 1)

    def test_display_result_renders_expected_sections(self):
        output = []

        def emit(line=""):
            output.append(str(line))

        result = {
            "version": "14.24",
            "top_lane_changes": [
                {"type": "champion", "champion": "Fiora", "change_type": "buff", "relevance": "primary"},
                {"type": "item", "item": "Trinity Force", "change": "Attack speed increased"},
                {"type": "system", "category": "Turret", "change": "Plating gold reduced"},
            ],
            "impact_analyses": ["Fiora priority rises"],
            "summary_report": {"tier": "S"},
            "metadata": {
                "extractor_tokens": {
                    "total_tokens": 3000,
                    "prompt_tokens": 1000,
                    "completion_tokens": 500,
                }
            },
        }

        app_main.display_result(result, "14.24", emit=emit)
        text = "\n".join(output)

        self.assertIn("📊 分析结果", text)
        self.assertIn("版本号: 14.24", text)
        self.assertIn("🦸 英雄变更 (1 个):", text)
        self.assertIn("⬆️ Fiora (主流)", text)
        self.assertIn("⚔️  装备变更 (1 个):", text)
        self.assertIn("🎮 系统变更 (1 个):", text)
        self.assertIn("📈 影响分析 (1 个):", text)
        self.assertIn("📝 总结报告:", text)
        self.assertIn("💰 成本统计:", text)


class TestLoadRawContent(unittest.IsolatedAsyncioTestCase):
    async def test_load_raw_content_from_file(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
            f.write("sample patch")
            file_path = f.name

        try:
            args = argparse.Namespace(version="latest", file=file_path)
            content = await app_main.load_raw_content(args, emit=lambda *_: None)
            self.assertEqual(content, "sample patch")
        finally:
            os.remove(file_path)

    async def test_load_raw_content_from_crawler(self):
        args = argparse.Namespace(version="14.24", file=None)

        with patch.object(app_main.LOLOfficialCrawler, "fetch_patch_notes", new=AsyncMock(return_value="fetched")):
            content = await app_main.load_raw_content(args, emit=lambda *_: None)

        self.assertEqual(content, "fetched")


if __name__ == "__main__":
    unittest.main()
