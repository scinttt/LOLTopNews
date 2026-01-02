# 英雄联盟上单版本更新指南 - 系统架构设计

## 项目概述
构建一个自动化的英雄联盟上单位置版本更新分析系统，通过爬虫获取官方更新公告，使用 LangGraph 编排多个 Agent 进行智能分析，最终生成上单生态影响报告并展示在 Web 界面。

## 技术栈选型
- **后端框架**: FastAPI
- **AI 编排**: LangGraph
- **大模型**: DeepSeek (deepseek-chat / deepseek-coder)
  - 成本优势: ¥1/M tokens (输入), ¥2/M tokens (输出)
  - 中文能力强，适合游戏领域分析
- **数据库**: PostgreSQL + pgvector (向量存储)
- **爬虫**: aiohttp + BeautifulSoup4 + Selenium (应对动态页面)
- **定时任务**: APScheduler (第二阶段)
- **前端**: FastAPI + Jinja2 模板 (第二阶段)
- **缓存**: Redis (可选，第二阶段优化)

---

## 核心架构设计

### 1. 系统架构（3个 LangGraph Agents + 爬虫模块）✅ 优化版

```
┌─────────────────────────────────────────────────────────────┐
│                     System Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐                                            │
│  │   Crawler    │  (普通 Python 模块，非 Agent)              │
│  │   Module     │                                            │
│  └──────┬───────┘                                            │
│         │                                                     │
│         ▼                                                     │
│  ┌─────────────────────────────────────────┐                │
│  │      LangGraph Workflow (3 Agents)      │                │
│  ├─────────────────────────────────────────┤                │
│  │                                          │                │
│  │  ┌──────────────────────────┐           │                │
│  │  │      Agent 1             │           │                │
│  │  │  Extractor + Filter      │           │                │
│  │  │ (提取上单相关变更)        │           │                │
│  │  └──────────┬───────────────┘           │                │
│  │             │                            │                │
│  │             ▼                            │                │
│  │  ┌──────────────────────────┐           │                │
│  │  │      Agent 2             │           │                │
│  │  │   Impact Analyzer        │           │                │
│  │  │  (深度影响分析)           │           │                │
│  │  └──────────┬───────────────┘           │                │
│  │             │                            │                │
│  │             ▼                            │                │
│  │  ┌──────────────────────────┐           │                │
│  │  │      Agent 3             │           │                │
│  │  │   Report Summarizer      │           │                │
│  │  │   (生成总结报告)          │           │                │
│  │  └──────────────────────────┘           │                │
│  │                                          │                │
│  └─────────────────────────────────────────┘                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**优化说明**:
- ✅ **从 4 个 Agents 减少到 3 个**
- ✅ **Extractor 和 Filter 合并** - 一次性提取上单相关变更
- ✅ **减少 Token 消耗** - 不提取无关英雄
- ✅ **减少 LLM 调用** - 去掉 Filter 的边缘英雄判断
- ✅ **简化 State 管理** - 少一层数据传递

#### Crawler Module（爬虫模块 - 非 Agent）
**职责**: 从固定数据源爬取版本更新内容
- **为什么不是 Agent**: 爬虫逻辑固定，目标明确，不需要 LLM 决策
- **输入**: 版本号（如 "14.24"）或 "latest"
- **数据源**:
  1. 英雄联盟官网更新公告 (https://lol.qq.com/gicp/news/410/37072785.html)
  2. 备用: 搜索引擎（Bing/Google 搜索 "英雄联盟 {version} 更新"）
- **输出**: 原始 HTML/文本内容，**直接传给 Extractor Agent**（不存数据库）
- **实现**:
  - 使用 aiohttp + BeautifulSoup4（优先）
  - 如遇反爬，使用 Selenium（备选）
  - 简单的重试机制（3次）
- **可选调试**: 开发阶段可将原始数据保存到 `data/raw_patches/{version}.html` 用于调试

**实现示例**:
```python
# crawlers/lol_official.py
class LOLOfficialCrawler:
    async def fetch_patch_notes(self, version: str = "latest"):
        """爬取指定版本的更新公告"""
        url = f"https://lol.qq.com/news/category_64.shtml"
        # 爬取逻辑...
        return raw_html
```

#### Agent 1: Top Lane Extractor（上单变更提取器）✅ 合并版
**职责**: 从原始公告中**直接提取上单位置相关的变更**（提取 + 筛选一步完成）

- **输入**: Crawler Module 的原始 HTML/文本内容

- **处理逻辑**:
  1. **智能筛选**: 在提取时就判断是否与上单相关
     - 核心上单英雄: 剑姬、诺手、剑魔、刀妹、鳄鱼、青钢影等 (~40个)
     - 边缘上单: 亚索、卡蜜尔等（根据变更内容判断）
     - 上单装备/符文: 黑切、日炎、征服者、坚决系符文等
     - 上路系统变更: 峡谷先锋、上路经验、防御塔机制

  2. **Prompt 设计** (关键):
     ```
     你是英雄联盟上单位置专家。从以下更新公告中提取**仅与上单位置相关的变更**。

     关注点:
     1. 上单常用英雄变更（剑姬、诺手、剑魔、刀妹...）
     2. 可以打上单的英雄变更（亚索、卡蜜尔等，需判断变更是否影响上路）
     3. 上单常用装备变更（黑切、日炎、三相、死舞、破败...）
     4. 上单相关符文变更（征服者、坚决系、凯旋...）
     5. 上路机制变更（峡谷先锋、上路经验、防御塔...）

     **忽略**: 中单、ADC、辅助、打野专属英雄和装备

     输出格式: JSON（只返回上单相关的变更）
     ```

- **输出**: JSON 格式的上单相关结构化数据
  ```json
  {
    "version": "14.24",
    "release_date": "2024-12-XX",
    "top_lane_changes": [
      {
        "champion": "剑姬",
        "type": "buff",
        "relevance": "primary",  // primary=主玩上单, secondary=可上单
        "details": {
          "Q技能": {"cooldown": "16/14/12/10/8 → 15/13/11/9/7"},
          "基础属性": {"移动速度": "345 → 350"}
        }
      },
      {
        "champion": "诺手",
        "type": "nerf",
        "relevance": "primary",
        "details": {...}
      }
    ],
    "item_changes": [
      {
        "item": "黑色切割者",
        "change": "攻击力 50 → 55"
      }
    ],
    "system_changes": [
      {
        "category": "峡谷先锋",
        "change": "先锋撞墙伤害增加"
      }
    ]
  }
  ```

- **优势**:
  - ✅ **一次性完成提取和筛选** - 不需要第二个 Agent
  - ✅ **减少 Token 消耗** - 不提取中单/打野/辅助英雄
  - ✅ **更准确** - LLM 在提取时就理解上单语境
  - ✅ **配置灵活** - 通过 Prompt 控制筛选逻辑

#### Agent 2: Impact Analyzer（影响分析器）
**职责**: 深度分析每个变更对上单生态的影响
- **输入**: Agent 1 的上单相关变更（已筛选）
- **处理**:
  - 调用 LLM 分析每个英雄变更的强度评估
  - 分析对线影响、团战影响、carry 能力变化
  - 预测 meta 变化（哪些英雄会崛起/削弱）
  - **RAG 增强**: 从历史版本数据中检索相似变更案例
- **输出**: 每个英雄的影响分析报告
  ```json
  {
    "champion": "剑姬",
    "impact_score": 7.5,
    "tier_prediction": "S → S+",
    "analysis": {
      "laning": "Q技能CD降低提升换血能力...",
      "teamfight": "移速提升改善绕后切C能力...",
      "counters_change": ["克烈上升", "诺手下降"],
      "recommended_builds": ["三相→死舞→破败"]
    }
  }
  ```

#### Agent 3: Report Summarizer（报告总结器）
**职责**: 生成最终的版本更新总结报告
- **输入**: Agent 2 的所有分析结果
- **处理**:
  - 汇总本版本上单 meta 变化趋势
  - 生成推荐英雄榜（Tier List）
  - 生成对抗关系图变化
  - 生成简洁的摘要和详细报告
- **输出**:
  - Markdown 格式的详细报告
  - 用于前端展示的 JSON 数据

---

## 2. API 调用方案

### LLM API 调用点（3 个 Agents，无爬虫）✅ 优化后

| 模块/Agent | API调用次数/版本 | 用途 | DeepSeek 模型 | Token估算 | 成本估算 |
|-----------|-----------------|------|--------------|----------|---------|
| **Crawler Module** | **0次** | **爬取数据（无需 LLM）** | **N/A** | **N/A** | ¥0 |
| **Top Lane Extractor** | **1次** | **提取上单相关变更** | deepseek-chat | 输入: 8-15K, 输出: 1.5K | ~¥0.02 |
| **Impact Analyzer** | **N次**(10个英雄) | **深度影响分析** | deepseek-chat | 输入: 3K, 输出: 1.5K | ~¥0.14 |
| **Report Summarizer** | **1次** | **生成总结报告** | deepseek-chat | 输入: 8K, 输出: 2.5K | ~¥0.04 |

**总计**: 12 次 API 调用 (vs 原方案的 12-17 次)

**成本对比** (基于 DeepSeek 定价):
- **优化前**: ~¥0.25/版本 (17 次调用)
- **优化后**: ~¥0.20/版本 (12 次调用) ✅ **节省 20%**
- 总 tokens: ~120K 输入 + 40K 输出
- 计算: (120/1000 × ¥1) + (40/1000 × ¥2) = **¥0.20/版本**

**优化效果**:
- ✅ **减少 5 次 LLM 调用**（去掉 Filter Agent）
- ✅ **节省 20% 成本**
- ✅ **减少 30% Token 消耗**（不提取无关英雄）
- ✅ **降低 15% 延迟**（少一个 Agent 处理步骤）

**成本优化策略**:
- DeepSeek 本身已极便宜，无需过度优化
- 实施简单缓存避免重复分析
- 批处理多个英雄可进一步降低调用次数

### 其他 API
- **DeepSeek API**: https://api.deepseek.com
  - 需要注册账号获取 API Key
  - 文档: https://platform.deepseek.com/docs
- **Riot Games API** (可选): 获取英雄元数据
  - 需要申请开发者 Key: https://developer.riotgames.com
- **搜索引擎 API** (可选): Google Custom Search API 或 SerpAPI

---

## 3. 数据存储方案

### PostgreSQL 数据库表设计

#### 3.1 核心数据表

**`patch_versions` - 版本信息表（简化版 - 不存原始数据）**
```sql
CREATE TABLE patch_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) UNIQUE NOT NULL,  -- 如 "14.24"
    release_date DATE,
    source_url TEXT,  -- 来源 URL，便于重新爬取
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**设计说明**:
- ✅ **不存储 `raw_content`** - 原始 HTML 直接传给 Extractor，不入库
- ✅ **节省空间** - 每个版本节省 50-200KB 存储
- ✅ **简化流程** - 减少数据库读写操作
- ✅ **保留 `source_url`** - 如需重新分析，可通过 URL 重新爬取
- ✅ **开发调试** - 临时数据可保存到 `data/raw_patches/` 文件夹

**`champion_changes` - 英雄变更表**
```sql
CREATE TABLE champion_changes (
    id SERIAL PRIMARY KEY,
    patch_id INT REFERENCES patch_versions(id),
    champion_name VARCHAR(50),
    champion_key VARCHAR(50),  -- 英雄标识符
    change_type VARCHAR(20),  -- buff/nerf/adjust/rework
    details JSONB,  -- 详细变更数据
    impact_score FLOAT,  -- 影响评分 0-10
    tier_before VARCHAR(10),  -- 变更前评级
    tier_after VARCHAR(10),   -- 变更后评级
    created_at TIMESTAMP DEFAULT NOW()
);
```

**`impact_analysis` - 影响分析表**
```sql
CREATE TABLE impact_analysis (
    id SERIAL PRIMARY KEY,
    change_id INT REFERENCES champion_changes(id),
    laning_impact TEXT,  -- 对线期影响
    teamfight_impact TEXT,  -- 团战影响
    meta_impact TEXT,  -- meta 影响
    counter_changes JSONB,  -- 克制关系变化
    build_recommendations JSONB,  -- 出装推荐
    analysis_embedding vector(1536),  -- pgvector 向量
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON impact_analysis USING ivfflat (analysis_embedding vector_cosine_ops);
```

**`patch_summaries` - 版本总结表**
```sql
CREATE TABLE patch_summaries (
    id SERIAL PRIMARY KEY,
    patch_id INT REFERENCES patch_versions(id),
    summary_text TEXT,  -- Markdown 总结
    meta_tier_list JSONB,  -- Tier List 数据
    key_changes JSONB,  -- 关键变化摘要
    created_at TIMESTAMP DEFAULT NOW()
);
```

**`top_champions` - 上单英雄池（配置表）**
```sql
CREATE TABLE top_champions (
    id SERIAL PRIMARY KEY,
    champion_name VARCHAR(50),
    champion_key VARCHAR(50),
    is_primary_top BOOLEAN DEFAULT TRUE,  -- 是否主玩上路
    play_rate_top FLOAT,  -- 上路胜率参考
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.2 RAG 知识库

**历史数据向量化存储**:
- 将历史版本的分析报告、变更数据转换为 embedding
- 使用 pgvector 存储在 `impact_analysis.analysis_embedding`
- 当分析新版本时，检索相似的历史变更案例辅助分析

**RAG 实现程度**:
- **Level 1 (推荐)**: 基础语义检索
  - 存储历史分析报告的 embedding
  - 分析时检索 Top-K 相似案例
  - 将案例作为 context 传给 LLM

- **Level 2**: 如果需要更高级
  - 构建英雄技能、装备属性的向量索引
  - 实现多跳推理（英雄→克制关系→装备链）
  - 融合图数据库（Neo4j）存储英雄关系网络

**向量化内容**:
1. 历史版本的影响分析文本
2. 英雄技能描述
3. 用户反馈和社区评论（如果爬取）

---

## 4. 项目目录结构（推荐方案）

### 方案对比

| 方案 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **单文件** | 原型验证 | 快速开发 | 难以维护，职责不清 |
| **5个文件** | 小型项目 | 简单直观 | 扩展性差，测试困难 |
| **模块化目录 (推荐)** | 生产项目 | 清晰、可测试、可扩展 | 初期稍复杂 |

### 推荐：模块化目录结构

```
lol_top_guide/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 主入口（MVP 阶段可选）
│   ├── config.py                    # 配置管理
│   ├── database.py                  # 数据库连接
│   │
│   ├── crawlers/                    # 爬虫模块（独立模块，非 Agent）
│   │   ├── __init__.py
│   │   ├── base.py                  # 爬虫基类（重试、异常处理）
│   │   ├── lol_official.py          # 官网爬虫实现
│   │   └── search_engine.py         # 搜索引擎备用爬虫（可选）
│   │
│   ├── agents/                      # LangGraph Agents（4个 Agent）
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Agent 基类（共享逻辑）
│   │   │
│   │   ├── extractor/               # Agent 1: Extractor（每个 Agent 一个文件夹）
│   │   │   ├── __init__.py
│   │   │   ├── agent.py             # Agent 核心逻辑
│   │   │   └── prompts.py           # Prompt 模板
│   │   │
│   │   ├── filter/                  # Agent 2: Top Lane Filter
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── prompts.py
│   │   │   └── champions_config.py  # 上单英雄白名单
│   │   │
│   │   ├── analyzer/                # Agent 3: Impact Analyzer
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   │
│   │   ├── summarizer/              # Agent 4: Summary Report
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   └── prompts.py
│   │   │
│   │   └── workflow.py              # LangGraph 流程编排（连接4个 Agent）
│   │
│   ├── models/                      # 数据库模型（SQLAlchemy）
│   │   ├── __init__.py
│   │   ├── patch.py                 # PatchVersion 模型
│   │   ├── champion.py              # ChampionChange 模型
│   │   └── analysis.py              # ImpactAnalysis 模型
│   │
│   ├── services/                    # 业务服务层
│   │   ├── __init__.py
│   │   ├── llm_service.py           # DeepSeek API 封装
│   │   ├── rag_service.py           # RAG 检索服务（向量搜索）
│   │   └── scheduler.py             # 定时任务（Phase 2）
│   │
│   ├── schemas/                     # Pydantic 数据模型
│   │   ├── __init__.py
│   │   ├── patch.py                 # 版本数据结构
│   │   └── analysis.py              # 分析结果结构
│   │
│   └── utils/                       # 工具函数
│       ├── __init__.py
│       ├── logger.py                # 日志配置
│       └── helpers.py               # 通用辅助函数
│
├── tests/                           # 测试文件（镜像 app/ 结构）
│   ├── __init__.py
│   ├── test_crawlers/
│   ├── test_agents/
│   └── test_services/
│
├── scripts/                         # 独立脚本
│   ├── run_analysis.py              # MVP 核心入口：分析单个版本
│   ├── init_db.py                   # 初始化数据库
│   └── seed_champions.py            # 导入上单英雄列表
│
├── data/                            # 配置数据文件
│   ├── top_champions.json           # 上单英雄白名单
│   ├── raw_patches/                 # 原始数据（仅开发调试，不提交 Git）
│   │   ├── 14.24.html
│   │   └── 14.23.html
│   └── prompts/                     # Prompt 模板（也可以放在代码里）
│       ├── extractor.txt
│       ├── filter.txt
│       ├── analyzer.txt
│       └── summarizer.txt
│
├── migrations/                      # Alembic 数据库迁移
│   └── versions/
│
├── .env.example                     # 环境变量模板
├── .env                             # 实际环境变量（不提交到 Git）
├── requirements.txt                 # 依赖包
├── pyproject.toml                   # 项目配置（可选）
├── README.md                        # 项目说明
└── .gitignore
```

---

## 详细说明

### 1. **爬虫模块** (`crawlers/`)
**为什么独立**：非 Agent，逻辑固定，可独立测试

```
crawlers/
├── base.py              # 基类：重试、异常处理、日志
├── lol_official.py      # 实现：爬取官网
└── search_engine.py     # 实现：备用方案
```

**示例代码**：
```python
# crawlers/base.py
class BaseCrawler:
    async def fetch_with_retry(self, url: str, retries: int = 3):
        """带重试的爬取逻辑"""
        pass

# crawlers/lol_official.py
from .base import BaseCrawler

class LOLOfficialCrawler(BaseCrawler):
    async def fetch_patch_notes(self, version: str):
        """爬取官网版本更新"""
        pass
```

---

### 2. **Agents 模块** (`agents/`)
**为什么每个 Agent 一个文件夹**：
- ✅ 每个 Agent 有独立的 Prompt、逻辑、配置
- ✅ 便于单独测试和优化
- ✅ Prompt 模板可以独立管理（后期可迁移到数据库）

```
agents/
├── extractor/
│   ├── agent.py         # 核心逻辑
│   └── prompts.py       # Prompt 模板
├── filter/
│   ├── agent.py
│   ├── prompts.py
│   └── champions_config.py  # 白名单配置
├── analyzer/
│   ├── agent.py
│   └── prompts.py
├── summarizer/
│   ├── agent.py
│   └── prompts.py
└── workflow.py          # LangGraph 编排
```

**示例代码**：
```python
# agents/extractor/agent.py
from langchain.agents import Agent
from .prompts import EXTRACTOR_PROMPT

class ExtractorAgent(Agent):
    def __init__(self, llm_service):
        self.llm = llm_service
        self.prompt = EXTRACTOR_PROMPT

    async def run(self, state: dict):
        """提取结构化数据"""
        raw_content = state["raw_content"]
        result = await self.llm.extract_structured_data(raw_content)
        return {"structured_data": result}

# agents/extractor/prompts.py
EXTRACTOR_PROMPT = """
你是英雄联盟数据提取专家...
"""

# agents/workflow.py
from langgraph.graph import StateGraph
from .extractor.agent import ExtractorAgent
from .filter.agent import FilterAgent
# ...

def build_workflow(llm_service):
    workflow = StateGraph()

    extractor = ExtractorAgent(llm_service)
    filter_agent = FilterAgent(llm_service)
    # ...

    workflow.add_node("extractor", extractor.run)
    workflow.add_node("filter", filter_agent.run)
    # ...

    return workflow.compile()
```

---

### 3. **MVP 阶段的简化方案**（可选）

如果想快速验证，可以先用简化版本：

```
lol_top_guide/
├── app/
│   ├── crawlers/
│   │   └── lol_official.py          # 单文件实现爬虫
│   ├── agents/
│   │   ├── extractor_agent.py       # 每个 Agent 一个文件
│   │   ├── filter_agent.py
│   │   ├── analyzer_agent.py
│   │   ├── summarizer_agent.py
│   │   └── workflow.py              # LangGraph 编排
│   ├── services/
│   │   └── llm_service.py           # DeepSeek API
│   └── models/
│       └── database.py              # 所有数据库模型
│
├── scripts/
│   └── run_analysis.py              # 主入口
│
├── data/
│   └── top_champions.json           # 配置文件
│
└── requirements.txt
```

**渐进式演进路径**：
1. **Week 1**: 使用简化版本快速开发
2. **Week 2**: 如果代码超过 200 行/文件，拆分成子文件夹
3. **Week 3**: 补充测试，规范化目录结构

---

### 4. **核心文件说明**

#### `scripts/run_analysis.py` - MVP 主入口
```python
"""
命令行工具：分析指定版本
使用: python scripts/run_analysis.py --version 14.24
"""
import asyncio
import os
from app.crawlers.lol_official import LOLOfficialCrawler
from app.agents.workflow import build_workflow
from app.services.llm_service import DeepSeekService
from app.database import save_analysis_results

async def main(version: str, debug: bool = False):
    # 1. 爬取数据（不存数据库）
    crawler = LOLOfficialCrawler()
    raw_content = await crawler.fetch_patch_notes(version)

    # 可选：开发调试时保存原始数据到文件
    if debug:
        os.makedirs('data/raw_patches', exist_ok=True)
        with open(f'data/raw_patches/{version}.html', 'w') as f:
            f.write(raw_content)
        print(f"✅ 原始数据已保存到 data/raw_patches/{version}.html")

    # 2. 运行 LangGraph 流程（直接处理）
    llm_service = DeepSeekService()
    workflow = build_workflow(llm_service)
    result = await workflow.ainvoke({
        "raw_content": raw_content,
        "version": version,
        "source_url": crawler.last_url  # 保存来源 URL
    })

    # 3. 只保存分析结果到数据库（不含原始内容）
    await save_analysis_results(version, result)
    print(f"✅ 分析完成，成本 ¥{result.get('cost', 0.20):.2f}，结果已存储")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, help="版本号，如 14.24")
    parser.add_argument("--debug", action="store_true", help="保存原始数据到文件")
    args = parser.parse_args()

    asyncio.run(main(args.version, args.debug))
```

#### `agents/workflow.py` - LangGraph 编排
```python
from langgraph.graph import StateGraph, END
from .extractor.agent import ExtractorAgent
from .filter.agent import FilterAgent
from .analyzer.agent import AnalyzerAgent
from .summarizer.agent import SummarizerAgent

def build_workflow(llm_service):
    workflow = StateGraph()

    # 实例化 Agents
    extractor = ExtractorAgent(llm_service)
    filter_agent = FilterAgent(llm_service)
    analyzer = AnalyzerAgent(llm_service)
    summarizer = SummarizerAgent(llm_service)

    # 添加节点
    workflow.add_node("extractor", extractor.run)
    workflow.add_node("filter", filter_agent.run)
    workflow.add_node("analyzer", analyzer.run)
    workflow.add_node("summarizer", summarizer.run)

    # 定义流程
    workflow.set_entry_point("extractor")
    workflow.add_edge("extractor", "filter")
    workflow.add_edge("filter", "analyzer")
    workflow.add_edge("analyzer", "summarizer")
    workflow.add_edge("summarizer", END)

    return workflow.compile()
```

---

### 5. **详细开发顺序（MVP 3周）**

## 🎯 核心原则
1. **验证优先** - 每天都要有可运行的代码
2. **端到端快速打通** - 先跑通流程，再优化细节
3. **风险前置** - 先解决最不确定的部分（爬虫、LLM 调用）
4. **数据驱动** - 用真实数据测试每个环节

---

## Week 1: 基础设施 + 核心验证

### Day 1: 环境搭建 + DeepSeek API 验证（最重要！）

**目标**: 确保核心依赖可用，DeepSeek API 能正常调用

```bash
# 1. 创建项目结构（简化版）
lol_top_guide/
├── app/
│   ├── services/
│   │   └── llm_service.py       # 今天重点
│   └── __init__.py
├── scripts/
│   └── test_deepseek.py         # 测试脚本
├── .env
└── requirements.txt
```

**任务清单**:
- [ ] 创建虚拟环境 `python -m venv .venv`
- [ ] 安装核心依赖 `pip install openai python-dotenv`
- [ ] 注册 DeepSeek 账号，获取 API Key
- [ ] 编写 `llm_service.py`（核心服务）
- [ ] 编写测试脚本验证 API 调用
- [ ] **验收**: 能成功调用 DeepSeek 并返回 JSON 格式数据

**示例代码**:
```python
# scripts/test_deepseek.py
from app.services.llm_service import DeepSeekService

async def main():
    service = DeepSeekService()

    # 测试简单调用
    messages = [{"role": "user", "content": "你好，返回JSON: {\"test\": \"success\"}"}]
    result = await service.chat(messages, temperature=0.3)
    print(f"✅ DeepSeek 调用成功: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

### Day 2: 爬虫模块 + 真实数据获取

**目标**: 能成功爬取英雄联盟官网的更新公告

```bash
lol_top_guide/
├── app/
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── base.py              # 重试逻辑
│   │   └── lol_official.py      # 今天重点
│   └── services/
│       └── llm_service.py
├── scripts/
│   ├── test_deepseek.py
│   └── test_crawler.py          # 今天新增
└── data/
    └── raw_patches/             # 开发调试用（不提交 Git）
        └── 14.24.html
```

**任务清单**:
- [ ] 安装爬虫依赖 `pip install aiohttp beautifulsoup4 lxml`
- [ ] 实现 `base.py`（重试机制、异常处理）
- [ ] 实现 `lol_official.py`（爬取逻辑，返回内存字符串）
- [ ] 手动测试爬取 1-2 个版本
- [ ] **可选**: 将爬取结果保存到 `data/raw_patches/{version}.html` 用于调试
- [ ] **验收**: 能获取到完整的更新公告文本（至少 5KB）

**爬虫目标页面**:
- 主页: https://lol.qq.com/news/category_64.shtml
- 具体公告: https://lol.qq.com/news/detail.shtml?id=xxx

**重要**: 爬虫直接返回字符串，**不存数据库**，直接传给下一步的 Extractor

---

### Day 3: Extractor Agent + 第一个 LLM 提取

**目标**: 用 DeepSeek 提取上单相关变更（核心功能）

```bash
lol_top_guide/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── extractor_agent.py   # 今天重点
│   ├── crawlers/
│   └── services/
└── scripts/
    └── test_extractor.py        # 测试提取
```

**任务清单**:
- [ ] 安装 LangGraph `pip install langgraph langchain`
- [ ] 编写 `extractor_agent.py`
- [ ] 设计 Extractor Prompt（参考架构文档）
- [ ] 用 Day 2 的样本数据测试提取
- [ ] 调试 Prompt，确保返回正确的 JSON
- [ ] **验收**: 能从真实公告中提取出 5-10 个上单英雄变更

**测试脚本**:
```python
# scripts/test_extractor.py
from app.agents.extractor_agent import TopLaneExtractor
from app.services.llm_service import DeepSeekService

async def main():
    # 读取样本数据
    with open('data/sample_patch.txt', 'r') as f:
        raw_content = f.read()

    # 测试提取
    llm = DeepSeekService()
    extractor = TopLaneExtractor(llm)
    result = await extractor.run({"raw_content": raw_content})

    print(f"✅ 提取到 {len(result['top_lane_changes'])} 个上单变更")
    print(result)

asyncio.run(main())
```

---

### Day 4-5: Analyzer Agent + 影响分析

**目标**: 实现影响分析功能

```bash
lol_top_guide/
├── app/
│   ├── agents/
│   │   ├── extractor_agent.py
│   │   └── analyzer_agent.py    # 今天重点
│   ├── crawlers/
│   └── services/
└── scripts/
    └── test_analyzer.py
```

**任务清单**:
- [ ] 编写 `analyzer_agent.py`
- [ ] 设计 Analyzer Prompt（重点！）
- [ ] 用 Day 3 提取的数据测试分析
- [ ] 优化 Prompt，提升分析质量
- [ ] **验收**: 能对单个英雄生成完整的影响分析报告

---

### Day 6-7: 数据库 + 数据持久化

**目标**: 搭建 PostgreSQL，能存储分析结果

```bash
lol_top_guide/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── patch.py             # 今天重点
│   │   └── champion.py
│   ├── database.py              # 数据库连接
│   └── config.py                # 配置管理
├── migrations/                   # Alembic 迁移
└── scripts/
    ├── init_db.py               # 初始化数据库
    └── test_db.py               # 测试存储
```

**任务清单**:
- [ ] 安装 PostgreSQL（推荐 Docker）
  ```bash
  docker run --name lol-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
  ```
- [ ] 安装依赖 `pip install sqlalchemy asyncpg alembic`
- [ ] 编写数据库模型（先实现核心 3 张表）
- [ ] 创建迁移脚本
- [ ] 测试数据存储和查询
- [ ] **验收**: 能将分析结果存入数据库并查询

---

## Week 2: 集成完整流程

### Day 8: Summarizer Agent

**目标**: 实现总结报告生成

```bash
lol_top_guide/
├── app/
│   ├── agents/
│   │   ├── extractor_agent.py
│   │   ├── analyzer_agent.py
│   │   └── summarizer_agent.py  # 今天重点
```

**任务清单**:
- [ ] 编写 `summarizer_agent.py`
- [ ] 设计 Summarizer Prompt
- [ ] 测试生成 Markdown 报告
- [ ] **验收**: 能生成完整的版本总结（Markdown + JSON）

---

### Day 9-10: LangGraph Workflow 编排

**目标**: 将 3 个 Agents 串联起来

```bash
lol_top_guide/
├── app/
│   ├── agents/
│   │   ├── extractor_agent.py
│   │   ├── analyzer_agent.py
│   │   ├── summarizer_agent.py
│   │   └── workflow.py          # 今天重点
```

**任务清单**:
- [ ] 编写 `workflow.py`（LangGraph 编排）
- [ ] 定义 State 结构
- [ ] 连接 3 个 Agents
- [ ] 测试端到端流程
- [ ] **验收**: 输入原始公告 → 输出完整分析报告

**测试命令**:
```bash
python scripts/test_workflow.py --version 14.24
```

---

### Day 11-12: 完整流程 + 命令行工具

**目标**: 实现 `run_analysis.py`，完整流程打通

```bash
lol_top_guide/
├── scripts/
│   └── run_analysis.py          # 今天重点：完整流程
```

**任务清单**:
- [ ] 编写 `run_analysis.py`（爬虫 → Workflow → 数据库）
- [ ] **重点**: 爬虫数据直接传给 Workflow，不存数据库
- [ ] 添加 `--debug` 参数，可选保存原始数据到文件
- [ ] 添加命令行参数解析和进度显示
- [ ] 测试分析 2-3 个版本
- [ ] **验收**:
  ```bash
  # 正常模式（不保存原始数据）
  python scripts/run_analysis.py --version 14.24
  # 输出: ✅ 分析完成，成本 ¥0.20，结果已存储

  # 调试模式（保存原始数据到文件）
  python scripts/run_analysis.py --version 14.24 --debug
  # 额外输出: ✅ 原始数据已保存到 data/raw_patches/14.24.html
  ```

---

### Day 13-14: Prompt 优化 + 测试

**目标**: 优化 Prompt，提升分析质量

**任务清单**:
- [ ] 分析 3 个版本，收集 LLM 输出
- [ ] 识别提取错误和分析不准确的地方
- [ ] 优化 3 个 Agent 的 Prompt
- [ ] 重新测试，对比优化前后效果
- [ ] 记录成本和性能数据
- [ ] **验收**: 提取准确率 > 90%，分析合理性好

---

## Week 3: 完善与优化

### Day 15-16: 配置文件 + 上单英雄白名单

**目标**: 完善配置管理

```bash
lol_top_guide/
├── data/
│   ├── top_champions.json       # 今天重点
│   └── config.yaml              # 配置文件
├── app/
│   └── config.py                # 配置加载
```

**任务清单**:
- [ ] 编写 `top_champions.json`（40+ 上单英雄）
- [ ] 创建配置文件管理系统
- [ ] 将硬编码的配置移到文件
- [ ] **验收**: 修改配置文件能影响 Extractor 行为

---

### Day 17-18: 错误处理 + 重试机制

**目标**: 增强系统健壮性

**任务清单**:
- [ ] 添加爬虫重试逻辑（3次）
- [ ] 添加 LLM 调用重试（网络错误）
- [ ] 添加数据库事务处理
- [ ] 添加异常日志记录
- [ ] 测试各种失败场景
- [ ] **验收**: 系统能优雅处理各种错误

---

### Day 19-20: 文档 + 性能测试

**目标**: 完成 MVP，准备交付

**任务清单**:
- [ ] 编写 README.md（快速开始指南）
- [ ] 编写 API 文档（Prompt 模板说明）
- [ ] 性能测试：连续分析 5 个版本
- [ ] 成本核算：记录实际花费
- [ ] 整理代码，添加注释
- [ ] **验收**:
  - 文档完整
  - 性能达标（<90秒/版本）
  - 成本可控（<¥0.25/版本）

---

### Day 21: 回顾与总结

**任务清单**:
- [ ] 整理测试数据（至少 5 个版本）
- [ ] 编写技术总结文档
- [ ] 列出已知问题和待优化点
- [ ] 规划 Phase 2（Web 界面）
- [ ] **交付物**:
  - ✅ 可运行的命令行工具
  - ✅ 数据库中的完整数据
  - ✅ 技术文档和使用说明
  - ✅ 成本和性能报告

---

## 总结建议

**MVP 阶段（Week 1-3）**：
- ✅ **5个文件** 起步：每个 Agent 一个文件 + workflow.py
- ✅ Prompt 直接写在代码里（Python 字符串）
- ✅ 配置用 JSON 文件（`top_champions.json`）

**生产阶段（Week 4+）**：
- ✅ **每个 Agent 独立文件夹**（如上面推荐结构）
- ✅ Prompt 迁移到独立文件或数据库
- ✅ 添加完整测试覆盖

**核心原则**：
1. **先跑通，再优化** - 不要过早优化
2. **文件超过 200 行就拆分** - 保持可读性
3. **测试驱动重构** - 有测试才敢重构

---

## 5. LangGraph 工作流设计

```python
# 优化后的流程设计 ✅（不存原始数据）
from langgraph.graph import StateGraph, END
from crawlers.lol_official import LOLOfficialCrawler

# 定义状态（简化版）
class PatchAnalysisState(TypedDict):
    version: str
    source_url: str  # 来源 URL
    raw_content: str  # 仅在内存中传递，不持久化
    top_lane_changes: dict
    impact_analyses: list
    summary_report: dict

# 主流程函数
async def analyze_patch(version: str):
    # 1. 爬虫模块（非 Agent）- 直接返回内容，不存数据库
    crawler = LOLOfficialCrawler()
    raw_content = await crawler.fetch_patch_notes(version)

    # 2. LangGraph Workflow（3个 Agents）- 直接处理
    workflow = StateGraph()

    workflow.add_node("extractor", top_lane_extractor_agent)
    workflow.add_node("analyzer", impact_analyzer_agent)
    workflow.add_node("summarizer", report_summarizer_agent)

    workflow.set_entry_point("extractor")
    workflow.add_edge("extractor", "analyzer")
    workflow.add_edge("analyzer", "summarizer")
    workflow.add_edge("summarizer", END)

    # 编译并执行
    app = workflow.compile()
    result = await app.ainvoke({
        "raw_content": raw_content,  # 内存中传递，不入库
        "version": version,
        "source_url": crawler.last_url
    })

    # 3. 保存分析结果（不含 raw_content）
    await db.save_analysis(version, result, source_url=crawler.last_url)

    return result
```

**条件路由（可选）**:
- 如果 `extractor` 发现无上单相关变更，直接跳到 END
- 如果爬取失败，进入重试节点或错误处理

**优化效果**:
- ✅ 从 4 步减少到 3 步
- ✅ State 结构更简洁（去掉中间的 `structured_data`）
- ✅ 代码更易维护

---

## 6. API 接口设计

### REST API 端点

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/patches` | 获取所有版本列表 |
| GET | `/api/patches/{version}` | 获取特定版本详情 |
| GET | `/api/patches/latest` | 获取最新版本分析 |
| POST | `/api/patches/analyze` | 手动触发新版本分析 |
| GET | `/api/champions/{name}/history` | 获取英雄历史变更 |
| GET | `/api/meta/tierlist` | 获取当前 Tier List |

### Web 页面路由

| 路径 | 功能 |
|------|------|
| `/` | 首页 - 最新版本总结 |
| `/patch/{version}` | 版本详情页 |
| `/champion/{name}` | 英雄历史变更页 |
| `/meta` | Meta 分析和 Tier List |

---

## 7. 定时任务设计

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# 每天检查新版本
@scheduler.scheduled_job('cron', hour=10, minute=0)
async def check_new_patch():
    latest_version = await fetch_latest_version_from_official()
    if not exists_in_db(latest_version):
        await trigger_analysis_workflow(latest_version)

# 每周日更新 Meta Tier List
@scheduler.scheduled_job('cron', day_of_week='sun', hour=20)
async def update_tier_list():
    await recalculate_tier_list()
```

---

## 8. 技术难点与解决方案

### 8.1 爬虫反爬策略
- **问题**: 官网可能有反爬机制
- **方案**:
  - 使用 undetected-chromedriver
  - 设置随机 User-Agent 和请求延迟
  - 失败时降级到搜索引擎聚合

### 8.2 上单英雄识别准确率
- **问题**: 某些英雄可以打多个位置
- **方案**:
  - 维护英雄位置置信度表
  - 结合社区数据（如 op.gg API）
  - 让 LLM 根据变更内容判断是否影响上路

### 8.3 LLM 分析一致性
- **问题**: 不同版本分析可能风格不一致
- **方案**:
  - 设计详细的 Prompt 模板
  - 使用 few-shot examples
  - 保存成功案例作为示例

### 8.4 成本控制
- **估算**: 每版本约 15-20 次 LLM 调用
- **优化**:
  - 缓存重复查询
  - 对于小改动使用规则引擎
  - 批处理多个英雄分析

---

## 9. 开发路线图

### 🎯 MVP (Minimum Viable Product) - 核心分析流程
**目标**: 实现从爬取到分析的完整数据管道，验证技术可行性
**预计时间**: 2-3 周

#### Week 1: 基础设施搭建
- [ ] 初始化项目结构（参考上面的目录结构）
- [ ] 配置 PostgreSQL 数据库（安装 pgvector 扩展）
- [ ] 创建核心数据表: `patch_versions`, `champion_changes`, `impact_analysis`
- [ ] 接入 DeepSeek API，编写调用封装 (`llm_service.py`)
- [ ] 准备上单英雄白名单配置文件 (JSON/YAML)

#### Week 2: 爬虫与 LangGraph 流程
- [ ] 实现英雄联盟官网爬虫
  - 目标页面: https://lol.qq.com/news/category_64.shtml
  - 提取版本号、更新日期、公告内容
- [ ] 实现爬虫模块（普通 Python 类，非 Agent）
- [ ] 构建 3 个 LangGraph Agents:
  - Top Lane Extractor Agent (提取上单相关变更，合并了筛选功能)
  - Impact Analyzer Agent (深度影响分析)
  - Report Summarizer Agent (生成最终报告)
- [ ] 编写 LangGraph workflow 编排代码

#### Week 3: 测试与优化
- [ ] 手动测试完整流程（输入版本号 → 输出分析报告）
- [ ] 优化 Prompt 工程，提升分析质量
- [ ] 将分析结果存入数据库
- [ ] 编写简单的命令行接口触发分析
- [ ] 性能测试和成本核算

**MVP 交付物**:
- ✅ 可运行的 Python 脚本/命令行工具
- ✅ 数据库中存储的完整分析数据
- ✅ 至少 2-3 个版本的测试数据
- ✅ 成本和性能评估报告

---

### 🚀 Phase 2: Web 界面与 API (可选)
**预计时间**: 1-2 周

- [ ] 开发 FastAPI REST API 端点
- [ ] 实现 Jinja2 前端展示页面
- [ ] 添加用户友好的 Web 界面
- [ ] API 文档（Swagger）

### 🔄 Phase 3: 自动化与增强 (可选)
**预计时间**: 1-2 周

- [ ] 添加 APScheduler 定时任务
- [ ] 实现 RAG 历史案例检索
- [ ] 添加 Redis 缓存层
- [ ] 性能优化和监控

---

## 10. DeepSeek API 集成示例

### 10.1 API 调用封装 (llm_service.py)

```python
from openai import OpenAI
import os

class DeepSeekService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 4000):
        """调用 DeepSeek Chat API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def extract_structured_data(self, raw_content: str):
        """结构化提取更新内容"""
        prompt = f"""
你是一个专业的英雄联盟版本更新分析助手。请从以下更新公告中提取结构化信息。

更新公告内容:
{raw_content}

请按照以下 JSON 格式返回提取结果:
{{
  "version": "版本号",
  "release_date": "发布日期",
  "changes": [
    {{
      "champion": "英雄名称",
      "type": "buff/nerf/adjust/rework",
      "details": {{
        "技能名": "变更描述",
        "属性名": "数值变化"
      }}
    }}
  ],
  "system_changes": [
    {{
      "category": "装备/符文/游戏机制",
      "name": "具体项目名称",
      "description": "变更内容"
    }}
  ]
}}

只返回 JSON，不要其他解释。
"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.3)

    def analyze_impact(self, champion: str, changes: dict, context: str = ""):
        """分析英雄变更影响"""
        prompt = f"""
你是一个资深的英雄联盟上单位置分析师。请深度分析以下英雄变更对上单生态的影响。

英雄: {champion}
变更内容: {changes}

{f"历史参考案例: {context}" if context else ""}

请按照以下结构分析:

1. **强度评估** (1-10分):
2. **对线期影响**:
3. **团战能力变化**:
4. **克制关系变化**:
5. **出装推荐调整**:
6. **Tier 预测**: (S+/S/A/B/C)

请用简洁专业的语言回答，重点分析实战价值。
"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.7)
```

### 10.2 关键 Prompt 模板

#### Extractor Agent Prompt
```
角色: 英雄联盟数据提取专家
任务: 从非结构化文本中提取版本更新信息
要求:
- 准确识别英雄名称（中英文对照）
- 提取数值变化（前后对比）
- 区分 buff/nerf/调整/重做
- 识别装备、符文、系统变更
输出格式: JSON
```

#### Analysis Agent Prompt
```
角色: 英雄联盟上单位置专家（钻石以上水平）
任务: 分析变更对上单生态的实战影响
关注点:
- 对线强度（换血、压制力、gank 抗性）
- 团战价值（坦度、输出、控制、绕后能力）
- Meta 适配性（当前版本环境）
- 克制关系变化（哪些英雄受益/受损）
语言风格: 专业简洁，避免废话
```

#### Filter Agent Prompt (边缘英雄判断)
```
角色: 位置识别专家
任务: 判断变更是否影响上单位置
输入: {champion: "亚索", changes: {...}}
判断标准:
1. 该英雄是否常在上路出现？
2. 变更是否影响上路对抗能力？
3. 装备/符文变更是否影响上单玩法？
输出: JSON {"is_top_related": true/false, "confidence": 0.0-1.0, "reason": "..."}
```

---

## 11. 依赖包清单（requirements.txt）

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
jinja2==3.1.3
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
pgvector==0.2.4

# LangChain & LangGraph
langchain==0.1.5
langgraph==0.0.20
langchain-community==0.0.16

# LLM Providers
openai==1.10.0  # DeepSeek 兼容 OpenAI SDK
# 或直接使用 httpx 调用 DeepSeek API

# Crawlers
aiohttp==3.9.1
beautifulsoup4==4.12.3
selenium==4.17.2
undetected-chromedriver==3.5.4
lxml==5.1.0

# Task Scheduling
apscheduler==3.10.4

# Vector & Embeddings
sentence-transformers==2.3.1  # 本地 embedding 模型

# Utilities
python-dotenv==1.0.0
pydantic==2.5.3
redis==5.0.1  # 可选缓存
httpx==0.26.0
```

---

---

## 总结

这是一个完整的企业级架构方案，核心要点：

✅ **3 个 LangGraph Agents + 独立爬虫模块** 形成清晰的数据处理管道（合并 Extractor + Filter）
✅ **DeepSeek API** 超低成本（¥0.20/版本）高效分析
✅ **混合筛选策略** 白名单 + LLM 智能判断
✅ **PostgreSQL + pgvector** 支持结构化数据和向量检索
✅ **Level 1 RAG** 足够实现历史案例参考增强
✅ **MVP 优先策略** 先验证核心流程，再扩展功能
✅ **不存原始数据** 直接内存传递，节省空间和 I/O

### 技术亮点
1. **成本极低**: DeepSeek 比 GPT-4 便宜 100 倍，可放心调用
2. **架构精简**: 3 个 Agent 各司其职，提取+筛选合并减少复杂度
3. **存储优化**: 不存原始 HTML，每版本节省 50-200KB 空间
4. **流程简化**: 爬虫 → Agents → 数据库，减少中间读写
5. **可扩展性**: 从 MVP 到完整系统平滑过渡
6. **实用主义**: 优先实现核心功能，避免过度设计

### 开发建议
1. **先做 MVP**: 用 2-3 周验证技术可行性和分析质量
2. **迭代优化**: 根据实际分析效果调整 Prompt 和流程
3. **成本监控**: 虽然便宜，但也要记录每次调用的 token 消耗
4. **数据积累**: 多分析几个版本，积累 RAG 知识库

**MVP 开发周期**: 2-3 周
**完整系统开发周期**: 6-7 周
**运行成本**: 约 **¥0.20/版本** (DeepSeek 超低成本，优化后节省 20%)

---

## 附录: 快速开始检查清单

### 开发前准备
- [ ] 注册 DeepSeek 账号并获取 API Key
- [ ] 安装 PostgreSQL 数据库（推荐使用 Docker）
- [ ] 安装 pgvector 扩展
- [ ] 准备 Python 3.10+ 环境
- [ ] （可选）注册 Riot Games 开发者账号

### 第一周任务
- [ ] 克隆项目模板，安装依赖
- [ ] 配置 .env 文件（API Key、数据库连接）
- [ ] 创建数据库表结构
- [ ] 测试 DeepSeek API 连接
- [ ] 手动爬取 1-2 个版本公告测试

### 验收标准
- [ ] 输入版本号，能自动爬取公告
- [ ] 能结构化提取英雄变更数据
- [ ] 能输出上单英雄的影响分析报告
- [ ] 数据正确存入数据库
- [ ] 成本在预期范围内（<¥1/版本）
