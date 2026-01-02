"""
测试获取最新版本更新链接的功能
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.crawlers.lol_official import LOLOfficialCrawler


async def main():
    """测试爬虫功能"""
    print("=" * 70)
    print("测试: 获取最新版本更新链接")
    print("=" * 70)
    print()

    crawler = LOLOfficialCrawler()

    try:
        # 测试 1: 获取最新版本更新链接
        print("🔍 测试 _fetch_news_list() 方法...")
        latest_url = await crawler._fetch_news_list()
        print(f"✅ 获取最新链接成功:")
        print(f"   URL: {latest_url}")
        print()

        # 测试 2: 爬取该链接的内容
        print("🔍 测试 fetch_latest_patch_notes() 方法...")
        content = await crawler.fetch_latest_patch_notes()
        print(f"✅ 爬取内容成功:")
        print(f"   长度: {len(content)} 字符")
        print(f"   来源: {crawler.last_url}")
        print()
        print(f"   前 200 字符预览:")
        print(f"   {content[:200]}...")
        print()

        print("=" * 70)
        print("✅ 所有测试通过！")
        print("=" * 70)

    except Exception as e:
        print()
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)