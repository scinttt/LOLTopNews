# LOL Top Lane Guide

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Status-Active-green.svg" alt="Status: Active">
  <img src="https://img.shields.io/badge/Type-Full--Stack-purple.svg" alt="Type: Full Stack">
</p>

> AI-powered League of Legends patch analysis tool focused on top lane meta. Automatically analyze LOL patch notes and generate comprehensive top lane impact reports using AI. Built with LangGraph, DeepSeek LLM, and intelligent web scraping.

## Features

- **Intelligent Analysis**: Uses DeepSeek AI to extract and analyze top lane changes
- **Cost-Effective**: ~¥0.03 per version analysis (100x cheaper than GPT-4)
- **Top Lane Focused**: Filters out irrelevant changes (mid, ADC, jungle, support)
- **Automated Scraping**: Directly fetches latest patch notes from LOL official website
- **Structured Output**: Clean, categorized changes (champions, items, systems)
- **REST API**: FastAPI-based API for programmatic access
- **Web UI**: React-based frontend for visualization

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Architecture                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────┐                                        │
│  │ Crawler Module │ (Web Scraping)                          │
│  │ lol_official.py│                                        │
│  └───────┬────────┘                                        │
│          │                                                  │
│          ▼                                                  │
│  ┌──────────────────────────────────────┐                  │
│  │       LangGraph Workflow             │                  │
│  ├──────────────────────────────────────┤                  │
│  │  Node 1: Extractor                   │                  │
│  │  - Extract top lane changes          │                  │
│  │  - Champion/Item/System categories  │                  │
│  └───────────┬──────────────────────────┘                  │
│              │                                              │
│              ▼                                              │
│  ┌──────────────────────────────────────┐                  │
│  │  Node 2: Analyzer                    │                  │
│  │  - Deep impact analysis              │                  │
│  │  - WebSearch tool integration        │                  │
│  └───────────┬──────────────────────────┘                  │
│              │                                              │
│              ▼                                              │
│  ┌──────────────────────────────────────┐                  │
│  │  Node 3: Summarizer                  │                  │
│  │  - Tier list generation              │                  │
│  │  - Build recommendations             │                  │
│  │  - Counter matrix                   │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ (for frontend)
- DeepSeek API key ([Get one here](https://platform.deepseek.com))

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/LOLTopNews.git
cd LOLTopNews

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY

# Run CLI
python app/main.py --version latest

# Or run API server
python app/api.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL
cp .env.example .env
# Set VITE_API_URL=http://localhost:8000

# Run development server
npm run dev
```

## Usage

### CLI

```bash
# Analyze latest patch
python app/main.py --version latest

# Analyze specific version
python app/main.py --version 15.24

# Analyze from local file
python app/main.py --file data/sample_patch_14.24.txt
```

### REST API

```bash
# Start the API server
python app/api.py

# API Endpoints
curl http://localhost:8000/api/analyze?version=latest
curl http://localhost:8000/health
```

## Project Structure

```
LOLTopNews/
├── app/
│   ├── main.py                 # CLI entry point
│   ├── api.py                  # FastAPI REST API
│   ├── crawlers/               # Web scraping module
│   │   ├── base.py             # Base crawler with retry logic
│   │   └── lol_official.py     # LOL official website crawler
│   └── agents/                 # LangGraph AI workflow
│       ├── state.py            # Workflow state definition
│       ├── llm.py              # LLM initialization
│       ├── tools.py            # WebSearch tool
│       ├── workflow.py         # Graph orchestration
│       └── nodes/              # Processing nodes
│           ├── extractor.py    # Extract top lane changes
│           ├── analyzer.py     # Impact analysis
│           └── summarizer.py   # Report generation
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── services/          # API services
│   │   └── App.tsx            # Main app
│   └── package.json
├── data/                       # Sample data
├── scripts/                    # Test scripts
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## Module Documentation

### Backend Modules

| Module | File | Description |
|--------|------|-------------|
| CLI Entry | `app/main.py` | Command-line interface for patch analysis |
| REST API | `app/api.py` | FastAPI-based REST API server |
| Crawler Base | `app/crawlers/base.py` | Base crawler with retry logic, validation |
| LOL Crawler | `app/crawlers/lol_official.py` | LOL official website scraper |
| Workflow | `app/agents/workflow.py` | LangGraph workflow orchestration |
| State | `app/agents/state.py` | WorkflowState type definition |
| LLM | `app/agents/llm.py` | DeepSeek LLM initialization |
| Tools | `app/agents/tools.py` | WebSearch tool (Tavily) |
| Extractor | `app/agents/nodes/extractor.py` | Extract top lane changes |
| Analyzer | `app/agents/nodes/analyzer.py` | Deep impact analysis |
| Summarizer | `app/agents/nodes/summarizer.py` | Tier list & build recommendations |

### Frontend Components

| Component | File | Description |
|-----------|------|-------------|
| Main App | `frontend/src/App.tsx` | Main React application |
| API Service | `frontend/src/services/api.ts` | Backend API client |
| Summary | `frontend/src/components/Summary.tsx` | Executive summary display |
| Tier List | `frontend/src/components/TierList.tsx` | Champion tier list display |
| Champion Changes | `frontend/src/components/ChampionChanges.tsx` | Champion changes display |
| Impact Analysis | `frontend/src/components/ImpactAnalysis.tsx` | Impact analysis display |

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API key | Yes |
| `DEEPSEEK_BASE_URL` | DeepSeek API base URL | No |
| `DEEPSEEK_MODEL` | Model name (default: deepseek-chat) | No |
| `TAVILY_API_KEY` | Tavily API key for web search | No |

## Development

### Running Tests

```bash
# Test crawler
python scripts/test_real_lol_url.py

# Test extractor
python scripts/test_extractor.py
```

### Code Style

- Follow PEP 8 for Python
- Use type hints
- Add docstrings for public functions

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root |
| GET | `/health` | Health check |
| GET | `/api/analyze?version={version}` | Analyze patch (GET) |
| POST | `/api/analyze` | Analyze patch (POST) |

### Response Format

```json
{
  "version": "15.24",
  "top_lane_changes": [...],
  "impact_analyses": [...],
  "summary_report": {
    "tier_list": {...},
    "meta_ecosystem": {...},
    "champion_details": [...],
    "counter_matrix": {...}
  },
  "metadata": {...}
}
```

## Cost Analysis

| Module | Tokens | Cost (DeepSeek) |
|--------|--------|-----------------|
| Extractor | ~7K | ¥0.008 |
| Analyzer | ~5K | ¥0.010 |
| Summarizer | ~8K | ¥0.012 |
| **Total** | ~20K | **¥0.030** |

## Tech Stack

### Backend
- Python 3.12+
- LangGraph (AI Workflow)
- DeepSeek (LLM)
- FastAPI (REST API)
- aiohttp + BeautifulSoup4 (Web Scraping)

### Frontend
- React 19
- TypeScript
- Vite

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) & [LangGraph](https://github.com/langchain-ai/langgraph) for AI orchestration
- [DeepSeek](https://www.deepseek.com/) for cost-effective LLM API
- [Riot Games](https://www.riotgames.com/) for League of Legends
- [Tavily](https://tavily.com/) for web search enhancement

## Disclaimer

This project is not affiliated with Riot Games. All game content and materials are trademarks and copyrights of Riot Games.

---

**Made with love for the top lane community**

*Author: David Zhang*
*License: MIT*
