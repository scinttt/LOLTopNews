"""
LOL Top Lane Guide - FastAPI REST API
提供版本更新分析的 REST API 接口
"""
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from crawlers.lol_official import LOLOfficialCrawler
from agents.workflow import run_workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 缓存配置
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 创建 FastAPI 应用
app = FastAPI(
    title="LOL Top Lane Guide API",
    description="英雄联盟上单版本更新分析 API",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

class AnalysisRequest(BaseModel):
    """分析请求"""
    version: Optional[str] = "latest"
    raw_content: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "version": "14.24",
                "raw_content": None
            }
        }


# ==================== 缓存助手 ====================

def get_cached_analysis(version: str) -> Optional[Dict[str, Any]]:
    """尝试获取缓存的分析结果"""
    if version == "latest" or version == "unknown":
        return None
        
    cache_file = CACHE_DIR / f"{version}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                logger.info(f"🚀 命中缓存: {version}")
                return json.load(f)
        except Exception as e:
            logger.warning(f"读取缓存失败 {version}: {e}")
    return None

def save_analysis_to_cache(version: str, result: Dict[str, Any]):
    """将分析结果保存到缓存"""
    if version == "unknown":
        return
        
    cache_file = CACHE_DIR / f"{version}.json"
    try:
        # 移除不可序列化的部分（如 LangGraph 的 messages 对象中可能有复杂对象）
        # 这里我们只保存核心字段
        serializable_result = {
            "version": result.get("version"),
            "top_lane_changes": result.get("top_lane_changes"),
            "impact_analyses": result.get("impact_analyses"),
            "summary_report": result.get("summary_report"),
            "metadata": result.get("metadata")
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(serializable_result, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 结果已缓存: {version}")
    except Exception as e:
        logger.error(f"保存缓存失败 {version}: {e}")


# ==================== API 路由 ====================

async def _fetch_raw_content(version: str) -> tuple[str, str]:
    """Fetch patch notes content for a version."""
    logger.info(f"🔍 开始爬取版本: {version}")
    crawler = LOLOfficialCrawler()
    raw_content, real_version = await crawler.fetch_patch_notes(version=version)
    logger.info(f"✅ 爬取成功: {real_version} ({len(raw_content)} 字符)")
    return raw_content, real_version


async def _analyze(raw_content: str, version: str):
    """Run analysis workflow with common logging and caching."""
    # 1. 尝试从缓存获取
    cached_result = get_cached_analysis(version)
    if cached_result:
        return cached_result

    # 2. 执行分析
    logger.info(f"🤖 开始分析工作流 (Version: {version})...")
    result = await run_workflow(raw_content, version=version)
    logger.info("✅ 分析完成")

    # 3. 写入缓存
    save_analysis_to_cache(version, result)
    
    return result

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "LOL Top Lane Guide API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/api/analyze")
async def analyze_version_get(
    version: str = Query(default="latest", description="版本号，如 14.24 或 latest")
):
    """
    分析指定版本的更新公告（GET 请求）

    参数:
        version: 版本号，默认为 latest（最新版本）

    返回:
        包含分析结果的 JSON 对象
    """
    logger.info(f"收到 GET 分析请求: version={version}")

    try:
        raw_content, real_version = await _fetch_raw_content(version)
        return await _analyze(raw_content, real_version)

    except Exception as e:
        logger.error(f"❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.post("/api/analyze")
async def analyze_version_post(request: AnalysisRequest):
    """
    分析指定版本的更新公告（POST 请求）

    请求体:
        {
            "version": "14.24",  // 可选，默认 latest
            "raw_content": "..."  // 可选，提供则不爬取
        }

    返回:
        包含分析结果的 JSON 对象
    """
    logger.info(f"收到 POST 分析请求: version={request.version}, has_content={bool(request.raw_content)}")

    try:
        raw_content = request.raw_content
        version = request.version or "latest"

        # 如果没有提供内容，则爬取
        if not raw_content:
            raw_content, version = await _fetch_raw_content(version)
        else:
            logger.info(f"📄 使用提供的内容: {len(raw_content)} 字符")

        return await _analyze(raw_content, version)

    except Exception as e:
        logger.error(f"❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


# ==================== 运行服务器 ====================

if __name__ == "__main__":
    import uvicorn

    # 开发环境配置
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )
