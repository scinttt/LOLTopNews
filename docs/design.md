# LOLTopNews - System Design Document

> AI-powered League of Legends patch analysis system, focused on top lane meta impact.
> Last updated: 2026-04-06

---

## System Overview

LOLTopNews is a full-stack application that automatically crawls League of Legends patch notes from the official website, uses LLM-based agentic workflow to extract, analyze, and summarize top lane meta changes, and presents the results through a React frontend.

**Core value proposition**: Turn raw patch notes into actionable top lane strategy insights (tier list, build paths, counter matrix) at ~¥0.03 per analysis.

---

## System Architecture

```
User/Client (Browser)
    ↕
┌──────────────────────────────────────────────────────┐
│  React Frontend (Vite + TypeScript)                  │
│  Components: TierList | ChampionChanges |            │
│              ImpactAnalysis | Summary                │
└──────────────────────────────────────────────────────┘
    ↕ HTTP (localhost:8000)
┌──────────────────────────────────────────────────────┐
│  FastAPI REST API (app/api.py)                       │
│  - GET /api/analyze?version=X                        │
│  - POST /api/analyze                                 │
│  - JSON file cache (data/cache/{version}.json)       │
└──────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────┐
│  Crawler Layer (app/crawlers/)                       │
│  - LOLOfficialCrawler: lol.qq.com                   │
│  - GB2312 encoding, retry, version detection         │
└──────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────┐
│  LangGraph Agentic Workflow (app/agents/)            │
│                                                      │
│  Extractor (T=0.3)                                   │
│    → Extract top lane champion/item/system changes   │
│  Analyzer (T=0.7, tool-enabled)                      │
│    → Deep impact analysis + meta predictions         │
│    → WebSearch tool (Tavily, max 10 calls)           │
│  Summarizer (T=0.4-0.5, 2-step)                     │
│    → Step 1: Tier list + meta ecosystem              │
│    → Step 2: Builds + counter matrix                 │
└──────────────────────────────────────────────────────┘
    ↓
  Response → Frontend renders analysis results
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, Uvicorn |
| LLM | DeepSeek (deepseek-chat) via OpenAI SDK |
| Workflow | LangGraph (StateGraph) + LangChain |
| Web Search | Tavily SDK (optional) |
| Crawler | aiohttp, BeautifulSoup4, lxml |
| Frontend | React 19, TypeScript, Vite |
| Cache | JSON file-based (data/cache/) |
| Testing | pytest |

---

## Project Structure

```
LOLTopNews/
├── app/
│   ├── main.py                  # CLI entry point
│   ├── api.py                   # FastAPI REST API (~220 lines)
│   ├── crawlers/
│   │   ├── base.py              # BaseCrawler: retry, validation
│   │   └── lol_official.py      # LOL official site crawler
│   └── agents/
│       ├── state.py             # WorkflowState TypedDict
│       ├── llm.py               # LLM factory (3 temperature variants)
│       ├── tools.py             # WebSearch tool (Tavily)
│       ├── workflow.py          # LangGraph orchestration
│       └── nodes/
│           ├── extractor.py     # Change extraction
│           ├── analyzer.py      # Impact analysis (tool-enabled)
│           └── summarizer.py    # Tier list + build aggregation
├── frontend/
│   └── src/
│       ├── App.tsx              # Main component + state management
│       ├── components/          # TierList, ChampionChanges, ImpactAnalysis, Summary
│       └── services/api.ts      # API client
├── tests/                       # pytest: API, workflow, caching
├── scripts/                     # Manual test scripts for crawler/extractor
├── data/
│   ├── cache/                   # Cached analysis results
│   ├── raw_patches/             # Crawled raw patch text
│   └── sample_patch_14.24.txt   # Sample data
├── requirements.txt
├── run_api.sh                   # uvicorn launcher
└── .env.example                 # DEEPSEEK_API_KEY, TAVILY_API_KEY
```

---

## Core Components

### 1. Crawler Layer

**BaseCrawler** (`app/crawlers/base.py`): Async retry (3 attempts, exponential backoff), content validation (min 1000 bytes), file save for debugging.

**LOLOfficialCrawler** (`app/crawlers/lol_official.py`): Targets lol.qq.com. Handles GB2312 encoding. Version detection via regex on article titles. Pagination search up to 10 pages. Fallback to known URLs if parsing fails.

### 2. LangGraph Workflow

The workflow is a 3-node StateGraph with conditional tool routing:

```
extractor → analyzer → [should_continue?]
                           ├─ has tool calls → tools node → analyzer (loop, max 10)
                           └─ no tool calls → summarizer → END
```

**WorkflowState** tracks: `raw_content`, `version`, `top_lane_changes`, `impact_analyses`, `summary_report`, `messages`, `error`, `metadata`, `tool_call_count`.

### 3. Agent Nodes

| Node | Temperature | Purpose | Output |
|------|------------|---------|--------|
| Extractor | 0.3 | Extract top lane changes from raw patch notes (first 10K chars) | `top_lane_changes[]` with type, champion, change_type, relevance |
| Analyzer | 0.7 | Deep impact analysis with optional web search | `champion_analyses[]` + `meta_overview` |
| Summarizer | 0.4-0.5 | 2-step aggregation: tier list + builds/counters | `summary_report` with tier_list, meta_ecosystem, champion_details, counter_matrix |

### 4. API Layer

**Endpoints**:
- `GET /` - API metadata
- `GET /health` - Health check
- `GET /api/analyze?version=latest` - Analyze with auto-crawl
- `POST /api/analyze` - Analyze with optional raw content body

**Caching**: JSON file at `data/cache/{version}.json`. Cache hit returns immediately; miss triggers full pipeline.

### 5. Frontend

React 19 + TypeScript + Vite. Components:
- **TierList** - S/A/B/C/D tier visualization
- **ChampionChanges** - Extracted changes display
- **ImpactAnalysis** - Per-champion analysis cards
- **Summary** - Executive summary + key highlights

---

## Data Flow

1. User enters version (e.g. "14.24" or "latest") in frontend
2. Frontend calls `GET /api/analyze?version=14.24`
3. API checks cache → hit returns immediately
4. Cache miss → Crawler fetches from lol.qq.com
5. Extractor parses raw text → structured top lane changes
6. Analyzer evaluates impact (may use WebSearch tool, up to 10 calls)
7. Summarizer aggregates into tier list, builds, counters
8. Result cached to JSON file, returned to frontend
9. Frontend renders 4 component views

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| DeepSeek over GPT-4 | 100x cheaper (~¥0.03/version), strong Chinese language support |
| LangGraph StateGraph | Modular nodes, built-in tool routing, message history |
| Temperature tuning per node | Extractor (0.3) for precision, Analyzer (0.7) for creativity, Summarizer (0.5) for balance |
| 2-step Summarizer | Step 1 structural (tier list), Step 2 creative (builds/counters) |
| JSON file cache | Simple, no-dependency MVP cache; sufficient for current scale |
| GB2312 encoding support | LOL official website (lol.qq.com) uses this encoding |
| Max 10 tool calls | Prevents infinite loops, controls cost |

---

## Configuration

**Required**:
- `DEEPSEEK_API_KEY` - LLM API key

**Optional**:
- `DEEPSEEK_MODEL` - Model name (default: deepseek-chat)
- `TAVILY_API_KEY` - Enables WebSearch tool for Analyzer

---

## Cost Model

| Component | Tokens | Cost (DeepSeek) |
|-----------|--------|-----------------|
| Extractor | ~7K | ¥0.008 |
| Analyzer | ~5K | ¥0.010 |
| Summarizer | ~8K | ¥0.012 |
| **Total per version** | **~20K** | **~¥0.030** |

---

## Feature Status

- ✅ Crawler (LOL official, version detection, pagination)
- ✅ Extractor (top lane change extraction)
- ✅ Analyzer (impact analysis + WebSearch tool)
- ✅ Summarizer (tier list, builds, counter matrix)
- ✅ FastAPI REST API with caching
- ✅ React frontend (4 components)
- ✅ Unit tests (API, workflow, caching)
- 📋 PostgreSQL + pgvector integration
- 📋 Scheduled crawling (APScheduler)
- 📋 Redis caching
- 📋 Win rate prediction model
- 📋 Frontend deployment

---

## Current Goals

- Maintain stable MVP: crawler → LLM pipeline → frontend
- Keep per-analysis cost under ¥0.05

## Ultimate Vision

A fully automated, self-updating LOL top lane meta intelligence platform that combines patch analysis with real-time community data and win rate predictions.

---

## Changelog

### 2026-04-06
- Initial design doc created based on existing codebase state
