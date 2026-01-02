"""
简化版爬虫测试
直接测试已知的公告URL
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.crawlers.lol_official import LOLOfficialCrawler


async def test_direct_url():
    """直接测试一个已知的公告URL"""
    print("=" * 60)
    print("测试: 爬取已知公告URL")
    print("=" * 60)

    # 使用一个真实的公告ID进行测试
    test_news_id = "16095"  # 这是一个示例ID，可能需要更新

    try:
        crawler = LOLOfficialCrawler()
        content = await crawler.fetch_patch_notes_by_id(test_news_id)

        print(f"\n✅ 成功爬取公告！")
        print(f"URL: {crawler.last_url}")
        print(f"内容长度: {len(content)} 字符")
        print(f"\n内容预览（前1000字符）:")
        print("-" * 60)
        print(content[:1000])
        print("-" * 60)

        # 保存到文件
        filename = f"data/raw_patches/test_{test_news_id}.txt"
        await crawler.save_to_file(content, filename)
        print(f"\n✅ 内容已保存到: {filename}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_news_list():
    """测试获取新闻列表"""
    print("\n" + "=" * 60)
    print("测试: 获取新闻列表")
    print("=" * 60)

    try:
        crawler = LOLOfficialCrawler()
        news_list = await crawler._fetch_news_list()

        print(f"\n✅ 成功获取新闻列表！")
        print(f"新闻数量: {len(news_list)}")

        if news_list:
            print(f"\n前10条新闻:")
            for i, news in enumerate(news_list[:10], 1):
                print(f"{i}. {news['title']}")
                print(f"   ID: {news['id']}")
                print()

            # 尝试爬取第一条新闻
            print("=" * 60)
            print("尝试爬取第一条新闻...")
            print("=" * 60)

            first_news = news_list[0]
            print(f"标题: {first_news['title']}")
            print(f"ID: {first_news['id']}")

            content = await crawler.fetch_patch_notes_by_id(first_news['id'])
            print(f"\n✅ 成功爬取！")
            print(f"内容长度: {len(content)} 字符")
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
    """运行测试"""
    print("\n" + "=" * 60)
    print("简化版爬虫测试")
    print("=" * 60 + "\n")

    # 测试1: 直接URL
    result1 = await test_direct_url()

    # 测试2: 新闻列表
    result2 = await test_news_list()

    # 汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"直接URL测试: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"新闻列表测试: {'✅ 通过' if result2 else '❌ 失败'}")

    if result1 or result2:
        print("\n✅ 爬虫基本功能正常！")
    else:
        print("\n❌ 爬虫测试失败，需要调整URL或解析逻辑")

    print()


if __name__ == "__main__":
    asyncio.run(main())
