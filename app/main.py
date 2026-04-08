"""
LOL Top Lane Guide - 应用入口
分析指定版本的更新公告，生成上单位置影响报告
"""
import argparse
import asyncio
import logging
from typing import Any, Dict, List, Tuple

from agents.workflow import run_workflow
from crawlers.lol_official import LOLOfficialCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_change_symbol(change_type: str) -> str:
    """Map change type to display symbol."""
    if change_type == "buff":
        return "⬆️"
    if change_type == "nerf":
        return "⬇️"
    return "🔄"


def split_changes_by_type(
    changes: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split extracted changes into champion/item/system groups."""
    champions = [c for c in changes if c["type"] == "champion"]
    items = [c for c in changes if c["type"] == "item"]
    systems = [c for c in changes if c["type"] == "system"]
    return champions, items, systems


async def load_raw_content(args, emit=print):
    """Load patch notes from file or crawler."""
    if args.file:
        emit(f"📄 从文件读取: {args.file}")
        with open(args.file, "r", encoding="utf-8") as f:
            raw_content = f.read()
        emit(f"✅ 读取成功: {len(raw_content)} 字符\n")
        return raw_content

    emit(f"🔍 爬取版本: {args.version}")
    crawler = LOLOfficialCrawler()
    raw_content = await crawler.fetch_patch_notes(version=args.version)
    emit(f"✅ 爬取成功: {len(raw_content)} 字符")
    emit(f"   来源: {crawler.last_url}\n")
    return raw_content


def display_result(result: Dict[str, Any], version: str, emit=print):
    """Render analysis result for CLI output."""
    emit()
    emit("=" * 70)
    emit("📊 分析结果")
    emit("=" * 70)
    emit()

    emit(f"版本号: {result.get('version', version)}")
    emit()

    changes = result.get("top_lane_changes", [])
    emit(f"✅ 提取到 {len(changes)} 个上单相关变更")
    emit()

    champions, items, systems = split_changes_by_type(changes)

    if champions:
        emit(f"🦸 英雄变更 ({len(champions)} 个):")
        for i, change in enumerate(champions, 1):
            champion = change.get("champion", "Unknown")
            change_type = change.get("change_type", "adjust")
            relevance = change.get("relevance", "primary")
            tag = "主流" if relevance == "primary" else "冷门"
            symbol = get_change_symbol(change_type)
            emit(f"   {i}. {symbol} {champion} ({tag})")
        emit()

    if items:
        emit(f"⚔️  装备变更 ({len(items)} 个):")
        for i, item in enumerate(items, 1):
            item_name = item.get("item", "Unknown")
            change = item.get("change", "")
            emit(f"   {i}. {item_name}")
            if change and len(change) < 50:
                emit(f"      └─ {change}")
        emit()

    if systems:
        emit(f"🎮 系统变更 ({len(systems)} 个):")
        for i, system in enumerate(systems, 1):
            category = system.get("category", "Unknown")
            change = system.get("change", "")
            emit(f"   {i}. {category}")
            if change and len(change) < 50:
                emit(f"      └─ {change}")
        emit()

    analyses = result.get("impact_analyses", [])
    if analyses:
        emit(f"📈 影响分析 ({len(analyses)} 个):")
        for analysis in analyses[:3]:
            emit(f"   - {analysis}")
        emit()
    else:
        emit("📈 影响分析: 待实现 (Day 4-5)")
        emit()

    summary = result.get("summary_report", {})
    if summary and summary:
        emit("📝 总结报告:")
        emit(f"   {summary}")
        emit()
    else:
        emit("📝 总结报告: 待实现 (Day 8)")
        emit()

    metadata = result.get("metadata", {})
    if "extractor_tokens" in metadata:
        tokens = metadata["extractor_tokens"]
        total = tokens.get("total_tokens", 0)
        cost = (
            tokens.get("prompt_tokens", 0) / 1_000_000 * 1
            + tokens.get("completion_tokens", 0) / 1_000_000 * 2
        )
        emit("💰 成本统计:")
        emit(f"   Token 使用: {total:,}")
        emit(f"   预估成本: ¥{cost:.4f}")
        emit()

    emit("=" * 70)
    emit("✅ 分析完成")
    emit("=" * 70)


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='LOL 上单版本更新分析工具')
    parser.add_argument(
        '--version',
        type=str,
        default='latest',
        help='版本号 (如 14.24) 或 latest 表示最新版本'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='从文件读取公告内容'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("LOL Top Lane Guide - 上单版本更新分析")
    print("=" * 70)
    print()

    # 1. 获取公告内容
    version = args.version

    try:
        raw_content = await load_raw_content(args)
    except Exception as e:
        action = "读取文件" if args.file else "爬取"
        print(f"❌ {action}失败: {str(e)}")
        if not args.file:
            print("\n💡 提示: 可以使用 --file 参数指定本地文件")
            print("   例如: --file data/sample_patch_14.24.txt")
        return

    # 2. 运行分析工作流
    print("🤖 开始分析...")
    print("-" * 70)

    try:
        result = await run_workflow(raw_content, version=version)
        display_result(result, version)

    except Exception as e:
        print()
        print(f"❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
