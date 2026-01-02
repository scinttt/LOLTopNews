"""
测试爬虫功能
验证能否成功爬取英雄联盟官网的更新公告
"""
import asyncio
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.crawlers.lol_official import LOLOfficialCrawler


async def test_fetch_latest():
    """测试爬取最新版本公告"""
    print("=" * 60)
    print("测试 1: 爬取最新版本更新公告")
    print("=" * 60)

    try:
        crawler = LOLOfficialCrawler(max_retries=3, retry_delay=2.0)
        content = await crawler.fetch_patch_notes(version="latest")

        print(f"\n✅ 成功爬取公告！")
        print(f"内容长度: {len(content)} 字符")
        print(f"来源URL: {crawler.last_url}")
        print(f"\n内容预览（前500字符）:")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)

        # 可选：保存到文件用于调试
        save_option = input("\n是否保存完整内容到文件？(y/n): ")
        if save_option.lower() == 'y':
            filename = f"data/raw_patches/latest_{asyncio.get_event_loop().time():.0f}.txt"
            await crawler.save_to_file(content, filename)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_fetch_news_list():
    """测试获取新闻列表"""
    print("\n" + "=" * 60)
    print("测试 2: 获取新闻列表")
    print("=" * 60)

    try:
        crawler = LOLOfficialCrawler()
        news_list = await crawler._fetch_news_list()

        print(f"\n✅ 成功获取新闻列表！")
        print(f"新闻数量: {len(news_list)}")

        if news_list:
            print(f"\n前5条新闻:")
            for i, news in enumerate(news_list[:5], 1):
                print(f"{i}. {news['title']}")
                print(f"   ID: {news['id']}")
                print(f"   URL: {news.get('url', 'N/A')}")
                print()

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_fetch_specific_version():
    """测试爬取特定版本（如果用户提供）"""
    print("\n" + "=" * 60)
    print("测试 3: 爬取特定版本（可选）")
    print("=" * 60)

    version = input("\n请输入要爬取的版本号（如 14.24，或按Enter跳过）: ").strip()

    if not version:
        print("跳过此测试")
        return None

    try:
        crawler = LOLOfficialCrawler()
        content = await crawler.fetch_patch_notes(version=version)

        print(f"\n✅ 成功爬取版本 {version} 的公告！")
        print(f"内容长度: {len(content)} 字符")
        print(f"来源URL: {crawler.last_url}")
        print(f"\n内容预览（前500字符）:")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)

        # 可选：保存到文件
        save_option = input("\n是否保存完整内容到文件？(y/n): ")
        if save_option.lower() == 'y':
            filename = f"data/raw_patches/{version}.txt"
            await crawler.save_to_file(content, filename)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_fetch_by_id():
    """测试根据新闻ID爬取"""
    print("\n" + "=" * 60)
    print("测试 4: 根据新闻ID爬取（可选）")
    print("=" * 60)

    news_id = input("\n请输入新闻ID（或按Enter跳过）: ").strip()

    if not news_id:
        print("跳过此测试")
        return None

    try:
        crawler = LOLOfficialCrawler()
        content = await crawler.fetch_patch_notes_by_id(news_id)

        print(f"\n✅ 成功爬取新闻 {news_id}！")
        print(f"内容长度: {len(content)} 字符")
        print(f"来源URL: {crawler.last_url}")
        print(f"\n内容预览（前500字符）:")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("英雄联盟官网爬虫测试套件")
    print("=" * 60 + "\n")

    # 运行测试
    results = []

    # 测试1: 获取新闻列表
    result1 = await test_fetch_news_list()
    results.append(("获取新闻列表", result1))

    # 测试2: 爬取最新版本
    result2 = await test_fetch_latest()
    results.append(("爬取最新版本", result2))

    # 测试3: 爬取特定版本（可选）
    result3 = await test_fetch_specific_version()
    if result3 is not None:
        results.append(("爬取特定版本", result3))

    # 测试4: 根据ID爬取（可选）
    result4 = await test_fetch_by_id()
    if result4 is not None:
        results.append(("根据ID爬取", result4))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    success_count = sum(1 for _, r in results if r)
    total_count = len(results)
    print(f"\n总计: {success_count}/{total_count} 通过")

    if success_count == total_count:
        print("\n✅ 所有测试通过！爬虫功能正常")
    else:
        print("\n⚠️ 部分测试失败，请检查日志")

    print("\n提示：爬虫可能会因为网站结构变化而失败，需要根据实际情况调整解析逻辑")
    print()


if __name__ == "__main__":
    asyncio.run(main())
