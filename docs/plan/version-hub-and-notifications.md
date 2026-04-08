# Plan: 版本首页 + 定时检测 + 邮件订阅推送

> 2026-04-06 | 3 个功能，按依赖顺序分 Phase 执行

---

## 目标

把 LOLTopNews 从"手动输入版本号的单次查询工具"升级为"首页永远展示最新分析、新版本自动更新、订阅用户收到邮件通知"的自运转产品。

**核心体验**：用户打开首页就看到最新版本分析，无需任何输入。新版本更新时自动替换首页内容，最多保留最近 5 个版本。订阅用户在新版本分析完成后收到邮件。

---

## Phase 1: 版本列表首页 + 缓存管理

### 目标
首页永远展示最新版本分析结果。用户打开页面零操作即可看到内容。保留最近 5 个小版本的缓存，自动淘汰最老版本。

### 后端改动

#### 1.1 新增版本索引文件 `data/cache/versions.json`

当前每个版本缓存在 `data/cache/{version}.json`，但没有索引。新增一个 manifest 文件：

```json
{
  "latest": "26.5",
  "versions": [
    {"version": "26.5", "analyzed_at": "2026-04-06T12:00:00Z"},
    {"version": "26.4", "analyzed_at": "2026-03-20T12:00:00Z"},
    {"version": "26.3", "analyzed_at": "2026-03-06T12:00:00Z"}
  ],
  "max_versions": 5
}
```

#### 1.2 修改 `app/api.py` 缓存逻辑

**修改 `save_analysis_to_cache()`**：
- 保存缓存后，更新 `versions.json` 索引
- 如果版本数超过 `max_versions`(5)，删除最老版本的 JSON 缓存文件
- 新版本插入列表头部，自动成为 `latest`

**新增 endpoint**：

```python
@app.get("/api/versions")
async def list_versions():
    """Return version index: latest version + history list"""
    # Read versions.json, return as-is
    # If not exist, return {"latest": null, "versions": []}
```

```python
@app.get("/api/versions/{version}")
async def get_version(version: str):
    """Return cached analysis for a specific version"""
    # Read data/cache/{version}.json
    # 404 if not found
```

**修改现有 `GET /api/analyze`**：
- `version=latest` 时，先查 `versions.json` 的 `latest` 字段
- 如果 latest 有缓存，直接返回（不触发 crawler）
- 保持原有行为：无缓存时触发 crawler → workflow → 缓存

#### 1.3 文件改动清单

| 文件 | 改动 |
|------|------|
| `app/api.py` | 新增 `/api/versions`、`/api/versions/{version}`；修改 `save_analysis_to_cache` 维护索引 + 淘汰旧版本 |

### 前端改动

#### 1.4 首页自动加载最新版本

**修改 `App.tsx`**：
- 页面加载时调用 `GET /api/versions` 获取版本列表
- 如果 `latest` 存在，自动调用 `GET /api/versions/{latest}` 加载分析结果
- 如果 `latest` 为 null（首次使用），显示引导界面

#### 1.5 版本切换 sidebar/dropdown

**新增组件 `VersionSelector.tsx`**：
- 显示最近 5 个已分析版本
- 当前版本高亮
- 点击切换版本（调用 `/api/versions/{version}`，从缓存秒返回）
- 保留手动输入框用于分析新版本

#### 1.6 文件改动清单

| 文件 | 改动 |
|------|------|
| `frontend/src/App.tsx` | 启动逻辑改为先 fetch versions → auto-load latest |
| `frontend/src/components/VersionSelector.tsx` | 新增：版本列表 + 切换 |
| `frontend/src/services/api.ts` | 新增 `fetchVersions()`、`fetchVersionData(version)` |

### 测试

| 文件 | 测试 |
|------|------|
| `tests/test_api.py` | 新增：`/api/versions` 返回正确结构；缓存淘汰逻辑（第6个版本写入时第1个被删） |

---

## Phase 2: 定时检测新版本 + 自动分析

### 目标
后台定时（每小时）检查 LOL 官网是否有新版本公告。发现新版本时自动触发 pipeline 分析并存入缓存，首页自动更新。

### 方案选择

**方案 A：APScheduler（进程内定时任务）** ← 选这个
- 优点：零外部依赖，与 FastAPI 同进程，简单
- 缺点：单实例部署限制（但 MVP 阶段足够）

**方案 B：独立 cron 脚本** — 备选，更适合多实例部署

### 后端改动

#### 2.1 新增 `app/scheduler.py`

```python
# Use APScheduler to run version check every hour
# On startup: schedule check_for_new_version() at interval=3600s

async def check_for_new_version():
    """
    1. Call LOLOfficialCrawler.fetch_latest_patch_notes() to detect latest version
    2. Compare with versions.json latest
    3. If new version detected:
       a. Run full workflow (extractor → analyzer → summarizer)
       b. Save to cache + update versions.json (triggers eviction if > 5)
       c. Return new version info (for Phase 3 email trigger)
    4. If same version: no-op, log "no new version"
    """
```

#### 2.2 修改 `app/api.py` — 注册 scheduler

```python
from scheduler import start_scheduler, stop_scheduler

@app.on_event("startup")
async def startup():
    start_scheduler()

@app.on_event("shutdown")
async def shutdown():
    stop_scheduler()
```

**新增手动触发 endpoint**（用于调试/测试）：

```python
@app.post("/api/check-update")
async def manual_check_update():
    """Manually trigger version check (for testing)"""
    result = await check_for_new_version()
    return result
```

#### 2.3 文件改动清单

| 文件 | 改动 |
|------|------|
| `app/scheduler.py` | 新增：APScheduler 定时任务 + `check_for_new_version()` |
| `app/api.py` | 注册 scheduler lifecycle；新增 `/api/check-update` |
| `requirements.txt` / `pyproject.toml` | 新增 `apscheduler>=3.10` |

### 测试

| 文件 | 测试 |
|------|------|
| `tests/test_scheduler.py` | mock crawler 返回新版本 → 验证 workflow 被调用 + versions.json 更新 |
| `tests/test_scheduler.py` | mock crawler 返回已有版本 → 验证 no-op |

---

## Phase 3: 邮件订阅推送

### 目标
用户在前端输入 email 订阅。新版本分析完成后，自动向所有订阅者发送邮件，包含版本摘要和链接。

### 技术方案（参考 `opensource/email` 项目）

| 组件 | 选型 | 理由 |
|------|------|------|
| 邮件发送 | **Resend API** | `opensource/email` 已验证可用，API 简洁，免费额度充足 |
| 订阅者存储 | **JSON 文件** (MVP) → PostgreSQL (later) | 与现有 JSON 缓存方案一致，MVP 不引入数据库 |
| 退订 | Token-based unsubscribe link | 遵循 RFC 8058 one-click unsubscribe |

### 后端改动

#### 3.1 新增 `app/subscribers.py` — 订阅者管理

参考 `opensource/email/lib/subscribers.ts` 的接口设计，Python 版本：

```python
# Storage: data/subscribers.json
# Format: {
#   "subscribers": [
#     {"email": "a@b.com", "status": "active", "unsubscribe_token": "xxx", "created_at": "..."}
#   ]
# }

class SubscribersRepository:
    def upsert_active(self, email: str) -> tuple[dict, str]:  # (subscriber, action)
    def unsubscribe_by_token(self, token: str) -> dict | None:
    def list_active(self) -> list[dict]:
```

#### 3.2 新增 `app/email_client.py` — Resend 邮件发送

参考 `opensource/email/lib/email.ts`：

```python
class ResendEmailClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def send_email(self, *, from_addr, to, subject, html, text, headers=None, reply_to=None):
        """POST https://api.resend.com/emails"""
```

#### 3.3 新增 `app/email_template.py` — 邮件模板

参考 `opensource/email/lib/template.ts`，但内容改为版本分析摘要：

```python
def render_patch_email(version: str, summary: str, tier_highlights: list, unsubscribe_url: str) -> dict:
    """
    Return {"subject": "LOL 26.5 Top Lane Analysis", "html": "...", "text": "..."}
    Content:
    - Version number + date
    - Executive summary (1-2 sentences)
    - Top 3 tier changes (e.g. "Fiora: B→S", "Darius: A→B")
    - CTA: "View full analysis" link
    - Unsubscribe link (RFC 8058 List-Unsubscribe header)
    """
```

#### 3.4 修改 `app/api.py` — 订阅 API

```python
@app.post("/api/subscribe")
async def subscribe(request: SubscribeRequest):
    """Subscribe email to patch notifications"""
    # Validate email
    # Upsert into subscribers.json
    # Return {ok, email, status}

@app.get("/api/unsubscribe")
async def unsubscribe(token: str):
    """One-click unsubscribe via token"""
    # Find subscriber by token
    # Set status to "unsubscribed"
    # Return HTML confirmation page
```

#### 3.5 修改 `app/scheduler.py` — 分析完成后发送邮件

在 `check_for_new_version()` 中，分析完成后：

```python
async def check_for_new_version():
    # ... existing logic ...
    if new_version_detected:
        result = await run_workflow(...)
        save_analysis_to_cache(...)
        # NEW: send notification emails
        await send_patch_notifications(version, result)

async def send_patch_notifications(version: str, result: dict):
    """Send email to all active subscribers"""
    subscribers = repository.list_active()
    for sub in subscribers:
        email = render_patch_email(version, result["summary_report"], ..., unsubscribe_url)
        await client.send_email(to=sub["email"], ...)
```

#### 3.6 文件改动清单

| 文件 | 改动 |
|------|------|
| `app/subscribers.py` | 新增：JSON-based 订阅者管理 |
| `app/email_client.py` | 新增：Resend API client |
| `app/email_template.py` | 新增：邮件模板渲染 |
| `app/api.py` | 新增 `/api/subscribe`、`/api/unsubscribe` |
| `app/scheduler.py` | 分析完成后触发 `send_patch_notifications()` |
| `.env.example` | 新增 `RESEND_API_KEY`、`EMAIL_FROM`、`APP_BASE_URL` |
| `requirements.txt` / `pyproject.toml` | 新增 `httpx`（已有，用于 Resend API 调用） |

### 前端改动

#### 3.7 新增订阅组件 `SubscribeForm.tsx`

```
┌─────────────────────────────────────┐
│  📬 Subscribe to Patch Updates      │
│  ┌─────────────────────┐ ┌────────┐ │
│  │ your@email.com      │ │Subscribe│ │
│  └─────────────────────┘ └────────┘ │
│  Get notified when a new patch      │
│  analysis is published.             │
└─────────────────────────────────────┘
```

- 放在首页底部或 header 区域
- POST `/api/subscribe` with email
- 成功后显示确认消息
- 基础 email 格式校验

#### 3.8 文件改动清单

| 文件 | 改动 |
|------|------|
| `frontend/src/components/SubscribeForm.tsx` | 新增：邮件订阅表单 |
| `frontend/src/App.tsx` | 引入 SubscribeForm |
| `frontend/src/services/api.ts` | 新增 `subscribe(email)` |

### 测试

| 文件 | 测试 |
|------|------|
| `tests/test_subscribers.py` | upsert、unsubscribe、list_active、重复订阅幂等性 |
| `tests/test_email.py` | mock Resend API → 验证 send_email 正确调用；模板渲染 |
| `tests/test_api.py` | `/api/subscribe` 成功/失败；`/api/unsubscribe` 有效/无效 token |

---

## 执行顺序 & 依赖关系

```
Phase 1 (版本首页)
    │
    ├── 后端: versions.json + API endpoints
    ├── 前端: auto-load latest + VersionSelector
    └── 测试
          │
Phase 2 (定时检测)
    │   依赖 Phase 1 的 versions.json 索引
    ├── scheduler.py + check_for_new_version()
    ├── /api/check-update 手动触发
    └── 测试
          │
Phase 3 (邮件推送)
        依赖 Phase 2 的新版本检测
    ├── subscribers.py + email_client.py + email_template.py
    ├── /api/subscribe + /api/unsubscribe
    ├── scheduler.py 集成发送逻辑
    ├── 前端 SubscribeForm
    └── 测试
```

## 新增环境变量

| 变量 | Phase | 必需 | 说明 |
|------|-------|------|------|
| `RESEND_API_KEY` | 3 | 是 | Resend 邮件服务 API key |
| `EMAIL_FROM` | 3 | 是 | 发件人地址 (e.g. `LOLTopNews <noreply@yourdomain.com>`) |
| `APP_BASE_URL` | 3 | 是 | 应用 URL，用于构造退订链接 |
| `CHECK_INTERVAL_SECONDS` | 2 | 否 | 检测间隔，默认 3600 |

## 风险 & 注意事项

1. **LOL 官网反爬** — 每小时检测一次频率很低，被封风险小。但应增加 User-Agent 随机化和请求间隔抖动。
2. **JSON 文件并发写入** — scheduler 和 API 可能同时写 versions.json。用 `filelock` 或 `asyncio.Lock` 保护。
3. **邮件发送失败** — 参考 `opensource/email` 的做法：单个订阅者发送失败不阻塞其他人，跳过并继续。
4. **Resend 免费额度** — 每月 3000 封，初期足够。
