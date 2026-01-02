"""
测试真实的LOL更新公告URL
https://lol.qq.com/gicp/news/410/37072785.html
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aiohttp
from bs4 import BeautifulSoup


async def test_real_url():
    """测试真实的LOL公告URL"""
    url = "https://lol.qq.com/gicp/news/410/37072785.html"

    print("=" * 70)
    print("测试真实LOL公告URL")
    print("=" * 70)
    print(f"URL: {url}\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"状态码: {response.status}")

                if response.status == 200:
                    # 尝试不同的编码
                    try:
                        html = await response.text(encoding='utf-8')
                    except:
                        html = await response.text(encoding='gb2312', errors='ignore')

                    print(f"✅ 成功获取页面内容")
                    print(f"内容长度: {len(html)} 字符\n")

                    # 解析HTML
                    soup = BeautifulSoup(html, 'lxml')

                    # 查找主要内容区域
                    # 尝试多种可能的内容区域选择器
                    selectors = [
                        ('div', {'class': 'content'}),
                        ('div', {'class': 'article-content'}),
                        ('div', {'id': 'content'}),
                        ('div', {'class': 'main-content'}),
                        ('article', {}),
                        ('main', {}),
                    ]

                    content_area = None
                    for tag, attrs in selectors:
                        content_area = soup.find(tag, attrs)
                        if content_area:
                            print(f"✅ 找到内容区域: <{tag} {attrs}>")
                            break

                    if not content_area:
                        # 如果找不到特定区域，使用body
                        content_area = soup.find('body')
                        print(f"⚠️ 使用整个body作为内容区域")

                    if content_area:
                        text_content = content_area.get_text(separator='\n', strip=True)
                        print(f"提取的文本长度: {len(text_content)} 字符")
                        print(f"\n内容预览（前2000字符）:")
                        print("-" * 70)
                        print(text_content[:2000])
                        print("-" * 70)

                        # 保存到文件
                        save_file = "data/raw_patches/latest_real.txt"
                        os.makedirs(os.path.dirname(save_file), exist_ok=True)
                        with open(save_file, 'w', encoding='utf-8') as f:
                            f.write(text_content)

                        print(f"\n✅ 内容已保存到: {save_file}")

                        # 检查是否包含版本更新关键词
                        keywords = ['版本', '更新', '英雄', '装备', '调整', 'buff', 'nerf']
                        found_keywords = [kw for kw in keywords if kw in text_content]
                        print(f"\n关键词检查: 找到 {len(found_keywords)}/{len(keywords)} 个关键词")
                        print(f"找到的关键词: {', '.join(found_keywords)}")

                        # 分析页面结构
                        print(f"\n页面结构分析:")
                        print(f"   标题: {soup.title.string if soup.title else 'N/A'}")

                        # 查找所有可能的内容div
                        all_divs = soup.find_all('div', class_=True)
                        print(f"   带class的div数量: {len(all_divs)}")
                        if all_divs:
                            print(f"   前10个div的class:")
                            for i, div in enumerate(all_divs[:10], 1):
                                classes = ' '.join(div.get('class', []))
                                print(f"      {i}. {classes}")

                        return True
                    else:
                        print("❌ 未找到内容区域")
                        return False

                else:
                    print(f"❌ HTTP 错误: {response.status}")
                    return False

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_crawler():
    """使用爬虫类测试"""
    print("\n" + "=" * 70)
    print("使用爬虫类测试")
    print("=" * 70 + "\n")

    from app.crawlers.base import BaseCrawler

    crawler = BaseCrawler()

    url = "https://lol.qq.com/gicp/news/410/37072785.html"

    async def _fetch_url():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response.raise_for_status()

                try:
                    html = await response.text(encoding='utf-8')
                except:
                    html = await response.text(encoding='gb2312', errors='ignore')

                soup = BeautifulSoup(html, 'lxml')
                content_area = soup.find('div', class_='content') or soup.find('body')

                if content_area:
                    return content_area.get_text(separator='\n', strip=True)
                else:
                    return soup.get_text(separator='\n', strip=True)

    try:
        content = await crawler.fetch_with_retry(_fetch_url)

        print(f"✅ 成功使用爬虫类获取内容")
        print(f"内容长度: {len(content)} 字符")

        # 验证内容
        if crawler.validate_content(content, min_length=1000):
            print(f"✅ 内容验证通过 (长度 >= 1000)")
        else:
            print(f"⚠️ 内容可能太短")

        # 保存
        await crawler.save_to_file(content, "data/raw_patches/latest_with_crawler.txt")

        return True

    except Exception as e:
        print(f"❌ 爬虫测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行测试"""
    print("\n" + "=" * 70)
    print("LOL真实公告URL测试")
    print("=" * 70 + "\n")

    result1 = await test_real_url()
    result2 = await test_with_crawler()

    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    print(f"直接请求测试: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"爬虫类测试: {'✅ 通过' if result2 else '❌ 失败'}")

    if result1 and result2:
        print("\n✅ 所有测试通过！真实URL可以正常爬取。")
    else:
        print("\n⚠️ 部分测试失败，请检查日志")

    print()


if __name__ == "__main__":
    asyncio.run(main())
