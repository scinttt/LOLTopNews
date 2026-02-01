"""
LOL Top Lane Guide - 应用入口
分析指定版本的更新公告，生成上单位置影响报告
"""
import asyncio
import argparse
import sys
import os
import logging

from crawlers.lol_official import LOLOfficialCrawler
from agents.workflow import run_workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    raw_content = None
    version = args.version

    if args.file:
        # 从文件读取
        print(f"📄 从文件读取: {args.file}")
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            print(f"✅ 读取成功: {len(raw_content)} 字符\n")
        except Exception as e:
            print(f"❌ 读取文件失败: {str(e)}")
            return
    else:
        # 爬取最新版本
        print(f"🔍 爬取版本: {args.version}")
        try:
            crawler = LOLOfficialCrawler()
            raw_content = await crawler.fetch_patch_notes(version=args.version)
            print(f"✅ 爬取成功: {len(raw_content)} 字符")
            print(f"   来源: {crawler.last_url}\n")
        except Exception as e:
            print(f"❌ 爬取失败: {str(e)}")
            print(f"\n💡 提示: 可以使用 --file 参数指定本地文件")
            print(f"   例如: --file data/sample_patch_14.24.txt")
            return

    # 2. 运行分析工作流
    print("🤖 开始分析...")
    print("-" * 70)

    try:
        result = await run_workflow(raw_content, version=version)

        # 3. 显示结果
        print()
        print("=" * 70)
        print("📊 分析结果")
        print("=" * 70)
        print()
    
        # 版本信息
        print(f"版本号: {result.get('version', version)}")
        print()

        # Extractor 结果
        changes = result.get("top_lane_changes", [])
        print(f"✅ 提取到 {len(changes)} 个上单相关变更")
        print()

        # 按类型分组显示
        champions = [c for c in changes if c["type"] == "champion"]
        items = [c for c in changes if c["type"] == "item"]
        systems = [c for c in changes if c["type"] == "system"]

        if champions:
            print(f"🦸 英雄变更 ({len(champions)} 个):")
            for i, change in enumerate(champions, 1):
                champion = change.get("champion", "Unknown")
                change_type = change.get("change_type", "adjust")
                relevance = change.get("relevance", "primary")

                # 标记主玩/次选
                tag = "主流" if relevance == "primary" else "冷门"

                # 标记 buff/nerf
                if change_type == "buff":
                    symbol = "⬆️"
                elif change_type == "nerf":
                    symbol = "⬇️"
                else:
                    symbol = "🔄"

                print(f"   {i}. {symbol} {champion} ({tag})")
            print()

        if items:
            print(f"⚔️  装备变更 ({len(items)} 个):")
            for i, item in enumerate(items, 1):
                item_name = item.get("item", "Unknown")
                change = item.get("change", "")
                print(f"   {i}. {item_name}")
                if change and len(change) < 50:
                    print(f"      └─ {change}")
            print()

        if systems:
            print(f"🎮 系统变更 ({len(systems)} 个):")
            for i, sys in enumerate(systems, 1):
                category = sys.get("category", "Unknown")
                change = sys.get("change", "")
                print(f"   {i}. {category}")
                if change and len(change) < 50:
                    print(f"      └─ {change}")
            print()

        # Analyzer 结果（如果已实现）
        analyses = result.get("impact_analyses", [])
        if analyses:
            print(f"📈 影响分析 ({len(analyses)} 个):")
            for analysis in analyses[:3]:
                print(f"   - {analysis}")
            print()
        else:
            print("📈 影响分析: 待实现 (Day 4-5)")
            print()

        # Summarizer 结果（如果已实现）
        summary = result.get("summary_report", {})
        if summary and summary:
            print(f"📝 总结报告:")
            print(f"   {summary}")
            print()
        else:
            print("📝 总结报告: 待实现 (Day 8)")
            print()

        # Token 使用统计
        metadata = result.get("metadata", {})
        if "extractor_tokens" in metadata:
            tokens = metadata["extractor_tokens"]
            total = tokens.get("total_tokens", 0)
            cost = (tokens.get("prompt_tokens", 0) / 1_000_000 * 1 +
                   tokens.get("completion_tokens", 0) / 1_000_000 * 2)
            print(f"💰 成本统计:")
            print(f"   Token 使用: {total:,}")
            print(f"   预估成本: ¥{cost:.4f}")
            print()

        print("=" * 70)
        print("✅ 分析完成")
        print("=" * 70)

    except Exception as e:
        print()
        print(f"❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
