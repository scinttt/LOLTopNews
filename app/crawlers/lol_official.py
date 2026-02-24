import re
import logging
import aiohttp
from bs4 import BeautifulSoup
from .base import BaseCrawler

logger = logging.getLogger(__name__)


class LOLOfficialCrawler(BaseCrawler):
    """英雄联盟官网爬虫"""

    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        """初始化爬虫"""
        super().__init__(max_retries, retry_delay)

        # LOL官网的新闻列表页
        self.news_list_url = "https://lol.qq.com/gicp/news/423/2/1334/1.html"

        # 已知的最新版本更新公告URL（作为后备）
        self.known_patch_urls = [
            "https://lol.qq.com/gicp/news/410/37072785.html",  # 示例URL
        ]

        # 请求头配置（模拟浏览器）
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        logger.info(f"LOL官网爬虫已初始化")

    async def fetch_patch_notes(self, version: str = "latest") -> tuple[str, str]:
        """
        爬取指定版本的更新公告

        Args:
            version: 版本号（如 "14.24"、"26.3"）或 "latest" 表示最新版本

        Returns:
            tuple[str, str]: (更新公告的文本内容, 实际探测到的版本号)

        Raises:
            ValueError: 指定版本未找到时抛出
            Exception: 爬取失败时抛出
        """
        if version == "latest":
            return await self.fetch_latest_patch_notes()

        logger.info(f"开始搜索版本 {version} 的更新公告...")
        target_url = await self._search_version_in_news_list(version)
        content = await self._fetch_url_content(target_url)
        return content, version.lstrip("vV")

    async def fetch_latest_patch_notes(self) -> tuple[str, str]:
        """
        爬取最新版本的更新公告

        Returns:
            tuple[str, str]: (更新公告的文本内容, 实际探测到的版本号)

        Raises:
            Exception: 爬取失败时抛出
        """
        logger.info("开始爬取最新版本更新公告...")

        # 1. 获取最新版本更新的URL和版本号
        latest_url, version = await self._fetch_news_list()

        # 2. 爬取该URL的内容
        content = await self._fetch_url_content(latest_url)

        return content, version

    async def _search_version_in_news_list(
        self, version: str, max_pages: int = 10
    ) -> str:
        """
        Paginate through the news list to find the article URL for the given version.

        Args:
            version: Version string to search for, e.g. "26.3" or "15.24"
            max_pages: Maximum pages to scan before giving up

        Returns:
            str: Full URL of the matching patch notes article

        Raises:
            ValueError: If the version is not found within max_pages
        """
        # Normalise version: accept both "14.24" and "v14.24" inputs
        normalised_version = version.lstrip("vV")

        # Build a regex that matches the version number at the start of the title,
        # e.g. "26.3版本公告" or "15.24版本公告"
        version_title_pattern = re.compile(
            rf"^{re.escape(normalised_version)}\s*版本公告"
        )

        logger.info(
            f"在新闻列表中搜索版本 {normalised_version}，最多扫描 {max_pages} 页..."
        )

        async with aiohttp.ClientSession(headers=self.headers) as session:
            for page_number in range(1, max_pages + 1):
                page_url = f"https://lol.qq.com/gicp/news/423/2/1334/{page_number}.html"
                logger.info(f"扫描第 {page_number} 页: {page_url}")

                try:
                    async with session.get(
                        page_url, timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 404:
                            logger.warning(f"第 {page_number} 页不存在，停止翻页")
                            break
                        response.raise_for_status()
                        html = await response.text(encoding="gb2312", errors="ignore")
                except Exception as fetch_error:
                    logger.warning(f"第 {page_number} 页请求失败: {fetch_error}")
                    break

                try:
                    soup = BeautifulSoup(html, "lxml")
                except Exception:
                    soup = BeautifulSoup(html, "html.parser")

                candidate_links = soup.find_all(
                    "a", href=re.compile(r"/gicp/news/410/\d+\.html")
                )

                for link in candidate_links:
                    title = link.get_text(strip=True)
                    if version_title_pattern.match(title):
                        href = link.get("href", "")
                        matched_url = f"https://lol.qq.com{href}"
                        logger.info(
                            f"✅ 找到版本 {normalised_version} 更新公告: {title} -> {matched_url}"
                        )
                        return matched_url

        raise ValueError(
            f"未在新闻列表前 {max_pages} 页中找到版本 {normalised_version} 的更新公告，"
            f"请确认版本号格式（如 '26.3'、'15.24'）是否正确"
        )

    async def _fetch_news_list(self) -> tuple[str, str]:
        """
        爬取新闻列表页，返回最新的版本更新新闻链接和版本号

        Returns:
            tuple[str, str]: (最新版本更新新闻的完整URL链接, 版本号)
        """

        logger.info(f"爬取新闻列表页: {self.news_list_url}")

        async def _fetch():
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(
                    self.news_list_url, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    # LOL官网使用GB2312编码
                    html = await response.text(encoding="gb2312", errors="ignore")

                    # 解析HTML（lxml 优先，不可用时退回 html.parser）
                    try:
                        soup = BeautifulSoup(html, "lxml")
                    except Exception:
                        soup = BeautifulSoup(html, "html.parser")

                    # 尝试多种可能的URL模式
                    # 模式1: /gicp/news/410/数字.html (最新格式，如截图所示)
                    links = soup.find_all(
                        "a", href=re.compile(r"/gicp/news/410/\d+\.html")
                    )

                    # 如果找到链接，返回第一个（最新的）
                    if links:
                        first_link = links[0]
                        href = first_link.get("href", "")
                        title = first_link.get_text(strip=True)

                        # 从标题提取版本号 (如 "14.24版本公告" -> "14.24")
                        version_match = re.search(r"(\d+\.\d+)", title)
                        detected_version = version_match.group(1) if version_match else "unknown"

                        # 构建完整URL
                        latest_url = f"https://lol.qq.com/{href}"

                        logger.info(f"✅ 找到最新版本更新: {title} (Version: {detected_version})")
                        return latest_url, detected_version

                    # 如果没有找到任何链接，使用known_patch_urls作为后备
                    logger.warning("HTML解析未找到新闻链接，使用已知URL作为后备")
                    if self.known_patch_urls:
                        fallback_url = self.known_patch_urls[0]
                        logger.info(f"使用后备URL: {fallback_url}")
                        return fallback_url, "unknown"
                    else:
                        raise ValueError("未找到版本更新链接，且没有配置后备URL")

        return await self.fetch_with_retry(_fetch)

    async def _fetch_url_content(self, url: str) -> str:
        """
        爬取指定URL的页面内容并提取文本

        Args:
            url: 页面URL

        Returns:
            str: 页面文本内容

        Raises:
            Exception: 爬取失败时抛出
        """
        logger.info(f"爬取URL内容: {url}")
        self.last_url = url

        async def _fetch():
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    # LOL官网使用GB2312编码
                    html = await response.text(encoding="gb2312", errors="ignore")

                    # 解析HTML，提取主要内容（lxml 优先，不可用时退回 html.parser）
                    try:
                        soup = BeautifulSoup(html, "lxml")
                    except Exception:
                        soup = BeautifulSoup(html, "html.parser")

                    content_div = soup.find("div", class_="article")

                    if content_div:
                        text = content_div.get_text(separator="\n", strip=True)
                    else:
                        # 如果找不到特定的内容区域，使用整个body
                        logger.warning("未找到特定内容区域，使用全部body内容")
                        body = soup.find("body")
                        text = (
                            body.get_text(separator="\n", strip=True) if body else html
                        )

                    # 验证内容
                    if not self.validate_content(text, min_length=500):
                        raise ValueError(f"爬取的内容无效或过短: {len(text)} 字符")

                    logger.info(f"✅ 成功爬取内容: {len(text)} 字符")
                    return text

        return await self.fetch_with_retry(_fetch)
