
import os
import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def websearch(query: str) -> str:
    """Search the web for League of Legends patch analysis and champion information.

    Use this tool when you need additional information about:
    - Champion abilities and mechanics
    - Item effects and synergies
    - Meta trends and analysis
    - Historical patch impact

    Args:
        query: The search query (e.g., "剑姬 15.24版本 上单 分析")

    Returns:
        Search results as a string
    """
    try:
        from tavily import TavilyClient

        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            return "Error: TAVILY_API_KEY not configured. Cannot perform web search."

        tavily_client = TavilyClient(api_key=tavily_api_key)
        response = tavily_client.search(
            query,
            max_results=3,
            search_depth="basic",
            include_raw_content=False
        )

        # 格式化搜索结果
        results = []
        for result in response.get('results', []):
            results.append(f"标题: {result.get('title', 'N/A')}\n内容: {result.get('content', 'N/A')}\n")

        return "\n---\n".join(results) if results else "No results found."

    except Exception as e:
        logger.error(f"WebSearch 失败: {str(e)}")
        return f"Search error: {str(e)}"
