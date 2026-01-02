"""
爬虫基类
提供重试机制、异常处理、日志记录等通用功能
"""
import logging
import asyncio
from typing import Optional, Callable, Any
from functools import wraps

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseCrawler:
    """爬虫基类"""

    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        """
        初始化爬虫基类

        Args:
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.last_url: Optional[str] = None  # 记录最后爬取的URL
        logger.info(f"初始化爬虫: 最大重试次数={max_retries}, 重试延迟={retry_delay}秒")

    async def fetch_with_retry(
        self,
        fetch_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        带重试的爬取逻辑

        Args:
            fetch_func: 实际执行爬取的函数
            *args: 传递给fetch_func的位置参数
            **kwargs: 传递给fetch_func的关键字参数

        Returns:
            爬取结果

        Raises:
            Exception: 所有重试失败后抛出最后一次的异常
        """
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"第 {attempt}/{self.max_retries} 次尝试爬取...")

                result = await fetch_func(*args, **kwargs)

                logger.info(f"✅ 爬取成功（第 {attempt} 次尝试）")
                return result

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"❌ 第 {attempt} 次尝试失败: {str(e)}"
                )

                # 如果还有重试次数，等待后重试
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * attempt  # 递增延迟
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"所有重试均失败，放弃爬取")

        # 所有重试都失败，抛出异常
        raise last_exception

    def validate_content(self, content: str, min_length: int = 1000) -> bool:
        """
        验证爬取内容是否有效

        Args:
            content: 爬取的内容
            min_length: 内容最小长度（字节）

        Returns:
            bool: 内容是否有效
        """
        if not content:
            logger.warning("内容为空")
            return False

        if len(content) < min_length:
            logger.warning(f"内容长度不足: {len(content)} < {min_length}")
            return False

        return True

    async def save_to_file(self, content: str, file_path: str) -> None:
        """
        保存内容到文件（用于调试）

        Args:
            content: 要保存的内容
            file_path: 文件路径
        """
        try:
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"✅ 内容已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}")


def retry_on_failure(max_retries: int = 3, delay: float = 2.0):
    """
    装饰器：为函数添加重试机制

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"函数 {func.__name__} 第 {attempt} 次执行失败: {str(e)}")

                    if attempt < max_retries:
                        wait_time = delay * attempt
                        await asyncio.sleep(wait_time)

            raise last_exception

        return wrapper
    return decorator
