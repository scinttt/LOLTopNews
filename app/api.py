"""
LOL Top Lane Guide - FastAPI REST API
提供版本更新分析的 REST API 接口
"""
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from agents.workflow import run_workflow
from crawlers.lol_official import LOLOfficialCrawler
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 缓存配置
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
VERSIONS_INDEX = CACHE_DIR / "versions.json"
MAX_CACHED_VERSIONS = 5

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from scheduler import start_scheduler, stop_scheduler
    start_scheduler()
    yield
    stop_scheduler()


# 创建 FastAPI 应用
app = FastAPI(
    title="LOL Top Lane Guide API",
    description="英雄联盟上单版本更新分析 API",
    version="1.0.0",
    lifespan=lifespan,
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


class SubscribeRequest(BaseModel):
    email: str


# ==================== Version Index ====================

def load_versions_index() -> Dict[str, Any]:
    """Load the version index file."""
    if VERSIONS_INDEX.exists():
        try:
            with open(VERSIONS_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"读取版本索引失败: {e}")
    return {"latest": None, "versions": []}


def save_versions_index(index: Dict[str, Any]) -> None:
    """Write the version index file."""
    with open(VERSIONS_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def update_versions_index(version: str) -> None:
    """Add a version to the index, evict oldest if over MAX_CACHED_VERSIONS."""
    index = load_versions_index()
    versions = index.get("versions", [])

    # Remove existing entry for this version (if re-analyzed)
    versions = [v for v in versions if v["version"] != version]

    # Prepend new version
    versions.insert(0, {
        "version": version,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    })

    # Evict oldest versions beyond limit
    while len(versions) > MAX_CACHED_VERSIONS:
        evicted = versions.pop()
        evicted_file = CACHE_DIR / f"{evicted['version']}.json"
        if evicted_file.exists():
            evicted_file.unlink()
            logger.info(f"🗑️ 淘汰旧版本缓存: {evicted['version']}")

    index["latest"] = versions[0]["version"]
    index["versions"] = versions
    save_versions_index(index)
    logger.info(f"📋 版本索引已更新: latest={index['latest']}, total={len(versions)}")


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
    """Save analysis result to cache and update version index."""
    if version == "unknown":
        return

    cache_file = CACHE_DIR / f"{version}.json"
    try:
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

        # Update version index
        update_versions_index(version)
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


# ==================== Version Endpoints ====================

@app.get("/api/versions")
async def list_versions():
    """Return the version index: latest version + history list."""
    return load_versions_index()


@app.get("/api/versions/{version}")
async def get_version(version: str):
    """Return cached analysis for a specific version."""
    cached = get_cached_analysis(version)
    if cached is None:
        raise HTTPException(status_code=404, detail=f"版本 {version} 未找到缓存")
    return cached


# ==================== Subscription Endpoints ====================

@app.post("/api/subscribe")
async def subscribe(request: SubscribeRequest):
    """Subscribe an email to patch notifications."""
    import re

    from subscribers import upsert_active

    email = request.email.strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    subscriber, action = upsert_active(email)
    return {"ok": True, "email": subscriber["email"], "status": subscriber["status"], "action": action}


@app.get("/api/unsubscribe")
async def unsubscribe(token: str = Query(..., description="Unsubscribe token")):
    """One-click unsubscribe via token."""
    from fastapi.responses import HTMLResponse
    from subscribers import unsubscribe_by_token

    result = unsubscribe_by_token(token)
    if result is None:
        return HTMLResponse(
            "<html><body><h1>Invalid unsubscribe link.</h1></body></html>",
            status_code=404,
        )
    return HTMLResponse(
        "<html><body><h1>You have been unsubscribed.</h1>"
        "<p>You will not receive future patch analysis emails.</p></body></html>"
    )


# ==================== Backfill ====================

_backfill_running = False


@app.post("/api/backfill")
async def backfill_recent_versions(background_tasks: BackgroundTasks):
    """Trigger background analysis of recent versions not yet cached."""
    global _backfill_running
    if _backfill_running:
        return {"ok": True, "message": "Backfill already running"}

    index = load_versions_index()
    cached_versions = {v["version"] for v in index.get("versions", [])}

    background_tasks.add_task(_run_backfill, cached_versions)
    return {"ok": True, "message": "Backfill started"}


async def _run_backfill(cached_versions: set[str]) -> None:
    global _backfill_running
    _backfill_running = True
    try:
        crawler = LOLOfficialCrawler()
        recent = await crawler.list_recent_versions(count=5)

        for version in recent:
            if version in cached_versions:
                continue
            try:
                logger.info(f"🔄 Backfilling version {version}...")
                raw_content, real_version = await crawler.fetch_patch_notes(version=version)
                result = await run_workflow(raw_content, version=real_version)
                save_analysis_to_cache(real_version, result)
                cached_versions.add(real_version)
                logger.info(f"✅ Backfill complete: {real_version}")
            except Exception as e:
                logger.warning(f"⚠️ Backfill failed for {version}: {e}")
    finally:
        _backfill_running = False


# ==================== Scheduler Trigger ====================

@app.post("/api/check-update")
async def manual_check_update():
    """Manually trigger a version check (for testing/debugging)."""
    from scheduler import check_for_new_version
    result = await check_for_new_version()
    return result


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
